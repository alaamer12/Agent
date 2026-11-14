# Generated imagery — the BOM → generate → conform pipeline

Status: implemented as three skills — `assets` (router), `collection` (BOM + prompts),
`resources` (probe + conform) — and two scripts, `sheet_probe.py` and `conform.py`.
Scope: a project's *generated* imagery. Stock photography (`fahlwy`), vector icons and
font/brand work (`resources`) keep their own flows.

## 1. Goals

A model asked for "ten diverse avatars" returns one image holding ten faces. The
project needs ten files: same size, same aspect, correctly named, cropped where the
subject actually is, encoded for the DPRs it renders at. The gap between "one render"
and "shippable assets" is where hand-work, drift and silent quality loss live.

The pipeline exists to close that gap with four properties:

- **The plan is written before anything is generated.** A prompt is downstream of the
  slot's master size, its sheet grid and its delivery spec; writing the prompt first
  produces art the project cannot ship.
- **One key, four places.** A slot id names the BOM row, the prompt, the render's cell
  and the delivered file. Nothing is re-derived by hand, so nothing can disagree.
- **The image work is scripted.** The model writes specifications and prose; Python
  measures and cuts. Geometry is never guessed in a prompt or a chat message.
- **Failures are loud.** Fewer subjects than slots, a cell too small for its DPR, a
  subject spanning a cut line — each stops the run or is reported, never papered over.

## 2. Three skills, one pipeline

```
collection          generate (external)          resources
BOM + prompts  ──►  masters            ──►       probe ──► conform ──► review
bom/<page>.md       raw/*.png                      assets/<slots>      review/*.png
```

| Step | Owner | Artifact | Done when |
|---|---|---|---|
| 1. Plan | `collection` | `BOM.md`, `bom/<page>.md`, `bom/style.md` | every page listed or marked `no-images`; every generated row has slot id, master, delivery, prompt |
| 2. Generate | `generate` | raw masters, `usage.jsonl` | the master exists at the BOM's size and grid |
| 3. Conform | `resources` (`sheet_probe.py`, `conform.py`) | slot-named DPR files, `conform-report.json` | `ok: true`, expected file count, no empty cells |

`assets` is the router: it states this order, the shared key and the handoffs, and
owns none of the laws inside a step. Pages marked `no-images` skip steps 2 and 3.

**Why step 1 is not its own skill.** A BOM split into a separate skill creates a lossy
handoff — the BOM owner knows the slot's size and grid, the prompt owner knows the style
canon, and neither can see the other's constraints. One skill owns both, in fixed order.

## 3. Scope: page versus set

| Scope | Question | Artifact | Band |
|---|---|---|---|
| Page | What images does this page need, and how is each produced? | `bom/<page>.md` | per page |
| Set | How do these frames look like one family? | `bom/style.md` + prompt blocks | per product |

A BOM is page-scoped and imagery-only. It answers "what does this page ship and how is
each piece made" — not fonts, video or documents. Style, character canon and hard rules
are set-scoped and written **once** in `bom/style.md`; every page BOM links to it. Two
canons is how a collection drifts.

## 4. Artifacts

| Path | Owner | Purpose |
|---|---|---|
| `BOM.md` | `collection` | index: page, image count, generated count, `no-images` marker |
| `bom/<page>.md` | `collection` | that page's slot table + prompts for its generated slots |
| `bom/style.md` | `collection` | Style DNA, character canon, hard and soft rules — the only canon |
| `bom/shared.md` | `collection` | assets referenced by more than one page, specified once |
| `raw/` | `generate` | untouched masters; never edited by hand |
| delivery folder | project | slot-named files written by conform; the code reads these |
| `conform-report.json` | `resources` | what was written, skipped, warned, failed |

A page that needs no imagery is listed as `no-images`, not omitted. An empty row is
evidence; an absent row is an oversight.

## 5. The slot table

The schema has one owner; `conform.py` reads it and changes nothing about it.

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| `avatar-01..10` | testimonial personas | generate sheet 5x2 | `1536x1024 sheet 5x2 gutter 0` | `128x128 1:1 webp q82 @1x,2x` | pending |
| `hero-home` | hero illustration | generate single | `1600x900 single` | `800x450 16:9 avif q60 @1x,2x` | pending |
| `logo` | brand mark | reuse `brand/logo.svg` | — | `240x64 svg` | shipped |
| `photo-teaser` | card photo | `fahlwy` | — | `640x360 16:9 jpeg q80 @2x` | pending |
| `icon-search` | nav icon | `resources` icon set | — | `24x24 svg` | shipped |

- **Slot** — one id or a range. The id becomes the filename stem; a range expands
  row-major across the sheet's cells.
- **Source** — `generate single`, `generate sheet CxR`, `reuse <path>`, `fahlwy`,
  `resources`. Only the two generated routes get a master spec and a prompt. Everything
  else is still listed, so a later agent cannot mistake an icon slot for a render.
