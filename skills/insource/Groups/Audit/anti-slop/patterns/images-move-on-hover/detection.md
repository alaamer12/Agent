# Detection: Images that move on hover

## Catalog route

The official catalog classifies this as a **source** rule. Hover transforms are candidate signals; purpose, amount, and alternate input paths require runtime evaluation.

## Candidate signals

1. Locate `:hover` scale/translate/pan, pointer-driven image scripts, and hover-revealed overlays.
2. Inspect actual mouse/trackpad, keyboard focus, and touch behavior.
3. Determine whether movement serves detail inspection or is decorative; check crop/layout shifts and surrounding content.
4. Ensure essential detail/actions are available without hover and check reduced-motion behavior.
5. If additional content is revealed, test dismissible/hoverable/persistent requirements where applicable.

## False-positive controls

- Do not flag a purposeful, restrained zoom solely because it moves.
- Distinguish transforming an existing image from revealing additional content.
- Do not infer touch/keyboard behavior from a desktop screenshot.

## Test disposition

Source candidates can find hover transforms. Runtime fixtures should include purposeful image zoom with keyboard/touch alternatives, hover-only essential content, and restrained decorative motion with reduced-motion support. Regex cannot confirm harm.