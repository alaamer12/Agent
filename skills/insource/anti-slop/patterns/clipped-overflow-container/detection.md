# Detection: Clipped menus and popovers

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime overlay bounds, paint order, and focus behavior are required.

## Browser checks

1. Open menus/popovers near viewport edges and inside relevant scrolling/clipping ancestors.
2. Test after scroll, resize, zoom, and variable/long content.
3. Distinguish ancestor clipping, occlusion by a higher paint layer, and viewport collision.
4. Move keyboard focus through content and confirm the focused item remains visible and reachable.
5. Trace ancestor overflow/containment, transforms, stacking contexts, containing blocks, position, and overlay constraints.

## False-positive controls

- Do not treat intentional internal scrolling as failure when all items are reachable and focus remains visible.
- Do not assume z-index alone resolves ancestor clipping.
- Do not flag clipped decoration if meaningful content remains operable.
- Browser top-layer/portal placement does not guarantee viewport-fit or accessible interaction.

## Test disposition

Browser cases should include ancestor-clipped menus, viewport-collision popovers with flip/shift behavior, and usable internally scrollable long menus. Verify keyboard/pointer/touch and focus restoration; regex is not applicable.