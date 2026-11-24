from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import manager


class ManagerFixture(unittest.TestCase):
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

    def skill(self, relative: str, *, base: Path | None = None, version: bool = True,
              specialized: str | None = "none") -> Path:
        path = (self.registry if base is None else base) / relative
        version_field = "version: 1.0.0\n" if version else ""
        specialized_field = "" if specialized is None else f"specialized: {specialized}\n"
        self.write(path / "SKILL.md", f"---\nname: {path.name}\n{version_field}{specialized_field}"
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


class SkillStructureTests(ManagerFixture):
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


class CrossreferenceTests(ManagerFixture):
    def crossreference(self, *, expected_code: int = 0) -> dict:
        result = self.cli("crossreference", "--json")
        self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_direction_is_not_assumed_to_be_mutual(self):
        alpha = self.skill("alpha")
        self.skill("beta")
        self.write(alpha / "references" / "guide.md", "Use /beta.\n")
        edges = self.crossreference()["edges"]
        self.assertEqual([(e["from"], e["to"], e["mutual"]) for e in edges],
                         [("alpha", "beta", False)])
        self.assertEqual(edges[0]["evidence"], [{"file": "alpha/references/guide.md",
                                               "line": 1, "text": "Use /beta."}])

    def test_mutual_reference_requires_both_directions(self):
        alpha = self.skill("alpha")
        beta = self.skill("beta")
        self.write(alpha / "README.md", "`beta`\n")
        self.write(beta / "README.md", "**alpha**\n")
        edges = self.crossreference()["edges"]
        self.assertEqual({(e["from"], e["to"]) for e in edges},
                         {("alpha", "beta"), ("beta", "alpha")})
        self.assertTrue(all(e["mutual"] for e in edges))

    def test_matching_is_whole_token_case_insensitive_and_line_deduplicated(self):
        alpha = self.skill("alpha")
        self.skill("beta-tool")
        self.write(alpha / "guide.md", "beta-tool-extra pre-beta-tool beta_tool\n"
                   "/BETA-TOOL and `beta-tool` and **beta-tool**\n"
                   "[tool](../beta-tool/SKILL.md)\n")
        edge = self.crossreference()["edges"][0]
        self.assertEqual(edge["count"], 2)
        self.assertEqual([item["line"] for item in edge["evidence"]], [2, 3])

    def test_long_line_evidence_includes_the_matched_name(self):
        alpha = self.skill("alpha")
        self.skill("beta")
        self.write(alpha / "guide.md", "unrelated context " * 100 + "use /beta.\n")
        evidence = self.crossreference()["edges"][0]["evidence"][0]
        self.assertIn("/beta", evidence["text"])
        self.assertLessEqual(len(evidence["text"]), 240)

    def test_self_references_and_unknown_names_are_not_edges(self):
        alpha = self.skill("alpha")
        self.write(alpha / "guide.md", "/alpha unknown-skill\n")
        self.assertEqual(self.crossreference()["edges"], [])

    def test_meta_child_owns_its_reference_not_parent(self):
        self.skill("meta")
        child = self.skill("meta/child")
        self.skill("peer")
        self.write(child / "guide.md", "Use peer.\n")
        edges = self.crossreference()["edges"]
        self.assertEqual([(e["source"], e["target"]) for e in edges], [("meta/child", "peer")])

    def test_battery_module_reference_belongs_to_battery(self):
        battery = self.skill("battery")
        self.skill("peer")
        self.write(battery / "mode" / "method.md", "Use peer.\n")
        edges = self.crossreference()["edges"]
        self.assertEqual([(e["source"], e["target"]) for e in edges], [("battery", "peer")])

    def test_command_reports_references_across_all_skills(self):
        alpha, beta, gamma, delta = [self.skill(name) for name in ("alpha", "beta", "gamma", "delta")]
        self.write(alpha / "guide.md", "beta\n")
        self.write(beta / "guide.md", "gamma\n")
        self.write(gamma / "guide.md", "delta\n")
        result = self.crossreference()
        self.assertEqual({(e["from"], e["to"]) for e in result["edges"]},
                         {("alpha", "beta"), ("beta", "gamma"), ("gamma", "delta")})
        self.assertEqual(result["stats"]["skills"], 4)
        self.assertEqual(result["stats"]["edges"], 3)

    def test_ambiguous_target_names_are_not_invented_edges(self):
        source = self.skill("source")
        self.skill("one/shared")
        self.skill("two/shared")
        self.write(source / "guide.md", "Use shared.\n")
        result = self.crossreference(expected_code=1)
        self.assertEqual(result["edges"], [])
        self.assertEqual(result["ambiguous"][0]["candidates"], ["one/shared", "two/shared"])
        self.assertEqual(result["ambiguous"][0]["evidence"][0]["line"], 1)

    def test_archives_resources_hidden_and_binary_content_are_excluded(self):
        alpha = self.skill("alpha")
        self.skill("beta")
        for name in ("Archive", "_Archive", "_Resources", ".hidden"):
            hidden = self.skill(f"{name}/hidden")
            self.write(hidden / "guide.md", "beta\n")
        self.write(alpha / "image.png", "beta\n")
        self.write(alpha / ".private.md", "beta\n")
        result = self.crossreference()
        self.assertEqual(result["edges"], [])
        self.assertEqual(result["stats"]["skills"], 2)
        self.assertEqual(result["stats"]["files_scanned"], 2)

    def test_invalid_document_encoding_reports_incomplete_scan(self):
        alpha = self.skill("alpha")
        (alpha / "bad.md").write_bytes(b"\xff\xfe\x80")
        result = self.crossreference(expected_code=1)
        self.assertEqual(result["errors"][0]["file"], "alpha/bad.md")

    def test_no_database_is_created_by_crossreference(self):
        self.skill("alpha")
        self.crossreference()
        self.assertFalse(Path(self.env["MANAGER_DB"]).exists())

    def test_positional_values_are_rejected_even_for_existing_skills(self):
        self.skill("alpha")
        self.skill("beta")
        for values in (("alpha",), ("missing",), ("alpha", "beta")):
            with self.subTest(values=values):
                result = self.cli("crossreference", *values)
                self.assertEqual(result.returncode, 2)
                self.assertIn(f"unrecognized arguments: {' '.join(values)}", result.stderr)

    def test_empty_inventory_is_valid_json(self):
        result = self.crossreference()
        self.assertEqual(result["edges"], [])
        self.assertEqual(result["stats"]["files_scanned"], 0)

    def test_verbose_table_has_real_evidence(self):
        alpha = self.skill("alpha")
        self.skill("beta")
        self.write(alpha / "guide.md", "Use /beta.\n")
        result = self.cli("crossreference", "--verbose")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Mutual", result.stdout)
        self.assertIn("alpha/guide.md:1", result.stdout)
        self.assertIn("Use /beta.", result.stdout)

    def test_each_document_is_opened_once_including_meta_children(self):
        self.skill("meta")
        child = self.skill("meta/child")
        self.skill("peer")
        self.write(child / "guide.md", "peer\n")
        opened = []
        original_open = Path.open

        def counted_open(path, *args, **kwargs):
            opened.append(path)
            return original_open(path, *args, **kwargs)

        skills = manager.walk_skills(self.registry, prune=False)
        with patch.object(Path, "open", counted_open):
            result = manager.scan_crossreferences(self.registry, skills)
        expected = set(self.registry.rglob("*.md"))
        self.assertEqual(set(opened), expected)
        self.assertEqual(len(opened), len(expected))
        self.assertEqual(result["stats"]["files_scanned"], len(expected))


class SpecializedLintTests(ManagerFixture):
    def lint(self) -> subprocess.CompletedProcess:
        return self.cli("lint", "--strict", "--no-version")

    def test_general_and_single_technology_values_pass(self):
        self.skill("dtb", specialized="none")
        self.skill("scss", specialized="scss")
        self.skill("native", specialized="react-native")
        self.skill("next", specialized="next.js")
        self.skill("sharp", specialized="c#")
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("specialized", result.stdout)

    def test_missing_value_fails_strict_lint(self):
        self.skill("bare", specialized=None)
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("missing specialized", result.stdout)

    def test_invalid_values_fail_strict_lint(self):
        for value in ('""', "General", "general", "n/a", "[scss]", "react native", "none, scss"):
            with self.subTest(value=value):
                skill = self.skill("odd", specialized=value)
                result = self.lint()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("invalid specialized", result.stdout)
                (skill / "SKILL.md").unlink()

    def test_comma_list_is_discouraged(self):
        self.skill("mobile", specialized="react-native, expo")
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("specialized lists 2 technologies", result.stdout)
        self.assertNotIn("invalid specialized", result.stdout)

    def test_meta_children_are_checked_but_battery_modules_are_not(self):
        self.skill("meta")
        self.skill("meta/child", specialized=None)
        battery = self.skill("battery")
        self.write(battery / "mode" / "method.md", "No frontmatter in a module.\n")
        result = self.lint()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout.count("missing specialized"), 1)
        self.assertIn("child", result.stdout)

    def test_foreign_agent_skills_are_not_checked(self):
        self.skill("vendor", base=Path(self.env["MANAGER_HOME"]) / ".qoder" / "skills", specialized=None)
        result = self.lint()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_aliases_are_rejected_with_the_canonical_name(self):
        for alias, canonical in (("tailwindcss", "tailwind"), ("tw", "tailwind"), ("gh", "github"),
                                 ("ts", "typescript"), ("postgres", "postgresql"), ("csharp", "c#")):
            with self.subTest(alias=alias):
                skill = self.skill("odd", specialized=alias)
                result = self.lint()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(f"use '{canonical}'", result.stdout)
                (skill / "SKILL.md").unlink()

    def test_canonical_names_pass(self):
        for value in ("tailwind", "github", "typescript", "postgresql", "c#", "next.js", "node.js", "win32"):
            with self.subTest(value=value):
                skill = self.skill("odd", specialized=value)
                result = self.lint()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                (skill / "SKILL.md").unlink()


