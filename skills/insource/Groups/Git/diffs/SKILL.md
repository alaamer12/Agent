---
name: diffs
version: 1.1.0
author: Amr
specialized: git
description: 'Read git diffs like evidence, not text: triage huge diffs and search diff history. Establishes the right baseline (A..B vs A...B, worktree/staged/HEAD, merge base), surveys a change set (stat, name-status, renames, generated/binary/whitespace), reads hunks correctly (arithmetic, function context, word-diff, color-moved), spots risk (removed error handling, changed defaults, boundaries, mode bits, dependency and migration changes, secrets), and searches with pickaxe -S/-G, message-level --grep, log -L, git grep at a revision, range-diff, remerge diffs. Topic dossier (--topic): messages + code + history in four budgeted channels, never a -p dump. Also answers "is this diff truthful?" - message vs changes, tests present, debug leftovers, partial staging, scope creep. Ships scripts/diff_survey.py (deterministic triage, --json, --fail-on, budgets). Use for reviewing PRs or commits, investigating what a commit did, hunting where a string was added or removed, or when a diff is too large to read.'
when_to_use: The user asks what a commit/PR/branch changed, asks to review a diff, points at a huge or confusing diff, asks where a string or behaviour was introduced or removed, or a change must be verified against its description.
argument-hint: "[range|staged|worktree|merge <sha>] [path...]"

---

# Diffs

A diff is **evidence about behaviour**, not a wall of plus and minus signs. Read it the way an investigator reads
a record: establish what is being compared, triage by risk, then read only the hunks that can change the answer.

```text
baseline  ->  survey  ->  triage  ->  read hunks  ->  search if needed  ->  verify the claim  ->  report
```

The failure modes this skill prevents: reviewing a rename as a delete plus a 400-line add; concluding "no
changes" from an empty `git show` on a merge; reading a 12,000-line lockfile before the 30-line logic change;
trusting a diff whose message says one thing and whose hunks do another.

## Step 0 — establish the baseline before reading a line

"The diff" is undefined until you say which two trees.

| You want | Command | Trap |
|---|---|---|
| PR/branch vs upstream | `git diff origin/main...HEAD` (three dots) | two dots shows work *on main* as if it were yours |
| One commit | `git show <sha>` | shows nothing for merge commits — see [`04`](references/04-merges-and-series.md) |
| Staged only | `git diff --cached` | worktree edits are invisible |
| Worktree only | `git diff` | staged changes are invisible |
| Everything vs HEAD | `git diff HEAD` | untracked files are still invisible — `git add -N <path>` first |
| A merge | `git show --cc <merge>` or `git show --diff-merges=remerge <merge>` | default `git show` silently prints no diff |
| Two arbitrary trees | `git diff --no-index dirA dirB` | no repo needed; useful for "old vs new" snapshots |

Say the baseline out loud in your report — a review of the wrong range is worse than no review.

## Step 1 — survey, do not read yet

```bash
python scripts/diff_survey.py --range origin/main...HEAD     # deterministic map + flags + risk summary
python scripts/diff_survey.py --staged --json                # machine-readable
git diff --stat -M -C <range>                                # what the human needs on one screen
git diff --name-status -M -C <range>                         # A/M/D/R/C/T, rename source and target
git diff --summary <range>                                   # renames, mode changes, create/delete
```

The survey gives per-file status, churn, and flags — `rename`, `binary`, `ws-only`, `generated`, `dependency`,
`migration`, `ci`, `config`, `deleted-test`, `secret-shaped` — plus a risk summary. It is the reading order.

Run from a subdirectory and the paths are repo-root-relative; add `--relative` (or `--relative=<dir>`) when you
want paths as the caller sees them.

## Step 2 — triage by risk, not by filename order

**Deletions first** — removed lines are where behaviour disappears; additions are visible, deletions are silent.
Then manifests and lockfiles, migrations and config, core logic, tests, and last the generated mass. The full
reading order, the size thresholds, the risk checklist and what to do when the diff is too big to be a diff:
[`01-triage-and-risk.md`](references/01-triage-and-risk.md).

## Step 2b — one function out of a 5 000-line diff (context is a budget)

When the question is about one part, **never load the diff**: put it on disk with `--to-file`, index it with
`--hunks` (every hunk named by function and priced in bytes), fetch one with `--hunk 1 --budget 4`, or slice a
revision with `--at <rev> --path <file> --lines A:B` / `--grep RE` — deleted files included. The narrowing
ladder, the `--to-file`/stderr trap on `core.autocrlf` trees, the row caps, and the one-giant-hunk fallbacks:
[`05`](references/05-token-efficient-reading.md).

## Step 3 — read the hunks correctly

The format carries meaning; reading it carelessly invents differences. Two laws: **always diff with `-M`** — a
rename is not a delete plus an add — and if a diff looks insane, re-run it with
`--diff-algorithm=histogram` (or `patience`) before believing it. The headers and hunk arithmetic, the function
context, word-diff and colour-moved markers, binary, encodings and line endings:
[`00-anatomy-of-a-diff.md`](references/00-anatomy-of-a-diff.md).

## Step 4 — search inside and around the diff

When the question is "where did this come from" rather than "what does this hunk say":

```bash
git log -S'<literal>' --oneline -p -- path/        # pickaxe: commits that changed the NUMBER of occurrences
git log -G'<regex>'  --oneline -p -- path/         # commits where an added/removed line MATCHES the regex
git log --grep='<topic>' -i --format='%h %s'       # commit MESSAGES - a channel -S/-G never search
git log -L :function:path -p                       # history of one function, not one file
git grep -n '<pattern>' <rev> -- path/             # search a snapshot, not the worktree
git range-diff origin/main...v1 origin/main...v2   # what changed between two versions of a series
```

