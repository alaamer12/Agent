# Decorative grid-line background

**ID:** `codex-grid-background`  
**Catalog section:** Visual Details  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns grid-line texture used decoratively behind a page or surface without a clear user or content purpose. Grids can also be functional: chart gridlines help estimate values, while workspace grids can serve as alignment or measurement references. The question is what the lines help the user do, not whether lines exist.

## Underlying principle and potential harm

Visual hierarchy should keep the important content prominent. Dense or high-contrast lines can compete with text, controls, or data, add unnecessary visual noise, and reduce clarity. WCAG non-text contrast applies to visual information needed to understand content or identify UI components/states; it does not indiscriminately require contrast for purely decorative details. Text placed over a pattern still needs to remain readable.

## Recognition signals

- Repeating lines appear behind a hero or card without aligning to content, measurements, or a task.
- Line density or contrast draws attention away from the foreground.
- Removing/softening the grid does not make data, positioning, or meaning harder to understand.
- Source clues include repeating CSS backgrounds or pseudo-elements independent of content; chart/canvas/SVG lines tied to plotted values may instead be functional.

## Causes to investigate

Possible causes include a generic background motif added to fill space; a prototype/design-tool grid left in the shipped UI; chart defaults that were not visually tuned; or a functional workspace pattern whose purpose is not apparent.

## Exceptions and false positives

- Chart gridlines can support estimation; useful lines should be visually subordinate.
- Drawing, design, mapping, and graph-paper surfaces can use grids as measurement or alignment references.
- A structural layout grid may align content without visible lines; do not confuse it with a rendered texture.
- A faint grid can be part of an intentional visual identity. Check actual interference and contrast instead of flagging its presence alone.

## Correction guidance

Identify the grid’s purpose with the product/design owner. If it is only ornament and competes with content, remove it or reduce opacity, density, or coverage, especially behind text and controls. If functional, keep necessary lines but tune their weight/contrast so data or active work remains legible; provide equivalent text information if the graphic communicates essential content. Verify rendered readability and contrast rather than relying on source appearance alone.

## Independent research references

- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — attention direction and how excess borders/backgrounds can add clutter.
- [W3C WAI — WCAG 2.2 non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) — which meaningful UI/graphic information requires contrast.
- [storytelling with data — Gridlines are gratuitous](https://www.storytellingwithdata.com/blog/2011/07/gridlines-are-gratuitous) — practical chart-gridline tradeoffs and subordination.
- [UX Collective — Background grids, from paper to display](https://uxdesign.cc/background-grids-from-paper-to-display-7484334e989c) — grids as workspace alignment feedback versus visual noise.
- [W3C WAI — WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — text contrast when patterned backgrounds sit behind text.