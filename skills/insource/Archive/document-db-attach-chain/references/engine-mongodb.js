/**
 * MongoDB adapter — FALLBACK ONLY.
 *
 * MongoDB has a real server-side join ($lookup in the aggregation
 * pipeline). Prefer that for anything running as a MongoDB query — it
 * filters/projects before transferring data and lets the query planner
 * use indexes across the join, which this adapter's application-level
 * $in fetch cannot replicate.
 *
 * Use this adapter only when:
 *   - joining a MongoDB collection against a non-MongoDB data source, or
 *   - a needed transform doesn't fit the aggregation pipeline's
 *     expressiveness.
 *
 * See references/engine-adapters.md for the $lookup example to reach for
 * first.
 */
export function mongodbAdapter(collection) {
  return {
    async findByField(field, ids) {
      const found = await collection.find({ [field]: { $in: ids } }).toArray();
      return found;
    },
  };
}
