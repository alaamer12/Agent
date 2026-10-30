# Animation that changes layout

**ID:** `layout-transition`  
**Catalog section:** Motion  
**Official modality:** Source

## Definition and empirical evidence

This signal concerns animating size or spacing in a way that shifts nearby content or may stutter. Geometry-changing properties can require layout/reflow and paint; `transform`/`opacity` are often compositor-optimizable. The property alone does not prove poor performance or harm.

## Underlying principle and potential harm

First decide whether the interaction should change document flow or only visual position. Unnecessary layout/paint work can miss frame budgets and stutter, particularly for large/complex layouts or constrained devices. Nearby movement can interrupt reading or obscure targets. CLS concerns unexpected movement; a gradual intentional transition can help users understand a state change.

## Recognition signals

- Animated `width`, `height`, `top`/`left`, margins, padding, or other geometry shifts neighbors during playback.
- Text wraps/reflows during motion, or content jumps/stutters on representative devices.
- Broad `transition: all` or large page regions animate without profiling.
- Runtime behavior on repeated/reversed interactions matters; source property scans cannot show actual cost/context.

## Causes to investigate

Possible causes include animating flow properties for visual-only movement; transitioning a large region; using broad property transitions; or adding meaningful layout motion without tuning its scope/duration.

## Exceptions and false positives

- Accordion/disclosure expansion can intentionally reveal content by changing height.
- Real flow changes may be more faithful than translating content over an unchanged layout.
- FLIP or View Transitions can animate between actual layout states using visual transforms.
- Transforms are not always a safe substitute if they overlap content or fail to reserve final space.
- Interaction-triggered motion may need reduced-motion treatment; WCAG’s animation-from-interactions criterion is Level AAA.

## Correction guidance

Decide whether the desired effect is true flow change or visual-only movement. For visual-only effects, consider transform/opacity; for meaningful reflow, limit scope/duration and profile on representative devices. Consider FLIP/View Transitions where appropriate. For accordions, use supported intrinsic-size techniques or robust alternatives. Test reduced motion, keyboard operation, text wrapping, and final layout; avoid introducing overlap while eliminating reflow.

## Independent research references

- [web.dev — Animations and performance](https://web.dev/articles/animations-and-performance) — layout/paint cost and compositor-friendlier transform/opacity.
- [web.dev — Cumulative Layout Shift](https://web.dev/articles/cls) — unexpected versus gradual intentional movement and reduced-motion guidance.
- [Chrome — Animate to `height: auto`](https://developer.chrome.com/docs/css-ui/animate-to-height-auto) — intrinsic-size transitions for disclosure/accordion patterns.
- [CSS-Tricks — FLIP technique](https://css-tricks.com/animating-layouts-with-the-flip-technique/) — transform-based visual interpolation between final layouts.
- [Chrome — View Transition API](https://developer.chrome.com/docs/web-platform/view-transitions) — transitions between rendered states.