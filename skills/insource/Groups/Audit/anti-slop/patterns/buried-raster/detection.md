# Detection: Images hidden under overlays

## Catalog route

The official catalog classifies this as a **source** rule. Overlay code is a candidate; rendered subject visibility and text contrast require visual evaluation.

## Candidate signals

1. Locate image+scrim layers, opacity/blend effects, gradients, and responsive crop/focal-position rules.
2. Inspect the rendered image and overlay together across viewport sizes/themes/content variants.
3. Check subject/focal visibility, text contrast where text lands, and whether overlay purpose fits image role.
4. Distinguish decorative imagery from informative image content and verify appropriate alternatives separately.

## False-positive controls

- Do not flag all hero scrims or tinted images; they may support readable text.
- Do not assume a semitransparent value has the same visual effect across images/crops.
- Do not use alt text as a fix for visually hidden information.

## Test disposition

Source candidates can identify overlay layers. Visual tests should include a useful localized scrim, an overlay that hides the subject, and responsive crop changes that preserve/lose focal detail; measure rendered text contrast. Regex cannot confirm.