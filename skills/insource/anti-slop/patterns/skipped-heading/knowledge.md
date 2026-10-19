# Skipped heading level

**ID:** `skipped-heading`  
**Catalog section:** General quality  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns semantic heading ranks that appear to jump over a level when introducing a deeper subsection (for example, `h2` followed by `h4`). HTML heading rank conveys document structure and supports navigation. Choose heading elements for content relationships, not their default appearance.

## Underlying principle and potential harm

Markup should expose the same information/relationships that the content outline intends. A skipped rank when entering a subsection can make the outline confusing to screen-reader users navigating a heading list. WCAG addresses programmatic relationships and descriptive headings, but an isolated rank jump is not automatically a conformance failure.

## Recognition signals

- A heading uses a deeper rank without a corresponding parent subsection.
- Page outline/assistive-technology heading list conflicts with the actual content hierarchy.
- A tag appears chosen to obtain default font sizing rather than represent structure.
- CSS visual size does not match semantic rank; style changes cannot alter rank.

## Causes to investigate

Possible causes include selecting tags for appearance; a CMS/component emitting a fixed rank in a different context; a missing intermediate section that genuinely exists; or edits that changed outline without updating markup.

## Exceptions and false positives

- A higher-level heading may follow a lower-level heading when it closes that subsection and begins a new one.
- Headings in persistent sidebars/independent regions need not mirror main-content ranks; keep each region consistent.
- Nested sections still require ranks that reflect actual relationships; sectioning markup is not a visual-size substitute.
- A large `h3` or small `h2` is not a semantic skip solely due to size.
- Conversely, visual hierarchy without semantic headings may fail to expose structure programmatically.

## Correction guidance

Determine the intended content outline. Use the next appropriate rank when a heading introduces a deeper subsection; add a missing parent only if that section really exists. If rank was chosen for size, retain the semantically appropriate element and style it with CSS. Define rank expectations for shared components/independent regions and test the combined runtime heading list without visual styling.

## Independent research references

- [W3C WAI — Headings in Page Structure](https://www.w3.org/WAI/tutorials/page-structure/headings) — rank hierarchy, subsection skips, valid skips when closing sections, and fixed regions.
- [MDN — Heading elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/Heading_Elements) — semantics/navigation and CSS versus heading tags for sizing.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) — SC 1.3.1 programmatic relationships and SC 2.4.6 descriptive headings.
- [WHATWG HTML — Sections](https://html.spec.whatwg.org/multipage/sections.html) — heading rank as semantic structure.