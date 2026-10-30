---
name: benchmark
description: 'Benchmark candidates on task-derived dimensions, in normal or ultra mode. Think first: which decision is being made (faster, more accurate, less memory) and how each will be measured - never a fixed list. Report the plan; ask the expected run time when unspecified: 5 min means ~10 iterations, an hour allows 100+. NORMAL measures the environment as-is (GC on, no warmup, no pinning) - what the deployment feels like; ULTRA fights noise for fairness (warmup, interleaved A/B/A/B, pinned core, locked frequency where permitted). Same language for every candidate, defaulting to the project''s; say so when harness overhead rivals the work measured. Correctness gate first: a fast wrong answer is not a faster candidate. Measure in an isolated env (venv, temp prefix) - never global packages - and restore any system control touched. Reports median/p95 with spread and a noise floor, never a bare mean; ''inconclusive'' when the gap sits inside the noise. scripts/bench_stats.py: stats, bootstrap verdict, budget math.'
when_to_use: The user asks which of two or more approaches/libraries/implementations is faster, leaner, or more accurate; asks for a benchmark, a perf comparison, timings, or "is X better than Y"; or a measured number is needed to settle a design choice.
argument-hint: "[normal|ultra] [candidates] — or 'how long do I want this to run?'"
---

# Benchmark

A benchmark is an experiment, and an experiment needs a hypothesis, a control, and a number you can defend.
"Run it ten times and take the average" produces a number that means nothing the moment the spread is wider
than the gap.

> **Nothing here is bound to a stack.** Languages, engines and runtimes named in this skill are **examples to
> reason from**, in brackets or marked as such — not required choices, and never an exhaustive set. The method
> (dimensions → controls → statistics → report) is the same in [Python], [Go], [Rust], [Java], [.NET], [Node],
> [C/C++], [SQL alone], or a shell script driving a binary; a hybrid or an unlisted approach is always allowed.
> `scripts/bench_stats.py` is a convenience for the arithmetic — the formulas and the CSV contract it consumes
> are in [`references/02`](references/02-statistics-and-traps.md), so any stack can compute the same numbers.

The shape of the work: **think → report the plan → run → report the results.** Never skip to running: the
dimensions you choose are the whole content of the answer, and they come from the task.

```text
1 think      what is being decided, and on which dimensions, measurable how?
2 report     candidates · language · mode · harness · iterations · time budget  ->  user confirms
3 run        correctness gate, then measure (normal or ultra)
4 report     median/p95 + spread + noise floor + verdict + what would change it
```

## Step 1 — think: derive the dimensions

Write down the decision the user is actually facing, then the dimensions that would settle it. Three to five,
each with a metric, a unit, a measurement method, and what would falsify the claim
([`00`](references/00-dimensions.md)).

| If the decision is about | Dimensions worth considering |
|---|---|
| speed | wall time per operation, throughput, latency distribution (median, p95, p99), cold start, first-query cost |
| memory | peak RSS, bytes per record, allocation rate, GC pauses, growth over time (leak shape) |
| accuracy / quality | exact match vs tolerance, error distribution, false-positive rate, determinism across runs |
| scale | cost at 1×, 10×, 100× the real data volume; where the curve bends |
| operations | disk layout, connection cost, memory-safety, dependency weight, licence, blast radius of an outage |

Two rules while thinking:

- **A single dimension is never the answer.** Speed versus memory, accuracy versus latency, cold versus warm:
  report the pair that trades off, or the user inherits a decision you hid inside the metric you chose.
- **Correctness is a gate, not a dimension.** Every candidate must produce the same output (exact, or within a
  stated tolerance) before any timing counts. A candidate that is 30% faster and returns different rows did not
  win — it answered a different question.

## Step 2 — report the plan, and get the time budget

