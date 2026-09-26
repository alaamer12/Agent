# Design notes: why this pattern looks the way it does

## Why three primitives, not one generic join function

- **attachOne** — one parent → one foreign doc. Single batched query via
  the engine's `FetchAdapter`.
- **attachMany** — one parent → array of foreign docs. Single batched
  query, same adapter.
- **attachGroup** — not a fetch itself, and needs no adapter at all. A
  combinator: flattens a *nested* path across every parent, hands the
  flattened set to whichever attachOne/attachMany you pass in, then
  re-nests the result.

A single function trying to do all three (à la Drizzle's recursive
relational query builder) would need a real recursive resolver, engine
differences aside — build it only once 2+ levels of nesting show up *in
practice*.

## Why the FetchAdapter interface, and why it's this small

`findByField(field, ids) -> Promise<PlainDoc[]>` is deliberately the
*only* method engines implement. Everything else —
`attachOne`/`attachMany`/`attachGroup`/`attachTo` — is written once
against that interface and never touches an engine-specific API directly.
This is what keeps generalizing to a new engine a matter of writing one
small adapter file (see `assets/templates/new-engine-adapter-template.md`)
rather than re-deriving the whole pattern per engine.

The interface intentionally does NOT expose engine-specific query
features (Mongo's `$lookup` pipeline stages, RxDB's `populate()`, Dexie's
compound indexes) — those are each engine's *stronger* native tool and
belong outside this pattern, used directly when they fit better. See
`references/principle-and-spectrum.md`.

## Why immutable, not mutating

An earlier draft had the nested combinator mutate rows in place while the
flat primitives returned new arrays — two functions that look
interchangeable at the call site with opposite semantics. The fix applied
here, uniformly across every engine: **everything returns new data,
nothing mutates.**

## Why attachGroup throws instead of silently attaching nothing

The most common real mistake is ordering — attaching a nested field before
the step that attaches its parent. `assertPathResolvable` walks the path
segment by segment and throws immediately, naming the exact missing
segment. This logic operates on plain objects post-fetch, so it is
identical across every engine — the guard doesn't know or care which
adapter produced the data it's checking.

**Known limit:** it only checks that a key exists on *at least one* row,
not on *every* row — a legitimately-empty relation (`comments: []`)
shouldn't throw, but this also means a partial-attach failure on some rows
(not all) won't be caught by the guard alone.

## Why this generalizes to some engines as the default, and to MongoDB as a fallback

RxDB, PouchDB, and Dexie have no server process running a query planner
across collections — there's no "better tool" for a cross-collection read
that this pattern is settling for over. MongoDB does: `$lookup` runs
server-side, can filter/project before transferring data, and lets the
planner use indexes across the join. Presenting attach-chain as equally
appropriate on all four engines would be a subtler version of the same
mistake this pattern was built to avoid on RxDB specifically — assuming a
constraint (no native join) is universal when it demonstrably isn't. See
`references/principle-and-spectrum.md` for the full reasoning and
`references/anti-patterns.md` Anti-pattern 5 for a concrete case of getting
this wrong.

## What this pattern does NOT solve, on any engine

- **No parallelism in the chain.** Every step runs strictly after the
  previous one resolves, even when two steps are independent. Run
  separate chains and `Promise.all` them outside the chain if that
  matters — see `examples/four-engines-walkthrough.md`.
- **No junction-table flattening.** A many-to-many relation via a join
  collection/table still leaves you with the junction shape
  (`post.postTags[].tag`), not the flattened SQL shape (`post.tags[]`).
  Flatten at the call site if needed.
- **Not a substitute for an engine's native relationship tooling.** RxDB's
  `ref` + `.populate()`, MongoDB's `$lookup`, or any equivalent on a future
  engine should be preferred for schema-declared or planner-optimizable
  relationships. This pattern is for ad-hoc, query-time reads.
- **Not a substitute for denormalization on hot paths**, regardless of
  engine.
