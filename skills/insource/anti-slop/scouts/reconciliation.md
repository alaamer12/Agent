# Parallel scout orchestration and evidence reconciliation

## Routing and independence

1. Confirm page/project scope and identify technologies, routes, components, and available rendered evidence.
2. Read the registry and choose only potentially relevant patterns. Preserve each pattern’s modality and test disposition.
3. Launch `impeccable-scout` and `structural-scout` independently in parallel for the same scoped target and relevant pattern IDs. Each scout receives the registry and its own role-specific guides; neither sees the other’s findings before returning its assessment.
4. Wait for both outputs. Keep their raw evidence trails, statuses, and limitations separate before synthesis.
5. Merge by stable `patternId`; do not let one modality silently overwrite or confirm the other.

## Cross-scout outcome rules

| Structural scout | Visual/contextual scout | Reconciled outcome |
|---|---|---|
| Candidate | Confirms visible harm and the context is not a legitimate exception | Confirmed; report both source and rendered evidence separately |
| Candidate | Finds a purposeful/accessible use that fits the task | False positive for the suspected violation; retain the structural signature and why it is legitimate |
| Candidate | Cannot see the affected route/state or lacks context | Candidate / unresolved; request the missing render or context |
| No deterministic match | Confirms a visible/contextual pattern and its harm | Confirmed visual/contextual finding; explicitly note no structural signature was found |
| No deterministic match | Suspects a pattern but impact/intent is unclear | Candidate; do not manufacture a source match |
| No finding | No finding | Not observed for the assessed scope; do not claim the whole project is clean if coverage was limited |

## Evidence and status policy

- Structural matches are always candidate evidence. They never automatically become `confirmed`.
- Visual resemblance to a reference is not sufficient; the scout must describe actual project evidence and context.
- A `confirmed` result requires evidence of the pattern’s defining condition and its problem in this context. If either is missing, retain `candidate`.
- Disagreement is a first-class result. Preserve both accounts and use `candidate`/`unresolved` until contextual review resolves it.
- A false positive documents the lookalike and its legitimate role; do not discard the original evidence.
- Reports distinguish structural, visual, and contextual evidence, confidence, route/region, viewport/state, limitations, exceptions, and recommended next step.

The integration cases under `../tests/integration/cases.json` are the acceptance examples for this policy.