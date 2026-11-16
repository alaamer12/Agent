# tiers — the three-tier type architecture

**Tier 1 primitives** own the generic visible states and are the only place a raw type is named. **Tier 2 brands** attach domain meaning, each with one creation point. **Tier 3 shapes** assemble brands into records and tagged unions. The laws, structure, policy, catalog mechanics and mistake tables live in [references/tiers.md](references/tiers.md) — the single owner.

Opt-in: this system is a deliberate adoption, not a default. Never impose it on a project that practices plain brands or ordinary types — that work belongs to the sibling `harden` level (`/typing harden`). Folder names are examples; the project's convention wins. The identifiers in these files (`PlainX`, `toX`, `UserEmail`) are illustrative roles — the project's and ecosystem's names win, as the `harden` level teaches.

## How to use

| Read | When | Tokens |
|------|------|--------|
| [references/tiers.md](references/tiers.md) | always: the ten laws, structure, the distinguishability test, creation policy, per-tier rules with polyglot examples, catalog, mistakes | ≈4.3k |
| [references/migration.md](references/migration.md) | converting existing code — follow its stages raw→1→2→3→boundary; for a single-tier change, read only that stage | ≈3.4k |
| [examples/tiered-walkthrough.md](examples/tiered-walkthrough.md) | one field end-to-end, promoting a raw config, state as a tagged union | ≈1.2k |
| [assets/templates/tiered-types-template.md](assets/templates/tiered-types-template.md) | starting a new surface: skeleton + catalog seed | ≈0.6k |

One task shape: pick the stage (new = tiers.md §tier rules; convert = migration.md stage), act, then the catalog row and checks land in the same change.

## The words this level assumes

The master vocabulary (and the banned-synonyms list) is owned by the `harden` level: [terminology](../harden/references/terminology.md). The daily tier terms — tier, raw type, plain type, primitive family, refinement, brand, shape, creation point, policy, catalog — are defined there once; this level does not restate them.

## Done

Additions to the `harden` level's done-list: no raw type outside the primitive-family files (lint-enforced); no cast outside a creation point; every meaning has exactly one brand and every traveling group one shape; imports follow tier order; policy stated per family/sibling group; the catalog is current.