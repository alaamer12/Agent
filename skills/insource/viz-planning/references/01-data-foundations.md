# Data Foundations

Covers: data source & update behavior, schema stability, dynamic/"etc." fields, data shape, data volume, multiple inputs with the same structure, data quality/noise, empty/null-like data, static vs. continuously growing data.

These are mostly **global** decisions — made once for the project, not per chart.

---

## Source and update behavior

Identify the source type first: a file, a URL, an API, a database, or several of these combined. Assume the data already exists — this skill (and generally the visualization layer) isn't responsible for scraping or building a data-engineering pipeline; that's a separate concern.

Then decide static vs. dynamic:

- **Static** — load once, visualize. Simple, and the right default unless there's a real reason to do otherwise.
- **Dynamic** — the source grows or changes over time (e.g. a scraper pushing new records every minute). This forces a second decision: does the visualizer reload everything each time, or fetch only what changed?

If dynamic, pin down:
- How often does it change — seconds, minutes, hours, daily?
- Are new records only appended, or can existing records change or be deleted?
- Is there a signal that new data exists (a timestamp, a version field, a webhook) or does the visualizer have to poll?
- Should it append/update in place, or fully replace the previous dataset each refresh?

A naive "reload everything on every refresh" approach is fine for small static data and actively wrong for a growing dataset at scale — it wastes bandwidth/compute and makes animated "what changed" transitions impossible. Decide this explicitly rather than defaulting into it.

## Schema stability and evolution

Will the shape of each record stay the same, or can fields be added, removed, renamed, retyped, or restructured (nested shapes changing) over time?

If the schema can drift, decide the policy for a field that doesn't match what was expected:

| Policy | What happens |
|---|---|
| Ignore | unknown field is silently dropped |
| Display | attempt to show it anyway (e.g. auto-add a column) |
| Warn | show it, but flag it to the user |
| Reject | refuse the whole dataset |
| Fail the one chart | isolate the failure so it doesn't take down the rest of the dashboard |

Default recommendation: **don't let one unexpected field take down an otherwise-valid dashboard.** Prefer "ignore or display + warn" over "reject", unless the user has explicitly asked for strict schema validation (e.g. this feeds something safety- or compliance-critical).

## Dynamic / "etc." fields

Separately from schema drift: does the data have an inherently open-ended set of categories or fields — user-generated tags, dynamically created categories on a website, arbitrary key-value metadata? This is a **fixed schema vs. dynamic schema** distinction, and it changes the visualization strategy: a fixed schema can map cleanly to fixed chart dimensions; a dynamic one needs the visualizer to discover dimensions at load time rather than assuming them.

## Data shape

Flat, nested, hierarchical, relational, time-series, categorical, multidimensional, or some mix. This matters concretely when the input format itself is flatter than the data's real structure — e.g. nested JSON like `pricing: { input, output }` doesn't fit a flat CSV row directly. Decide the flattening convention up front (`pricing.input` → `input_price`, or some other scheme) so it's consistent across the whole dataset rather than improvised per-chart.

The internal representation used inside the visualization system should generally be able to hold richer structure than the least-expressive input format allows — don't let CSV's flatness become the ceiling for what the system can represent internally.

## Data volume

20 points and 20,000,000 points are different engineering problems, not just different chart settings. Establish:

- Will all data load at once, or does it need pagination/streaming/sampling?
- Can the full dataset fit in memory?
- Will it be pre-aggregated before it ever reaches the rendering layer?
- Will the chart render every individual point, or a reduced/binned representation?

Rendering every point directly stops being viable well before "millions" — most chart types become unreadable, and browsers become sluggish, in the thousands-to-tens-of-thousands range depending on chart type. If volume is uncertain, plan for aggregation/sampling rather than assuming raw rendering will scale.

## Multiple inputs with the same structure

If several files/sources share a structure (e.g. `data1.parquet data2.parquet data3.parquet`), don't assume matching filenames or extensions mean matching schemas — check it. Run `scripts/compare_schemas.py file1 file2 file3 ...`: it reports which fields are common to every file vs. only present in some, flags type mismatches on the fields that are common, and gives a verdict (identical / same-fields-different-types / field-sets-differ).

Beyond what the script checks, decide explicitly:

- Are the schemas actually compatible, or only superficially similar?
- Should records be concatenated into one dataset, kept as separate comparable datasets, or diffed against each other?
- Should the record's originating source be preserved as a field (so it can still be filtered/colored by source later)?
- How are duplicates across sources handled?
- Does the order of the inputs matter?

Concatenating without preserving source is a one-way decision — it's much easier to keep the source field and drop it later than to reconstruct it after the fact.

## Data quality and noise

This overlaps with data engineering, but it directly affects correctness, so it needs an explicit policy rather than a silent assumption:

- **Duplicates** — is a repeated value two real observations, or one record counted twice? Don't assume; this changes counts and averages.
- **Nulls / missing fields / malformed records** — ignored, displayed as-is, treated as zero, represented as explicitly missing, or excluded from aggregation? These are *not* interchangeable — "treat null as zero" and "exclude from average" produce different numbers from the same data.
- **Outliers** — see `03-choosing-and-transforming.md`, which covers detection and representation in depth.

## Empty vs. null vs. missing

These are commonly conflated but are meaningfully different, and a visualization can get quietly wrong by treating them as the same thing. `scripts/profile_data.py` (Step 1) already reports these separately per field — `null`, `empty_string`, `empty_object`, `empty_array`, and "missing (field absent)" as a distinct count from all of them — so this is rarely something to ask the user about; read it from the report instead:

```
null       → an explicit null value
""         → empty string (a value, just an empty one)
{}         → empty object
[]         → empty collection
"null"     → the literal string "null" (a data quality bug, not a null)
missing    → the field doesn't exist on the record at all
```

Decide per field (not globally — a missing `description` and a missing `price` probably deserve different treatment):
- Does this count as null for aggregation purposes?
- Should it render as blank, as "N/A", or be excluded from the chart entirely?
- Should missing (field absent) be visually distinguished from explicitly null?
- Should the user be warned when a meaningful fraction of a field is empty?

## Static vs. continuously growing — as a lifecycle, not just a load-time decision

This deserves restating because it affects the *whole* system, not just the initial fetch:

```
Static:                          Continuously growing:
File / URL                       URL / API
   ↓                                ↓
Load once                        Initial load
   ↓                                ↓
Visualize                        Ping every X seconds → detect changes
                                     ↓
                                  Calculate delta → fetch only new data
                                     ↓
                                  Update visualization → repeat
```

If growing: does historical data stay available, or does the view only ever show a rolling window? Should updates to the chart animate, or just snap to the new state? These are worth deciding before building, since retrofitting delta-loading onto a "reload everything" implementation is a real rewrite, not a tweak.
