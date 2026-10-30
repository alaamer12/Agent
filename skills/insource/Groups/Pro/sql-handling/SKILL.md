---
name: sql-handling
description: "Establishes engine-agnostic SQL standards and relational modeling discipline in two phases - Stage 1 the SQL conventions document (dumb-store rule, prohibited triggers/views/stored procedures, canonical types, ISO8601 UTC timestamps, pervasive parameterization, transaction boundaries), then Stage 2 the application table reference (schema strategy chosen with the user: 3NF/BCNF, pragmatic denormalization, or a document hybrid; entities and lifecycles, dependencies, ANSI DDL with foreign keys, column specifications, canonical queries). Invoke it on its own for schema design, SQL review, or writing docs/table-reference.md; it also serves as the data step of a standards pass such as `like-a-pro`. Vendor-neutral (PostgreSQL, SQLite, MySQL, Supabase, Neon) and conversational - no forced 3NF. Standalone; no orchestration required."
---

# SQL Handling Skill

The **sql-handling** skill establishes and enforces database-agnostic SQL standards and relational modeling discipline. It operates independently of specific RDBMS vendors (PostgreSQL, SQLite, MySQL, Supabase, Neon, etc.) by enforcing the **Dumb Store philosophy** and producing structured, documented schema references aligned with the project's chosen data architecture (e.g., normalized relational, read-optimized/denormalized, or hybrid document-relational).

---

## 1. When to Use

- When establishing database conventions for a confirmed application.
- When creating or reviewing database schemas, tables, and relationships.
- When drafting the application's table reference documentation (`docs/table-reference.md`).
- As the data step of a standards pass (`like-a-pro` invokes it this way) - a use case, not
  a requirement: it runs alone.

---

## 2. Scope: one application, confirmed

Standards apply **per application**, not per repository: in a monorepo each deployable gets its own
conventions document and table reference. Candidate apps are identified from buildable units, deployment
manifests and workspace roots - never from directory names alone. If the target is not already agreed,
list the candidates with their evidence and ask which one before designing anything.

---

## 3. The Two-Phase Methodology

Execution operates across two sequential phases:

```text
┌────────────────────────────────────────────────────────┐
│                sql-handling Lifecycle                  │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Phase 1: Application SQL Conventions                 │
 │ • Dumb store rule (business logic in app layer)      │
 │ • Core prohibitions (triggers, views, sprocs, JSON)  │
 │ • Canonical data types, ISO8601 UTC dates, booleans  │
 │ • Parameterized queries & transaction boundaries     │
 │ ➔ Output: .repertoire/.steering/<app>/tech/          │
 │           sql-conventions.md                         │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Phase 2: Application Table Reference & Schema Design │
 │ • Clarify schema modeling strategy (Normalized vs   │
 │   Pragmatic Denormalized vs Document Hybrid)         │
 │ • Document real-world entities & lifecycles          │
 │ • Map dependencies or entity boundaries              │
 │ • Record schema rationale & trade-offs               │
 │ • Standard ANSI DDL generation with foreign keys     │
 │ • Column Reference specifications                    │
 │ • Canonical parameterized application queries        │
 │ ➔ Output: docs/table-reference.md                    │
 └──────────────────────────────────────────────────────┘
```

---

## 4. Core Universal Invariants

1. **Dumb Store Invariant:** The database is an atomic, durable store. Business logic, validation, state machines, and ranking belong in the application code.
2. **Prohibited Constructs:** Triggers, views with embedded logic, and stored procedures are strictly banned. Semi-structured/JSON storage is governed by the agreed application schema strategy.
3. **Pervasive Parameterization:** String concatenation in SQL is prohibited; all queries must use parameters (`@param`, `?`, `$1`).
4. **Application Timestamps:** Timestamps are formatted as ISO8601 UTC strings or standard timestamp types passed from the application layer.
5. **Explicit Schema Strategy Agreement:** The schema design strategy (e.g. 3NF, BCNF, flat denormalized, or reporting star/snowflake) is an intentional architectural question decided and recorded with the user.

---

## 5. References & Assets

- **Engine-Agnostic SQL Principles:** See [references/engine-agnostic-sql-principles.md](references/engine-agnostic-sql-principles.md) for core modeling patterns, normalization options, and prohibition rationales.
- **Phase 1 Template (SQL Conventions):** See [assets/templates/sql-conventions-template.md](assets/templates/sql-conventions-template.md) for the copyable conventions skeleton.
- **Phase 2 Template (Table Reference):** See [assets/templates/table-reference-template.md](assets/templates/table-reference-template.md) for the flexible table reference skeleton.
- **Execution Walkthrough:** See [examples/sql-walkthrough.md](examples/sql-walkthrough.md) for an end-to-end example.
