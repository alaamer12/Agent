# Hero metric layout

**ID:** `hero-metric-layout`  
**Catalog section:** Layout & Space  
**Official modality:** Design review

## Definition and empirical evidence

This pattern concerns giving a large metric visual prominence in a page/hero. Large values are also a legitimate dashboard convention: a card may show one important fact, while a KPI visual communicates progress toward a measurable goal. Large numerals alone are not evidence of a problem.

## Underlying principle and potential harm

Prominence should help users understand a relevant result, not substitute for its meaning. An isolated or weakly labeled number can be ambiguous or function as decorative “proof” without explaining what was measured. Unit, period, denominator, target, data freshness, or trend direction can change its interpretation.

## Recognition signals

- A large value is not clearly labeled with what it measures, unit, scope, or relevant time period.
- A positive/negative judgment is implied without a valid target, baseline, or comparison.
- Color/arrows/wording imply improvement even though the metric’s direction may have a different interpretation.
- The number’s source, definition, or freshness is unclear.

## Causes to investigate

Possible causes include using a vanity number to make a hero persuasive; copying a generic metric template; choosing a metric unrelated to the page’s purpose; or omitting context for visual minimalism.

## Exceptions and false positives

- A verified, relevant product/customer result can be the main message of a data-led landing page.
- A dashboard may focus on one high-priority value for at-a-glance monitoring.
- A KPI tracking a goal should communicate progress toward a measurable goal; a card may simply present an important fact.
- Context can live nearby (label, date-range selector, comparison, linked detail) rather than all in the hero.
- Some current values have no meaningful target/favorable direction; avoid forced red/green judgments.
- Large type or minimal labeling alone does not prove misinformation or poor hierarchy; check the full page and data source.

## Correction guidance

Start with the question the page should answer and verify the metric is defined, accurate, current, and relevant. Add only the context needed for interpretation—often label, units, timeframe/scope, and a valid comparison/target if one exists. State freshness/caveats when needed. Ensure color/arrows do not imply an incorrect direction. Remove or de-emphasize unsupported decoration; retain a valid focal metric and make it easy to verify.

## Independent research references

- [Microsoft Power BI — Visualizations overview](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualizations-overview) — single-fact cards versus goal-progress KPIs.
- [Tableau — What is a KPI dashboard?](https://www.tableau.com/kpi/what-is-kpi-dashboard) — audience/purpose, time frames, meaningful comparisons/targets.
- [Government Analysis Function — Data visualization charts](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts) — chart choices and misleading interpretation.
- [Microsoft Power BI — KPI visuals](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-kpi) — target/trend labels and the fact that higher is not always better.