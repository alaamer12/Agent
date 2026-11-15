# type-up: Principles Reference

> **Applies when the project adopts the tiered system** (Mode B in `../SKILL.md`). For general type enhancement without the tiers, use `core-workflow.md`.

Cross-tier rules. Tier-specific detail lives in [`../tiers/`](../tiers/); step-by-step conversion lives in the `transform-*` files in this folder.

## 1. Vocabulary

Every term is defined once in [terminology](./terminology.md). Use those terms and no synonyms.

## Naming: describe the role, follow the ecosystem

These files describe **roles**; the identifiers in examples are illustrative, not conventions to copy.

| Role | Described as | Example name here | Follow the ecosystem, for instance |
|------|--------------|-------------------|-----------------------------------|
| Plain type | "a raw type named as a deliberate no-rule choice" | `PlainString` | the language's own type; or whatever the project already calls it |
| Visible-state refinement | "a plain type narrowed to a state the value shows" | `UppercaseString` | a built-in (`Uppercase<string>`), a refined type (Scala `Iron`), a constraint type |
| Domain brand | "a refinement with a domain meaning" | `UserEmail` | `opaque type` (Scala), newtype (Rust, Haskell), `NewType` (Python), value class (Kotlin) |
| Creation point | "the one place a runtime value becomes the type" (a smart constructor) | `isUserEmail` | `TryFrom` / `FromStr` (Rust), `apply` / `from` (Scala), `New…` (Go), the validation library's call |
| Failure carrier | "how invalid input is reported" | (none; use the ecosystem's) | `Either` (Scala, Haskell), `Result` (Rust), `(T, error)` (Go), exceptions (Python, TypeScript) |
| Shape | "an assembly of brands" | `UserSchema` | case class, struct, dataclass, record, `interface` |
| Boundary check | "where untyped data is checked once" | `parseUser` | a library schema's `parse`, a type guard, `TryFrom`, a decoder |

Rules:

1. **Name what it is**, descriptively. Do not import a prefix or suffix scheme (`Plain…`, `to…`, `parse…`, `…Lit`, `…Schema`) because these docs used one.
2. **The project's existing names win**; then the ecosystem's idioms, casing and file-naming (`snake_case` in Python and Rust files, `PascalCase` types in TypeScript, exported-capital rules in Go).
3. **Reuse the ecosystem's own types** for failure and absence (`Either`, `Result`, `Option`, `Maybe`); never define a parallel one.
4. **`PlainX` in these files is shorthand** for "the plain type of raw type X". If the language's own type serves, no plain type is needed; if the project already has a name for it, use that.
5. **One naming scheme per project**, written in the catalog.

## Structure: where the tier folders go

*Folder names are example names: this skill prefers `primitives/`, `brands/` and `shapes/`, but the project's own convention wins, and for brands the ecosystem's own word is fine (`newtypes/`, `opaque/`). Not enforced.*

Source folders that hold no types (app, ui, views, components, hooks, services…) are hidden; only the folders that contain types are described, whatever the rest of the project is called:

```
src/
├── …                                (app, ui, and every other source folder: hidden)
├── shared/
│   └── types/
│       ├── primitives/              tier 1: only ever here
│       ├── brands/                  tier 2 used by two or more features
│       └── shapes/                  tier 3 used by two or more features
└── features/
    ├── search/
    │   ├── …                        (views, components, decorations, hooks, services: hidden)
    │   └── types/
    │       ├── brands/              tier 2 owned by search
    │       └── shapes/              tier 3 owned by search
    └── profile/
        └── types/ …                 same two folders, owned by profile
```

| Tier | Folder | Placement rule |
|------|--------|----------------|
| 1 primitives | `shared/types/primitives/` | only here, never inside a feature (lint: a `primitives/` folder under `features/` is an error) |
| 2 brands | `features/<owner>/types/brands/`, or `shared/types/brands/` | owned by one feature: stays there; needed by two or more: moved to shared once, and everyone imports it. A feature never imports another feature's private brand; promote it first |
| 3 shapes | `features/<owner>/types/shapes/`, or `shared/types/shapes/` | same ownership rule as brands |

Also:

- **No feature folders?** One `types/` folder holds the same three folders.
- **Organized another way** (packages, modules, bounded contexts)? The same two scopes apply: one shared scope and one per owner.
- **Boundary checks** live next to the shape they produce, or beside the service that receives the data; the project's convention decides.
- **Tests** sit next to the files they test. **Database constraints and migrations** live in the project's own migration tool ([database constraints](./database-constraints.md)).
- Imports follow tier order: shapes import brands, brands import primitives, in the same scope or from shared.

## 2. Core principles

| Principle | Why |
|-----------|-----|
| **Golden rule: do not reinvent the wheel** | an existing type (language, standard library, project dependency) fills a role before any custom type is written; add only the missing part, and in Mode B let only tier 1 import it ([reuse-before-create](./reuse-before-create.md)) |
| **Never use a raw type; every type is branded, every brand is defined, every shape is built from brands** | the compiler, not discipline, carries each decision |
| **A refinement is a visible state, not an operation** | `"hello-world"` vs `"HELLO-WORLD"` differ by looking; a trimmed or truncated string looks like any string (the distinguishability test in tier 1) |
| **Compiler first, runtime last** | the target is the compiler saying "this is a string, not the uppercase string expected"; a runtime check exists only for data that originates at runtime, and no function per type is required ([compiler first](./wrong-type-errors.md)) |
| **The same rule in every place a value lives** | visible-state rules are simple predicates: compiler, boundary check and database (`CHECK`, domains) enforce one rule, tested with shared vectors ([database constraints](./database-constraints.md)) |
| **Ordinary functions, not conversion functions** | functions take brands and shapes in their signatures; values come from a verified literal, a more refined value, or one creation point where runtime data enters |
| **Prefer a type the ecosystem already has** | a built-in or library type (`Uppercase<string>`, a refined type, an opaque type) before any wrapper |
| **Make each micro-decision once** | module A lowercasing and module B not lowercasing is a bug that review cannot see |
| **Raw type named in one file per primitive family** | a single lint rule enforces the whole system |
| **Values flow up freely, down only through a creation point** | every narrowing is one checkable function |
| **Creation point is the single source of truth for a brand** | the type and its rule cannot drift |
| **Zero or minimal runtime cost in the core** | brands are type-only; creation points are lightweight; heavy validation libraries stay optional |
| **Document with examples** | every public type shows real usage |
| **Adopt per surface, fully** | partial adoption teaches developers which fields "really" need it |

## 3. Representation strategies

| Approach | Best when | Idioms |
|----------|-----------|--------|
| **Built-in / ecosystem type** | the language or a library already expresses the rule, checked by the compiler | TS `Uppercase<string>` and template literal types, Scala refined types, Python `Literal` |
| **Alias** (`PlainX`) | making "unconstrained" visible, zero cost | TS `type`, Python `TypeAlias`, Go alias |
| **Brand / phantom** | nominal distinction without a runtime wrapper | TS intersection with marker |
| **NewType / opaque / newtype struct** | nominal distinction enforced by the language | Python `NewType`, Rust newtype, Scala opaque, Go struct with unexported field |
| **Refinement chain** | encode generic rules progressively | tier 1 chains |
| **Enum / union** | closed sets | all modern languages |
| **Tagged union** | cases carrying different data | TS discriminated union, Rust `enum`, Python `Literal` + dataclasses |

Trade-off: a form that forces casts on every dynamic consumer is worse than a documented alias plus runtime creation points. Prefer the lightest form that blocks implicit conversion.

## 4. The three checks

| Check | Mechanism | Catches |
|-------|-----------|---------|
| **Static** (first) | compiler + lint | wrong type passed, skipped normalization, raw types, casts, tier-skipping imports |
| **Runtime** (only where data originates at runtime) | creation points, the boundary check, and database constraints where data is stored ([database constraints](./database-constraints.md)) | bad data entering the app, and writes that bypass the code |
| **Tests** | negative compile tests, property tests of creation points | a rule that never fails, drift between a brand's type and its rule |

Lint rules: raw types and library value types imported only in tier 1 primitive-family files; `PlainX` only in tier 1 and in boundary check files; brand casts only at a brand's creation point; imports follow tier order (a shape does not import a primitive).

Property tests per creation point: normalizers are idempotent; outputs satisfy the refinement; rejected inputs stay rejected; round-trip through `toWire` and `parse` returns an equal value.

## 5. Keeping the checks synchronized

Because the creation point is the single source of truth, one table is enough:

| Name | Tier | Built from | Creation point | Policy | Test | Validation library (if any) |
|------|------|-----------|-------------|--------|------|-------------------------|
| `PositiveIntNumber` | 1 | `IntNumber` | a type guard | reject | property: ≥1 integer | `int().positive()` |
| `UserEmail` | 2 | `LowercaseString` | a type guard or the library's parse | normalize, reject | idempotent, malformed rejected | `email().toLowerCase()` |
| `UserSchema` | 3 | brands | the boundary check | composes | boundary tests | object schema |

When a rule changes, update the creation point, its test, and any validation library entry in one commit. A validation library never defines a rule the creation point lacks.

## 6. Creation point policy

| Policy | Returns | Use when |
|--------|---------|----------|
| Normalize | brand, always | any input can be repaired safely |
| Normalize, then reject | brand or failure | repair, then check |
| Reject | brand or failure | input must already be correct |

Decide once per primitive family (tier 1) and per group of sibling brands (tier 2), write it down, keep the policies consistent.

## 7. The micro-decision rule

Whenever you catch yourself making a small choice about a value (case, range, unit, sign, timezone, currency, trimming, truncating), stop and promote it:

```
generic visible state (case, sign, integer, finite, empty) → tier 1 refinement
operation (trim, truncate, decode)                     → a step inside the owning brand's creation point, never a type
domain choice   → tier 2 brand
group of values → tier 3 shape
```

The system only prevents the decisions you encoded. Noticing "I just made a small choice here" is the habit that keeps it working.

## 8. Anti-patterns

| Avoid | Prefer |
|-------|--------|
| Raw `string` / `number` / `boolean` outside tier 1 | the type the code means (a kind or refinement), or `PlainX` only for "any value" |
| `PlainNumber` / `PlainString` where the code needs a kind, a sign or a range | `IntNumber`, `PositiveFloatNumber`, a brand |
| `PlainX` in a shape field | a tier 2 brand |
| `as SomeBrand` outside a creation point | call the creation point |
| Two definitions of one meaning | one brand, imported |
| A brand built from a raw type | build from a tier 1 type |
| Mixed normalize / reject policy in one group of siblings | one policy per primitive family and per group of sibling brands |
| One giant `types.ts` | one file per primitive family (tier 1), per domain (tier 2), per group of shapes (tier 3) |
| Flags instead of cases | tagged union |
| One shape loosened for raw, patch and resolved | three named variants |
| Anonymous `Record<string, unknown>` | a named opaque type |
| A heavy validation library as the only check | creation points at the boundary; library derived from them |
| Adopting for a few fields only | adopt per surface, fully |

## 9. Spectrum of typing rigor

```
Raw types
  → PlainX aliases              visible, auditable, no safety yet
    → tier 1 refinement chains  generic rules enforced
      → tier 2 brands           domain meaning enforced
        → tier 3 shapes         whole structures enforced
```

Pay for as much as the cost of a mistake, the lifespan of the code, and the number of modules sharing the data justify. Skip it for throwaway scripts and prototypes with an expected rewrite; adopt it for long-lived code where several modules touch the same data. The cost is more code to write, manage and remember; the return is the micro-decision bugs that never reach production.
