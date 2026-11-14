# Database-layer debugging

Use when the failing component is the database or the app's view of it —
live DB disagrees with the schema definition (schema drift), migrations to
author/verify/roll forward safely, missing/duplicate/wrong rows,
constraints and RLS/policy surprises, ORM-generated SQL that isn't what it
looks like, slow queries and plan regressions, locks/deadlocks,
connection-pool exhaustion, replication-lag/stale reads.

Catalog queries per engine (PostgreSQL, MySQL, SQLite — example engines):
[`database-verification.md`](database-verification.md). Migration dry-run
template (PostgreSQL-family dialect; adapt):
[`../assets/test-migration.sql`](../assets/test-migration.sql). Concrete
inspectors: [`../examples/schema-inspector-polyglot.md`](../examples/schema-inspector-polyglot.md).

## The prime axiom

> **Never assume application state ≡ database state.**

Every data symptom is decided by comparing, in order: what the app *thinks*
it wrote/query → what SQL the ORM *actually* emitted (enable query logging /
inspect generated SQL) → what the DB **catalog and rows** actually say.
Each comparison splits the bug space in half: app-vs-ORM, ORM-vs-DB,
DB-vs-expected.

## Schema drift / mismatch — the canonical case

Symptom: code + live DB disagree (missing column, type/nullability skew,
policy drift), or environments disagree.

```
1. Extract expected   — read the project's schema definition: ORM schema
                       files, master SQL, migrations folder
2. Extract actual     — the engine's catalog queries (see the verification
                       reference)
3. Diff               — column/type/null/default/constraints/indexes/policies
4. Decide ground truth — which side is definitionally correct? (usually the
                       project's schema artifacts; a manual prod edit that
                       drifted the live DB still has to be reconciled)
5. Repair BOTH sides  — see source-of-truth rule
6. Verify with script — .debugging/tmp/ verify-schema tool, exit 0/1 —
                       strong promotion candidate (generalize --table)
```

### The source-of-truth rule (minimal-≠-incomplete, applied)

Fixing only the live DB leaves the defect in the *defining artifact*: the
next `db init`, recreate, or fresh-environment deploy reproduces the bug
exactly. The complete fix = live state repaired (or a migration applied)
**and** the schema file / master SQL / migration set corrected to match —
then both verified again from scratch (apply the corrected SQL in a
throwaway/transaction and re-run the comparison).

## Migrations — author & verify discipline

1. **Idempotent by design**: conditional-DDL forms wherever the engine has
   them — e.g. (PostgreSQL-family) `ADD COLUMN IF NOT EXISTS`,
   `CREATE INDEX IF NOT EXISTS`, `DROP POLICY IF EXISTS` + `CREATE POLICY`,
   `CREATE OR REPLACE`; security-definer functions get an explicit fixed
   search path. Engines without conditional DDL: guard with a catalog
   check in the same transaction.
2. **Dry-run in a transaction**: execute the DDL inside `BEGIN … ROLLBACK`
   first — [`../assets/test-migration.sql`](../assets/test-migration.sql)
   is the shape (apply → assert against catalog → rollback). Commit only
   when the assertions pass and the intent is real.
3. **Synchronize definitions**: ORM schema, migration files, and any
   canonical master SQL must all land on the same structure in the same
   change — half-synchronized migrations *are* drift.
4. **Reversibility question asked and answered** for destructive steps
   (drop/rename/type-change): data loss window, deploy order (expand →
   migrate → contract), and who executes it if credentials are read-only →
   escalation protocol, [`../SKILL.md`](../SKILL.md) stance 6 (prepared
   SQL in `.debugging/tmp/` for the user to paste into their SQL editor).

## Wrong / missing / duplicate rows

- **Missing** → soft-delete flags, tenant/RLS filters, an uncommitted
  write, a cascade, or a read from a lagging replica. Decide with a raw
  query bypassing app filters (and the policy/claim context for RLS).
- **Duplicate** → missing unique constraint + at-least-once delivery
  (consumer retries), non-atomic upsert, or double-write across code
  paths. The structural fix is usually the *constraint*, not a check in
  one writer — every writer must be unable to recreate it
  (stance: structurally impossible).
- **Wrong value** → trace who *last wrote it*: audit columns
  (`updated_at/by`), transaction logs, then the writer path in
  [`backend.md`](backend.md). The DB is the crime scene, not the criminal.

## Integrity enforced in the DB, not only in code

Application validation is bypassed by every other path (batch jobs, SQL
console, migrations, other services, test mocks). Where correctness
matters, the storage layer holds the final line: `CHECK`, `FOREIGN KEY`,
`UNIQUE`, `NOT NULL`, exclusion constraints, and policies. When fixing a
data bug, ask: *which DB-level constraint would have made this state
impossible?* — adding it is part of the complete fix.

## Locks, isolation & concurrency anomalies

- **Deadlock** → read the deadlock detail (which txns, which locks);
  usually opposite-ordered multi-row writes; fix by ordering or shrinking
  transactions.
- **Write skew** — the classic trap snapshot-isolation systems miss: two
  txns each *read* overlapping rows, satisfy an invariant from their
  reads (e.g. "≥1 doctor on call"), then write **disjoint** rows — both
  commit, invariant destroyed. Diagnose: inspect the actual emitted SQL
  pattern (read-then-write without lock); remediate: row locks on the
  guard rows (`SELECT … FOR UPDATE` family) or serializable isolation.
- **Stale/phantom/dirty reads, lost updates** → name the isolation level
  actually in effect (ORM default ≠ assumed default), then reproduce the
  interleaving (two harness processes are enough).
- **Pool exhaustion** → engine activity view (e.g. `pg_stat_activity`)
  counts vs pool size; the killer question: are connections leaking
  (unclosed in a path) or is real demand growing? —
  [`production.md`](production.md).

## Plan regressions (sudden slowness, no code change)

Run the engine's plan explainer (e.g. PostgreSQL
`EXPLAIN (ANALYZE, BUFFERS)`). Usual culprits in order: stale statistics
⇒ sequential scan where index existed (recheck `ANALYZE`), index dropped
by a migration, **implicit cast** (string parameter vs int column —
disables index usage per row), plan flip from row-count change. Compare
plans between known-good and now, not vibes.

## RLS / policy / grants

Always inspect all four together (`database-verification.md`): RLS
enabled?, which policies per command, target roles, `USING` vs `WITH
CHECK` expressions, and the actual grants. A "can read but can't update"
app symptom is usually policy/role context — e.g. on hosted platforms the
claim a policy reads (`auth.uid()`-style) is absent on service
connections — not an ORM bug.

---
**Better next stop:** writer paths → [`backend.md`](backend.md) ·
replication/production-environment differences → [`production.md`](production.md) ·
migration-test as permanent check → [`regression-testing.md`](regression-testing.md) ·
process → [`../SKILL.md`](../SKILL.md).
