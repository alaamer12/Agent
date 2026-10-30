# Detection: Placeholder-style illustrations

## Catalog route

The official catalog classifies this as a **source** rule. Primitive geometry or flat fills are candidate construction signals; visual/contextual review decides whether an illustration feels unfinished or useful.

## Candidate signals

1. Locate SVG/image assets and identify shape-built or low-fidelity illustration styles.
2. Compare rendered asset with approved illustration guidance and related assets.
3. Assess clarity, composition, proportions, palette/stroke consistency, and whether the image serves a task or defined brand role.
4. Check informative/decorative purpose and appropriate text alternatives separately.

## False-positive controls

- Do not flag geometric shape construction, minimal palettes, or abstract art alone.
- Do not equate SVG path simplicity with placeholder quality.
- Do not use accessibility semantics as a proxy for visual craftsmanship.

## Test disposition

Source candidates can find assets but visual calibration must include an intentional geometric system and an unrefined placeholder. Include separate decorative/informative alt-text cases; regex cannot confirm visual quality.