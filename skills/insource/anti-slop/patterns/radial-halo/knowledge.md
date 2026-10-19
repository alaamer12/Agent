# Radial-gradient background halo

**ID:** `radial-halo`  
**Catalog section:** Color & Contrast  
**Official modality:** Source

## Definition and empirical evidence

The catalog signal is a radial glow behind page content that, when repeated across pages, makes them feel like variations of one template. A radial gradient is a neutral CSS technique; use it when it supports a deliberate focal point, lighting effect, or brand language.

## Underlying principle and potential harm

Color and contrast guide attention. A conspicuous halo repeated behind unrelated content can compete with the content, flatten page-type distinctions, or make a site feel formulaic. Text over a gradient may have varying contrast; accessibility depends on the actual rendered pairing, not gradient use alone.

## Recognition signals

- Similar glows repeat in the same position behind headings/hero content across different page types.
- The brightest/saturated area distracts from the intended focal point, imagery, controls, or action.
- Gradient backgrounds create text contrast variation across lines, viewports, or themes.
- A `radial-gradient()` declaration locates a candidate but cannot establish repetition, perceived prominence, or intent.

## Causes to investigate

Possible causes include a shared hero template applying glow by default; using gradients to create emphasis without deciding what deserves it; or retaining a campaign treatment across pages with different purposes.

## Exceptions and false positives

- A glow can direct attention to a product/subject when that emphasis matches the page’s purpose.
- A subtle vignette/ambient field may add depth without dominating.
- Repetition may be intentional branding; compare representative page types and content.
- A gradient can be too subtle to alter hierarchy. A CSS match/screenshot alone cannot establish an interchangeable design or poor readability.

## Correction guidance

Confirm the effect’s role and compare it across page types. If it is a default flourish, remove/soften it or vary treatment according to content rather than repeating mechanically. If it is a meaningful brand/focal device, document where it applies and preserve distinctions among page types. Test rendered hierarchy and text contrast at relevant viewports and themes.

## Independent research references

- [MDN `radial-gradient()`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/gradient/radial-gradient) — gradient parameters and the technique’s neutral implementation.
- [Nielsen Norman Group — Visual Hierarchy in UX](https://www.nngroup.com/articles/visual-hierarchy-ux-definition) — color/contrast as attention cues and backgrounds as possible clutter.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — contrast evaluated on rendered text/background.
- [Adobe Design — Adapting product systems for marketing](https://adobe.design/ideas/designing-design-systems-adapting-product-design-systems-for-marketing-interfaces) — expressive brand treatment within a coherent design language.