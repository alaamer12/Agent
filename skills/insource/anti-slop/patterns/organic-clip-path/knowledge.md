# Jagged image masks

**ID:** `organic-clip-path`  
**Catalog section:** Imagery  
**Official modality:** Source

## Definition and empirical evidence

This pattern concerns images clipped/masked with irregular or visibly jagged contours. CSS clipping/masking are neutral rendering techniques; assess whether the contour looks intentional and supports the image’s role, art direction, or composition.

## Underlying principle and potential harm

An awkward or inconsistently jagged edge may look accidental or distract from the subject. A crop/mask can hide a face, product feature, gesture, or other focal information. These effects depend on actual rendering/content, not merely a non-rectangular shape.

Image accessibility depends on purpose: informative images need an alternative conveying essential information; decorative images may use an empty alternative. An alt attribute does not repair a visually obscured subject for sighted users.

## Recognition signals

- Contour has accidental-looking kinks or inconsistent edges that conflict with art direction.
- Shape competes with the image subject or cuts into focal content at responsive sizes.
- `clip-path`, SVG clip paths, or `mask-image` are source clues; they cannot establish intent or quality.
- Center crop/object-fit behavior hides an off-center subject at some dimensions.

## Causes to investigate

Possible causes include a path tuned for only one size; default center cropping; poorly scaled mask/low-resolution asset; or an effect reused across unlike images without checking each subject.

## Exceptions and false positives

- Hand-cut, fluid, collage-like, or irregular silhouettes can be deliberate brand art direction.
- Different crops/masks can be appropriate when they preserve the focal subject across formats.
- Decorative imagery may not convey essential information; informative imagery needs a suitable alternative.
- A smooth mask can still obscure content; a visibly irregular contour can be intentional and well executed.

## Correction guidance

Confirm image role and intended art direction. If an edge looks accidental or competes with the subject, simplify/refine the path, reduce its prominence, or change the crop. Tune focal positioning or art-direct separate responsive crops, then inspect the actual subject at each size. Keep intentional organic treatments that fit the brand and purpose. Provide appropriate alt text for informative images and empty alternatives for decorative ones.

## Independent research references

- [MDN — CSS clipping](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Masking/Clipping) and [CSS masking](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Masking) — clipping region versus opacity/luminance masks.
- [web.dev — Responsive images](https://web.dev/learn/design/responsive-images) — `object-fit` cropping and `object-position` focal adjustment.
- [GOV.UK Design System — Images](https://design-system.service.gov.uk/styles/images) — intentional illustration need, style consistency, and information simplification.
- [W3C WAI — Images Tutorial](https://www.w3.org/WAI/tutorials/images/) — informative/decorative/functional image alternatives.