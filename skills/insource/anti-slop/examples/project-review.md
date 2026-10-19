# Example: project-level review

This is an illustrative workflow, not a report about a real repository.

## Scope discovery and registry routing

1. Identify the UI framework, routes, shared components, style system, rendered entry points, and the user journeys the request covers.
2. Use the registry to select relevant pattern IDs by route/component/content and modality. A dashboard with image-bearing cards might select `nested-cards`, `low-contrast`, `images-move-on-hover`, and `identical-card-grids`; only load those knowledge/detection files if source or renders show they apply.
3. Record routes/components not inspected and states that need a running browser. Do not invoke every detector against every file.

## Independent parallel reviews

- `structural-scout` scans the selected component/style paths for implemented source candidates, such as `nested-cards` or `images-move-on-hover`. It emits candidate-only file/line/snippet evidence.
- `impeccable-scout` separately reviews screenshots/running routes at representative desktop/mobile sizes and relevant states. It assesses whether repeated cards, image movement, colors, or visual hierarchy create a problem for the dashboard task.
- Neither pass reads the other’s findings before returning. Both preserve their own limitations and paths.

## Illustrative synthesis

```text
nested-cards — candidate / contextual false positive
Structural: nested Card components occur in ServiceSummary.tsx.
Visual/context: each inner surface contains a distinct service-level metric with its own target; the hierarchy is visible.
Resolution: false positive for this component; retain the evidence and rationale.

images-move-on-hover — visual-only candidate
Structural: no supported hover-image transform signature in the scanned files.
Visual: the preview expands substantially on pointer hover; keyboard/touch alternatives were not available in the tested state.
Resolution: candidate requiring interaction follow-up; no source match does not erase the visual evidence.

low-contrast — confirmed only if measured
Visual/context: identify the actual text/background pair, theme/state, measured ratio, and applicable exception. “Muted gray” alone is not a finding.
```

Merge by pattern ID only after both independent passes complete. Follow `scouts/reconciliation.md`; retain unresolved disagreement as `candidate`/contextual follow-up and report scope limitations.