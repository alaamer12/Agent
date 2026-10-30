from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
EVAL_ROOT = Path(__file__).resolve().parent
EVALS_PATH = EVAL_ROOT / "evals.json"
SCANNER_PATH = PACKAGE_ROOT / "scripts" / "structural_scout.py"


def _load_scanner() -> Any:
    spec = importlib.util.spec_from_file_location("anti_slop_structural_scout", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load structural scanner at {SCANNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _score(expected: set[str], observed: set[str]) -> dict[str, Any]:
    true_positives = expected & observed
    false_positives = observed - expected
    false_negatives = expected - observed
    precision = len(true_positives) / len(observed) if observed else (1.0 if not expected else 0.0)
    recall = len(true_positives) / len(expected) if expected else (1.0 if not observed else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "expected": sorted(expected),
        "observed": sorted(observed),
        "true_positives": sorted(true_positives),
        "false_positives": sorted(false_positives),
        "false_negatives": sorted(false_negatives),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def _capture(case: dict[str, Any], fixture: Path, screenshot_path: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is required to capture eval screenshots") from error

    browser_errors: list[str] = []
    viewport = case["viewport"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=viewport)
        page.on("pageerror", lambda error: browser_errors.append(str(error)))
        page.goto(fixture.as_uri(), wait_until="load")
        page.screenshot(path=str(screenshot_path), full_page=False)
        runtime = page.evaluate(
            """() => {
              const images = Array.from(document.images).map(image => ({
                src: image.getAttribute('src'),
                complete: image.complete,
                naturalWidth: image.naturalWidth,
                failed: image.complete && image.naturalWidth === 0
              }));
              const method = document.querySelector('.method');
              const methodState = method ? {
                text: method.textContent.trim(),
                clientWidth: method.clientWidth,
                scrollWidth: method.scrollWidth,
                clipped: method.scrollWidth > method.clientWidth
              } : null;
              const button = document.querySelector('.pay');
              const overlay = document.querySelector('.cover');
              let overlap = null;
              if (button && overlay) {
                const rect = button.getBoundingClientRect();
                const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
                overlap = {
                  buttonVisible: rect.width > 0 && rect.height > 0,
                  centerHitIsButton: hit === button || button.contains(hit),
                  hitElement: hit ? `${hit.tagName.toLowerCase()}${hit.className ? '.' + String(hit.className).trim().replace(/\\s+/g, '.') : ''}` : null
                };
              }
              return {images, methodState, primaryActionOverlap: overlap};
            }"""
        )
        browser.close()

    return {
        "screenshot": screenshot_path.relative_to(PACKAGE_ROOT).as_posix(),
        "viewport": viewport,
        "browser_errors": browser_errors,
        "runtime_observations": runtime,
    }


def run(output_path: Path, capture_screenshots: bool = True) -> dict[str, Any]:
    eval_data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    scanner = _load_scanner()
    results: dict[str, Any] = {
        "skill_name": eval_data["skill_name"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluation_scope": "three annotated local HTML impact cases; not a host LLM benchmark",
        "cases": [],
        "aggregate": {},
        "visual_agent_review": {
            "status": "not-run-by-local-script",
            "note": "Requires independent visual/contextual review of captured screenshots; no visual classification is inferred from HTML or browser measurements.",
        },
    }
    structural_expected: set[str] = set()
    structural_observed: set[str] = set()

    for case in eval_data["html_impact_evals"]:
        fixture = (PACKAGE_ROOT / case["files"][0]).resolve()
        if not fixture.is_file():
            raise FileNotFoundError(f"Missing eval fixture: {fixture}")
        findings, scanned_files = scanner.scan_paths([fixture])
        observed_ids = {finding["patternId"] for finding in findings}
        expected_ids = set(case["expected_structural_pattern_ids"])
        structural_expected.update(expected_ids)
        structural_observed.update(observed_ids)

        case_result: dict[str, Any] = {
            "id": case["id"],
            "tier": case["tier"],
            "fixture": fixture.relative_to(PACKAGE_ROOT).as_posix(),
            "impact_note": case["impact_note"],
            "structural_score": _score(expected_ids, observed_ids),
            "structural_findings": findings,
            "scanned_files": [Path(path).name for path in scanned_files],
        }
        if capture_screenshots:
            screenshot_dir = EVAL_ROOT / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f"{case['id']}.png"
            case_result["browser_capture"] = _capture(case, fixture, screenshot_path)
        results["cases"].append(case_result)

    results["aggregate"]["structural_candidate_score"] = _score(structural_expected, structural_observed)
    results["aggregate"]["structural_candidate_score"]["interpretation"] = (
        "Candidate-signature coverage only; structural hits do not confirm user-facing anti-patterns."
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Render and score the local anti-slop HTML impact evaluations.")
    parser.add_argument("--output", type=Path, default=EVAL_ROOT / "results.json")
    parser.add_argument("--no-screenshots", action="store_true", help="Run only the structural candidate score")
    args = parser.parse_args()
    results = run(args.output.resolve(), capture_screenshots=not args.no_screenshots)
    for case in results["cases"]:
        score = case["structural_score"]
        print(
            f"{case['id']} ({case['tier']}): structural P={score['precision']:.0%} "
            f"R={score['recall']:.0%} F1={score['f1']:.0%}; "
            f"observed={','.join(score['observed']) or 'none'}"
        )
    score = results["aggregate"]["structural_candidate_score"]
    print(
        f"Aggregate structural candidates: P={score['precision']:.0%} "
        f"R={score['recall']:.0%} F1={score['f1']:.0%}"
    )
    print(f"Results: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())