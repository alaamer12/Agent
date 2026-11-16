# How `eas-cli` decides what goes in the archive

Behaviour below was read out of `eas-cli`'s `build/vcs/clients/git.js` and
`build/vcs/local.js`. Versions differ in detail; re-check the installed copy when
a conclusion matters:

```
node -e "console.log(require('eas-cli/package.json').version)"
grep -rn "EASIGNORE_FILENAME" node_modules/eas-cli/build/vcs/
```

## Selection order

1. `git rev-parse --show-toplevel` → **archive root**. In a monorepo this is the
   repository root, so the upload contains every workspace package and every other
   app, not just the one being built.
2. `<archive root>/.easignore` is looked up **only at that path**. A `.easignore`
   inside an app subdirectory is not read.
3. If it exists, the archiver's rule set is `.easignore` **plus defaults**
   (`.git`, `node_modules`). No `.gitignore` file anywhere is consulted — not the
   root one, not nested ones.
4. If it does not exist, the archiver globs `**/.gitignore` and applies each file's
   rules relative to its own directory, i.e. nested package ignores do work.
5. The archive is produced as a shallow `git clone` **plus** a working-tree copy
   (unless `requireCommit: true`). Untracked and uncommitted files are therefore
   uploaded. Tracked files matching the active rules are then removed from the
   copy with:

   ```
   git ls-files --exclude-from=<active ignore file> --ignored --cached
   ```

   Run that command yourself to preview exactly which committed files disappear.
6. `.git` is deleted from the copy only when the active rules ignore it.

## Size limits

- Above **150 MB** the CLI warns and points at `.easignore`.
- Above **2 GB** the upload is rejected outright.
- The number worth reading is the CLI's own `Compressed project files (… (SIZE))`
  line: compressed. Compare against the audit script's uncompressed total to judge
  how much is text versus binaries.

## Pattern semantics

`.easignore` uses gitignore syntax, so the usual traps apply:

| Pattern | Meaning |
|---|---|
| `dist/` | any directory named `dist` at any depth |
| `/apps/mobile/android/` | anchored to the archive root only |
| `android` | matches files **and** directories named `android` anywhere — too broad |
| `docs` vs `docs/` | the first also matches a file named `docs` |
| `!apps/web/package.json` | re-includes inside an excluded parent |

Negation only works while the parent directory is still traversable: excluding
`apps/web/` and then negating `!apps/web/package.json` does nothing. Exclude the
**contents** instead.

## Monorepo workspace rule

Package managers validate the lockfile against every workspace member's manifest,
so excluding a sibling app wholesale breaks install on the builder. The pattern
that shrinks the upload without breaking resolution:

```
apps/web/*
!apps/web/package.json
apps/admin/*
!apps/admin/package.json
```

Applies to npm, pnpm, yarn and bun workspaces alike. Verify with the audit script
afterwards — a missing manifest shows up as an install failure early in the build,
not as an ignore error.

## What is safe to exclude

Check the consumer before excluding anything, in this order:

1. Every workspace `package.json` `exports`/`main` — if one resolves into `dist/`
   or `build/`, that directory is a **source** for the build, not output.
2. `app.json` / `app.config.*` references — `google-services.json`,
   `GoogleService-Info.plist`, splash icons, adaptive icons, fonts. These are read
   by prebuild at build time and must be present.
3. Native config plugins that read local files (paths passed to plugin options).
4. Lockfiles — needed for deterministic install on the builder.

Everything else in a typical repository is fair game: caches (`.turbo`, `.cache`,
`node_modules/.cache`), build output, coverage, screenshots, editor and agent
folders, docs, fixtures, database dumps, and generated native projects.

## Secrets

Because the archiver's rules can be *only* `.easignore`, a project that relies on
`.gitignore` for secret hygiene will upload those secrets the moment someone adds
an `.easignore`. Being untracked is not protection — untracked files are exactly
what the working-tree copy adds.

Name them explicitly in `.easignore`: `.env`, `.env*.local`, `*.p8`, `*.pem`,
`*.key`, `*.jks`, `*.keystore`, `*.mobileprovision`, `*.p12`, credential
directories, and service-account JSON files. Then move the values to EAS
environment variables or stored credentials, and treat anything that already
shipped as exposed: rotate it.
