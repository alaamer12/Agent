# Universal Walkthrough: The Same Relation, Four Engines

Following polyglot's comparative pattern: the same scenario — posts with
their author attached, batched — shown across all four engines so the
constant (batching, immutability) and the variable (fetch primitive,
native-join availability) are both visible side by side.

Scenario: `posts` collection/table, each with `userId`; attach the
matching `users` document as `.author`.

---

## 1. RxDB (no native join)

```ts
import { attachTo } from './implementation.universal';
import { rxdbAdapter } from './engine-rxdb';

const posts = await attachTo(rawPosts)
  .one({ adapter: rxdbAdapter(db.users), localField: 'userId', foreignField: 'id', as: 'author' });
```
Underneath: `db.users.find({ selector: { id: { $in: [...] } } })` — one
batched query, RxDB's own primitive.

## 2. Dexie (no native join)

```ts
import { attachTo } from './implementation.universal';
import { dexieAdapter } from './engine-dexie';

const posts = await attachTo(rawPosts)
  .one({ adapter: dexieAdapter(db.users), localField: 'userId', foreignField: 'id', as: 'author' });
```
Underneath: `db.users.bulkGet([...])` (since `id` is the primary key here)
— IndexedDB's fast batched primary-key lookup.

## 3. PouchDB (no native join, ID-keyed relation)

```js
import { attachTo } from './implementation.universal.js';
import { pouchdbAdapter } from './engine-pouchdb.js';

const posts = await attachTo(rawPosts)
  .one({ adapter: pouchdbAdapter(usersDb), localField: 'userId', foreignField: '_id', as: 'author' });
```
Underneath: `usersDb.allDocs({ keys: [...], include_docs: true })` — the
one PouchDB primitive that's genuinely batched without a custom view.

## 4. MongoDB (HAS a native join — this is the fallback path)

```js
// PREFERRED for a pure-MongoDB query:
const posts = await db.posts.aggregate([
  { $lookup: { from: 'users', localField: 'userId', foreignField: '_id', as: 'authorArr' } },
  { $unwind: { path: '$authorArr', preserveNullAndEmptyArrays: true } },
]).toArray();

// attach-chain fallback (e.g. users list actually comes from a different
// service, or the transform doesn't fit the pipeline):
import { attachTo } from './implementation.universal.js';
import { mongodbAdapter } from './engine-mongodb.js';

const posts = await attachTo(rawPosts)
  .one({ adapter: mongodbAdapter(db.collection('users')), localField: 'userId', foreignField: '_id', as: 'author' });
```

---

## What's constant, what's not

| | RxDB | Dexie | PouchDB | MongoDB |
|---|---|---|---|---|
| Native cross-collection join | No | No | No | **Yes** (`$lookup`) |
| Default recommendation | attach-chain | attach-chain | attach-chain | `$lookup` |
| Batched primitive under the adapter | `find({ $in })` | `bulkGet` / `where().anyOf()` | `allDocs({ keys })` | `find({ $in })` (fallback) |
| `attachOne`/`attachMany`/`attachGroup`/`attachTo` code | identical | identical | identical | identical |

The chain code, the immutability guarantee, and the ordering guard never
change — only the four-line adapter does. That's the actual "polyglot"
property here: one core, swappable engine adapters, and an honest note on
which engine shouldn't default to this pattern at all.

---

## Nested example, one engine, to show attachGroup still works identically

(Nesting behaves the same regardless of adapter — shown once with RxDB;
swapping the adapter is the only change needed to run this on another
engine.)

```ts
import { attachTo, attachOne, attachMany } from './implementation.universal';
import { rxdbAdapter } from './engine-rxdb';

const posts = await attachTo(rawPosts)
  .many({ adapter: rxdbAdapter(db.comments), localField: 'id', foreignField: 'postId', as: 'comments' })
  .group('comments', flat =>
    attachOne(flat, { adapter: rxdbAdapter(db.users), localField: 'userId', foreignField: 'id', as: 'author' })
  );
```
