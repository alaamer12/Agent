from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_all_json_contracts_parse(self) -> None:
        for path in (
            ROOT / "registry" / "registry.json",
            ROOT / "report.schema.json",
            ROOT / "scouts" / "structural-scout" / "output.schema.json",
            ROOT / "scouts" / "impeccable-scout" / "output.schema.json",
            ROOT / "tests" / "visual" / "cases.json",
            ROOT / "tests" / "visual" / "results.json",
            ROOT / "tests" / "integration" / "cases.json",
            ROOT / "evals" / "evals.json",
            ROOT / "evals" / "agent-review-observations.json",
            ROOT / "evals" / "results.json",
            ROOT / "evals" / "agent-review-score.json",
        ):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_registry_has_documentation_for_each_pattern_and_a_test_disposition(self) -> None:
        registry = json.loads((ROOT / "registry" / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(len(registry["patterns"]), 67)
        for pattern in registry["patterns"]:
            with self.subTest(pattern=pattern["id"]):
                self.assertTrue((ROOT / "registry" / pattern["knowledge"]).is_file())
                self.assertTrue((ROOT / "registry" / pattern["detectionGuide"]).is_file())
                self.assertIn(pattern["tests"]["disposition"], {
                    "source-candidate-accuracy-tests-pending",
                    "browser-runtime-calibration-pending",
                    "visual-context-calibration-pending",
                })

    def test_progressive_workflows_and_report_separate_modalities(self) -> None:
        self.assertTrue((ROOT / "examples" / "page-review.md").is_file())
        self.assertTrue((ROOT / "examples" / "project-review.md").is_file())
        schema = json.loads((ROOT / "report.schema.json").read_text(encoding="utf-8"))
        finding_properties = schema["properties"]["findings"]["items"]["properties"]
        self.assertTrue({
            "structuralEvidence",
            "visualEvidence",
            "contextualAssessment",
            "exceptionsChecked",
            "counterevidence",
            "recommendations",
            "verification",
        }.issubset(finding_properties))

    def test_skill_package_has_standard_entry_references_and_evals(self) -> None:
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill_text.split("---", 2)
        self.assertEqual(frontmatter[0], "")
        self.assertIn("name: anti-slop", frontmatter[1])
        self.assertIn("description:", frontmatter[1])
        self.assertLessEqual(len(skill_text.splitlines()), 500)
        for relative in (
            "references/review-workflow.md",
            "references/evidence-and-reporting.md",
            "references/scout-contracts.md",
            "references/catalog-and-provenance.md",
            "references/operations-and-evaluation.md",
            "examples/page-review.md",
            "examples/project-review.md",
            "evals/README.md",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file())

        evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual(evals["skill_name"], "anti-slop")
        cases = evals["evals"]
        self.assertEqual(len(cases), 3)
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            with self.subTest(eval_id=case["id"]):
                self.assertTrue(case["prompt"].strip())
                self.assertTrue(case["expected_output"].strip())
                self.assertTrue(case["expectations"])
                for relative in case.get("files", []):
                    self.assertTrue((ROOT / relative).is_file(), relative)

        html_cases = evals["html_impact_evals"]
        self.assertEqual({case["tier"] for case in html_cases}, {"high", "medium", "low"})
        self.assertEqual(len(html_cases), 3)
        self.assertEqual(len({case["id"] for case in html_cases}), 3)
        self.assertTrue((ROOT / "evals" / "run_html_evals.py").is_file())
        self.assertTrue((ROOT / "evals" / "score_agent_reviews.py").is_file())
        for case in html_cases:
            with self.subTest(html_eval_id=case["id"]):
                self.assertTrue(case["prompt"].strip())
                self.assertTrue(case["expected_visual_pattern_ids"])
                self.assertTrue(case["expected_structural_pattern_ids"])
                self.assertEqual(case["viewport"]["width"], 1280)
                for relative in case["files"]:
                    self.assertTrue((ROOT / relative).is_file(), relative)

        score = json.loads((ROOT / "evals" / "agent-review-score.json").read_text(encoding="utf-8"))
        self.assertEqual(score["aggregate"]["structural_candidate_detection"]["recall"], 1.0)
        self.assertEqual(score["aggregate"]["visual_detection"]["recall"], 0.4444)
        self.assertEqual(score["aggregate"]["combined_positive_findings"]["false_negatives"], ["html-high-impact:text-occlusion"])

    def test_navigation_links_and_schema_read_rules_are_explicit(self) -> None:
        navigation_docs = (
            ROOT / "SKILL.md",
            ROOT / "scouts" / "structural-scout" / "README.md",
            ROOT / "scouts" / "impeccable-scout" / "AGENT.md",
            ROOT / "references" / "scout-contracts.md",
        )
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for document in navigation_docs:
            text = document.read_text(encoding="utf-8")
            for destination in link_pattern.findall(text):
                if destination.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                target = (document.parent / destination.split("#", 1)[0]).resolve()
                with self.subTest(document=document.relative_to(ROOT), destination=destination):
                    self.assertTrue(target.is_file(), destination)

        structural_guide = navigation_docs[1].read_text(encoding="utf-8")
        visual_guide = navigation_docs[2].read_text(encoding="utf-8")
        skill_text = navigation_docs[0].read_text(encoding="utf-8")
        self.assertIn("--json", structural_guide)
        self.assertIn("prose-only", structural_guide)
        self.assertIn("prose-only", visual_guide)
        self.assertIn("structural-scout/output.schema.json", skill_text)
        self.assertIn("impeccable-scout/output.schema.json", skill_text)
        self.assertIn("report.schema.json", skill_text)


if __name__ == "__main__":
    unittest.main()