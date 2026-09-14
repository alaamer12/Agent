# Walkthrough: Executing sql-conventional across an Application

This walkthrough demonstrates the end-to-end two-phase execution of `sql-conventional`.

---

## Phase 1: Establishing SQL Conventions

An application (e.g. order management service) requires database standards.
The agent evaluates the storage invariants:
1. **Dumb Store:** Prohibits database triggers for order totals or status notifications.
2. **Types & Dates:** All timestamps are typed as ISO8601 UTC strings or native timestamp with timezone, formatted by the application layer.
3. **Naming & Keys:** Surrogate `order_id` (UUIDv7 or BigInt), `orders` plural table name.
4. **Output Artifact:** Writes `.repertoire/.steering/<app-name>/tech/sql-conventions.md`.

---

## Phase 2: Generating the Application Table Reference

The application requires tables for `orders`, `line_items`, and `products`.

### Step 1: Inquiring & Agreeing on Schema Strategy
The agent discusses data volume, access patterns, and consistency needs with the user.
- **Decision:** Core transactional tables (`orders`, `line_items`, `products`) adopt a relational normalized design (3NF), while an optional read rollup table could be denormalized if high-throughput analytics are required later.

### Step 2: Mapping Functional Dependencies & Schema Boundaries
```text
orders:
  order_id → customer_id, status, placed_at, total_amount

line_items:
  (order_id, item_id) → product_id, quantity, unit_price
```

### Step 3: Assessing Schema Structure
- **Atomicity (1NF):** Quantities and prices are scalar values. No JSON lists of items embedded in `orders`.
- **Key Dependency (2NF/3NF):** `quantity` and `unit_price` in `line_items` depend on the whole composite key `(order_id, item_id)`. Product names reside in `products` to prevent transitive dependencies.
- **Consistency Invariant:** Total amounts are verified in the application layer during order placement transactions.

### Step 4: DDL Generation & Queries
```sql
CREATE TABLE orders (
    order_id    VARCHAR(36)     PRIMARY KEY,
    customer_id VARCHAR(36)     NOT NULL,
    status      VARCHAR(32)     NOT NULL CHECK (status IN ('pending', 'paid', 'shipped')),
    placed_at   VARCHAR(30)     NOT NULL
);

CREATE TABLE line_items (
    order_id    VARCHAR(36)     NOT NULL REFERENCES orders(order_id),
    item_id     INTEGER         NOT NULL,
    product_id  VARCHAR(36)     NOT NULL,
    quantity    INTEGER         NOT NULL CHECK (quantity > 0),
    unit_price  INTEGER         NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, item_id)
);
```

### Step 5: Canonical Queries
Parameterized repository queries are drafted for insertions and retrieval by primary key.

### Step 6: Output Artifact
The agent writes the complete table reference to `docs/table-reference.md`.
