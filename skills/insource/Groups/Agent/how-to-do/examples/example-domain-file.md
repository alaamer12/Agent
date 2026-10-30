# Changing Table Schemas

<!--
  This file documents HOW to correctly perform a class of related changes in
  this codebase — e.g. all schema-table operations, all auth-flow changes,
  all build-pipeline changes. It is not a log of what was done; it is a
  generalized, reusable procedure derived from real completed tasks.

  Each task below is addressable by its bracketed ID. Task-IDs are added
  here over time as new kinds of tasks in this domain come up. Patches are
  appended under a task-ID when an existing procedure turns out to be
  incomplete for a new instance of that task.
-->

## Tasks in this file

- [TBL-ADD] Add new table to schema — a new entity/table is needed, with no changes to existing tables

---

### [TBL-ADD] Add new table to schema
<!-- id: TBL-ADD | domain: changing-table-schemas | status: draft -->

**Matches queries like:** "add a table for X", "add [thing] into schema", "new entity for Y", "create a table to store Z"

**Origin query (raw):** "add a table for catalog"
**Origin query (interpolated):** Add a new `catalog` table to the schema, with columns matching whatever fields the catalog entity needs, wired into the existing schema/migration/type pipeline the same way other tables are.

**Preconditions:**
- Schema definitions live under `/src/db/schema/`, one file per table
- Migrations are generated with `drizzle-kit generate`, not hand-written
- Every table must be re-exported from the schema barrel file to be visible to the API layer

**Steps:**

##### Step 1 — Define the table schema
- Files:
  - `/src/db/schema/<table-name>.ts` — define the table using `pgTable(...)`, with columns matching whatever fields the request actually calls for (not a fixed column set — this varies per table)
  - `/src/db/schema/index.ts` — add `export * from './<table-name>'`
- Why: a table only defined but not exported doesn't get picked up anywhere else in the pipeline — it silently behaves as if it doesn't exist to the rest of the codebase, even though the file is there.

##### Step 2 — Add relations
- Files:
  - `/src/db/schema/<table-name>.ts` — if the table references or is referenced by another table, add a `relations(...)` block
- Why: this repo's ORM does not infer relations from foreign key columns alone; without an explicit `relations()` block, relational queries (`.with: { ... }`) silently return `undefined` instead of erroring.

##### Step 3 — Export from barrel file
- Files:
  - `/src/db/index.ts` — add the new table to the exported table map object
- Why: the API layer resolves tables by name through this map, not by importing schema files directly. A table only in `schema/index.ts` but missing here will fail at the API layer with a confusing "table not found" error that looks unrelated to the actual cause.

##### Step 4 — Generate migration
- Command: `npm run db:generate`
- Files:
  - `/drizzle/migrations/<generated-timestamp>_<name>.sql` — auto-generated, do not hand-edit
- Why: —

##### Step 5 — Register table in seed/type layer
- Files:
  - `/src/db/seed.ts` — add an entry to the `tableRegistry` array (even if not seeding data yet, this array drives dev-mode table reset scripts)
  - `/src/types/generated.ts` — regenerate via `npm run types:generate`, do not hand-edit
- Why: `tableRegistry` is what `db:reset` iterates over in local dev; a table missing here silently survives resets that are supposed to wipe it, which has caused stale-data confusion before.

##### Step 6 — Seed with dummy data *(optional)*
- Condition: only if the query explicitly mentions seeding, dummy data, sample data, or fixtures
- Files:
  - `/src/db/seed.ts` — add a `db.insert(<table>).values([...])` block with representative sample rows matching the table's actual columns
- Why: —

**Verification:**
- `npm run db:generate` produces a migration file with no manual edits needed afterward
- `npm run typecheck` passes (confirms Step 5's type regeneration picked up the new table)
- A query through the API layer against the new table resolves without a "table not found" error (confirms Step 3)

---
#### Patches
<!-- newest first -->

##### Patch — 2026-09-18

**Raw query:** "add a soft-delete flag to the catalog table"
**Interpolated query:** Add a nullable `deleted_at` timestamp column to the existing `catalog` table so rows can be soft-deleted instead of hard-deleted. No cascade behavior specified.

**Missing/extra step found:**
> After Step 4 (generate migration), the soft-delete middleware config also needs the table registered, or soft-deleted rows keep appearing in default queries even though the column exists and the migration applied cleanly.
- Files:
  - `/src/db/middleware/soft-delete.ts` — add `catalog` to the `SOFT_DELETE_TABLES` list so the query builder auto-filters `deleted_at IS NOT NULL`

**Insert as:** new optional Step 6.5, condition: "query mentions soft-delete, `deleted_at`, or non-destructive deletion"

**Scope note:** This is specific to soft-delete columns, not all new columns — a plain new column (e.g. a `description` text field) would not need the middleware registration step. Not yet confirmed across a second soft-delete instance, so left as a patch rather than promoted into the base Steps.
