# Detection: Border accent on rounded element

## Catalog route

The official catalog classifies this as a **source** rule. Source code can locate a border style; only contextual/visual review can decide whether its communication is redundant or useful.

## Candidate signals

1. Inspect selectors/components for prominent colored borders on rounded surfaces; capture exact declarations and affected roles.
2. Compare occurrences across equivalent cards and distinguish default, hover, focus, selection, error, warning, and success states.
3. Check the component’s interaction and whether the boundary communicates grouping or clickability.
4. For meaningful UI/state boundaries, measure rendered adjacent-color contrast; do not infer it from a color-name match.

## Contextual confirmation

Ask what the accent means and whether users can perceive the same state through text, icon, shape, or behavior. Confirm brand/component guidance and inspect keyboard focus in the rendered UI.

## False-positive controls

- Do not flag status, selected, focus, validation, or interactive-card boundaries solely for being colored.
- Do not assume every card requires or should lack a border.
- Do not apply non-text contrast to decorative lines that convey no required information.
- Regex detecting `border`/color/radius cannot establish intent or visible result.

## Test disposition

Source-candidate tests should include generic decorative accents and legitimate semantic state borders, with negative fixtures for non-rounded/state-specific treatments. Visual evaluation must determine hierarchy and semantics; no regex hit is a confirmation.