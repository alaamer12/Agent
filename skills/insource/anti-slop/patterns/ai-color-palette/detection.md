# Detection: AI color palette

## Catalog route

The official catalog classifies this as a **source** rule. Purple/cyan colors or gradient syntax identify a candidate for review, not an anti-pattern by themselves.

## Candidate signals

1. Inventory applied colors/gradients and trace their tokens, roles, and theme modes.
2. Review multiple screens for repeated generic treatments and compare with the product’s documented brand/user/task context.
3. Inspect actual rendered hierarchy and text/background pairs; assess non-text cues for meaningful states.
4. Record exact occurrences and the specific contextual mismatch rather than “purple detected.”

## False-positive controls

- Do not ban purple, violet, cyan, gradients, or dark surfaces by name.
- Do not assume novelty is better than a coherent brand palette.
- Do not equate palette membership with accessibility; measure rendered combinations separately.
- Source color strings cannot establish user association or intent.

## Test disposition

Source fixtures may identify repeated purple/cyan defaults as candidates; negatives should include an intentional accessible brand palette. Visual/context tests must assess product fit and hierarchy. Regex cannot confirm a generic or inappropriate palette.