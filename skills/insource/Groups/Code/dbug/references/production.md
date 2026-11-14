# Production & unreproducible debugging

Use when reproduction is the problem itself — production-only failures,
intermittent ("once a day"), only-under-load, only-one-customer/tenant,
crash-after-N-hours, and heisenbugs that vanish when observed; plus
concurrency investigation (races, deadlocks, interleaving reconstruction)
and resource-growth analysis (memory/FD/connection-pool leaks).

When the failure won't come to you, you go to it — with instruments, not
guesses. Two iron rules first:

1. **Bleeding production outranks curiosity** — mitigate by the cheapest
   reversible step (feature flag off, rollback, drain traffic, cache
   bump), *preserve evidence on the way* (dumps, logs, IDs), then diagnose
   calmly. A revert is not "not debugging"; it's buying a lab.
2. **Non-reproducible is a measurement problem, not a mysticism problem.**
   The bug has conditions; you haven't named them yet.

## Characterize into measurable conditions

Convert "sometimes it crashes" into a hypothesis-testable sentence:

```
fails ≈ 1-in-N · since <deploy/date> · only tenant X · only when payload
has shape Y · only instance A–C (not D) · only at :00 hourly · latency
spike precedes it · no memory growth beforehand
```

Instruments that build this picture: metrics time-series (scope + trend +
correlation), logs filtered to the *failing* request IDs only, traces of
failing vs passing instances diffed. The diff between passing and failing
populations is the suspect set — that's the environment differential
principle applied to time/tenancy/instances instead of dev-vs-prod.

## Observability-first (the safe instrumentation)

- **Four golden signals per service — the finite measurement checklist**
  (Google SRE): *latency* (track failed requests separately; watch the
  p99 tail over short windows — it leads saturation), *traffic*,
  *errors*, *saturation*. A metric that every hypothesis explains
  unchanged is decoration, not evidence.
- **Correlation IDs everywhere**: a propagated trace header (e.g. W3C
  `traceparent` — illustrative standard) carried across HTTP/RPC/queue
  headers, stitched into logs — the backbone of every prod investigation;
  without it you're matching timestamps by hand.
- **Flame graphs, matched to the question**: *on-CPU* — what consumes
  cycles (wide top-of-graph blocks); *off-CPU* — blocked time: I/O waits,
  lock contention, pool starvation, scheduling delays — answers "slow but
  CPU idle", the overlooked default for latency complaints; *allocation* —
  who's creating the memory pressure before the leak hunt below.
- **Structured logs with sampling** at the suspected hop: production-safe
  when volume-managed; add *before* the next incident when the class is
  known to recur (observability debt is why this bug is hard, and part of
  the complete fix).
- **Environment differential matrix** — "works in staging, fails in prod"
  compare: runtime patch versions & lockfiles · env vars/config (and
  string-vs-bool flag parsing traps) · DB schema/index/collation &
  migration state · data shape/volume · proxies/TLS/header-stripping ·
  OS limits (`ulimit`, cgroup memory, FD counts, ephemeral ports) ·
  feature-flag states · external-service versions. Diff artifacts, don't
  audit vibes. High-frequency culprits living in this matrix: `"false"`
  parsed as boolean-true config strings; load balancers stripping auth or
  trace headers; missing composite index that only bites at prod row
  counts; collation/encoding differences; cgroup OOM-killer silently
  restarting one instance (→ check restart counts before "random" 502s).
- One-customer bugs: suspect *their data/config* first (row shapes,
  volumes, locale, timezone, entitlement flags) — diff against a healthy
  tenant before touching shared code.
- **Channels outside your app.** Don't stop at your own telemetry:
  stack dumps of a *live* running process (pstack-class tools),
  structured crash reports (stack + registers + disassembly serialized
  as JSON for dedup and clustering), time-travel/replay recordings, and
  allocation tagging that makes one subsystem appear separately in
  profiler output. Two consequences: externally supplied, structured
  user reports (OS-level state, not app logs) can localize a bug before
  any maintainer repro exists — demand and parse them; and when no
  existing channel shows what you suspect, **create a channel** — that
  is a legitimate debugging move, not scope creep. For state-endpoint
  genres, remember coverage is not uniform: some datasets are empty
  until the program opts in — *no data ≠ no problem*.

