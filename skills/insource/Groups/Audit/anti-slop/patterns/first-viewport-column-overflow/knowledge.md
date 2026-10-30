# Unbalanced opening columns

**ID:** `first-viewport-column-overflow`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

The catalog flags an opening layout where one column extends far below the other, leaving a large gap. A finding still needs judgment about the page/task and intentional choices. Unequal column heights or asymmetric layout alone are not evidence of a problem.

## Underlying principle and potential harm

Evaluate whether the opening composition communicates content priority and relationships. An unexplained empty region beside a continuing column may feel unfinished or distract from the primary message. Long content can also move related information/action farther down than the page purpose warrants; this is not automatically an issue just because content is below the fold.

At narrow effective widths, WCAG reflow concerns loss of content/functionality or unnecessary two-dimensional scrolling—not equal-height columns or first-viewport composition.

## Recognition signals

- A conspicuous empty region sits beside a column that continues far below, with no grouping/focal reason.
- The primary message/action becomes difficult to locate or related content is split awkwardly.
- Columns cause clipping, overlap, or horizontal overflow as the viewport narrows.
- Visual reordering creates a mismatch with source/keyboard reading order when the columns stack.

## Causes to investigate

Possible causes include equal visual space assigned to content with different needs; excessive fixed/minimum heights; a long text/media block paired with a short one; missing responsive changes; or content added to one column without revisiting the composition.

## Exceptions and false positives

- Editorial layouts intentionally use unequal column widths/weights.
- A main article may appropriately sit in a two-thirds column without a matching sidebar.
- Content-driven lengths do not need matching bottoms; whitespace can emphasize or separate groups.
- Desktop columns may intentionally stack at narrower widths.
- Equal-height columns can still be confusing or cramped; judge grouping and task clarity rather than symmetry.

## Correction guidance

Confirm intended hierarchy and the purpose of the opening. If a gap is accidental and undermines focus, move shorter material below both columns, redistribute related content, adjust proportions, or reduce unnecessary fixed height. Preserve deliberate editorial asymmetry. Test realistic content at desktop/narrow widths; verify no lost content/horizontal scrolling and coherent source, visual, and keyboard order.

## Independent research references

- [Impeccable Slop catalog](https://impeccable.style/slop) — long opening column/large-gap signal and contextual-judgment caveat.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — scale, grouping, and whitespace.
- [GOV.UK Design System — Layout](https://design-system.service.gov.uk/styles/layout) — purposeful two-thirds content column without a matching sidebar.
- [W3C WAI WCAG 2.2 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — narrow-width no-loss/reflow requirements and exceptions.
- [W3C WAI CSS grid reflow technique](https://www.w3.org/WAI/WCAG22/Techniques/css/C32) — responsive grid reflow and source/keyboard order.