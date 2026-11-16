/**
 * Universal attach-chain core.
 *
 * This file contains everything that does NOT change between engines:
 *   - the immutability guarantee
 *   - the attachGroup flatten/batch/re-nest combinator
 *   - the ordering guard (assertPathResolvable)
 *   - the attachTo(...).one().many().group() chain, with no .build()/.exec()
 *
 * What DOES change per engine is the batched-fetch call itself — that's
 * captured by the FetchAdapter interface below. See references/engine-*.ts
 * for concrete adapters (RxDB, Dexie, PouchDB, MongoDB).
 *
 * Read references/principle-and-spectrum.md before using this on an engine
 * with a native join (MongoDB) — this pattern is a fallback there, not the
 * default.
 */

type PlainDoc = Record<string, any>;

/**
 * The one piece every engine implements differently: given a set of foreign
 * keys, return the matching documents in a single batched call. Everything
 * else in this file is engine-agnostic and calls through this interface.
 */
export interface FetchAdapter {
  /**
   * Fetch documents where `field` is one of `ids`, in a single batched
   * round trip (never one call per id). Return plain objects, not
   * engine-native document wrappers — callers should not need to know
   * which engine produced a given attached value.
   */
  findByField(field: string, ids: any[]): Promise<PlainDoc[]>;
}

export interface AttachOneOptions<T> {
  adapter: FetchAdapter;
  localField: keyof T;
  foreignField: string; // explicit on the universal interface — engines differ on what a sane default primary key field even is
  as: string;
}

export interface AttachManyOptions<T> {
  adapter: FetchAdapter;
  localField: keyof T;
  foreignField: string;
  as: string;
}

// ---------------------------------------------------------------------------
// attachOne / attachMany — identical logic across every engine; only the
// adapter's findByField call differs underneath.
// ---------------------------------------------------------------------------

export async function attachOne<T extends PlainDoc>(
  rows: T[],
  opts: AttachOneOptions<T>,
): Promise<Array<T & Record<string, PlainDoc | null>>> {
  if (rows.length === 0) return [];

  const ids = [...new Set(rows.map(r => r[opts.localField as string]).filter(v => v != null))];
  if (ids.length === 0) return rows.map(r => ({ ...r, [opts.as]: null }));

  const foreignDocs = await opts.adapter.findByField(opts.foreignField, ids);
  const byKey = new Map(foreignDocs.map(d => [d[opts.foreignField], d]));

  return rows.map(r => ({ ...r, [opts.as]: byKey.get(r[opts.localField as string]) ?? null }));
}

export async function attachMany<T extends PlainDoc>(
  rows: T[],
  opts: AttachManyOptions<T>,
): Promise<Array<T & Record<string, PlainDoc[]>>> {
  if (rows.length === 0) return [];

  const ids = [...new Set(rows.map(r => r[opts.localField as string]).filter(v => v != null))];
  if (ids.length === 0) return rows.map(r => ({ ...r, [opts.as]: [] }));

  const foreignDocs = await opts.adapter.findByField(opts.foreignField, ids);

  const grouped = new Map<any, PlainDoc[]>();
  for (const doc of foreignDocs) {
    const key = doc[opts.foreignField];
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key)!.push(doc);
  }

  return rows.map(r => ({ ...r, [opts.as]: grouped.get(r[opts.localField as string]) ?? [] }));
}

// ---------------------------------------------------------------------------
// attachGroup — engine-agnostic; operates purely on already-fetched plain
// objects, so it needs no adapter at all.
// ---------------------------------------------------------------------------

