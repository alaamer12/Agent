/**
 * PouchDB adapter.
 *
 * PouchDB's only truly batched primitive is allDocs({ keys, include_docs }),
 * which is ID-only. There is no secondary-index $in query without a
 * pre-defined map/reduce view.
 *
 * This means this adapter has two modes:
 *   - field === '_id': uses allDocs — genuinely batched, one round trip.
 *   - any other field: requires a view name to be passed; queries that
 *     view with { keys, include_docs: true }. If no view is supplied,
 *     this throws rather than silently falling back to N individual
 *     db.get() calls — a fallback loop would reintroduce the exact N+1
 *     problem this pattern exists to avoid, so it's treated as a setup
 *     error to fix (add the view) rather than a runtime degradation.
 *
 * @param {PouchDB.Database} db
 * @param {{ viewsByField?: Record<string, string> }} [opts] map of
 *   non-_id field names to the PouchDB view name that indexes them
 */
export function pouchdbAdapter(db, opts = {}) {
  const viewsByField = opts.viewsByField ?? {};

  return {
    async findByField(field, ids) {
      if (field === '_id') {
        const result = await db.allDocs({ keys: ids, include_docs: true });
        return result.rows.map(row => row.doc).filter(Boolean);
      }

      const viewName = viewsByField[field];
      if (!viewName) {
        throw new Error(
          `pouchdbAdapter: no view registered for field '${field}'. ` +
          `PouchDB has no batched query for non-_id fields without a ` +
          `map/reduce view — define one (emitting '${field}' as the key) ` +
          `and pass it via { viewsByField: { ${field}: 'your-view-name' } }.`,
        );
      }

      const result = await db.query(viewName, { keys: ids, include_docs: true });
      return result.rows.map(row => row.doc).filter(Boolean);
    },
  };
}
