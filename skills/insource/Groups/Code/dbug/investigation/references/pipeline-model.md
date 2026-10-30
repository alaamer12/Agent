# The pipeline model — where failures actually live

Distilled from the research corpus (`data/user.txt` §1–4,10,11,29,30;
`data/grok.txt` §1–2,4; `data/gemini.txt` §1–4) — the literature converges
on the same foundations: Zeller's defect→infection→failure model (*Why
Programs Fail*) and SRE hypothetico-deductive troubleshooting practice.
Core claim: **a program is
an interconnected execution and data pipeline, and a failure observed at
one point is almost never the defect at that point.**

## Defect → infection → propagation → failure

Four states separate a bug from its symptom:

```
Defect        the wrong thing that exists (code, config, schema, data, env)
  ↓ executed
Infection     the first invalid *state* it creates (wrong variable, row,
  ↓           cache entry, lock order, timing)
Propagation   the infected state flows onward through transformations,
  ↓           calls, writes, renders
Failure       the observable symptom at a terminal boundary (crash, wrong
              UI, bad response, alert)
```

Consequence: the crash site is the *last* place the truth was still useful.
The highest-leverage question in all of debugging is:

> **Where is the first invalid state — the earliest point where actual
> state diverged from expected state?**

Once you hold that point, the defect is nearby (or is an environment/config
defect producing it). Everything below is machinery for getting there.

## The pipeline

```
User → browser event → frontend fn → API request → backend entry
  → auth/validate → business logic → repository/ORM → DB → transform
  → response → client state → render
```

Real systems are deeper (middleware, queues, workers, caches, webhooks,
external APIs, pools, triggers, replication). A failure at any node says
only: *somewhere upstream along this graph, reality diverged from the
model.*

### Roles: classify every component you touch

| Role | What it does | Examples | What to check there |
|---|---|---|---|
| **Entry / source** | accepts external input, starts execution | route handler, event handler, queue consumer, cron, webhook receiver, CLI arg parse | input hygiene, auth/context propagation, trace/correlation headers, parameter sanity |
| **Intermediate / transformation** | transforms, validates, enriches, routes, calls onward | middleware, service classes, ORM mapping, reducers, proxies | state transitions, mapping correctness, contract adherence, error translation/swallowing |
| **Terminal / sink** | commits the observable result | response write, DB write, UI render, message publish, file/export | mutation atomicity, side-effect correctness, schema/constraint compliance, serialization |

Debugging strategy follows role: at Entry verify what came in; at
Intermediate audit what the transformation promised; at Terminal compare
expected vs actual output/state directly.

### Failures cluster at boundaries

Process, network, thread/async (context loss, unhandled rejections),
transactional (uncommitted reads, deferred constraints) boundaries. When a
pipeline seems "fine on both sides", look *at* the crossings: serialization,
header stripping, pooling, retries.

### A stack trace IS a pipeline map

Segment exception frames into three regions before reading them:

```
top frames    = sink/crash site — HOW the invalid state finally blew up
                (driver timeout, null deref). Shows how, rarely why.
middle frames = application domain — the FIRST app frame above
                library/runtime code is where your code handed a bad
                state to the machinery. Start backward tracing here,
                not inside node_modules / site-packages / stdlib.
bottom frames = entry/source — framework boot, event loop, routing.
                Almost never the culprit; confirm the path taken.
```

Cautions: the top-most *application* frame is the reporter, not necessarily
the producer — keep climbing until an invariant breaks (first invalid
state). Async boundaries (promises, callbacks, emitters) sever the stack —
that's where correlation IDs replace call frames.

## Debugging directions — choose by information gain per cost

```
Forward   input → A → B → C → failure   when: input is suspicious/small,
                                         pipeline deterministic, failure
                                         occurs early
Backward  failure ← C ← B ← A ← input   when: crash site/trace known, system
                                         large, entry produces floods of
                                         unrelated execution
Narrow    app → subsystem → module → fn → branch → stmt → variable
                                         when: broad failure, suspect region
                                         unknown — halve the space each step
Widen     fn → callers → lifecycle → db → cache → worker → infra
                                         when: unit works in isolation but
                                         fails integrated (state/env/
                                         concurrency-dependent)
```

Don't default to "start at the beginning". Pick the direction with the
cheapest distinguishing experiment; switch when it stops paying.

## State and data lineage

**The state question:** *at what exact point did system state diverge from
expected state?* Compare pass-run vs fail-run snapshots at the same
pipeline boundaries; the first index where they differ is the infection
point. Usable artifacts: before/after snapshots, mutation logs, cache
inspection, session/storage dumps, DB transaction history, event logs.

**The data question:** for the wrong value, where did it *originate*, where
was it last correct, where first wrong/stale/duplicated/lost? Trace the
lineage chain (input → DTO → domain object → query → row → transform →
response → client state → render) one hop at a time — a binary-search
checkpoint mid-chain halves it per probe.

Classic trap this catches: UI empty list ← API returns empty ← query uses
stale filter ← cached config ← deploy never invalidated cache. Fixing the
crash site (or hardcoding a fallback) leaves the systemic defect alive.

## Invariants, assertions, and structural impossibility

An **invariant** is a condition that must hold: preconditions (input),
postconditions (output), representation invariants (a domain object is
always internally consistent), database constraints (CHECK, FK, UNIQUE,
NOT NULL), state-machine rules (no `paid → created`).

- **While debugging:** assert the invariant at each candidate hop. The
  assertion that fires marks the first invalid state — fail-fast beats
  reading ten log lines.
- **When fixing:** enforce the invariant at *every layer it applies to*.
  One validation in one handler is bypassed by the other caller, the batch
  job, and the mock. Defense in depth is the mechanism by which a fixed bug
  becomes *structurally impossible to recreate casually*: entry guard +
  domain check + DB constraint + type-level modeling where the language
  offers it. Prefer making invalid states unrepresentable (types,
  constraints) over checking for them at runtime; when representation
  can't, validate at the boundary *and* the sink.
