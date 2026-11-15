---
name: type-up
description: >-
  Enhances a codebase's type system so bugs surface at check time instead of
  runtime, in any language: brands for raw types, creation points, and boundary
  checks that turn untrusted data into typed values. Two modes: general
  enhancement (default), and an opt-in three-tier system (primitives, brands,
  shapes) for projects that adopt it. Use when the user asks to improve,
  tighten or audit types, remove stringly-typed or primitive-obsessed code,
  add branded/NewType/opaque types, validate config or API contracts, make
  wrong values an error (compile-time and runtime), use the project's
  validation library (Zod, Valibot, Pydantic, Hypothesis, serde…), or convert
  a raw-typed surface. Compiler first: rejection is moved to compile time
  wherever possible. Golden rule: reuse existing types, never reinvent them. Do not impose the
  tiers or any naming scheme unless the project or user chooses them.
---

# type-up

Make values carry their meaning and rules in their types, so a small decision (lowercase or not, positive or not) is made once, in one place, and cannot be made differently in two modules.

## Golden rule: do not reinvent the wheel

If the language, its standard library, or a dependency already in the project provides the type (Pydantic's `PositiveInt`, Rust's `NonZeroU32`, TypeScript's `Uppercase<string>`, Zod's `z.number().int().positive()`), use it. The tiers are roles, not code to write: never create a custom `PositiveInt` just to follow them. Check what the existing type guarantees (runtime, compile time, or both) and add only the missing part, usually the nominal marker. In Mode B the existing type enters through tier 1 only: tier 1 re-exports it, and tiers 2 and 3 import it from there. See [reuse-before-create](references/reuse-before-create.md).

## Principles (both modes)

- **Compiler first, runtime last.** The goal is the compiler saying "this is a string, not the uppercase string expected". Look for a type the language or ecosystem already provides, then closed sets, then nominal types, then literal checks; add a runtime check only where data originates at runtime. No function per type is required.
- **Ordinary functions take brands in their signatures.** The compiler rejects a plain value or a swapped argument. A creation point exists only where a runtime value must enter, in the ecosystem's idiom (type guard, library parse, `TryFrom`), never as a mandatory `toX` per type.
- **Names describe roles and follow the ecosystem.** Use the project's names, idioms and types (Scala `Either`, Rust `Result` / `TryFrom`, Go `(T, error)`); example identifiers in these files are illustrative.

## Scope

**Covers:** brands (alias, NewType, opaque, branded), creation points and boundary checks, shapes and tagged unions, raw / patch / resolved variants, validation libraries and database constraints, the three checks (static, runtime, tests), converting a raw-typed surface.
**Does not cover:** choosing a language or validation library for the user, runtime performance tuning, database schema design, UI or architecture structure (keep those vocabularies separate: "tier" here belongs to the type system only).

## Choose the rigor with the user

Options below are illustrative; a hybrid or different answer is always acceptable. Detect the project's existing convention first (folders like `primitives/`, `brands/`, `shapes/`, or the user saying "tiers"); otherwise ask, with the trade-off in one line each.

- `[plain types]`: readable names for raw types, zero cost, no safety
- `[brands with creation points]`: rules enforced, runtime checks at boundaries, tests (**Mode A, default**)
- `[tiered system]`: no raw type outside one file per primitive family, every meaning a brand, every shape assembled from brands; most code, fewest hidden bugs (**Mode B, opt-in**)

## How to use (read only what the mode and task need)

1. Settle the mode, and detect the project's validation and test tooling (use what it already has; add no dependency unprompted). Do not load Mode B files for a Mode A task.
2. Read the files for that mode from the table, in order, stopping when you can act.
3. Work in dependency order, then run the checks and update the catalog in the same change.

### Both modes: terms, tools, errors and storage

