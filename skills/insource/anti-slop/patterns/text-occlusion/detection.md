# Detection: Text covered by another element

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime geometry and rendered text are required to establish coverage.

## Browser checks

1. Identify text bounds and overlapping opaque/partially opaque elements at relevant routes/states.
2. Test normal/narrow widths, long/localized copy, and increased zoom/text size.
3. Determine whether meaningful text/interaction is actually obscured or whether the overlay is intentional and controllable.
4. Inspect position, stacking contexts, transforms, clipping/overflow, and fixed sizing to find likely causes.
5. For hover/focus content, check dismissible, hoverable, and persistent behavior.

## False-positive controls

- Do not flag intentional count/status badges, tooltips, popovers, or selection overlays solely for overlap.
- Do not treat a higher `z-index` as a universal fix.
- Do not infer visible readability from DOM/accessibility-tree presence alone.
- Separate actual meaningful text occlusion from overlap of decoration.

## Test disposition

Browser evaluation should cover accidental covered text, purposeful badge/tooltip overlays, and layouts that only occlude after resize or long text. Regex is not applicable to confirmation.