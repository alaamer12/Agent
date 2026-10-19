# Detection: Content overflowing its container

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime layout and access to full content are required; overflow can be intentional.

## Browser checks

1. Test at narrow widths, zoom/text enlargement, and with long/unbreakable/localized content.
2. Identify whether overflow belongs to the page or a meaningful contained region.
3. Check clipping/lost text and controls, wrapping, flex/grid shrink, and focus visibility.
4. For intended scroll areas, verify touch/pointer/keyboard discoverability and access to all content.
5. Confirm adjacent content reflows even where tables/code need two-dimensional layout.

## False-positive controls

- Do not flag usable, intentional table/code/carousel scrolling solely for being horizontal.
- Do not hide overflow cosmetically without checking content loss.
- Do not assume no visible scrollbar means no clipping.
- Do not apply the two-dimensional exception to unrelated content around a table.

## Test disposition

Browser fixtures should include accidental page overflow, a clipped control/text case, an accessible contained table/code region, and long tokens that wrap correctly. Regex is not applicable to confirmation.