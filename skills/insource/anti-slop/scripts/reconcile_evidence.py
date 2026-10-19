"""Merge independently produced scout evidence without losing modality or uncertainty."""

from __future__ import annotations

from typing import Any


def reconcile_pattern(
    pattern_id: str | None,
    structural: dict[str, Any] | None,
    visual: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return a contextual synthesis while preserving each scout's original evidence."""
    structural_candidate = bool(structural and structural.get("status") == "candidate")
    visual_status = visual.get("status") if visual else None

    if visual_status == "confirmed":
        status = "confirmed"
        resolution = "visual-contextual-evidence-confirms"
        contextual_review_required = False
    elif visual_status == "false-positive":
        status = "false-positive"
        resolution = "visual-contextual-evidence-explains-lookalike"
        contextual_review_required = False
    elif visual_status == "candidate" or structural_candidate:
        status = "candidate"
        resolution = "contextual-review-required" if structural_candidate and visual_status != "candidate" else "candidate-evidence-retained"
        contextual_review_required = True
    else:
        status = "not-observed"
        resolution = "no-relevant-evidence-returned"
        contextual_review_required = False

    disagreement = bool(
        structural_candidate
        and visual_status in {"false-positive", "not-observed", None}
    )
    if structural_candidate and visual_status == "confirmed":
        agreement = "structural-and-visual"
    elif structural_candidate and visual_status == "candidate":
        agreement = "both-candidate"
    elif structural_candidate and visual_status == "false-positive":
        agreement = "disagreement-resolved-by-context"
    elif structural_candidate and visual_status in {"not-observed", None}:
        agreement = "structural-only-unresolved"
    elif visual_status == "confirmed":
        agreement = "visual-only"
    elif visual_status == "candidate":
        agreement = "visual-candidate-only"
    elif visual_status == "false-positive":
        agreement = "contextual-lookalike"
    else:
        agreement = "no-finding"

    return {
        "patternId": pattern_id,
        "status": status,
        "agreement": agreement,
        "disagreement": disagreement,
        "contextualReviewRequired": contextual_review_required,
        "resolution": resolution,
        "structuralEvidence": structural,
        "visualEvidence": visual,
    }


def reconcile_case(case: dict[str, Any]) -> dict[str, Any]:
    structural = case.get("structural") or None
    visual = case.get("visual") or None
    pattern_id = (
        (structural or {}).get("patternId")
        or (visual or {}).get("patternId")
    )
    return reconcile_pattern(pattern_id, structural, visual)