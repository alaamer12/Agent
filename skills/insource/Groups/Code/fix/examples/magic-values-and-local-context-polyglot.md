# Incomplete-Fix Risks: Hard-coded Values & Local Context — Polyglot Walkthrough

**Principle (Fix skill):** A correct immediate fix can still leave the system inconsistent. Two common illustrations (not obligations) are:

1. The same meaningful value appearing under different names or as bare literals.
2. Sibling instances in the same contextual block that still contain the original defect.

Magic numbers are simply a frequent example of the first case; linters often flag them. The real obligation is consistency within the relevant context of the change.

## 1. Example: hard-coded value consolidation

### Before
```text
// service_a.go
const maxRetries = 10

// service_b.py
RETRY_LIMIT = 10

// config.yaml
max_attempts: 10
```

### After (shared constant)
Choose the language’s idiomatic shared location:

**TypeScript / shared package**
```typescript
// packages/shared/src/limits.ts
export const MAX_RETRIES = 10 as const;
```

**Python**
```python
# shared/constants.py
MAX_RETRIES: Final[int] = 10
```

**Go**
```go
// internal/limits/limits.go
const MaxRetries = 10
```

**Rust**
```rust
// crates/shared/src/limits.rs
pub const MAX_RETRIES: u32 = 10;
```

Then update every occurrence that represents the **same concept**.

## 2. Local context generalization (UI example)

Three cards that share the same icon layout. Fix discovered in Card A.

### Anti-pattern
Fix only Card A and stop.

### Correct local generalization
Inspect Card B and Card C (same visual/logical block, same implementation pattern). Apply the same alignment/spacing correction if the underlying issue is present.

This stays inside the relevant context. It does **not** justify scanning unrelated pages or back-end services.

## Key rules
- Search by constant name **and** by the raw value.
- Different names (`MAX_RETRIES` vs `RETRY_LIMIT`) may still represent the same concept.
- Local generalization is required for clear siblings; unbounded codebase-wide search is not.