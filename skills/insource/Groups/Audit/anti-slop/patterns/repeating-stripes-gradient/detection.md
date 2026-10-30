# Detection: Repeating-gradient stripes

## Catalog route

The official catalog classifies this as a **source** rule. A repeating pattern match is a lead; visual/contextual evidence determines whether it is unneeded decoration.

## Candidate signals

1. Search for repeating gradients and inspect image/SVG/CSS patterns that produce repeated stripes.
2. Record the exact surface, source location, frequency/spacing, contrast, and affected foreground content.
3. Determine whether stripes track data, table rows, progress, selection, status, alignment, or an intended brand texture.
4. Compare the rendered area with a plain/quieter version and verify readability in supported themes/states.

## False-positive controls

- Do not flag functional chart/table patterns or state indicators by syntax alone.
- Do not assume a gradient is decorative because it uses CSS, or functional because it is an image.
- Evaluate color-independent cues if stripes convey information.

## Test disposition

Test source candidates on a decorative repeating-gradient positive and negatives for functional table/chart/state patterns. Visual review is required to classify clutter and hierarchy; regex cannot confirm the anti-pattern.