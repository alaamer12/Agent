# Detection: Dark mode with glowing accents

## Catalog route

The official catalog classifies this as a **source** rule. Repeated glow/color tokens locate candidates; theme-aware visual review decides whether hierarchy or legibility is harmed.

## Candidate signals

1. Inspect supported dark-theme renders for number, placement, and strength of luminous accents.
2. Trace each accent to action/state/data roles and check consistency across components.
3. Evaluate text and meaningful control boundaries against rendered dark backgrounds.
4. If animated, inspect the actual timing/intensity and test the applicable flashing criterion.

## False-positive controls

- Do not flag a dark theme or purposeful state/focus accent by itself.
- Do not assume bright color is high-contrast for every foreground/background pair.
- Distinguish static glow from flashing animation.
- Source match cannot establish user discomfort or visual hierarchy.

## Test disposition

Source candidates can identify repeated glow declarations. Visual tests should include overused decorative neon, a restrained dark brand theme, and semantic focus/status accents; contrast and flashing are assessed independently. Regex cannot confirm.