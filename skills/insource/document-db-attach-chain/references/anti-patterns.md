# Anti-patterns this skill exists to prevent

## Anti-pattern 1: naming these functions `join`/`leftJoin`/`rightJoin`

```ts
// DON'T
const result = await leftJoin(posts, users, 'userId', 'id');
```

For engines with no native join (RxDB, PouchDB, Dexie), SQL-style naming
implies row-preservation-direction semantics and planner-level cost
characteristics that don't exist. Use `attachOne`/`attachMany`/
`attachGroup` — names that describe what actually happens.

## Anti-pattern 2: assuming every document DB lacks joins

```
// DON'T write skill guidance like:
// "No document database supports joins, so always use attach-chain."
```

MongoDB's `$lookup` is a real, planner-optimized server-side join. Treating
attach-chain as the universal default (rather than the RxDB/PouchDB/Dexie
default, and the MongoDB *fallback*) pushes people away from a better tool
on the one engine that has one. See
`references/principle-and-spectrum.md`.

## Anti-pattern 3: manual nested loops instead of attachGroup

```ts
// DON'T — re-fetches per post, defeats batching entirely, on ANY engine
for (const post of posts) {
  post.comments = await attachOne(post.comments, { adapter, localField: 'userId', foreignField: 'id', as: 'author' });
}
```

This is not engine-specific — looping a batched-fetch call per parent
defeats the batching on RxDB, Dexie, PouchDB, and MongoDB alike. Always use
`attachGroup(rows, path, attachFn)`, which flattens across ALL parents
before issuing a single query.

## Anti-pattern 4: looping unbatched single-doc gets on PouchDB when no view exists

```js
// DON'T — falls back to N individual db.get() calls, reintroducing N+1
async function attachOnePouchUnbatched(rows, { db, localField, as }) {
  return Promise.all(rows.map(async r => ({
    ...r,
    [as]: await db.get(r[localField]).catch(() => null),
  })));
}
```

When a PouchDB relation isn't keyed by `_id` and no view exists, the fix is
to define the view — not to silently degrade to per-row `db.get()` calls.
`references/engine-pouchdb.js`'s adapter throws instead of falling back,
specifically to surface this as a setup problem to fix.

## Anti-pattern 5: reaching for `$in`-fetch on MongoDB before checking whether `$lookup` fits

```js
// Usually DON'T, on MongoDB, when the whole query is server-side anyway:
import { attachTo } from './implementation.universal.js';
import { mongodbAdapter } from './engine-mongodb.js';
const posts = await attachTo(rawPosts).one({ adapter: mongodbAdapter(db.collection('users')), ... });

// DO, when it's a pure MongoDB query:
const posts = await db.posts.aggregate([
  { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'author' } },
]).toArray();
```

The attach-chain adapter for MongoDB exists for genuine edge cases (joining
across data sources, transforms `$lookup` can't express) — not as a stylistic
alternative to `$lookup` for an ordinary same-database join.

## Anti-pattern 6: mixed mutation semantics

```ts
// DON'T — inconsistent: some functions mutate, some return new data
posts = await attachOne(posts, { ... });      // must reassign
await attachGroup(posts, 'comments', ...);    // mutates in place, no reassign needed
```

Every function in `references/implementation.universal.ts` returns new
data; nothing mutates the input, on any engine.

## Anti-pattern 7: attachGroup without the ordering guard

```ts
// DON'T — silently attaches to nothing if 'comments' isn't attached yet
await attachGroup(posts, 'comments.author', flat => attachMany(flat, { ... }));
```

`attachGroup` calls `assertPathResolvable()` before flattening, turning a
silent no-op into an immediate, actionable thrown error — identical
behavior regardless of which engine's adapter is in use, since the guard
operates on plain objects, not engine-native documents.

## Anti-pattern 8: reaching for this pattern instead of an engine's native population/relationship tool

```ts
// DON'T, for a relationship read constantly and declared in the schema
const posts = await attachTo(rawPosts).one({ adapter: rxdbAdapter(db.users), ... });

// DO, when authorId is declared with `ref: 'users'` in an RxDB schema
const author = await post.populate('authorId');
```

This pattern is for ad-hoc, query-time reads — not a replacement for
whatever native relationship mechanism an engine already provides (RxDB's
`ref`/`.populate()`, Mongoose-style population on MongoDB, etc.).
