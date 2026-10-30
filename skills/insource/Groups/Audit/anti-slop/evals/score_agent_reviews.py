from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVAL_ROOT = Path(__file__).resolve().parent
PACKAGE_ROOT = EVAL_ROOT.parent
EVALS_PATH = EVAL_ROOT / "evals.json"
OBSERVATIONS_PATH = EVAL_ROOT / "agent-review-observations.json"
OUTPUT_PATH = EVAL_ROOT / "agent-review-score.json"
POSITIVE_STATUSES = {"candidate", "confirmed"}


def _metrics(expected: set[str], observed: set[str]) -> dict[str, Any]:
    hits = expected & observed
    false_positives = observed - expected
    misses = expected - observed
    precision = len(hits) / len(observed) if observed else (1.0 if not expected else 0.0)
    recall = len(hits) / len(expected) if expected else (1.0 if not observed else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "expected_count": len(expected),
        "observed_count": len(observed),
        "true_positives": sorted(hits),
        "false_positives": sorted(false_positives),
        "false_negatives": sorted(misses),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def score() -> dict[str, Any]:
    eval_data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    observations = json.loads(OBSERVATIONS_PATH.read_text(encoding="utf-8"))["reviewers"]
    visual_expected: set[str] = set()
    visual_observed: set[str] = set()
    structural_expected: set[str] = set()
    structural_observed: set[str] = set()
    combined_expected: set[str] = set()
    combined_observed: set[str] = set()
    status_total = 0
    status_correct = 0
    visual_fp_expected = 0
    visual_fp_correct = 0
    case_scores: list[dict[str, Any]] = []

    for case in eval_data["html_impact_evals"]:
        case_id = case["id"]
        visual_findings = observations["visual"]["cases"].get(case_id, [])
        structural_findings = observations["structural"]["cases"].get(case_id, [])
        visual_status = {item["patternId"]: item["status"] for item in visual_findings}
        structural_status = {item["patternId"]: item["status"] for item in structural_findings}

        expected_visual = set(case["expected_visual_pattern_ids"])
        observed_visual = {pattern_id for pattern_id, status in visual_status.items() if status in POSITIVE_STATUSES}
        expected_structural = set(case["expected_structural_pattern_ids"])
        observed_structural = {pattern_id for pattern_id, status in structural_status.items() if status in POSITIVE_STATUSES}
        expected_overall = case["expected_overall_status"]
        expected_positive = {pattern_id for pattern_id, status in expected_overall.items() if status in POSITIVE_STATUSES}

        combined_status: dict[str, str] = {}
        for pattern_id in expected_overall:
            v_status = visual_status.get(pattern_id)
            s_status = structural_status.get(pattern_id)
            if v_status == "confirmed":
                actual = "confirmed"
            elif v_status == "false-positive" and s_status not in POSITIVE_STATUSES:
                actual = "false-positive"
            elif v_status in POSITIVE_STATUSES or s_status in POSITIVE_STATUSES:
                actual = "candidate"
            else:
                actual = "not-observed"
            combined_status[pattern_id] = actual
            status_total += 1
            status_correct += actual == expected_overall[pattern_id]

        expected_visual_false_positives = set(case.get("expected_false_positive_pattern_ids", []))
        visual_fp_expected += len(expected_visual_false_positives)
        visual_fp_correct += sum(visual_status.get(pattern_id) == "false-positive" for pattern_id in expected_visual_false_positives)

        case_combined_observed = {
            pattern_id
            for pattern_id in expected_overall
            if combined_status[pattern_id] in POSITIVE_STATUSES
        }
        visual_expected.update(f"{case_id}:{pattern_id}" for pattern_id in expected_visual)
        visual_observed.update(f"{case_id}:{pattern_id}" for pattern_id in observed_visual)
        structural_expected.update(f"{case_id}:{pattern_id}" for pattern_id in expected_structural)
        structural_observed.update(f"{case_id}:{pattern_id}" for pattern_id in observed_structural)
        combined_expected.update(f"{case_id}:{pattern_id}" for pattern_id in expected_positive)
        combined_observed.update(f"{case_id}:{pattern_id}" for pattern_id in case_combined_observed)
        case_scores.append({
            "case_id": case_id,
            "tier": case["tier"],
            "visual": _metrics(expected_visual, observed_visual),
            "structural": _metrics(expected_structural, observed_structural),
            "expected_overall_status": expected_overall,
            "observed_overall_status": combined_status,
            "overall_status_exact_matches": sum(
                combined_status[pattern_id] == expected_overall[pattern_id] for pattern_id in expected_overall
            ),
            "overall_status_count": len(expected_overall),
        })

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score_scope": "three curated HTML cases; case-pattern annotations, not a 67-pattern or production benchmark",
        "scoring_rules": {
            "positive_prediction": "candidate or confirmed",
            "visual_false_positive": "counts as a negative classification and is separately checked against expected false-positive lookalikes",
            "combined_status": "visual confirmed wins; an explicit visual false-positive resolves only when no structural candidate conflicts; otherwise either modality yields candidate; no finding yields not-observed",
            "limitation": "A detector can score perfectly on intentionally planted signatures without demonstrating general-world precision or recall."
        },
        "aggregate": {
            "visual_detection": _metrics(visual_expected, visual_observed),
            "structural_candidate_detection": _metrics(structural_expected, structural_observed),
            "combined_positive_findings": _metrics(combined_expected, combined_observed),
            "visual_lookalike_classification": {
                "correct": visual_fp_correct,
                "expected": visual_fp_expected,
                "accuracy": round(visual_fp_correct / visual_fp_expected, 4) if visual_fp_expected else 1.0,
            },
            "combined_status_calibration": {
                "correct": status_correct,
                "expected": status_total,
                "accuracy": round(status_correct / status_total, 4) if status_total else 1.0,
            },
        },
        "cases": case_scores,
        "observations_file": OBSERVATIONS_PATH.name,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    report = score()
    for modality in ("visual_detection", "structural_candidate_detection", "combined_positive_findings"):
        metric = report["aggregate"][modality]
        print(
            f"{modality}: P={metric['precision']:.0%} R={metric['recall']:.0%} "
            f"F1={metric['f1']:.0%} (TP={len(metric['true_positives'])}, "
            f"FP={len(metric['false_positives'])}, FN={len(metric['false_negatives'])})"
        )
    calibration = report["aggregate"]["combined_status_calibration"]
    lookalikes = report["aggregate"]["visual_lookalike_classification"]
    print(f"Combined status calibration: {calibration['correct']}/{calibration['expected']} = {calibration['accuracy']:.0%}")
    print(f"Visual lookalikes correctly rejected: {lookalikes['correct']}/{lookalikes['expected']} = {lookalikes['accuracy']:.0%}")