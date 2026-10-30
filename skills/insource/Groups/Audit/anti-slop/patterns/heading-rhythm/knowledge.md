# Heading closer to the previous section

**ID:** `heading-rhythm`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

This browser rule concerns a section heading whose spacing makes it seem attached to the preceding section rather than the content it introduces. Proximity affects perceived grouping; the right rhythm depends on the content/layout, so a measured gap alone is not proof of a defect.

## Underlying principle and potential harm

Use spacing to make relationships clear. Headings generally need stronger separation from the previous section than from their following content. If the preceding section is too close, the heading may appear to continue it; if the following content is too far away, the heading can seem detached. Either can weaken scanning and section boundaries.

## Recognition signals

- The whitespace above the heading is smaller than or visually weaker than the space below it.
- The heading reads as the prior paragraph’s continuation rather than the next section’s label.
- Wrapped headings or long content change the perceived grouping at some viewport sizes.
- Computed vertical margins/padding differ from authored expectations because adjacent block margins collapse; margins between flex/grid items behave differently.

## Causes to investigate

Possible causes include insufficient space before the heading; excessive trailing space after the prior section; inconsistent spacing tokens/component styles; or assuming adjacent margins add when they collapse.

## Exceptions and false positives

- Close heading-to-content spacing is usually purposeful grouping.
- Compact/editorial layouts may use tighter rhythm when relationships remain clear.
- An introductory paragraph may belong with the previous section/transition; inspect content hierarchy rather than applying a formula.
- Typography, dividers, alignment, or other cues may clarify a small gap; apparent generosity may still fail in the overall composition.
- USWDS’s 1.5× above-to-below suggestion is a design-system guideline, not a universal threshold.

## Correction guidance

Confirm content hierarchy first. If the heading reads as part of the prior section, increase separation above it, reduce excess trailing space before it, or add another grouping cue; keep it visually connected to its own content. Follow project spacing conventions and inspect computed/rendered behavior across relevant layouts.

## Independent research references

- [Nielsen Norman Group — Proximity principle](https://www.nngroup.com/articles/gestalt-proximity) — grouping and heading-to-section whitespace.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — spacing ratio recommendation and grouping/separation.
- [W3C WAI — Headings in page structure](https://www.w3.org/WAI/tutorials/page-structure/headings) — content organization and navigation role of headings.
- [MDN — Margin collapsing](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Box_model/Margin_collapsing) — computed vertical gaps and flex/grid behavior.