- **Master** — `WxH single` or `WxH sheet CxR [gutter N]`. The raw render, large enough for
  `delivery px × max DPR`. Conform parses this cell, so fallback notes live in the economy check.
- **Delivery** — `WxH [aspect] [format] [qN] [@DPRs]`. What conform implements.
- **Status** — `pending / shipped / reused / no-image`. Closes the "is anything
  missing" question without a conversation.

## 6. The economy test

Sheets are cheaper only while the cells are big enough:

```
required_master = ceil(delivery_px × max_DPR)              # per axis
cell            = (sheet_px - (cols - 1) × gutter) / cols
sheet valid     = cell >= required_master  and  count <= cols × rows
requests        = ceil(N / cells_per_sheet)                 # versus N singles
```

Ten avatars, one 1536×1024 sheet (5×2, no gutter):

| Delivery | Required master | Cells | Valid? | Requests |
|---|---|---|---|---|
| `128px @1x,2x` | 256px | 283×328 | yes | 1 |
| `128px @1x,2x,3x` | 384px | 283×328 | **no** | 3 sheets of 2×2, or 10 singles |
| `64px @1x,2x,3x` | 192px | 283×328 | yes | 1 |

The same sheet is economical at 2x and impossible at 3x. That arithmetic — not a
feeling about image count — is what the BOM records, together with a fallback plan so a
failed render has an answer ready.

**Two qualities, never one word.** *Master quality* is the render: model tier,
resolution, prompt. *Delivery quality* is the encode: format and `qN` per DPR step.
Economy lives in request count and master size and must not be paid for with either.
Costs are never estimated in the BOM; `generate` writes `usage.jsonl`, and that is the
only source.

**Correlated risk.** A sheet is one request and one failure domain: a single malformed
cell invalidates the render, while individual generations cost N requests and drift in
style. The BOM records which way the plan leans.

## 7. Measure before cutting

```bash
python scripts/sheet_probe.py raw/avatars.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"
```

```text
size      1536x1024 RGBA alpha=yes background=(2, 2, 3)
content   [62, 167, 1475, 822]  margins left=62 top=167 right=61 bottom=202
columns   5 band(s) gaps [12, 12, 12, 12]
rows      2 band(s) gaps [100]
grid      5x2 cells about 283x328
subjects  10 found, min 269x272, max 271x276
ceiling   269px square master
delivers  64@1x,2x,3x,4x  96@1x,2x  128@1x,2x  192@1x  256@1x
note      left/right margins differ (62 vs 61): cutting the canvas would shift the grid
```

Each line answers a decision:

| Reading | Decision |
|---|---|
| band count per axis | does the image really hold the planned grid? Fewer bands than cells means two subjects touch |
| gaps regular/uneven | is an even split safe, or must cuts follow the measured band starts? |
| subject min size | the largest square master the sheet can supply **without upscaling** — the honest limit for the delivery spec |
| content box and margins | whether a canvas cut would shift the grid |
| empty cells | whether the render is short of subjects before any file is written |

`--json` returns the same report as data: `content_box`, `columns.starts/ends/gaps`,
per-cell `subject` boxes, `empty_cells`, `master_ceiling`, `delivery_ceiling.fits`.

## 8. The cut-line law: content, not canvas

`conform.py` divides the **content box** by default. On the sheet above, the canvas is
1536 wide, so five equal columns end at 307, 614, 922, 1229 — and the first avatar runs
from x=62 to x=332, so column one's right edge at **307 lands inside a subject**.
Dividing the content box (62–1475) instead places every cut in a gutter: 345, 628, 910,
1193.

| Mode | Result |
|---|---|
| content box (default) | margins absorbed; every cut line in a gutter |
| `--full-canvas` | classic equal-cell split; correct only when margins are absent or symmetric |
| `--cell N` | fixed pitch from the region origin; for sheets with an exactly known cell size |

Remainder pixels are distributed, never dropped: a 100px region split three ways gives
33, 34, 33. A one-pixel difference between cells is irrelevant because every cell is
trimmed and refit afterwards.

Cells need not be square. A cell is a *slice region*; the asset's aspect comes from
trimming the subject and padding it to the delivery aspect.

A set that needs more than one render is written as one BOM row per sheet
(`avatar-01..04`, `avatar-05..08`); each row is its own run. One BOM row never spans two
images.

## 9. Cutting, trimming, keying, fitting

