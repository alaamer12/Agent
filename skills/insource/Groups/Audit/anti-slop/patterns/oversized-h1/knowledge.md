# Oversized hero headline

**ID:** `oversized-h1`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

The catalog concerns a long hero headline set so large that it occupies most of the first screen, leaving little room to explain the offer or show the next action. The issue is its impact on the composition and task, not a fixed font-size threshold.

## Underlying principle and potential harm

Make the headline prominent enough to communicate the page’s main message while keeping necessary context and the intended page experience understandable. Large text naturally takes more space; when a long title dominates, supporting copy or a useful next step may be hard to find. Narrow widths or increased text size can cause crowding, clipping, and displaced content.

## Recognition signals

- The hero’s actual headline consumes most of the available composition and pushes useful context/action out of view or into awkward placement.
- It wraps into unexpected extra lines, clips, overlaps, or crowds supporting copy/controls at relevant widths.
- Its visual dominance is disproportionate to the page’s main offer or editorial purpose.
- Source clues include computed H1 size/line-height, text measure/width, breakpoints, forced breaks, and `white-space` rules.

## Causes to investigate

Possible causes include desktop type scaling carried unchanged to narrow screens; long or recently changed copy; forced line breaks/constrained measure; or fluid sizing that grows faster than the layout.

## Exceptions and false positives

- Editorial/brand-led pages may intentionally make display type the primary content.
- A short, high-priority headline can use large type to establish hierarchy efficiently.
- Not every intended next action must appear above the fold; evaluate the page purpose and navigation.
- Large computed size, several lines, or a dramatic treatment alone does not prove clutter, unreadability, or WCAG failure.

## Correction guidance

Confirm the headline’s purpose and brand role. If it crowds out necessary context or action, shorten copy, reduce the maximum display size, adjust measure/line-height, or adapt the layout at narrow widths. Preserve large type where it serves hierarchy. Check the real copy across representative viewports and 200% text resize to ensure no content or functionality is lost.

## Independent research references

- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — scale, attention, and alternative hierarchy cues.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — type roles, measure, line-height, and space consumed by large text.
- [Design Systems — Typography](https://www.designsystems.com/typography-guides) — responsive type planning and display-face use.
- [MDN `clamp()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/clamp) — bounded fluid type sizing and scaling.
- [W3C WAI WCAG 2.2 resize text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) — 200% text-resize no-loss criterion.