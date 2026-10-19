# Detection: Unbalanced opening columns

## Catalog route

The official catalog classifies this as a **browser** rule. Runtime geometry and visual assessment are required; equal column heights are not a target.

## Browser checks

1. Inspect the actual opening at representative viewport widths with realistic content.
2. Compare column bounds, height, whitespace, content roles, and placement of the primary message/action.
3. Determine whether asymmetry supports grouping/focal hierarchy or leaves unexplained empty space.
4. At narrow widths, check reflow, overflow, clipping, and source/visual/keyboard order.

## False-positive controls

- Do not flag unequal column lengths, editorial asymmetry, or purposeful whitespace alone.
- Do not require an action to appear above the fold in every design.
- Do not infer a failure from a static source declaration or a desktop screenshot alone.

## Test disposition

Browser evaluation should include accidental long/short-column imbalance, purposeful editorial asymmetry, and responsive stacking with coherent reading order. Regex is not applicable to confirmation.