export async function attachGroup<T extends PlainDoc>(
  rows: T[],
  path: string,
  attach: (flat: PlainDoc[]) => Promise<PlainDoc[]>,
): Promise<T[]> {
  assertPathResolvable(rows, path);

  const keys = path.split('.');
  const get = (obj: any) => keys.reduce((o, k) => o?.[k], obj);

  const owners: { rowIndex: number; isArray: boolean }[] = [];
  const flat: PlainDoc[] = [];

  rows.forEach((row, rowIndex) => {
    const val = get(row);
    if (Array.isArray(val)) {
      val.forEach((v: PlainDoc) => { flat.push(v); owners.push({ rowIndex, isArray: true }); });
    } else if (val != null) {
      flat.push(val);
      owners.push({ rowIndex, isArray: false });
    }
  });

  const attached = await attach(flat);

  const perRow = new Map<number, PlainDoc[]>();
  attached.forEach((item, i) => {
    const { rowIndex } = owners[i];
    if (!perRow.has(rowIndex)) perRow.set(rowIndex, []);
    perRow.get(rowIndex)!.push(item);
  });

  return rows.map((row, rowIndex) => {
    const items = perRow.get(rowIndex) ?? [];
    const wasArray = owners.find(o => o.rowIndex === rowIndex)?.isArray ?? true;
    return setImmutable(row, keys, wasArray ? items : (items[0] ?? null));
  });
}

function setImmutable(obj: PlainDoc, keys: string[], value: any): PlainDoc {
  const [head, ...rest] = keys;
  if (rest.length === 0) return { ...obj, [head]: value };
  const child = obj[head];
  if (Array.isArray(child)) {
    throw new Error(
      `attachGroup: cannot set nested path through an array at '${head}'. ` +
      `Call attachGroup once per level instead of a single multi-level path through an array.`,
    );
  }
  return { ...obj, [head]: setImmutable(child ?? {}, rest, value) };
}

function assertPathResolvable<T extends PlainDoc>(rows: T[], path: string): void {
  const keys = path.split('.');
  let current: any[] = rows;
  let walked = '';

  for (const key of keys) {
    walked = walked ? `${walked}.${key}` : key;
    const next: any[] = [];
    let anyRowHadKey = false;

    for (const item of current) {
      if (item == null) continue;
      if (Object.prototype.hasOwnProperty.call(item, key)) {
        anyRowHadKey = true;
        const val = item[key];
        if (Array.isArray(val)) next.push(...val);
        else if (val != null) next.push(val);
      }
    }

    if (!anyRowHadKey) {
      throw new Error(
        `attachTo(...).group('${path}') failed: '${walked}' does not exist on any row.\n` +
        `This usually means a required .one()/.many()/.group() step is missing earlier ` +
        `in the chain, or the steps are out of order (e.g. .group('${path}') was called ` +
        `before the step that attaches '${keys[0]}').`,
      );
    }

    current = next;
  }
}

// ---------------------------------------------------------------------------
// attachTo — the universal chain. Identical for every engine because it
// only ever calls attachOne/attachMany/attachGroup, never an engine API
// directly. Swap engines by swapping the FetchAdapter passed into .one()/
// .many() — nothing about the chain itself changes.
// ---------------------------------------------------------------------------

export class AttachChain<T extends PlainDoc> implements PromiseLike<T[]> {
  private pending: Promise<T[]>;

  constructor(rows: T[]) {
    this.pending = Promise.resolve(rows);
  }

  one(opts: AttachOneOptions<T>): AttachChain<T> {
    this.pending = this.pending.then(rows => attachOne(rows, opts)) as Promise<T[]>;
    return this;
  }

  many(opts: AttachManyOptions<T>): AttachChain<T> {
    this.pending = this.pending.then(rows => attachMany(rows, opts)) as Promise<T[]>;
    return this;
  }

  group(path: string, attach: (flat: PlainDoc[]) => Promise<PlainDoc[]>): AttachChain<T> {
    this.pending = this.pending.then(rows => attachGroup(rows, path, attach));
    return this;
  }

  then<TResult1 = T[], TResult2 = never>(
    onfulfilled?: ((value: T[]) => TResult1 | PromiseLike<TResult1>) | null,
    onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | null,
  ): Promise<TResult1 | TResult2> {
    return this.pending.then(onfulfilled, onrejected);
  }
}

export function attachTo<T extends PlainDoc>(rows: T[]): AttachChain<T> {
  return new AttachChain(rows);
}
