# Detection: Cramped padding

## Catalog route

The official catalog classifies this as a **browser** rule. Assess rendered comfort and usable target bounds; do not use a universal padding threshold.

## Browser checks

1. Inspect realistic/long content at narrow and wide viewports.
2. Check text-to-edge distance, wrapping, collisions, grouping, clipping, and control activation.
3. Inspect actual clickable/tappable bounds separately from visible icon size and container padding.
4. Test 200% text enlargement and narrow reflow for content/functionality loss.

## False-positive controls

- Do not flag dense-data compact modes solely for small padding.
- Do not infer target-size failure from visual proximity; measure the interactive target.
- Do not assume generous padding guarantees usability.

## Test disposition

Browser cases should include crowded text/control layouts, intentional compact data density, and increased text sizes/narrow widths that do and do not preserve content. Regex is not applicable to confirmation.