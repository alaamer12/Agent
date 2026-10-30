# Test Data as Contracts

## Principle

Test data is not incidental. It is part of the executable contract of “how to test X”.

Every test must obtain its data through a named, reusable construction mechanism (factory, builder, or fixture). Hard-coded literals inside test bodies are treated as defects.

## Recommended shape

```
tests/
  factory/          # or fixtures/, contracts/, testdata/
    user.rs / user.py / UserFactory.ts
    order.rs
    ...
  unit/
  integration/
```

- One focused factory (or fixture module) per concept.
- Methods are role-named: `valid()`, `invalid()`, `expired()`, `with_items(n)`, `minimal()`, `comprehensive()`.
- Prefer returning domain types over primitives when the type system allows it.
- Generation must be deterministic or thread-safe when tests can run in parallel.

## Anti-patterns

- Hard-coded UUIDs, emails, amounts, or JSON blobs scattered through test files.
- God-object factories that create every possible entity.
- Shared mutable fixtures that tests mutate and leave behind.
- Production data copies that contain PII or change underfoot.

## Isolation techniques (language-agnostic)

- Per-test factories that create fresh data.
- Database transactions + rollback.
- Ephemeral databases or database branching.
- Containerized services with known seed data.
- In-memory fakes for unowned boundaries.

## Relationship to property-based testing

Factories supply the building blocks; property-based generators can reuse or compose them when the property needs rich domain objects.