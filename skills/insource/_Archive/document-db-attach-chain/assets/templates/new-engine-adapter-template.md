# Template: Adding a New Engine Adapter

Copy this when adding support for a document DB not already covered
(e.g. Firestore, CouchDB, Realm). Fill in the placeholders; don't change
the shape of the `FetchAdapter` interface itself — that's what keeps
`attachOne`/`attachMany`/`attachGroup`/`attachTo` engine-agnostic.

```ts
import type { FetchAdapter } from './implementation.universal';

/**
 * <engine-name> adapter.
 *
 * Native cross-collection join available? <yes/no — if yes, name it and
 * state clearly that it should be preferred; this adapter is then a
 * fallback, matching the MongoDB precedent>
 *
 * Native batched-fetch primitive used: <name the actual API call>
 *
 * Known limitations: <e.g. "batched lookup is ID-only," "requires a
 * pre-built index/view for non-primary-key fields" — state plainly rather
 * than silently falling back to an unbatched loop>
 */
export function <engineName>Adapter(<connection-or-collection-param>): FetchAdapter {
  return {
    async findByField(field, ids) {
      // 1. Confirm the engine can batch-fetch by `field` in one round trip.
      //    If it can only batch by primary key, and `field` isn't the
      //    primary key, either:
      //      a) require a pre-built index/view (see engine-pouchdb.js for
      //         the pattern: throw with a clear message instead of
      //         silently degrading to N unbatched calls), or
      //      b) document that this engine's adapter only supports
      //         primary-key relations.
      //
      // 2. Return PLAIN OBJECTS, not engine-native document wrappers —
      //    callers using attachOne/attachMany should never need to know
      //    which engine produced a given value.

      throw new Error('not implemented');
    },
  };
}
```

## Checklist before adding the adapter to `references/engine-adapters.md`

- [ ] Does this engine have a native cross-collection join? If yes, does
      the adapter's doc comment clearly say "prefer the native join; this
      is a fallback" — matching the MongoDB precedent — rather than
      presenting attach-chain as the default?
- [ ] Is `findByField` genuinely one round trip, not N?
- [ ] If a relation can't be batched without extra setup (an index, a
      view), does the adapter throw with an actionable message, or does it
      silently fall back to a loop? (It must throw — see
      `references/anti-patterns.md` Anti-pattern 4.)
- [ ] Add a row to the summary table in `references/engine-adapters.md`.
- [ ] Add this engine to the comparative walkthrough in
      `examples/four-engines-walkthrough.md` if it's a commonly-requested
      engine, so the "what's constant, what's not" table stays complete.
