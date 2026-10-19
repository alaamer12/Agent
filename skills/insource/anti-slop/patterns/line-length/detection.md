# Detection: Line length too long

## Catalog route

The official catalog classifies this as a **browser** rule. Evaluate rendered measure and reading behavior; a character-count heuristic is not a conformance threshold.

## Browser checks

1. Inspect real running prose at representative wide/narrow viewports and supported font settings.
2. Measure rendered line width/characters as a clue; consider font, language, size, and line height.
3. Separate prose from headings, code, tables, and other structured content.
4. Test zoom/reflow and unintended horizontal scrolling; inspect whether any horizontal scroll is intentionally confined to a table/code block.

## False-positive controls

- Do not enforce one universal character count.
- Do not apply the Level AAA SC 1.4.8 criterion as a Level AA limit.
- Do not flag code/table width without assessing need and responsive access.
- A CSS width or screenshot alone cannot establish actual reading difficulty.

## Test disposition

Browser cases should include wide prose with difficult line returns, a readable broad measure, and intentionally wide table/code blocks with usable confined scrolling. Regex is not applicable to confirmation.