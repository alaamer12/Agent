# Detection: Wide letter spacing on body text

## Catalog route

The official catalog classifies this as a **source** rule. Positive tracking can locate candidates; rendered paragraph role, font, and script determine impact.

## Candidate signals

1. Find positive `letter-spacing` declarations/tokens applied to body paragraphs and trace inheritance/responsive scope.
2. Inspect computed value, font loading/fallback, script, font size, and actual word/letter gaps.
3. Review multi-line body copy at representative viewports and user text-spacing overrides.
4. Separate paragraph styles from uppercase labels/headings and brand treatments.

## False-positive controls

- Do not apply a universal positive-tracking threshold.
- Do not flag short display/uppercase roles solely for wider spacing.
- Do not assume Latin tracking behavior applies to cursive scripts.
- Do not treat WCAG override-test values as required authored defaults.

## Test disposition

Source tests should include widely tracked body paragraphs, a short tracked heading/label, and script-aware examples. Browser review confirms actual word grouping and resize behavior; regex cannot establish readability.