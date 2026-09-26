# Move 11: chart-junk removal

## The shape of the "before"

A chart carries visual elements that don't correspond to anything a reader needs to read off it: a marker on every single data point regardless of whether any of them are individually notable, more gridlines than needed to estimate a value, decorative fills, gradients, or 3D/bevel effects on the plotted shapes, axis labels at irregular or overly granular intervals, or a legend crowded directly onto the chart's shape (percentage labels stacked on thin donut slices) rather than given its own clear space.

Diagnostic question, applied to every visible mark on the chart one at a time: what specific number, comparison, or fact does this particular mark let a reader determine that they couldn't without it? If no answer comes to mind, that mark is chart-junk.

## The shape of the "after"

Keep only marks that pass the diagnostic question. In practice this usually means: enough gridlines/axis labels to estimate a value at a glance (not one per data point, not so few that estimation is impossible), the plotted line/bars/shape itself, and — often just one, sometimes a small few — a marker or annotation on whichever specific point is actually worth calling out (a peak, a low point, an anomaly, a target crossed), rather than a marker on every point uniformly. A legend states category names and, where useful, states the single most important derived fact in words as well (a peak value and when it occurred, a total, a percentage) so the chart doesn't require any decoding at all to get the headline — the shape is there for the reader who wants more detail than the sentence gives.

What makes this reasoning-driven rather than a fixed chart style:
- The right chart type (`[a line for a trend]` vs `[small multiples of bars for a comparison across many items]` vs `[a single ring/gauge for one proportion]` vs `[a table of exact numbers, when precision matters more than shape]`) depends on the question being answered (see move 1) — this move doesn't prescribe which chart type to use, only how to keep whichever type is chosen free of unjustified marks.
- "One marker, not one per point" is a strong default, not an absolute rule — a chart whose entire point is to let the reader compare every individual value precisely (a small, dense dataset where every point matters) may legitimately keep a marker on each one; the test is still "does each mark answer a question," and sometimes the answer for every point is yes.

## A minimal, illustrative sketch (not a template to copy)

```
[axis labels: only as many as needed to estimate a value, at round intervals]
[gridlines: same cadence as the axis labels, no finer]
[the plotted data itself: line, bars, or shape — whichever chart type answers
 the actual question being asked of this data]
[marker(s) or annotation: only where something specific is worth calling out
 by name, not by default on every data point]
[legend: category names, plus the single most important derived fact stated
 in words if there is one]
```
