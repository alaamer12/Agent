# Justified text

**ID:** `justified-text`  
**Catalog section:** General quality  
**Official modality:** Source

## Definition and empirical evidence

Full justification aligns paragraph lines to both edges by expanding/contracting spacing; the final line is usually exempt. Word-spaced languages commonly adjust spaces between words, while other writing systems may use different conventions. Justification is a context-dependent typographic choice, not a universal defect.

## Underlying principle and potential harm

Assess actual rendered paragraphs at their width, font, language, and viewport. Uneven word gaps can form distracting “rivers” and make it harder for some readers to track/recognize word boundaries. Narrow or changing measures can also create awkward spacing/hyphenation. The alignment property alone does not establish a reading problem.

WCAG 2.2 SC 1.4.8 is a **Level AAA** criterion calling for a mechanism to change text presentation, including disabling justification. It is not a Level AA requirement or universal ban.

## Recognition signals

- Word gaps stretch conspicuously or form vertical rivers in actual paragraphs.
- Hyphen breaks/word spacing change awkwardly across responsive widths or font loading.
- Source clue: `text-align: justify`; inspect hyphenation, `lang`, and writing-system conventions too.
- CSS justification behavior is language-specific; declaration alone cannot predict final rendering.

## Causes to investigate

Possible causes include print layout carried into fluid UI; a narrow/variable text measure; unsuitable language-aware hyphenation; or applying full justification by default without checking browser output.

## Exceptions and false positives

- Books, newspapers, and magazines may use justified columns as deliberate editorial composition with controlled measure/hyphenation.
- Fixed-layout/document-like reading views may use justification if spacing remains acceptable and required user presentation controls exist.
- Justification differs by language/script; do not apply Latin word-spacing assumptions universally.
- A justified paragraph can render evenly; ragged-right text can also be hard to read. Judge the actual text and user context.

## Correction guidance

For ordinary responsive UI prose, prefer alignment to the text direction’s start edge and a natural rag. If justification serves a real editorial purpose, tune measure and language-aware hyphenation, inspect browser output across widths, and provide a way to remove justification when WCAG 1.4.8 applies. Do not alter letter spacing indiscriminately to hide poor word spacing; retest real text/fonts/scripts.

## Independent research references

- [W3C WAI WCAG 2.2 visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html) — Level AAA presentation control and rationale around rivers/spacing.
- [W3C CSS Text Level 3 — Text justification](https://drafts.csswg.org/css-text-3/text-justify-i18n/) — language/script-dependent justification behavior.
- [Harvard DAS — Readable paragraph text](https://accessibility.huit.harvard.edu/technique-paragraph-typesetting) — rivers, measure, and rendered readability.
- [Google Fonts Knowledge — Justification & hyphenation](https://fonts.google.com/knowledge/history_of_type/justification_hyphenation) — relationship between justification, hyphenation, and readability.