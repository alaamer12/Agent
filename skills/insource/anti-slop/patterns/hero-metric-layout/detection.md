# Detection: Hero metric layout

## Catalog route

This is a **design-review** pattern. Large numbers, stat cards, and count-up effects cannot establish whether a metric is useful, accurate, or misleading.

## Visual/contextual checks

1. Identify the metric’s audience and the page question it is meant to answer.
2. Verify label, unit, scope/denominator, timeframe, source, and freshness.
3. Check whether comparison/target is meaningful and valid; interpret direction correctly.
4. Inspect hierarchy and whether the figure is a focal data point or decoration.
5. Determine whether nearby controls/detail provide the necessary context.

## Structural clues (candidate only)

Large numeric typography, stat-card components, charts, and count-up animation can locate candidates for review but cannot assess metric validity or user interpretation.

## False-positive controls

- Do not flag large type, KPI cards, or data-led heroes solely for prominence.
- Do not force benchmarks/positive direction when none is meaningful.
- Do not infer a false claim without tracing metric definition and source.

## Test disposition

Not regex-confirmable. Visual cases should include a well-labeled operational KPI, a substantiated data-led hero, and an ambiguous/unsubstantiated large number with misleading comparison or direction.