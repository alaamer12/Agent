---
name: tier-up
version: 1.0.0
description: 'Installs and runs the three-tier type architecture in a project: the raw type is named in exactly one file per primitive family, every domain meaning becomes a brand with one creation point and a stated policy, and every record is a shape assembled from brands; imports follow tier order and never skip. Opt-in — chosen by the project or the user, never imposed. Includes the conversion path for existing code (raw → tier 1 → tier 2 → tier 3 → boundary) with per-stage steps and a migration done-list. Trigger on "tier-up", "tiered types", "the tier system", "primitives brands shapes", "no raw types outside one file", "adopt the tier architecture", "promote this to a brand", converting a module to full typing rigor. The general craft — brands in any idiom, the compiler-first ladder, validation libraries, database constraints, the master vocabulary — is owned by /type-up; say so and stop rather than reinventing it. "Tier" here means the type-system tiers only, never architecture layers.'
when_to_use: The project or user chose the three-tier type system, or code must be converted to it; also maintaining one tier in a project that already has the folders (primitives/, brands/, shapes/).
argument-hint: "[surface or module] [new | convert]"
---

# tier-up — the three-tier type architecture

**Tier 1 primitives** own the generic visible states and are the only place a raw type is named. **Tier 2 brands** attach domain meaning, each with one creation point. **Tier 3 shapes** assemble brands into records and tagged unions. The laws, structure, policy, catalog mechanics and mistake tables live in [references/tiers.md](references/tiers.md) — the single owner.

Opt-in: this system is a deliberate adoption, not a default. Never impose it on a project that practices plain brands or ordinary types — that work belongs to `/type-up`. Folder names are examples; the project's convention wins. The identifiers in these files (`PlainX`, `toX`, `UserEmail`) are illustrative roles — the project's and ecosystem's names win, as `/type-up` teaches.

## How to use

| Read | When | Tokens |
|------|------|--------|
| [references/tiers.md](references/tiers.md) | always: the ten laws, structure, the distinguishability test, creation policy, per-tier rules with polyglot examples, catalog, mistakes | ≈4.3k |
| [references/migration.md](references/migration.md) | converting existing code — follow its stages raw→1→2→3→boundary; for a single-tier change, read only that stage | ≈3.4k |
| [examples/tiered-walkthrough.md](examples/tiered-walkthrough.md) | one field end-to-end, promoting a raw config, state as a tagged union | ≈1.2k |
| [assets/templates/tiered-types-template.md](assets/templates/tiered-types-template.md) | starting a new surface: skeleton + catalog seed | ≈0.6k |

One task shape: pick the stage (new = tiers.md §tier rules; convert = migration.md stage), act, then the catalog row and checks land in the same change.

## The words this skill assumes

The master vocabulary (and the banned-synonyms list) is owned by `/type-up` (its terminology reference); these ten lines are what a tier task reads daily, so this skill stays usable standalone:

- **tier** — one of the three ordered groups; built only from the tier below. Type-system only, never an architecture layer.
- **raw type** — a type the language provides (`string`, `int`); named in tier 1 and nowhere else.
- **plain type (`PlainX`)** — the deliberate "any value is acceptable" name for a raw type; shorthand here, not a naming scheme to adopt.
- **primitive family** — all tier 1 types derived from one raw type, in one file (string family, number family).
- **refinement** — a tier 1 narrowing to a **visible state** of the value (case, integer-ness, sign, finiteness, emptiness); the distinguishability test in tiers.md §3 gates what qualifies.
- **brand** — a tier 2 type carrying one domain meaning with one creation point.
- **shape** — a tier 3 record or tagged union assembled from brands; "schema" is *not* the word for it (reserved for validation-library/database schemas).
- **creation point** — the only place a runtime value becomes the type; the law allows type guards, library parses, `TryFrom` — whatever the ecosystem's idiom.
- **policy** — normalize / reject / normalize-then-reject, decided once per primitive family and per group of sibling brands.
- **catalog** — the table recording each type: tier, built from, creation point, policy, users; updated in the same commit as the code.

## Done (the tiered system's additions to /type-up's done-list)

No raw type outside the primitive-family files (lint-enforced); no cast outside a creation point; every meaning has exactly one brand and every traveling group one shape; imports follow tier order; policy stated per family/sibling group; the catalog is current.