class SkillLengthTests(ManagerFixture):
    def grow(self, skill: Path, target: int) -> int:
        f = skill / "SKILL.md"
        lines = f.read_text(encoding="utf-8").splitlines()
        lines = (lines + ["filler rule"] * target)[:target]
        f.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return len(f.read_text(encoding="utf-8").splitlines())

    def lint_strict(self) -> subprocess.CompletedProcess:
        return self.cli("lint", "--strict", "--no-version")

    def test_long_entrypoint_with_other_files_fails(self):
        skill = self.skill("router")
        self.write(skill / "references" / "guide.md")
        count = self.grow(skill, 210)
        result = self.lint_strict()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(f"SKILL.md has {count} lines", result.stdout)

    def test_solo_long_skill_passes(self):
        self.grow(self.skill("monolith"), 210)
        result = self.lint_strict()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("SKILL.md has", result.stdout)

    def test_boundary_is_under_200(self):
        skill = self.skill("edge")
        self.write(skill / "references" / "guide.md")
        self.assertEqual(self.grow(skill, 199), 199)
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stderr)
        self.assertEqual(self.grow(skill, 200), 200)
        result = self.lint_strict()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("SKILL.md has 200 lines", result.stdout)

    def test_skill_length_can_be_accepted(self):
        skill = self.skill("waived")
        self.write(skill / "references" / "guide.md")
        self.grow(skill, 230)
        self.write(skill / "SKILL.md",
                   (skill / "SKILL.md").read_text(encoding="utf-8").replace(
                       "specialized: none\n",
                       "specialized: none\nlint-accept:\n"
                       '  skill-length: "Reference tables are the payload."\n'))
        result = self.lint_strict()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        verbose = self.cli("lint", "--strict", "--no-version", "--verbose")
        self.assertIn("skill-length", verbose.stdout)
        self.assertIn("Reference tables are the payload.", verbose.stdout)

    def test_battery_module_length_is_not_checked(self):
        battery = self.skill("battery")
        self.write(battery / "mode" / "method.md", "rule\n" * 250)
        result = self.lint_strict()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_foreign_agent_skills_are_not_policed(self):
        vendor = self.skill("vendor", base=Path(self.env["MANAGER_HOME"]) / ".qoder" / "skills")
        self.write(vendor / "references" / "guide.md")
        self.grow(vendor, 210)
        result = self.lint_strict()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_report_flags_solo_skills(self):
        self.skill("monolith")
        self.write(self.skill("withrefs") / "references" / "guide.md")
        rows = {r["name"]: r for r in self.report()["skills"]}
        self.assertTrue(rows["monolith"]["solo"])
        self.assertFalse(rows["withrefs"]["solo"])
        table = self.cli("report", "--no-color")
        self.assertEqual(table.returncode, 0, table.stderr)
        self.assertIn("SKILL.md only", table.stdout)
        self.assertIn("Solo SKILL.md skills", table.stdout)


