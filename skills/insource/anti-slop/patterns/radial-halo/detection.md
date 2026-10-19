# Detection: Radial-gradient background halo

## Catalog route

The official catalog classifies this as a **source** rule. A radial-gradient token is only a candidate; the rule concerns repeated, template-like visual use.

## Candidate signals

1. Locate radial-gradient backgrounds, pseudo-elements, images, and related tokens.
2. Compare rendered placement/intensity across representative pages and page types.
3. Assess whether the glow directs attention to the intended focus or competes with content.
4. Check text contrast over each relevant gradient area/theme/viewport.

## False-positive controls

- Do not flag every radial gradient.
- Do not infer cross-page sameness from a single route.
- Do not assume a CSS source match shows the rendered prominence or contrast.
- Preserve purposeful brand/focal lighting when it supports page meaning.

## Test disposition

Source candidates can identify gradient implementations, but visual evaluation is required. Include a repeated generic halo positive and negatives for subtle brand texture and a purposeful product spotlight; test contrast separately. Regex cannot confirm.