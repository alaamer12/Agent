from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = ROOT / "anti-slop" / "scripts"
CASES_FILE = ROOT / "anti-slop" / "tests" / "integration" / "cases.json"
sys.path.insert(0, str(SCRIPT_DIR))

from reconcile_evidence import reconcile_case


class ScoutReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))["cases"]

    def test_cross_scout_cases_match_expected_outcomes(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["id"]):
                result = reconcile_case(case)
                expected = case["expected"]
                self.assertEqual(result["status"], expected["status"])
                if expected.get("doNotConfirmFromStructure"):
                    self.assertNotEqual(result["status"], "confirmed")
                if expected.get("preserveBothEvidence"):
                    self.assertEqual(result["structuralEvidence"], case.get("structural"))
                    self.assertEqual(result["visualEvidence"], case.get("visual"))
                if expected.get("preserveVisualEvidence"):
                    self.assertIsNotNone(result["visualEvidence"])
                if expected.get("contextualReviewRequired"):
                    self.assertTrue(result["contextualReviewRequired"])
                if expected.get("scopeLimited"):
                    self.assertEqual(result["status"], "not-observed")

    def test_structural_candidate_cannot_confirm_without_visual_confirmation(self) -> None:
        result = reconcile_case(
            {
                "structural": {"patternId": "gradient-text", "status": "candidate"},
                "visual": {"patternId": "gradient-text", "status": "not-observed"},
            }
        )
        self.assertEqual(result["status"], "candidate")
        self.assertTrue(result["contextualReviewRequired"])
        self.assertTrue(result["disagreement"])


if __name__ == "__main__":
    unittest.main()