## Heisenbugs — observation changes behaviour

Symptom: attaching a debugger/slowing prints makes it disappear. Causes:
timing perturbation (breakpoints, synchronous log I/O), memory-layout
perturbation, GC/scheduler interference. Protocol:

```
prefer read-only existing telemetry            (zero perturbation)
  ↓ insufficient
low-overhead async logging / tracepoints       (buffered, off hot path)
  ↓ insufficient
increase the race window deliberately          (controlled delay in suspect
                                               region, behind a dev flag)
  ↓ insufficient
stress it harder instead of observing softer   (N runs → probabilistic
                                               repro → then normal methods)
  ↓ truly untouchable locally
deterministic replay (record prod traffic), shadow traffic, or kernel-
level sampling probes (eBPF-class — illustrative; privileged/ops-owned) —
escalate to user/ops with the 5-point protocol if those tools exist only
there.
```

## Concurrency: reconstruct the actual interleaving

Your mental model assumes `A1→A2→A3 ∥ B1→B2→B3`; reality may be
`A1→B1→B2→A2→B3→A3`. Method:

1. **Name the shared mutable state** — which variable/row/cache is
   readable-and-writable by both paths? No shared state, no race (look
   elsewhere: it's an ordering/timezone/caching bug).
2. **Evidence the schedule**: log with thread/task/async-context ID +
   monotonic timestamps (never cross-machine wall clocks — skew is real)
   under a loop that runs the window N times.
3. **Race detectors** where the runtime/platform offers them (Go `-race`,
   ThreadSanitizer-class tools — examples) run *in a test*, not in prod.
4. **Deadlock**: two transactions holding-and-waiting → inspect engine
   deadlock detail; fix by lock ordering, shrinking transactions, or
   row-lock patterns (→ [`database.md`](database.md)).
5. **Prove the fix**: stress test with the interleaving constrained —
   deterministic-ish harness beats "seems fine now". Retry-with-side-
   effects and at-least-once queues are *distributed races in disguise*:
   idempotency keys / dedupe tables are the structural fix.

## Resource growth (crashes after N hours)

```
time-series first: is it sawtooth-rising (leak) or step (new workload) or
flat-but-then-crash (limit: FDs, conns, disk, quotas)?
  ↓
narrow the resource: heap · goroutine/thread count · open FDs/sockets ·
pool checkout-waiters · cache size · disk
  ↓
baseline snapshot → N iterations of suspect workflow → GC → terminal
snapshot → diff by retained size → retention chain to the root that holds
it (globals, listeners never removed, unclosed handles, timers, request-
scoped objects parked in singletons)
  ↓
fix the retention source — deleting the allocation-site "temp" object
treats the symptom; and add the leak's tripwire (metric/alert or test)
```

Connection-pool exhaustion sits at the border of performance and leak:
`waiters > pool size` with checkout-without-release found → that's a code
path, not a capacity question. Never "just raise the pool" without the
release audit.

## Forensics & postmortem glue

Preserve-evidence habits that make all of the above possible: exit codes
and stderr captured, core/crash dumps configured before they're needed,
deploy timeline correlated with first-failure timestamp (the cheapest
bisect there is), a bug record with the hypotheses table
([`../assets/bug-record-template.md`](../assets/bug-record-template.md)).
If the eventual answer was "the observability gap made this take hours",
closing that gap is part of the complete fix (stance 3 again: the next
occurrence must be cheap).

---
**Better next stop:** once reproduced, hand to the matching domain playbook
([`backend.md`](backend.md) · [`database.md`](database.md) ·
[`frontend.md`](frontend.md)) and the normal loop closers in
[`../SKILL.md`](../SKILL.md) ·
permanent test decision → [`regression-testing.md`](regression-testing.md).