Present, in a few lines, before writing any harness: the dimensions with their metrics · the candidates ·
the language and why · the mode · where the code will run (isolated env, or the project's existing one) ·
the workload (data size, distribution, the actual query set) · the iteration count and where it came from ·
what you will *not* measure.

**If the user gave no time budget, ask. This is a blocking question** — iterations are the difference between a
conclusion and a coin flip, and the budget decides how many you can afford:

```bash
python scripts/bench_stats.py --budget 300 --per-iteration 2.4    # -> 40 iters, 10 warmup, 60s analysis reserve
```

| Budget | Realistic |
|---|---|
| 5 min | 10–15 iterations, 1–2 dimensions, no ultra ceremony |
| 30 min | 50 iterations, 3 dimensions, cold + warm, one workload size |
| hours | 100+, several input sizes, ultra mode, repeat runs on different days |

State the mode. **Normal (default)** measures the environment as it is; **ultra** measures the mechanism under
controlled conditions. They answer different questions and both are legitimate
([`01`](references/01-normal-vs-ultra.md)).

## Step 3 — build the harness

- **One language for all candidates.** If the thing being compared is a library or engine (SQLite, a codec, a
  database, a sorting implementation), the host language rarely changes the *ordering* — but it does change the
  absolute numbers and the fixed overhead. So: pick the language the project uses; if that is not obvious, ask.
- **Say when the harness rivals the work.** If the binding layer, interpreter overhead, or marshalling is the
  same size as what you are measuring, the comparison measures the wrapper, not the candidate. That is a
  finding, not a failure: report it, and state whether a same-language-native re-run would be needed for a
  finer call.
- **Same inputs, fixed seed, same measurement point.** The timer boundary must be identical for every
  candidate; setup outside it, teardown outside it, results consumed inside it (or laundered through a sink).
- **Trap-proof the loop** ([`02`](references/02-statistics-and-traps.md)): dead-code elimination, constant
  folding, inlined no-ops, timer resolution, JIT warmup, cache state, build mode (debug vs release, optimisation
  flags), and the classic "I measured the logger".
- **Isolate the environment; never pollute the global one.** Anything the benchmark needs that the project does
  not already have goes into a throwaway, project-local or temp environment — not into the user's global packages,
  not into the project's manifest:

  | Need | Example option (use whatever the stack has) |
  |---|---|
  | a Python sandbox | `[python -m venv .venv-bench]`, `[uv venv]`, `[poetry]`, `[conda create -p ./.conda-bench]` |
  | a Node sandbox | `[npm ci --prefix ./.bench-node]`, a temp dir with its own `package.json`, `[pnpm]` isolated store |
  | Ruby / PHP / Java / .NET / Go / Rust | `[bundle config set --local path vendor/bundle]`, `[composer install --working-dir]`, `[maven -Dmaven.repo.local]`, `[nuget restore -PackagesDirectory]`, `[go mod vendor]`, a temp `[cargo new]` |
  | a system service or tool with no isolation story | a container, a VM, or `[nix develop]` / `[devshell]` |

  Rules: the same environment for every candidate, or the difference is part of the result and gets stated ·
  the project's dependency set is untouched at the end (`git status` on manifests before and after) · scratch
  data, databases, and generated workloads go in a temp directory, not the repo root · report what was created
  and what was removed. Installing a benchmark's dependency into the user's global environment is a side effect
  they did not ask for; do it only with their explicit go-ahead.
- **System-level controls are borrowed, not owned.** Power plan, governor, affinity, priority, turbo flags:
  record the value *before* changing it and restore it after, with proof in the report
  ([`01`](references/01-normal-vs-ultra.md) — "restore what you touched").

## Step 4 — run it

```text
per candidate:  environment snapshot  ->  correctness check  ->  warmup (ultra)  ->  N measured iterations
interleaved:    A B A B A B ...       (a sequential AAA...BBB run measures drift, not candidates)
```

In ultra mode, record every control you applied **and every one you could not** (a shared cloud VM, a laptop on
battery, an unavoidable antivirus). A fairness claim you cannot honor is worse than an honest normal run
([`01`](references/01-normal-vs-ultra.md)).

**Prove each control engaged.** Read the affinity mask back from inside the process, print `gc.isenabled()`,
echo the runtime flags. Then check the machine's own floor: run one candidate twice under two labels — if that
gap is *wider* than a normal run's, the controls did nothing and the run must be labelled **normal**, not ultra.
An unverified control is a false claim in the header of an otherwise honest report
([`case-02`](examples/case-02-ultra-that-failed.md) is exactly that mistake, measured).

Feed the samples to the statistics helper rather than eyeballing them:

```bash
python scripts/bench_stats.py --samples runs.csv --baseline fast --confidence 95
```

It reports n, median, mean, p95, min/max, MAD and CV per candidate, the noise floor, and a bootstrap verdict on
each gap — including "inside noise", which is a real result.

## Step 5 — report the results

```markdown
## Verdict
<one line: which candidate wins on which dimension, and whether it is a real gap or noise>

## Numbers
| Candidate | Median | p95 | Spread (MAD) | vs baseline | Verdict |
|---|---|---|---|---|---|

## Conditions            mode · language · isolated env (and what was removed) · hardware/OS · workload · iterations · what was controlled (and restored)
## What this does NOT say  limits, unmeasured dimensions, what would change the conclusion
## Reproduce             exact commands
```

Hard rules: report the median with a spread, never a bare mean (one slow outlier moves a mean and lies about the
distribution); quote the noise floor before claiming any percentage; if the gap is inside the noise, the answer
is **inconclusive**, and that sentence is a deliverable, not a failure. Numbers without conditions are
anecdotes with decimals.

## Boundaries

| Out of scope | Go instead |
|---|---|
| where the time goes inside one implementation | a profiler (flame graphs, tracing) |
| choosing a technology from requirements, no measurement yet | `techstack` |
| comparing candidate *products* with researched non-performance evidence | `decide` / `judge` |
| proving a change fixed a defect | tests + the `diffs`/`postmortem` evidence trail |
| a permanent performance gate in CI | the project's CI, seeded with this harness once the shape is settled |

## References and scripts

| Path | Owns |
|---|---|
| [`references/00-dimensions.md`](references/00-dimensions.md) | deriving dimensions from the task, the dimension card, paired dimensions, the correctness gate, workload design |
| [`references/01-normal-vs-ultra.md`](references/01-normal-vs-ultra.md) | exactly what each mode controls, throwaway environments per stack (never the global one), restoring machine-wide settings after ultra, per-language knobs, when ultra is impossible or misleading, reporting honesty |
| [`references/02-statistics-and-traps.md`](references/02-statistics-and-traps.md) | iteration math, median/p95/MAD/CV, noise floor, interleaving, bootstrap verdicts, the compiler and harness traps |
| [`references/03-environment-and-reporting.md`](references/03-environment-and-reporting.md) | what to capture about the machine, the isolation record (env used, manifests untouched, settings restored), artifact layout, report templates, saving the harness into the repo |
| [`examples/case-01-sqlite-normal-mode.md`](examples/case-01-sqlite-normal-mode.md) | a full measured run: dimensions, budget math, the correctness gate that changed the answer, normal-mode numbers, verdict |
| [`examples/case-02-ultra-that-failed.md`](examples/case-02-ultra-that-failed.md) | an ultra attempt whose controls never engaged — how the noise floor proves it, and what to check before labelling a run ultra |
| `scripts/bench_stats.py` | `--samples` stats + bootstrap verdict + noise floor; `--budget` iteration math; self-test with no arguments |
