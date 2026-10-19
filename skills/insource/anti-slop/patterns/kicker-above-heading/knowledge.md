# Label above a heading

**ID:** `kicker-above-heading`  
**Catalog section:** Typography  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns a short eyebrow/kicker label placed directly above a heading. Such labels can introduce a topic/category or orient a page within a broader group; their presence alone is not evidence of a problem. They are useful when the label adds distinct information while the heading remains the primary statement.

## Underlying principle and potential harm

Use hierarchy to direct attention according to meaning. Labels repeated without information can add noise, repeat the heading, or distract from the main message. If a styled kicker is incorrectly marked up as a heading, it can also distort the semantic document outline.

## Recognition signals

- Similar sections/cards repeatedly use labels with little or no information beyond the heading.
- Labels do not identify a useful category, taxonomy, or orientation context.
- The label is more prominent than the real heading or introduces an extra competing hierarchy level.
- Markup uses heading elements for purely visual kicker styling while skipping or confusing semantic heading structure.

## Causes to investigate

Possible causes include a component that inserts an eyebrow by default; repeated marketing copy; category metadata surfaced without user benefit; or adopting a visual trend without defining the label’s role.

## Exceptions and false positives

- Topic/content-type labels can help categorize cards or sections.
- An eyebrow can orient a page within a related group or larger information architecture.
- Editorial labels are useful when they contribute context distinct from the headline.
- A label may appear redundant in isolation but be meaningful in the surrounding page taxonomy.
- Visual styling does not determine semantic heading level; markup should reflect document structure.

## Correction guidance

Ask what information the label supplies and whether the heading or nearby content already supplies it. Remove it if it adds no useful context; otherwise keep it concise, subordinate to the true heading, and consistently tied to a real category/orientation need. Set semantic heading ranks based on content structure, not the desired visual style. Review repeated examples in their page context before applying a blanket change.

## Independent research references

- [REI Cedar — Eyebrow](https://cedar.rei.com/guidelines/typography/eyebrow) — category/grouping cues and how eyebrows differ from headings.
- [CFPB Design System — Headings](https://cfpb.github.io/design-system/foundation/headings) — optional eyebrow use for heading context/orientation.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — hierarchy and excessive competing distinctions.
- [W3C WAI — Headings in page structure](https://www.w3.org/WAI/tutorials/page-structure/headings) — semantic heading organization and assistive-technology navigation.