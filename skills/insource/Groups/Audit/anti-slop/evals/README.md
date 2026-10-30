# Skill-use evaluations

`evals.json` preserves three host-level prompts under `evals` and adds three annotated HTML cases under `html_impact_evals` (high, medium, and low fixture-specific impact). The HTML cases intentionally combine visible concerns with legitimate lookalikes; their impact tiers describe these fixtures, not official catalog severities.

## Local HTML evaluation

Run from the repository root:

```text
python anti-slop/evals/run_html_evals.py
```

The runner uses headless Chromium through Playwright to render each page at its declared viewport, save a screenshot under `evals/screenshots/`, record selected browser-observable conditions, and run the read-only structural scout. `evals/results.json` records the run and candidate-signature precision/recall/F1 against `expected_structural_pattern_ids`. The score does not evaluate visual judgment and a structural match remains candidate-only.

After two independent reviewers assess the same cases without seeing each other’s findings, record their pattern IDs/statuses in `agent-review-observations.json` and run:

```text
python anti-slop/evals/score_agent_reviews.py
```

The scorer compares the recorded observations to the visual, structural, false-positive, and overall-status annotations, then writes `agent-review-score.json`. Its precision/recall/F1 values use case-pattern pairs, so the same pattern in two cases counts as two evaluations. Do not treat the curated score as production accuracy, a 67-pattern benchmark, or a compatible-host LLM skill score.

## Running

1. Load this skill in a compatible agent host and provide the selected case’s listed files as review inputs.
2. Run each case in a fresh session so previous findings do not leak into later cases.
3. Compare the response against `expected_output` and each expectation; record evidence and uncertainty, not just a pass/fail score.
4. For a skill-benefit benchmark, run the same cases without the skill under otherwise comparable conditions. Do not treat skill presence as a substitute for human judgment.
5. Save host-specific transcripts, run metadata, and grading outside the skill’s reference material; the local HTML runner stores only its reproducible browser/source results and does not fabricate model outputs.

The repository’s local tests validate the JSON, unique case IDs, expectation presence, and input paths. They do not invoke an LLM or claim that the skill has passed host-level behavioral evals.