# Engine-Agnostic SQL Standards & Relational Modeling Reference

This reference guide establishes universal, engine-agnostic database principles and normalization trade-offs used across applications.

---

## 1. The Dumb Store Invariant Across Database Engines

Whether using an embedded engine (SQLite, DuckDB), a standalone RDBMS (PostgreSQL, MySQL), or a serverless data platform (Supabase, Neon, libSQL), the database is treated strictly as an atomic, reliable persistence layer:

```text
┌────────────────────────────────────────────────────────┐
│                   Application Layer                    │
│ • Business logic, invariants, state machines           │
│ • Parsing, validation, formatting, enrichment          │
│ • Unit-tested domain rules & error handling            │
└──────────────────────────┬───────────────────────────┘
                           │ (ANSI SQL / Parameterized Queries)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Database Layer                       │
│ • Dumb atomic store: rows, foreign keys, unique indexes│
│ • No triggers, no stored procedures, no business views │
│ • Explicit transactional boundaries                    │
└────────────────────────────────────────────────────────┘
```

---

## 2. Normalization Spectrum & Form Axioms

Schema design involves deliberate choices along the normalization spectrum. Application conventions define the agreed target:

```text
1NF ───► 2NF ───► 3NF ───► BCNF
          ▲
          └── Pragmatic Denormalization (e.g. read caches, reporting rollups)
```

### First Normal Form (1NF)
- **Axiom:** Every attribute domain contains only atomic scalar values; no repeating groups, comma-separated lists, or nested JSON arrays.
- **When Applied:** Fundamental baseline for all relational designs.

### Second Normal Form (2NF)
- **Axiom:** Table is in 1NF, and every non-prime attribute is fully functionally dependent on the entire candidate key (no partial key dependencies).

### Third Normal Form (3NF)
- **Axiom:** Table is in 2NF, and no non-prime attribute is transitively dependent on any candidate key (if $X \rightarrow Y$ and $Y \rightarrow Z$, then $Z$ must not live in table $X$).
- **Trade-off:** Eliminates update anomalies and data duplication at the cost of requiring multi-table joins.

### Boyce-Codd Normal Form (BCNF)
- **Axiom:** For every non-trivial functional dependency $X \rightarrow Y$, $X$ must be a superkey.

### Pragmatic Denormalization Trade-offs
When high-throughput read latency or analytical aggregation justifies violating 3NF:
- Document the intentional redundancy explicitly.
- Define the single source of truth and the synchronization mechanism in the application layer.

---

## 3. Explicit Prohibitions & Rationale

| Prohibited Construct | Systematic Danger | Production Alternative |
|---|---|---|
| **Database Triggers** | Hidden side effects, execution order ambiguity, untestable logic outside CI suites. | Domain events, repository transaction methods, application pipeline hooks. |
| **Business Logic Views** | Performance degradation, leaky abstraction across DB/app layers. | Parameterized application repository queries with explicit projection lists. |
| **JSON / JSONB Columns** | Loss of schema enforcement, inability to declare foreign keys on internal properties. | Normalized 1:N or M:N child tables. (Exception: purely opaque client settings dictionary). |
| **Stored Procedures** | Vendor lock-in, fragmented version control, impossible local unit testing. | Application-layer transactional command handlers. |
| **Database-Side Timestamps** | Non-deterministic tests, server clock drift between app and DB nodes. | ISO8601 UTC timestamp generated in application memory and passed via query parameters. |
