# Merges and series — the diffs that lie quietly

Two situations produce diffs that are technically correct and practically misleading: merge commits, and a branch
that was rebased or force-pushed. Both have purpose-built tools.

## Why `git show <merge>` seems empty

A merge commit's "diff" is ambiguous — against which parent? By default `git show` prints the combined diff only
for merges that are *not* a trivial auto-merge, and in many cases you get the message with no diff at all. The
default is a convenience, not the truth.

| You want to see | Command | What it shows |
|---|---|---|
| what the branch contributed (relative to mainline) | `git diff <merge>^1 <merge>` | everything brought in — the usual PR view |
| what the merge changed relative to *each* parent | `git show -m <merge>` | one diff per parent, in sequence |
| only the **conflict resolutions** | `git show --cc <merge>` | combined diff: what the merge itself decided |
| resolution as if the merge were recomputed | `git show --diff-merges=remerge <merge>` | the human changes on top of the automatic merge — the most honest view |
| history on the mainline only | `git log --first-parent` | hides the branch's internal commits |

`--remerge-diff` is the one to reach for on a merge that "looks like it lost a change": it re-runs the merge
mechanically and shows only what a human or conflict resolution altered.

## Reading a combined diff

```text
diff --cc src/app.py
index 1111111,2222222..3333333
--- a/src/app.py
+++ b/src/app.py
@@@ -10,6 -10,7 +10,7 @@@
  def handler():            <- two spaces: unchanged in both parents
 -  return old_value        <- removed relative to parent 1 only
 -+ return new_value        <- differs between the parents; the merge chose the '+' form
```

The columns are parents; a line can be an addition relative to one parent and unchanged relative to the other.
Do not count `+`/`-` when there are two columns — read the columns.

## `range-diff` — reviewing a force-push honestly

```bash
git fetch origin pull/123/head:pr-old        # or keep the old SHA you reviewed
git range-diff origin/main...pr-old origin/main...pr-new
```

Output symbols:

| Symbol | Meaning |
|---|---|
| `=` | identical commit (patch unchanged) |
| `!` | same commit intent, **patch changed** — read this |
| `+` / `-` | commit added / dropped in the new version |
| `>` / `<` | commit reordered |

Without `range-diff`, reviewing a rebased branch means re-reading everything and hoping to notice the one line
that changed. With it, you read only `!` rows — usually one or two commits — and you can say "the fix only
changed the test, not the code" with evidence.

The older alternative is an interdiff (`git diff old..new`), which works but mixes the rebase noise with the real
edits. Prefer `range-diff` when the series is a series.

## Long-lived branches and first-parent history

On a branch that merges mainline repeatedly, `git log` interleaves the branch's own commits with merge-noise.
`--first-parent` shows the history as a reviewer experiences it: each merge is one event. Combine:

```bash
git log --first-parent --oneline origin/main..HEAD
git diff --first-parent origin/main...HEAD          # net effect on the branch as a whole
git range-diff --first-parent origin/main...old origin/main...new
```

`--first-parent` is a view, not a filter of the data: the commits exist, you are choosing not to read each one.

## Stacked series

For a PR that is really five PRs:

1. `git log --reverse --format='%h %s' <base>..<head>` — the intended order.
2. `git show <sha>` per commit — one claim per commit, one diff per claim.
3. `git range-diff` against the previous review round if the base moved.
4. Check the seams: does commit 3 depend on a helper introduced in commit 5? A series that only builds at the
   end is a bisect hazard — say so.

## Criss-cross merges and multiple merge bases

```bash
git merge-base --all A B
```

More than one line means the history is criss-crossed; the "merge base" is several commits, and `A...B` picks one
of them. If a diff against the merge base looks wrong, list `--all` and diff against each — the discrepancy is
usually the answer.

## Merge review checklist

- The **resolution** is reviewed, not just the branch: `--remerge-diff` for any merge that touched conflicting
  files.
- **Both sides kept or one deliberately dropped** — a resolution that silently picks "ours" on a shared file is
  the classic lost change.
- **Tests ran on the merge result**, not on each side separately.
- **Conflict markers** gone: `git grep -nE '^(<<<<<<<|=======|>>>>>>>)'`.
- On GitHub/GitLab, the "merge commit" you review is often a squash: the branch's internal history is gone, so
  `range-diff` compares the squash, not the commits.
