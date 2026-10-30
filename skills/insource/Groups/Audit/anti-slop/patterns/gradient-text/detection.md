# Detection: Gradient text

## Catalog route

The official catalog classifies this as a **source** rule. `background-clip: text` or an SVG gradient is a candidate; contrast and readability require rendered evaluation.

## Candidate signals

1. Locate clipped backgrounds, transparent text fills, SVG gradient fills, and image-based text.
2. Record affected text, role, size, stroke weight, foreground gradient, actual backdrop, and fallback behavior.
3. Evaluate the weakest contrast across the entire gradient and relevant themes/states.
4. Test browser fallback and 200% resize; preserve semantic text when decorative techniques are used.

## False-positive controls

- Do not ban all gradient text or assume gradient styling implies low contrast.
- Apply the logo exception only to text that is part of a logo/brand name.
- Do not use average contrast when a portion of the gradient is materially weaker.

## Test disposition

Source candidates should include low-contrast gradient heading and a readable brand/display gradient with solid fallback. Visual/runtime evaluation must test weakest-area contrast, browser support, and resize behavior. Regex cannot confirm.