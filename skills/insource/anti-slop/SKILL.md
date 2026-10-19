---
name: anti-slop
description: Review UI and product-design quality for a page, selected routes, an application, or a repository. Use when asked to find, explain, prioritize, or guide correction of design anti-patterns using visual/contextual evidence, source inspection, or both. Routes through a 67-pattern catalog and keeps findings evidence-based; it does not infer AI authorship or treat style matches as violations.
compatibility: Python 3.10+ is required for bundled validation and structural-scanner scripts. Browser rendering, screenshot capture, and parallel subagent support depend on the host and are optional.
metadata:
  inspired_by: "Impeccable (https://impeccable.style/)"
  catalog_last_verified: "2026-10-06"
  attribution: >-
    Credits Impeccable's public Slop catalog and examples as inspiration and
    source material for the catalog concepts represented here.
  relationship: >-
    An independent, narrower adaptation, not a copy of Impeccable's full skill
    or a claim to its work. It helps agents understand UI/design slop patterns
    and gives focused correction guidance; it is not as comprehensive as
    Impeccable.
---

# anti-slop

## Mission and operating contract

Review a requested interface or project for evidence of UI/design anti-patterns, explain the user-facing concern, account for legitimate context, and recommend proportionate corrections. The registry contains the 67-entry Impeccable catalog (61 source/browser rules and six design-review patterns), reconciled with the 60 supplied local records.

Treat catalog entries as investigation routes, not universal style laws. A visual resemblance, regex match, token difference, console message, or isolated screenshot is a **signal**, not proof. Never infer AI authorship from a design or writing pattern. Do not edit the reviewed product unless the user explicitly asks for implementation.

## When to use this skill

Use it when the user asks for a visual/UI anti-pattern review of one page, selected pages, an application, or a codebase; asks what a catalog signal means in a product context; or requests evidence-based correction guidance for interface quality.

### Included

- Registry-routed, selective reviews of rendered pages and relevant source.
- Explanation of user impact, context, exceptions, detector limitations, and practical corrections.
- Separate visual/contextual review and source/structure review with explicit evidence reconciliation.
- Page, multi-page, application-flow, and repository review with scope and coverage limits reported.

### Excluded

- AI-authorship detection or claims based on punctuation, wording, style, or visual similarity.
- Treating all 67 catalog entries as requirements, running every detector against every file, or declaring a project clean from partial coverage.
- A formal accessibility conformance audit, security review, product usability study, or claim that a single automated check certifies quality. Accessibility-relevant signals may be surfaced, but assess the applicable criterion and rendered behavior.
- Automatic product-code edits. Make changes only when the user requests them.

When target, task, audience, brand intent, or relevant state materially affects a decision, use the available evidence and mark uncertainty; ask for missing context only if it could change the finding or recommendation.

## Review procedure

Follow this sequence for every review. The detailed scope-routing guide is in `references/review-workflow.md`.

1. **Set the scope.** Identify the target routes/files, review depth, user task, known audience/brand constraints, viewport/theme/state, and available source or rendered UI. State unavailable inputs rather than inventing them.
2. **Discover the relevant surface.** For a project review, identify the UI stack, route/component boundaries, shared design tokens, major user flows, and which screens can actually be rendered. Avoid scanning unrelated backend, generated, vendor, or build output.
3. **Route through the registry.** Read `registry/registry.json`; select only potentially relevant pattern IDs by catalog section, scope, official modality, implementation applicability, and evidence available. A registry selection is a hypothesis to inspect, not a finding.
4. **Load only selected knowledge.** Open each selected pattern’s `knowledge.md` and `detection.md`, plus only the linked captures/examples needed to understand its signal and false positives. Do not load all pattern files or screenshots.
5. **Run independent passes.** When both modalities are available, have `impeccable-scout` and `structural-scout` assess their own evidence independently and in parallel. Neither reads the other’s preliminary findings. Host instructions and output contracts are indexed in `references/scout-contracts.md`. If a host lacks subagents, perform isolated sequential passes and do not blend their reasoning before both finish.
6. **Preserve evidence before merging.** Retain source locations/snippets and visual route/region/viewport/state observations separately, along with context, counterevidence, confidence, and limits.
7. **Reconcile conservatively.** Apply `references/evidence-and-reporting.md`. Agreement may strengthen a finding but does not replace proof of actual harm; disagreement remains visible and unresolved cases stay candidates or require context.
8. **Report useful outcomes.** Prioritize observable user impact, state coverage, legitimate exceptions, and proportionate corrections. Use the report contract in `report.schema.json` when machine-readable JSON is requested.
9. **Verify corrections when requested.** Revisit the affected route/state and report what was rechecked. Do not claim verification for states or viewports not inspected.

