---
name: type-up
description: >-
  Converts plain primitive types (string, number, boolean, etc.) into a
  professional typing system with semantic aliases, documentation, runtime
  validation, and tests. Use when the user asks for better types, semantic
  types, branded/NewType types, config typing, API contracts, PathLike-style
  aliases, schema validation, or professional typing for public surfaces.
---

# type-up

Turn **basic primitive fields** into a **documented, validated type system** that helps editors, authors, runtime safety, and CI — while remaining practical for consumers.

---

## When to use

- Configuration shapes, public APIs, domain contracts, CLI patches
- User says: "professional types", "semantic types", "branded types", "NewType",
  "add validation", "improve types", "PathLike", "schema for config"
- Any public surface where intent is lost behind `string` / `int` / `bool`

**Not for:** pure internal implementation details with no public or shared surface — keep those lightweight.

---

## Core Principles (language-agnostic)

| Principle | Why |
|-----------|-----|
| **Semantic aliases over raw primitives** | `PathLike`, `CheckId`, `PositiveInt` document intent without forcing casts on every consumer |
| **Refinement where format/range matters** | Template literals, NewTypes, branded types, or constrained aliases |
| **Unions / enums over free-form strings** | Closed sets of allowed values |
| **Multiple layers of safety** | Static types (authoring) → runtime validation (production) → schema / property tests (dev/CI) |
| **Zero or minimal runtime cost in core** | Keep production validators lightweight; put heavier schema libs in optional/dev packages |
| **Keep layers in sync** | One conceptual change updates types, validator, and schema together |
| **Document with examples** | Every public type or config field should show real usage |

---

## Workflow (checklist)

```
- [ ] 1. Inventory fields — list every property, current type, real-world constraints & invariants
- [ ] 2. Name semantic primitives — PathLike, GlobPattern, PositiveInt, Identifier, etc.
- [ ] 3. Choose representation strategy per language (alias / NewType / branded / opaque)
- [ ] 4. Compose interfaces / structs / records for the public surface
- [ ] 5. Add layered variants if needed (raw config vs resolved / patched)
- [ ] 6. Mirror constraints in a runtime validator (lightweight, production-safe)
- [ ] 7. Add schema / generative tests for the types package or equivalent
- [ ] 8. Document usage patterns and keep a sync table of field → type → validator → schema
```

---

## Recommended package / module layout (adapt per ecosystem)

```
types/ or contracts/
  <domain>.types.<ext>     # public type definitions + docs
  primitives.<ext>         # shared semantic aliases
  schema.<ext>             # validation schema (Zod, Pydantic, etc.)
  validate.<ext>           # lightweight runtime checks
  tests/                   # schema + round-trip tests
```

---

## Definition of done

- [ ] No bare primitives on public fields where domain semantics exist
- [ ] Semantic types carry documentation and usage examples
- [ ] Runtime validator enforces the same constraints as the static types
- [ ] Schema / property tests pass
- [ ] Layers stay synchronized (documented sync table or single source of truth)
- [ ] Consumers can use the types without friction (no mandatory casts in common cases)

---

## Additional resources

- [references/typing-principles.md](references/typing-principles.md) — layering, primitive catalog, trade-offs
- [examples/polyglot-walkthrough.md](examples/polyglot-walkthrough.md) — before/after across languages
