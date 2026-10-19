# Detection: Low-contrast text

## Catalog route

The official catalog classifies this as a **source** rule. Source colors can identify candidates; confirmation requires measuring the effective rendered pair and applying the correct criterion.

## Candidate signals

1. Locate text/essential graphic colors and resolve cascade, tokens, opacity, alpha, images, gradients, and layers.
2. Identify text size/weight and applicable WCAG criterion/exception.
3. Measure rendered foreground/background pairs across themes, states, and variable backgrounds; sample the weakest relevant region.
4. For meaningful component/state boundaries or graphics, assess SC 1.4.11 separately from text contrast.

## False-positive controls

- Do not flag by names such as `gray`, `muted`, `disabled`, or `bright` without checking applicability and rendered result.
- Do not assume a token pair represents the composited background.
- Do not apply non-text contrast to purely decorative edges.
- Do not infer a contrast ratio from a screenshot/color swatch alone.

## Test disposition

Accuracy tests should include text below/at thresholds, alpha-composited/gradient backgrounds, large-text cases, and exceptions; also cover essential versus decorative non-text graphics. Use a contrast calculation plus browser/runtime values; regex cannot confirm.