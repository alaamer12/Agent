# Universal SQL Conventions Template

Use this universal template when establishing Phase 1 SQL storage conventions for any application. Fill in or adapt the choices (<...>) based on the application's engine, requirements, and domain.

```markdown
# SQL Conventions & Storage Architecture — <Application Name>

> **Scope:** Relational schema conventions, DDL standards, queries, and transactions for `<Application Name>`.
> **Philosophy:** Database as a Dumb Store. Portability and explicit application-layer control.

---

## 1. Storage Philosophy: The Dumb Store Rule

The database is an atomic, durable, queryable data store. It does **not** contain business logic, autonomous data mutations, or unversioned operational decisions.

- **Application Authority:** Parsing, business rules, validation, status transitions, search re-ranking, and conflict resolution belong exclusively in the application layer.
- **Portability & Isolation:** Schema designs avoid vendor lock-in and non-portable database extensions.
- **Boundary Invariant:** If logic can be executed and unit-tested in the application layer, execute it in the application layer. Use SQL for persistence, relational integrity, and indexed retrieval.

---

## 2. Structural Patterns & Boundaries (Allowed vs Restricted)

Clarify which database features are permitted, restricted, or prohibited for this application:

| Architectural Pattern | Policy for Application | Rationale & Boundaries |
|---|---|---|
| **Triggers** | <Prohibited / Restricted> | Hidden side effects outside application code; replaced by application repository/unit-of-work logic. |
| **Views / Materialized Views** | <Prohibited / Read-Only Reporting Only> | Avoid coupling domain business logic to DB engine views. |
| **JSON / Semi-Structured Columns** | <Prohibited / Restricted to Key-Value settings> | Normalized relational child tables preferred; JSON allowed only for unstructured user preferences. |
| **Stored Procedures** | <Prohibited / Minimal> | Domain logic resides in version-controlled application code. |
| **Auto-Increment vs UUIDs** | <UUIDv7 / BIGINT Identity / Sequential INT> | Consistent identifier generation strategy across services. |
| **Time Authority** | <App-generated UTC / Engine NOW()> | Pervasive ISO8601 UTC timestamps coordinated by the application. |

---

## 3. Data Types & Canonical Column Representations

Map the application's domain primitives into canonical SQL data types:

| Conceptual Domain Type | Target SQL Type (e.g. Postgres / SQLite / MySQL) | Constraints & Default Standards | Anti-Patterns to Avoid |
|---|---|---|---|
| **Primary Identifier** | `<BIGINT / UUID / VARCHAR(36) / INTEGER>` | `PRIMARY KEY` | Mutable or unindexed natural keys |
| **Short Text / Title** | `<VARCHAR(N) / TEXT>` | `NOT NULL DEFAULT ''` (if empty allowed) | Unbounded text for fixed-length codes |
| **Long Text / Body** | `<TEXT>` | `NOT NULL` | Storing structured tables inside text |
| **Boolean Flag** | `<BOOLEAN / SMALLINT / INTEGER (0/1)>` | `NOT NULL DEFAULT <0/false>` | Inconsistent string booleans (`'true'`, `'Y'`) |
| **Timestamp / Instant** | `<TIMESTAMP WITH TIME ZONE / TEXT (ISO8601)>` | Standardized UTC format | Naked Unix epoch ints or timezone-naive strings |
| **Enumeration / State** | `<TEXT / VARCHAR(32) / ENUM>` | `CHECK (col IN (...))` or Enum | Opaque magic integers without documentation |
| **Monetary / Precise Decimal**| `<NUMERIC(P, S) / BIGINT (minor units)>` | Exact decimal or integer cents | Floating-point `REAL`/`FLOAT` for money |

---

## 4. Query Safety & Parameterization

Every query executed by the application must use parameterized bindings (`@param`, `?`, or `$1` depending on client driver):

- **Zero String Concatenation:** Never concatenate raw user input or runtime values into SQL strings.
- **Dynamic Queries:** Dynamic query composition must append bound parameters, never raw literals.

---

## 5. Naming Conventions

Define the naming rules for this application's schema:
- **Tables:** `<snake_case, pluralized (e.g. users, orders, items) / PascalCase / singular>`
- **Association / Join Tables:** `<composite names e.g. user_roles, order_items>`
- **Columns:** `<snake_case (e.g. user_id, created_at, is_active)>`
- **Foreign Keys:** `<singular_parent>_id` (e.g. `order_id` references `orders(id)`)
- **Timestamps:** Suffix `<_at / _time>` (e.g. `created_at`, `updated_at`, `deleted_at`)
- **Booleans:** Prefix `<is_ / has_ / can_>` (e.g. `is_active`, `has_verified_email`)

---

## 6. Transactions & Concurrency

1. **Explicit Scoping:** Multi-table mutations must be wrapped in explicit application-managed transactions.
2. **Minimal Duration:** Perform network calls, external API queries, and heavy transformations **before** entering the database transaction.
3. **Conflict Handling:** Use deterministic upsert semantics (`ON CONFLICT` / `MERGE` / `INSERT IGNORE`) where idempotency is required.
```
