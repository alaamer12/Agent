# Detection: Font outside DESIGN.md

## Catalog route

The official catalog classifies this as a **source** rule. A source match is candidate evidence only; it cannot confirm that the design choice is wrong.

## Candidate signals

1. Read the project’s current `DESIGN.md` and extract the named typography roles, families, and tokens.
2. Inspect applicable CSS/SCSS, CSS-in-JS, template, and component declarations for `font-family`, font variables, `@font-face`, and inline values.
3. Resolve inheritance and imported tokens before comparing authored choices. Treat generic and fallback stack members separately from the preferred family.
4. For a candidate, record the exact source path and declaration plus the documentation section/token it differs from. Do not report only a family-name search hit.

## Confirmation requires context

Check whether the design document is stale, whether the family is an approved brand or role-specific choice, and whether the font is actually rendered after loading. A computed-style check can validate runtime rendering, but still cannot decide whether the deviation is intentional.

## False-positive controls

- Do not flag documented fallbacks as independent deviations.
- Do not assume that a design system permits only one family.
- Do not equate a font mismatch with an accessibility failure.
- Do not promote a regex/text match to a confirmed finding.

## Test disposition

Source-candidate detector is appropriate to evaluate. Positive fixtures should include an undeclared authored family; negative fixtures should cover a declared role token, an allowed fallback stack, and a documented role-specific family. The implementation and accuracy test are pending; the source signature remains unconfirmed until those tests run.