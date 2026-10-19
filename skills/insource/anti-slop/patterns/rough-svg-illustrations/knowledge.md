# Rough SVG illustrations

**ID:** `rough-svg-illustrations`  
**Catalog section:** Visual Details  
**Official modality:** Design review

## Definition and empirical evidence

The catalog describes a crude hand-coded mascot/rough SVG illustration. The key distinction is between deliberate hand-drawn style and unfinished or careless execution. Illustration can explain, express brand personality, or decorate; irregular paths alone do not establish poor quality.

## Underlying principle and potential harm

Illustrations should be purposeful, fit the product’s context, and be competently executed for their intended style. An unconsidered mascot may distract from a task, clash with product tone, reduce trust, or be difficult to interpret. Meaningful SVGs also need accessible semantics; this requirement is independent of how polished their vector paths are.

## Recognition signals

- The intended subject/message is unclear at the displayed size.
- Accidental gaps, awkward joins, unintended overlaps, clipping, inconsistent line quality/palette, or excessive detail conflict with the established illustration direction.
- The illustration distracts from information-carrying content or feels mismatched to the audience/product.
- SVG source may be inline or embedded, but hand-coding or path complexity is not a quality signal by itself.

## Causes to investigate

Possible causes include a prototype/placeholder mascot left in production; a copied/traced drawing not cleaned up; no shared illustration direction; a tone mismatch; or an asset never reviewed at its final size.

## Exceptions and false positives

- Controlled hand-drawn irregularity can deliberately convey a friendly, handmade, or expressive identity.
- An illustration system can vary subjects/compositions while keeping repeatable properties such as color, line width, and corner behavior.
- Sketches may be appropriate in exploration or a purposely informal product.
- Hand-coded SVG is a neutral implementation method; assess accessibility according to whether it is informative or decorative, not how it was authored.

## Correction guidance

Confirm message, audience, role, and intended art direction with the product/brand owner. If roughness is accidental, replace/refine the art: clarify silhouette/focal point, repair unintended path defects, and tune detail/line weight for the rendered size. If roughness is intentional, define repeatable palette, line behavior, texture, and detail level. Mark purely decorative SVGs appropriately and provide meaningful imagery with accessible names/descriptions as needed.

## Independent research references

- [GOV.UK Design System — Images](https://design-system.service.gov.uk/styles/images) — use illustrations where users need them and maintain consistent visual properties.
- [Nielsen Norman Group — Using Imagery in Visual Design](https://www.nngroup.com/articles/imagery-in-visual-design) — information-carrying versus decorative imagery and hierarchy.
- [Smashing Magazine — Hand-drawing style in web design](https://www.smashingmagazine.com/2008/06/hand-drawing-style-in-modern-web-design-volume-2) — hand-drawn personality and usability tradeoffs.
- [W3C WAI ACT Rule — SVG accessible name](https://www.w3.org/WAI/standards-guidelines/act/rules/7d6734) — accessible naming and decorative/informative SVG semantics.