# Detection: Single font for everything

## Catalog route

This is a **design-review** pattern. Count of declared families cannot determine whether the type system has clear hierarchy or role fit.

## Visual/contextual checks

1. Review heading, body, label, and display roles in real rendered pages.
2. Assess hierarchy across size, weight, style, spacing, color, and placement.
3. Check family weights/styles, long-reading and display behavior, language coverage, and brand/editorial intent.
4. Decide whether an additional face would solve an observed role problem or merely increase complexity.

## Structural clues (candidate only)

One family token across many roles can locate screens for review; stylesheet counts cannot establish visual weakness.

## False-positive controls

- Do not require two or more typefaces.
- Do not assume that a single family implies flat hierarchy or poor readability.
- Do not infer quality from the number of `font-family` declarations alone.

## Test disposition

Not regex-confirmable. Visual calibration should include one family with clear hierarchy and one with actual role/weight limitations, plus a multi-family example whose hierarchy remains weak.