# Detection: Extreme border-radius on cards

## Catalog route

This is one of the six **design-review** patterns. Do not create a numeric radius threshold: assess the rendered curve relative to component dimensions, content, role, and system guidance.

## Visual/contextual checks

1. Identify card boundaries and compare corner radius with card size and content insets.
2. Inspect crowding, clipping, nested curves, visual grouping, and whether different roles remain distinguishable.
3. Review small/large cards, dense/sparse content, narrow viewports, and relevant states.
4. Compare against the product’s shape tokens, component variants, platform conventions, and brand direction.

## Structural clues (candidate only)

`border-radius`, clipping/masking, radius tokens, and rounded media inside rounded cards can identify surfaces to inspect; they cannot establish whether a radius is excessive.

## False-positive controls

- Do not flag pills, circles, tags, or a deliberate rounded brand system as card violations.
- Do not assume every card should have a different shape; shared silhouette can indicate a component family.
- Do not invent a fixed pixel or ratio limit unsupported by the project’s design system.

## Test disposition

Not regex-confirmable. Visual calibration should cover content-crowded tiny cards, spacious large-radius cards, intentional pill/circle roles, and nested shapes with both balanced and pinched corners.