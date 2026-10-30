# Low-contrast text

**ID:** `low-contrast`  
**Catalog section:** General quality  
**Official modality:** Source

## Definition and empirical evidence

This rule prompts checking whether text or meaningful interface graphics contrast sufficiently with their actual adjacent colors. WCAG 2.2 AA SC 1.4.3 generally requires 4.5:1 for normal text and 3:1 for large text (at least 18pt regular or 14pt bold), with stated exceptions. SC 1.4.11 separately requires 3:1 for visual information needed to identify UI components/states or essential graphic parts; it does not apply to every decorative edge.

## Underlying principle and potential harm

Contrast belongs to the rendered foreground/background pair and the element’s role—not a color name, token, or swatch. Insufficient text contrast can make text harder to perceive for people with low vision/reduced contrast sensitivity; low-contrast essential boundaries/graphics can make controls, states, or data distinctions harder to identify.

## Recognition signals

- Text/meaningful graphics appear visually indistinct from adjacent colors.
- Opacity, alpha, overlays, images, or gradients vary the effective background across the text/graphic.
- The theme/state/viewport changes contrast from the checked base token pair.
- A secondary/muted text role is assumed exempt without checking the actual ratio.

## Causes to investigate

Possible causes include reusing a subdued text color on a different surface; applying opacity to text/parent; image/gradient/translucent underlays; untested theme/state changes; or assuming secondary styling waives contrast.

## Exceptions and false positives

- A lower-emphasis semantic role is legitimate if it meets the applicable requirement.
- SC 1.4.3 exceptions include inactive components, pure decoration, and text that is part of a logo/brand name; “secondary” is not a general exception.
- SC 1.4.11 concerns essential component/state/graphic information, not decorative lines.
- Gray/bright color/gradient alone does not prove low contrast; a passing token pair does not guarantee all composited instances pass.

## Correction guidance

Identify the element’s role and criterion, then measure the rendered pair in each theme/state/view. Include alpha compositing and the weakest relevant area of variable backgrounds. If text fails, adjust foreground, surface, opacity, or backing; preserve subdued hierarchy with a compliant secondary color. Assess essential component edges/graphics under SC 1.4.11 and retest after changes.

## Independent research references

- [W3C WAI WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) — SC 1.4.3 thresholds/exceptions and SC 1.4.11 non-text scope.
- [MDN `opacity`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/opacity) — compositing/opacity effects on actual contrast.
- [MDN `background-image`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/background-image) — text contrast with layered images/gradients.
- [Material Design 3 — Color roles](https://m3.material.io/styles/color/roles) — semantic lower-emphasis on-surface text/icon roles.
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker) — practical foreground/background and alpha checking.