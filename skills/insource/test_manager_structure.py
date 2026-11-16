from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import manager


class SkillStructureTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = tempfile.TemporaryDirectory(prefix="manager-structure-")
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name)
        self.registry = self.root / "registry"
        self.registry.mkdir()
        self.env = {**os.environ, "MANAGER_DB": str(self.root / "state.db"),
                    "MANAGER_HOME": str(self.root / "home"), "NO_COLOR": "1"}

    def write(self, path: Path, text: str = "# Instructions\n") -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def skill(self, relative: str, *, base: Path | None = None, version: bool = True) -> Path:
        path = (self.registry if base is None else base) / relative
        version_field = "version: 1.0.0\n" if version else ""
        self.write(path / "SKILL.md", f"---\nname: {path.name}\n{version_field}"
                   "description: Instructions for the fixture.\n---\n\n# Fixture\n")
        return path

    def cli(self, command: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(Path(manager.__file__).resolve()), command,
             "--registry", str(self.registry), "--no-color", *args],
            env=self.env, cwd=self.root, capture_output=True, text=True,
            encoding="utf-8", timeout=45,
        )

    def report(self, *args: str) -> dict:
        result = self.cli("report", "--json", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def link(self, source: Path, target: Path) -> None:
        manager.make_link(source, target)
        self.addCleanup(lambda: manager.remove_entry(target) if manager.is_link_like(target) else None)

    def test_support_folders_do_not_turn_a_skill_into_a_battery(self):
        skill = self.skill("normal")
        for directory in ("reference", "references", "examples", "assets", "scripts",
                          "templates", "research", "docs", "tests", "evals", "fixtures",
                          "data", "resources", "legacy"):
            self.write(skill / directory / "method.md")
        row = self.report()["skills"][0]
        self.assertEqual((row["type"], row["modules"], row["children"]), ("skill", [], []))

    def test_non_instruction_assets_do_not_become_modules(self):
        skill = self.skill("normal")
        self.write(skill / "images" / "logo.svg", "<svg/>\n")
        self.assertEqual(self.report()["skills"][0]["type"], "skill")

    def test_battery_modules_are_not_independent_report_rows(self):
        battery = self.skill("battery")
        self.write(battery / "first" / "method.md")
        self.write(battery / "second" / "README.md")
        rows = self.report()["skills"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["type"], "battery-skill")
        self.assertEqual(rows[0]["modules"], ["first", "second"])

    def test_module_detection_does_not_require_method_filename(self):
        battery = self.skill("battery")
        self.write(battery / "pillar" / "references" / "guide.md")
        self.assertEqual(self.report()["skills"][0]["type"], "battery-skill")

    def test_meta_children_have_their_own_types_and_nearest_parent(self):
        self.skill("outer")
        self.skill("outer/nested")
        child = self.skill("outer/nested/child")
        self.write(child / "mode" / "method.md")
        rows = {row["path"]: row for row in self.report()["skills"]}
        self.assertEqual(rows["outer"]["children"], ["nested"])
        self.assertEqual(rows["outer"]["type"], "meta-skill")
        self.assertEqual(rows["outer/nested"]["type"], "meta-skill")
        self.assertEqual(rows["outer/nested/child"]["type"], "battery-skill")
        self.assertEqual(rows["outer/nested/child"]["parent"], "outer/nested")
        self.assertEqual(rows["outer"]["issues"], [])

    def test_groups_are_not_skills_or_meta_parents(self):
        self.skill("Groups/Topic/deeper/member")
        rows = self.report()["skills"]
        self.assertEqual([(r["name"], r["type"], r["parent"]) for r in rows],
                         [("member", "skill", None)])
        result = self.cli("find", "Topic")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not a skill; holds", result.stdout)

    def test_support_named_skill_is_not_excluded(self):
        self.skill("Groups/Topic/assets")
        self.skill("parent")
        self.skill("parent/resources")
        rows = {row["path"]: row for row in self.report()["skills"]}
        self.assertIn("Groups/Topic/assets", rows)
        self.assertEqual(rows["parent"]["type"], "meta-skill")
        self.assertIn("parent/resources", rows)

    def test_template_skill_file_does_not_become_an_independent_child(self):
        self.skill("normal")
        self.skill("normal/assets/templates/sample")
        self.assertEqual([r["path"] for r in self.report()["skills"]], ["normal"])

    def test_mixed_composition_fails_strict_lint(self):
        root = self.skill("mixed")
        self.skill("mixed/independent")
        self.write(root / "internal" / "method.md")
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("mixed composition", result.stdout)
        self.assertIn("internal", result.stdout)
        row = next(r for r in self.report()["skills"] if r["path"] == "mixed")
        self.assertEqual(row["type"], "meta-skill")
        self.assertTrue(row["issues"])

    def test_clean_battery_lints_only_its_entrypoint(self):
        root = self.skill("battery")
        self.write(root / "mode" / "method.md", "No YAML needed for a module.\n")
        result = self.cli("lint", "--strict", "--no-version", "--verbose")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Battery-Skill", result.stdout)
        self.assertNotIn("missing frontmatter", result.stdout)

    def test_nested_child_metadata_is_linted(self):
        self.skill("meta")
        child = self.skill("meta/child")
        self.write(child / "SKILL.md", "# Missing frontmatter\n")
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("no frontmatter", result.stdout)
        self.assertIn("child", result.stdout)

    def test_nested_child_requires_version(self):
        self.skill("meta")
        self.skill("meta/child", version=False)
        result = self.cli("lint", "--strict")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("missing or invalid version", result.stdout)

    def test_duplicate_names_are_preserved_in_report(self):
        self.skill("one/shared")
        self.skill("two/shared")
        rows = self.report("shared")["skills"]
        self.assertEqual({row["path"] for row in rows}, {"one/shared", "two/shared"})
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("duplicate name", result.stdout)

    def test_report_summary_does_not_double_count_nested_files(self):
        root = self.skill("meta")
        child = self.skill("meta/child")
        self.write(child / "references" / "guide.md")
        report = self.report()
        self.assertEqual(report["total_files"], len(list(root.rglob("*.md"))))
        self.assertEqual(report["types"], {"skill": 1, "meta-skill": 1, "battery-skill": 0})

    def test_report_sort_and_filter_work_for_nested_children(self):
        self.skill("meta")
        self.skill("meta/child")
        report = self.report("--sort", "type", "--reverse")
        types = [r["type"] for r in report["skills"]]
        self.assertEqual(types, sorted(types, reverse=True))
        self.assertEqual([r["path"] for r in self.report("child")["skills"]], ["meta/child"])

    def test_empty_report_is_valid_json(self):
        report = self.report()
        self.assertEqual(report["skills"], [])
        self.assertEqual(report["total_files"], 0)

    def test_find_internal_module_never_calls_it_a_skill(self):
        root = self.skill("battery")
        self.write(root / "mode" / "method.md")
        result = self.cli("find", "mode")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("internal module of battery; not an independent skill", result.stdout)

    def test_find_explicit_external_skill_path_is_not_lost(self):
        external = self.skill("external", base=self.root / "other")
        result = self.cli("find", str(external))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Skill", result.stdout)
        self.assertIn(str(external), result.stdout)

    def test_agent_and_recorded_installs_use_structural_type(self):
        source = self.skill("battery")
        self.write(source / "mode" / "method.md")
        result = self.cli("skill", "battery", "--agents", "qoder", "--hard-copy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        destination = self.root / "project"
        result = self.cli("skill", "battery", "--into", str(destination), "--hard-copy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.cli("find", "battery")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("agent:qoder", result.stdout)
        self.assertIn("into (recorded)", result.stdout)
        self.assertEqual(result.stdout.count("Battery-Skill"), 3)

    def test_link_cycle_is_not_traversed(self):
        root = self.skill("normal")
        self.link(root, root / "loop")
        self.assertEqual(self.report()["skills"][0]["type"], "skill")

    def test_broken_agent_link_is_not_reported_as_a_live_skill(self):
        target = self.skill("target", base=self.root / "other")
        link = self.root / "home" / ".qoder" / "skills" / "target"
        self.link(target, link)
        target.rename(target.with_name("moved"))
        result = self.cli("find", "target")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("broken-link", result.stdout)
        self.assertIn("no live skill verified", result.stdout)

    def test_archive_and_hidden_entries_do_not_change_type(self):
        root = self.skill("normal")
        self.skill("normal/Archive/old")
        self.skill("normal/.hidden/internal")
        self.assertEqual(manager.classify_directory(root), "skill")

    def test_classification_reacts_to_entrypoint_changes(self):
        root = self.skill("changing")
        self.assertEqual(manager.classify_directory(root), "skill")
        self.write(root / "module" / "method.md")
        self.assertEqual(manager.classify_directory(root), "battery-skill")
        self.skill("changing/module")
        self.assertEqual(manager.classify_directory(root), "meta-skill")
        (root / "module" / "SKILL.md").unlink()
        self.assertEqual(manager.classify_directory(root), "battery-skill")


if __name__ == "__main__":
    unittest.main()