| Read | When | Tokens |
|------|------|--------|
| [references/reuse-before-create.md](references/reuse-before-create.md) | before defining any type: search the language, standard library and project dependencies first; add only what is missing | ≈1.7k |
| [references/terminology.md](references/terminology.md) | a term is unclear, or before writing explanations: every term in this skill is defined once here | ≈2.1k |
| [references/tooling-adaptation.md](references/tooling-adaptation.md) | the project has a validation or test library (Zod, Valibot, Pydantic, Hypothesis, serde…): implement with it | ≈2.6k |
| [references/database-constraints.md](references/database-constraints.md) | persisted data: the same rules as `CHECK` / domains, keeping code and database consistent | ≈1.6k |
| [examples/database-walkthrough.md](examples/database-walkthrough.md) | worked SQL, shared test vectors, tagged union table, tightening a live table | ≈1.4k |
| [references/wrong-type-errors.md](references/wrong-type-errors.md) | the compiler-first ladder (built-in types, closed sets, nominal, literal checks), runtime errors only for dynamic data, negative tests | ≈2.4k |

Types prove only what is known at check time: literals and closed sets can fail the build; dynamic values must pass a runtime check. Visible-state rules are simple predicates, so the database can enforce the same rules (`CHECK`, domains), keeping code and storage consistent.

### Mode A: general enhancement (default)

| Read | When | Tokens |
|------|------|--------|
| [references/core-workflow.md](references/core-workflow.md) | always first: principles, workflow, layout, done checklist | ≈0.9k |
| [references/typing-principles.md](references/typing-principles.md) | choosing representations, validation, schema checks, anti-patterns | ≈1.6k |
| [examples/polyglot-walkthrough.md](examples/polyglot-walkthrough.md) | want before / after across languages | ≈1.6k |
| [assets/templates/brand-template.md](assets/templates/brand-template.md) | starting a new type catalog | ≈0.3k |

### Mode B: tiered system (opt-in)

Folders (example names; the project's convention wins): `shared/types/{primitives,brands,shapes}`, plus `features/<owner>/types/{brands,shapes}` for types one feature owns. For brands the ecosystem's word (`newtypes/`, `opaque/`) is fine. See [structure](references/tier-principles.md#structure-where-the-tier-folders-go).

Tiers: **1 primitives** (one file per family, plain types and refinement chains, the only place a raw type is named) → **2 brands** (domain meaning, built from tier 1, one creation point each) → **3 shapes** (records and tagged unions built from brands). Laws: raw type named in one file per family; imports follow tier order and never skip; every brand defined once; casts only at a brand's creation point; one normalize/reject policy per family; `PlainX` only as a chain base, a creation point/boundary input, or a deliberate "any value" choice (never where the code needs a kind, sign or range); promote any micro-decision you catch into a refinement or brand; a refinement is a **visible state** (case, sign, integer, empty), while operations such as trim or truncate are creation point steps, never types.

| Read | When | Tokens |
|------|------|--------|
| [tiers/tier-1-primitives.md](tiers/tier-1-primitives.md) | primitives, refinement chains, removing raw types | ≈3.3k |
| [tiers/tier-2-brands.md](tiers/tier-2-brands.md) | domain meanings, creation points, placement | ≈2.5k |
| [tiers/tier-3-shapes.md](tiers/tier-3-shapes.md) | records, tagged unions, variants | ≈2.1k |
| [references/transform-raw-type-to-tier-1.md](references/transform-raw-type-to-tier-1.md) | converting raw types | ≈1.9k |
| [references/transform-tier-1-to-tier-2.md](references/transform-tier-1-to-tier-2.md) | promoting values to brands | ≈1.4k |
| [references/transform-tier-2-to-tier-3.md](references/transform-tier-2-to-tier-3.md) | grouping brands into shapes | ≈1.5k |
| [references/transform-boundary-and-variants.md](references/transform-boundary-and-variants.md) | parsing outside data, raw / patch / resolved | ≈1.7k |
| [references/tier-principles.md](references/tier-principles.md) | vocabulary, checks, sync table, anti-patterns | ≈3.5k |
| [examples/tiered-walkthrough.md](examples/tiered-walkthrough.md) | complete end-to-end examples | ≈1.2k |
| [assets/templates/tiered-types-template.md](assets/templates/tiered-types-template.md) | starting skeleton and catalog | ≈0.6k |

Pick tier files by the task (a tier 1 change needs only tier 1), add the matching `transform-*` file when converting existing code.

## Done (both modes)

No unvalidated outside data flows inward; each rule lives in one place; checks (static, runtime, tests) cover it; the catalog is current. Mode B adds: no raw type outside tier 1 files and no cast outside creation points.
