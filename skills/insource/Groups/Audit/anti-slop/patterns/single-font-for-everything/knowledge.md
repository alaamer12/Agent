# Single font for everything

**ID:** `single-font-for-everything`  
**Catalog section:** Typography  
**Official modality:** Design review

## Definition and empirical evidence

This design-review pattern questions using one typeface family for headings, body, labels, and display roles. One family is not inherently harmful: a suitable family with useful weights/styles can support a clear hierarchy.

## Underlying principle and potential harm

Evaluate whether the chosen face and available styles support each role and the product’s voice. A single family may limit distinction if it lacks needed weights/styles, makes roles hard to separate, or does not suit display/extended reading. These are conditional risks; family count alone proves none of them.

## Recognition signals

- Heading, body, label, and display roles appear undifferentiated in the rendered interface.
- The family lacks weights/styles needed for distinct roles, or synthetic weights create poor results.
- Long reading/display contexts look unsuitable at actual size or in supported scripts.
- A CSS inventory showing one family is only a clue; inspect the full scale and rendered hierarchy.

## Causes to investigate

Possible causes include choosing one face for brand coherence or simplicity; adding a new role without reassessing the family; insufficient weights/styles; or relying on size alone for hierarchy.

## Exceptions and false positives

- One family with varied weights/styles can support polished, clear hierarchy.
- Size, weight, style, spacing, color, and placement can distinguish roles without switching families.
- A product can intentionally use one family across display/body roles if each use remains suitable.
- Multiple families can still yield weak hierarchy or poor readability; a second face is not inherently better.

## Correction guidance

Identify the roles and distinctions users need. If hierarchy is weak, first adjust scale, weight, style, spacing, or placement. Add a carefully scoped complementary face only if the current family is genuinely unsuitable or lacks needed styles; verify the rendered change improves clarity, readability, and brand fit. Keep one family when it meets the product’s needs.

## Independent research references

- [Nielsen Norman Group — Pairing Typefaces](https://www.nngroup.com/articles/pairing-typefaces) — pairing is optional; one family’s weights/styles can make hierarchy.
- [Shopify Polaris — Font and typescale](https://polaris.shopify.com/design/typography/font-and-typescale) — single primary admin face with separate heading/body scales and language fallback.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — typeface suitability is contextual, not a hard serif/sans rule.