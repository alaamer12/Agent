# Detection: Low-contrast text

## Catalog route

The official catalog classifies this as a **source** rule. Source colors can identify candidates; confirmation requires measuring the effective rendered pair and applying the correct criterion.

## Candidate signals

1. Locate text/essential graphic colors and resolve cascade, tokens, opacity, alpha, images, gradients, and layers.
2. Identify text size/weight and applicable WCAG criterion/exception.
3. Measure rendered foreground/background pairs across themes, states, and variable backgrounds; sample the weakest relevant region.
4. For meaningful component/state boundaries or graphics, assess SC 1.4.11 separately from text contrast.
5. **State-algebra collisions (source candidate):** a control's reachable states are separate rendered pairs — resolve the cascade per state, not per resting rule. Signatures to raise as candidates:
   - a `:hover`/`:focus`/`:active` rule that sets `background` but not `color`, while the base rule's label color was written for the base background;
   - a `:disabled` rule that sets `color` (or removes an `opacity` wash) while a higher-specificity `:hover` rule sets `background` — disabled elements still match `:hover`, so the two rules compose into an untested pair;
   - `opacity`-based disabled styling on a filled button (label and background fade at different rates against the page);
   - theme-layer token re-points (`--ink*`, `--brand*`) where one consumer rule was tuned for the old value.
   For each, compute the composited ratio of every reachable state (rest/hover/focus/disabled/disabled+hover). The WCAG exception for inactive components covers `:disabled` at rest, NOT its hover-repaint collision, and never covers enabled controls.

## False-positive controls

- Do not flag by names such as `gray`, `muted`, `disabled`, or `bright` without checking applicability and rendered result.
- Do not assume a token pair represents the composited background.
- Do not apply non-text contrast to purely decorative edges.
- Do not infer a contrast ratio from a screenshot/color swatch alone.

## Test disposition

Accuracy tests should include text below/at thresholds, alpha-composited/gradient backgrounds, large-text cases, and exceptions; also cover essential versus decorative non-text graphics. Use a contrast calculation plus browser/runtime values; regex cannot confirm.