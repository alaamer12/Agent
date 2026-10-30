# Detection: Tiny body text

## Catalog route

The official catalog classifies this as a **source** rule. Assess sustained body paragraphs in rendered context; do not enforce a universal authored pixel minimum.

## Candidate signals

1. Identify long-form paragraph roles separately from labels, captions, footnotes, and dense data.
2. Inspect computed font size, actual font/fallback, relative units, inheritance, and responsive rules.
3. Review readability at representative widths and check contrast for actual foreground/background.
4. Test 200% text resize and WCAG text-spacing overrides for loss, clipping, or overlap.

## False-positive controls

- Do not flag by a universal CSS px cutoff.
- Do not treat a compact caption/data role as body-copy evidence.
- Do not equate small type with contrast failure or WCAG failure.
- Do not assume source values reflect user-adjusted rendered size.

## Test disposition

Source tests should include small body paragraphs, legitimate captions, compact data roles, and relative/responsive sizing. Browser tests assess actual readability, contrast, resizing, and spacing adaptation. Regex cannot confirm user impact.