> **Preserved original** (the body of the first `SKILL.md`), kept intact with terminology updated to [terminology](terminology.md): brands, the three checks, variants.

# type-up

Turn **raw-type fields** into a **documented, validated type system** that helps editors, authors, runtime safety, and CI — while remaining practical for consumers.

---

## When to use

- Configuration shapes, public APIs, domain contracts, CLI patches
- User says: "professional types", "brands", "branded types", "NewType",
  "add validation", "improve types", "PathLike", "schema for config"
- Any public surface where intent is lost behind `string` / `int` / `bool`

**Not for:** pure internal implementation details with no public or shared surface — keep those lightweight.

---

## Core Principles (language-agnostic)

| Principle | Why |
|-----------|-----|
| **Brands over raw types** | `PathLike`, `CheckId`, `PositiveInt` document intent without forcing casts on every consumer |
| **Refinement where format/range matters** | Template literals, NewTypes, branded types, or constrained aliases |
| **Unions / enums over free-form strings** | Closed sets of allowed values |
| **Multiple checks** | Static types (authoring) → runtime validation (production) → schema / property tests (dev/CI) |
| **Zero or minimal runtime cost in core** | Keep production creation points lightweight; put heavier validation libraries in optional/dev packages |
| **Keep checks in sync** | One conceptual change updates types, creation points, and schema together |
| **Document with examples** | Every public type or config field should show real usage |

---

## Workflow (checklist)

```
- [ ] 1. Inventory fields — list every property, current type, real-world constraints & invariants
- [ ] 2. Name brands — PathLike, GlobPattern, PositiveInt, Identifier, etc.
- [ ] 3. Choose representation strategy per language (alias / NewType / branded / opaque)
- [ ] 4. Compose interfaces / structs / records for the public surface
- [ ] 5. Add variants if needed (raw / patch / resolved)
- [ ] 6. Mirror constraints in creation points (runtime, lightweight, production-safe)
- [ ] 7. Add schema / generative tests for the types package or equivalent
- [ ] 8. Document usage patterns and keep a sync table of field → type → creation point → schema
```

---

## Recommended package / module layout (adapt per ecosystem)

```
types/ or contracts/
  <domain>.types.<ext>     # public type definitions + docs
  primitives.<ext>         # shared brands
  schema.<ext>             # validation schema (Zod, Pydantic, etc.)
  validate.<ext>           # lightweight runtime checks
  tests/                   # schema + round-trip tests
```

---

## Definition of done

- [ ] No raw types on public fields where a domain meaning exists
- [ ] Brands carry documentation and usage examples
- [ ] Creation points enforce the same constraints as the static types
- [ ] Schema / property tests pass
- [ ] Checks stay synchronized (documented sync table or single source of truth)
- [ ] Consumers can use the types without friction (no mandatory casts in common cases)

---

## Additional resources

- [references/typing-principles.md](typing-principles.md) — the three checks, brand catalog, trade-offs
- [examples/polyglot-walkthrough.md](../examples/polyglot-walkthrough.md) — before/after across languages
