# Detection: Decorative grid-line background

## Catalog route

The official catalog classifies this as a **source** rule. Source inspection can identify repeating grid-like paint; it cannot establish whether the grid is decorative or useful.

## Candidate signals

1. Inspect CSS backgrounds, pseudo-elements, SVG, canvas, and image assets for repeating lines or grid texture.
2. Record the source path, affected surface, line spacing, contrast, coverage, and foreground content.
3. Determine whether lines map to chart values, coordinates, alignment, measurement, or another user task.
4. Compare the rendered surface with the grid removed or softened; preserve the reason the pattern appears visually disruptive or functionally necessary.

## Contextual confirmation

Use visual review to judge hierarchy, foreground readability, whether the grid carries information, and whether removing it harms the task. Check text contrast and meaningful graphical/UI information separately.

## False-positive controls

- Do not flag graph-paper, chart, map, diagram, and design-workspace grids solely because they repeat.
- Do not treat a CSS `repeating-linear-gradient` match as proof of a visual problem.
- Separate structural layout grids from visible decorative grids.
- A visual similarity or source match alone cannot confirm harm.

## Test disposition

Source match is a candidate and should be tested on a decorative repeating-grid positive plus negative functional chart/workspace grids and a non-visible layout grid. Visual calibration is needed for hierarchy and impact; deterministic regex cannot confirm the pattern.