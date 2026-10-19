# Detection: Broken or placeholder image

## Catalog route

The official catalog classifies this as a **source** rule. Source paths and placeholders locate candidates; browser loading state is required to confirm a failure.

## Candidate signals

1. Inspect `<img>`/`srcset`/CSS images, `loading`, `alt`, and loading/error state handling.
2. Scroll lazy-loaded images into their loading range and wait for normal load behavior.
3. Check actual network/resource response and image load/error event.
4. Determine whether fallback is a purposeful stable error state, temporary skeleton, or unresolved placeholder.
5. Assess alternative text according to informative, functional, or decorative purpose.

## False-positive controls

- Do not mark an offscreen lazy image broken before it is expected to load.
- Do not treat a deliberate skeleton as an error while loading is in progress.
- Do not assume successful rendering proves adequate `alt` text.
- Do not infer resource failure from a single screenshot alone.

## Test disposition

Source tests should include valid, missing, lazy-offscreen, resolved skeleton, and persistent-error fallback fixtures. Browser tests verify network/load state and alternative text; regex cannot confirm.