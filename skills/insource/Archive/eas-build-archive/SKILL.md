---
name: eas-build-archive
description: Diagnose and shrink what `eas build` uploads for Expo and React Native projects. Use when an EAS Build archive is unexpectedly large or slow, when a build fails with a Gradle/CocoaPods or toolchain version mismatch that works locally, when a custom dev client throws "Cannot find native module", when secrets or generated folders may be reaching the build service, or whenever `.easignore` or `.gitignore` behaviour for EAS needs explaining.
---

# EAS Build Archive

## Overview

EAS Build uploads a copy of the repository before it builds anything. The archive's
contents decide three things people usually debug separately: upload size, which
toolchain versions the build uses, and whether credentials leave the machine. This
skill measures the archive the way `eas-cli` does, attributes its weight, and
reduces it safely.

## The model that explains almost every symptom

1. `eas-cli` locates the **git root** (`git rev-parse --show-toplevel`) and treats
   that as the archive root. In a monorepo the upload contains the whole workspace,
   not just the app directory.
2. Ignore rules come from **`<git root>/.easignore` if it exists — and only from
   that file**. When `.easignore` is present, every `.gitignore` in the repository,
   including nested ones in sub-packages, is ignored by the archiver.
3. Without `.easignore`, it collects the `.gitignore` stack (root plus nested).
   A rule that protects a directory inside an app package therefore has to live in
   whichever file the archiver is currently reading.
4. `node_modules` and `.git` are excluded by default. Everything else is included
   unless a rule removes it.
5. The archive is built as a git clone **plus** a copy of the working tree, so
   uncommitted and untracked files ship. Tracked files that the active rules match
   are then deleted from the copy.

Consequences worth internalising:

- A directory excluded only by a nested `.gitignore` **is** uploaded when
  `.easignore` exists. This is how a 100 MB stale native folder ends up in a build.
- Untracked local secrets (`.env`, `*.p8`, keystores) are uploaded unless the
  active ignore file names them. Being untracked by git is not protection.
- `requireCommit: true` changes step 5 to committed content only.

## Workflow

### 1. Measure, don't guess

```
node scripts/eas-archive-audit.mjs [--top N]
```

It replays the archiver's selection and reports total size, the largest groups,
secrets, native project files, generated output, oversized single files, and
candidate rules. Never propose an exclusion without this output in hand.

### 2. Attribute the weight before choosing a fix

Compare the measured number against what the project actually needs to build:
app source, workspace package sources, lockfile, and root config. Everything else
is a candidate: other apps in the monorepo, agent/editor folders, docs, fixtures,
screenshots, caches, build output, and generated native projects.

### 3. Check the two dangerous categories first

- **Secrets** — anything credential-shaped reaching the build service is an
  incident, not an optimization. Move it to EAS environment variables or stored
  credentials, then exclude the path.
- **Native project directories** (`android/`, `ios/`, `Podfile.lock`,
  `gradle-wrapper.properties`) in a prebuild/CNG project. Shipping these makes EAS
  skip generation and build with whatever versions the folder was born with —
  the classic "works locally, fails in the cloud with a version mismatch" build.
  See `references/native-drift.md`.

### 4. Write `.easignore` as a replacement, never as an addendum

Because the file replaces `.gitignore` for the archiver, a new `.easignore` must
carry over every rule that keeps generated output **and secrets** out. Add the
new exclusions on top of that carried-over set. Do not exclude a directory that a
`package.json` `exports` entry resolves into, and do not exclude workspace
`package.json` files — the package manager needs them to validate the lockfile.
Pattern semantics and the monorepo workspace trick are in `references/easignore-semantics.md`.

### 5. Verify before uploading

```
git ls-files --exclude-from=.easignore --ignored --cached
```

This is the exact command `eas-cli` runs to delete tracked files from the copy.
Its output is the list of committed files that will vanish from the archive —
read it and confirm nothing needed is on it. Then re-run the audit script and
compare totals.

### 6. Confirm against a real build

The CLI prints `Compressed project files (… (SIZE))` and warns above 150 MB. The
archive size in that line is the ground truth. A rebuild is required after any
change to what gets compiled in — ignoring a folder, adding a native dependency,
or changing per-profile Gradle/CocoaPods properties all mean a new client binary.

## Symptom index

| Symptom | Usual cause | Where |
|---|---|---|
| Upload hundreds of MB, slow | Whole monorepo + caches + generated output | workflow 1–4 |
| `Minimum supported Gradle version is X. Current version is Y` | Stale `android/` in the archive, EAS skipped prebuild | `references/native-drift.md` |
| `Gradle build daemon disappeared unexpectedly`, no stack | Builder ran out of memory; check ABI/variant fan-out | `references/native-drift.md` |
| `Cannot find native module 'X'` in a dev client | Package declared after the binary was built | `references/native-drift.md` |
| Secrets in the archive | Active ignore file doesn't name them; untracked ≠ excluded | workflow 3 |
| Rule in a package's `.gitignore` has no effect | `.easignore` exists and replaced it | model, fact 2 |

## Guardrails

- Report measured numbers; never claim a size reduction without the audit output
  or the CLI's own archive line.
- Deleting from `node_modules` is fine; deleting tracked files is not — exclude
  them from the archive instead of removing them from the repository.
- When a stale generated directory must go, confirm nothing links to it first
  (`find node_modules -path "*/<pkg>" -printf "%p -> %l\n"` for package-manager
  stores) and prefer the package manager's reinstall over hand-pruning.
- If a fix changes what a release build compiles, say so explicitly rather than
  letting it ride along in a dev-only profile.

## Resources

- `scripts/eas-archive-audit.mjs` — replays EAS's archive selection; run first.
- `references/easignore-semantics.md` — archiver internals, pattern rules, monorepo specifics.
- `references/native-drift.md` — prebuild/CNG, toolchain version failures, memory-driven daemon deaths, missing native modules.
