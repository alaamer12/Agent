# Images that move on hover

**ID:** `images-move-on-hover`  
**Catalog section:** Motion  
**Official modality:** Source

## Definition and empirical evidence

This pattern is a signal for images that shift, scale, pan, or reveal a zoomed view on pointer hover. Hover can provide feedback but depends on input modality and should not be the only path to important meaning/detail. Image zoom can also be purposeful.

## Underlying principle and potential harm

Treat motion as an enhancement, not the only route to image meaning or essential detail. Pronounced/repeated zoom may distract, feel unstable, or obscure surrounding content. Hover-only details/actions can be undiscoverable to touch and keyboard users.

WCAG 2.3.3 is Level AAA and covers disabling non-essential interaction-triggered motion. WCAG 1.4.13 is Level AA when hover/focus reveals additional content that disappears; it requires dismissibility, hoverability, and persistence under its conditions. A visual transformation of the same image is not necessarily additional content.

## Recognition signals

- The image scales/pans significantly, crops important content, or shifts neighboring layout.
- Captions/actions/essential details appear only on pointer hover.
- The effect has no keyboard/touch alternative or fails to honor reduced-motion preference.
- Source clues include `:hover`, focus styles, transitions, `transform: scale()`, clipping, and pointer scripts; assess runtime behavior on actual input devices.

## Causes to investigate

Possible causes include motion added as generic polish; enlargement used instead of a designed zoom control; hover-only captions/actions; or desktop-pointer tuning without keyboard/touch review.

## Exceptions and false positives

- Zoom can help inspect product, artwork, map, or photographic detail.
- A subtle scale change may confirm targeting when the image is already an obvious control.
- A hover preview can supplement persistent content and tap/click/keyboard zoom.
- A magnified panel/caption revealed as additional content differs from scaling the same image; assess WCAG 1.4.13 when applicable.
- A static image may still hide essential detail; evaluate interaction paths, not movement alone.

## Correction guidance

Keep purposeful motion but reduce distance/scale/duration if it competes with content. Provide visible/discoverable tap/click and keyboard paths for essential details/actions; preserve focus feedback. Honor reduced-motion preferences by removing/replacing non-essential motion while keeping zoom available. Ensure revealed overlays remain operable from the trigger. Retest actual pointer, keyboard, and touch input.

## Independent research references

- [W3C WAI WCAG 2.2 content on hover/focus](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) — scope and requirements for additional revealed content.
- [W3C WAI WCAG 2.2 animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) — Level AAA disabling non-essential interaction motion.
- [Nielsen Norman Group — Icon Usability](https://www.nngroup.com/articles/icon-usability/) — why hover-only information transfers poorly to touch.
- [MDN `prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-motion) — user motion preference.
- [Apple HIG — Gestures](https://developer.apple.com/design/human-interface-guidelines/gestures) — zoom gesture and multiple input methods.