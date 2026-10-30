# Deriving the dimensions

> **Illustrative, not exhaustive.** Engines, runtimes, OS tools and flag names in this file are examples
to reason from. The measurement logic is stack-neutral, and an unlisted or hybrid option is a valid answer.

The dimensions *are* the answer. A benchmark that measures throughput when the user's real constraint is tail
latency at 3 a.m. has produced a confident, useless number. So think before coding: name the decision, then the
measurements that could change it.

## Start from the decision, not the metric

Write one sentence: *"the choice between X and Y depends on ___"*. That blank is your first dimension. Then ask
what else could change the decision — that is usually the second, and the pair is where the value is.

| The user's words | The decision hiding underneath | Dimensions that settle it |
|---|---|---|
| "is `[a full-text index]` faster than `[a substring scan]`?" | can we keep search under a second as the table grows | median + p95 query time at 1×/10×/100× rows; index build time; index size on disk |
| "which `[queue/broker]` should we use?" | operational load, not just speed | publish/consume latency, backlog behaviour at 10×, restart recovery, dependency weight, memory at idle |
| "does the `[new parser]` break anything?" | correctness first | exact output equality on real corpus, then throughput, then peak memory |
| "is the rewrite worth it?" | cost paid now vs cost saved later | runtime delta, cold start, memory, and the *size of the delta relative to the migration risk* |
| "how much faster is ultra mode?" | nothing — that is a measurement-method question | report the **normal/ultra gap for the same candidate** (it is itself a finding: how much of the win was noise) |

## The dimension card

Every dimension gets this shape before the harness is written:

```text
Name        cold start time
Metric      seconds from process spawn to first successful response
Unit        ms, median over N attempts, with p95
Method      fresh process per attempt, OS wall clock, no reuse of warmed caches
Falsifier   if the gap is smaller than the run-to-run noise floor, no claim is made
Reality     is this what production sees? (warm pool? then cold start is not the dimension, it is a footnote)
```

A dimension with no falsifier is a vibe. A dimension whose "Reality" row says *no* is still measurable, but it
must be labelled as a mechanism measurement, not a deployment claim.

## Pairs, never singles

Every dimension has a natural opponent; measuring one and reporting a winner is how benchmarks mislead:

| Dimension | Its pair | Why together |
|---|---|---|
| throughput | latency distribution | a batching system wins one and loses the other |
| median latency | p95 / p99 | the tail is where user-visible pain lives |
| speed | memory / allocation rate | the fast one may be fast because it caches everything |
| warm performance | cold start | serverless and restart-heavy deployments live in the cold number |
| accuracy | runtime | a 2 % error cut that doubles latency may be the wrong trade |
| steady state | behaviour under growth | the crossover point *is* the finding |
| performance | blast radius on failure | fastest with no timeout is a bad trade in a request path |

Report the pair, then say which one the user's context weights harder — and if you do not know, ask.

## The correctness gate

Before a single timing: run every candidate on the same inputs and compare outputs.

```text
exact equality          rows/hashes identical
within tolerance        |a-b| <= eps, stated, with the worst observed delta
semantic equality       sorted sets, or a normalised form (floats, key order, collation)
```

If they disagree, stop and report the disagreement as the headline: *"these two are not interchangeable —
candidate B drops 14 rows on NULL handling"*. That is worth more than any timing, and it is exactly the finding
a user with a benchmark-shaped question did not expect to need.

## Workload design

- **Use the real data shape.** A uniform random key set flatters hash-based structures; Zipf-skewed access
  flatters caches. If the production distribution is known, benchmark it; if unknown, say so and test both.
- **Size matters more than count.** 10 k rows that fit in L2 and 10 M that do not are different experiments; run
  at the size the deployment will see, and one size up to find the bend.
- **Fix the seed**, and record it. Reproduction without a seed is theatre.
- **Warm vs cold, stated.** Same table: first query in a fresh process vs query 50 of a warm loop. Report which
  one you ran; the two answers can differ by an order of magnitude.
- **Setup outside the timer, results consumed inside it** — or launder the result through a sink so the
  optimiser cannot delete your work ([`02`](02-statistics-and-traps.md)).

## Choosing how many to measure

Three to five dimensions is the working range for one run. More than that and either the time budget dies or the
report becomes a wall nobody acts on. If the user's real question needs six, ask which two would actually change
the decision — usually the rest were decorative.
