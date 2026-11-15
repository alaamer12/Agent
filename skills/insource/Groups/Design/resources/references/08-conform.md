# Conforming a generated master

One render, many assets. A model asked for "ten diverse avatars" returns a single image holding a
grid of ten faces; the project needs ten files, each the same size, each correctly named, each
cropped where the subject actually is. **Conform** is that step. A `single` master (one hero, one
texture) goes through the same step as a one-slot run - see §3a.

The master does not have to be generated. A catalog page, a sprite sheet or any image the user
already owns is cut the same way - it is a BOM row with `sheet <path>` as its source and no prompt.
Only the pixels and the slot ids matter; what the assets are called or where they came from does
not change the cut.

```
BOM row  ──►  generate / owned file  ──►  probe + conform        ──►  delivery files + report
(collection)  (external or existing)      (this skill)               (named by slot id)
```

The slot id is the key in all four places: the BOM row, the generation prompt (when there is one),
the raw render and the delivered file. Nothing is re-derived by hand, and an id is any string the
project uses - `welcome` and `avatar-01` are the same kind of key.

Four files, three of them runnable:

| Script | Answers |
|---|---|
| `sheet_probe.py` | What is on this sheet - content bounds, row-by-row layout, gutters, cut lines, cell sizes, how large a master the subjects can supply? |
| `conform.py` | Cut it, fit it, name it, verify it against the BOM. |
| `contact_sheet.py` | Do the delivered files look right - clean alpha edges, no halos, no leftover background? |
| `sheet_geometry.py` | Not run: the masks, bands and cut boxes the two above share, so the report and the cut cannot disagree. |

---

## 1. Measure before cutting

```bash
python scripts/sheet_probe.py raw/avatars.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"
```

```text
size      1536x1024 RGBA alpha=yes background=(2, 2, 3)
content   [62, 167, 1475, 822]  margins left=62 top=167 right=61 bottom=202
columns   5 band(s) gaps [15, 15, 15, 16]
rows      2 band(s) gaps [103]
layout    regular - 10 subject(s), rows 5,5
grid      5x2 cells about 283x328
subjects  10 found, min 269x275, max 271x277
ceiling   269px square master
delivers  64@1x,2x,3x,4x  96@1x,2x  128@1x,2x  192@1x  256@1x
master    1536x1024 sheet 5x2
note      left/right margins differ (62 vs 61): cutting the canvas would shift the grid
```

Read it as five decisions:

1. **Is it one grid at all?** `layout regular` with `rows 5,5` means the rows agree, so `5x2` is a
   true description. `staggered` or `mixed` means they do not - §3b.
2. **Do the bands match the plan?** 5 columns and 2 rows for a 5x2 grid means every subject is
   separated by background. A band count lower than the grid means two subjects touch - an even
   cut would slice one of them, so cut on the measured bands or regenerate.
3. **Is the grid regular?** Even gaps mean an even split is safe. `(uneven)` and the `clipped_cuts`
   list say which interior cut lines land on content; those are the ones that would clip.
4. **How large is a subject?** `ceiling` is the smallest subject side, so it is the largest square
   master the sheet can supply **without upscaling**. Here 269px: `128x128@2x` (needs 256) fits,
   `128x128@3x` (needs 384) does not.
5. **Where is the content?** Margins of 62/61/167/202 mean the subject grid does not fill the
   canvas. That single fact decides the cut mode below.

`--json` gives the same report as data: `content_box`, `layout` (kind, per-row counts, master
spec, clipped cut lines), `columns.starts/ends/gaps`, per-cell `subject` boxes, `empty_cells`,
`master_ceiling`, `delivery_ceiling.fits`.

`master` is the line to paste into the BOM's Master column. It comes from the pixels, not from
you: `1536x1024 sheet 5x2`, or `1536x1024 sheet rows 8,8,8,10` when the rows disagree.


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
| `--bands` | cut down the middle of the gutters the image actually has (§3b) |

Remainder pixels are distributed, never dropped: a 100px-wide region split into 3 gives 33, 34,
33. A one-pixel difference between cells is irrelevant because every cell is trimmed and refit.

The run checks its own cuts. Before writing, every interior boundary of the even grid is sampled
against the content mask; boundaries that land on a subject are listed as a warning and the report
still `ok`, because the trim may recover it - but a boundary that lands on content is the signal to
switch to `--bands`:

```text
warning   1 of 2 interior cut line(s) of the even grid land on content (x=200); the gutters are
          not even - cut on the measured bands with `--bands` or plan `sheet rows ...`
```

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
python scripts/conform.py --bom bom/home.md --slots hero-home --in raw/hero-home.png --out assets/home
python scripts/conform.py --bom bom/home.md --slots avatar-01..10 --in raw.png --out out/ --dry-run
python scripts/conform.py --in sheet.png --out out/ --grid 4x4 --gutter 24 --cell 512 \
    --slots a,b,c --delivery "128x128 1:1 webp q82 @1x,2x"
python scripts/conform.py --in sheet.png --out out/ --grid 4x4 --bands \
    --slots a,b,c --delivery "128x128 1:1 webp q82 @1x,2x"
