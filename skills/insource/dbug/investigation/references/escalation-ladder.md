# The escalation ladder — cheapest sufficient experiment first

Source: `data/user.txt` §8,18,24,25; `data/grok.txt` §3,6;
`data/gemini.txt` §5,16,18. The rule: **start at the bottom and climb only
when current evidence cannot distinguish your top hypotheses.** Each level
is a *question-answering* tool, chosen by information gain per unit cost.

## The ladder

```
L0  Observe precisely        expected vs actual, repro rate, conditions,
   (free, no change)         impact. Capture the error/trace/response verbatim.
L1  Reproduce                exact → reliable partial → probabilistic →
                             synthetic → minimal. Non-reproducible = a
                             finding, route to production/.
L2  Read existing evidence   logs, metrics, traces, recent diffs, .htd,
                             .debugging/bugs — before creating new evidence.
L3  Targeted instrumentation structured log points at pipeline midpoints,
                             invariant assertions, scoped debug facility
                             (→ ../../instrumentation/SKILL.md).
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
                             postmortem timelines. (→ ../../production/SKILL.md)
```

Mitigate first when production is bleeding (feature-flag off, rollback,
traffic drain) — then diagnose; SRE triage precedes curiosity.

## Technique economics

Representative costs — context-dependent, never treat as gospel:

| Technique | Cost | Noise | Prod-safe | Info gain | Answers |
|---|---|---|---|---|---|
| Read error/trace verbatim | ~0 | none | yes | varies | where did it break |
| Socratic/model check | ~0 | none | yes | varies | wrong assumptions |
| Existing logs/metrics | low | none | yes | med–high | what happened |
| Targeted log checkpoint | low | med | usually | med | is state correct *here* |
| Invariant assertion | low | low | careful | high | where state turns invalid |
| Debugger breakpoint | low | low | no | high | exact values/flow at a point |
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
test's skeleton — → ../../regression-testing/SKILL.md).

## Reproduction hierarchy (L1 in detail)

```
exact        same steps, same data, fails identically
  ↓ no?      partial      reliably reproduces *a* failure of same shape
  ↓ no?      probabilistic fails 1-in-N — now measurable (run N times)
  ↓ no?      synthetic    fabricated input/state that triggers same symptom
  ↓ no?      minimal      smallest construction that still fails
  ↓ no?      hypothesis-driven: skip repro, test predictions instead (L3+)
```

"Sometimes it crashes" converts into measurable conditions: after ~N
requests AND dataset X present AND worker Y active AND cache state Z.
Characterize, then treat as reproducible.

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
  → concurrency protocol (../../production/SKILL.md §concurrency)
ENVIRONMENT/LOAD-specific (works in staging, prod-only, big-data-only)?
  → differential matrix (L6, production/SKILL.md)
OUTPUT right but SLOWER / resources climbing?
  → profiles & time-series (L7: on-CPU vs off-CPU vs allocation)
        ↓ any branch
run the CHEAPEST experiment distinguishing your top TWO hypotheses,
confirm causality (counterfactual / statistical — hypothesis-and-evidence.md)
```
