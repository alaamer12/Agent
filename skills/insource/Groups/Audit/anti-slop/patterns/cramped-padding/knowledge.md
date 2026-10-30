# Cramped padding

**ID:** `cramped-padding`  
**Catalog section:** General quality  
**Official modality:** Browser

## Definition and empirical evidence

This visual-review signal concerns content or controls that appear too close to container edges or to one another. Padding is one part of density, not a value with a universal minimum. A compact layout can be deliberate for data-heavy views.

## Underlying principle and potential harm

Spacing should fit content, task, component, and user needs. Reduced spacing may make information harder to distinguish and controls harder to use; crowded text can be harder to scan, while close targets may be uncomfortable/easier to activate accidentally. These are contextual risks, not proven by a small CSS value.

WCAG target-size evaluates pointer targets, not general card/text padding. Text resize/reflow are separate criteria.

## Recognition signals

- Text touches borders, wrapped lines/control bounds collide, content is clipped, or grouping is unclear.
- Controls are difficult to activate; inspect actual clickable/tappable bounds, which may be larger than visible icons.
- Narrow widths or 200% text enlargement remove content/functionality or cause overlap.
- Computed padding/gaps are source clues; assess rendered results with representative/long content.

## Causes to investigate

Possible causes include compact density applied to reading content; fixed dimensions/padding that do not adapt to wrapping or enlargement; controls placed too close; or layouts tuned only with short placeholder content.

## Exceptions and false positives

- Data-intensive tables/views may intentionally offer compact density.
- Dense toolbars/control rows can use compact spacing if targets remain distinguishable and usable.
- Small within-group gaps can communicate relationships; more spacing everywhere is not always clearer.
- A low padding value may render clearly; generous padding cannot fix clipping, weak grouping, or overlapping targets.

## Correction guidance

Identify what is cramped and why. Adjust padding/layout at relevant breakpoints, let content grow/wrap, or separate neighboring groups. Retain a deliberate compact mode for dense data rather than applying it to reading/forms indiscriminately. Verify target size/spacing separately, then retest 200% text enlargement and narrow reflow. Do not apply a universal padding threshold.

## Independent research references

- [Cloudscape — Content density](https://cloudscape.design/foundation/visual-foundation/content-density) — comfortable/compact modes and readability/target tradeoffs.
- [W3C WAI WCAG 2.2 target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) — pointer targets and exceptions distinct from padding.
- [W3C WAI WCAG 2.2 resize text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) — 200% resizing without content/functionality loss.
- [W3C WAI WCAG 2.2 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — narrow viewport no-loss/reflow behavior.