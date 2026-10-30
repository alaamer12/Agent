# Detection: Jagged image masks

## Catalog route

The official catalog classifies this as a **source** rule. `clip-path`/mask syntax finds candidates; rendered art direction and focal visibility require visual review.

## Candidate signals

1. Locate CSS/SVG clipping and mask rules applied to raster/vector images.
2. Inspect silhouettes at actual display sizes and responsive crops for irregular defects or subject loss.
3. Check focal point after `object-fit`/`object-position` and compare against approved art direction.
4. Determine whether imagery is informative or decorative and review alternative text separately.

## False-positive controls

- Do not flag every organic/non-rectangular contour.
- Do not infer craftsmanship from path complexity or file format.
- Do not treat alt text as evidence that the visible subject is not obscured.

## Test disposition

Source candidates can locate clipping/masking. Visual cases should include intentional fluid-brand masks, accidental jagged edges, and responsive crops that hide/preserve focal content. Regex cannot confirm quality.