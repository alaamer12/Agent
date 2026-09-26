---
name: document-db-attach-chain
description: Batched, immutable, order-guarded cross-collection reads for document databases (RxDB, PouchDB, Dexie/IndexedDB, MongoDB) via an engine-agnostic attachOne/attachMany/attachGroup chain (attachTo(...).one().many().group()) built on a small per-engine FetchAdapter. Use whenever writing query code that combines documents from two or more collections/tables on RxDB, PouchDB, Dexie, or MongoDB — e.g. attaching a post's author, a user's related records, or "posts with comments and comment authors" style reads. Also use when asked for a "join" helper, an "ODM-style" or "Drizzle-like" relation utility for these engines, or when attachOne/attachMany/attachGroup/attachTo are named directly. On MongoDB, check "Choosing a strategy" first — this pattern is the fallback there, not the default (prefer $lookup). Do NOT use for one schema-declared relationship read repeatedly on an engine with native population (e.g. RxDB's .populate()) — see "When NOT to use this."
---

# Document DB Attach Chain

No document database engine has a universal answer to cross-collection
reads: some (RxDB, PouchDB, Dexie) have no server-side query planner
spanning collections at all, so "join" only ever means "fetch, then fetch
again, then merge in application code." Others (MongoDB) have a real
native join (`$lookup`). This skill teaches one engine-agnostic pattern —
batched, immutable, order-guarded — for the engines that need it, and is
explicit about when an engine has something better.

Read `references/principle-and-spectrum.md` first if it's unclear which
engine you're working with falls on which side.

## The three primitives (identical on every engine)

| Function | Shape | What it does |
|---|---|---|
| `attachOne(rows, opts)` | parent → one foreign doc \| null | Single batched fetch via the engine's `FetchAdapter` |
| `attachMany(rows, opts)` | parent → array of foreign docs | Single batched fetch, grouped by foreign key |
| `attachGroup(rows, path, attachFn)` | batches an attachOne/attachMany call across a NESTED path | Flattens across all parents, one batched fetch, re-nests |

These three functions never talk to a database directly — they call
through a `FetchAdapter` (one method: `findByField(field, ids)`). That's
the entire surface area that changes between engines. See
`references/implementation.universal.ts`.

## The chain: `attachTo(rows)`

```ts
import { attachTo } from './implementation.universal';
import { rxdbAdapter } from './engine-rxdb'; // swap this import per engine — nothing else changes

const posts = await attachTo(rawPosts)
  .one({ adapter: rxdbAdapter(db.users), localField: 'userId', foreignField: 'id', as: 'author' })
  .many({ adapter: rxdbAdapter(db.comments), localField: 'id', foreignField: 'postId', as: 'comments' })
  .group('comments', flat =>
    attachOne(flat, { adapter: rxdbAdapter(db.users), localField: 'userId', foreignField: 'id', as: 'author' })
  );
```

No `.build()`/`.exec()` — `await` on the chain resolves it directly (it
implements `PromiseLike`).

## Workflow for using this skill

1. **Identify the engine, then check "Choosing a strategy" below before
   writing any code.** RxDB, PouchDB, Dexie → this pattern is the default.
   MongoDB → check whether `$lookup` fits first; only fall back to this
   pattern if it genuinely doesn't (see
   `references/principle-and-spectrum.md`).
2. **Confirm it's not a case for the engine's native relationship tool
   instead.** A single schema-declared relationship read repeatedly →
   RxDB's `.populate()` or the engine's equivalent. See "When NOT to use
   this."
3. **Pick or write the adapter for this engine.** `references/engine-*.{ts,js}`
   has RxDB, Dexie, PouchDB, and MongoDB adapters ready to use. For an
   engine not yet covered, copy
   `assets/templates/new-engine-adapter-template.md`.
4. **Identify the shape needed**: one relation or several? Flat or nested?
   `attachOne` or `attachMany` at each level?
5. **Write the chain top-to-bottom in dependency order** — a step
   attaching a nested field must come after the step attaching its parent
   field. `examples/four-engines-walkthrough.md` has the same scenario
   worked across all four engines, plus a nested example.
6. **Don't hand-roll nested loops on any engine.** Always use
   `.group(path, attachFn)` for a relation nested inside an already-attached
   array — see `references/anti-patterns.md` Anti-pattern 3.
7. **If two or more steps are independent** and the read is
   latency-sensitive, don't expect the chain to parallelize — it's
   sequential by design on every engine. Run separate chains and
   `Promise.all` them if that matters.
8. **Copy the adapter + universal implementation into the project once**,
   as shared utilities, rather than re-deriving per call site. Don't
   modify the mutation/ordering-guard behavior in
   `implementation.universal.ts` without reading
   `references/design-notes.md` first.

## Choosing a strategy per engine

| Engine | Native cross-collection join? | Default for this kind of read |
|---|---|---|
| RxDB | No | This pattern |
| PouchDB | No | This pattern (relations not keyed by `_id` need a view — see `references/engine-adapters.md`) |
| Dexie | No | This pattern |
| MongoDB | **Yes** — `$lookup` | `$lookup`; this pattern only as a fallback |

Regardless of engine, prefer denormalization over either option for data
read constantly on a hot path — see "When NOT to use this."

## When NOT to use this

- **A single relationship declared in the engine's own schema and read
  repeatedly** — use the engine's native mechanism (RxDB's
  `post.populate('authorId')` / `authorId_` getter). Gets you built-in
  caching this pattern doesn't reimplement.
- **A pure MongoDB query where `$lookup` covers it** — prefer `$lookup`.
  See "Choosing a strategy" above and
  `references/anti-patterns.md` Anti-pattern 5.
- **Data rendered constantly / on a hot path, on any engine** —
  denormalize (store the joined shape at write time) instead of joining at
  read time at all.
- **A many-to-many relation where the flattened SQL shape is needed**
  (`post.tags[]`, not `post.postTags[].tag`) — this pattern gives the
  junction-collection shape; flatten manually at the call site.

## Reference files

- `references/principle-and-spectrum.md` — the abstract principle behind
  this pattern, and the real trade-off spectrum across engines (which have
  no native join vs. MongoDB, which does). Read this first.
- `references/implementation.universal.ts` — the engine-agnostic core:
  `attachOne`, `attachMany`, `attachGroup`, `attachTo`/`AttachChain`, and
  the `FetchAdapter` interface every engine implements.
- `references/engine-rxdb.ts`, `references/engine-dexie.ts`,
  `references/engine-pouchdb.js`, `references/engine-mongodb.js` — concrete
  adapters. Each documents its engine's native batched-fetch primitive and
  any limitations.
- `references/engine-adapters.md` — narrative walkthrough of all four
  adapters with a summary comparison table.
- `references/design-notes.md` — why each design decision was made
  (immutability, the ordering guard, the adapter interface's minimal
  surface, no parallelism, no junction flattening) and what still isn't
  solved.
- `references/anti-patterns.md` — eight concrete flawed drafts this
  pattern went through, including engine-specific ones (assuming all
  document DBs lack joins; unbatched PouchDB fallback; reaching for this
  pattern over `$lookup` on MongoDB).
- `examples/four-engines-walkthrough.md` — the same relation attached
  across RxDB, Dexie, PouchDB, and MongoDB side by side, plus one nested
  example.
- `assets/templates/new-engine-adapter-template.md` — copyable template
  and checklist for adding support for an engine not yet covered
  (Firestore, CouchDB, Realm, etc.).
