# Conforming a generated sheet

One render, many assets. A model asked for "ten diverse avatars" returns a single image holding a
grid of ten faces; the project needs ten files, each the same size, each correctly named, each
cropped where the subject actually is. **Conform** is that step.

```
BOM row  ──►  generate      ──►  probe + conform        ──►  delivery files + report
(collection)  (external)         (this skill)               (named by slot id)
```

The slot id is the key in all four places: the BOM row, the generation prompt, the raw render and
the delivered file. Nothing is re-derived by hand.

Three scripts:

| Script | Answers |
|---|---|
| `sheet_probe.py` | What is on this sheet - content bounds, bands, gaps, cell sizes, how large a master the subjects can supply? |
| `conform.py` | Cut it, fit it, name it, verify it against the BOM. |
| `contact_sheet.py` | Do the delivered files look right - clean alpha edges, no halos, no leftover background? |

---

## 1. Measure before cutting

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

Read it as four decisions:

1. **Do the bands match the plan?** 5 columns and 2 rows for a 5x2 grid means every subject is
   separated by background. A band count lower than the grid means two subjects touch - an even
   cut would slice one of them, so cut on the measured bands or regenerate.
2. **Is the grid regular?** Even gaps mean an even split is safe. `(uneven)` means the generator
   spaced subjects unevenly; use the measured band starts to place cuts.
3. **How large is a subject?** `ceiling` is the smallest subject side, so it is the largest square
   master the sheet can supply **without upscaling**. Here 269px: `128x128@2x` (needs 256) fits,
   `128x128@3x` (needs 384) does not.
4. **Where is the content?** Margins of 62/61/167/202 mean the subject grid does not fill the
   canvas. That single fact decides the cut mode below.

`--json` gives the same report as data: `content_box`, `columns.starts/ends/gaps`, per-cell
`subject` boxes, `empty_cells`, `master_ceiling`, `delivery_ceiling.fits`.

---

## 2. The cut-line law: content, not canvas

`conform.py` divides the **content box**, not the canvas, by default.

Why it matters, on the sheet above: the canvas is 1536 wide, so five equal columns end at
307, 614, 922, 1229. The first avatar runs from x=62 to x=332 - column one's right edge at 307
lands **inside it**. Dividing the content box (62-1475) instead puts every cut line in a gutter:
345, 628, 910, 1193.

| Mode | Result |
|---|---|
| content box (default) | margins absorbed, every cut line in a gutter |
| `--full-canvas` | classic equal-cell split; correct only when the sheet has no margins or they are symmetric and even |
| `--cell N` | fixed pitch from the region origin; for sheets whose cell size is known exactly |

Remainder pixels are distributed, never dropped: a 100px-wide region split into 3 gives 33, 34,
33. A one-pixel difference between cells is irrelevant because every cell is trimmed and refit.

A set that needs more than one render is written as one BOM row per sheet (`avatar-01..04`,
`avatar-05..08`); each row is its own run. One BOM row never spans two images.

**Clipping check.** When a subject reaches a cut line *between* two cells, the run adds a warning:
the neighbouring cell may hold the rest of that subject. Touching the sheet's outer boundary is
not warned about - in content-box mode the outermost cells start at the subject's own edge by
construction.

---

## 3. Cutting

```bash
python scripts/conform.py --bom bom/home.md --group avatar --in raw/avatars.png --out assets/avatars
python scripts/conform.py --bom bom/home.md --slots avatar-01..10 --in raw.png --out out/ --dry-run
python scripts/conform.py --in sheet.png --out out/ --grid 4x4 --gutter 24 --cell 512 \
    --slots a,b,c --delivery "128x128 1:1 webp q82 @1x,2x"
```

- **`--group avatar`** selects every BOM slot whose id is `avatar` or starts with `avatar-`.
- **`--slots avatar-01..10`** selects explicitly; ranges keep zero padding (`avatar-01`, not
  `avatar-1`). Both forms accept comma lists.
- **One run = one sheet group.** All selected slots must share the sheet plan; a BOM with two
  different sheet sizes is two runs.
- Row-major order: cell 1 is top-left, cell N is bottom-right.
- `--dry-run` prints the plan without opening the image or writing anything - safe in CI and
  before spending a re-render.

Rows the BOM marks `shipped`, `reused`, `no-image`, `done` or `skip` are skipped, as are rows with
no master spec (stock photos, CSS icons, SVG logos). `--force` re-does shipped slots.

---

## 4. Trimming, empty cells and the count check

After cropping a cell, the subject's bounding box is measured against:

- the **alpha channel**, when the sheet has real transparency;
- the **sheet's background colour**, otherwise. Using the sheet colour rather than the cell's
  corner matters when a subject touches a cell edge - the corner would then be the subject and the
  "subject" would come out as the gap.

`--trim` (on by default) crops to that box; `--no-trim` keeps the full cell. `--trim-threshold`
(default 8) is how much a pixel must differ from the background to count.

A cell whose remaining area is uniform is **empty**. If any cell is empty the run reports which
slots they are and exits **3** - a 9-subject sheet cannot fill a 10-slot BOM, and guessing which
slot is missing corrupts names downstream. `--allow-empty` writes the non-empty cells and leaves a
report you can act on. A `1x1` sheet is the exception: its cell *is* the subject, so uniformity
there means "nothing to trim", not "empty".

---

## 5. Background keying (`--key-bg`)

Generated sheets often return an opaque white background. `--key-bg auto` (default) makes the
background transparent before cropping, using a **border-seeded flood fill**:

- Seeded from the sheet's edge, so only background *connected to the edge* is removed. A white
  highlight inside an eye, a white shirt, a pale cheek stay opaque. This is why it is a flood fill
  and not "remove every white pixel".
