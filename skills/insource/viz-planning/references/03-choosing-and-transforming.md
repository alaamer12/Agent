# Choosing and Transforming

Covers: choosing the visualization, relationships between data points, grouping, "Others", aggregation, data reduction & progressive disclosure, discoverability of hidden/aggregated data, outlier detection & representation, and why filtering/grouping/aggregation/"Others" are four different operations.

These are mostly **chart-specific** decisions — made per chart, informed by the global decisions in files 01–02.

---

## Choosing the visualization

Not "take the data and make some charts" — the chart should follow from: what the data represents, what question is being answered (see `02-semantics-and-intent.md`), how many dimensions and categories are involved, the relationships between points, how much redundancy there is, and what comparison the viewer actually needs to make.

Concretely: if a dataset has many independent metrics across several entities, a **table** (rows = entities, columns = metrics) is often clearer than a wall of separate charts, because it makes direct comparison trivial:

```
             Metric A   Metric B   Metric C   Metric D
Model A         82         91         73         88
Model B         79         94         71         86
Model C         84         89         75         90
```

Always ask: **does a chart actually communicate this better than a table (or a number, or a sentence)?** Defaulting to "chart" when a table or a single stat would serve the reader better is a common failure mode.

### Default to fewer charts, not more

A working visualization engineer's instinct runs opposite to "make a chart for everything measurable." Before adding another chart to a dashboard or report, ask:

- Could this be a second series/line on an existing chart instead of a new one?
- Could it be a facet, a filter, or a toggle on an existing chart instead of a separate view?
- Could a table row or a single annotated number carry it instead of a full chart?
- Does this actually answer a different question than an existing chart, or just re-slice the same answer?

Ten small charts that each require the reader to hold context across all of them communicate less than one well-chosen chart that puts the comparison in a single field of view. If a chart list starts looking like "one chart per column in the source data" rather than "one chart per question the audience needs answered," that's the signal to consolidate, not to keep adding.

### Match chart type to audience literacy

Chart choice isn't purely a function of the data's shape — it's a function of what the specific audience in front of it can correctly read in a few seconds, and that depends heavily on who they are:

- **General / non-technical audiences** — reliably read bar charts, line charts, and pie charts (for a small number of categories) with no onboarding needed. Default to this family for public-facing reports, executive summaries, or anything a lay audience sees without someone there to walk them through it.
- **Data-literate audiences** (analysts, engineers, researchers) — can correctly read scatter plots, box plots, heatmaps, violin plots, and small multiples, and these are often genuinely more information-dense or more honest about a distribution's actual shape than a bar/line/pie equivalent.

The mistake to avoid: picking the more sophisticated chart because it's more information-dense or more statistically "correct," then handing it to an audience that can't read it. A box plot is a better representation of a distribution's spread than a bar chart of the mean — but if the audience doesn't already know how to read a box plot, a bar chart of the mean with a plainly-labeled range is the one that actually lands. When the audience is uncertain or mixed, default to the more universally legible chart family; if the denser view is still valuable, offer it as a drill-down from the simple one (see "Data reduction and progressive disclosure" above) rather than leading with complexity.

## Relationships between data points

- **Independent** (e.g. separate products) — each item can be compared on its own; order usually doesn't carry meaning.
- **Sequential** (`N-2 → N-1 → N`) — order itself is part of the meaning.
- **Continuous** (`10 → 12 → 15 → 18 → 21`) — the relationship between *neighboring* values matters, not just each value alone.
- **State transitions** (`State N-1 → State N → State N+1`) — that N happened after N-1 is meaningful, not incidental.

This determines whether a bar chart, a line, a table, or a state/flow diagram is the right shape.

## Grouping, "Others", and aggregation — three different operations

These get conflated constantly. They are not interchangeable:

**Grouping** creates meaningful buckets out of individual values to reduce granularity while preserving structure:
```
1, 2, 3, 4, 5, 6, 7, 8 ...  →  0–5, 5–10, 10–15, 15–20, ...
```
Applies to numbers (bin width), dates (day/week/month), or categories (rolling up subcategories). Decide: is the interval configurable, can the system pick a sensible default automatically, are boundaries inclusive/exclusive, and can a group be expanded to see its underlying records?

