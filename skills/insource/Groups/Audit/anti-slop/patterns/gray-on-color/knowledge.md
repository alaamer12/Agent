# Gray text on colored background

**ID:** `gray-on-color`  
**Catalog section:** Color & Contrast  
**Official modality:** Source

## Definition and empirical evidence

The catalog warns about potentially washed-out gray text on a colored surface; it does not prohibit gray or colored backgrounds. WCAG evaluates the effective rendered foreground/background pair. Level AA generally requires 4.5:1 for normal text and 3:1 for qualifying large text (at least 18pt, or 14pt bold), with stated exceptions.

## Underlying principle and potential harm

Muted secondary text can be an intentional hierarchy role, but meaningful text must remain legible and satisfy applicable contrast requirements. Weak contrast can make labels, instructions, or supporting copy harder to perceive, particularly for some users with low vision or color-vision deficiencies. A color name or hue pairing alone does not establish failure.

## Recognition signals

- Gray or low-opacity text sits over a saturated/tinted surface and may be too close in effective luminance.
- The background is a gradient, image, translucent layer, or theme/state-dependent color.
- Parent opacity, alpha channels, inherited styles, or compositing change the actual text/background pair.
- A gray text token may have been reused on a different surface than intended.

## Causes to investigate

Possible causes include a muted-text token used on a newly saturated surface; opacity applied to text/parent; a brand/theme change without retesting; or measuring base colors rather than the composited result.

## Exceptions and false positives

- A lower-emphasis semantic text role is legitimate when it remains sufficiently distinct in the actual pair.
- Gray text on tinted/brand/status surfaces can pass if measured contrast is adequate.
- The lower 3:1 threshold applies only to WCAG-defined large text, not every visually prominent heading.
- WCAG has specific exceptions such as decoration, inactive controls, and logos; “secondary” text is not an exception by itself.
- A source scan or screenshot may miss computed opacity, layered surfaces, and theme variants.

## Correction guidance

Confirm the text role and actual background, including compositing. If meaningful text fails its threshold, adjust foreground (for example, a darker tint or suitable neutral), increase surface contrast, or use a more stable surface. Retest the rendered pair with an appropriate contrast checker; do not choose by hue intuition. If an intentional muted role passes, document the semantic role and pairing. Recheck modes, transparency, and states.

## Independent research references

- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — thresholds, large-text definition, and exceptions.
- [MDN `opacity`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/opacity) — element opacity versus background alpha and rendered compositing.
- [Material Design 3 — Color roles](https://m3.material.io/styles/color/roles) — semantic roles including lower-emphasis on-surface text.
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker) — foreground/background and alpha-aware contrast testing.