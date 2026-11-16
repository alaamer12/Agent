import type { RxCollection } from 'rxdb';
import type { FetchAdapter } from './implementation.universal';

/**
 * RxDB adapter. Uses find({ selector: { field: { $in: ids } } }) — RxDB's
 * batched query primitive — for any field, including the primary key.
 * (findByIds() is a slightly faster path when foreignField happens to be
 * the primary key, but $in works uniformly and keeps this adapter simple.)
 *
 * Reminder: if the relation is declared in the schema with `ref:
 * 'collectionName'` and read repeatedly, prefer RxDB's own
 * doc.populate('field') instead of this adapter — see
 * references/principle-and-spectrum.md.
 */
export function rxdbAdapter(collection: RxCollection): FetchAdapter {
  return {
    async findByField(field, ids) {
      const found = await collection.find({ selector: { [field]: { $in: ids } } }).exec();
      return found.map(doc => doc.toJSON());
    },
  };
}
