---
name: dbug-backend
description: Debug a backend service when the symptom lives in server-side behaviour — API/route returns wrong or errors, middleware/auth/DI surprises, background jobs/queues/workers, timeouts, connection pools, retries, environment/config not loading, module/workspace resolution failing in a monorepo, or "is it our code or the database/third party?" Load this from the dbug router whenever the failing component is a server, service, CLI, worker, or its configuration. Provides the request-lifecycle model, layer-attribution method, the isolated-harness technique, and scratch-environment guardrails (env discovery, monorepo path resolution, non-destructive testing).
---

# dbug-backend — server-side debugging

Universal (language/runtime-agnostic) playbook for services, workers, CLIs
and their plumbing. Concrete TypeScript/Bun instance:
[`examples/ts-service-test-harness.md`](examples/ts-service-test-harness.md).

## Guardrails (apply to every backend debug session)

1. **Ephemeral scratch isolation** — ad-hoc scripts live in
   `.debugging/tmp/` (not `scratch/` — the lifecycle rules in
   [`../instrumentation/SKILL.md`](../instrumentation/SKILL.md) govern
   promote/delete).
2. **Deterministic environment discovery** — read config from env, never
   hardcode credentials in scripts; resolve `.env` hierarchically with
   precedence (see [`references/env-and-resolution.md`](references/env-and-resolution.md)).
3. **Non-destructive verification** — exercise mutations inside a
   transaction and `ROLLBACK`; if rows must be committed, clean up in
   `finally` / use unique test identifiers.
4. **Direct service execution** — call the service/query function itself
   in a harness to isolate root cause *before* going through HTTP/UI.
5. **Idempotent fixes on the persistence side** — see `../database/`.

## Where in the lifecycle is the failure?

```
request → middleware → authn → authz → validation → controller → service
        → repository → ORM → pool → DB        (and the response chain back)
        → worker/queue/external API for async paths
```

Attribute first — five suspects hide behind one 500:

| Suspect | Evidence it's the one | How to prove |
|---|---|---|
| **Request problem** (bad input, auth header, content-type) | 4xx with detail; failure identical on raw curl with same payload | replay captured request exactly; strip to minimal form |
| **Our application logic** | fails at same frame every time; DB reads/writes are correct around it | isolated harness call (§ below) |
| **A dependency** (ORM, lib, middleware order, DI wiring) | works when the suspect component is bypassed; version just changed | pin/swap/revert the dependency; bisect |
| **Database** | state correct in app, wrong in DB — or the reverse; errors are driver/SQL shaped | raw query comparison → `../database/` |
| **Infrastructure** (pool, timeout, env, DNS, clock) | only under load / only some instances / only one environment | environment differential (`../investigation/references/escalation-ladder.md` L6) |

Distinguish via the pipeline: each hop either matches its contract (go on)
or doesn't (investigate the crossing *into* it).

Classic symptom→layer pairs worth checking before deep tracing (the
high-priors this table encodes):

| Symptom | Suspect layer | Look for |
|---|---|---|
| 504 under load, CPU fine | event loop / thread pool | synchronous CPU work blocking async loop; pool smaller than real concurrency |
| 403 for the *right* user | middleware pipeline order | authorization claims parsed *after* the guard that consumes them |
| Intermittent 500s only under concurrency | DI / object scope | request state parked inside a singleton-scoped dependency |
| Stale payload for some users | cache (app or proxy) | cache key missing a varying input (tenant, version); invalidation not propagated |

## Isolated service harness — the workhorse

Goal: answer "does this function behave incorrectly *by itself*?" without
the web server, the UI, or shared state.

```pseudocode
function harness():
    env  = loadProjectEnvironment()              # per references/env-and-resolution.md
    db   = initializeClient(env["DATABASE_URL"])
    svc  = instantiateTargetService(db)          # replicate real DI wiring deliberately

    try:
        # read path
        result = svc.fetchRecordById("known_id")
        assert(result != null, "expected record")

        # write path — never leave a trace
        tx = db.beginTransaction()
        try:
            created = svc.createRecord(payload)
            assert(created.id != null)
        finally:
            tx.rollback()
        exit(0)
    catch e:
        print("harness failure:", e); exit(1)
    finally:
        db.close()
```

Run it as a script from `.debugging/tmp/` — deterministic exit code, so
the same file becomes a bisect driver and the seed of a committed test
(`../regression-testing/`). Three classic distinctions it makes:

- **function vs caller** — harness passes but real flow fails → look at
  what callers/inputs/middleware contribute (widen).
- **logic vs state** — harness passes against a mocked/fresh DB but fails
  on real data → data-shaped bug, go to `../database/`.
- **app vs transport** — harness fine, HTTP broken → serialization,
  framework, proxy, auth layer.

## Async paths: jobs, queues, workers, retries

- Trace **one message** end to end with its ID: produced? delivered?
  consumed? acked? dead-lettered? Each boundary is a yes/no experiment.
- Duplicate consumption → at-least-once delivery + missing idempotency
  (dedupe key / unique constraint / transactional outbox).
- Retry storms → check backoff, whether retries repeat *side effects*
  (classic bug class), timeouts shorter than real work duration.
- "Nothing happened" → consumer crashed silently (swallowed exception,
  unlogged DLQ) before handler code; confirm with producer-side counters
  + broker metrics, not by reading handler source.

## Env, config & workspace resolution

Deterministic `.env` discovery (process.env > local overrides > package-
level > root; canonicalize `DATABASE_URL` aliases like `POSTGRES_URL`,
`DIRECT_URL`) and monorepo path resolution for scratch scripts
(bun/tsx native workspace support; else tsconfig `paths` shim in the scratch
dir, or runtime module-alias registration) are fully worked out in
[`references/env-and-resolution.md`](references/env-and-resolution.md) —
read it the first time a scratch script can't find a package or a config.
Classic symptom this fixes: "works when run from the app folder, breaks
from root" → invocation-root + env-precedence, not a logic bug.

## Performance-shaped backend symptoms (quick map)

- **timeout/504** → attribute time to a hop before optimizing one; pool
  exhaustion (`waiters > pool size`), lock waits, downstream latency,
  sync-CPU on event loop → `../investigation/references/problem-playbooks.md`
  §Timeout.
- **memory grows / crash after N hours** → `../production/` §resource
  growth (don't heap-profile a logic bug or vice versa).
- **race/deadlock/intermittent under load** → `../production/` §concurrency.

---
**Better next stop:** query/DB-state specifics → [`../database/SKILL.md`](../database/SKILL.md) ·
unreproducible/prod-only → [`../production/SKILL.md`](../production/SKILL.md) ·
the client half of a shared symptom → [`../frontend/SKILL.md`](../frontend/SKILL.md) ·
process itself → [`../investigation/SKILL.md`](../investigation/SKILL.md).
