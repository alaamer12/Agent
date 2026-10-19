# Detection: Tight line height

## Catalog route

The official catalog classifies this as a **source** rule. Computed line height and rendered multi-line text matter; do not enforce one ratio as an authoring default.

## Candidate signals

1. Locate `line-height` tokens/declarations and compare computed value with font size and affected text role.
2. Inspect real multi-line paragraphs at representative widths, fonts, and languages for collision/tracking difficulty.
3. Test wrapped text, font fallback, user enlargement, and WCAG 1.4.12 spacing overrides.
4. Keep short headings/buttons distinct from sustained prose.

## False-positive controls

- Do not flag a compact heading/control solely by a numeric ratio.
- Do not describe WCAG’s 1.5× override value as the required author default.
- Do not assume a design token guarantees every rendered paragraph is readable.

## Test disposition

Source fixtures should include crowded multi-line prose, a compact short heading, and text that tolerates user spacing overrides. Browser checks verify actual wrapping/collisions; regex cannot confirm readability.