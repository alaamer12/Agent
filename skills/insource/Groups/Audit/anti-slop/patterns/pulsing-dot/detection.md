# Detection: Pulsing status dot

## Catalog route

The official catalog classifies this as a **source** rule. Animation source is a candidate; meaning, duration, state, and rendered timing require review.

## Candidate signals

1. Find repeating opacity/scale/glow keyframes or animation loops on small status indicators.
2. Identify the exact status and whether it is genuinely active/live or only decorative.
3. Inspect duration, flash characteristics, how many elements pulse, and whether the motion stops when the state changes.
4. Test reduced-motion behavior and accessible state labeling/programmatic updates.

## False-positive controls

- Do not flag every animated status or a purposeful transient state cue solely for pulsing.
- Distinguish smooth pulse from rapid flashing and assess applicable criteria separately.
- Do not rely on color/motion alone to explain the state.

## Test disposition

Source fixtures may find repeated pulse animations, with negatives for state-bound live activity and a static/reduced-motion fallback. Runtime tests must check actual timing/duration and reduced-motion behavior; regex cannot confirm harm.