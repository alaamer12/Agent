# Detection: Cards flush against the scroller edge

## Catalog route

The official catalog classifies this as a **browser** rule. It requires runtime geometry and visual/context inspection.

## Browser checks

1. Identify horizontal scroll viewport, card bounds, content padding, parent margins, clipping/overflow, and safe-area insets.
2. Compare card/background edges with text and control bounds; distinguish full-bleed surfaces from inset content.
3. Inspect initial, intermediate, and terminal scroll positions at representative viewport sizes and device cutouts.
4. Check the scroller boundary and whether a next-card peek or other cue communicates additional content.
5. Test interactive target size/spacing separately.

## False-positive controls

- Do not flag intentional edge-to-edge carousels or full-bleed images solely for reaching a viewport edge.
- Do not infer cramped content from a surface edge when text/controls have proper internal insets.
- Do not treat card margins as a target-size failure.
- Source declarations cannot establish actual scroll behavior/device obstruction.

## Test disposition

Browser fixture/evaluation should include an obstructed edge-flush card, an edge-to-edge carousel with safe content insets, a deliberate next-card peek, and cutout/device-safe-area cases. Regex is not applicable to confirmation.