class LintAcceptTests(ManagerFixture):
    def hybrid(self, accept_yaml: str = "", *, specialized: bool = True) -> Path:
        root = self.skill("hybrid")
        self.skill("hybrid/child")
        self.write(root / "mode" / "method.md")
        spec = "specialized: none\n" if specialized else ""
        self.write(root / "SKILL.md",
                   f"---\nname: hybrid\nversion: 1.0.0\n{spec}{accept_yaml}"
                   "description: Fixture.\n---\n\n# Fixture\n")
        return root

    def test_accepted_hybrid_passes_strict_lint(self):
        self.hybrid('lint-accept:\n  mixed-composition: "Intentional hybrid battery+meta."\n')
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("mixed composition", result.stdout)
        self.assertIn("Accepted findings", result.stdout)

    def test_accepted_finding_is_auditable_in_verbose(self):
        self.hybrid('lint-accept:\n  mixed-composition: "Keep as-is."\n')
        result = self.cli("lint", "--strict", "--no-version", "--verbose")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("accepted findings (1)", result.stdout)
        self.assertIn("Keep as-is.", result.stdout)

    def test_unaccepted_hybrid_still_fails(self):
        self.hybrid()
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("mixed composition", result.stdout)

    def test_empty_reason_is_rejected_and_finding_still_fires(self):
        self.hybrid('lint-accept:\n  mixed-composition: ""\n')
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("needs a non-empty reason", result.stdout)
        self.assertIn("mixed composition", result.stdout)

    def test_unknown_rule_is_rejected(self):
        self.hybrid('lint-accept:\n  bogus-rule: "why"\n')
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("unknown rule 'bogus-rule'", result.stdout)
        self.assertIn("mixed composition", result.stdout)

    def test_non_mapping_value_is_rejected(self):
        self.hybrid("lint-accept: mixed-composition\n")
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("must be a mapping", result.stdout)

    def test_acceptance_only_waives_the_named_rule(self):
        self.hybrid('lint-accept:\n  mixed-composition: "Hybrid is intentional."\n', specialized=False)
        result = self.cli("lint", "--strict", "--no-version")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("missing specialized", result.stdout)
        self.assertNotIn("mixed composition", result.stdout)


class SyncAuditTests(ManagerFixture):
    def agent_root(self) -> Path:
        return Path(self.env["MANAGER_HOME"]) / ".qoder" / "skills"

    def sync_issues(self) -> str:
        result = self.cli("lint", "--verbose", "--no-version")
        self.assertNotIn("Traceback", result.stderr)
        start = result.stdout.find("synchronization issues (")
        return result.stdout[start:] if start >= 0 else ""

    def test_real_folder_without_entrypoint_is_reported(self):
        self.skill("wrapped", base=self.agent_root() / "wrapper")
        issues = self.sync_issues()
        self.assertIn("missing-skill", issues)
        self.assertIn("wrapper", issues)
        self.assertIn("wrapped", issues)

    def test_dangling_link_is_reported(self):
        target = self.skill("gone", base=self.root / "other")
        self.link(target, self.agent_root() / "gone")
        target.rename(target.with_name("moved"))
        self.assertIn("broken-link", self.sync_issues())

    def test_link_to_folder_without_entrypoint_is_reported(self):
        module = self.write(self.root / "other" / "module" / "method.md").parent
        self.link(module, self.agent_root() / "module")
        self.assertIn("missing-skill", self.sync_issues())

    def test_healthy_copies_and_hidden_folders_are_not_reported(self):
        self.skill("healthy", base=self.agent_root())
        self.write(self.agent_root() / ".system" / "notes.md")
        self.assertEqual(self.sync_issues(), "")


