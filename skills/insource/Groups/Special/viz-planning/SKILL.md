---
name: viz-planning
description: Use this skill when planning, designing, or architecting a data visualization system, dashboard, chart component, reporting tool, or analytics app — anything built once and used repeatedly, or involving real complexity (unstable schemas, growing/streaming datasets, multiple sources, many categories, outliers, filtering or persisted state). Walks through data source stability, schema evolution, volume, semantics, chart selection, grouping/aggregation/outlier handling, filtering and state architecture, layout, and configuration precedence BEFORE any chart gets built, so the wrong visualization or a fragile pipeline doesn't get picked by default. Trigger even when the user just says "help me build a dashboard for X" or "I need to visualize this data" without naming any of these specifics — the point is surfacing considerations they haven't thought of yet. Do NOT use for one-off requests like "chart this CSV" or "plot Q3 revenue" against already-clean, already-understood data — just chart it directly.
---

# Viz Planning

## Why this exists

Picking a chart type is the last decision in data visualization, not the first. Before that: where the data comes from and how stable it is, what it means, how much of it there is, what question it's answering, what deserves focus, what should be grouped or hidden versus always discoverable, how state and configuration persist, and what happens when the data doesn't match expectations. Skipping these produces dashboards that break on the first schema change, pie charts with 40 unreadable slices, or filters that vanish on refresh.

It also means resisting the pull toward more charts, and more sophisticated chart types, than the audience actually needs. A working visualization engineer defaults to the fewest charts that fully answer the question, and picks chart types the intended audience can read in a few seconds — a general/non-technical audience reads a bar, line, or pie chart instantly; the same audience has to be taught how to read a scatter plot or a box plot first. One well-chosen chart a lay audience immediately understands beats ten information-dense ones that each need a caption explaining how to read them.

This skill is a triage-and-decision framework, not a charting library. It ends with a written set of decisions handed off to whatever actually builds the thing — this environment's chart/Visualizer tools, a frontend framework, a BI tool, or custom code.

## Step 0 — Scope check

Decide which mode this is before doing anything else — three options, not two:

- **Lightweight.** A single chart from a dataset that's already clean, already fully understood, and won't be reused or extended (e.g. "chart these 12 monthly numbers"). Skip the rest of this skill entirely — just make the chart.
- **Targeted.** A single, non-recurring chart or report that still has one specific nontrivial problem to solve — too many categories, an ambiguous field, choosing between two chart types, an outlier skewing the read, how to highlight one entity against the rest. Skip straight to whichever single reference file in Step 4 covers that problem, apply it, and stop there — no inspection pass, no question list, no VISUALIZATION.md. Most "how should I show X" questions that aren't about building a system or dashboard land here.
- **Full.** A dashboard, a reusable component, a recurring report, an internal tool, or any request where the data's shape, freshness, or scale is unclear. Run the full sequence, Steps 1–6, below.

When unsure between Targeted and Full, prefer Full. When unsure between Lightweight and Targeted, ask: is there an actual decision to make, or is the chart obvious once the data's in hand? If there's a real decision, it's at least Targeted.

## Step 1 — Inspect the data yourself (if a real dataset exists)

Don't ask the user questions the data can already answer. If an actual file (or files) exist — uploaded, on disk, a queryable endpoint — inspect it before asking anything.

Run `scripts/profile_data.py <path>` (handles `.json`, `.jsonl`/`.ndjson`, `.csv` out of the box; for any other format, write an equivalent short script on the spot — load it, count records, list fields, sample randomly, sample sequentially). One pass reports:

- volume, and schema (field presence rate, types, empty/null rate broken down by kind, candidate-categorical fields with their cardinality, numeric ranges, observed decimal precision)
- exact-duplicate count
- for timestamp-looking fields, the actual date/time range and span — this is what tells you a "365 daily records" situation exists before you pick a chart, instead of finding out after
- whether any field is monotonic across the **whole file** — the strongest available signal for whether the data is inherently ordered
- a **random sample** — reveals whether values are diverse/well-distributed or clustered
- a **sequential sample**, first N in file order — reveals whether file order itself carries meaning (append order, time order, etc.)

The comparison between the two samples is the actual point, not either sample alone: if they look interchangeable, order is probably incidental; if the sequential one shows a trend the random one doesn't, treat order as meaningful and worth surfacing.

This single pass typically answers most of the source/schema/volume/quality/cardinality/time/continuity questions directly, without asking the user any of them. Apply judgment reading the output — e.g. a low-cardinality integer field can still be an ID rather than a category; check whether it's also flagged monotonic before calling it "categorical."

If there's no real dataset yet (a described-but-not-provided source, or a from-scratch design conversation), skip this step — there's nothing to inspect — and rely on Step 3's questions instead.

**Multiple files of the same/similar structure** (e.g. `data1.json`, `data2.json`, `data3.json` meant to be treated as one dataset): don't assume matching filenames or extensions mean matching schemas. Run `scripts/compare_schemas.py file1 file2 file3 ...` — it reports fields common to all files vs. fields only in some, type mismatches on shared fields, and a verdict on whether they're safe to concatenate directly, need type normalization first, or have real field-set drift that needs an explicit policy.

## Step 2 — Report what you found

Before asking anything, tell the user what Step 1 (or, absent real data, the conversation so far) revealed — in plain language, not a raw dump of script output. For example: "62 profiles. Schema drifts slightly — `score` and `beta_flag` are missing on some records. `age` has ~5% nulls. No field is monotonic across the file, so this looks like independent records rather than a time series. `tags` is a dynamic multi-value field, 6 distinct values seen so far." This step is load-bearing: it shows the reasoning, and it's what tells the user which things are being inferred versus which things still need their input.

