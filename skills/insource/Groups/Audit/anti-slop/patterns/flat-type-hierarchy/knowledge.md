# Flat type hierarchy

**ID:** `flat-type-hierarchy`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

This pattern describes text roles that are insufficiently differentiated for readers to perceive importance and relationships quickly. A coherent combination of size, weight, spacing, color, and placement can establish hierarchy; dramatic size jumps or a prescribed ratio are not required.

## Underlying principle and potential harm

Typography should help readers identify page titles, section headings, body copy, and supporting labels. If important roles look too similar, users may need more effort to scan, distinguish sections, or find the main point. Visual hierarchy and semantic document structure are related but distinct: proper heading markup does not guarantee visual clarity, and visual scale does not determine semantic heading rank.

## Recognition signals

- Page titles, section headings, and body text appear equivalent in rendered size/weight/emphasis without compensating spacing or placement.
- Adjacent heading levels are hard to distinguish and users cannot easily scan section boundaries.
- Responsive styles or inherited defaults flatten distinctions that are clearer at other viewports.
- Semantic heading ranks do not follow content structure; this is a separate structural issue from visual flatness.

## Causes to investigate

Possible causes include a compressed type scale; body styles applied to headings; inconsistent component tokens; responsive rules that flatten type; or a deliberately restrained style extended too broadly without other hierarchy cues.

## Exceptions and false positives

- Editorial layouts may rely on weight, spacing, alignment, or position rather than large size differences.
- Dense dashboards/tables may use a narrow size range if grouping and other cues preserve priority.
- A compact type scale is not itself a defect; evaluate the complete composition.
- Correct HTML heading order does not guarantee visible hierarchy; large text should not be made a heading solely for visual size.
- No universal size or weight ratio is established by the cited guidance.

## Correction guidance

Identify intended roles and density constraints. Where roles are hard to tell apart, strengthen the relevant contrasts with a coherent type scale and complementary weight/spacing/placement cues, rather than enlarging everything. Preserve semantic heading order, then verify clarity across content, viewport widths, and text resizing to 200%. If restraint is intentional and remains understandable, document the rationale rather than forcing a formula.

## Independent research references

- [HarvardSites Design System — Typographic Scale](https://designsystem.harvardsites.harvard.edu/news/2025/05/typographic-scale) — size/weight as role cues and type scale for varied content.
- [USWDS font-size tokens](https://designsystem.digital.gov/design-tokens/typesetting/font-size) — role-based scale that projects can customize.
- [W3C WAI — Headings in page structure](https://www.w3.org/WAI/tutorials/page-structure/headings) — heading rank, structure, and navigation.
- [W3C WAI — WCAG 2.1 resize text](https://www.w3.org/WAI/WCAG21/Understanding/resize-text.html) — 200% resizing without content/functionality loss; no universal type-role ratio.