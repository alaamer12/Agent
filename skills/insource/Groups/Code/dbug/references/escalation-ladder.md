# The escalation ladder — cheapest sufficient experiment first

The rule: **start at the bottom and climb only
when current evidence cannot distinguish your top hypotheses.** Each level
is a *question-answering* tool, chosen by information gain per unit cost.

## The ladder

```
L0  Observe precisely        expected vs actual, repro rate, conditions,
   (free, no change)         impact. Capture the error/trace/response verbatim.
L1  Reproduce                exact → reliable partial → probabilistic →
                             synthetic → minimal. Non-reproducible = a
                             finding, route to production.md.
L2  Read existing evidence   logs, metrics, traces, recent diffs, .htd,
                             .debugging/bugs — before creating new evidence.
L3  Targeted instrumentation structured log points at pipeline midpoints,
                             invariant assertions, scoped debug facility
                             (→ instrumentation.md).
L4  Isolate                  call the suspect fn/component/service directly
                             in a harness with controlled inputs; mock or
                             cut boundaries — decides "our code vs theirs".
L5  Bisect / divide          git bisect, binary commenting of blocks, feature
                             flags, dataset halving (delta-debugging idea:
                             partition → test each half → recurse on the
                             failing half).
L6  Environment differential compare dev vs staging vs prod: runtime,
                             deps/lockfile, env vars, config, schema, data,
                             limits, flags, proxies.
L7  Runtime/system depth     profilers, heap snapshots, race detectors,
                             connection-pool stats, kernel/OS counters.
L8  Production forensics     sampling, trace correlation, shadow traffic,
                             crash dumps/core files, deterministic replay,
                             postmortem timelines. (→ production.md)
```

Mitigate first when production is bleeding (feature-flag off, rollback,
traffic drain) — then diagnose; SRE triage precedes curiosity.

## Technique economics

Representative costs — context-dependent, never treat as gospel:

| Technique | Cost | Noise | Prod-safe | Info gain | Answers |
|---|---|---|---|---|---|
| Read error/trace verbatim | ~0 | none | yes | varies | where did it break |
| Duck-debug / model check | ~0 | none | yes | varies | wrong assumptions |
| Existing logs/metrics | low | none | yes | med–high | what happened |
| Targeted log checkpoint | low | med | usually | med | is state correct *here* |
| Invariant assertion | low | low | careful | high | where state turns invalid |
| Debugger breakpoint | low | low | no | high | exact values/flow at a point |
| Tracepoint / conditional logging / data breakpoint | low | low | no | high | values at a point or on write, WITHOUT editing source or pausing the run |
| Isolated harness call/test | med | low | yes | high | does the unit behave wrong alone |
| Distributed trace (IDs) | med | med | yes | very high | full path across services |
| git bisect | low | low | yes | very high | which change broke it |
| Environment diff | med | low | yes | high | which difference matters |
| Heap/CPU profile, race detector | high | low | situational | very high | resource/timing causality |
| eBPF / replay / forensics | high | very low | yes (privileges) | max | live prod behaviour untouched |

## Binary search is the general strategy behind L4–L5

