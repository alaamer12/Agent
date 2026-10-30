# Detection: Heading closer to the previous section

## Catalog route

The official catalog classifies this as a **browser** rule. Evaluate the rendered grouping relationship, not only raw margin values.

## Browser checks

1. Identify the preceding section, heading, and following content in the rendered page.
2. Compare actual whitespace above/below the heading and check which content appears grouped with it.
3. Inspect representative widths, wrapped headings, and realistic content.
4. Trace computed margins/padding, line-height, spacing tokens, and margin collapse where relevant.

## False-positive controls

- Do not enforce a universal above/below spacing ratio.
- Do not treat close heading-to-content spacing as a problem; it normally supports grouping.
- Consider typography, dividers, and layout cues in addition to distance.
- Source margin declarations alone may not equal rendered spacing.

## Test disposition

Browser cases should include an incorrectly grouped heading, clear grouping with tight spacing, and margin-collapse versus flex/grid gap behavior. Regex is not applicable to confirmation.