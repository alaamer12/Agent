# Case 01 — a real run, start to finish (normal mode)

> Measured on the machine this skill was authored on, 2026-10-29, Python 3.11 stdlib `sqlite3`.
> Numbers are for that machine; the *method* is what to copy.
>
> **The stack here is incidental.** SQLite happened to be the question and Python the available host; the same
> six steps (dimensions → budget → gate → measure → report) apply to `[Go]`, `[.NET]`, a `[Postgres]` comparison,
> or two `[shell]` pipelines around a binary.

**Question.** "Is SQLite FTS5 actually worth the extra table, or is `LIKE '%term%'` fine?"

## 1. Think — dimensions from the decision

The decision is operational, not abstract-fast: *can we keep search cheap without a second index?*

| Dimension | Metric | Unit | Falsifier |
|---|---|---|---|
| query latency | median + p95 of one full-text lookup | ms | a gap under ~3× the measured noise floor cannot rank them |
| index cost | one-off rebuild of the FTS table | s | if it exceeds the maintenance window, the win is moot |
| storage | bytes of the FTS index vs the base table | MB | if the index rivals the data, "free" is wrong |
| **semantic equivalence** | identical row-id sets per term | boolean | any divergence stops the comparison (gate, not dimension) |
| *not measured* | concurrent writers, memory footprint, cold cache | — | listed as limits, not silently omitted |

Workload: 200 000 rows of ~90-char text, a rare term in 1 row of 40, four terms, seed `20261029`. Query set:
whole-word terms (what the product actually searches).

## 2. Report the plan — and the time budget

The user said nothing about duration, so this was the blocking question. Answer: *"few minutes"*.

```bash
python scripts/bench_stats.py --budget 180 --per-iteration 0.05 --warmup-frac 0.2 --reserve 0.2
# budget 180s · per-iteration 0.050s · warmup 20% · reserve 20%  -> 2 880 iterations
```

That said, per-iteration was estimated, not measured; the estimate said thousands of iterations were affordable.
Reality check: with the FTS rebuild and correctness gate included, **24 measured iterations per candidate in
interleaved order was enough** (the noise floor came out at 0.44 %, far below the 4 000× gap being tested).
More iterations would only sharpen a number nobody is doubting. Report the reasoning, not just the count.

## 3. Correctness gate first

| term | `LIKE` rows | `FTS5` rows | equal? |
|---|---|---|---|
| helios / quorum / vellum / kestrel | 1 250 each | 1 250 each | yes |

Then the probe that mattered:

```text
substring probe 'heli':  like=1251  fts=0     -> not interchangeable for infix search
```

**That is the headline finding.** Half the "speed" question dissolves: FTS5 cannot answer infix fragments at all.
If the product ever needs "match as I type a partial word", this is not a faster/slower choice — it is a feature
gap, and the honest recommendation changes (trigram index, not FTS5). A benchmark that skipped this check would
have reported a 44× win for an approach that cannot serve the real query.

## 4. Run — normal mode

No warmup discard, no pinning, no GC/AV/thermal control: exactly what a developer sees on a working laptop.
Order `like, fts5, like2` repeated per iteration; `like2` is the *same* implementation under a second label,
which exists only to measure the machine's own noise.

## 5. Report

```bash
python scripts/bench_stats.py --samples samples.csv --baseline like --null like,like2
```

```text
noise floor (like vs like2, same implementation): 0.44% ratio spread at 95% confidence
fts5   vs like   ratio 0.02232  95% CI [0.02173, 0.02438]  over 24 pairs -> real difference
like2  vs like   ratio 1.004    95% CI [0.9819, 1.03]      over 24 pairs -> INSIDE NOISE - inconclusive

| Candidate | n  | Median | p95   | MAD    | CV    | Min   | Max   |
| fts5      | 24 | 1.064  | 1.367 | 0.0509 | 11.8% | 0.964 | 1.44  |
| like      | 24 | 47.47  | 53.68 | 0.8096 | 4.9%  | 45.4  | 54.92 |
| like2     | 24 | 47.70  | 50.28 | 1.172  | 2.7%  | 45.94 | 50.46 |
```

**Verdict.** FTS5 answers in **1.06 ms vs 47.5 ms — about 45× faster** (1/0.0223), and the interval is far
outside the 0.44 % noise floor, so the gap is real, not machine mood. Note the shape of the numbers, not just the
size: `like` scales with the table (a full scan), FTS5 with the result set (an index lookup), so the ratio grows
with rows — at 200 k it is 45×, at 20 k it would be nearer 5×, at 2 M much larger. The decision is size-dependent
and the report should say so.

`like2` vs `like` came back **inconclusive** — which is the control working correctly: the run can resolve 45×,
but not 0.4 %, and this harness must not be asked to rank two candidates that are 1 % apart.

**Conditions.** mode: **normal** (nothing controlled) · Windows 10, Python 3.11, SQLite as bundled by that
Python · one in-process connection reused across iterations (so this measures warm-cache latency, not cold start)
· 24 iterations, 6 unmeasured warmup rounds discarded before counting (a deviation from "no warmup" that must be
disclosed, because it was applied) · seed 20261029.

**Isolation.** Nothing was installed: every module came from the standard library, so no venv was needed, no
project manifest changed, and no machine-wide setting was touched (hence nothing to restore). The database and
generated rows lived in a temp directory under the run folder. A run that needed a third-party `[FTS variant]` or
`[an engine binary]` would have gone into `[python -m venv .venv-bench]` (or a container), never a global install.

**What this does not say.** Not concurrent-write behaviour, not cold-cache or first-query cost, not memory, not
index rebuild time (measured separately if it matters: it was seconds here and the maintenance window is minutes),
and nothing about other machines. It says nothing about infix search either — the gate showed FTS5 cannot do it.

## What this example is for

Five things worth copying into any run:

1. the **correctness gate found the real answer** (FTS5 cannot do infix), which no timing would have surfaced;
2. a **control candidate** (`like2`) that measures the machine, so "real gap" is a checked claim;
3. **median + p95 + CV**, not a bare mean — FTS5's CV was 11.8 %, so its mean would have been dragged by outliers;
4. the budget question answered *and* the iteration count justified against the gap being tested;
5. **disclosed deviations** (warmup was discarded in a "normal mode" run) — normal vs ultra is about what you
   control, and unreported control is how a normal-mode number quietly becomes an ultra one.
