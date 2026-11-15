# Filled BOM excerpt - one sheet, ten avatar slots

A real page BOM for a testimonials/community section: ten persona avatars, delivered at 128px,
generated as one sheet. Every number below was measured, not guessed.

## bom/home.md

- **Source:** `PAGES.md` §home
- **Style canon:** `bom/style.md` (flat 2D vector, warm off-white UI, rounded shapes)
- **Placement:** `public/images/home/avatars/`, resolved by slot id in `Home.tsx`; replacing an
  avatar is dropping a same-named file
- **Sheet plan:** one 1536×1024 render, 5×2, no gutter (the generator spaces subjects itself)
- **Fallback:** if the sheet fails, two 2×2 sheets at 1024×1024 (cells 512px) or ten singles

| Slot | Role | Source | Master | Delivery | Status |
|---|---|---|---|---|---|
| `avatar-01..10` | testimonial personas | generate sheet 5x2 | 1536x1024 sheet 5x2 gutter 0 | `128x128 1:1 webp q82 @1x,2x` | pending |
| `logo-customer` | customer wordmark row | reuse `brand/customers.svg` | — | `240x64 svg` | shipped |
| `bg-testimonial` | section texture | generate single | 2048x1152 single | `1024x576 16:9 webp q70 @1x,2x` | pending |

### Why `@1x,2x` and not `@3x`

`128px @3x` needs 384px masters. The 5×2 sheet yields ≈283×328 cells, so the plan would be
impossible without upscaling. Measured with `sheet_probe`:

```
content   margins left=62 top=167 right=61 bottom=202
columns   5 bands, gaps [15, 15, 15, 16]
rows      2 bands, gap [103]
subjects  min 269x275, max 271x277
ceiling   269px square master
delivers  64@1x,2x,3x,4x  96@1x,2x  128@1x,2x  192@1x  256@1x
```

If the product later needs 3x avatars, the BOM changes to three 2×2 sheets (512px cells) - a
different request count, recorded before generating, not discovered after.

## Prompt - `avatar-01..10` (one prompt for the sheet)

> **Style** - Flat 2D vector cartoon illustration, clean smooth geometric shapes, minimal shading,
> soft warm palette on a plain off-white background. Strictly 2D: no 3D render engine look, no
> realistic materials, no skin texture, no gradients beyond flat tint.
>
> **Character** - Ten distinct friendly adults, chest-up, centred in a 5×2 grid, one person per
> cell, generous even spacing between cells, identical camera framing in every cell.
>
> **Action** - Each person faces the viewer with a relaxed, welcoming smile; varied hair, skin
> tones, headwear and clothing colours; no props crossing cell boundaries.
>
> **Color Palette & Background** - Warm off-white canvas (#F7F4EF), muted pastels for clothing,
> consistent lighting direction. No text, no letters, no numbers, no logos, no watermarks.

Hard rules are appended verbatim from `bom/style.md`.

## Generation and conform

```bash
# derived from the BOM row - master size, sheet grid, batch
python scripts/generate.py --prompt-file bom/home-avatar-prompt.txt --size 1536x1024 --out raw/
#   ^ run from the `generate` skill

# measure, then cut into slot files
python scripts/sheet_probe.py raw/avatars.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"
python scripts/conform.py --bom bom/home.md --group avatar --in raw/avatars.png \
    --out public/images/home/avatars
python scripts/contact_sheet.py public/images/home/avatars --out review/home-avatars.png --skip-density
```

Result: 20 files (`avatar-01.webp` … `avatar-10.webp` plus `@2x`), 128×128 and 256×256, RGBA,
transparent outside each subject, `conform-report.json` with `ok: true`, no warnings, ≈190 KB
total. A review sheet (`contact_sheet.py --skip-density`) composites the ten 1x files on a
checkerboard: clean circular edges, transparent corners, no halo. The other two rows are outside
this run: `logo-customer` is `shipped` (reused), and `bg-testimonial` is its own single-master
run (`--slots bg-testimonial --in raw/bg-testimonial.png`), used whole with its background kept.
