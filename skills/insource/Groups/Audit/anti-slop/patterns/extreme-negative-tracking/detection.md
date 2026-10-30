# Detection: Crushed letter spacing

## Catalog route

The official catalog classifies this as a **source** rule. A negative `letter-spacing` declaration is candidate evidence; its appearance depends on the rendered font, role, size, script, and text.

## Candidate signals

1. Locate negative tracking in CSS, CSS-in-JS, component styles, and tokens; record exact source and role.
2. Resolve inheritance and relative units; inspect computed tracking after the actual font has loaded and in fallback states.
3. Review actual glyph shapes/text at relevant sizes and writing systems for crowding/merging.
4. Test the user text-spacing override criterion independently of the author’s chosen value.

## False-positive controls

- Do not flag all negative tracking or enforce a universal numeric threshold.
- Do not assume the same value has the same visual effect across typefaces/scripts.
- Do not confuse WCAG override-test values with required defaults.

## Test disposition

Source tests can flag an extreme negative candidate and include negative fixtures for a short display title, a different face, and script-aware styles. Visual/runtime tests must assess legibility and font fallback; regex cannot confirm.