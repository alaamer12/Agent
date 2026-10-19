# Detection: Animation that changes layout

## Catalog route

The official catalog classifies this as a **source** rule. Geometry-changing animation is a candidate signal; performance and user impact require runtime profiling.

## Candidate signals

1. Locate animations/transitions of size, position, margin, padding, or other layout-affecting properties.
2. Trace scope: identify nearby elements that reflow or shift during the transition.
3. Profile layout/paint/frame timing during repeated, reversed, and interrupted interactions.
4. Determine whether the desired behavior is genuine flow change (e.g. disclosure) or visual-only movement.
5. Test reduced-motion, keyboard, and final-layout behavior.

## False-positive controls

- Do not label a geometry property slow without runtime profiling.
- Do not replace meaningful flow transitions with transforms if they overlap content or fail to reserve space.
- Do not equate intentional movement with CLS; distinguish expected transition from unexpected shift.

## Test disposition

Source fixtures can locate geometry transitions. Runtime cases should compare an unnecessary large relayout with a meaningful accordion and a transform/FLIP transition, profiling representative devices and reduced-motion behavior. Regex cannot confirm performance impact.