- Requires a flat border ring (`_uniform_border`). A sheet whose subject bleeds to the edge is left
  alone with a reason in the report - keying it would eat the subject.
- A sheet that is 99.5% one colour is left alone: there is nothing to separate.
- Sheets that already have transparency skip keying entirely.

Disable with `--no-key-bg`; seed an explicit colour with `--key-bg '#FFFFFF'`. The report records
what happened under `key: {applied, reason}`.

Keying is not background *removal* for complex scenes: a gradient or photo backdrop needs a
segmentation tool. Conform says so instead of producing a ragged mask.

---

## 6. Fitting: contain, then pad - never squash

1. Scale to fit the target box preserving aspect (`min(tw/sw, th/sh)`, LANCZOS).
2. Centre it on a canvas of exactly the delivery size.
3. Pad with transparency for `png`/`webp`/`avif`; with `--pad-color` (default white) for `jpeg`.

The alternative - stretching to the box - changes faces. A wide illustration delivered as a square
avatar gets padding, not a fatter subject. `--pad-color #RRGGBB` also flattens alpha for JPEG.

**No silent upscaling.** If the subject is smaller than the required master
(`delivery_px × max_DPR`), the slot is an error (exit **4**) naming both numbers. `--allow-upscale`
exists for deliberate cases and should be rare: an upscaled avatar is soft at every DPR.

---

## 7. DPR ladder and naming

Delivery `128x128 1:1 webp q82 @1x,2x,3x` writes, per slot:

| File | Size |
|---|---|
| `avatar-01.webp` | 128x128 |
| `avatar-01@2x.webp` | 256x256 |
| `avatar-01@3x.webp` | 384x384 |

The largest step is produced first (from the master), the rest are downscales - never re-derived
from a smaller file.

`--naming` overrides the pattern with `{slot} {w} {h} {dpr} {ext}`:

```bash
--naming "{slot}-{w}{ext}"     # avatar-01-128.webp, avatar-01-256.webp
--naming "{slot}-{dpr}{ext}"   # avatar-01-1x.webp, avatar-01-2x.webp
```

The `@Dx` suffix is added automatically for dpr > 1 only when the pattern names neither `{dpr}` nor
`{w}` - no double suffixes.

Encoding uses the delivery spec's own vocabulary (`webp q82`), which is the same vocabulary
`optimize.py` accepts. Conform does not invent a second quality scale; it applies the one the BOM
declared. Generic one-file conversions stay in `transform.py` and `optimize.py`.

---

## 8. Verification and the report

After writing, every file is re-opened and checked: exists, exact size, aspect within 1%. Failures
exit **4**. `--no-verify` skips the check but not the report.

Geometry cannot see a white halo. Composite the delivered files on a checkerboard:

```bash
python scripts/contact_sheet.py assets/avatars --out review/avatars.png --skip-density
```

That writes one PNG with every slot at a known size and measures each file: transparent share,
corner alpha, opaque-border share. A border that is mostly opaque is reported - either keying was
skipped or the subject genuinely fills the frame, and the picture tells you which. `--json` prints
the same facts as data; the script never edits the assets.

`conform-report.json` (default `<out>/conform-report.json`):

```json
{
  "bom": "bom/home.md",
  "sheet": "raw/avatars.png",
  "group": "avatar",
  "master": {"size": [1536, 1024], "kind": "sheet", "grid": [5, 2], "gutter": 0,
             "cell": [307, 512], "boxes": [[62, 167, 345, 495]]},
  "region": [62, 167, 1475, 822],
  "key": {"applied": false, "reason": "sheet already has transparency"},
  "expected": 10,
  "empty_cells": [],
  "files": [{"slot": "avatar-01", "dpr": 1.0, "width": 128, "height": 128,
             "format": "webp", "path": "assets/avatars/avatar-01.webp", "bytes": 5606}],
  "skipped": [{"slot": "logo", "why": "no master/delivery spec (not generated)"}],
  "warnings": [],
  "errors": [],
  "ok": true
}
```

`--json` prints it instead of the table. Exit codes: **0** ok, **2** bad spec or image, **3**
count/empty mismatch, **4** verification failure.

---

## 9. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Last column is cut in half | canvas divided instead of content | default mode already fixes it; drop `--full-canvas` |
| One slot contains two half-faces | subjects touch; even grid splits them | regenerate with more spacing, or cut on the probe's measured band starts |
| `N of M cells are empty` | the render has fewer subjects than the BOM | re-render, fix the BOM, or `--allow-empty` and fill the hole separately |
| `subject reaches the cell edge` warning | subject spans a cut line | re-render; if the design truly bleeds, cut with explicit `--full-canvas --cell` |
| `cell ... smaller than the required master` | the sheet cannot supply that DPR | lower the DPR, raise the sheet size, or split into more sheets |
| White corners around a round avatar | keying skipped | `--key-bg auto` (default) needs a flat border; check `key.reason`, then review with `contact_sheet.py` |
| Soft/aliased edges | upscaled | raise the master or lower the DPR; do not ship `--allow-upscale` output |
| `pillow is required` | dependency missing | install in the project's environment, never globally |
| Non-square cells | expected | cells are slice regions, not asset aspects; every subject is trimmed and refit |

## 10. Limits

- A subject that is **partially outside** the canvas cannot be recovered; the probe's `columns`
  band count is the early signal.
- **Uneven, hand-made collages** need explicit `--grid`/`--cell` cuts; a grid is a grid.
- **Non-flat backgrounds** are not keyed out (see §5).
- **Overlapping subjects** cannot be separated by geometry - that is a segmentation problem.
- Conform never decides what a page *needs*; that is the BOM's job, written by `collection`.
