# Detection: Gray text on colored background

## Catalog route

The official catalog classifies this as a **source** rule. Gray-on-color is a signal to measure contrast, not a categorical failure.

## Candidate signals

1. Locate text color and its effective background through tokens, cascade, opacity/alpha, gradients, images, and layers.
2. Determine text size/weight and whether any WCAG exception applies.
3. Measure the rendered pair in every relevant theme/state and at the lowest-contrast region for gradients.
4. Preserve source path, computed values, contrast ratio, and relevant text role.

## False-positive controls

- Do not flag by names such as `gray`, `muted`, or `colored` without measuring the pair.
- Do not test uncomposited base colors when opacity/layers apply.
- Do not treat secondary status as a WCAG exception.
- Do not assume palette membership guarantees contrast.

## Test disposition

Include positive low-contrast text on tinted surfaces and negatives for adequate gray/brand pairs, alpha-composited backgrounds, large-text thresholds, and a deliberately passing secondary role. Test the effective rendered colors; text regex is insufficient.