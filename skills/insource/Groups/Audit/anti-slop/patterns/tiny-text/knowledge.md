# Tiny body text

**ID:** `tiny-text`  
**Catalog section:** General quality  
**Official modality:** Source

## Definition and empirical evidence

This review signal concerns continuous body paragraphs rendered unusually small for their reading role. USWDS recommends comfortable body text (at least an effective 16px in its system) and uses smaller sizes sparingly for short companion text or specialized UI; that is system guidance, not a universal WCAG pixel minimum.

## Underlying principle and potential harm

Evaluate paragraph size with typeface, contrast, line measure, display conditions, and audience. Small text may be harder for some readers to see/distinguish; difficult paragraphs can increase effort or cause missed information. These are risks to verify, not proven by size alone.

WCAG separately requires resizing text to 200% without loss, tolerating text-spacing overrides, and meeting contrast criteria for the rendered pair. Those outcomes do not establish one universally required default font size.

## Recognition signals

- Continuous body copy is difficult to read at ordinary viewing conditions, not merely a short label/caption.
- A caption/data style has spread to explanatory paragraphs.
- Computed size changes through relative units, inheritance, responsive rules, or font fallback.
- Text clips/overlaps under 200% resize or spacing overrides; contrast is a separate measurement.

## Causes to investigate

Possible causes include shrinking prose to fit a dense layout; applying compact data/caption styles to body copy; fixed sizing that ignores user settings; or fitting too much content into a narrow component.

## Exceptions and false positives

- Captions, photo credits, footnotes, and short companion text may be smaller when legible.
- Dense tables/data displays may use compact text as a deliberate tradeoff; assess the task and enlargement behavior.
- Relative/user-adjusted sizes may differ from source values; test actual rendering.
- WCAG has no universal minimum authored pixel size; 200% resize/spacing tests assess adaptability, not default comfort.

## Correction guidance

Confirm that the affected text is sustained body copy and identify its reading context. If too small or difficult to read, increase size or improve contrast/measure; avoid applying compact caption/data styles to prose. Preserve smaller treatments for short companion text/dense data where usable. Retest actual content at representative widths, 200% resize, text-spacing overrides, and applicable contrast thresholds. Do not impose a universal pixel cutoff.

## Independent research references

- [USWDS Typography](https://designsystem.digital.gov/components/typography) — comfortable body sizing and sparing caption/data exceptions.
- [Nielsen Norman Group — Legibility, Readability, and Comprehension](https://www.nngroup.com/articles/legibility-readability-comprehension) — reader variation, legibility, and user text-size control.
- [W3C WAI WCAG 2.2 resize text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html) — 200% resize and no-loss behavior, not a size minimum.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — thresholds for rendered text/background pairs.
- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — user override test and author-default distinction.