## Step 3 — Ask only what's still vague

Skip anything Step 1 already answered from evidence. What's left is usually intent, not structure — data can't answer these:

1. **Purpose** — what question should this answer (comparison/trend/distribution/proportion/relationship/composition)? The data can suggest candidates; it can't pick one.
2. **Focus** — is there a target entity/category to steer attention toward, against the rest?
3. **Audience literacy — ask this one explicitly, every time.** Will this be read by people who work with data professionally, or a general/non-technical audience? This isn't a minor detail — it decides which chart types are even viable (see `references/03-choosing-and-transforming.md`): general audiences reliably read bar/line/pie; scatter plots, box plots, and heatmaps need literacy most general audiences don't have, even when they're more information-dense.
4. **Reuse** — one-time report, recurring internal tool, or public-facing?
5. **Default time window — ask this when Step 1 reports a wide time span at fine granularity** (e.g. a year of daily data): showing the full span at full resolution is rarely the right default. Should the default view show a recent window (last N days/weeks), the full span at a coarser rollup (weekly/monthly), or something else — with full detail still reachable via zoom/date-range picker rather than gone?
6. **Number formatting/precision** — should precision be uniform across the dashboard, or does it vary by field (e.g. currency to cents, percentages to one decimal, counts as whole numbers)? Step 1's report already shows the decimal precision actually observed in the data — use that as the starting point rather than guessing a rounding rule from scratch.
7. **State & sharing** — should views be shareable via URL, or is this single-user, single-session?
8. **Scope of customization — ask this explicitly whenever more than one chart is in play:** should decisions (grouping, color, interactivity, chart type, etc.) apply uniformly across all charts, or does each one need its own treatment? If the answer is "per chart," recommend a best-fit chart type and configuration for each one individually rather than reusing one template across charts serving different purposes.

Keep this to a handful of questions — don't re-ask anything the inspection or the conversation already covered. Where the environment supports structured quick-choice input, use it; otherwise ask plainly.

## Step 4 — Deep dive (load only what's relevant)

Each reference file is a slice of the pipeline. Load only the ones flagged as applicable by Steps 1–3 — don't read all six by default.

| File | Covers | Load it when… |
|---|---|---|
| `references/01-data-foundations.md` | source & update behavior, schema evolution, dynamic/"etc." fields, data shape, volume, multi-file input, quality/noise, null vs. empty handling | source isn't a one-time clean static file, or schema/quality is uncertain |
| `references/02-semantics-and-intent.md` | timestamps, value representation (raw vs. %, currency, labels), what the visualization is meant to communicate, data focus, field semantics/descriptions | data has time fields, ambiguous fields, or a target entity to highlight |
| `references/03-choosing-and-transforming.md` | chart selection, relationships between data points, grouping vs. "Others" vs. aggregation, progressive disclosure, outlier handling | more than a trivial number of categories/points, or the right chart type isn't obvious |
| `references/04-interaction-config-state.md` | filtering architecture (URL params as canonical state), persisted UI state, config sources & precedence | any filtering, or anything that should survive a refresh / be shareable |
| `references/05-layout-and-presentation.md` | dashboard layout/grid, how a chart is framed (title/description/source), legends, long-text handling, color as semantic encoding | multi-chart dashboards, or charts with legends/many labels |
| `references/06-plumbing-and-failure.md` | input format normalization, caching/performance at scale, interaction depth (tooltips, drill-down), unexpected-data handling, global-vs-chart-specific feature scoping | large/streaming data, multiple input formats, or building a reusable system rather than a single chart |

`references/checklist.md` is a condensed, scannable version of every question across all six files — use it mid-project as a quick audit rather than re-reading the full files.

## Step 5 — Minimize, then write VISUALIZATION.md

Before listing charts, actively try to shrink the list. For each candidate chart, ask: could this be a second series or a facet/filter on an existing chart instead of a new one? Could a table row or a single annotated number carry it instead? Does it answer a genuinely different question than an existing chart, or just re-slice the same answer? If a chart list is starting to look like "one chart per column in the source data" rather than "one chart per question the audience needs answered," consolidate before writing anything down.

For **Full** scope, produce `VISUALIZATION.md` (start from `assets/VISUALIZATION-template.md`) — a per-chart checklist, not a prose doc. Every decision and micro-decision gets its own single-line checkbox item: chart type, the field(s) used, grouping/binning, aggregation, outlier handling (name the specific method/algorithm if a custom calculation feeds the chart), focus/highlighting, color mapping, legend, interactivity. One decision per line, numbered, checkable — not paragraphs. This is the actual build spec: whoever implements the charts next should be able to work directly from the checkboxes without re-reading the planning conversation.

For **Targeted** scope: no file — just explain the specific decision and why, inline, using the relevant reference file's reasoning.

## Step 6 — Hand off

This skill stops at the decision layer. Building the UI is a separate step — use whatever's appropriate here (this environment's chart/Visualizer tools, a frontend or dashboard framework, a BI tool). Don't let this skill's scope creep into being a charting tutorial.

## One principle to hold onto

Section-by-section rigor is a tool, not a ritual. The right question is always "does this decision matter for this project," never "have I addressed all the categories." A feature being globally available (grouping, "Others", drill-down) doesn't mean it's meaningful for every chart — a benchmark comparison table doesn't need binning; a histogram does. Global decisions (source, schema policy, state architecture) get made once per project; chart-specific decisions (grouping, focus, outlier handling) get made per chart within it. And the fastest way to shrink the question list in Step 3 is a good Step 1 — inspect before asking.
