# Identical card grids

**ID:** `identical-card-grids`  
**Catalog section:** Layout & Space  
**Official modality:** Design review

## Definition and empirical evidence

This pattern concerns repeating the same card geometry/arrangement when content roles, importance, or shape differ. A consistent card grid can be useful for related items; identical geometry alone is not evidence of a problem.

## Underlying principle and potential harm

Let layout reflect content relationships and the user’s task. An undifferentiated template for unlike content can flatten priority, make unrelated sections appear equivalent, or add containers without improving grouping. Comparable items often benefit from predictable placement, while card layouts can be harder to scan/compare if their information is unpredictable.

## Recognition signals

- Unlike material is forced into identical slots despite different roles, lengths, or importance.
- Equal-size/equal-emphasis cards make critical versus secondary content indistinguishable.
- Cards make users compare information scattered in inconsistent positions.
- Repeated component/grid styles are source clues; they cannot establish whether items are actually comparable or repetition helps scanning.

## Causes to investigate

Possible causes include a reusable card component used as the default for every section; treating all items as equally important; choosing a template before content roles are settled; or retaining a uniform grid after content changed.

## Exceptions and false positives

- A consistent responsive grid helps present related/comparable items.
- Predictable title/metadata/action positions can support comparison.
- Shared geometry can establish a cohesive component family even when content varies.
- Uniform tiles may be correct when choices/categories truly have equal priority.
- Visual variation is not automatically better; it can make comparisons harder.

## Correction guidance

Start with content relationships and user task. Keep consistent grids for comparable items; vary size/placement/emphasis only when role or priority warrants it. For direct comparison/search, consider a list/table with aligned fields; for content that needs no enclosure, use headings and whitespace. Test realistic content and responsive layouts, checking hierarchy and information findability.

## Independent research references

- [Nielsen Norman Group — Cards](https://www.nngroup.com/articles/cards-component) — flexible content containers, varying lengths, and scan/comparison considerations.
- [Material Design 3 — Cards](https://m3.material.io/components/cards/guidelines) — grids/mosaics and cautions against unnecessary card enclosures.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — attention hierarchy and obscured priority.
- [USWDS Card](https://designsystem.digital.gov/components/card) — related card groups in responsive grid utilities.