# Structural Scout

## Role

Inspect source and structure for pattern-specific, source-backed candidate evidence. Consult [`../../registry/registry.json`](../../registry/registry.json) first; only scan relevant technologies/files and load each applicable pattern’s `detection.md`. This scout does not decide visual quality or confirm an anti-pattern from syntax alone.

## Scope and safeguards

- Use deterministic text/structure checks only where the registry marks a structural candidate detector as implemented.
- Browser-modality patterns require rendered runtime evidence; design-review patterns require visual/contextual judgment.
- Keep findings at `candidate` status. A structural hit cannot be promoted to `confirmed` by this scout.
- Preserve the exact path, line/column, snippet, matched signature, and limitations.
- Treat heuristic thresholds as local candidate signals, not universal design/accessibility requirements.
- Never infer AI authorship from a design-pattern match.
- Avoid generated/vendor/build folders and large/binary files; the scanner is read-only.

## Run

From the repository root:

```text
python anti-slop/scripts/structural_scout.py <file-or-directory> [--pattern <id> ...] [--json]
```

The current implementation supports the registry IDs returned by `candidate_detector_ids()` in `scripts/structural_scout.py`. Use `--pattern` after registry routing to restrict a scan. Positive, negative, and exception fixtures are stored under `tests/fixtures/<pattern-id>/`. Run the accuracy suite with:

```text
python -m unittest discover -s anti-slop/tests/structural -p "test_*.py"
```

## Output schema

When invoking the scanner with `--json`, or when returning this scout's result as machine-readable JSON, read [`output.schema.json`](output.schema.json) and conform to it. The schema constrains the candidate-only envelope and each reproducible source finding; it does not provide pattern applicability or permission to confirm a violation. Skip the schema when reporting prose-only observations that are not structural-scout output.

## Evidence contract

Each finding includes:

- `patternId`: stable registry ID.
- `path`, `line`, `column`, `snippet`: reproducible source location.
- `evidenceModality`: `structural`.
- `status` and `confidence`: always `candidate`.
- `explanation`: what source signature matched and what contextual check remains.

The top-level JSON sets `findingStatus` to `candidate-only`. No output field represents a confirmed violation. The scout can return zero matches without implying the UI has no visual/contextual anti-patterns.