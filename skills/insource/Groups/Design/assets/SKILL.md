---
name: assets
version: 2.0.0
specialized: none
description: >-
  Battery-Skill for a project's imagery pipeline: plan the bill of materials, generate the masters,
  conform them into delivery files. Three internal modules - collection dissects a page or reference
  into BOM.md, bom/<page>.md and bom/style.md and writes the prompts; generate produces masters;
  conform (the resource-files module) probes a sheet, splits it and fits each slot to its delivery
  spec with a verification report. The router fixes the order and the shared key: one slot id across
  BOM row, prompt, raw render and delivered file, so nothing is re-derived by hand. Pages marked
  no-images skip the pipeline. Use when asked what images a page needs, to plan or run an image
  program end to end, to turn a sheet into project assets, or to decide which module handles a step.
  Triggers: assets, image pipeline, BOM, image plan, generated sheet, conform, split a sheet.
when_to_use: The user asks what images a page needs, wants a project's imagery planned, generated and delivered end to end, needs a generated sheet turned into project asset files, or asks which module owns a step. Also /assets.
argument-hint: "[the page, image plan, sheet or pipeline step]"
---

# assets - the image pipeline

A Battery-Skill: three steps, three internal modules, one shared key. This root owns the **order and
the handoffs**; each module owns the laws inside its step. Read only the module the current step needs.

```
collection          generate            conform
BOM + prompts  ──►  masters  ──►  probe ──►  conform  ──►  delivery files + report
bom/<page>.md       raw/*.png               assets/<slots>      conform-report.json
```

| Module | Role | Read |
|---|---|---|
| `collection/` | Plan: BOM + prompts | `collection/method.md` |
| `generate/` | Master: render the images | `generate/method.md` |
| `conform/` | Conform + delivery: probe, split, fit, report (the resource-files module) | `conform/method.md` |

## The pipeline

| Step | Module | Artifact | Done when |
|---|---|---|---|
| 1. Plan | `collection/` | `BOM.md`, `bom/<page>.md`, `bom/style.md` | every page listed (or `no-images`), every generated row has slot id, master, delivery and prompt |
| 2. Master | `generate/`, or the file the user already owns (a catalog page, a sprite sheet) | raw masters, `usage.jsonl` | the master exists at the BOM's size and plan |
| 3. Conform | `conform/` (`sheet_probe.py`, `conform.py`, `contact_sheet.py`) | slot-named DPR files, `conform-report.json`, review sheet | `ok: true`, expected file count, no empty cells, edges reviewed on a checkerboard |

Order is the contract. A prompt written before the BOM drifts from the delivery spec; conforming
before the master size is validated produces upscaled files. Steps 2 and 3 are skipped entirely for
pages marked `no-images`. Step 1 decides which of the two step-2 routes each row takes: `generate`
rows get a prompt, `sheet <path>` rows do not.

## Routing

| The user asks | Go to |
|---|---|
| Which images does this page need? What should we generate? | `collection/` (BOM phase) |
| Write the prompts / keep the illustrations consistent | `collection/` |
| Generate the images | `generate/` |
| Cut this generated sheet into project files / normalise sizes and names | `conform/` |
| Cut a reference sheet I already own into project files (catalog page, sprite sheet) | `conform/` - BOM row `sheet <path>`, no prompt |
| Measure a sheet before cutting it | `conform/` (`sheet_probe.py`) |
| Check delivered edges and transparency by eye | `conform/` (`contact_sheet.py`) |
| Convert, optimize, rename, localize, inventory files | `conform/` |
| Real photos, avatars from a library | `fahlwy` (external skill) |
| Which pages exist at all | `pages` (external skill) - the BOM consumes the `pages` tree (`<docs>/pages/`) |

## The slot id

One id, four places: the BOM row, the prompt block, the raw render's cell, the delivered filename.
`avatar-01` is the same string everywhere; ranges (`avatar-01..10`) expand in row-major cell order.
The id is a name, not a type: `welcome`, `empty-state`, `store-category-3` work identically, and a
sheet of unrelated subjects is cut in the order its ids are listed. This is what removes the manual
linking step - if two of the four disagree, the pipeline broke.

## Artifact paths

| Path | Module | Purpose |
|---|---|---|
| `bom/BOM.md` | `collection/` | index: page, image count, generated count, `no-images` |
| `bom/<page>.md` | `collection/` | slot table + prompts for generated slots |
| `bom/style.md` | `collection/` | Style DNA, character canon, hard/soft rules - the only canon |
| `raw/` | `generate/` | untouched masters; never edited by hand |
| delivery folder | project | slot-named files written by conform; the code reads these |
| `conform-report.json` | `conform/` | what was written, skipped, warned, failed |
| review sheet | `conform/` | checkerboard of the delivered files, with measured alpha edges |

## What the router does not own

- **Naming, formats, optimization, icon/splash specs** - the `conform/` module. Do not restate them here.
- **Style DNA, character canon, prompt anatomy, economy math** - the `collection/` module. One canon, one owner.
- **Generation execution, providers, cost ledger** - the `generate/` module.
- **Page inventory** - `pages` (external).

If this file starts growing tables of sizes or naming rules, it has begun duplicating a module and
should be cut back to routing.

## When the pipeline breaks

| Symptom | Where it broke | Next step |
|---|---|---|
| Prompt asks for detail a cell cannot hold | plan: master not checked against delivery | re-run the BOM economy row, adjust master or DPR |
| Delivery files soft or aliased | conform ran on too small a cell | raise the master or lower the DPR; never ship `--allow-upscale` |
| Filenames do not match the code | slot id renamed in one place only | fix the BOM row, regenerate the names; the BOM is the source |
| A page has no images and nobody noticed | page missing from `BOM.md` | list it and mark `no-images` explicitly |
| A generated sheet has 9 subjects for 10 slots | step 2 / seed drift | re-render; conform already refuses to guess |
| 32 files for 34 slots, or cut crowns | plan: rows hold 8,8,8,10 but the BOM says `CxR` | probe it and plan `sheet rows 8,8,8,10`; conform cuts on the measured gutters |