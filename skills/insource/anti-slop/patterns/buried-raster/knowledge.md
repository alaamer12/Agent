# Images hidden under overlays

**ID:** `buried-raster`  
**Catalog section:** Imagery  
**Official modality:** Source

## Definition and empirical evidence

This pattern is a signal for an image whose visible content is substantially obscured by a foreground overlay. Overlays are also a legitimate way to improve text legibility over imagery; their presence alone does not prove a defect.

## Underlying principle and potential harm

Assess whether the overlay has a clear purpose and whether the image still fulfills its role. An overly strong/broad tint can erase useful detail, weaken subject/mood, or make a hero resemble a plain panel with indistinct imagery behind it. Meaningful image information obscured visually is not restored for sighted users by alternative text.

Text contrast must be evaluated on the rendered text/background pair. A scrim is a technique, not proof that contrast requirements are met.

## Recognition signals

- Tint/overlay obscures the subject, focal detail, or intended atmosphere.
- A dark overlay is reused across unrelated images without crop/content-specific placement.
- Gradient falloff no longer aligns with text after responsive crop changes.
- Source clues include opacity, blend modes, pseudo-elements, gradients, and `object-fit`/`object-position`.

## Causes to investigate

Possible causes include a default dark tint reused globally; adding opacity for text contrast without reviewing lost detail; a gradient positioned for one crop only; or decorative treatment on informative imagery.

## Exceptions and false positives

- A localized or gradient scrim can protect text while preserving the rest of a photograph.
- A tint can be intentional brand/art direction if the subject remains perceptible.
- A CSS background can be appropriate for decorative imagery; an informative image needs an alternative and should not convey required information solely through an inaccessible background.
- A close responsive crop may intentionally emphasize a subject; verify that focal content remains visible.
- A strong-looking overlay may be needed for contrast; a subtle one can still hide the key region. Appearance alone does not settle purpose/legibility.

## Correction guidance

Identify image role and text-protection need. If meaningful content is hidden, narrow/soften the tint, reposition text, use a localized gradient/scrim or solid text panel, or choose an image with suitable copy space. Retain strong overlays only where purpose warrants them. Test actual text contrast and subject visibility at desktop/mobile crops. Provide text alternatives for informative images and avoid redundant alternatives for decorative ones.

## Independent research references

- [Nielsen Norman Group — Text over images](https://www.nngroup.com/articles/text-over-images) — contrast techniques including gradients, darkening, blur, and text backings.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — rendered text/background contrast and exceptions.
- [Nielsen Norman Group — Big pictures on small screens](https://www.nngroup.com/articles/big-pictures-small-screens) — responsive cropping and text wrapping effects.
- [W3C WAI — Decorative Images](https://www.w3.org/WAI/tutorials/images/decorative/) — image purpose and suitable CSS backgrounds.
- [W3C Failure F3](https://www.w3.org/WAI/WCAG21/Techniques/failures/F3) — required information cannot be conveyed exclusively by a CSS background image.