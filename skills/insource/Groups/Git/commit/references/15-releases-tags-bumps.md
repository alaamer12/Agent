# Releases, tags, and version bumps

Version mechanics are where confident guessing does the most damage, because the artifact is public. Each rule
below is a flag or a step that is easy to get wrong and hard to undo once the tag is on the release feed.

## How many bumps for several fixes? One (p.85–87)

Two `fix:` commits shipping together → **one** patch bump (`1.2.3 → 1.2.4`). SemVer tracks public changes per
*release*, not per commit. The commits stay separate; the version does not multiply.

## Where the bump lives: its own commit, always (p.86–87)

```text
chore(release): bump version to 1.2.4
```

Three reasons, all practical:

- **Clarity** — code changes and release mechanics are different kinds of decision.
- **Reusability** — reverting the code must not revert the version, and vice versa.
- **Tooling** — release automation of any kind expects version commits to be standalone (or fully
  auto-generated), and a mixed commit breaks it: [semantic-release], [changesets], [release-it],
  [standard-version], [cargo-release], [bump-my-version], [python-semantic-release], [mvn release:],
  [gbp-dch]/[debchange], or a project's own script.

Manual flow (p.86–87):

```bash
# fix commits land
<project version command>   # the stack's own bump: it edits the version file, commits, and tags
git push                    # branches only
git tag v1.2.4              # only if the project's flow is manual
git push --follow-tags      # see the flag rules below
```

Find the project's command rather than assuming one — it is what keeps the version file, the tag, and the
changelog in sync, and a hand-made tag that skips it is how releases drift:

| Stack | The bump command usually lives in |
|---|---|
| Node | `package.json` scripts, or [npm]/[pnpm]/[yarn]/[bun] `version` |
| Rust | [cargo-release] |
| Python | [bump-my-version], [tbump], a `bump` make target |
| Java / Kotlin | the release plugin or a `release` goal |
| .NET | a version property in the project file plus a CI step, or a `dotnet` release script |
| Go | tags only — the tag *is* the version; no file to edit |
| Packaging / OS | a changelog tool that bumps and records together |

Monorepo (p.87): the pattern is per-change intent files that a release step consumes and turns into one
`chore: version packages` commit — [changesets] is the common shape; other ecosystems have equivalents, and
some projects just write the release commit by hand.

## Flag mechanics you must not guess at (p.87–90)

| Command | What it actually does | Trap |
|---|---|---|
| `git commit -am "msg"` | stages **modified and deleted tracked files** and commits them | **new/untracked files are not included.** A "successful" commit that silently omits the file you just created is the classic morning-of-release surprise (p.88–89) |
| `git push` | pushes branches | never pushes tags |
| `git push -f` | force-pushes a branch | still does not push tags — adding `-f` does not change that (p.89) |
| `git push --tags` | pushes **all** local tags | includes orphans and old ones; usually excessive and noisy |
| `git push --follow-tags` | pushes only **annotated** tags attached to the commits being pushed | the correct default; CI/CD and GitHub Releases need it to see the version (p.89) |
| `git push -f --tags` | force-push plus every local tag | dangerous in shared repos; do not combine them (p.90) |

Lightweight vs annotated tags: `git tag v1.2.4` makes a lightweight tag; `git tag -a v1.2.4 -m "release"` makes
an annotated one, and `--follow-tags` only carries annotated tags. If the release pipeline depends on
`--follow-tags`, create annotated tags.

## Sign-off and signing (orig)

```bash
git commit -S -m "feat: …"     # GPG/SSH-sign the commit
git commit -s -m "feat: …"     # add a Signed-off-by: trailer (DCO) — different thing entirely
```

`-S` proves who authored it; `-s` states the right to submit it. Projects requiring a DCO want `-s`; projects
verifying signatures want `-S`. Do not add either unless the project asks, and never sign as someone else
([`05`](05-trailers-and-footers.md)).

## Changelog and release-note hygiene

- The `BREAKING CHANGE:` footer and the `!` marker are what generators read; if a contract changed, both
  should be present ([`05`](05-trailers-and-footers.md)).
- A wrong `feat`/`fix`/breaking label is not cosmetic — it becomes a wrong version number in a published
  artifact. When the label is a judgment call with release consequences, state it and let the owner confirm.
- If the project's release notes are user-facing, they are written for users, not derived verbatim from commit
  subjects. `fix(api): handle null response in user endpoint` is not a changelog line.

## The pre-push checklist for a release commit sequence

```bash
git log --oneline origin/main..HEAD      # what is about to become public
git diff --stat origin/main..HEAD        # the shape of it
git status --short                       # anything untracked that belongs in this release?
grep -RIn "BEGIN .*PRIVATE KEY\|AKIA[0-9A-Z]\{16\}" --exclude-dir=.git . | head
git tag --points-at HEAD                 # is the tag already here?
```

Then, and only then: push branches, push tags with `--follow-tags`, and confirm the release job picked up the
version. If anything in that list surprises you, stop — a release is the one thing that cannot be undone
quietly once users have consumed it.
