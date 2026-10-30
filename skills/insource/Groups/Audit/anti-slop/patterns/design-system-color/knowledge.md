# Color outside DESIGN.md

**ID:** `design-system-color`  
**Catalog section:** Your design system  
**Official modality:** Source

## Definition and empirical evidence

Impeccable compares literal colors in the implementation with the project palette and companion tonal ramps documented in `DESIGN.md`. The supplied local description explicitly allows legitimate new colors but expects them to be intentional design-system additions rather than unexplained drift.

## Underlying principle and potential harm

Use the documented semantic color vocabulary for established roles, and keep that vocabulary aligned with approved product and brand decisions. Unreviewed literals can produce inconsistent role colors and make palette-wide changes harder than updating shared tokens. Conversely, being in the palette does not guarantee an accessible foreground/background combination: accessibility is determined by the rendered pairing and how information is conveyed.

## Recognition signals

- A literal color or new token appears outside the documented palette or tonal ramps.
- A component bypasses an available semantic token for its role.
- A new value is used across hover, focus, error, disabled, or other states without corresponding documented relationships.
- Light/dark modes or system color-scheme preferences produce unreviewed computed colors.
- Contrast or color-only communication problems appear in rendered states, regardless of token membership.

## Causes to investigate

Possible causes include stale design documentation after a brand update; hard-coded one-off styling instead of an existing semantic token; a missing component/state color; or a mode-specific value added without documenting its role and tonal relationships. These are hypotheses, not proof from an out-of-list color.

## Exceptions and false positives

- Design systems commonly have semantic theme and state colors in addition to a smaller product-specific palette.
- An approved brand/system change may make the document stale rather than the code wrong.
- Light/dark themes may deliberately choose distinct values for the same role.
- A new tone or component-specific value can be appropriate when its purpose, supported modes, accessible combinations, and scope are explicit.
- Palette membership and accessibility are separate: an allowed token may still be used in a low-contrast pairing, while a new color may be accessible.

## Correction guidance

Confirm current brand decisions with the design owner, then compare source values, `DESIGN.md`, token definitions, and supported modes. Replace accidental literals with the semantic token for the intended role. For a legitimate addition, record its role, scope, modes, and required tonal relationships, and promote it to a shared token where reuse is intended. Test applicable text/non-text contrast in every supported mode and ensure information is not communicated by color alone. Keep any exception narrow and justified.

## Independent research references

- [Impeccable context files](https://impeccable.style/docs/context) — comparison against the project's declared palette and keeping design records current.
- [USWDS color tokens overview](https://designsystem.digital.gov/design-tokens/color/overview) — system, theme, and state color-token organization.
- [VA Design System tokens](https://design.va.gov/foundation/design-tokens) — primitive versus semantic tokens and why references help maintain changes.
- [W3C WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref) — contrast and the requirement not to rely on color alone.
- [MDN `color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/color-scheme) — browser/system light and dark scheme behavior.