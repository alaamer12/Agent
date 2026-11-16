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


if __name__ == "__main__":
    unittest.main()