## Supported scopes

- **Page:** one route, rendered screen, screenshot, and relevant component/source. Inspect the whole page and essential states, not just the hero viewport.
- **Multi-page:** selected routes, especially when comparing shared visual recipes, repeated components, or route-specific context.
- **Application:** representative workflows, states, responsive variants, and the components that implement them; sample by user flow rather than indiscriminate exhaustive scanning.
- **Project:** relevant UI source and rendered product areas across a repository. Discover the application first, then route a focused set of patterns and files.

## Evidence and decisions

Use the following controlled vocabulary:

- **Structural evidence:** source-backed candidate signal with path, line/column, and matched snippet.
- **Visual evidence:** observed rendered appearance/behavior with route or screenshot, region, viewport, and state.
- **Contextual evidence:** user task, meaning, product/brand intent, workflow, or documented exception relevant to impact.
- **Candidate:** a relevant signal whose harm, intent, or applicability is not established.
- **Confirmed:** evidence establishes both the defining condition and a material problem in the reviewed context.
- **False positive:** the apparent match is explained by a legitimate role/context; retain the evidence and rationale.
- **Not observed:** no match was found within the explicitly reviewed scope; this is not a project-wide clean bill of health.

Structural scout findings remain candidates. Visual-only evidence may establish a rendered problem without a source match. Do not let one modality silently overrule the other. See `references/evidence-and-reporting.md` for merge cases and required reporting details.

## Output requirements

Summarize review scope and coverage. For each material finding include stable pattern ID/name, status, confidence, evidence modality, exact source or rendered reference, observed impact or reason it remains a candidate, context/exceptions/counterevidence, a proportionate correction, and verification steps. Preserve unresolved disagreement and state what was not reviewed. `report.schema.json` is the canonical structured report shape.

## Package map and read routes

Use this map as the package index. Paths are relative to this `SKILL.md`. Read the always-read route for every review; open conditional files only when their trigger applies. Do not load a whole directory just because one file in it is needed.

### Every review

1. Read [`references/review-workflow.md`](references/review-workflow.md) for scope triage, registry routing, and page/multi-page/application/project procedures.
2. Read [`registry/registry.json`](registry/registry.json) to select a small relevant pattern set. For each selected ID, follow that record’s `knowledge` and `detectionGuide` paths to `patterns/<pattern-id>/knowledge.md` and `detection.md`; do not open unselected pattern directories.
3. When both rendered UI and source are available, read [`references/scout-contracts.md`](references/scout-contracts.md), then the role-specific scout instructions below. After both independent assessments return, read [`scouts/reconciliation.md`](scouts/reconciliation.md) before merging.
4. Read [`references/evidence-and-reporting.md`](references/evidence-and-reporting.md) when assessing status, reconciling evidence, or preparing a report. Read [`report.schema.json`](report.schema.json) only when machine-readable combined-report JSON is requested; skip it for prose-only reports.

### Scout folders

- **Visual/contextual reviewer:** [`scouts/impeccable-scout/AGENT.md`](scouts/impeccable-scout/AGENT.md) is the role and procedure; read it when assigning or performing the visual pass. Read [`scouts/impeccable-scout/output.schema.json`](scouts/impeccable-scout/output.schema.json) before emitting or validating that scout’s JSON. Skip the schema for prose-only notes that are not being returned as scout output.
- **Structural reviewer:** [`scouts/structural-scout/README.md`](scouts/structural-scout/README.md) explains registry scope, invocation, and candidate-only limits; read it when assigning or running the structural pass. Read [`scouts/structural-scout/output.schema.json`](scouts/structural-scout/output.schema.json) before using `--json` or emitting/validating structural-scout JSON. Skip it for a prose explanation that is not scout output.
- The two schemas define different role-specific outputs; neither replaces the combined [`report.schema.json`](report.schema.json). Do not substitute one schema for another.