class AgentSourceTests(ManagerFixture):
    def test_agent_uses_relocated_source_not_stale_root_file(self):
        self.write(self.registry / "AGENTS.md", "Stale root instructions.\n")
        source = self.write(self.registry / "_Resources" / "AGENTS.md", "Current instructions.\n")
        result = self.cli("agent", "--agents", "qoder", "--hard-copy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        target = Path(self.env["MANAGER_HOME"]) / ".qoder" / "agents.md"
        self.assertEqual(target.read_text(encoding="utf-8"), source.read_text(encoding="utf-8"))

    def test_agent_error_names_the_relocated_source(self):
        self.write(self.registry / "AGENTS.md", "Not the source anymore.\n")
        result = self.cli("agent", "--agents", "qoder", "--hard-copy")
        self.assertEqual(result.returncode, 1)
        self.assertIn(str(self.registry / "_Resources" / "AGENTS.md"), result.stderr)

    def test_agent_dry_run_reads_new_source_without_deploying(self):
        self.write(self.registry / "_Resources" / "AGENTS.md")
        result = self.cli("agent", "--agents", "qoder", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("_Resources", result.stdout)
        self.assertFalse(Path(self.env["MANAGER_HOME"]).exists())


class ArgumentHintTests(ManagerFixture):
    def surface(self, name: str, body: str, *, hint: str | None = None,
                accept: bool = False) -> Path:
        fm = ("---\n" f"name: {name}\n" "version: 1.0.0\n" "specialized: none\n"
              "description: Fixture description.\n")
        if accept:
            fm += ('lint-accept:\n'
                   '  argument-hint: "Explains README command sections; takes no commands."\n')
        if hint is not None:
            fm += f'argument-hint: "{hint}"\n'
        path = self.registry / name / "SKILL.md"
        self.write(path, fm + "---\n\n# Fixture\n\n" + body)
        return path

    def lint_strict(self) -> subprocess.CompletedProcess:
        return self.cli("lint", "--strict", "--no-version")

    def test_interface_heading_without_hint_warns(self):
        self.surface("demo", "## Commands\n\nDo the thing.\n")
        result = self.lint_strict()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("argument-hint", result.stdout)
        self.assertIn('heading "Commands"', result.stdout)

    def test_declared_hint_silences_the_rule(self):
        self.surface("demo", "## Commands\n\nDo the thing.\n", hint="[run] <target>")
        result = self.lint_strict()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_empty_hint_counts_as_missing(self):
        self.surface("demo", "## Commands\n\nDo the thing.\n", hint="")
        self.assertEqual(self.lint_strict().returncode, 1)

    def test_own_slash_usage_with_argument_warns(self):
        self.surface("demo", "Reach it as `/demo run <thing>` anytime.\n")
        self.assertIn("self-slash", self.lint_strict().stdout)

    def test_bare_slash_invocation_alone_does_not_fire(self):
        self.surface("demo", "Type `/demo` and the run starts.\n")
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stdout)

    def test_other_skills_commands_are_not_signals(self):
        self.surface("demo", "Pair with `/other-tool <thing>` and `/second thing` freely.\n")
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stdout)

    def test_prose_vocabulary_is_not_a_signal(self):
        self.surface("demo", "Consider dark mode, maintenance windows and shell commands "
                             "in CI; the command list lives upstream.\n")
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stdout)

    def test_numbered_outline_and_prose_headings_do_not_fire(self):
        self.surface("demo", "## 7. Commands, examples, and verification honesty\n\n"
                             "## Why this needs a different mode than normal questions\n\n"
                             "## Step 6 - Sweep mode\n\nText.\n")
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stdout)

    def test_short_numbered_mode_heading_fires(self):
        self.surface("demo", "### 2. Select mode\n\n- **Open**: discover.\n- **Strict**: named axes.\n")
        self.assertIn("Select mode", self.lint_strict().stdout)

    def test_mode_letters_fire(self):
        self.surface("demo", "Mode A answers from what is there. Mode B recovers the thread.\n")
        self.assertIn("mode letters", self.lint_strict().stdout)

    def test_single_weak_signal_is_not_enough(self):
        self.surface("demo", "The two commands run in order.\n")
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stdout)

    def test_two_weak_signals_fire(self):
        self.surface("demo", "The three commands - micro, component, transition.\n\n"
                             "Commands: shown per run.\n")
        self.assertEqual(self.lint_strict().returncode, 1, self.lint_strict().stdout)

    def test_frontmatter_description_words_are_not_body_signals(self):
        path = self.surface("demo", "Just a fixture body.\n")
        text = path.read_text(encoding="utf-8").replace(
            "description: Fixture description.",
            "description: Handles three commands and two modes for the project.")
        self.write(path, text)
        self.assertEqual(self.lint_strict().returncode, 0, self.lint_strict().stdout)

    def test_misfire_can_be_accepted(self):
        self.surface("demo", "## Commands\n\nThe README documents its commands.\n", accept=True)
        result = self.lint_strict()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        verbose = self.cli("lint", "--strict", "--no-version", "--verbose")
        self.assertIn("argument-hint", verbose.stdout)
        self.assertIn("Explains README command sections", verbose.stdout)


