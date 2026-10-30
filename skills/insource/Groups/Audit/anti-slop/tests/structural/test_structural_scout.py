from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "anti-slop" / "scripts"
FIXTURE_DIR = ROOT / "anti-slop" / "tests" / "fixtures"
sys.path.insert(0, str(SCRIPT_DIR))

import structural_scout


CASES = (
    "gradient-text",
    "repeating-stripes-gradient",
    "layout-transition",
    "marquee",
    "justified-text",
    "wide-tracking",
    "side-tab",
    "gpt-thin-border-wide-shadow",
    "images-move-on-hover",
    "broken-image",
    "all-caps-body",
    "nested-cards",
    "repeated-container-text",
    "skipped-heading",
    "em-dash-overuse",
)


def finding_ids(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    return {finding["patternId"] for finding in structural_scout.scan_text(source, str(path))}


class StructuralScoutAccuracyTests(unittest.TestCase):
    def test_positive_and_negative_fixtures_for_every_detector(self) -> None:
        for pattern_id in CASES:
            with self.subTest(pattern_id=pattern_id):
                positive = sorted((FIXTURE_DIR / pattern_id / "positive").glob("*"))
                negative = sorted((FIXTURE_DIR / pattern_id / "negative").glob("*"))
                self.assertTrue(positive, f"missing positive fixture for {pattern_id}")
                self.assertTrue(negative, f"missing negative fixture for {pattern_id}")
                self.assertTrue(
                    any(pattern_id in finding_ids(path) for path in positive),
                    f"positive fixture did not produce candidate {pattern_id}",
                )
                self.assertFalse(
                    any(pattern_id in finding_ids(path) for path in negative),
                    f"negative fixture incorrectly produced candidate {pattern_id}",
                )

    def test_exception_fixtures_are_preserved_as_candidates_or_silent_as_appropriate(self) -> None:
        for pattern_id in CASES:
            with self.subTest(pattern_id=pattern_id):
                exceptions = sorted((FIXTURE_DIR / pattern_id / "exceptions").glob("*"))
                self.assertTrue(exceptions, f"missing exception fixture for {pattern_id}")
                for path in exceptions:
                    findings = structural_scout.scan_text(path.read_text(encoding="utf-8"), str(path))
                    matching = [item for item in findings if item["patternId"] == pattern_id]
                    if pattern_id in {"all-caps-body", "skipped-heading"}:
                        self.assertFalse(matching, "the exception fixture is outside the structural candidate signature")
                    else:
                        self.assertTrue(matching, "source similarity remains a candidate, never a confirmation")
                        self.assertTrue(all(item["status"] == "candidate" for item in matching))

    def test_detector_inventory_matches_registry_disposition(self) -> None:
        registry_path = ROOT / "anti-slop" / "registry" / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(structural_scout.candidate_detector_ids(registry), set(CASES))

    def test_em_dash_detector_requires_saturation_not_a_few_dashes(self) -> None:
        sparse = ("x" * 640 + " — ") * 8
        self.assertNotIn("em-dash-overuse", {f["patternId"] for f in structural_scout.scan_text(sparse, "copy.txt")})

    def test_findings_are_structural_candidates_with_reproducible_locations(self) -> None:
        fixture = FIXTURE_DIR / "gradient-text" / "positive" / "gradient-text.css"
        findings = structural_scout.scan_text(fixture.read_text(encoding="utf-8"), str(fixture))
        finding = next(item for item in findings if item["patternId"] == "gradient-text")
        self.assertEqual(finding["evidenceModality"], "structural")
        self.assertEqual(finding["status"], "candidate")
        self.assertEqual(finding["confidence"], "candidate")
        self.assertTrue(finding["path"].endswith("gradient-text.css"))
        self.assertGreaterEqual(finding["line"], 1)
        self.assertTrue(finding["snippet"])

    def test_registry_routed_selection_limits_findings(self) -> None:
        fixture = FIXTURE_DIR / "gradient-text" / "positive" / "gradient-text.css"
        findings, scanned = structural_scout.scan_paths([fixture], {"gradient-text"})
        self.assertEqual({finding["patternId"] for finding in findings}, {"gradient-text"})
        self.assertEqual(len(scanned), 1)


if __name__ == "__main__":
    unittest.main()