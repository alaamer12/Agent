# Scout contracts and host integration

The two scouts are complementary reviewers for real product work. They are not research agents for expanding the catalog. Consult the registry and load only selected pattern knowledge before invoking either role.

## Visual/contextual scout

[`scouts/impeccable-scout/AGENT.md`](../scouts/impeccable-scout/AGENT.md) defines the visual reviewer. It inspects rendered pages/screenshots, user/task context, pattern evidence, exceptions, and observable impact. It must not infer source facts from pixels or AI authorship from a style.

When producing or validating machine-readable visual-scout output, read [`scouts/impeccable-scout/output.schema.json`](../scouts/impeccable-scout/output.schema.json). It defines the visual scout's own fields and status vocabulary; skip it for prose-only analysis that is not returned as scout output. Include observed and assessed IDs, screenshots/routes/regions, viewport/state, context, counterevidence, limitations, and conservative status.

## Structural scout

[`scouts/structural-scout/README.md`](../scouts/structural-scout/README.md) defines the code/structure reviewer. It reads relevant registry entries and detection guides, scans only applicable paths, and emits source-backed candidate evidence. It cannot confirm violations.

Run the reusable scanner from the repository root:

```text
python anti-slop/scripts/structural_scout.py <file-or-directory> [--pattern <pattern-id> ...] [--json]
```

When invoking `--json` or returning machine-readable structural-scout output, read [`scouts/structural-scout/output.schema.json`](../scouts/structural-scout/output.schema.json). It constrains the scanner's candidate-only payload; skip it for prose-only notes. Supported detector IDs are defined by `candidate_detector_ids()` in the scanner; do not assume every registry item has an implemented detector.

## Parallel execution

After registry routing, start both reviews independently when the host supports subagents and both input modalities exist. Give each scout the same scope and selected pattern IDs, but do not pass one scout’s initial findings to the other. Each scout reads its own role guide; load its output schema only when emitting/validating its JSON. Wait for both responses before using [`scripts/reconcile_evidence.py`](../scripts/reconcile_evidence.py) or otherwise synthesizing. On hosts without parallel subagents, perform separate sequential passes from clean notes and preserve the same separation.

## Reconciliation utility

[`scripts/reconcile_evidence.py`](../scripts/reconcile_evidence.py) exposes `reconcile_case(case)` as a Python helper; it is not a command-line program. [`tests/integration/test_reconciliation.py`](../tests/integration/test_reconciliation.py) exercises the helper against [`tests/integration/cases.json`](../tests/integration/cases.json).

The helper implements the policy in [`scouts/reconciliation.md`](../scouts/reconciliation.md); it preserves modality evidence and never confirms from structural evidence alone. Its output is not a substitute for checking whether the visual/contextual evidence is actually adequate. Read [`report.schema.json`](../report.schema.json) only when the merged report must be returned as machine-readable JSON; it is separate from both scout schemas.