| Stage | Behaviour |
|---|---|
| crop | one cell per slot, row-major, from the shared sheet plan |
| keying (`--key-bg auto`, default) | border-seeded flood fill makes the sheet's **edge-connected** background transparent before cropping, so interior whites survive and a subject filling its cell is never keyed from its own corner; skipped when the sheet already has alpha, when the border is not flat, or when the sheet is one flat colour |
| trim (`--trim`, default) | crop to the subject's bounding box — measured on alpha when present, otherwise against the *sheet's* background colour, never the cell corner (a subject touching the cell edge would otherwise be measured as the gap) |
| fit | scale to fit the target box preserving aspect (LANCZOS), centre, pad — transparency for alpha formats, `--pad-color` for JPEG. Never stretch |
| ladder | largest step from the master, the rest downscaled from it; never re-derived from a smaller file |
| verify | every file re-opened: exists, exact size, aspect within 1% |
| review | `contact_sheet.py` composites the files on a checkerboard and measures alpha edges — transparency is invisible against white |

**Keying is not background removal.** A gradient or photographic backdrop needs
segmentation; conform says so instead of emitting a ragged mask.

**No silent upscaling.** A subject smaller than `delivery_px × max_DPR` is an error
naming both numbers. `--allow-upscale` exists for deliberate cases and should be rare.

## 10. Naming and the DPR ladder

`128x128 1:1 webp q82 @1x,2x` writes, per slot:

| File | Size |
|---|---|
| `avatar-01.webp` | 128×128 |
| `avatar-01@2x.webp` | 256×256 |

`--naming` accepts `{slot} {w} {h} {dpr} {ext}`. The `@Dx` suffix is added only when a
pattern names neither `{dpr}` nor `{w}`, so there are no double suffixes. Encoding
vocabulary is the delivery spec's own (`webp q82`) — the same one `optimize.py`
accepts. Conform does not own a second quality scale.

## 11. Report and exit codes

`conform-report.json` records the run: `master`, `region`, `key {applied, reason}`,
`expected`, `empty_cells`, `files[]`, `skipped[]`, `warnings[]`, `errors[]`, `ok`.

| Exit | Meaning |
|---|---|
| 0 | ok |
| 2 | bad spec, unreadable image, or impossible geometry |
| 3 | count/empty mismatch — the sheet does not match the BOM |
| 4 | verification failure, or a subject too small for its spec |

A count mismatch stops the run on purpose. A 9-subject sheet cannot fill a 10-slot BOM,
and guessing which slot is missing corrupts names downstream. `--allow-empty` writes the
rest and leaves the hole visible in the report.

## 12. Why scripts, not model prose

The model writes what is a judgement call: what each page needs, how a slot is
classified, the style canon, the prompt. Python decides what is measurable: content
bounds, band counts, cell geometry, trim boxes, encoders, file sizes.

That split is what makes the pipeline repeatable. "Cut it into ten equal pieces" is
three words and at least two wrong answers — canvas versus content, and whether the
remainder is dropped. A specification that leaves geometry to prose is a specification
that produces different files on every run.

## 13. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Last column cut in half | canvas divided instead of content | default mode; drop `--full-canvas` |
| One slot holds two half-faces | subjects touch; even grid splits them | regenerate with more spacing, or cut on measured band starts |
| `N of M cells are empty` | render has fewer subjects than the BOM | re-render, fix the BOM, or `--allow-empty` and fill the hole |
| `subject reaches the cell edge` | subject spans a cut line between cells | re-render; if the design truly bleeds, `--full-canvas --cell` |
| `cell … smaller than the required master` | sheet cannot supply that DPR | lower the DPR, raise the sheet, or split into more sheets |
| White corners on a round avatar | keying skipped | needs a flat border; check `key.reason` |
| Soft or aliased edges | upscaled | raise the master or lower the DPR; do not ship `--allow-upscale` |
| Prompt wants detail a cell cannot hold | master not checked against delivery | re-run the economy row before writing prompts |
| Filenames do not match the code | slot id renamed in one place | fix the BOM row; the BOM is the source |

## 14. Limits

- A subject **partially outside the canvas** cannot be recovered; the probe's band count
  is the early signal.
- **Overlapping subjects** cannot be separated by geometry — that is segmentation.
- **Non-flat backgrounds** are not keyed out.
- **Hand-made, irregular collages** need explicit cuts; a grid is a grid.
- Conform never decides what a page *needs*. That is the BOM's job.
- The probe measures an existing sheet; it does not predict whether a model will honour a
  requested grid.

## 15. Verification

- `resources/scripts/test_conform.py` (46 tests), `test_sheet_probe.py` (8) and
  `test_contact_sheet.py` (8) cover grammar parsing, remainder distribution, content-box cuts,
  keying (including interior whites), empty cells, upscale refusal, naming, edge measurement and
  the report shape.
- The end-to-end case is a real 1536×1024 RGBA avatar sheet: ten slots, twenty files
  (128 and 256 WebP, RGBA), `ok: true`, zero warnings, ≈191 KB total, region
  `[62, 167, 1475, 822]`, and a reviewed contact sheet with transparent corners and no halo.
- The same sheet's canvas division would have cut avatar one at x=307 while its subject
  runs to x=332 — the regression is asserted in the tests, not just observed once.
