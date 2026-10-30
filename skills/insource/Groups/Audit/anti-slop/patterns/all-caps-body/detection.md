# Detection: All-caps body text

## Catalog route

The official catalog classifies this as a **source** rule. Uppercase body copy is a candidate for review, not an automatic readability/accessibility violation.

## Candidate signals

1. Identify paragraphs/text-heavy elements whose rendered text is all uppercase.
2. Trace authored casing versus CSS `text-transform`; record source text, language, semantic role, and component.
3. Distinguish body paragraphs from short labels, acronyms, controls, brand marks, and display headings.
4. Inspect localized casing and rendered text-spacing/resize behavior where relevant.

## False-positive controls

- Do not flag short labels, acronyms, wordmarks, or brief display text solely for uppercase.
- Do not assume English casing rules apply to all languages/scripts.
- Do not infer screen-reader semantics solely from CSS presentation.
- Do not cite WCAG spacing as a ban on uppercase.

## Test disposition

Source candidates can test long all-caps paragraphs versus short labels, acronyms, and proper source casing with CSS transformation. Visual/context review should evaluate scanning and readability; regex cannot confirm user impact.