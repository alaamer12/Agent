# SVG requirements

Read this before drawing or accepting SVG glyphs. A font is built from many
drawings that must agree on one coordinate system; most bad fonts come from
drawings that do not.

## Contents
- The shared grid
- File naming
- Supported and unsupported SVG features
- Preparing SVGs from design tools

## The shared grid

All glyph SVGs use the same units, and the build maps them as:

    font_x = (svg_x - viewBox_min_x) * scale
    font_y = (baseline - svg_y) * scale        # y is flipped: SVG grows down, fonts grow up

- **Default grid** (used by `glyph_kit.py` and the examples): `viewBox="0 0 W 700"`,
  y=0 is cap-height, y=700 is the baseline, `--scale 1` (1 SVG unit = 1 font unit).
  Cap height is therefore 700 on a 1000-unit em.
- **Baseline** defaults to the bottom edge of each file's viewBox. When any glyph
  needs a descender (g, j, p, q, y, comma), draw every file on a taller viewBox
  and pass the baseline explicitly, e.g. `viewBox="0 0 W 900"` with `--baseline 700`
  puts 200 units of descender room below the baseline.
- **Same viewBox height in every file.** The builder warns if heights differ,
  because different heights silently shift glyphs vertically relative to each other.
- Width is free: the builder measures each outline and sets spacing itself.
  The viewBox width does not need to match the drawing.
- Draw at roughly the final size. Overshoot is normal: round letters (O, C, S)
  extend ~10 units past cap height and below baseline; that is intentional.

## File naming

The file name decides which character the glyph represents.

| File name            | Character |
|----------------------|-----------|
| `uni0041.svg`        | U+0041 (A). Preferred form. |
| `u0061.svg`, `U+0061.svg` | U+0061 (a) |
| `A.svg`, `7.svg`     | That single character |

Use `uniXXXX` for anything that is not an uppercase letter or digit. Reasons:
`a.svg` and `A.svg` are the same file on Windows and macOS (they overwrite each
other), and characters such as `/ . ? :` cannot appear in file names at all.
`glyph_kit.filename_for("a")` returns the safe name.

A missing space glyph is added automatically (width `--space-width`).
Files whose name maps to no character are skipped with a message; two files
mapping to one character abort the build.

## Supported and unsupported SVG features

Supported (each verified): `<path>` with any command (M L H V C S Q T A Z; cubics
and arcs are converted to TrueType quadratics), `<rect>`, `<circle>`, `<ellipse>`,
`<polygon>`, `<polyline>`, `transform` on an element or any parent `<g>`
(translate, scale, rotate, skewX, skewY, matrix), several elements per file
(unioned into one outline), `fill-rule="evenodd"` on the element or in its
`style`, and `width`/`height` when there is no `viewBox`.

Ignored or unsupported:

| Feature | Behavior | What to do |
|---------|----------|------------|
| Strokes (`fill="none"`, `stroke-*`) | Element skipped; fonts have no strokes | Convert strokes to outlines first (Inkscape: Path > Stroke to Path; Illustrator: Object > Path > Outline Stroke) or draw filled shapes. |
| `fill-rule` or `fill="none"` set on a parent `<g>` | Not inherited | Put it on each element. |
| Gradients, filters, images, text, CSS classes | Ignored or wrong | Not representable in a monochrome outline font. Convert text to paths. Color fonts are out of scope. |
| `<use>`, `<symbol>`, clipPath, mask | Skipped | Expand to plain paths. |

## Holes (counters in A, B, O, R, 8...)

Two correct ways; pick one per glyph:

1. One `<path>` containing outer and inner sub-contours with `fill-rule="evenodd"`
   (see `assets/templates/uni0041.svg`). Direction of the sub-contours does not matter.
2. Overlapping solid strokes that leave a gap between them (the `glyph_kit`
   approach). Nothing special needed.

A hole made by drawing a white shape on top does **not** work: fonts have no white.

## Preparing SVGs from design tools

Figma / Illustrator / Inkscape export checklist: outline strokes, convert text to
paths, expand `<use>`, keep every glyph artboard the same height, keep the
baseline at the same y in every artboard, name files by code point.
