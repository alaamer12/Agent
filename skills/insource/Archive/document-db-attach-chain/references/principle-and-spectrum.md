# The Attach-Chain Principle, and the Engine Spectrum It Applies To

## The abstract problem (per polyglot's Step 1: extract the principle)

Not: *"How to join in RxDB."*
But: *"How to perform batched, immutable, order-safe cross-collection
reads on a document store, in engines where no native cross-collection
join exists to do this for you."*

That qualifier — "in engines where no native join exists" — matters. It is
not universally true across document databases, and pretending otherwise
would be exactly the Vendor Coupling anti-pattern polyglot warns against,
just inverted: instead of coupling to one vendor's syntax, it would falsely
generalize one vendor's *limitation* as if it were shared by the whole
category.

## The real spectrum

Document databases split into two genuinely different camps on this
question — not four equivalent flavors of the same thing:

```text
No native cross-collection join           Native server-side join exists
◄──────────────────────────────────────────────────────────────────────►
  RxDB · PouchDB · Dexie/IndexedDB              MongoDB ($lookup)
  (client-side / offline-first,                 (server-side, full
   no query planner spans collections)           aggregation pipeline)
```

**Left side (RxDB, PouchDB, Dexie):** these are embedded/client-side
document stores. There is no server process running a query planner across
collections — every "join" is fundamentally "fetch, then fetch again, then
merge in application code," full stop. The attach-chain pattern in this
skill isn't competing with a native alternative here; it's the only
reasonable way to do this well (batched, not N+1) rather than badly.

**Right side (MongoDB):** MongoDB runs `$lookup` server-side inside the
aggregation pipeline — a genuine, planner-optimized join that can push
filtering and projection down before data ever leaves the server. Here the
attach-chain pattern is not the default choice; it's one option on a
real trade-off spectrum against `$lookup`, and usually loses to it for
server-executed queries. See "Choosing a strategy per engine" below.

## Choosing a strategy per engine

Per polyglot's Step 2 (formulate the trade-off spectrum, don't mandate one
answer) and its "Dynamic Strategy Framing" pattern — don't default to
attach-chain everywhere. Ask, or infer from the engine:

- **Is this query running server-side, with the data already there
  (MongoDB, or any server-resident document store with a native join)?**
  → Prefer the native join (`$lookup`). It can filter/project before
  transferring data, runs in one round trip, and the query planner may
  use indexes across the join in ways application-level code cannot
  replicate. Reach for attach-chain on MongoDB only when a projection or
  transform genuinely doesn't fit the aggregation pipeline's expressiveness,
  or when part of the "relation" is coming from a different data source
  entirely (e.g. joining a MongoDB collection against a REST API result).
- **Is this query running client-side / embedded, with no server process
  to plan across collections (RxDB, PouchDB, Dexie)?**
  → Attach-chain (or an engine-idiomatic equivalent) is the correct
  default. There's no native alternative to lose to.
- **Is the relationship read constantly, on a hot path, regardless of
  engine?**
  → Denormalize (store the joined shape at write time) rather than joining
  at read time at all — this beats both attach-chain and `$lookup` for
  hot-path reads, on every engine. See `references/anti-patterns.md`.
- **Is the relationship declared in the engine's own schema and read
  repeatedly (RxDB's `ref`, Mongoose-style references, etc.)?**
  → Use the engine's native population mechanism (`.populate()` in RxDB)
  first. Attach-chain is for ad-hoc, query-time reads — not a replacement
  for an engine's built-in relationship tooling.

## What stays constant across every engine (the actual universal part)

Regardless of which side of the spectrum an engine sits on, the three
properties this pattern cares about don't change:

1. **Batch, don't loop.** Never issue one query per parent row when a
   single batched query (`$in`, `anyOf`, `bulkGet`, `allDocs({keys})`,
   `$lookup`) can do it in one round trip.
2. **Immutable by default.** Return new documents/objects; don't mutate
   what was fetched.
3. **Fail loud on ordering mistakes.** When one attach step depends on the
   result of a previous one (nested relations), missing or misordered
   steps should throw with a clear message — not silently produce empty
   results.

These three are the actual "principle over syntax" (polyglot rule #1) this
skill teaches. Everything else — which function names, which batched-fetch
primitive, whether a native join is even available — is engine-specific
and belongs in `references/engine-adapters.md`, never hardcoded into the
core guidance as if it were universal.
