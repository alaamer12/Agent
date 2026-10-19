# Body text touching the page edge

**ID:** `body-text-viewport-edge`  
**Catalog section:** General quality  
**Official modality:** Browser

## Definition and empirical evidence

This rule signals running text appearing to meet the viewport boundary without an inset. Edge-to-edge backgrounds/images/dividers may be intentional; assess the text itself, not just the surface edge.

## Underlying principle and potential harm

Margins and line measure support readable text layout, while safe areas protect content from cutouts/system UI. Body text flush to an edge may feel crowded or become obscured. If enlargement/reflow clips content or forces two-dimensional scrolling, that is a separate accessibility concern. WCAG text resize/reflow criteria do not prescribe one universal margin value.

## Recognition signals

- Running text glyphs visibly touch the viewport boundary at representative sizes/orientations.
- Safe-area/cutout/system UI obscures the text.
- Narrow breakpoints remove a previously present content inset.
- 200% text resize or narrow reflow causes clipping or page-wide horizontal scrolling.
- A screenshot or zero-padding rule is a clue, not a verdict about all viewport states.

## Causes to investigate

Possible causes include a missing/overridden content inset; full-bleed styling applied to text as well as its background; a responsive rule dropping padding; or treating safe-area insets as a substitute for ordinary margins.

## Exceptions and false positives

- Full-bleed backgrounds, images, and dividers can reach the screen edge while text remains inset.
- An immersive/editorial layout may intentionally place brief display text near an edge if readable and unobstructed.
- Short headlines/labels are not the same as long-form body copy; assess role and rendering.
- The apparent edge may be a surface boundary rather than the text’s own boundary; a CSS margin value alone does not prove readable spacing.

## Correction guidance

Identify which layer reaches the edge. If running text is crowded/obstructed, add responsive inline padding or use an inset text column while keeping a background full-bleed if desired. Account for safe areas but do not rely on them as the only margin. Recheck realistic text at narrow widths and 200% enlargement for loss/sideways page scrolling; use system spacing guidance as a starting point, not a universal criterion.

## Independent research references

- [USWDS Typography](https://designsystem.digital.gov/components/typography) — responsive text margins and readable measure.
- [Android — Edge-to-edge design](https://developer.android.com/design/ui/mobile/guides/layout-and-content/edge-to-edge) — full-bleed backgrounds versus inset text/buttons and cutouts.
- [Apple HIG — Layout](https://developer.apple.com/design/human-interface-guidelines/layout) — standard margins, readable widths, and safe areas.
- [W3C WAI WCAG 2.2 resize text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) — 200% text resize without content loss.
- [W3C WAI WCAG 2.2 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — narrow-view behavior without two-dimensional scrolling for ordinary content.