**"Extract everything about topic X" is a dossier, not one search** — four channels in cheapest-first order,
patches pointed at but never auto-dumped:

```bash
python scripts/diff_survey.py --topic Sentry [--cwd <repo>] [--rev <snap>] [--budget KB] [--max-rows N]
```

[`02`](references/02-searching-diffs.md) has the channels, the measured bill (~50 k tokens of `-S … -p` patches
against ~600 for the complete dossier), and the rest of the search toolkit.

## Step 4b — the range spans commits: read the path, not just the endpoints

An aggregate diff answers *"what differs at the end"*; experiments, reverts, authorship and motive need the
per-commit level: `--per-commit` with its hidden-churn report, `git log -L`, `git blame -w -M -C`, `--follow`.
Three commits that add an experiment, revert it and make the real change aggregate to **`1 file changed,
1 insertion`** — [06](references/06-across-commits.md).

## Step 5 — verify the claim, not just the diff

A diff can be internally consistent and still not do what its message, PR body or ticket says. Hold the hunks
against the claim (a missing hunk is an unshipped claim, an unrelated hunk is scope creep), then the tests
(present, real, unweakened), the leftovers, staged vs worktree, regenerated artifacts and secrets in added
lines — [`03-truthfulness-review.md`](references/03-truthfulness-review.md).

## Step 6 — merges and series

Merge commits are where diffs lie most convincingly: `git show` prints nothing, `git diff <merge>^ <merge>`
shows the unrelated mainline work, and combined diffs need a different reading. Use `--cc`, `--remerge-diff` to
see only what the resolution changed, `--first-parent` when the branch is long-lived, and `git range-diff` to
review a force-pushed series ([`04`](references/04-merges-and-series.md)).

## Step 7 — report

Short, evidence-first ([`assets/templates/diff-review-report.md`](assets/templates/diff-review-report.md)):

```text
Baseline: <range and why> · <n files, +a/−d, renames r, binary b>
Read: <the hunks that matter, with path:line at the new side>
Risk: <flags that survived inspection, with one line each>
Not shown / unknown: <untracked, skipped generated files, untested paths>
Verdict: <does it do what it claims? what would falsify that?>
```

## Pitfalls that change conclusions

Every trap that flips a conclusion — the wrong baseline, the forgotten `-M`, whitespace read as logic, an
aggregate read as the story, `blame` read as authorship, a single sha given to `--range` — is tabulated with its
reality in [`07-pitfalls-that-change-conclusions.md`](references/07-pitfalls-that-change-conclusions.md). Read
it before you report.

## Scripts and assets

| Path | Owns |
|---|---|
| `scripts/diff_survey.py` | `--range` · `--staged` · `--worktree` · `--merge` · `--path` · `--json` · `--fail-on high`; deterministic per-file map + risk flags. Context budgeting: `--file` · `--to-file` · `--hunks [--match]` · `--hunk 1,4` · `--budget KB` · `--force` · caps of 40 rows. Content at a revision: `--at REV --path F --lines A[:B]` / `--grep RE [--context N]` (deleted files included, 16 KB default budget, **binary blobs refused rather than dumped**). Commit level: `--cwd <repo>` · `--per-commit [--max-commits 15] [--max-hidden 10] [--first-parent]`. Topic level: `--topic <word> [--rev] [--max-rows 15] [--budget]` - one budgeted dossier of messages + per-file counts + pickaxe history, case-insensitive, subjects clipped at 120 chars, patches pointed at only. Self-test with no arguments (39 checks) |
| [`references/00-anatomy-of-a-diff.md`](references/00-anatomy-of-a-diff.md) | headers, hunk arithmetic, renames, modes, binary, combined diffs, word-diff markers |
| [`references/01-triage-and-risk.md`](references/01-triage-and-risk.md) | reading order, size thresholds, the risk checklist, big-diff strategies |
| [`references/02-searching-diffs.md`](references/02-searching-diffs.md) | pickaxe -S/-G, message-level `--grep`, the topic dossier (`--topic`), `-L`, range-diff, grep at a rev, orderfile, algorithms, parsing `-z` |
| [`references/03-truthfulness-review.md`](references/03-truthfulness-review.md) | message vs hunks, tests, leftovers, partial staging, scope creep, secrets |
| [`references/04-merges-and-series.md`](references/04-merges-and-series.md) | merge diffs (`--cc`, `--remerge-diff`, `-m`, `--first-parent`), `range-diff` for series |
| [`references/05-token-efficient-reading.md`](references/05-token-efficient-reading.md) | the narrowing ladder, hunk addressing and budgets, what to do when a file diffs as one hunk, sub-agent handoffs |
| [`references/06-across-commits.md`](references/06-across-commits.md) | per-commit reading and hidden churn, `log -L`, what blame does and does not answer, `--follow`, `range-diff`, choosing the level |
| [`references/07-pitfalls-that-change-conclusions.md`](references/07-pitfalls-that-change-conclusions.md) | the trap/reality table: baselines, renames, whitespace, generated mass, `autocrlf`/`quotepath`, loaded context, hidden churn, blame, `--range` with one sha |
| [`assets/templates/diff-review-report.md`](assets/templates/diff-review-report.md) | the seven-line report |
