---
name: sql-conventional
description: Establishes engine-agnostic SQL standards, relational database architecture, and generates application table references with customizable schema strategies for a confirmed application. Use when designing database schemas, reviewing SQL patterns, or authoring table specifications.
---

# SQL Conventional Skill

The **sql-conventional** skill establishes and enforces database-agnostic SQL standards and relational modeling discipline. It operates independently of specific RDBMS vendors (PostgreSQL, SQLite, MySQL, Supabase, Neon, etc.) by enforcing the **Dumb Store philosophy** and producing structured, documented schema references aligned with the project's chosen data architecture (e.g., normalized relational, read-optimized/denormalized, or hybrid document-relational).

---

## 1. When to Use

- When establishing database conventions for a confirmed application.
- When creating or reviewing database schemas, tables, and relationships.
- When drafting the application's table reference documentation (`docs/table-reference.md`).
- As the second technical conventions step within the `like-a-pro` meta-skill lifecycle.

---

## 2. The Two-Phase Methodology

Execution operates across two sequential phases:

```text
┌────────────────────────────────────────────────────────┐
│               sql-conventional Lifecycle               │
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

## 3. Core Universal Invariants

1. **Dumb Store Invariant:** The database is an atomic, durable store. Business logic, validation, state machines, and ranking belong in the application code.
2. **Prohibited Constructs:** Triggers, views with embedded logic, and stored procedures are strictly banned. Semi-structured/JSON storage is governed by the agreed application schema strategy.
3. **Pervasive Parameterization:** String concatenation in SQL is prohibited; all queries must use parameters (`@param`, `?`, `$1`).
4. **Application Timestamps:** Timestamps are formatted as ISO8601 UTC strings or standard timestamp types passed from the application layer.
5. **Explicit Schema Strategy Agreement:** The schema design strategy (e.g. 3NF, BCNF, flat denormalized, or reporting star/snowflake) is an intentional architectural question decided and recorded with the user.

---

## 4. References & Assets

- **Engine-Agnostic SQL Principles:** See [references/engine-agnostic-sql-principles.md](references/engine-agnostic-sql-principles.md) for core modeling patterns, normalization options, and prohibition rationales.
- **Phase 1 Template (SQL Conventions):** See [assets/templates/sql-conventions-template.md](assets/templates/sql-conventions-template.md) for the copyable conventions skeleton.
- **Phase 2 Template (Table Reference):** See [assets/templates/table-reference-template.md](assets/templates/table-reference-template.md) for the flexible table reference skeleton.
- **Execution Walkthrough:** See [examples/sql-walkthrough.md](examples/sql-walkthrough.md) for an end-to-end example.