```

- **`--group avatar`** selects every BOM slot whose id is `avatar` or starts with `avatar-`.
- **`--slots avatar-01..10`** selects explicitly; ranges keep zero padding (`avatar-01`, not
  `avatar-1`) and the range must end in a number (`avatar-01..10`, not `avatar-01..avatar-10`).
  Both forms accept comma lists.
- **One run = one master.** `--in` is one image file. All selected slots must share its master
  plan; a BOM with two different sheet sizes, or a sheet plus a single, is two runs.
- Row-major order: cell 1 is top-left, cell N is bottom-right. A **subset** cuts its own cells:
  `--slots avatar-05..08` produces cells 5-8, not the first four - every slot on the master owns a
  cell, including the ones already shipped.
- **Ids are arbitrary.** `welcome`, `empty-state` and `avatar-01` are the same kind of key; a range
  is only shorthand for a numbered family. A sheet of unrelated subjects lists its ids in the BOM
  in sheet order (row-major), and that is the order they are cut in. `--slots` takes any list;
  `--group` is a convenience for ids that share a hyphen prefix.
- `--dry-run` prints the plan without opening the image or writing anything - safe in CI and
  before spending a re-render. In band mode the boxes are an even estimate and the report says so
  (`cut.estimated`); the real gutters are measured at run time.

Rows the BOM marks `shipped`, `reused`, `no-image`, `done` or `skip` are skipped, as are rows with
no master spec (stock photos, CSS icons, SVG logos). `--force` re-does shipped slots. Without a
BOM, there is no master to read: pass `--grid COLSxROWS` or `--rows C1,C2,...` or the run stops
instead of guessing.


### 3a. Single masters

A `WxH single` master holds exactly one slot, composed for its layout. Conform treats it as a
finished composition, not a cell:

| Behaviour | Sheet | Single |
|---|---|---|
| Region | content box (or `--full-canvas`) | the whole canvas, always |
| Trim | on (`--no-trim` to keep the cell) | off (`--trim` to opt in) |
| Keying | `auto` (`--no-key-bg` to keep) | off (`--key-bg auto\|#HEX` to opt in) |
| Slots per run | the sheet's cells | exactly one - select it with `--slots <id>` |
| `--grid` / `--cell` | re-cut the plan | rejected - a single master is used whole |
| Aspect mismatch | padded | padded **and warned**: regenerate at the delivery aspect or crop deliberately with `transform.py` |
| Upscale refusal, DPR ladder, naming, verify | same | same |

Negative space and backgrounds are part of a hero's layout; trimming or keying them by default
would ship a different picture than the one approved.

### 3b. Staggered and mixed sheets: cut on the gutters

A sheet whose rows hold different numbers of subjects has **no grid**. The global x-projection
smears across all rows, so the probe reports one column band even though every row holds eight or
ten subjects. The honest reading is row by row, and that is what the probe does:

```text
layout    mixed - 34 subject(s), rows 8,8,8,10
subjects  34 found, min 128x169, max 189x182
master    1536x1024 sheet rows 8,8,8,10
clips     8 interior cut line(s) of an even split land on content (x=213, x=399, x=584, x=770)
```

Here is what the two cuts do to the same real catalog - 34 badges, `rows 8,8,8,10`:

| | even `8x4` grid | `rows 8,8,8,10` |
|---|---|---|
| capacity | 32 cells for 34 slots - refuses | 34 |
| cut line | 186px pitch against 189px subjects, 8px gutters | middle of each measured gutter |
| result | clipped crowns, shifted rows, subjects reaching every interior edge | 34 clean files, one warning |

The plan, and the run:

```bash
python scripts/conform.py --bom bom/badges.md --group badge \
    --in refs/badges.png --out assets/badges
```

The same cut without a BOM:

```bash
python scripts/conform.py --in refs/badges.png --out out/ --rows 8,8,8,10 \
    --slots badge-01..34 --delivery "96x96 1:1 webp q82 @1x"
```

How it cuts: row bands are measured first, then each row's own column bands, and every boundary is
the midpoint of the gutter between two bands - outer edges stay on the content box. Trimming then
has a margin, so "subject reaches the cell edge" means a real clip rather than a flush subject.

- **`--bands`** does the same for a uniform sheet: `--grid 8x3 --bands` measures the gutters
  instead of dividing evenly. Use it whenever the probe reports `(uneven)` or `clipped_cuts`.
- **A rows plan implies band cutting.** It also refuses `gutter`, `CxR` and `--cell`, because none
  of them can describe rows that do not share a pitch.
- **`--rows`/`--grid` override the BOM's plan for one run**, not just supply it when absent. The
  override is still measured, so a flag that disagrees with the image stops at the count check below
  rather than cutting the wrong cells.
- **Count mismatch stops the run** with exit **3**, naming the row:

  ```text
  conform: row 2 of the plan has 4 subject(s) but the image shows 3 column band(s) in that row;
           subjects may be touching - regenerate with more spacing, or fix the plan
  ```

  Band mode has no "empty cell": a row that does not show its count is a mismatch, not a hole.