class SkillRemoveTests(ManagerFixture):
    def _use_sandbox_env(self) -> None:
        """Point the in-process manager helpers at the sandbox db/home."""
        for key in ("MANAGER_DB", "MANAGER_HOME"):
            old = os.environ.get(key)
            os.environ[key] = self.env[key]

            def _restore(key=key, old=old) -> None:
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old

            self.addCleanup(_restore)

    def _lock_data(self) -> str:
        import sqlite3
        conn = sqlite3.connect(self.env["MANAGER_DB"])
        try:
            row = conn.execute("select data from kv where store='lock'").fetchone()
            return row[0] if row else ""
        finally:
            conn.close()

    def test_remove_uninstalls_agent_link_without_touching_source(self):
        source = self.skill("solo")
        result = self.cli("skill", "solo", "--agents", "qoder", "-l")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        link = Path(self.env["MANAGER_HOME"]) / ".qoder" / "skills" / "solo"
        self.assertTrue(manager.is_link_like(link))
        self.assertIn("solo", self._lock_data())
        result = self.cli("skill", "-U", "solo", "--agents", "qoder")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(link.exists() or manager.is_link_like(link))
        self.assertTrue((source / "SKILL.md").is_file())
        self.assertNotIn("solo", self._lock_data())

    def test_remove_hard_copy_drops_record_and_backs_up(self):
        self._use_sandbox_env()
        source = self.skill("solo")
        destination = self.root / "project"
        result = self.cli("skill", "solo", "--into", str(destination), "--hard-copy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        target = destination / "solo"
        self.assertTrue(target.is_dir() and not manager.is_link_like(target))
        self.assertIsNotNone(manager.get_record(self.registry, target))
        result = self.cli("skill", "-U", "solo", "--into", str(destination))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("removed copy", result.stdout)
        self.assertFalse(target.exists())
        self.assertIsNone(manager.get_record(self.registry, target))
        self.assertTrue((source / "SKILL.md").is_file())
        backups = list(Path(self.env["MANAGER_HOME"]).glob("skill-remove-backup-*.zip"))
        self.assertEqual(len(backups), 1)

    def test_remove_refuses_unmanaged_directory_without_force(self):
        destination = self.root / "project"
        handmade = destination / "handmade"
        self.write(handmade / "SKILL.md", "# mine\n")
        result = self.cli("skill", "-U", "handmade", "--into", str(destination))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skipped", result.stdout)
        self.assertTrue((handmade / "SKILL.md").is_file())
        result = self.cli("skill", "-U", "--force", "handmade", "--into", str(destination))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(handmade.exists())

    def test_remove_never_follows_nested_junctions(self):
        destination = self.root / "project"
        child = self.skill("child", base=self.root / "elsewhere")
        parent = destination / "parent"
        self.write(parent / "SKILL.md", "# parent\n")
        manager.make_link(child, parent / "nested")
        self.addCleanup(lambda: manager.remove_entry(parent / "nested")
                        if manager.is_link_like(parent / "nested") else None)
        result = self.cli("skill", "-U", "--force", "-B", "parent", "--into", str(destination))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(parent.exists())
        self.assertTrue((child / "SKILL.md").is_file())

    def test_remove_protects_registry_sources_and_dry_run_is_inert(self):
        source = self.skill("solo")
        destination = self.root / "project"
        self.cli("skill", "solo", "--into", str(destination), "--hard-copy")
        result = self.cli("skill", "-U", "solo", "--into", str(destination), "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("would remove copy", result.stdout)
        self.assertTrue((destination / "solo").is_dir())
        result = self.cli("skill", "-U", "--force", "solo", "--into", str(self.registry))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("protected", result.stdout)
        self.assertTrue((source / "SKILL.md").is_file())

    def test_remove_requires_names_or_all(self):
        result = self.cli("skill", "-U")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--remove", result.stdout + result.stderr)

    def test_remove_accepts_multiple_names_in_one_call(self):
        destination = self.root / "project"
        for name, mode in (("one", []), ("two", []), ("three", ["--hard-copy"])):
            self.skill(name)
            result = self.cli("skill", name, "--into", str(destination), *mode)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.cli("skill", "-U", "one", "two", "three", "three",
                          "--into", str(destination))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ("one", "two", "three"):
            self.assertFalse((destination / name).exists())
        self.assertEqual(result.stdout.count("| three "), 1)


class AgentsTableTests(ManagerFixture):
    def _table(self) -> dict:
        result = self.cli("agents", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_defaults_are_seeded_once_from_the_builtin_locations(self):
        table = self._table()
        self.assertEqual(
            sorted(table), ["claude", "gemini", "junie", "opencode", "qoder"])
        self.assertEqual(table["qoder"]["skill_dir"], ".qoder/skills")
        self.assertEqual(table["qoder"]["origin"], "seed")
        # seeding is idempotent: a second call does not duplicate or reset
        self.cli("agents", "--json")
        self.assertEqual(sorted(self._table()), sorted(table))

    def test_deploy_uses_registered_locations_not_the_builtin_paths(self):
        source = self.skill("solo")
        custom = self.root / "elsewhere" / "skills"
        result = self.cli("agents", "--set", "toolmy", "--skill-dir", str(custom))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self._table()["toolmy"]["origin"], "user")
        result = self.cli("skill", "solo", "--agents", "toolmy")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((custom / "solo" / "SKILL.md").is_file())

    def test_update_with_differing_values_errors_unless_override(self):
        other = self.root / "second"
        self.cli("agents", "--set", "toolmy", "--skill-dir", str(self.root / "first"))
        result = self.cli("agents", "--set", "toolmy", "--skill-dir", str(other))
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflict", result.stdout + result.stderr)
        self.assertIn("--override", result.stdout + result.stderr)
        self.assertNotIn(str(other), self._table()["toolmy"]["skill_dir"])
        result = self.cli("agents", "--set", "toolmy", "--skill-dir", str(other), "--override")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("updated", result.stdout)
        self.assertEqual(self._table()["toolmy"]["skill_dir"].replace("\\", "/"),
                         other.as_posix())

    def test_sharing_another_agents_skill_dir_errors_unless_override(self):
        shared = (self.root / "shared").as_posix()
        self.cli("agents", "--set", "first", "--skill-dir", str(self.root / "shared"))
        result = self.cli("agents", "--set", "second", "--skill-dir", str(self.root / "shared"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("already belongs to agent 'first'", result.stdout + result.stderr)
        result = self.cli("agents", "--set", "second", "--skill-dir", str(self.root / "shared"),
                          "--override")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("second", self._table())

    def test_removed_default_stays_removed_and_rejects_deployment(self):
        self.skill("solo")
        result = self.cli("agents", "--remove", "qoder")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("qoder", self._table())
        result = self.cli("agents", "--json")  # any command triggers connect + re-seed
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("qoder", self._table())
        result = self.cli("skill", "solo", "--agents", "qoder")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown agent", result.stdout + result.stderr)

    def test_reregistering_a_tombstone_restores_use(self):
        self.cli("agents", "--remove", "qoder")
        custom = self.root / "revived"
        result = self.cli("agents", "--set", "qoder", "--skill-dir", str(custom))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("re-registered", result.stdout)
        self.skill("solo")
        result = self.cli("skill", "solo", "--agents", "qoder")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((custom / "solo" / "SKILL.md").is_file())

    def test_unknown_agent_error_lists_registered_names_with_hint(self):
        self.skill("solo")
        result = self.cli("skill", "solo", "--agents", "ghost")
        self.assertEqual(result.returncode, 1)
        out = result.stdout + result.stderr
        self.assertIn("unknown agent(s): ghost", out)
        self.assertIn("qoder", out)
        self.assertIn("agents --set", out)

    def test_aliases_resolve_through_the_table(self):
        self.skill("solo")
        result = self.cli("skill", "solo", "--agents", "claude-code")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        link = Path(self.env["MANAGER_HOME"]) / ".claude" / "skills" / "solo"
        self.assertTrue(link.exists() or manager.is_link_like(link))


class ClaimTests(ManagerFixture):
    def _agent(self, name: str) -> Path:
        directory = self.root / f"{name}-skills"
        result = self.cli("agents", "--set", name, "--skill-dir", str(directory))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return directory

    def _install(self, name: str, agent: str, *mode: str) -> None:
        self.skill(name)
        result = self.cli("skill", name, "--agents", agent, *mode)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_agents_inventory_lists_installed_skills(self):
        xag = self._agent("xag")
        self._install("solo", "xag")
        handmade = xag / "handmade"
        self.write(handmade / "SKILL.md", "# mine\n")
        result = self.cli("agents", "--inventory", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        skills = {s["name"]: s for s in data["xag"]["skills"]}
        self.assertIn(skills["solo"]["kind"], ("symlink", "junction"))
        self.assertTrue(Path(skills["solo"]["source"]).is_dir())
        self.assertEqual(skills["handmade"]["kind"], "unmanaged-dir")

    def test_claim_append_adds_missing_and_never_touches_existing(self):
        xag, yag = self._agent("xag"), self._agent("yag")
        self._install("one", "xag")
        self._install("two", "xag")
        self._install("one", "yag")
        handmade = yag / "handmade"
        self.write(handmade / "SKILL.md", "# mine\n")
        result = self.cli("claim", "xag", "yag", "--append")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("kept", result.stdout)
        self.assertTrue((yag / "two").is_dir() or manager.is_link_like(yag / "two"))
        self.assertTrue((handmade / "SKILL.md").is_file())
        self.assertTrue((yag / "one" / "SKILL.md").is_file())

    def test_claim_override_replaces_shared_and_prunes_extras(self):
        xag, yag = self._agent("xag"), self._agent("yag")
        self._install("one", "xag")
        self._install("extra", "yag", "--hard-copy")     # managed extra must go
        result = self.cli("claim", "xag", "yag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("removed copy", result.stdout)
        self.assertFalse((yag / "extra").exists())
        self.assertTrue((yag / "one" / "SKILL.md").is_file())
        self.assertTrue((self.registry / "extra" / "SKILL.md").is_file())  # source untouched

    def test_claim_override_protects_unmanaged_unless_force(self):
        xag, yag = self._agent("xag"), self._agent("yag")
        self._install("one", "xag")
        handmade = yag / "handmade"
        self.write(handmade / "SKILL.md", "# mine\n")
        result = self.cli("claim", "xag", "yag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("protected", result.stdout)
        self.assertTrue((handmade / "SKILL.md").is_file())
        result = self.cli("claim", "xag", "yag", "--force")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(handmade.exists())
        backups = list(Path(self.env["MANAGER_HOME"]).glob("claim-remove-backup-*.zip"))
        self.assertEqual(len(backups), 1)

    def test_claim_guards_same_folder_empty_source_and_append_force(self):
        xag = self._agent("xag")
        self._install("one", "xag")
        empty = self._agent("empty")
        (self.root / "empty-skills").mkdir(parents=True, exist_ok=True)
        result = self.cli("claim", "xag", "xag")
        self.assertEqual(result.returncode, 1)
        self.assertIn("same folder", result.stdout + result.stderr)
        result = self.cli("claim", "empty", "xag")
        self.assertEqual(result.returncode, 1)
        self.assertIn("empty set", result.stdout + result.stderr)
        result = self.cli("claim", "xag", "empty", "--append", "--force")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--append never removes", result.stdout + result.stderr)

    def test_claim_dry_run_is_inert(self):
        xag, yag = self._agent("xag"), self._agent("yag")
        self._install("one", "xag")
        result = self.cli("claim", "xag", "yag", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((yag / "one").exists() or manager.is_link_like(yag / "one"))


class InteractiveTests(ManagerFixture):
    def _agent(self, name: str) -> Path:
        directory = self.root / f"{name}-skills"
        result = self.cli("agents", "--set", name, "--skill-dir", str(directory))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return directory

    def _run(self, stdin: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(Path(manager.__file__).resolve()), "interactive",
             "--registry", str(self.registry), "--no-color", *args],
            env=self.env, cwd=self.root, capture_output=True, text=True,
            input=stdin, encoding="utf-8", timeout=45,
        )

    def _seed(self, *agents_dirs: Path) -> None:
        for name in ("aa", "bb", "cc"):
            self.skill(name)
        for directory in agents_dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def test_checklist_step_transitions_are_pure(self):
        visible = ["aa", "bb", "cc"]
        cursor, selected, action = manager.checklist_step(visible, set(), 0, "down")
        self.assertEqual((cursor, action, selected), (1, "move", set()))
        cursor, selected, action = manager.checklist_step(visible, set(), 2, "down")
        self.assertEqual(cursor, 2)  # clamped
        _, selected, action = manager.checklist_step(visible, {"bb"}, 0, "space")
        self.assertEqual((selected, action), ({"bb", "aa"}, "toggle"))
        _, selected, action = manager.checklist_step(visible, {"aa"}, 0, "a")
        self.assertEqual((selected, action), ({"aa", "bb", "cc"}, "all"))
        _, selected, action = manager.checklist_step(visible, {"aa", "bb", "cc"}, 0, "a")
        self.assertEqual((selected, action), (set(), "all"))
        self.assertEqual(manager.checklist_step(visible, {"aa"}, 0, "enter")[2], "done")
        for quit_key in ("q", "esc", "ctrl-c"):
            self.assertEqual(manager.checklist_step(visible, {"aa"}, 0, quit_key)[2], "quit")
        self.assertEqual(manager.checklist_step([], set(), 0, "space")[2], "none")
        lines, top = manager._checklist_lines(visible, {"bb"}, 1, {"aa"}, 10)
        self.assertEqual(top, 0)
        self.assertIn("[x] bb", lines[1])
        self.assertIn("installed", lines[0])

    def test_interactive_installs_checked_skill(self):
        xag = self._agent("xag")
        self._seed(xag)
        result = self._run("3\ndone\ny\n", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 install", result.stdout)
        self.assertTrue((xag / "cc" / "SKILL.md").is_file())
        self.assertFalse((xag / "aa").exists())

    def test_interactive_uninstalls_deselected_skill(self):
        xag = self._agent("xag")
        self._seed(xag)
        result = self.cli("skill", "aa", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self._run("1\ndone\ny\n", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 uninstall", result.stdout)
        self.assertFalse((xag / "aa").exists())
        self.assertTrue((self.registry / "aa" / "SKILL.md").is_file())  # source untouched

    def test_interactive_confirmation_gates_everything(self):
        xag = self._agent("xag")
        self._seed(xag)
        result = self._run("3\ndone\nn\n", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("declined; nothing changed", result.stdout)
        self.assertFalse((xag / "cc").exists())
        result = self._run("3\nquit\n", "--agents", "xag")
        self.assertIn("cancelled; nothing changed", result.stdout)
        self.assertFalse((xag / "cc").exists())

    def test_interactive_dry_run_shows_plan_without_touching(self):
        xag = self._agent("xag")
        self._seed(xag)
        result = self._run("3\ndone\n", "--agents", "xag", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 install", result.stdout)
        self.assertIn("dry-run", result.stdout)
        self.assertFalse((xag / "cc").exists())

    def test_questionary_picker_toggles_filters_and_cancels(self):
        q = manager._questionary()
        if q is None:
            self.skipTest("questionary is not installed")
        from prompt_toolkit.application import create_app_session
        from prompt_toolkit.input.defaults import create_pipe_input
        from prompt_toolkit.output import DummyOutput

        def pick(keys: str, selected: set[str], installed: set[str]) -> set[str] | None:
            with create_pipe_input() as pipe:
                pipe.send_text(keys)
                with create_app_session(input=pipe, output=DummyOutput()):
                    return manager._pick_checkbox(q, ["aa", "bb", "cc"], set(selected),
                                                  set(installed))

        self.assertEqual(pick("\x1b[B \r", set(), set()), {"bb"})       # arrow + space
        self.assertEqual(pick("cc \r", set(), set()), {"cc"})           # type-to-filter
        self.assertEqual(pick(" \r", {"aa"}, {"aa"}), set())            # untick aa
        self.assertIsNone(pick("\x03", set(), set()))                   # ctrl-c cancels

    def test_interactive_leaves_foreign_installs_untouched(self):
        xag = self._agent("xag")
        self._seed(xag)
        handmade = xag / "handmade"
        self.write(handmade / "SKILL.md", "# mine\n")
        result = self._run("done\ny\n", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("nothing to change", result.stdout)
        self.assertTrue((handmade / "SKILL.md").is_file())


class RemoteTests(ManagerFixture):
    def _git(self, cwd: Path, *args: str) -> None:
        proc = subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t",
                               "-c", "user.email=t@t", *args],
                              env=self.env, capture_output=True, text=True,
                              encoding="utf-8", timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def _remote_repo(self, *skill_names: str) -> Path:
        repo = self.root / "remote-repo"
        for name in skill_names:
            self.skill(name, base=repo)
        repo.mkdir(parents=True, exist_ok=True)
        self._git(repo, "init", "-q", "-b", "main")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "init")
        return repo

    def _agent(self, name: str) -> Path:
        directory = self.root / f"{name}-skills"
        result = self.cli("agents", "--set", name, "--skill-dir", str(directory))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return directory

    def _cache(self) -> Path:
        return self.root / "remotes" / "remote-repo"

    def test_skill_remote_registers_fetches_and_links(self):
        repo, xag = self._remote_repo("remalpha", "rembeta"), self._agent("xag")
        result = self.cli("skill", "--remote", str(repo), "remalpha", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(manager.is_link_like(xag / "remalpha"))
        self.assertTrue(manager.same_path(xag / "remalpha", self._cache() / "remalpha"))
        self.assertTrue((xag / "remalpha" / "SKILL.md").is_file())
        self.assertFalse((xag / "rembeta").exists())

    def test_skill_remote_multi_skill_repo_without_names_shows_candidates(self):
        repo, xag = self._remote_repo("remalpha", "rembeta"), self._agent("xag")
        result = self.cli("skill", "--remote", str(repo), "--agents", "xag")
        self.assertEqual(result.returncode, 1)
        output = result.stdout + result.stderr
        self.assertIn("rembeta", output)
        self.assertIn("name the ones to install", output)

    def test_skill_remote_single_skill_repo_needs_no_name(self):
        repo, xag = self._remote_repo("only"), self._agent("xag")
        result = self.cli("skill", "--remote", str(repo), "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((xag / "only" / "SKILL.md").is_file())

    def test_remote_update_reflects_new_commits(self):
        repo = self._remote_repo("remalpha")
        self._agent("xag")
        result = self.cli("skill", "--remote", str(repo), "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        (repo / "remalpha" / "SKILL.md").write_text(
            (repo / "remalpha" / "SKILL.md").read_text(encoding="utf-8") + "\nMARKER\n",
            encoding="utf-8")
        self._git(repo, "commit", "-qam", "bump")
        result = self.cli("remote", "--update")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("updated", result.stdout)
        self.assertIn("MARKER", (self._cache() / "remalpha" / "SKILL.md").read_text(encoding="utf-8"))

    def test_remote_remove_deletes_cache_and_warns_of_dangling_links(self):
        repo, xag = self._remote_repo("remalpha"), self._agent("xag")
        self.cli("skill", "--remote", str(repo), "remalpha", "--agents", "xag")
        result = self.cli("remote", "--remove", "remote-repo")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self._cache().exists())
        self.assertIn("still point into the removed cache", result.stdout + result.stderr)

    def test_report_and_find_and_lint_see_remotes_only_with_flag(self):
        repo = self._remote_repo("remalpha")
        self._agent("xag")
        result = self.cli("skill", "--remote", str(repo), "remalpha", "--agents", "xag")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("remalpha", json.dumps(self.report()))
        data = self.report("--remote")
        row = next(r for r in data["skills"] if r["name"] == "remalpha")
        self.assertEqual(row["path"], "remote:remote-repo/remalpha")
        self.assertIn("remote:remote-repo", data["remote_heads"])
        result = self.cli("find", "remalpha", "--remote")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("remote:remote-repo", result.stdout)
        # a remote skill installed nowhere else is linted only via the remote root
        self.write(repo / "rembeta" / "SKILL.md", "---\nname: rembeta\n---\n\n# beta\n")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-qm", "add-beta")
        upd = self.cli("remote", "--update")
        self.assertEqual(upd.returncode, 0, upd.stdout + upd.stderr)
        result = self.cli("lint", "--remote")
        out = result.stdout + result.stderr
        self.assertIn("remote:remote-repo", out)
        self.assertIn("rembeta", out)

    def test_skill_remote_unknown_name_lists_available(self):
        repo, xag = self._remote_repo("remalpha", "rembeta"), self._agent("xag")
        result = self.cli("skill", "--remote", str(repo), "nope", "--agents", "xag")
        self.assertEqual(result.returncode, 1)
        output = result.stdout + result.stderr
        self.assertIn("not a skill in remote", output)
        self.assertIn("rembeta", output)

    def test_remote_add_conflict_requires_force(self):
        repo_one, repo_two = self._remote_repo("one"), self.root / "two"
        self.skill("solo", base=repo_two)
        self._git(repo_two, "init", "-q", "-b", "main")
        self._git(repo_two, "add", "-A")
        self._git(repo_two, "commit", "-qm", "init")
        result = self.cli("remote", "--add", str(repo_one), "--name", "shared")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.cli("remote", "--add", str(repo_two), "--name", "shared")
        self.assertEqual(result.returncode, 1)
        self.assertIn("--force", result.stdout + result.stderr)
        result = self.cli("remote", "--add", str(repo_two), "--name", "shared", "--force")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        listing = self.cli("remote", "--json")
        self.assertEqual(json.loads(listing.stdout)["shared"]["url"], str(repo_two))


if __name__ == "__main__":
    unittest.main()
