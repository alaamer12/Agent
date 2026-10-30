# Sources - where each convention claim came from

Consulted 2026-10-27. Rules that are folklore are marked as such, because the difference between "git does
this" and "a blog post said this in 2014" matters when your project disagrees.

## The classic seven rules

**"How to Write a Git Commit Message" - Chris Beams, 2014, still the reference text**
(<https://cbea.ms/git-commit/>). Its seven rules: separate subject from body with a blank line; limit the
subject to 50 characters; capitalize the subject; do not end it with a period; use the imperative mood in the
subject; wrap the body at 72 characters; use the body to explain *what* and *why* and not *how*.

- The skill adopts all seven, with two amendments: **capitalization is a repo-consistency choice, not a rule**
  (Conventional Commits write `fix(scope): lower-case`, and mixing the two dialects is the real failure), and
  **50 is a budget rather than a wall** - see the 2025 note below.
- The "If applied, this commit will <subject>" test for imperative mood is his, and it is the fastest way to
  settle the argument with a teammate.

## Why imperative, from git's own behavior

`git merge` produces `Merge branch 'x'…` and `git revert` produces `Revert "<subject>"` - imperative
templates in the tool itself, which is the compositional argument for writing subjects the same way. Git's
own project writes subsystem-prefixed imperative subjects (`submodule: …`), a useful reminder that there was
never one global style.

## Length limits: mechanics, not taste

The 50/72 numbers exist because of terminal rendering, `git log --oneline`, `git shortlog`, and
`git format-patch` subjects quoted at ~72 columns in email. Modern discussions confirm the reasoning is
partly historical:

- **"Git Commit Messages - Why keep the 50 character convention?" (May 2025)**
  (<https://blog.thirstybear.co.uk/2025/05/git-commit-messages-why-keep-50.html>) - argues the limit still buys
  a compressed subject, while acknowledging that forges display more.
- Stack Overflow's long-running thread on 50/72 formatting
  (<https://stackoverflow.com/questions/2290016/git-commit-messages-50-72-formatting>) shows the split in
  practice: 50/72 for terminal fidelity, 72 for the subject in web-first teams.
- DevIQ and Midori's guides restate the rule and its rationale (<https://deviq.com/practices/50-72-rule/>,
  <https://www.midori-global.com/blog/2018-04-02/git-50-72-rule>), as does GitKraken's best-practices page
  (<https://gitkraken.com/learn/git/best-practices/git-commit-message>).
- Empirical note: studies and repo audits consistently find a **minority** of real commits use imperative
  mood (see the discussion at <https://www.reddit.com/r/programming/comments/hcmup8/>), so this skill presents
  imperative as the professional default *and* the thing to match to a repo's history, not as a universal fact.

## Conventional Commits

**The specification** (<https://www.conventionalcommits.org/en/v1.0.0/>, originating from the Angular
convention, <https://www.conventionalcommits.org/en/v1.0.0-beta.4/>): `<type>[optional scope][!]: <description>`,
optional body, optional footers, `BREAKING CHANGE` in a footer or `!` before the colon, and version bumping
driven by `fix`/`feat`/breaking. qoomon's cheatsheet
(<https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13>) is the most convenient summary of the
parser-visible details - what is optional, where the `!` goes, how `feat!` vs `BREAKING CHANGE:` interact.

The format exists to be machine-readable, and the roles that consume it are stack-neutral: something checks
the message at commit time, something offers the structure while typing, something derives the changelog and
the version bump from the types. Every ecosystem has its own occupants for those roles - [commitlint],
[lefthook], [pre-commit], a plain `commit-msg` hook, [commitizen]/`git cz` and its adapters, [cargo-release],
[bump-my-version], [standard-version], [release-it], [changesets]. The skill names roles first and tools in
brackets, because a guide that assumes a Node toolchain reads as irrelevant to most repositories.

The roles matter for the same reason in any stack: **the tooling is why teams adopt the format, and it is also
why a wrong type is not cosmetic** - a mislabelled `feat`/`fix`/breaking becomes a wrong published version.

## The 2025-2026 criticism, which the skill takes seriously

Two threads in mid-2026 argued against type-first messages:

- **"Stop Using Conventional Commits"** (<https://lobste.rs/s/oqlpna/stop_using_conventional_commits>, and the
  r/git discussion <https://www.reddit.com/r/git/comments/1vvt8r7/>).
- Substantive points raised there and in similar write-ups: contributors, debuggers and incident responders
  all care about **which area** changed, yet the format makes scope optional while putting type first; the
  type is frequently a guess, and a wrong guess silently corrupts automated changelogs; the label encourages
  committing per label instead of per change; `chore` becomes a landfill for anything uncategorizable; and
  user-facing release notes are a different artifact from maintainer-facing history, so generating a changelog
  straight from commit types produces notes written for the wrong audience.

The balanced position this skill adopts: adopt the format where it buys real automation and the team enforces
it; keep it out of small or personal projects where it is ceremony; and in every case let **atomicity and a
descriptive subject outrank the label** - a correctly typed `chore: update` is worth less than a plain
`fix(orders): stop double-charging retried webhooks`.

## Trailers, sign-off and attribution

- Git's own trailer handling: `git interpret-trailers(1)` and `git commit --trailer` (git 2.32+) define the
  format this skill's examples use - the last contiguous block of `token: value` lines after a blank line.
- `Co-authored-by: Name <email>` is parsed by GitHub into commit attribution; the kernel-style
  `Co-developed-by:` exists for joint authorship in projects that follow `Documentation/SubmittingPatches`.
- `Signed-off-by:` is the Developer's Certificate of Origin statement (developercertificate.org), required by
  the Linux kernel, Git itself, CNCF projects and many others; `git commit -s` adds it with the configured
  identity.
- `Fixes: <sha> ("<subject>")`, `Reported-by:`, `Reviewed-by:`, `Tested-by:`, `Acked-by:` come from kernel
  patch conventions and are widely borrowed; they are the reason a bisect can start from the fix commit
  itself.
- `Closes #123` / `Fixes #123` closing semantics and the "only closes when merged to the default branch"
  behavior are forge features (GitHub's closing-keywords documentation), which is why the skill puts
  references in trailers rather than the subject.

## Atomicity and change-based commits

The "one logical change per commit, each leaving the tree working" rule is standard version-control practice
and shows up in review-tooling guidance (Google's engineering practices on small CLs, GitHub's own commit
guidance) and in the change-based-commit argument (a commit is what you would describe in one sentence). Its
justification here is mechanical rather than moral: `git bisect`, `git revert` and cherry-picks all operate
per commit, so a mixed commit makes those tools wrong.

## Provenance of the scenario material (references 09-17)

The scenario guidance in [`09`](09-when-to-commit.md)–[`17`](17-command-reference.md) is distilled from a
long "commit like a pro" conversation, reconstructed across **two exports of the same thread** and
cross-checked against each other:

- **`merged.pdf`** — 145 pages after extraction (an earlier viewer hint claimed 410; both `pypdf` and poppler
  report 145, and 25 pages carry no text layer at all). Text extraction yields ~126k characters with 206
  replacement characters from icon-font damage, and roughly a third of the pages are blank. Citations written
  `p.N` are page numbers in this export.
- **`Commit_Like_A_Pro_2026-10-27T10-52-08.pdf`** — the clean pre-OCR original: 65 pages that are really two
  full-resolution screenshot strips. Cited as `orig`.

What the original recovered that the merged export lost: everything after the file-path-scope answer (≈p.95) —
the third multi-file option (drop the scope), scopes-as-vocabulary, subject-line style rules, the footer
`timestamp` mixed-change case, and bulk committing across many README files — plus specifics OCR had mangled:
the `build` type, several `chore:`/`style:`/`test:` examples, and `git commit -S`.

**What is still missing, and is therefore not claimed here.** The original's last strip is cut off mid-code-block
at the screenshot's bottom edge, so the closing lines of the bulk-commit answer are absent. A floating UI bar and
scroll buttons are painted over scattered lines *in the screenshots themselves*; those lines are unrecoverable
from the images and were filled from the merged export's text layer where it survived, and otherwise left out
rather than guessed.

## Errors in the source, reported rather than repeated silently

A guide copied from a conversation inherits the conversation's mistakes. These are corrected above, and the
correction is recorded here so nobody "restores" them from the transcript:

| Source claim | Problem | As shipped here |
|---|---|---|
| `git diff -p > file.patch` (p.41, verbatim in the original) | `-p` is not a `git diff` flag — it is a `git add`/`git reset` option | [`10`](10-hunks-and-splitting.md) uses `git diff > file.patch` and explains why patch files are the weakest parking option |
| `devtools/patches/` guidance (p.43) | tells you both to track the folder and to gitignore it | [`10`](10-hunks-and-splitting.md) states the contradiction and resolves it per project: tracked with a README, or not at all |
| Variable renaming filed under `chore:` (p.66) but under `refactor:` (p.47, p.77) | the same source disagrees with itself | [`11`](11-gray-zones-type-and-scope.md) answers `refactor:` — intent-clarifying structure changes are refactoring, and the thread argues for it twice |
| `__init__.py` → `chore:` (p.142-143) | appears only in `merged.pdf`, not in the original — evidence the merged file was assembled from more than one export | kept, with that caveat stated, in [`11`](11-gray-zones-type-and-scope.md) |

The general rule this section exists to enforce: **when a source and a convention conflict, follow the
convention and note the conflict** — a citation is provenance, not authority.

## Where Commitizen came from, and what the sources each lost

The source names `git cz` (Commitizen) and "pre-commit hooks to block accidental `wip:` commits" once each, in
the closing "Extra: Git Aliases or Tools" section of the `wip:` answer (p.34). Both are one-line suggestions;
the thread never develops either.

Neither export carries the passage intact, and the two files complement each other exactly:

| Source | State of that passage |
|---|---|
| `merged.pdf` (text layer) | the tool name arrives mangled as `Commitize-nf`; the second bullet is complete, including the word "commits" |
| clean original (screenshots) | the tool name is perfectly legible; a floating UI bar is painted over the second bullet, leaving only the fragment `nits` |

So the name came from the original and the noun came from the text layer. That is the whole method of this
reconstruction: **read both, credit which one carried which fact, and leave the gap visible rather than
filling it.**

What is therefore *not* in the guide as recovered material: no Commitizen configuration, no adapter or
framework names (`cz-conventional-changelog` and friends), and no hook script for the `wip:` blocker. The
script that appears in [`07`](07-history-hygiene-and-hooks.md) is **new material, authored here and labelled
as such** — the source names the idea, this skill writes the code. Anyone comparing this guide against the
original should expect that difference and not read it as a citation.
