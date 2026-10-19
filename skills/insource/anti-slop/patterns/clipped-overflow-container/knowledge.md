# Clipped menus and popovers

**ID:** `clipped-overflow-container`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

This pattern concerns a menu/popover cut off by an ancestor overflow boundary, hidden behind other content, or positioned partly outside the visible viewport. CSS overflow can intentionally clip content or create scroll regions; the question is whether necessary overlay content remains visible and operable.

## Underlying principle and potential harm

Menus/popovers should fit the context in which they open. Clipped choices/actions can be missed; keyboard focus may move to a clipped item without bringing it into view. A large `z-index` does not necessarily escape ancestor clipping because stacking and overflow are separate constraints.

## Recognition signals

- Items or edges are cut off inside a scroll/clipping ancestor.
- The overlay paints behind other surfaces or extends beyond viewport boundaries.
- Keyboard focus enters an item that is not visibly brought into view.
- Clipping occurs near different viewport edges, after scrolling/resizing, or with longer menu content.

## Causes to investigate

Possible causes include rendering inside a clipped ancestor; assuming z-index escapes clipping; transforms/containing blocks creating unexpected positioning; no viewport collision handling; or constrained popups without internal scrolling/focus behavior.

## Exceptions and false positives

- Long menus can use a max-height and internal scroll if all items remain reachable and focused content visible.
- Clipping is normal for a carousel or scroll panel; that does not mean a popover attached to it should also be clipped.
- Nonessential shadows/animation edges can be clipped while all functional content remains available.
- Browser top-layer popovers/dialogs or portals can escape ordinary ancestors, but still need correct placement and behavior.
- A screenshot or CSS declaration alone cannot establish whether a boundary is intentional or the overlay is usable.

## Correction guidance

Identify intended boundaries and which content must remain visible. Move overlays outside interfering ancestors (e.g. portal/top layer) rather than increasing z-index blindly. Handle viewport collision with flip/shift, constrain size and enable internal scrolling where appropriate. Preserve menu semantics and keyboard focus behavior (including focus restoration on close); test near viewport/container edges with keyboard, pointer, and touch.

## Independent research references

- [MDN `overflow`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow) — clipping/scroll behavior and keyboard focus consequences.
- [MDN Top layer](https://developer.mozilla.org/en-US/docs/Glossary/Top_layer) — popovers/dialogs above normal paint layers.
- [React `createPortal`](https://react.dev/reference/react-dom/createPortal) — moving DOM placement outside interfering containers.
- [Floating UI `computePosition`](https://floating-ui.com/docs/computePosition) — flip/shift/size collision handling.
- [W3C WAI-ARIA APG Menu Button](https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/) — menu semantics and keyboard/focus behavior.