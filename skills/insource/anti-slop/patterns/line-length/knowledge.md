# Line length too long

**ID:** `line-length`  
**Catalog section:** Layout & Space  
**Official modality:** Browser

## Definition and empirical evidence

This rule identifies running text whose long measure may make it harder to return to the next line. The catalog’s roughly 80-character heuristic is a review prompt, not a universal cutoff. Text measure should suit role, typeface, language, and reading conditions.

## Underlying principle and potential harm

Long lines can make line returns harder to track; suitable line height may help. Research does not show that longer lines invariably slow on-screen reading, and results/preferences vary. Character count alone does not establish harm.

WCAG 2.2’s 80-character (40 CJK) text-width provision is part of Level AAA SC 1.4.8 and requires a user-available presentation mechanism. It is not a universal Level AA limit. Level AA reflow is separate and concerns avoiding content loss/two-dimensional page scrolling at specified narrow widths, with limited exceptions for genuinely two-dimensional content.

## Recognition signals

- Long-form prose spans most of a wide viewport and line returns are difficult to follow.
- Line height and paragraph grouping do not support reading at the current measure.
- Fixed widths or whitespace rules prevent fluid wrapping or reflow.
- Source clues include text-container width/max-width and responsive/overflow rules; character count changes with font, size, and script.

## Causes to investigate

Possible causes include prose inheriting a full-width grid column; a layout optimized for desktop balance rather than reading; fixed dimensions that fail at zoom/small viewports; or one container rule applied to prose, tables, and code alike.

## Exceptions and false positives

- Tables may need width to preserve data comparisons; check their responsive strategy.
- Code may contain logical long lines; any horizontal scrolling should be appropriate to the content and preferably confined to the block.
- Short headings/alerts/captions and large display text can use a different measure.
- A measure outside a heuristic may be readable with suitable typography; a short measure can also feel awkward.
- Do not turn a Level AAA criterion or content-specific exception into a universal AA rule.

## Correction guidance

Separate long-form prose from code, tables, and short UI text. If prose is unnecessarily wide, use a responsive max measure and tune line height; keep the layout fluid at small sizes. Preserve useful structure for tables/code and allow block-level horizontal scrolling only where warranted. Verify real content, fonts/languages, narrow viewports, and text enlargement rather than counting characters alone.

## Independent research references

- [USWDS Typography](https://designsystem.digital.gov/components/typography) — 45–90-character guidance, 66-character long-text target, and role/line-height qualifications.
- [Mary Dyson — Line length revisited](https://designregression.com/article/line-length-revisited-following-the-research) — reading evidence is conditional; long lines do not invariably slow reading.
- [W3C WAI WCAG 2.2 visual presentation](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html) — 80/40-character line-width provision is Level AAA and user-mechanism based.
- [W3C WAI WCAG 2.2 reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) — narrow-width reflow and two-dimensional content exception.
- [A List Apart — Web Typography: Designing Tables to be Read](https://alistapart.com/article/web-typography-tables) — tables need different width treatment from prose.