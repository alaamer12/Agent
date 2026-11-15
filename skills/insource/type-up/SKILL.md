---
name: type-up
version: 2.1.0
description: 'Enhances a codebase''s type system so bugs surface at check time instead of runtime, in any language: brands for raw types, creation points, and boundary checks that turn untrusted data into typed values. Use when the user asks to improve, tighten or audit types, remove stringly-typed or primitive-obsessed code, add branded/NewType/opaque types, validate config or API contracts, make wrong values an error (compile-time and runtime), use the project''s validation library (Zod, Valibot, Pydantic, Hypothesis, serde…), or convert a raw-typed surface. Compiler first: rejection is moved to compile time wherever possible. Golden rule: reuse existing types, never reinvent them. The opt-in three-tier architecture (primitives, brands, shapes) and its conversion path are a separate skill, /tier-up; do not impose naming schemes or that architecture unless the project or user chooses them.'
---

# type-up

Make values carry their meaning and rules in their types, so a small decision (lowercase or not, positive or not) is made once, in one place, and cannot be made differently in two modules.

**Golden rule: do not reinvent the wheel.** If the language, its standard library, or a dependency already in the project provides the type, use it and add only what it lacks. [reuse-before-create](references/reuse-before-create.md) owns the how.

## Scope

**Covers:** brands (alias, NewType, opaque, branded), creation points and boundary checks, shapes and tagged unions, raw / patch / resolved variants, validation libraries and database constraints, the three checks, converting a raw-typed surface.
**Does not cover:** choosing a language or validation library for the user, runtime performance tuning, database schema design, UI or architecture structure. The **three-tier type architecture** — raw types confined to one file per primitive family, every meaning a brand, every shape assembled from brands, plus its staged conversion — is its own skill, `/tier-up`: reach for it only when the project or user chooses it (detect the convention: `primitives/`, `brands/`, `shapes/` folders, or the word "tiers").

## How to use

Read only what the task needs, and stop when you can act. Every rule of this skill lives in exactly one file; the others link to it.

| Read | When | Tokens |
|------|------|--------|
| [references/principles.md](references/principles.md) | always first: the doctrine, the three checks, workflow, naming, sync, anti-patterns, rigor ladder | ≈2.6k |
| [references/wrong-type-errors.md](references/wrong-type-errors.md) | choosing a mechanism: the compiler-first ladder, rejection per language, negative tests | ≈2.4k |
| [references/reuse-before-create.md](references/reuse-before-create.md) | before defining any type: the search order and the gap table | ≈1.7k |
| [references/terminology.md](references/terminology.md) | a term is unclear or you are writing explanations — every term is defined once, here | ≈2.1k |
| [references/tooling-adaptation.md](references/tooling-adaptation.md) | the project already uses a validation or test library (Zod, Valibot, Pydantic, Hypothesis, serde…) | ≈2.5k |
| [references/database-constraints.md](references/database-constraints.md) | persisted data: `CHECK` / domains, shared vectors (+ [worked examples](examples/database-walkthrough.md)) | ≈1.4k |

Working a project that already adopted `/tier-up`? General guidance still applies; the tier laws and conversion stages answer there.

Starting a catalog for a new surface: [assets/templates/brand-template.md](assets/templates/brand-template.md); for the before/after shape across languages: [examples/polyglot-walkthrough.md](examples/polyglot-walkthrough.md).

## Done

No unvalidated outside data flows inward; each rule lives in one place; the three checks cover it; consumers use the types without friction. (Full checklist: [principles.md](references/principles.md#8-workflow--definition-of-done).)
