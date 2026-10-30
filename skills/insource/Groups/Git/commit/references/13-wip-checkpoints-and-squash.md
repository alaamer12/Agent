# WIP, checkpoints, and when to squash

Two-phase discipline, and the single mental model that decides most cleanup questions:

> **Commits are personal checkpoints; a squash is a public statement.** (p.62)

## The `wip:` family (p.30–34)

`wip:` means "work in progress — not done, not reviewed". It is **not** a Conventional Commits type, and it is
universally understood. Legitimate homes (p.31): named stashes
(`git stash push -m "wip: started report section"` — named beats anonymous clutter) and temporary commits
(`git commit -am "wip: save progress"` — short-term only).

Informal staging keywords the source endorses as "not official, but incredibly helpful for team context"
(p.33–34):

| Keyword | Meaning | Cleanup |
|---|---|---|
| `wip:` | incomplete work | squash into the real `feat:`/`fix:` |
| `temp:` | temporary hack or dirty fix | reword, or replace with the real fix |
| `debug:` | added logs or instrumentation | drop before merge |
| `try:` | a hypothesis being tested | drop or squash |
| `checkpoint:` | messy milestone backup | squash |
| `save:` | don't-lose-my-work commit | drop |
| `wip-fix:` | a real fix parked in the wrong place | cherry-pick to `fix/*`, then reword |

Hygiene: history browsers and forge tooling already surface `wip:` (p.32) - [tig], [Magit], [gitk], a `git log --grep=wip` query, or the PR checks on the host. Convenience alias
(p.34): `git config --global alias.wip '!git add -A && git commit -m "wip: save progress"'`.

These prefixes are a **staging vocabulary**, not a shipping vocabulary. `commit_lint.py --history` reports them
when they appear on a shared branch.

## The three-phase discipline (p.33)

1. **During development** — commit freely: wip, temp, debug, all of it. Progress insurance, faster isolation,
   survivable interruptions, partial reverts (p.57).
2. **Once it works** — clean the history: squash `wip:` into proper types, drop or reword `temp:`/`debug:`.
3. **Before sharing** — push only polished commits to PR/release branches. A pre-commit or CI rule can block
   `wip:` from ever reaching a production branch (p.34).

## The multi-day pattern (p.56–58)

Mid-development history:

```text
chore: scaffold initial structure for user profile
feat: implement data model for profile
feat: connect backend API
fix: handle null values in profile form
test: add unit tests for profile validation
style: run formatter
```

Cleanup before merge:

```bash
git rebase -i origin/main
# pick the first commit, squash the rest, final message:
# feat: implement complete user profile feature
#
# Includes model, API, form handling, and unit tests.
```

Team shortcut (p.58): keep small commits on the branch and let GitHub/GitLab **squash-merge** do the cleanup at
merge time — "best of both worlds." Cadence rule of thumb: commit at every meaningful step — model done, API
working, UI wired, test added.

Anti-patterns (p.58): one giant commit after four days (no safety net, cannot bisect, unreviewable); leaving
`wip`/`update again` spam in a merged branch; force-pushing shared work without a reason.

## When squashing is right (p.59)

1. You want a clean linear history for review and release notes — `feat: add report export functionality`
   beats a trail of `wip: trying export logic` and `temp: debugging`.
2. The team enforces a clean `main` via the squash-merge button.
3. Pre-release cleanup: `git rebase -i HEAD~8`, squash the mess, and the PR becomes one reviewable
   `feat: add invoice PDF generation`.

## When squashing is wrong (p.60–61)

1. **The development trace has value** — R&D and algorithm work:
   `feat: add base algorithm` → `refactor: decouple I/O from core logic` →
   `perf: improve matrix loop performance` → `fix: edge case with zero weights` → `test: add edge case tests`.
   Each step is knowledge; flattening them destroys the record of what was learned.
2. **You need `git bisect`** — a fully squashed commit is one binary unit: either it works or it does not, and
   a 40-commit range collapses to one suspect.
3. **Shared branches** — others build on your commits; squashing forces conflict-prone force-pushes.

Bottom line (p.61): commit as often as useful; squash before merging **only if the individual steps have no
long-term value**; never squash `main` or shared history unless you are certain.

## "Won't squashing create huge commits?" (p.62–63)

Only if misused. Squashing is meant to create *coherent* commits, not large ones.

- Golden rule: one commit = one complete, understandable unit (`feat: add PDF export` ✓).
- Anti-example: `feat: add PDF export, fix bug with date parsing, refactor user model, change CSS, update
  tests` — "that's not one unit — that's a dump."
- Healthy grouping: export stub + export logic + export tests squash together;
  `refactor: extract reusable date formatters` stays its own commit.
- **The 1–2 minute test** (p.63): if a squashed commit takes longer than that to understand, split it.
- Don't squash everything: only exploratory noise. Commits that "stand on their own" survive.

## "But the diff is 800 lines!" (p.65–66)

Big ≠ bad.

- **Fine:** one coherent atomic unit — `feat: implement markdown rendering engine` (~800 lines: parser,
  renderer, editor integration, basic tests), logically grouped, reviewed as a whole.
- **Bad:** unrelated changes glued for tidiness — `feat: add payment system and fix login bug and also change
  navbar design` (1,200 lines, 15 files): unreviewable, un-revertable, non-atomic.
- The test (p.66): **"Is this one thing, or several things?"** Several → split.
- Tools that keep big work honest: `git add -p`, `git rebase -i`, `git diff --stat` (watch the counts), and
  feature toggles, which let a large feature ship as several flag-gated commits.
- Reference sizes from a good split (p.65): payment API 600 lines / race-condition fix 25 / navbar spacing 80 —
  each its own commit.

## "My merged branch left exactly one commit on main — did I lose history?" (p.67–69)

No. That is the design of GitHub flow and GitLab squash-merge: `main` stays linear, each commit is one purpose,
and the *process* — intermediate commits, review comments, discussion — lives permanently in the PR/MR.
"That commit is like the final polished result, not the messy thought process" (p.68).

Make the surviving commit carry the context in its body (p.68):

```text
fix: handle incorrect dates in report generation

- root cause: timestamp parsing failed when input had non-UTC format
- added fallback to ISO parsing with timezone awareness
- updated tests to cover edge cases
- confirmed fix with legacy CSV inputs
```

When **not** to squash to one (p.68–69): very complex refactors or migrations; anywhere bisect granularity
matters; merging into a long-lived integration branch → "rebase but don't squash, or squash selectively."

Hybrid policy (p.69): short-lived feature/fix branch → squash. Large refactor or deep bug → keep the logical
commits and squash only the noise. Need traceability → rich messages plus the PR record. The named trade-off is
real: **clean history vs full traceability**, balanced with smart commit messages and PR documentation.
