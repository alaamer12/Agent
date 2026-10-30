# Statistics, and the traps that fake a result

> **Illustrative, not exhaustive.** Engines, runtimes, OS tools and flag names in this file are examples
to reason from. The measurement logic is stack-neutral, and an unlisted or hybrid option is a valid answer.

Two ways a benchmark lies: the harness deletes the work, or the spread is wider than the gap. Both are silent.

## How many iterations — from the budget, not from hope

```bash
python scripts/bench_stats.py --budget 300 --per-iteration 2.4
# budget 300s · per-iteration 2.4s · reserve 20% for analysis/report · warmup 20%
# -> measure 80s = 33 iterations (7 warmup). Need 50? budget 480s, or shorten the workload.
```

Rough math for a relative error `e` on the median with coefficient of variation `CV`: `n ≈ (2·CV / e)²`.
CV 12 % and a 5 % precision target asks for ~23 iterations. If the budget only allows 10, say what precision 10
buys instead of pretending otherwise — and never let the budget eat the reporting: reserve ~20 % for it.

## Which numbers to report

| Statistic | Use it for | Do not |
|---|---|---|
| **median** | the central claim | compare medians of 3 samples and call it a result |
| **p95 / p99** | tails, user-visible stalls | quote a p99 from 10 iterations (it is just the max) |
| **MAD / IQR** | spread that survives outliers | reporting a bare mean and hiding the skew |
| **CV** | noise level, comparability across candidates | shipping a "12 % faster" claim at CV 20 % |
| min / best | only as "best observed", with a reason | as the headline number |

A mean alone is a lie of omission: one scheduler hiccup among 30 samples moves the mean and does not move the
median, and the median is what the next run will look like.

## The noise floor — measure it, don't assume it

Before comparing A to B, compare A to A′: the same implementation, run in the same session, under the same
interleaving. That gap is what your machine can invent out of nothing.

```text
A vs A'   median 1.02× ± 4%   <- this is the floor
A vs B    median 1.03×        <- inside the floor: inconclusive, full stop
A vs B    median 1.30×        <- real, and 30% is the claim, not "faster"
```

Claims smaller than roughly 2–3× the floor are not supported by that run. Either raise `n`, tighten the mode
(ultra), or report "no measurable difference at this resolution" — which is often the useful answer, because it
means the choice can be made on other grounds (maintenance, licence, memory).

## Order, drift, and pairing

```text
A A A A A A A A A A   B B B B B B B B B B     <- A gets the cold machine, B gets the warm one,
                                                 and 10 minutes of background indexing
A B A B A B A B A B                            <- drift hits both equally: do this
```

Even better, **pair** the samples: iterate the same input in both candidates within one cycle and compare
differences per pair — the bootstrap in `bench_stats.py` resamples pairs, not loose samples, which removes slow
drift from the confidence interval. Repeat the whole session on a different day for anything that will be quoted
later; a result that only appears at 14:00 on a Tuesday is a result about Tuesdays.

Statistical significance is not the finish line: with 500 iterations a 0.5 % gap becomes "significant" and stays
irrelevant. Report the size of the gap, the interval around it, and whether that size changes any decision.

## The traps that produce a fake win

| Trap | What happens | Defence |
|---|---|---|
| **Dead-code elimination** | the result is never used, so the optimiser deletes the work; 1 000× speedup appears | consume the result (sink), or accumulate and print/return it |
| **Constant folding** | inputs are compile-time constants, so the answer is precomputed | vary inputs at runtime; read them from an array the compiler cannot see through |
| **Loop-invariant hoisting** | the work is moved out of the timed loop | re-derive inputs inside the loop; use a data-dependent sink |
| **Inlined no-op** | the "function under test" optimises away entirely | check the generated assembly/IL when the number is implausibly small |
| **Wrong clock** | wall clock on a system with 15 ms timer granularity (classic Windows pitfall) | monotonic high-resolution clock; if the work is shorter than the tick, batch iterations and divide |
| **Measuring the harness** | allocation, formatting, or logging inside the timed region | move output out; if the candidate needs setup, set it up outside |
| **JIT warmup** | the first 5 iterations are 10× slower and they are in your average | warm up, or state that cold performance is the dimension |
| **Build mode mismatch** | one candidate from a release build, the other debug; `-O3` vs default | identical flags, and print them |
| **First-touch page faults** | the first run allocates and faults memory others reuse | pre-touch buffers, then measure |
| **Cache state asymmetry** | candidate A leaves the data warm for itself, B evicts it | interleave; and run both orders to check |
| **GC in the window** | a collection lands in one candidate's iteration | report GC counts/pauses if the runtime exposes them; ultra: control it and say how |
| **Frequency/thermal drift** | core clocks fall during the run | ultra: lock/pin and note temperature; normal: accept and widen the interval |
| **Synchronisation illusion** | measuring a call that returns before the work finishes (async, batched writes, `fsync` off) | measure the observable completion, not the submission |
| **Unrepresentative input** | random keys favour hashing, or one huge row favours a fast path | the real distribution, or both extremes stated |

Sink sketches, same idea every language — the optimiser must not be able to prove the value is unused:

```python
acc ^= hash(result)          # [Python]  after the loop: print(acc) or return acc
```
```ts
sink ^= result;              // [TypeScript/JS] a module-level var, read after timing
```
```csharp
sink ^= result;              // [.NET] volatile field, printed after the loop; watch JIT inlining
```
```rust
std::hint::black_box(result)                        // [Rust]
```
```c
__asm__ __volatile__("" : : "r"(result) : "memory") // [C/C++]
```
```java
sink = result;   // a non-final field, read and printed after timing  // [Java]
```
```go
outcome = x      // package-level var, printed at exit               // [Go]
```

## What to keep alongside the numbers

Every sample row: `candidate, iteration, value, timestamp, (temperature/load if ultra)`. The distribution is
the evidence — a report with only aggregates cannot be re-examined, and "trust me, it's faster" is what we are
trying to replace.