Anything linear can be halved: commit ranges (bisect), config space,
feature sets, dataset size, log checkpoints along a call chain, mocking
boundaries. Check the midpoint; recurse where the fault lives. N steps
become log N. For inputs: strip parts until only the failure-inducing
minimum remains (a minimal repro is both evidence Level 5 and the regression
test's skeleton — → regression-testing.md).

## Minimization discipline — narrowing an artifact properly

When cutting a failing input/code down to its failure-inducing core, the
published delta-debugging discipline applies:

- **Baseline first.** If a known-good side exists (previous release,
  parent commit, working environment, healthy tenant), isolating the
  DIFFERENCE between good and bad costs an order of magnitude less than
  reducing the failing side alone (measured on one GCC bug: 59 tests vs
  731). Construct a passing baseline when none seems to exist.
- **Three-valued oracle.** Every reduction step answers PASS / FAIL /
  UNRESOLVED — never read UNRESOLVED as PASS; an inconclusive result
  forces finer granularity, not relief. Automated shrinking and bisect
  presuppose a deterministic, re-runnable check: verify the failure's
  reproducibility first (environmental randomization silently breaks
  every reducer).
- **Same-failure fingerprint.** "Still reproduces" must mean the same
  error signature — for crashes, matching program counter AND call
  backtrace, not merely "something fails": a shrunk repro can quietly
  become a different bug. After fixing what the small case exposed,
  re-check the ORIGINAL full-scale case.
- **Structure-aware cuts, valid output.** Halve along the artifact's own
  structure (lines → AST/tree levels, not flat characters — cuts the
  test count ~10x on large inputs); keep the reduced case syntactically
  valid and human-recognizable — smaller-but-unparseable is *less*
  debuggable. Some size-INCREASING moves (inline a helper, split a
  complex expression) are legitimate when they unlock later cuts.
- **Stop at local minimum.** Provable 1-minimality (removing any single
  remaining element kills the failure) is the ideal but costs one test
  per surviving element; global minimality is NP-complete. "Small
  enough, still failing, every piece plausible" is the practical bar.
- **Sporadic bugs are exempt.** Deletion-based narrowing assumes
  removing code preserves the failure — false for nondeterministic
  defects, where hypothesis-testing on non-reproducing runs is the
  strategy that still works. Raise the repro rate instead of shrinking.

## Reproduction hierarchy (L1 in detail)

```
exact        same steps, same data, fails identically
  ↓ no?      partial      reliably reproduces *a* failure of same shape
  ↓ no?      probabilistic fails 1-in-N — now measurable (run N times)
  ↓ no?      synthetic    fabricated input/state that triggers same symptom
  ↓ no?      minimal      smallest construction that still fails
  ↓ no?      hypothesis-driven: skip repro, test predictions instead (L3+)
```

The red-capable command — the loop's *form* — in preference order,
whichever the stack supports: a failing test at any seam · curl/HTTP
script against the dev server · CLI invocation diffed against a saved
snapshot · headless browser asserting on DOM/console/network · replay of
a captured trace/payload/event log from disk · throwaway single-service
harness with mocked dependencies (examples/isolated-harness-polyglot.md)
· property/fuzz loop that auto-shrinks a counterexample · scripted
end-to-end flow. All must end in exit 0/1.

"Sometimes it crashes" converts into measurable conditions: after ~N
requests AND dataset X present AND worker Y active AND cache state Z.
Characterize, then treat as reproducible. Debuggability is a RATE
threshold — ≈1-in-2 is workable, 1-in-100 is not; when the rate is too
low, add stress/loop instrumentation to RAISE it before attempting any
shrinking or bisecting.

## The decision tree — picking the path (compressed diagnostic framework)

```
What is the symptom? (expected vs actual)
        ↓
Production bleeding now? ──yes──► mitigate first (flag off / rollback /
        ↓                          drain), PRESERVE evidence, then continue
Reproducible locally?
  ├─ yes → known boundary? ──yes──► isolate boundary: harness/mocks (L4)
  │                                 (stack trace? start at FIRST APP FRAME —
  │                                  pipeline-model.md §stack traces)
  │         └─ no ─► trace the pipeline: pick direction, binary checkpoints
  └─ no ─► instrument for CHARACTERIZATION (make conditions measurable),
           then re-enter the tree from the top
        ↓ — once inside the pipeline, what looks wrong? —
DATA wrong (flow completes, values off)?
  → lineage/state-divergence tracing (pipeline-model.md)
ORDER/TIMING wrong (unit passes alone, fails concurrent)?
  → concurrency protocol (production.md §concurrency)
ENVIRONMENT/LOAD-specific (works in staging, prod-only, big-data-only)?
  → differential matrix (L6, production.md)
OUTPUT right but SLOWER / resources climbing?
  → profiles & time-series (L7: on-CPU vs off-CPU vs allocation)
        ↓ any branch
run the CHEAPEST experiment distinguishing your top TWO hypotheses,
confirm causality (counterfactual / statistical — hypothesis-and-evidence.md)
```
