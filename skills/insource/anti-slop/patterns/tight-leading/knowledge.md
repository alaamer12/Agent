# Tight line height

**ID:** `tight-leading`  
**Catalog section:** General quality  
**Official modality:** Source

## Definition and empirical evidence

This visual-review signal concerns line spacing that makes multi-line text crowded or difficult to track. CSS `line-height` controls line-box height; a unitless value scales with font size. Readability depends on role, typeface, size, language, and measure; there is no universal authoring ratio for every use.

## Underlying principle and potential harm

Lines in sustained text need enough separation for readers to track them. Tight leading can make line returns harder or cause visual collisions after wrapping/font substitution. Study findings are context-dependent; a CSS value alone does not prove harm.

WCAG 2.2 SC 1.4.12 tests whether users can override text spacing (including line height at least 1.5× font size) without loss of content/functionality. It does not require authors to use those values by default, and applicability varies by language/script.

## Recognition signals

- Multi-line text appears crowded, glyphs collide, lines are hard to track, or wrapped text clips.
- Computed `line-height` is tight relative to font size/typeface/measure, especially in long passages.
- Font loading/fallback, localization, zoom, or user spacing overrides change the rendered result.
- Source values are clues; inspect computed styles and actual line wrapping.

## Causes to investigate

Possible causes include compact heading/control styles reused on paragraphs; fixed-height components; shared tokens used outside intended roles; or tuning for one font without checking fallback/localized text.

## Exceptions and false positives

- Compact line height can suit one- or two-line headings, buttons, and short UI text.
- Dense data may prioritize space if text remains usable and overrides do not hide/overlap content.
- Font metrics, writing systems, and line length affect perceived leading.
- A low numeric value/single-line heading does not prove a problem; a familiar token does not prove multi-line readability.

## Correction guidance

Identify affected role and user context. If longer text looks crowded, increase its leading or adjust size, measure, or font as appropriate; do not change every component to satisfy one ratio. Preserve compact leading for short roles and test wrapped/localized copy, font fallback, and enlargement. Run the WCAG user-override scenario and verify no loss of content/functionality.

## Independent research references

- [W3C WAI WCAG 2.2 text spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html) — user override, not authored default, and language/script applicability.
- [USWDS Typography](https://designsystem.digital.gov/components/typography) — role/length-sensitive line-height guidance.
- [W3C WAI Technique C21](https://www.w3.org/WAI/WCAG22/Techniques/css/C21) — line tracking technique and non-normative guidance.
- [Rello et al. — Make It Big!](https://pielot.org/pubs/Rello2016-Fontsize.pdf) — reading study with context-specific line-spacing results.