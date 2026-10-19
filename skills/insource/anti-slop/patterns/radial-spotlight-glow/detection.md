# Detection: Soft spotlight behind content

## Catalog route

The official catalog classifies this as a **source** rule. Source inspection locates candidate gradients; rendered review determines whether emphasis is misdirected or useful.

## Candidate signals

1. Find radial gradients, gradient assets, image lighting, and their position/intensity.
2. Identify the intended focal content and compare it with the brightest/saturated area.
3. Assess competition with higher-priority text, actions, or imagery.
4. Measure text contrast at the least favorable point across the actual gradient and supported viewports.

## False-positive controls

- Do not flag every radial gradient or image spotlight.
- Distinguish a purposeful product/image highlight from a generic default flourish.
- Do not evaluate text contrast at one convenient point; gradients vary spatially.
- Source syntax cannot establish perceived emphasis or role.

## Test disposition

Source candidate tests can identify radial-gradient implementations; visual calibration must include correctly targeted lighting, a glow emphasizing secondary content, and subtle brand atmosphere. Contrast testing should sample worst-case rendered pairs. Regex cannot confirm.