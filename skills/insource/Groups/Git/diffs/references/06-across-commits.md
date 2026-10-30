# Across commits — reading history, not just a snapshot

A range diff answers *"what is different at the end"*. Most real questions are about the path between: what was
tried, what was reverted, who last touched this line, why. Those need different tools, and the aggregate diff
actively misleads for all of them.

## The cancellation trap (measured)

Three commits in a range: `c2` adds an experimental line, `c4` removes it, `c5` makes the real change.

```text
git diff --stat BASE..TIP     ->  core.py | 1 +     "1 file changed, 1 insertion"
--per-commit                  ->  c5 +1/-0 · c4 +0/-1 · c2 +1/-0
HIDDEN CHURN - core.py  aggregate +1/-0  but 3 commits sum +2/-1
```

Reading the aggregate, you would conclude "a one-line addition" and never learn that the file carried dead
experimental state for two commits — which is exactly the window where a production build off `c3` misbehaves.
**Any range with more than ~2 commits gets read per commit first, aggregate second.**

```bash
python scripts/diff_survey.py --per-commit --range BASE..TIP          # map + hidden churn
python scripts/diff_survey.py --range <sha> --hunks                   # drill into the one commit that matters
python scripts/diff_survey.py --range <sha> --hunk 3 --budget 8
```

`--cwd <repo>` works in every mode, so the survey can run against a different checkout or a sub-agent's
workspace. `--first-parent` restricts the list to the mainline — essential in merge-heavy history, where
`HEAD~20..HEAD` is **98 commits**, not 20 (measured on a 2 098-commit repo, 52 merges).

**Merges are excluded from churn accounting.** A merge's first-parent diff repeats the very commits the range
also lists, so counting both doubles the totals and invents hidden churn — the first real-repo run of this tool
reported 461 files as cancelled when only 87 were. Rows still appear, tagged `merge`.

Costs measured on that repo (one batched `git log --numstat`, caps applied):

| Command | Time | Output |
|---|---|---|
| `--per-commit --range HEAD~20..HEAD` | 5.0s | 2.4 KB (~620 tokens), 15 rows + top 10 churn |
| same, before the caps and batching | 33.8s | 44 KB (~11 k tokens) |
| `--per-commit --range HEAD~300..HEAD --max-commits 12` | 15.8s | 1.8 KB (~456 tokens) |
| `--range HEAD~300..HEAD --json --max-files 5` | 4.8s | 5.9 KB |
| `--range HEAD --hunks` (HEAD is a merge) | 0.3s | 4.6 KB, 130 hunks priced at 124 KB |

Uncapped, `--per-commit` over 300 commits emitted 279 KB — which is why `--max-commits` (15) and
`--max-hidden` (10) exist and why the tool prints how many rows it withheld.

`--cwd <repo>` on every mode so the survey can run against a different checkout or a sub-agent's workspace.

## `git log -L` — the cheapest correct answer about a function

```bash
git log -L :compute_totals:src/billing.py            # whole history of that function
git log -L 40,80:src/billing.py -p                   # a line range, following it as it moves
git log -L :/def refresh/:auth.py BASE..TIP          # bounded to the range, by regex when names repeat
```

Measured on a 5-commit range where the aggregate showed one changed line: `log -L` returned 970 bytes (~240
tokens) and contained the entire true story — the experiment, the revert, the real change. A `git diff` of the
whole range costs the same and shows less. **Prefer `-L` whenever the question names a function.**

## `git blame` — what it is good at, and what it lies about

```bash
git blame -L 40,60 -- src/billing.py                 # who last touched each line, and in which commit
git blame -w -M -C -L 40,60 -- src/billing.py        # ignore whitespace, follow moves and copies
git blame --since=2026-10-01 -L 40,60 -- src/billing.py
```

| Question | blame answers it? |
|---|---|
| "which commit last modified this line" | yes, exactly |
| "who wrote the logic" | **no** — a moved, reformatted or copy-pasted line blames its last mover |
| "what did the line look like before, and why did it change" | no — follow up with `git show <sha>` or `log -L` |
| "was this line ever different inside this range" | **no** — a line added then deleted never appears |
| "does the same bug exist in a copy of this file" | only with `-C -C` (detect copies), which is slow and off by default |

Use `-w -M -C` when blame keeps pointing at an unrelated commit after a refactor — that pointer is usually a
move, not an authorship.

## Following a file through renames

```bash
git log --follow --oneline -- src/formatting.py      # stops following after ~one rename unless -C given
git log --oneline --follow --find-renames -- src/formatting.py
git show <sha>:src/util.py                           # the pre-rename content at a known commit
```

`git log -- path` without `--follow` **ends at the rename**, so the file looks like it was created recently — a
common way to conclude "no history here" where there is years of it.

## Comparing two versions of the same work

```bash
git range-diff origin/main...pr-v1 origin/main...pr-v2
```

Symbols: `=` unchanged · `!` patch changed (read these) · `+`/`-` commit added/dropped · `>`/`<` reordered.
Without it, a second review of a rebased branch is a full re-read hoping to notice one edit.

## Searching a range rather than a snapshot

```bash
git log -S'<literal>' --oneline -- path/             # commits that changed the occurrence count
git log -G'<regex>' --oneline -p -- path/            # commits whose added/removed lines match
git log --format='%h %s' BASE..TIP -- src/core.py    # which commits touched this file
git rev-list --count BASE..TIP                       # how deep the range is, before choosing a method
```

## Choosing the level

| Question | Level | Cost |
|---|---|---|
| "what is the net difference" | aggregate `--stat`, then `--hunks` index | smallest |
| "what did the team try and abandon" | `--per-commit` + hidden churn | one row per commit |
| "why is this function shaped like this" | `git log -L :func:path` | one small diff per touching commit |
| "which commit last touched this line" | `blame -L` with `-w -M -C` | a few lines |
| "what changed between review rounds" | `range-diff` | only the `!` commits |
| "which commit broke it" | bisect, or `--per-commit` then test each candidate | log₂(n) runs, not n |

The default mistake is picking the aggregate for a question that is about the path.