- **A rows plan cannot be re-timed.** The reference is the only master, so if the smallest subject
  is below the delivery's required master, lower the DPR - not the quality (§6).

---


## 4. Trimming, empty cells and the count check

After cropping a cell, the subject's bounding box is measured against:

- the **alpha channel**, when the sheet has real transparency;
- the **sheet's background colour**, otherwise. Using the sheet colour rather than the cell's
  corner matters when a subject touches a cell edge - the corner would then be the subject and the
  "subject" would come out as the gap.

`--trim` (on by default for sheets, off for singles) crops to that box; `--no-trim` keeps the full cell. `--trim-threshold`
(default 8) is how much a pixel must differ from the background to count.

A cell whose remaining area is uniform is **empty**. If any cell is empty the run reports which
slots they are and exits **3** - a 9-subject sheet cannot fill a 10-slot BOM, and guessing which
slot is missing corrupts names downstream. `--allow-empty` writes the non-empty cells and leaves a
report you can act on. A `1x1` sheet is the exception: its cell *is* the subject, so uniformity
there means "nothing to trim", not "empty".

---

## 5. Background keying (`--key-bg`)

Generated sheets often return an opaque white background. `--key-bg auto` (default for sheets;
singles keep their background unless asked) makes the
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
  "master": {"size": [1536, 1024], "kind": "sheet", "grid": [5, 2], "rows": null,
             "gutter": 0, "cell": [307, 512], "boxes": [[62, 167, 345, 495]]},
  "region": [62, 167, 1475, 822],
  "cut": {"mode": "grid", "rows": [5, 5]},
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

`cut.mode` is `grid` or `bands`; `cut.rows` is the per-row column counts actually used, and
`cut.estimated` marks a dry-run's estimate. `master.rows` is the `sheet rows ...` plan, `null` for
`CxR`.

`--json` prints it instead of the table. Exit codes: **0** ok, **2** bad spec or image, **3**
count/empty mismatch (including a band count that disagrees with the plan), **4** verification
failure.

---

## 9. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Last column is cut in half | canvas divided instead of content | default mode already fixes it; drop `--full-canvas` |
| One slot contains two half-faces | subjects touch; even grid splits them | regenerate with more spacing, or cut on the bands: `--bands` |
| `N of M interior cut line(s) ... land on content` | the gutters are not even | `--bands`, or write the measured `sheet rows ...` plan |
| 32 cells for 34 slots / rows shifted by one subject | the rows hold different counts (`8,8,8,10`) | probe it and plan `sheet rows 8,8,8,10` instead of `CxR` |
| `row 2 of the plan has 4 subject(s) but the image shows 3` | subjects touch in that row, or the plan is wrong | regenerate with spacing, or fix the plan; exit 3 |
| `N of M cells are empty` | the render has fewer subjects than the BOM | re-render, fix the BOM, or `--allow-empty` and fill the hole separately |
| `subject reaches the cell edge` warning | subject spans a cut line | re-render; if the design truly bleeds, cut with explicit `--full-canvas --cell` |
| `cell ... smaller than the required master` | the sheet cannot supply that DPR | lower the DPR, raise the sheet size, or split into more sheets |
| White corners around a round avatar | keying skipped | `--key-bg auto` (default) needs a flat border; check `key.reason`, then review with `contact_sheet.py` |
| Soft/aliased edges | upscaled | raise the master or lower the DPR; do not ship `--allow-upscale` output |
| `pillow is required` | dependency missing | install in the project's environment, never globally |
| Non-square cells | expected | cells are slice regions, not asset aspects; every subject is trimmed and refit |
| `a single master holds one slot, but N matched` | `--group` matched several single rows | one run per single: `--slots <id>` |
| `single master ... padded, not cropped` warning | the render's aspect differs from the delivery | regenerate at the delivery aspect, or crop deliberately with `transform.py` first |
| `conform needs a master plan` | no BOM master, no `--grid`, no `--rows` | conform from the BOM, or pass `--grid COLSxROWS` / `--rows C1,C2,...` |
| `slot range ... must end in a number` | wrote `avatar-01..avatar-10` | `avatar-01..10` |
| `fallback notes belong in the economy check` | Master cell holds `(fallback: ...)` | move the note out; conform parses Master strictly |

## 10. Limits

- A subject that is **partially outside** the canvas cannot be recovered; the probe's `columns`
  band count is the early signal.
- **Hand-made collages** are cut on their gutters, not on a grid: probe, then `rows` or `--bands`.
  What geometry still cannot do is invent a grid the image does not have - a sheet whose rows
  overlap, or whose subjects touch with no gutter, is re-rendered.
- **Very large sheets** are measured on a projection capped at 2048px on the long side, so a
  gutter narrower than about one downscaled pixel is invisible. Below that size nothing is
  downscaled.
- **Non-flat backgrounds** are not keyed out (see §5).
- **Overlapping subjects** cannot be separated by geometry - that is a segmentation problem.
- Conform never decides what a page *needs*; that is the BOM's job, written by `collection`.
