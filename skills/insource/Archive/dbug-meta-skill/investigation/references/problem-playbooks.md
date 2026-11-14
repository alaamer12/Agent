# Problem-class playbooks — "if we have THIS problem, how do we debug it?"

Condensed from the corpus (`data/user.txt` §27; `data/grok.txt` §7;
`data/gemini.txt` §20). Each playbook is a starting path, not a ritual —
the moment evidence contradicts it, return to the hypothesis loop. Every
playbook still ends at the same three closers: root cause proven →
regression test → capture (how-to-do).

## Wrong or unexpected data (no crash)

> "The API returns wrong data / the page shows the wrong value / the report
> total is off"

1. Capture one concrete instance verbatim (request, response, the ID).
2. Locate where the value is *produced correctly or not at all*: check the
   DB row first — is the source data right?
   - Source wrong → who wrote it (audit: writer path, worker, migration).
   - Source right → trace transformations backward hop by hop (pipeline
     model §data lineage): query → mapping → cache → serialization → client.
3. Assertion at the chain's midpoint halves the hops per experiment.
4. First divergence found → is it a code transform, a stale cache, or a
   concurrent writer? Each has a different fix layer.
5. Fix every layer that can carry the invalid value; regression test
   asserting the *value*, not just the status code.

## Data disappears / appears duplicated

1. Confirm with a direct query at the DB — application view vs storage view
   disagree frequently (filters, RLS, soft-delete flags, caching).
2. Disappeared: who can delete — cascade, scheduled job, upsert overwriting
   with a new ID, retry with a different key? Check write audit, transaction
   logs, webhook consumers.
3. Duplicated: at-least-once delivery (queue/webhook retry) without
   idempotency; missing unique constraint; read path joining 1:N and not
   collapsing. Check the delivery path's dedupe key + the DB's constraint.
4. Both: reproduce with one record and the real event sequence — then the
   regression test replays it.

## "It worked before" / regression after a change

1. Bookend it: last known-good vs first known-bad (ask the user).
2. Diff the window (`git-forensics.md`); the suspect is usually inside.
3. Window too wide → bisect with an automated repro script.
4. Exposing commit ≠ introducing commit — check what was already latent.

## Intermittent failure ("sometimes 500s", "once a day")

→ `production/` is the domain skill; the process core:
1. Characterize into measurable conditions (rate, time, load, user, data).
2. Correlate IDs across logs/traces for the *failing* instances only.
3. Compare against passing instances — the difference is the suspect set.
4. Never "fixed" by non-reproduction: convert to a probabilistic test
   (loop N times) so the regression check has teeth.

## Only production / only one customer / only under load

→ `production/` + `escalation-ladder.md` L6: environment differential
(runtime, deps, env/config, schema, data shape, limits, traffic pattern).
"One customer" = data-shaped bug: diff that tenant's rows/config against a
healthy tenant before touching code.

## Timeout / hang / 504

1. Where does time go — measure the hops (gateway→app→db→external), don't
   guess the slow one.
2. Classic suspects in order: missing/degraded index (execution plan), N+1
   or unbounded query, lock wait/deadlock retry storm, connection-pool
   exhaustion (waiters > pool size), downstream API latency, synchronous
   CPU work on the event loop, retry amplification.
3. DB suspected → `database/` (plans, locks, pool stats).

## Background job / queue / webhook misbehaviour

1. Did the message arrive? (producer vs broker vs consumer boundaries)
   Look at each crossing before opening handler code.
2. Arrived but nothing happened: poison message stuck in retry loop,
   consumer crashed silently (dead-letter?), handler swallowed the error.
3. Arrived twice → idempotency; never arrived → producer/subscription/
   routing; vanished mid-flight → visibility timeout redelivery races.
4. Replay one safe message manually through the consumer in an isolated
   harness (`backend/`) — that's the fastest ground truth.

## Auth/authz surprising results (403 for the right user, or worse: 200)

1. Dump the *actual* identity/claims/roles object the guard saw — token
   parsing vs session hydration vs middleware ordering produce these
   surprises.
2. Check decision inputs in order: token valid → identity resolved → role
   loaded → policy evaluated → row-level filter applied. Assert each hop;
   the failing assertion localizes the layer.
3. Security-relevant fix goes at *every* layer (stance 3) — an authz UI
   that hides a button is not the fix.

## Migration / schema mismatch (DB vs schema source disagree)

→ `database/` runs this one; the meta-shape: compare both sources of truth,
diff, decide which side is *definitionally* right (the project's schema
artifacts are), repair definition AND state, verify with a script.

## CI/CD failure that passes locally

1. Reproduce the CI *environment*, not the code: same runtime version,
   clean clone, same env vars (or lack thereof), same cache state.
2. Usual suspects: committed-but-untracked files, ordering/timezone
   assumptions, network-seeded fixtures, env var present locally, flaky
   test the PR merely exposed.
3. Diff `local vs CI` like any environment differential (L6).

## Memory grows / crashes after N hours

→ `production/` (resource growth): time-series first (is it sawtooth
rising?), then baseline→workload→terminal snapshot diff, then retention
chain to the leaking reference. The fix is at the retention source, not at
the allocation site.

## Race / deadlock / ordering wrong

→ `production/` (concurrency): reconstruct the actual interleaving with
thread/task IDs + monotonic timestamps; race detector under stress; the
fix imposes ordering/locking/ownership or removes the shared mutable state.

---
**Playbooks not listed:** the general algorithm is the same — characterize,
map the pipeline, choose direction, cheapest experiment, find first invalid
state. If a class recurs in this repo, that's a **how-to-do** candidate:
this file is for debugging paths, `.htd/` is for build paths.
