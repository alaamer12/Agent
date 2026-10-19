# Cards flush against the scroller edge

**ID:** `edge-flush-cards`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

This browser rule flags cards in a horizontal scroller that appear to meet the viewport edge with no inset. The concern is clarity/usability, not edge alignment by itself. Platform guidance supports both full-width scrolling and inset content.

## Underlying principle and potential harm

Treat the card surface, its content, and the scroll viewport as separate layout layers. A full-bleed card/carousel can be intentional while critical text and controls remain protected from cutouts and system UI. An edge-flush treatment may feel cramped, obscure the scroller boundary, or hide cues that more items exist, but these are contextual effects to verify.

WCAG target-size checks evaluate the interactive target and spacing—not the margin between a card and viewport. Assess tappable controls independently.

## Recognition signals

- The entire card/content appears to abut the physical or viewport edge, rather than only its background/image.
- Text/control content is clipped or close to cutouts/system UI.
- The scroller boundary or availability of more items is unclear.
- Initial, intermediate, and terminal scroll positions behave differently; an edge peek may be intentional at one position.

## Causes to investigate

Possible causes include intentional full-bleed design; carousel margins differing from surrounding content; padding applied at the wrong layer; missing safe-area handling; or a next-card peek cue whose sizing breaks at some breakpoints.

## Exceptions and false positives

- Android guidance supports horizontal carousels extending into display cutouts while text/buttons remain inset from system UI and hardware.
- A partial next card can deliberately signal that more content is available.
- Full-bleed images/surfaces may extend to the edge while card content remains inset.
- Full-width and inset scroll views can both work when their boundaries and behavior are clear.
- Edge proximity alone does not prove clipping, unsafe content, poor touch targets, or wrong intent.

## Correction guidance

Confirm the intended edge-to-edge treatment and platform/safe-area rules. If content is obstructed or uncomfortably close, inset text/controls or apply safe-area insets while preserving a full-bleed surface if desired. If scrollability is unclear, establish alignment/boundaries or retain a deliberate peek cue. Test control target size independently; verify widths, cutouts, and multiple scroll positions.

## Independent research references

- [Apple HIG — Scroll views](https://developer.apple.com/design/human-interface-guidelines/scroll-views) — partial-content scroll cues and full-width/inset boundary guidance.
- [Android — Edge-to-edge design](https://developer.android.com/design/ui/mobile/guides/layout-and-content/edge-to-edge) — horizontal carousels at cutouts and insets for controls/text.
- [Nielsen Norman Group — Carousel Usability](https://www.nngroup.com/articles/designing-effective-carousels) — next-item peek/navigation cues for more content.
- [W3C WAI WCAG 2.2 target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — target area/spacing distinct from card inset.