**"Others"** aggregates categories that are individually too small to justify their own slot:
```
A 35%  B 25%  C 15%  D 8%  E 5%  Others 12% (= F + G + H + I + J + ...)
```
The categories folded into "Others" don't need any natural relationship to each other — unlike grouping, this is purely about display budget, not about meaningful buckets.

**Aggregation** reduces multiple raw points into one summary value — sum, average, count, min, max, median, percentage. Grouping and aggregation typically work together (group ages into 5-year bins, *then* count people per bin) — but they're still two separate steps, and "Others" is a third, separate concept layered on top of either.

## Data reduction and progressive disclosure

A chart with 50 pie slices is unreadable regardless of how correct the data is. Decide the reduction strategy: Top-N, a percentage threshold, an absolute-value threshold, or something driven by available screen space. Then decide whether a focused entity (see `02-semantics-and-intent.md`) should always stay visible even if it would otherwise fall below the cutoff.

**Critical constraint: reducing visual complexity should never permanently remove access to the data.** If something is grouped, "Others"-ed, or hidden for readability, define how a curious user gets to it:

- expand in place (e.g. clicking "Others" reveals its constituent categories)
- open a more detailed chart or a table
- show the underlying values as text/tooltip
- switch chart type — e.g. a pie chart for overall composition, and a bar chart for examining what's inside "Others"

If there's no answer to "how does the user get back the detail," the reduction is data loss dressed up as design, not a design decision.

### The same reduction applies to time range, not just category count

A year of daily data plotted at full resolution has the same problem as a 50-slice pie chart — it's technically all there, and practically unreadable. Check Step 1's output for the actual span of any timestamp field before deciding: a chart doesn't need to default to showing everything just because everything is available.

- **Pick a sensible default window** rather than "all of it": recent-N (last 30/60/90 days), or the full span at a coarser rollup (daily → weekly → monthly) if the long-term trend is the point.
- **Match the window to the question**: "what happened recently" wants a short recent window at full resolution; "how has this trended over the year" wants the full span, aggregated, not the full span at daily resolution.
- **Keep the rest reachable**: a date-range picker, a zoom/brush control, or a "view full history" link — the same discoverability principle as "Others" above. Defaulting to a smaller window is a readability choice, not a decision to delete the rest of the data.

## Outlier detection and representation

This deserves being treated as three separate decisions, not one:

**1. Detection** — what method, and is it configurable? Options include IQR, Z-score, modified Z-score/MAD, plain standard deviation, or a domain-specific threshold. Also decide what happens when the dataset is too small or unsuited to whichever method is chosen (small-N stats can flag normal variation as "outliers").

**2. Representation** — if outliers are kept visible, how are they distinguished? Options (combinable, and combining them helps accessibility): a different color, a different shape (e.g. circles for normal points, squares for outliers), a dedicated legend entry, and the original value still reachable via tooltip/label.

**3. Participation in calculations** — this is the one most likely to silently produce a misleading chart if left undecided:
- **Included** — outliers still count toward means, trend lines, axis scales, aggregates.
- **Excluded** — outliers are shown but don't affect the math.
- **Optional** — user/config toggles it.

If excluded, the visualization should make that visible (e.g. "average excludes N outliers") rather than silently presenting a filtered statistic as if it were the full picture. And separately: if outliers are hidden entirely rather than just deprioritized, can the user still discover how many there were and inspect their actual values — a toggle, a count, a drill-down table?

Detecting an outlier, visually representing it, and excluding it from calculations are three independent choices — deciding one doesn't decide the others.

## Filtering, grouping, aggregation, reduction — keep them conceptually separate

| Operation | What it does |
|---|---|
| Filtering | removes data from the current view entirely |
| Grouping | buckets individual values into meaningful ranges |
| Aggregation | summarizes multiple values into one (sum/avg/count/etc.) |
| "Others" | folds low-importance categories together for display budget |
| Progressive disclosure | keeps data available but initially hidden |

They compose freely, but naming which one is actually happening avoids building the wrong control for the job (e.g. a "filter" UI when what's actually needed is a grouping-interval control).
