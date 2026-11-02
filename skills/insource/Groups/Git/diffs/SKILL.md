---
name: diffs
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

Read in this order ([`01-triage-and-risk.md`](references/01-triage-and-risk.md)):

1. **Deletions first** — removed lines are where behaviour disappears (error handling, validation, tests,
   defaults). Additions are visible; deletions are silent.
2. **Dependency manifests and lockfiles** — a version bump explains a hundred other hunks; read the manifest,
   skim the lock.
3. **Schema migrations and config** — irreversible or environment-shaped.
4. **Core logic** — the hunks with a `@@ … @@ <function context>` header naming something that matters.
5. **Tests** — are there any? Do they test the change or merely touch it?
6. **Generated / vendored / minified** — confirm they were regenerated, then skip.

`git diff -O orderfile` puts your paths first; `--dirstat` shows where the mass sits before you open anything.

## Step 2b — one function out of a 5 000-line diff (context is a budget)

When the question is about one part, **never load the diff**. Put it on disk, index it, fetch by id:

```bash
python scripts/diff_survey.py --to-file /tmp/big.diff --range origin/main...HEAD
python scripts/diff_survey.py --file /tmp/big.diff --hunks --match compute_totals
python scripts/diff_survey.py --file /tmp/big.diff --hunk 1 --budget 4
```

Use `--to-file` rather than calling `git diff` yourself: on a Windows tree with `core.autocrlf`, git writes one
stderr warning per CRLF file, and a 130-file working tree produced ~15 k tokens of warnings in testing. The
script captures stderr, so noise never reaches context.

The index names every hunk by its function/section and **prices it in bytes before you read it**; `--budget`
refuses to print past the limit, and both the index and the file survey cap at 40 rows (`--max-hunks`,
`--max-files`) — narrow with `--match`/`--path` before raising them. One hunk of an 885 KB diff then costs ~150
bytes of context instead of 221 k tokens. If the index shows a single giant hunk, the file is effectively a
rewrite — switch to `git log -L :func:path`, `--diff-algorithm=histogram`, or a region read:

```bash
python scripts/diff_survey.py --at <rev-before> --path doomed.py --lines 1000:1004   # 300 B, not 58 909 B
python scripts/diff_survey.py --at <rev-before> --path config.yaml --grep 'timeout' --context 3
```

`--at` reads a slice or the matches **of a file at a revision** — including deleted ones, whose content exists
nowhere else. It carries its own 16 KB default budget (`--budget`, `--force`), and when a fetch is refused the
tool suggests exactly this command. ([`05`](references/05-token-efficient-reading.md))

## Step 3 — read the hunks correctly

The format carries meaning; reading it carelessly invents differences
([`00-anatomy-of-a-diff.md`](references/00-anatomy-of-a-diff.md)):

- `@@ -old_start,old_count +new_start,new_count @@ context` — the counts are the contract; a hunk that adds 2 and
  removes 2 is often a rewrite of the *same* lines, not four changes.
- `-M` / `-C` turn "delete 400, add 400" into `similarity index 96%`, `rename from/to`. **Always diff with `-M`.**
- `-w` shows whether anything changed beyond whitespace; `--ignore-cr-at-eol` for line-ending churn. Compare
  `--numstat` with and without `-w` — equal numbers mean a whitespace-only edit.
- Long lines: `--word-diff=plain` (or `=porcelain` for parsing) shows the token that changed.
- Moves: `--color-moved=zebra` (with `--color=always` when piping) separates moved blocks from edits.
- A messy diff can be an artifact of the algorithm: `--diff-algorithm=histogram` (or `patience`) usually aligns
  refactors more sensibly than the default Myers. If a diff looks insane, re-run it before believing it.
- Binary: `--numstat` shows `-  -`; use `--binary` only when you need the patch, `--text` to force a textual
  read of something git classified as binary.

## Step 4 — search inside and around the diff

When the question is "where did this come from" rather than "what does this hunk say"
([`02-searching-diffs.md`](references/02-searching-diffs.md)):

```bash
git log -S'<literal>' --oneline -p -- path/        # pickaxe: commits that changed the NUMBER of occurrences
git log -G'<regex>'  --oneline -p -- path/         # commits where an added/removed line MATCHES the regex
git log --grep='<topic>' -i --format='%h %s'       # commit MESSAGES - a channel -S/-G never search
git log -L :function:path -p                       # history of one function, not one file
git grep -n '<pattern>' <rev> -- path/             # search a snapshot, not the worktree
git range-diff origin/main...v1 origin/main...v2   # what changed between two versions of a series
git diff <rev> -- <path> | grep -n '^[+-]'         # narrow a huge hunk stream to changed lines only
```

