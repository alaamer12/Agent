# Quick Audit Checklist

A condensed, scannable version of every question in this skill. Use this mid-project to spot-check a design rather than re-reading the full reference files. Each line points back to the file with the full reasoning if something needs a deeper look.

## Data foundations → `01-data-foundations.md`
- [ ] Source type identified (file / URL / API / DB / multiple)?
- [ ] Static vs. dynamic decided, and if dynamic, poll interval / change-detection defined?
- [ ] Schema drift policy defined (ignore / display / warn / reject an unknown field)?
- [ ] Fixed vs. dynamic/"etc." schema identified?
- [ ] Data shape identified (flat / nested / hierarchical / relational / time-series)?
- [ ] Volume estimated, and does it require pagination/streaming/sampling?
- [ ] If multiple same-structure inputs: concatenate, compare, or keep separate — and source-of-record preserved?
- [ ] Duplicate/null/malformed record policy defined?
- [ ] Empty vs. null vs. missing distinguished where it matters?

## Semantics and intent → `02-semantics-and-intent.md`
- [ ] Timestamp format/timezone identified, humanization decided?
- [ ] Value representation decided per field (raw / %, currency, compact, bucketed label)?
- [ ] The question the chart answers is named (comparison/trend/distribution/proportion/relationship/composition/etc.)?
- [ ] Focus entity (if any) identified, and how it'll be visually distinguished?
- [ ] Ambiguous fields have a description, sourced or authored?

## Choosing and transforming → `03-choosing-and-transforming.md`
- [ ] Chart type chosen based on purpose + cardinality — table considered as an alternative to a chart?
- [ ] Point relationship type identified (independent / sequential / continuous / state transition)?
- [ ] Grouping, "Others", and aggregation are NOT conflated — each named explicitly if used?
- [ ] If data is reduced/hidden for readability: is there a defined path back to the full detail?
- [ ] Outlier detection method chosen (if relevant), and does it degrade gracefully on small N?
- [ ] Outlier representation decided (color/shape/legend)?
- [ ] Outlier participation in calculations decided (included / excluded / optional) and made visible if excluded?

## Filtering, config, state → `04-interaction-config-state.md`
- [ ] Filters represented as query parameters (canonical), UI as a secondary editor?
- [ ] URL-state vs. local-storage-state boundary defined (shareable vs. personal)?
- [ ] If multiple config sources exist, is precedence explicitly defined?

## Layout and presentation → `05-layout-and-presentation.md`
- [ ] Dashboard grid/layout decided (fixed vs. responsive, reorderable/resizable or not)?
- [ ] Per-chart framing decided (title/description/source/units)?
- [ ] Legend needed, and position/interactivity decided?
- [ ] Long-text strategy decided per label type?
- [ ] Color semantics defined and kept consistent across the whole dashboard?

## Plumbing and failure → `06-plumbing-and-failure.md`
- [ ] Normalization layer exists if more than one input format is supported?
- [ ] Caching layers identified (raw / parsed / transformed) and delta-loading considered if growing?
- [ ] Interactivity depth (tooltip richness, cross-chart filtering) decided per chart?
- [ ] Unexpected-data failure isolated to the smallest affected unit, not the whole dashboard (unless strict validation was explicitly chosen)?
- [ ] Every feature classified per chart: Supported / Supported with configuration / Not meaningful here?
