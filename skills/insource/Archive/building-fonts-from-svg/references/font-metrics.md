# Font metrics

Read this when choosing build options, changing proportions, or when text lines
look cramped, clipped, or unevenly spaced.

## Contents
- Vertical metrics
- Horizontal spacing
- Defaults and when to change them

## Vertical metrics

All values are in font units; the build uses 1000 units per em (`--upm`).

| Term | Default | Meaning |
|------|---------|---------|
| Baseline | 0 | Letters sit on it. Set by the SVG `--baseline`. |
| Cap height | 700 (`--cap-height`) | Height of capitals. Metadata only: the real height comes from the drawings. |
| x-height | 500 (`--x-height`) | Height of lowercase bodies. Metadata only. |
| Ascender | 800 (`--ascender`) | Space reserved above the baseline for line layout. |
| Descender | -200 (`--descender`) | Space reserved below the baseline (negative). |

The build writes the ascender/descender into `hhea` and `OS/2` (typo metrics)
and sets the Windows clip values (`usWinAscent`/`usWinDescent`) to cover the
tallest and lowest glyph actually drawn. If a glyph pokes past the ascender or
descender the build prints a warning: raise `--ascender` / lower `--descender`,
otherwise some programs clip the outline.

Cap height and x-height are descriptive only; if the drawings change, update the
flags so word processors and CSS `ex`/`cap` units report correct values.

## Horizontal spacing

- **Side bearing** (`--side-bearing`, default 50): empty space left and right of
  each glyph. Advance width = ink width + 2 x side bearing + `--tracking`.
- Every glyph is shifted so its ink starts exactly at the side bearing, whatever
  x position it was drawn at.
- Spacing is therefore uniform per glyph, not optical. Pairs like AV or To look
  loose because uniform bearings cannot see diagonal or open shapes. That is what
  kerning fixes (see `extending.md`), not wider bearings.
- `--space-width` (default 300) is the width of the space character.

## Defaults and when to change them

| Goal | Change |
|------|--------|
| Looser or tighter overall rhythm | `--tracking` (try +20 / -20) or `--side-bearing` |
| Heavy display strokes that look crowded | Raise `--side-bearing` to 70-90 |
| Lowercase with descenders | Taller viewBox, `--baseline`, `--descender` (see `svg-requirements.md`) |
| Glyphs look too big or small for the em | `--scale` (0.9 shrinks 10%); adjust ascender to match |
| Different em size (e.g. 2048 for TrueType convention) | `--upm 2048 --scale 2.048` and scale ascender/descender/side-bearing accordingly |
