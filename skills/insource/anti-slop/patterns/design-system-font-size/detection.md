# Detection: Font size outside DESIGN.md

## Catalog route

The official catalog classifies this as a **source** rule. A textual value outside a listed scale is candidate evidence only; fluid computed values and user settings need contextual/runtime review.

## Candidate signals

1. Extract documented sizes by text role, including approved component and responsive variants.
2. Inspect CSS/SCSS, CSS-in-JS, templates, and token files for authored font sizes and unresolved literals.
3. Trace `var()`, inheritance, relative units, `clamp()`, media/container queries, and component props before comparing values.
4. Record the declaration, role, token/scale entry it differs from, and affected route/component.

## Contextual confirmation

Inspect computed sizes at supported breakpoints, zoom levels, and user font-size settings. Test 200% text resizing and WCAG text-spacing overrides for lost content/functionality. A source match cannot establish those runtime outcomes.

## False-positive controls

- Do not flag fluid intermediate values or role-specific sizes without checking the documented system.
- Do not equate token mismatch with a WCAG failure.
- Do not treat a documented token as proof that resizing and spacing work.
- Regex can locate literal values, but cannot resolve full cascade, computed sizing, or user preferences.

## Test disposition

Source-candidate tests should include an unexplained unlisted size; a documented role token; a `clamp()`/relative responsive size; a component-specific variant; and layouts that pass/fail user resize and spacing overrides. Detector implementation and accuracy evaluation are pending.