# Detection: Body text touching the page edge

## Catalog route

The official catalog classifies this as a **browser** rule. Check rendered text bounds and safe areas, not just full-bleed surface edges.

## Browser checks

1. Inspect running text bounds at narrow/wide viewports and portrait/landscape orientations.
2. Distinguish text inset from background/image/divider boundaries.
3. Check display cutouts/system UI and safe-area handling.
4. Test 200% text enlargement and narrow reflow for clipping or unintended page-wide horizontal scroll.

## False-positive controls

- Do not flag full-bleed backgrounds when text remains inset and readable.
- Do not enforce one universal margin/padding size.
- Do not infer a violation from source padding alone or a single viewport screenshot.

## Test disposition

Browser cases should include text genuinely at/under a viewport edge, a full-bleed image with inset copy, and safe-area/zoom/reflow states. Regex is not applicable to confirmation.