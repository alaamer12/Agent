import type { Table } from 'dexie';
import type { FetchAdapter } from './implementation.universal';

/**
 * Dexie adapter. Uses table.where(field).anyOf(ids) for an indexed field,
 * or table.bulkGet(ids) when the field is the primary key — both are
 * genuinely fast single-pass IndexedDB operations, unlike looping .get()
 * calls (see references/engine-adapters.md for measured performance
 * differences).
 *
 * IMPORTANT: `field` must be an indexed property in the Dexie schema
 * (declared in db.version(n).stores({...})) for where().anyOf() to work.
 * Querying a non-indexed field will throw at runtime — add the index
 * rather than falling back to an unindexed scan.
 */
export function dexieAdapter(table: Table): FetchAdapter {
  return {
    async findByField(field, ids) {
      const primaryKeyName = table.schema.primKey.name;

      if (field === primaryKeyName) {
        const results = await table.bulkGet(ids);
        return results.filter(Boolean) as Record<string, any>[];
      }

      return table.where(field).anyOf(ids).toArray();
    },
  };
}
