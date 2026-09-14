# Table Reference Template (Phase 2 Specification)

Use this template as the standard skeleton when generating Phase 2 Application Table References (`docs/table-reference.md`).

```markdown
# Table Reference & Relational Schema: <Application Name>

> **Schema Strategy:** <e.g. 3NF Normalized / Pragmatic 2NF / Read-Optimized Denormalized / Star Schema>
> Every table defines: Purpose → Structural Boundaries & Dependencies → Schema Rationale / Normalization Target → DDL → Column Reference → Canonical Queries.

---

## Schema Summary Table

| Table Name | Primary Key | Schema Strategy / NF | Purpose |
|---|---|---|---|
| `<table_1>` | `<pk_col>` | <Strategy / e.g. 3NF or Denormalized> | `<brief summary>` |
| `<table_2>` | `<pk_col>` | <Strategy / e.g. 3NF or Denormalized> | `<brief summary>` |

---

## 1. `<table_name>`

### Purpose
<Explain what real-world entity, event, or relationship this table persists and its lifecycle in the application.>

### Structural Boundaries & Functional Dependencies
<List entity boundaries, ownership, or non-trivial functional dependencies if normalized:>
```text
<pk_column> → <attr_1>
<pk_column> → <attr_2>
```

### Schema Rationale & Normalization Assessment
<Document why this schema structure was chosen and how it meets the application's goals (e.g. 3NF proof, or rationale for denormalization/caching):>

| Assessment Criterion | Status | Technical Rationale & Trade-offs |
|---|---|---|
| **Atomicity (1NF)** | <Satisfied / Documented Exception> | <Explanation of atomic scalar values or justified semi-structured fields.> |
| **Key Dependency (2NF/3NF/BCNF)** | <Satisfied / Pragmatically Denormalized> | <Explanation of dependencies or why fields were denormalized for query throughput.> |
| **Consistency / Sync Invariant** | <Enforced by DB / Enforced by App> | <How data integrity is maintained across mutations.> |

### DDL (Data Definition Language)
Standard ANSI SQL statement:
```sql
CREATE TABLE <table_name> (
    <column_1>      <TYPE>          PRIMARY KEY,
    <column_2>      <TYPE>          NOT NULL,
    <column_fk>     <TYPE>          NOT NULL REFERENCES <parent_table>(<parent_pk>),
    <status_col>    VARCHAR(32)     NOT NULL DEFAULT '<default>' CHECK (<status_col> IN ('<val1>', '<val2>')),
    created_at      VARCHAR(30)     NOT NULL,
    updated_at      VARCHAR(30)     NOT NULL
);

CREATE INDEX idx_<table_name>_<column_fk> ON <table_name>(<column_fk>);
```

### Column Reference
Detailed specification of columns, nullability, constraints, and semantics:

| Column | Data Type | Nullable | Constraint / Default | Semantic Description |
|---|---|---|---|---|
| `<column_1>` | `<TYPE>` | No | PRIMARY KEY | Unique identifier for the entity. |
| `<column_2>` | `<TYPE>` | No | NOT NULL | Explanatory description of the attribute. |
| `<column_fk>`| `<TYPE>` | No | FK → `parent(id)` | Relational link to owning entity. |
| `created_at` | `TEXT/TS` | No | ISO8601 UTC | Timestamp of record creation. |

### Canonical Queries
The standard, parameterized SQL queries used by the application repositories to interact with this table:

```sql
-- 1. Insert Entity
INSERT INTO <table_name> (<col1>, <col2>, created_at, updated_at)
VALUES (@col1, @col2, @created_at, @updated_at);

-- 2. Fetch by Primary Key
SELECT <col1>, <col2>, created_at, updated_at
FROM   <table_name>
WHERE  <column_1> = @id;

-- 3. Atomic Status Transition / Update
UPDATE <table_name>
SET    <status_col> = @new_status,
       updated_at   = @updated_at
WHERE  <column_1>   = @id
  AND  <status_col> = @expected_previous_status;
```
```