`-S` answers "when did this appear/disappear"; `-G` answers "when did a line mentioning it change"; `--grep`
answers "what did humans *say* about it" — a channel the diff scanners never see. Choosing the wrong one is the
most common reason a search "finds nothing".

**"Extract everything about topic X" is a dossier, not one search** — four channels (messages, code-at-rev
counts, `-S` history, `-G` count-vs-history) in cheapest-first order, patches pointed at but never auto-dumped:

```bash
python scripts/diff_survey.py --topic Sentry [--cwd <repo>] [--rev <snap>] [--budget KB] [--max-rows N]
```

Measured on a mid-size app repo: `git log -S Sentry -p` cost ~50 k tokens; the complete dossier was ~600 —
and it surfaced the merge-commit message the diff-only searches had no channel for
([`02`](references/02-searching-diffs.md) §topic dossier).

## Step 4b — the range spans commits: read the path, not just the endpoints

An aggregate diff answers *"what differs at the end"*; questions about experiments, reverts, authorship and
motive need the per-commit level ([`06`](references/06-across-commits.md)):

```bash
python scripts/diff_survey.py --per-commit --range BASE..TIP    # one row per commit + HIDDEN CHURN report
python scripts/diff_survey.py --per-commit --range BASE..TIP --cwd ../other-checkout
git log -L :function:path                                        # the whole history of one function, cheaply
git blame -w -M -C -L 40,60 -- path                              # last touch (not authorship)
git log --follow --oneline -- renamed/path                       # without --follow it stops at the rename
```

A measured example of why this matters: three commits (`add experiment`, `revert experiment`, `real change`)
aggregate to **`1 file changed, 1 insertion`** — the experiment and its revert cancel out and are simply absent.
`--per-commit` reports them and flags the file as hidden churn. Use the per-commit level for any range with more
than about two commits, then drill into the one commit that matters.

## Step 5 — verify the claim, not just the diff

A diff can be internally consistent and still not do what its message, PR body or ticket says
([`03-truthfulness-review.md`](references/03-truthfulness-review.md)). Check:

- **Message vs hunks** — does every behaviour the message claims have a hunk? Does every hunk belong to the
  message? Unrelated hunks are scope creep; a missing hunk is an unshipped claim.
- **Tests** — present in the diff? Changed to match new behaviour, or weakened to pass?
- **Leftovers** — `console.log`, `print(`, `TODO`, commented-out blocks, debug flags, temporary sleeps.
- **Staged vs worktree** — `git status --short` plus both diffs; a "complete" change is often only staged.
- **Regenerated artifacts** — committed build output, lockfile without a manifest change, snapshots updated
  without a test change.
- **Secrets and data** — scan added lines, not the whole file.

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

| Trap | Reality |
|---|---|
| "No diff" | merge commit, untracked file, wrong baseline, or path outside the range |
| Rename read as delete+add | you forgot `-M`; the "new" file is the same code |
| Whitespace noise hides a one-line change | `-w` before concluding "only formatting" |
| `git diff` shows nothing | the change is staged: `git diff --cached` |
| Huge generated file read line by line | the information is the regenerated diff, not the content |
| `autocrlf` rewrites every line | diff with `--ignore-cr-at-eol`; never review line endings as logic |
| Non-ASCII paths print as `\344\275\240` | `git -c core.quotepath=false diff …` |
| Piped output with no colour | `--color=always` when `--color-moved` matters |
| Diff agrees with the message, code does not compile | the diff is not the system; run it if the claim is behavioural |
| Whole diff loaded to answer one question | context spent for nothing — index first, `--hunks` then `--hunk --budget` |
| `git show <sha>` to see a deleted file | the commit prints the whole deletion — `--at <rev-before> --path F --lines/--grep` |
| Aggregate range read as the story | commits that cancel out are invisible: `--per-commit` exposes hidden churn |
| `blame` treated as authorship | it reports the **last touch** — a move or reformat reassigns the line; use `-w -M -C`, then `log -L` |
| "This file has no history" | `git log -- path` stops at a rename — add `--follow` |
| Topic hunt answered by dumping every patch | `git log -S topic -p` can run to tens of k tokens in a few-hundred-commit repo; the `--topic` dossier said more in ~600 - and covered the message channel too |
| `--range <single-sha>` treated as worktree | a single revision means **that commit's own diff**; use `--worktree`/`--staged` for local state |

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
| [`assets/templates/diff-review-report.md`](assets/templates/diff-review-report.md) | the seven-line report |
