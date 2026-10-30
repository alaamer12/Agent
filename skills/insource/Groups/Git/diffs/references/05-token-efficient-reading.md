# Token-efficient reading — the diff is data, not reading material

The context window is a budget you spend once per session. A 50 KB hunk is roughly 12 k tokens of *one* hunk;
three of those and the session is over, with most of it spent on lines that were never relevant. So the rule is
not "read carefully" — it is **narrow before you load**.

## The narrowing ladder

Stop at the first rung that answers the question. Each rung costs less than the one below it.

| Rung | What you load | Cost | Answers |
|---|---|---|---|
| 1 | `git diff --stat <range>` / `--name-status` | tens of lines | which files, how much |
| 2 | `scripts/diff_survey.py --range …` | one table + flags | what kind of change, where the risk is |
| 3 | `--hunks [--match X]` | the hunk **index** | which function changed, and what it would cost to read |
| 4 | `--hunk 7 --budget 8` | one hunk | the actual lines |
| 5 | `Read` with offset/limit on the file | a region | surrounding logic the hunk cannot show |
| 6 | the whole file | everything | only when the file is small or you are rewriting it |

The trap is jumping from 1 to 6 because `git diff` is one keystroke away.

## Addressing a hunk instead of dumping a diff

```bash
python scripts/diff_survey.py --to-file /tmp/big.diff --range origin/main...HEAD
python scripts/diff_survey.py --file /tmp/big.diff --hunks --match compute_totals
#   ID   FILE              +/-   BYTES   FUNCTION / SECTION
#   1    billing.py        1/1     149   def compute_totals(day):
#   2    tests/x.py        1/1     157   def test_totals():
python scripts/diff_survey.py --file /tmp/big.diff --hunk 1 --budget 4
```

`--to-file` exists because **calling `git diff` directly can leak more than the diff**: on a Windows working tree
with `core.autocrlf`, git prints one `warning: in the working copy of …` line per CRLF file to stderr, and a
130-file tree produced ~15 k tokens of warnings in live testing — the same order as the answer. The script
captures stderr, so warnings never reach context. Calling git yourself? `git diff --output=/tmp/big.diff <range>
2>/dev/null`.

- `--budget KB` **refuses** to print past the budget. That refusal is the feature: it forces the narrowing step
  instead of letting a huge hunk through "because it was requested".
- The BYTES column is the price, quoted *before* purchase. An index that sums to 60 KB is telling you to change
  strategy, not to read it anyway.
- The index is **capped at 40 rows** (`--max-hunks`) and the file survey at 40 (`--max-files`): a full 330-row
  index cost 19 KB of context in testing to answer nothing. Narrow with `--match`/`--path` before raising caps.

## Reading a region out of a deleted or rewritten file

A deleted 2 000-line file is the worst case for the naive approach: the diff carries all 2 000 removed lines, so
`git show <sha>` puts ~14 k tokens in context to answer a question about twelve of them. The hunk index prices it
honestly (**58 909 bytes, ~14 727 tokens**, loaded: nothing), and `--at` reads what you asked for instead:

```bash
python scripts/diff_survey.py --at <rev-before> --path doomed.py --lines 1000:1004
python scripts/diff_survey.py --at <rev-before> --path doomed.py --grep 'cleanup|TODO' --context 3
```

```text
743b23d6:doomed.py  lines 1000-1004 of 2000  (total file 56890 bytes ~14222 tokens)
  1000| line 999 of the doomed file
  ...
```

Measured: **300 bytes** for the slice, **951 bytes** for a 5-match grep — against 58,909 for the hunk. The file
never has to exist any more; only the revision does. Same tool for a binary-looking rewrite, a file the diff
collapses into one hunk, or "what did this config say before it was removed".

Budget: `--at` applies the same discipline as everything else — a **16 KB default**, `--budget N` to change it,
`--force` to override. Asking for lines 1–5 000 of a 3 000-line file is a mistake, not an instruction, and it is
refused rather than obeyed. `--path` must exist at that revision; if it does not, the error suggests
`git log --follow --name-only -- <path>` because the file was probably renamed, not deleted.

**Binary content is refused, not dumped.** A deleted PNG asked for as `--lines 1:5` would otherwise return
kilobytes of noise presented as text (this happened on a real repo during testing). The guard checks for NUL and
`%PDF` markers and answers with what is actually useful:

```text
refused: img.png at fe79fe6e is binary (11 bytes) - diff and text slices cannot help here
  content:  git show fe79fe6e:img.png > <out-file>
  metadata: git cat-file -s fe79fe6e:img.png ; git log --follow --oneline -- img.png
```

## When the index shows one giant hunk

A 900-line single hunk means the algorithm could not align the file — it is effectively a rewrite. Reading it is
the worst option. Take one of these instead:

```bash
git diff --diff-algorithm=histogram --output=/tmp/big2.diff <range>   # often splits it
git diff --anchored='^\s*(def|class|function|export) ' -- <path>      # anchor on declarations
git show <rev>:<path> | sed -n '40,120p'                              # just the new version's region
git log -L :compute_totals:<path> -p                                   # the function's own history
git diff --word-diff=porcelain -U0 -- <path>                          # token-level, when only a few words changed
```

`git log -L` is usually the cheapest correct answer to "what happened to this function", because it prints one
small diff per commit that touched it, and nothing else.

## Budgeting rules that keep a session alive

- **Never `cat` a diff into context.** Write it with `--output`, then index and fetch.
- **One read per question.** If you are asking "did the guard change?", the answer is one hunk, not the file.
- **Generated files: read the generator's diff, not the output.** A minified bundle or lockfile hunk is
  information about a tool, not about intent.
- **Skip before you skim.** `--diff-filter`, pathspecs, and `':(exclude)dist/**'` remove whole classes of hunk;
  scrolling them is not "being thorough".
- **Delegating to a sub-agent: hand it the index and the hunk ids,** not the diff text. Otherwise the context
  cost is paid twice.
- **Count as you go.** If you have loaded three large hunks and the question is still open, the problem is that
  the question was wrong — reformulate it (usually into "which function owns this behaviour?").

## Rough conversion, so the numbers mean something

| Bytes | Approx. tokens | Verdict |
|---|---|---|
| ≤ 2 KB | ~500 | free — read it |
| 2–10 KB | ~0.5–2.5 k | fine for one hunk |
| 10–50 KB | ~2.5–12 k | only with a stated reason |
| > 50 KB | 12 k+ | wrong tool: index, `-L`, or per-commit review |

(Approximate: code and non-ASCII text tokenize differently. Treat it as an order-of-magnitude guardrail, not
an accounting system.)

## The one-line summary

**Load answers, not diffs.** The index is what makes that possible: it names the hunks by function and prices
them, so "read the part about `compute_totals`" costs 149 bytes instead of 49 000.
