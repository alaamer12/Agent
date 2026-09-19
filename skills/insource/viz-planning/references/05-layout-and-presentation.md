# Layout and Presentation

Covers: chart layout and dashboard structure, how a chart is presented, legends, long-text handling, color and visual encoding.

Dashboard-level layout is **global**; how an individual chart is framed, legended, and colored is largely **chart-specific**, though color semantics should stay consistent across the whole dashboard.

---

## Chart layout and dashboard structure

- How many charts, and how are they arranged — a grid? Fixed or responsive?
- How many per row, and does that change with viewport size?
- Can charts be resized or reordered by the user (e.g. drag-and-drop)?
- Can the user pan around a dashboard too large to fit on screen at once?

These are worth deciding before individual charts are built, since chart sizing/aspect-ratio choices downstream depend on the grid they'll sit in.

## How a chart is presented

A chart is rarely just the chart. Decide what wraps it, per chart (not necessarily the same answer for every chart on a dashboard):

```
Chart
  → Title + Chart
    → Title + Description + Chart
      → Category + Title + Description + Chart
```

And separately:
- Does it need a visible data source / "as of" freshness indicator?
- Does it need units shown explicitly (axis label, subtitle)?
- Does it need annotations calling out specific points?

## Legends

If the chart has more than one series, it likely needs a legend. Decide:
- Position — inside the chart area, or outside (top/bottom/left/right), or adaptive to available space?
- Interactive or static — can clicking a legend entry hide/isolate that series, or is it purely a key?

Legends aren't needed for single-series charts — including one anyway just adds visual noise without adding information.

## Long text handling

Long category names, labels, or titles break layouts if this isn't decided up front:

- **Truncate + tooltip** — show a shortened label, full text on hover.
- **Wrap** — let the label take multiple lines.
- **Move/rotate** — rotate axis labels, or move them outside the plot area.
- **Resize** — let the chart itself grow to accommodate.

Pick one strategy per label type (axis labels vs. legend entries vs. tooltip content can reasonably use different strategies) rather than letting whichever renderer's default behavior happens to apply.

## Color and visual encoding

The more important question isn't "what's the palette" — it's **what does each color mean, and is that meaning held consistent across the whole dashboard.** E.g.:

```
Blue  → the focused/target entity
Green → positive
Red   → negative
Gray  → neutral / close
```

If blue means "the target" on one chart and something else on the next chart in the same dashboard, that inconsistency actively works against the viewer's ability to read the dashboard quickly. Decide:
- Is color assigned to categories (a fixed category → color mapping used everywhere) or to values (a scale, e.g. a heatmap)?
- Is color semantic (meaning-bearing, as above) or purely decorative/distinguishing?
- How are many categories handled once a reasonable, distinguishable palette (roughly 8–12 hues before colors become hard to tell apart) is exhausted — pattern/texture, grouping into "Others," or a different chart type entirely?
- Does the dashboard support multiple themes (light/dark), and if so, do semantic color meanings need theme-specific variants to stay legible and keep the same relative meaning?
