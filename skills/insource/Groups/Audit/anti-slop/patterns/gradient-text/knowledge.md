# Gradient text

**ID:** `gradient-text`  
**Catalog section:** Color & Contrast  
**Official modality:** Source

## Definition and empirical evidence

This pattern refers to glyphs filled/colored with a gradient, commonly using `background-clip: text`. It is a styling choice, not proof of a design/accessibility defect. The rendered text needs adequate contrast and fallback behavior when the effect or background image is unavailable.

## Underlying principle and potential harm

Text must remain legible throughout the gradient and over the actual backdrop. Since glyph color varies, some portions can blend into the page/background, especially with small text or thin strokes. WCAG generally requires 4.5:1 for normal text and 3:1 for large text, with a limited exception for text that is part of a logo/brand name; that is not an exemption for all branded copy. Text must also resize to 200% without losing content or functionality.

## Recognition signals

- CSS `background-clip: text`, transparent text fill, SVG gradient fills, or image-based text.
- Gradient portions with the weakest contrast cross glyph strokes, particularly at small sizes.
- Missing solid fallback or browser behavior when clipping/background image is unsupported.
- Contrast varies across the glyphs; test the lowest-contrast area, not one average sample.

## Causes to investigate

Possible causes include applying a fashionable effect by default; using color variation to manufacture prominence; reusing a brand gradient outside its display role; or omitting fallback styling.

## Exceptions and false positives

- Gradient logos/wordmarks and short display-brand treatments can be intentional.
- A gradient may be readable in a large heading or backed by a solid accessible color.
- The logo contrast exception is limited to text that is part of a logo/brand name.
- A source match settles neither intent nor actual readability; a visually attractive gradient may still contain unreadable portions.

## Correction guidance

If meaningful text is hard to read, adjust gradient colors/direction, add a sufficiently contrasting solid color fallback, or move the gradient to a decorative element. Test rendered glyphs across the full gradient, relevant themes/states, font loading, browser support, and text resizing. Keep intentional treatments when they work in context and document their scope.

## Independent research references

- [MDN `background-clip`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/background-clip) — text clipping technique, contrast, fallback, and browser support.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — rendered text contrast and limited logo exception.
- [W3C WAI WCAG 2.2 resize text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) — 200% resize/no-loss requirement.
- [WebAIM — Contrast and Color Accessibility](https://webaim.org/articles/contrast) — gradients need lowest-contrast-area evaluation.
- [Nielsen Norman Group — Text over images](https://www.nngroup.com/articles/text-over-images) — rendered backdrop contrast and design-preserving ways to improve it.