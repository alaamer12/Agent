---
name: typing
version: 1.0.2
author: Amr
specialized: none
description: 'Type-hinting experience, one skill, two levels: harden (the general craft — brands for raw types, creation points, boundary checks that turn untrusted data into typed values, compiler-first rejection, validation libraries and database constraints, in any language) and tiers (the opt-in three-tier architecture — primitives, brands, shapes — with its conversion path). The router picks ONE level and reads only its method.md. Default to harden; reach for tiers only when the project or user chose it (detect primitives/, brands/, shapes/ folders or the word tiers) — never impose the architecture or a naming scheme. Triggers: improve/tighten/audit types, stringly-typed or primitive-obsessed code, branded/NewType/opaque types, validate config or API contracts, make wrong values an error, type-up, tier-up, tiered types, primitives brands shapes, adopt the tier architecture, promote this to a brand. Golden rule: reuse existing types, never reinvent them. Tier means type-system tiers only, never architecture layers.'
when_to_use: The user asks to improve, tighten or audit a codebase's types (harden), or the project or user chose the three-tier type architecture and code must be built or converted to it (tiers).
argument-hint: "[harden|tiers] <target>"
---

# typing — one skill, two levels of type-hinting

Name a level and the target; with no level named, the dispatch test below decides. Each level is a
complete workflow in its own folder. The only rule that spans them: **load one `method.md`** —
never run both levels' machinery for a one-level job.

## Levels

| Level | The request sounds like | Method |
|---|---|---|
| `harden` | "tighten these types", "make wrong values an error", "add brands / creation points", "validate this config or API contract", "remove stringly-typed code", "type-up" | [`harden/method.md`](./harden/method.md) |
| `tiers` | "adopt the tier architecture", "tiered types", "primitives brands shapes", "convert this module to the tiers", "tier-up" | [`tiers/method.md`](./tiers/method.md) |

## Dispatch — the levels get confused

- **harden is the default.** Any project, any language: brands, creation points, boundary checks,
  compiler-first rejection, reuse-before-create, validation libraries, database constraints. No
  folder convention required.
- **tiers is opt-in.** Reach for it only when the project or user chose the three-tier architecture —
  detect `primitives/`, `brands/`, `shapes/` folders or the word "tiers". Never impose it on a
  project practicing plain brands or ordinary types; that work is harden.
- A harden task in a project that already adopted the tiers still reads harden for general guidance;
  the tier laws and conversion stages answer in tiers.

## Shared laws

- **Golden rule: do not reinvent the wheel.** Use an existing type from the language, its standard
  library, or a dependency already in the project; add only what it lacks. The how:
  [harden/references/reuse-before-create.md](./harden/references/reuse-before-create.md).
- **One vocabulary.** Every term is defined once in
  [harden/references/terminology.md](./harden/references/terminology.md); both levels use it.
  "Tier" means type-system tiers only, never architecture layers.
- **Compiler first.** Move rejection to compile time wherever possible; runtime checks guard the
  boundaries the compiler cannot see.
- **One rule, one place.** Each rule lives in exactly one file; the others link to it.

## Layout

```
typing/
  SKILL.md            # this router
  harden/             # general level
    method.md
    references/       # principles, wrong-type-errors, reuse-before-create, terminology, tooling-adaptation, database-constraints
    examples/         # polyglot-walkthrough, database-walkthrough
    assets/templates/ # brand-template
  tiers/              # opt-in three-tier level
    method.md
    references/       # tiers, migration
    examples/         # tiered-walkthrough
    assets/templates/ # tiered-types-template
```

## Done

Each level owns its done-list: [harden](./harden/method.md#done) and [tiers](./tiers/method.md#done).
The tiers list adds to the harden list; it does not replace it.