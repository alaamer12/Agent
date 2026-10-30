# Review workflow and routing

Use this guide after the `anti-slop` skill has been selected and before loading detailed pattern knowledge.

## Request triage

1. Translate the request into one of the skill’s four scopes: page, multi-page, application, or project.
2. Identify the target routes/components/files, user task, likely audience, brand/design-system context, viewport/theme/state, and available rendered/source evidence.
3. Separate required inputs from useful context. Do not block on unavailable brand material if a candidate-only review is still useful; record the missing context and its effect.
4. For implementation requests, make clear that the default deliverable is assessment/recommendation; only edit the product when asked.

## Registry routing

Read `registry/registry.json` and select patterns using all available routing signals:

- catalog category and section;
- official modality (`source`, `browser`, or `design-review`);
- scope and technology/component evidence;
- review target and user task;
- detector applicability and test disposition.

Select a small relevant subset; do not default to all 67. For each selected ID, open the registry-linked `knowledge.md` and `detection.md`. The registry and per-pattern documents are the source of truth; examples are evidence, not universal rules.

### Modality routing

| Available evidence | Appropriate work | Do not claim |
| --- | --- | --- |
| Rendered route/screenshot | Visual and contextual inspection; compare relevant pattern signals, exceptions, and impact | Source implementation, runtime states not captured, quantitative contrast without measurement |
| Source files | Only registry-supported deterministic structural candidates; precise file/line/snippet | Rendered harm, intent, or confirmation from syntax alone |
| Render and source | Separate independent visual and structural passes, then reconcile | That agreement automatically establishes harm or that disagreement can be discarded |
| Neither | Explain the catalog signal or request needed artifacts/context | A review finding, absence of slop, or project-wide coverage |

## Scope-specific procedure

### Page

Inspect the complete page where possible, including content below the first viewport, and select relevant responsive/interaction states. Route to patterns suggested by the page’s role and evidence. Run only applicable source detectors. Report the exact viewports and states reviewed.

### Multi-page

Compare selected routes for repeated visual treatments, patterns that differ by context, and shared design tokens/components. Do not call consistency monotonous without comparing content roles and user tasks. Record each route and distinguish shared evidence from route-specific evidence.

### Application

Choose representative journeys and states (initial, loading, success, error, expanded, selected, focus, responsive) relevant to the request. Keep evaluation bounded; request more scope if a conclusion depends on an unreviewed flow.

### Project

Discover frameworks, route/component organization, design tokens, important user flows, and rendered entry points. Build a focused set of UI source paths and screens, then route patterns. Exclude generated/vendor/build output and unrelated backend source unless the relevant interface behavior lives there. Do not run all detectors on all files.

## Included vs excluded review signals

Include a pattern only when its defining signal could plausibly affect the requested surface. Treat catalog labels as hypotheses and account for legitimate uses documented in that pattern’s knowledge. Exclude unrelated patterns even if their identifiers or superficial cues are easy to search. Do not use this skill to label prose or a UI as AI-generated; it does not establish authorship.

## Completion checklist

- Scope and reviewed/unreviewed routes, files, states, and viewports are named.
- Registry routing selected only relevant pattern IDs.
- Each loaded pattern’s false-positive controls were considered.
- The two evidence modalities were assessed independently when available.
- Findings distinguish candidate, confirmed, false positive, and not observed.
- Actionable correction and verification guidance are proportionate to the evidence.