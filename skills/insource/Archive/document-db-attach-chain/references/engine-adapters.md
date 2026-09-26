# Engine Adapters

Each engine has a different native batched-fetch primitive. The universal
`attachOne`/`attachMany`/`attachGroup` shape stays the same; only the
fetch call inside each adapter changes. Respect each engine's own idioms
(polyglot rule: "Language-Specific Idioms to Respect," applied here to
database idioms) rather than forcing one engine's API shape onto another.

---

## RxDB

**Native batched-fetch primitives:** `collection.findByIds(ids)` (primary
key lookup, returns a `Map`), or `collection.find({ selector: { field: {
$in: ids } } })` for a non-primary-key match.

**Native relationship mechanism (prefer this for schema-declared, repeated
reads):** `ref` in the schema + `doc.populate('field')` or the `field_`
getter.

```ts
async function attachOneRxDB<T extends Record<string, any>>(
  rows: T[],
  opts: { from: RxCollection; localField: keyof T; foreignField?: string; as: string },
): Promise<T[]> {
  const ids = [...new Set(rows.map(r => r[opts.localField]).filter(Boolean))];
  if (ids.length === 0) return rows.map(r => ({ ...r, [opts.as]: null }));

  let byKey: Map<any, any>;
  if (opts.foreignField) {
    const found = await opts.from.find({ selector: { [opts.foreignField]: { $in: ids } } }).exec();
    byKey = new Map(found.map(d => [d.toJSON()[opts.foreignField!], d.toJSON()]));
  } else {
    const found = await opts.from.findByIds(ids as string[]).exec();
    byKey = new Map([...found].map(([id, doc]) => [id, doc.toJSON()]));
  }

  return rows.map(r => ({ ...r, [opts.as]: byKey.get(r[opts.localField]) ?? null }));
}
```

Full implementation: `references/implementation.rxdb.ts`.

---

## PouchDB

**Native batched-fetch primitive:** `db.allDocs({ keys: [...], include_docs: true })` — a single bulk lookup by document ID. PouchDB has no secondary-index `$in`-style query without a map/reduce view, so batched lookup by a *non-ID* foreign field requires either a pre-built view (`db.query(viewName, { keys: [...] })`) or falling back to fetching a broader range and filtering client-side.

```js
async function attachOnePouch(rows, { db: foreignDb, localField, as }) {
  const ids = [...new Set(rows.map(r => r[localField]).filter(Boolean))];
  if (ids.length === 0) return rows.map(r => ({ ...r, [as]: null }));

  // batched by _id only — the common case for a foreign-key-as-_id design
  const result = await foreignDb.allDocs({ keys: ids, include_docs: true });
  const byId = new Map(result.rows.map(row => [row.id, row.doc ?? null]));

  return rows.map(r => ({ ...r, [as]: byId.get(r[localField]) ?? null }));
}

// batched by a non-_id field requires a view:
// db.query('by_userId', { keys: ids, include_docs: true })
```

**Design note:** because PouchDB's efficient batched lookup is ID-only,
relations that aren't keyed by `_id` need a pre-defined view for this
pattern to stay batched. Without a view, falling back to N individual
`db.get()` calls reintroduces the N+1 problem this pattern exists to avoid
— treat "no matching view" as a signal to add one, not a reason to loop.

Full implementation: `references/implementation.pouchdb.js`.

---

## Dexie (IndexedDB)

**Native batched-fetch primitives:** `table.bulkGet(keys)` for primary-key
lookup (preserves request order, returns `undefined` for misses), or
`table.where(field).anyOf(values).toArray()` for an indexed non-primary
field — both are genuinely fast (single IDB cursor pass), unlike looping
`.get()` calls or `Promise.all`-ing individual `.where()` queries, which
measured significantly slower in practice (see Dexie's own issue tracker
on bulk query performance).

```ts
async function attachOneDexie<T extends Record<string, any>>(
  rows: T[],
  opts: { table: Table; localField: keyof T; foreignField?: string; as: string },
): Promise<T[]> {
  const ids = [...new Set(rows.map(r => r[opts.localField]).filter(Boolean))];
  if (ids.length === 0) return rows.map(r => ({ ...r, [opts.as]: null }));

  let foreignDocs: any[];
  let keyField: string;

  if (opts.foreignField) {
    keyField = opts.foreignField;
    foreignDocs = await opts.table.where(opts.foreignField).anyOf(ids).toArray();
  } else {
    keyField = opts.table.schema.primKey.name;
    const results = await opts.table.bulkGet(ids);
    foreignDocs = results.filter(Boolean) as any[];
  }

  const byKey = new Map(foreignDocs.map(d => [d[keyField], d]));
  return rows.map(r => ({ ...r, [opts.as]: byKey.get(r[opts.localField]) ?? null }));
}
```

Full implementation: `references/implementation.dexie.ts`.

---

## MongoDB

**This engine has a native cross-collection join — prefer it.** Per
`references/principle-and-spectrum.md`, MongoDB's aggregation pipeline
`$lookup` stage runs server-side, can be combined with `$match`/`$project`
to filter before transferring data, and is what the query planner can
actually optimize. The attach-chain pattern below exists for completeness
and for the cases where `$lookup` genuinely doesn't fit — not as the
default MongoDB recommendation.

**Native join (prefer this):**
```js
db.posts.aggregate([
  { $match: { status: 'published' } },
  {
    $lookup: {
      from: 'users',
      localField: 'userId',
      foreignField: '_id',
      as: 'author',
    },
  },
  { $unwind: { path: '$author', preserveNullAndEmptyArrays: true } },
]);
```

**Attach-chain fallback (batched application-level fetch)**, for cases
like joining against a non-MongoDB source, or when `$lookup`'s pipeline
expressiveness doesn't cover a needed transform:

```js
async function attachOneMongo(rows, { collection, localField, foreignField = '_id', as }) {
  const ids = [...new Set(rows.map(r => r[localField]).filter(Boolean))];
  if (ids.length === 0) return rows.map(r => ({ ...r, [as]: null }));

  const foreignDocs = await collection.find({ [foreignField]: { $in: ids } }).toArray();
  const byKey = new Map(foreignDocs.map(d => [String(d[foreignField]), d]));

  return rows.map(r => ({ ...r, [as]: byKey.get(String(r[localField])) ?? null }));
}
```

Full implementation: `references/implementation.mongodb.js`.

---

## Summary table

| Engine | Native cross-collection join? | Batched-fetch primitive used by the adapter | Native relationship/population mechanism |
|---|---|---|---|
| RxDB | No | `findByIds` / `find({ $in })` | `ref` + `.populate()` |
| PouchDB | No | `allDocs({ keys })` (ID-only; non-ID needs a view) | none built-in |
| Dexie | No | `bulkGet` / `where().anyOf()` | none built-in |
| MongoDB | **Yes** (`$lookup`) | `find({ $in })` (fallback only) | `$lookup` (prefer over this pattern) |
