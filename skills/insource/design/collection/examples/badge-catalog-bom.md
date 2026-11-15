# Filled BOM excerpt - one existing sheet, thirty-four badge slots

A real case: the client already owns a badge catalog image
(`Colorful Game Achievement Badge Collection.png`, 1536×1024 RGBA). The product needs thirty-four
96px badge files. Nothing is generated - the existing pixels are the master, and the job is to cut
them correctly.

## bom/achievements.md

- **Source:** `PAGES.md` §achievements
- **Style canon:** none needed - this is existing art, not a generated set
- **Placement:** `public/badges/`, resolved by slot id in `BadgeGrid.tsx`; a badge is swapped by
  dropping a same-named file
- **Master:** one existing 1536×1024 image, four rows holding 8, 8, 8 and 10 subjects
- **Fallback:** none available - the reference is the only master, so the delivery spec has to fit
  it rather than the other way round

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| `badge-01..34` | achievement badges | sheet `refs/badges.png` | `1536x1024 sheet rows 8,8,8,10` | `96x96 1:1 webp q82 @1x` | pending |
| `badge-locked` | locked-state placeholder | `resources` (CSS mask) | — | `96x96 svg` | shipped |

### Why `rows 8,8,8,10` and not `8x4`

The sheet is not a grid. Four rows hold 8, 8, 8 and 10 subjects, and the last row's subjects sit
closer together than the first three. Measured with `sheet_probe.py`:

```
size      1536x1024 RGBA alpha=yes
content   [27, 60, 1513, 896]  margins left=27 top=60 right=23 bottom=128
columns   1 band(s) gaps []          # a global projection smears all rows together
rows      4 band(s) gaps [33, 34, 64]  (uneven)
layout    mixed - 34 subject(s), rows 8,8,8,10
subjects  34 found, min 128x169, max 189x182
ceiling   128px square master
delivers  64@1x,2x  96@1x  128@1x
master    1536x1024 sheet rows 8,8,8,10
clips     8 interior cut line(s) of an even split land on content
```

What the two plans do to this image:

| | even `8x4` grid | `rows 8,8,8,10` |
|---|---|---|
| capacity | 32 cells for 34 slots - refuses to run | 34 |
| pitch vs subject | 186px pitch against subjects up to 189px wide | midpoint of each measured gutter |
| observed result | a 24-slot subset run reported `ok` while the review sheet showed sliced crowns and 17 edge warnings | 34/34 files, one warning, clean review |

`ceiling 128` is why the delivery is `@1x` only: 96px needs no DPR step here, and `96@2x` would
need 192px, which the smallest subject (128px) cannot supply. The reference is the only master, so
the answer is a lower DPR, never an upscaled badge.

### Baked numerals are UI text, not generated art

Levels 1-10 in the sheet carry a numeral drawn into the pixels. That is acceptable for existing art
this project ships, but it is the reason a *regeneration* of these badges is not just a re-render:

- the style canon's hard rule says **no text, letters or numbers** in generated imagery, because
  models render numerals inconsistently (and often wrongly);
- if the badges are ever regenerated, the level number is overlaid by the UI (an HTML/CSS badge or
  a `resources` composite), not baked into the master;
- the slot id stays `badge-01..34` either way, so no code changes when the artwork is replaced.

## Generation and conform

No prompt block: a `sheet <path>` row is cut, not generated.

```bash
# measure the owned sheet, then paste the printed master line into the BOM
python scripts/sheet_probe.py refs/badges.png

# cut, fit, name, verify - one run for the whole sheet
python scripts/conform.py --bom bom/achievements.md --group badge \
    --in refs/badges.png --out public/badges
python scripts/contact_sheet.py public/badges --out review/badges.png --skip-density
```

Result: 34 files (`badge-01.webp` … `badge-34.webp`), 96×96, RGBA, `conform-report.json` with
`ok: true`, `cut.mode: bands`, one warning (`badge-29` sits close to its cell edge), region
`[27, 60, 1513, 896]`. The review sheet composites all 34 on a checkerboard: every badge intact,
transparent edges, no sliced crowns, row-major order matching the catalog.

The `badge-locked` row is outside this run: it is a CSS mask shipped from `resources`, not a
cut cell, so it has no master and no delivery file from conform.
