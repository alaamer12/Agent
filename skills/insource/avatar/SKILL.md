---
name: avatar
description: 'Creates avatars in an approach-unbiased way: an avatar is a stand-in for an entity where it is absent (recognition / consistency / composition / production), so the skill first reads the request on four axes - medium, source of truth (reference image, name string, seed, brief, photo), determinism, and parts-ness (one fixed picture vs a swappable system) - then picks a way to build it from a living catalog (data.csv) instead of defaulting to one style. Full lifecycle: brief, approach choice, build, parts contract (boundary, anchor, independence, style, overlap, combination-tested - any medium), a universal debugging taxonomy, delivery, and mandatory catalog write-back so every discovered way to create avatars is recorded and every built resource is registered per-approach (wagba-avatars.csv style). One verified approach exists today - the modular explodable SVG rig in approaches/modular-svg-rig/ (10 slots, 25 parts, render-and-compare, combination verifier) - as one row among many, not the identity of the skill. Use whenever the user wants a profile picture, character portrait, avatar family, swappable/mix-and-match parts, monogram/identicon/dicebear-style defaults, an avatar from a reference image, or asks how unique or how to build any of it.'
when_to_use: The user asks for an avatar, profile picture, character or portrait to be created, varied, modularized, debugged or systematized - including "make me an avatar", "recreate this character", "give me 4 haircuts that swap", "default avatars for our users", "why does my part swap break the face".
argument-hint: "[who/what it represents] + [source: reference image / name / brief] + [fixed vs swappable, sizes, count]"
---

# /avatar - the open world of making a stand-in for someone

Creating avatars is not one technique. It is a design space with infinite possibilities - vector rigs,
monograms, hash identicons, parameterized generators, emoji composites, photo derivatives, generated
rasters, one hand-drawn picture - and the skilled move is **choosing the way that fits the request**, not
reaching for the way you know. This skill keeps every way it has ever proven or built in a queryable
catalog, runs the same lifecycle regardless of approach, and requires every run to leave the catalog
bigger than it found it.

**The four axes that pick an approach** (full treatment in [`00`](references/00-lifecycle-and-parts.md)):
medium (vector ↔ raster ↔ live-typographic), source of truth (image ↔ string ↔ seed ↔ brief ↔ photo), determinism
(fixed↔procedural), parts-ness (single↔swappable-system). "An avatar" answers none of them - ask or assume
explicitly. "The same guy with 4 haircuts" answers all four, and that is a rig job.

## Lifecycle (every approach, same spine)

```
- [ ] 1 Brief    who/what, where it appears (sizes/frames), one vs family, source material
- [ ] 2 Choose   query data.csv (catalog.py list/search); read the approach card;
                 no fitting verified row -> prove an unverified one or invent, then ADD
- [ ] 3 Build    per the approach card; first complete artifact early, iterate on artifacts
- [ ] 4 Parts    only if swappable: the parts contract - boundary, anchor, independence,
                 style, overlap-not-abutting, combination-tested (any medium)
- [ ] 5 Verify   render? matches source? swap isolates? edge inputs? universal failure
                 taxonomy in references/00; make the verifier catch every bug class found
- [ ] 6 Deliver  artifact set + honest report + WRITE BACK: catalog.py add/stamp, and every
                 built resource into the approach's own CSV
```

## The catalog - the skill's memory

- **`data.csv`** - the global, unbiased registry of ways to create avatars. One row per approach:
  mechanism, inputs/outputs, parts model, tooling, `status` (verified / unverified / degraded / dead),
  `last_proven`, and a pointer to its resource registry. Never delete a row; flip its status - the
  graveyard is knowledge.
- **`approaches/<id>/`** - encapsulated per-approach folders: method card (README), method references,
  scripts, assets, examples, and a **resource CSV** registering what was actually built (for the rig:
  `wagba-avatars.csv` - 10 slots, 25 parts, the default combo, 4 known-bad fixtures, each with file path
  and verification date).
- **`log.csv`** - append-only ledger; every add/stamp/set auto-logs, method lessons go in as `NOTE`.
- **`scripts/catalog.py`** - the interface: `list / get / search / stats / stale / stamp / set / add /
  resources / log / export`; no arguments runs its self-test. Query it; do not skim the CSVs.

Governance rules and the two-layer design: [`01`](references/01-catalog-discipline.md).

## The built approach today

**`modular-svg-rig`** (status: verified, proven 2026-10-30) - the explodable SVG character rig: match a
reference by render-and-compare, split into slots with envelopes/anchors/palette variables, author swappable
parts, verify sampled combinations, deliver rig + sheets + picker. Its whole method lives, untouched and
isolated, in [`approaches/modular-svg-rig/README.md`](approaches/modular-svg-rig/README.md). It is **one
row in the catalog** - pick it when the axes say rig, not because it is what this skill knows.

## Non-negotiables

- **No default style.** The axes decide; the catalog supplies candidates; inventing a new way is a
  first-class outcome - and gets recorded the same session.
- **Every run writes back.** New way → `add`; re-proven → `stamp`; built resources → the approach CSV;
  lesson → `log NOTE`. A run that leaves the catalog unchanged taught the skill nothing.
- **`verified` means proven *in this environment by a real artifact*** - seeded rows stay `unverified`
  until a build proves them; say so when you use one.
- **Swaps must isolate.** A parts system where changing one unit moves another is broken regardless of
  what the sheet looks like; fix the unit, not the threshold.
- **Test at the smallest real size** and on the edge inputs (long names, non-latin, empty sets) before
  calling any avatar done.
- **Dependencies live in a project-local `.venv`** - never the global interpreter.

## Resources

| File | Owns | Read when |
|---|---|---|
| [`references/00-lifecycle-and-parts.md`](references/00-lifecycle-and-parts.md) | The avatar essence, the four axes, the lifecycle in depth, the medium-neutral parts contract, the debugging taxonomy | Every run, before choosing |
| [`references/01-catalog-discipline.md`](references/01-catalog-discipline.md) | The two-layer catalog, status rules, write-back duties, query commands | Before the first write-back, and when extending |
| [`data.csv`](data.csv) | The global catalog of ways | Step 2 |
| [`log.csv`](log.csv) | The growth ledger | Reading history; appending via catalog.py |
| [`scripts/catalog.py`](scripts/catalog.py) | The catalog interface | Step 2 and step 6 |
| [`approaches/modular-svg-rig/README.md`](approaches/modular-svg-rig/README.md) | The verified rig method end to end | When the axes pick a rig |
| [`approaches/modular-svg-rig/wagba-avatars.csv`](approaches/modular-svg-rig/wagba-avatars.csv) | Everything the rig approach has built, with paths and dates | Before building any rig resource |