### References and examples

- [`references/review-workflow.md`](references/review-workflow.md): read on each review for scope and routing.
- [`references/evidence-and-reporting.md`](references/evidence-and-reporting.md): read for evidence vocabulary, status decisions, and synthesis/report requirements.
- [`references/scout-contracts.md`](references/scout-contracts.md): read before scout orchestration for the independent-parallel protocol, each scout’s schema, and the reconciliation utility.
- [`references/catalog-and-provenance.md`](references/catalog-and-provenance.md) and [`source-map.md`](source-map.md): read only when investigating catalog origin, source-version differences, or which retained capture/example supports a selected pattern. Do not browse the full capture archive during an ordinary review.
- [`references/operations-and-evaluation.md`](references/operations-and-evaluation.md): read only when running tests/scripts, maintaining the package, capturing evidence, or executing skill evals; it documents prerequisites and side effects.
- [`examples/page-review.md`](examples/page-review.md) and [`examples/project-review.md`](examples/project-review.md): optional walkthroughs when a procedure is unclear. They are illustrative, not evidence about the current target.

### Scripts, tests, evals, and evidence

- `scripts/structural_scout.py`: run only after registry routing, on selected source paths and supported pattern IDs; read [`scouts/structural-scout/README.md`](scouts/structural-scout/README.md) first.
- `scripts/reconcile_evidence.py`: import/use only after both independent scout outputs are available; policy is in [`scouts/reconciliation.md`](scouts/reconciliation.md). It is not a substitute for contextual judgment.
- `scripts/validate_registry.py`: maintainer integrity check; use when validating package/catalog links, not as a product-review detector.
- `scripts/build_registry.py`: maintainer-only generator that rewrites the canonical registry from captured source; never run during an ordinary review.
- `scripts/capture_inner_scroll.py`: optional evidence-acquisition helper for authorized pages with internally scrolling panels; use only when that capture is needed and Playwright/browser prerequisites are available.
- `tests/README.md` and `tests/`: maintainer verification only. Structural fixtures and tests validate source-candidate accuracy; `tests/visual/cases.json`, `results.json`, `screenshots/`, and `test_visual_cases.py` define reviewed calibration cases; `tests/integration/cases.json` and `test_reconciliation.py` exercise cross-scout outcomes; `tests/test_skill_contract.py` checks package contracts. Do not load tests as findings about a product under review.
- `evals/evals.json`, [`evals/README.md`](evals/README.md), and `evals/fixtures/`: maintainer-only host prompts and three high/medium/low HTML benchmark cases; never consult expected findings during ordinary product reviews.
- `evals/run_html_evals.py`: maintainer runner requiring Playwright/Chromium; captures the annotated HTML cases and scores structural candidate signatures only. Read the eval README first; do not interpret its score as a visual-agent or host-LLM score.
- `evals/agent-review-observations.json` and `evals/score_agent_reviews.py`: recorded independent-review observations and their annotation scorer; read/run only when grading these evals, not during product reviews.
- `evals/screenshots/`, `evals/results.json`, and `evals/agent-review-score.json`: generated local HTML-evaluation evidence and scores; open only when reviewing or reporting that run. These outputs do not establish host-level skill performance.
- `assets/source/` stores captured catalog/demo text and DOM; `assets/screenshots/slop/` and `assets/screenshots/examples/` store sequential visual captures. Read [`source-map.md`](source-map.md) to locate evidence for a selected pattern, then open only those captures. These archives are reference evidence, not a checklist to load wholesale.

### External source inputs (maintenance only)

The project-root [`../antipatterns.json`](../antipatterns.json), [`../registry.rs`](../registry.rs), and [`../slop.PNG`](../slop.PNG) are original/reconciliation inputs, not runtime skill resources. Read them only when maintaining or auditing the catalog’s provenance; use `registry/registry.json` as the operational routing index. The PNG is a partial viewport, not complete catalog evidence.

## Quick validation

From the repository root, run `python anti-slop/scripts/validate_registry.py` and the test commands in `references/operations-and-evaluation.md`. The registry is reference data; never regenerate it during a product review.