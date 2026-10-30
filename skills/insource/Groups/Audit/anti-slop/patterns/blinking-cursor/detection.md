# Detection: Decorative blinking cursor

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime interaction is needed to distinguish fake decoration from a native or truthful activity indicator.

## Browser checks

1. Locate visible cursor/caret shapes beside text and test whether they blink.
2. Check whether the text is actually editable and whether the caret tracks the insertion point/focus.
3. Confirm any live typing/activity state is genuine and ends when activity ends.
4. Test duration, reduced-motion behavior, Pause/Stop/Hide applicability, and rapid-flash criteria separately.

## False-positive controls

- Do not flag native insertion carets in focused editable controls.
- Do not treat every blink as a rapid flash or WCAG failure.
- Do not assume a cursor is functional based on its terminal-like appearance.

## Test disposition

Browser cases should include a fake cursor beside static text, a genuine focused input caret, and a real typing indicator that stops with activity. Verify reduced-motion and timing behavior; regex is not applicable to confirmation.