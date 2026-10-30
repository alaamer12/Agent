# Detection: Color outside DESIGN.md

## Catalog route

The official catalog classifies this as a **source** rule. A static out-of-palette match is candidate evidence and does not prove that the value is wrong or inaccessible.

## Candidate signals

1. Read the current `DESIGN.md` palette and ramps, plus the project token definitions and semantic roles.
2. Inspect authored CSS, CSS-in-JS, templates, and component styles for literal colors and token references. Resolve variables and imports before comparing values.
3. Trace each candidate to its intended role and state (default, hover, focus, disabled, success, error, etc.).
4. Record file, line, declaration, intended role, and closest documented token. Do not treat a color string found in an asset or unused stylesheet as applied UI evidence.

## Contextual confirmation

Check for approved brand updates, component-specific tokens, supported color modes, and documented exceptions. Verify computed colors in relevant states. Test rendered contrast pairs and color-dependent meaning separately; neither can be concluded from palette membership alone.

## False-positive controls

- Do not flag a semantic token or an intentional mode-specific value merely because it differs from the default palette.
- Do not assume hard-coded values are automatically harmful without identifying a shared token and actual usage.
- Do not treat a palette match as proof of accessible contrast, or an unmatched literal as proof of poor contrast.
- Regex can find literals but cannot resolve arbitrary CSS variables, runtime themes, or design intent by itself.

## Test disposition

Source-candidate evaluation is appropriate. Fixtures should cover an unlisted authored UI color, a documented semantic token, a supported theme/state override, unused/dead declarations, and an allowed value used in a poor contrast pair. Detector implementation and precision tests are pending.