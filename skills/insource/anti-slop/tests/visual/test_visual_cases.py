from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VISUAL_ROOT = ROOT / "anti-slop" / "tests" / "visual"
CASES = VISUAL_ROOT / "cases.json"
RESULTS = VISUAL_ROOT / "results.json"
REGISTRY = ROOT / "anti-slop" / "registry" / "registry.json"


class VisualCalibrationManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        cls.results = json.loads(RESULTS.read_text(encoding="utf-8"))["cases"]
        cls.pattern_ids = {pattern["id"] for pattern in json.loads(REGISTRY.read_text(encoding="utf-8"))["patterns"]}

    def test_calibration_covers_obvious_subtle_and_legitimate_cases(self) -> None:
        case_ids = {case["id"] for case in self.cases}
        self.assertTrue({"obvious-slop", "subtle-slop", "legitimate-lookalike"}.issubset(case_ids))

    def test_fixture_and_screenshot_references_exist(self) -> None:
        for case in self.cases:
            html_paths = case["html"] if isinstance(case["html"], list) else [case["html"]]
            for relative in [*html_paths, *case["screenshots"]]:
                with self.subTest(case=case["id"], path=relative):
                    self.assertTrue((VISUAL_ROOT / relative).is_file())

    def test_expected_and_reviewed_classifications_match_registry(self) -> None:
        results_by_id = {case["id"]: case for case in self.results}
        self.assertEqual(len(results_by_id), len(self.results), "visual results contain duplicate case IDs")
        self.assertEqual(set(results_by_id), {case["id"] for case in self.cases})
        for case in self.cases:
            with self.subTest(case=case["id"]):
                result = results_by_id[case["id"]]
                self.assertEqual(
                    len({item["patternId"] for item in result["observed"]}),
                    len(result["observed"]),
                    "visual results contain duplicate pattern observations",
                )
                observed = {item["patternId"]: item for item in result["observed"]}
                self.assertEqual(
                    len({item["patternId"] for item in case["expected"]}),
                    len(case["expected"]),
                    "visual case contains duplicate expected pattern IDs",
                )
                expected_ids = {item["patternId"] for item in case["expected"]}
                self.assertEqual(set(observed), expected_ids)
                for expected in case["expected"]:
                    pattern_id = expected["patternId"]
                    self.assertIn(pattern_id, self.pattern_ids)
                    self.assertIn(pattern_id, observed)
                    self.assertEqual(observed[pattern_id]["status"], expected["status"])
                for pattern_id in case.get("expectedNotConfirmed", []):
                    self.assertNotEqual(observed[pattern_id]["status"], "confirmed")


if __name__ == "__main__":
    unittest.main()