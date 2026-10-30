# Plumbing and Failure Handling

Covers: input formats and conversion, performance and caching, interactivity (depth), failure and unexpected-data behavior, and global vs. chart-specific feature scoping.

Mostly **global** architecture decisions, plus one recurring principle (the last section) for scoping every other decision correctly.

---

## Input formats and normalization

If the system accepts more than one input format (CSV, JSON, Parquet, a live API, etc.), the question isn't only "can it read all of these" — it's whether there's an actual normalization layer so downstream visualization logic operates on one consistent internal representation:

```
CSV ────────┐
JSON ───────┤
Parquet ────┼──→ normalization → internal representation → visualization
URL / API ──┘
```

Without this layer, every chart component ends up with format-specific branches sprinkled through it, which is exactly the kind of thing that breaks quietly when a new source format shows up later.

## Performance and caching

- Will raw data be cached? Will *parsed* data be cached separately from raw? Will *transformed* (grouped/aggregated) data be cached separately again? These are three different cache layers with different invalidation needs.
- Could a local store (even just SQLite) hold processed/query-able data instead of re-parsing the source every time?
- For growing data: can only the delta since last load be fetched and processed, rather than reprocessing everything?
- Can expensive transformations (heavy aggregations, joins) be reused across requests rather than recomputed per view?

```
First read: load → parse → transform → store processed form
Next read:  read cached processed form directly
```

For continuously growing sources specifically:
```
Initial load → cache → new source data arrives → calculate delta
   → process only the delta → update cache → update visualization
```

If volume (`01-data-foundations.md`) is large or growing, treat this as a required design step, not an optimization to defer — retrofitting caching after the fact usually means restructuring how data flows through the system, not just adding a cache layer on top.

## Interactivity depth

If the chart is interactive at all (hover, click, zoom, pan, drill-down, sort, selection...), decide how much information each interaction surfaces. A tooltip could be minimal:
```
Model: Gemini
Score: 73.7%
Benchmark: DeepSWE v1.1
```
or much richer. Decide per chart type rather than using one tooltip template everywhere — a dense data table probably wants terse tooltips; a sparse scatter plot can afford richer ones. Also decide whether interacting with one chart should affect *other* charts on the same dashboard (e.g. clicking a bar filters every other chart to that category) — this is a meaningful architectural choice, not a minor UX flourish, since it implies shared state across chart components.

## Failure and unexpected-data behavior

What happens when live data doesn't match what was expected — an extra field shows up, a type changes, a value is out of range? Options: ignore it, display it anyway, warn the user, reject the whole dataset, or fail only the specific chart that depends on it.

**Default: don't let one unexpected field take down an otherwise-valid dashboard.** Isolate failures to the smallest affected unit (one chart, not the whole page) unless the project has explicitly opted into strict schema validation — e.g. because the output feeds something where silently displaying wrong data would be worse than an explicit error.

## Global vs. chart-specific — apply this to everything above

The single most useful discipline across this whole skill: **not every feature applies to every chart.** Grouping matters for an age histogram; it doesn't mean anything for a benchmark comparison table. "Others" helps a 50-slice pie chart; it's meaningless on a line chart. Drill-down makes sense for hierarchical/grouped data; it doesn't for a single flat scatter plot.

Classify each capability, per chart, as one of:
```
Supported
Supported with configuration
Not meaningful for this visualization
```

This is what keeps a visualization *system* (as opposed to a single chart) from forcing irrelevant controls onto every chart it renders — the goal is a framework that offers capabilities where they're meaningful, not one that mechanically applies the same feature set everywhere regardless of fit.
