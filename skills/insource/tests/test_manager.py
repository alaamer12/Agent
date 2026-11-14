"""Tests for manager.py.

Run with:  python -m unittest discover -s tests -v
The suite redirects MANAGER_HOME to a temporary folder, so it never touches the
real agent configuration.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
MANAGER = ROOT / "manager.py"
sys.path.insert(0, str(ROOT))

import manager  # noqa: E402


def is_link(path: Path) -> bool:
    try:
        st = os.lstat(path)
    except OSError:
        return False
    attrs = getattr(st, "st_file_attributes", 0)
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)) or stat.S_ISLNK(st.st_mode)


class ManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="manager-test-"))
        self.registry = self.tmp / "registry"
        self.home = self.tmp / "home"
        self.registry.mkdir()
        (self.registry / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
        self._skill("alpha", "Short description.")
        self._skill("beta", "B" * 1100)
        self._skill("gamma", "Gamma description.")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _skill(self, name: str, description: str) -> None:
        folder = self.registry / name
        folder.mkdir()
        (folder / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: '{description}'\n---\n\n# {name}\n",
            encoding="utf-8",
        )

    def run_manager(self, *args: str) -> tuple[int, str, str]:
        env = dict(os.environ)
        env["MANAGER_HOME"] = str(self.home)
        env["PYTHONIOENCODING"] = "utf-8"
        proc = subprocess.run(
            [sys.executable, str(MANAGER), *args, "--registry", str(self.registry), "--no-color"],
            cwd=self.registry,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_default_command_and_agent_filter(self) -> None:
        code, out, err = self.run_manager("alpha")
        self.assertEqual(code, 0, err)
        dest = self.home / ".qoder" / "skills" / "alpha"
        self.assertTrue((dest / "SKILL.md").is_file())
        self.assertTrue(is_link(dest))

        code, out, err = self.run_manager("skill", "beta", "-A", "qoder")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.home / ".qoder" / "skills" / "beta").exists())
        self.assertFalse((self.home / ".junie" / "skills" / "beta").exists())

    def test_multiple_skill_names(self) -> None:
        code, out, err = self.run_manager("skill", "alpha", "gamma", "-A", "qoder")
        self.assertEqual(code, 0, err)
        self.assertTrue((self.home / ".qoder" / "skills" / "alpha").exists())
        self.assertTrue((self.home / ".qoder" / "skills" / "gamma").exists())
        self.assertFalse((self.home / ".qoder" / "skills" / "beta").exists())

        into = self.tmp / "multi" / "skills"
        code, out, err = self.run_manager("alpha", "gamma", "--into", str(into))
        self.assertEqual(code, 0, err)
        self.assertTrue((into / "alpha" / "SKILL.md").is_file())
        self.assertTrue((into / "gamma" / "SKILL.md").is_file())

        code, out, err = self.run_manager("skill", "alpha", "gamma", "-A", "qoder", "-c")
        self.assertEqual(code, 0, err)
        self.assertFalse(is_link(self.home / ".qoder" / "skills" / "alpha"))
        self.assertFalse(is_link(self.home / ".qoder" / "skills" / "gamma"))

    def test_hard_copy_manifest_and_sync_report(self) -> None:
        code, out, err = self.run_manager("skill", "beta", "-A", "qoder", "-c")
        self.assertEqual(code, 0, err)
        dest = self.home / ".qoder" / "skills" / "beta"
        self.assertTrue(dest.is_dir())
        self.assertFalse(is_link(dest))

        manifest = json.loads((self.registry / "manager-copies.json").read_text(encoding="utf-8"))
        record = next(v for v in manifest["copies"].values() if v["skill"] == "beta")
        self.assertEqual(len(record["fingerprint"]), 64)
        self.assertEqual(len(record["target_fingerprint"]), 64)

        (self.registry / "beta" / "SKILL.md").write_text(
            "---\nname: beta\ndescription: 'changed'\n---\n", encoding="utf-8"
        )
        code, out, err = self.run_manager("lint")
        self.assertEqual(code, 0, err)
        self.assertIn("source-changed", out + err)

    def test_refresh_and_force(self) -> None:
        self.run_manager("skill", "beta", "-A", "qoder", "-c")
        dest = self.home / ".qoder" / "skills" / "beta" / "SKILL.md"
        (self.registry / "beta" / "SKILL.md").write_text("source v2", encoding="utf-8")

        code, out, err = self.run_manager("skill", "--refresh", "-A", "qoder")
        self.assertEqual(code, 0, err)
        self.assertIn("source v2", dest.read_text(encoding="utf-8"))

        dest.write_text("local edit", encoding="utf-8")
        code, out, err = self.run_manager("skill", "--refresh", "-A", "qoder")
        self.assertEqual(code, 0, err)
        self.assertIn("local edit", dest.read_text(encoding="utf-8"))
        self.assertIn("modified", out)

        code, out, err = self.run_manager("skill", "--refresh", "-A", "qoder", "-f")
        self.assertEqual(code, 0, err)
        self.assertNotIn("local edit", dest.read_text(encoding="utf-8"))

    def test_into_and_lint_scan(self) -> None:
        into = self.tmp / "project" / "skills"
        code, out, err = self.run_manager("skill", "alpha", "--into", str(into))
        self.assertEqual(code, 0, err)
        self.assertTrue((into / "alpha" / "SKILL.md").is_file())

        code, out, err = self.run_manager("skill", "gamma", "--into", str(into), "-c")
        self.assertEqual(code, 0, err)
        self.assertFalse(is_link(into / "gamma"))

        code, out, err = self.run_manager("lint", "--into", str(into))
        self.assertEqual(code, 0, err)
        checked = re.search(r"SKILL\.md files checked\s*\|\s*(\d+)", out)
        self.assertIsNotNone(checked)
        self.assertEqual(int(checked.group(1)), 4)

    def test_agent_command(self) -> None:
        code, out, err = self.run_manager("agent", "-A", "qoder")
        self.assertEqual(code, 0, err)
        target = self.home / ".qoder" / "agents.md"
        self.assertTrue(target.exists())

        code, out, err = self.run_manager("agent", "-A", "qoder", "-c")
        self.assertEqual(code, 0, err)
        self.assertFalse(is_link(target))
        manifest = json.loads((self.registry / "manager-copies.json").read_text(encoding="utf-8"))
        self.assertTrue(any(v["kind"] == "file" for v in manifest["copies"].values()))

    def test_dry_run_mutates_nothing(self) -> None:
        code, out, err = self.run_manager("skill", "gamma", "-A", "qoder", "-d")
        self.assertEqual(code, 0, err)
        self.assertFalse((self.home / ".qoder" / "skills" / "gamma").exists())
        self.assertIn("would link", out)

    def test_lint_strict_exit_code(self) -> None:
        code, out, err = self.run_manager("lint")
        self.assertEqual(code, 0, err)
        self.assertIn("over limit", out)

        code, out, err = self.run_manager("lint", "-S")
        self.assertEqual(code, 1, out + err)

        (self.registry / "beta" / "SKILL.md").write_text(
            "---\nname: beta\ndescription: 'short now'\n---\n", encoding="utf-8"
        )
        code, out, err = self.run_manager("lint", "-S")
        self.assertEqual(code, 0, out + err)

    def test_frontmatter_shapes(self) -> None:
        cases = {
            "plain": "description: plain text",
            "folded": "description: >-\n  folded\n  text",
            "literal": "description: |\n  line one\n  line two",
            "single": "description: 'it''s quoted'",
            "double": 'description: "double quoted"',
        }
        for name, body in cases.items():
            path = self.tmp / f"{name}.md"
            path.write_text(f"---\nname: {name}\n{body}\n---\n", encoding="utf-8")
            data, error = manager.read_frontmatter(path)
            self.assertIsNone(error, name)
            self.assertIsInstance(data, dict)
            self.assertTrue(data.get("description"), name)

    @unittest.skipIf(manager.yaml is None, "PyYAML required")
    def test_invalid_yaml_is_not_accepted_by_fallback(self) -> None:
        path = self.registry / "alpha" / "SKILL.md"
        for body in ("description: Use when: invalid", "description: 'it isn't valid'"):
            with self.subTest(body=body):
                path.write_text(f"---\nname: alpha\n{body}\n---\n", encoding="utf-8")
                data, error = manager.read_frontmatter(path)
                self.assertIsNone(data)
                self.assertIn("invalid YAML", error)
                code, out, err = self.run_manager("lint", "--strict")
                self.assertEqual(code, 1, err)
                self.assertIn("invalid YAML", out)

    @unittest.skipIf(manager.yaml is None, "PyYAML required")
    def test_non_mapping_frontmatter_is_rejected(self) -> None:
        path = self.tmp / "sequence.md"
        path.write_text("---\n- name: alpha\n- description: example\n---\n", encoding="utf-8")
        data, error = manager.read_frontmatter(path)
        self.assertIsNone(data)
        self.assertEqual(error, "frontmatter must be a mapping")

    def test_lint_checks_names_and_multiline_descriptions(self) -> None:
        path = self.registry / "alpha" / "SKILL.md"
        for metadata, expected in (
            ("description: short", "missing or invalid name"),
            ("name: Bad_Name\ndescription: short", "missing or invalid name"),
            ("name: renamed\ndescription: short", "does not match folder"),
            ("name: alpha\ndescription: |\n  first\n  second", "single-line string"),
        ):
            with self.subTest(metadata=metadata):
                path.write_text(f"---\n{metadata}\n---\n", encoding="utf-8")
                code, out, err = self.run_manager("lint", "--strict")
                self.assertEqual(code, 1, err)
                self.assertIn(expected, out)
                self.assertIn(str(path), out)

    def test_lint_checks_nested_skills_without_changing_install_discovery(self) -> None:
        nested = self.registry / "alpha" / "child"
        nested.mkdir()
        (nested / "SKILL.md").write_text("---\nname: wrong\ndescription: short\n---\n", encoding="utf-8")
        archive = self.registry / "Archive" / "old"
        archive.mkdir(parents=True)
        (archive / "SKILL.md").write_text("invalid", encoding="utf-8")
        code, out, err = self.run_manager("lint", "--strict")
        self.assertEqual(code, 1, err)
        self.assertIn("folder 'child'", out)
        self.assertRegex(out, r"SKILL\.md files checked\s*\|\s*4")
        self.assertNotIn("old", manager.registry_skills(self.registry))
        self.assertNotIn("child", manager.registry_skills(self.registry))

    def test_lint_reports_duplicate_registry_names(self) -> None:
        duplicate = self.registry / "group" / "alpha"
        duplicate.mkdir(parents=True)
        (duplicate / "SKILL.md").write_text("---\nname: alpha\ndescription: short\n---\n", encoding="utf-8")
        code, out, err = self.run_manager("lint", "--strict")
        self.assertEqual(code, 1, err)
        self.assertIn("duplicate name 'alpha'", out)

    def test_lint_checks_external_linked_skills_and_deduplicates_targets(self) -> None:
        external = self.tmp / "external" / "foreign"
        external.mkdir(parents=True)
        (external / "SKILL.md").write_text("---\nname: Invalid_Name\ndescription: short\n---\n", encoding="utf-8")
        root = self.home / ".qoder" / "skills"
        root.mkdir(parents=True)
        manager.make_link(external, root / "foreign")
        manager.make_link(self.registry / "alpha", root / "alpha")
        code, out, err = self.run_manager("lint", "--strict")
        self.assertEqual(code, 1, err)
        self.assertIn("missing or invalid name", out)
        self.assertRegex(out, r"SKILL\.md files checked\s*\|\s*4")

    def test_lint_reports_unknown_broken_links_even_with_no_skills(self) -> None:
        root = self.home / ".qoder" / "skills"
        root.mkdir(parents=True)
        target = self.tmp / "removed"
        target.mkdir()
        manager.make_link(target, root / "retired-name")
        target.rmdir()
        for name in ("alpha", "beta", "gamma"):
            (self.registry / name / "SKILL.md").unlink()
        code, out, err = self.run_manager("lint", "--strict")
        self.assertEqual(code, 1, err)
        self.assertIn("retired-name", out)
        self.assertIn("broken-link", out)
        self.assertNotIn("passed metadata checks", out)

    def test_lint_reports_links_without_skill_files(self) -> None:
        root = self.home / ".qoder" / "skills"
        root.mkdir(parents=True)
        target = self.tmp / "empty-target"
        target.mkdir()
        manager.make_link(target, root / "empty-skill")
        code, out, err = self.run_manager("lint", "--strict")
        self.assertEqual(code, 1, err)
        self.assertIn("missing-skill", out)

    def test_lint_reports_incomplete_yaml_validation(self) -> None:
        args = manager.build_parser().parse_args(["lint", "--strict"])
        with mock.patch.object(manager, "yaml", None), \
                mock.patch.dict(os.environ, {"MANAGER_HOME": str(self.home)}), \
                mock.patch.object(manager, "display_table") as table, \
                mock.patch.object(manager, "display_kv"):
            self.assertEqual(manager.cmd_lint(args, self.registry, 1, []), 1)
        rows = table.call_args_list[0].args[1]
        self.assertTrue(any("YAML validation unavailable" in row[3] for row in rows))

    def test_missing_frontmatter(self) -> None:
        path = self.tmp / "none.md"
        path.write_text("# no frontmatter\n", encoding="utf-8")
        data, error = manager.read_frontmatter(path)
        self.assertIsNone(data)
        self.assertEqual(error, "no frontmatter")

    def _readme_registry(self) -> str:
        tools = self.registry / "Groups" / "Tools" / "delta"
        (tools / "epsilon").mkdir(parents=True)
        (tools / "SKILL.md").write_text(
            "---\nname: delta\ndescription: 'Delta parent.'\nwhen_to_use: When delta.\n"
            "argument-hint: \"[target]\"\n---\n", encoding="utf-8")
        (tools / "epsilon" / "SKILL.md").write_text(
            "---\nname: epsilon\ndescription: 'Epsilon child.'\n---\n", encoding="utf-8")
        (self.registry / "Archive" / "old").mkdir(parents=True)
        (self.registry / "Archive" / "old" / "SKILL.md").write_text(
            "---\nname: old\ndescription: 'Old.'\n---\n", encoding="utf-8")
        beta = "B" * 1100
        return "\n".join([
            "# Agent Skills Catalog", "",
            "Total active skills: **5** — 3 standalone at the repository root and the rest organized "
            "under 1 topic groups. 1 archived skills are listed at the end.", "",
            "## Quick Index", "", "### Tools", "",
            "- [delta](./Groups/Tools/delta/SKILL.md) — Delta parent.", "",
            "### Standalone (repository root)", "",
            "- [alpha](./alpha/SKILL.md) — Short description.",
            f"- [beta](./beta/SKILL.md) — {beta[:150]}…",
            "- [gamma](./gamma/SKILL.md) — Gamma description.", "",
            "## Skill Details", "", "### Tools", "",
            "#### `delta`", "",
            "- **Path:** [`Groups/Tools/delta/SKILL.md`](./Groups/Tools/delta/SKILL.md)",
            "- **Description:** Delta parent.", "- **Use-case:** When delta.",
            "- **Usage:** `/delta [target]`", "- **Sub-skills:** `epsilon`", "",
            "#### `epsilon`", "",
            "- **Path:** [`Groups/Tools/delta/epsilon/SKILL.md`](./Groups/Tools/delta/epsilon/SKILL.md)",
            "- **Description:** Epsilon child.", "- **Parent:** `delta`", "",
            "### Standalone (repository root)", "",
            "#### `alpha`", "", "- **Path:** [`alpha/SKILL.md`](./alpha/SKILL.md)",
            "- **Description:** Short description.", "",
            "#### `beta`", "", "- **Path:** [`beta/SKILL.md`](./beta/SKILL.md)",
            f"- **Description:** {beta}", "",
            "#### `gamma`", "", "- **Path:** [`gamma/SKILL.md`](./gamma/SKILL.md)",
            "- **Description:** Gamma description.", "",
            "## Archive", "", "- [old](./Archive/old/SKILL.md) — Old.", "",
        ])

    def test_readme_check_passes_when_in_sync(self) -> None:
        (self.registry / "README.md").write_text(self._readme_registry(), encoding="utf-8")
        self.assertEqual(manager.check_readme(self.registry), [])

    def test_readme_check_reports_every_kind_of_drift(self) -> None:
        text = self._readme_registry()
        text = text.replace("Total active skills: **5**", "Total active skills: **4**")
        text = text.replace("- [gamma](./gamma/SKILL.md) — Gamma description.\n", "")
        text = text.replace("- **Description:** Short description.", "- **Description:** Old alpha text.")
        text = text.replace("- **Usage:** `/delta [target]`", "- **Usage:** `/delta`")
        text = text.replace("- **Parent:** `delta`", "")
        text = text.replace("- [old](./Archive/old/SKILL.md) — Old.",
                            "- [gone](./Archive/gone/SKILL.md) — Gone. See [notes](./docs/missing.md).")
        (self.registry / "README.md").write_text(text, encoding="utf-8")
        (self.registry / "zeta").mkdir()
        (self.registry / "zeta" / "SKILL.md").write_text("---\nname: zeta\ndescription: 'Zeta.'\n---\n", encoding="utf-8")

        rows = manager.check_readme(self.registry)
        found = {(skill, section, issue.split(" (")[0]) for skill, section, issue in rows}
        expected = {
            ("-", "header", "claims 4 active skills, on disk: 6"),
            ("-", "header", "claims 3 standalone skills, on disk: 4"),
            ("gamma", "quick-index", "missing"),
            ("zeta", "quick-index", "missing"),
            ("zeta", "details", "missing"),
            ("alpha", "details", "description differs from SKILL.md"),
            ("delta", "details", "usage differs from argument-hint"),
            ("epsilon", "details", "parent should be 'delta'"),
            ("old", "archive", "missing"),
            ("gone", "archive", "stale entry: no archived skill at Archive/gone/SKILL.md"),
            ("-", "links", "broken link: ./docs/missing.md"),
        }
        self.assertTrue(expected <= found, sorted(found - expected) + ["missing:"] + sorted(expected - found))
        self.assertFalse(any(section == "quick-index" and skill == "alpha" for skill, section, _ in rows))

    def test_readme_check_flags_category_and_stale_details(self) -> None:
        text = self._readme_registry().replace("### Tools\n\n#### `delta`", "### Other\n\n#### `delta`")
        text = text.replace("## Archive", "#### `ghost`\n\n- **Path:** [`ghost/SKILL.md`](./ghost/SKILL.md)\n\n## Archive")
        (self.registry / "README.md").write_text(text, encoding="utf-8")
        rows = manager.check_readme(self.registry)
        self.assertIn(("delta", "details", "under 'Other', expected 'Tools'"), rows)
        self.assertIn(("ghost", "details", "stale entry: no active skill at ghost/SKILL.md"), rows)

    def test_readme_check_normalizes_paths(self) -> None:
        text = self._readme_registry()
        text = text.replace("- [alpha](./alpha/SKILL.md)", "- [alpha](alpha/SKILL.md)")
        text = text.replace("(./gamma/SKILL.md)", "(./Gamma/SKILL.md)")
        (self.registry / "Archive" / "Needs Work" / "older").mkdir(parents=True)
        (self.registry / "Archive" / "Needs Work" / "older" / "SKILL.md").write_text(
            "---\nname: older\ndescription: 'Older.'\n---\n", encoding="utf-8")
        text = text.replace("1 archived", "2 archived").replace(
            "- [old](./Archive/old/SKILL.md) — Old.",
            "- [old](./Archive/old/SKILL.md) — Old.\n- [older](./Archive/Needs%20Work/older/SKILL.md \"t\") — Older.")
        (self.registry / "README.md").write_text(text, encoding="utf-8")
        rows = manager.check_readme(self.registry)
        self.assertEqual(
            sorted(rows),
            sorted([
                ("gamma", "quick-index", "path case differs: README has Gamma/SKILL.md, disk has gamma/SKILL.md"),
                ("gamma", "details", "path case differs: README has Gamma/SKILL.md, disk has gamma/SKILL.md"),
            ]),
        )

    def _viber_manifest(self) -> None:
        group = self.registry / "Groups" / "Code"
        for name in ("fix", "update"):
            (group / name).mkdir(parents=True)
            (group / name / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: '{name}.'\n---\n", encoding="utf-8")
        manifest = {
            "phases": [
                {"phase": "One", "skills": [
                    {"name": "alpha", "status": "mandatory"},
                    {"name": "alpha", "status": "mandatory", "as": "alpha-tier"},
                    {"name": "notes-md", "status": "mandatory"},
                ]},
                {"phase": "Two", "skills": [
                    {"name": "FULL CODE", "status": "mandatory group", "path": "Groups/Code"},
                ]},
            ]
        }
        target = self.registry / "Groups" / "Viber" / "viber.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(manifest), encoding="utf-8")

    def test_viber_plan_resolves_names_groups_and_missing(self) -> None:
        self._viber_manifest()
        rows = manager.viber_plan(self.registry)
        resolved = [(row["entry"], row["name"], row["path"].name if row["path"] else None) for row in rows]
        self.assertEqual(resolved, [
            ("alpha", "alpha", "alpha"),
            ("alpha-tier", "alpha", "alpha"),
            ("notes-md", "notes-md", None),
            ("FULL CODE", "fix", "fix"),
            ("FULL CODE", "update", "update"),
        ])

    def test_viber_installs_the_set_once_with_skill_flags(self) -> None:
        self._viber_manifest()
        into = self.tmp / "project" / ".agents" / "skills"
        code, out, err = self.run_manager("viber", "--into", str(into), "--hard-copy")
        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(p.name for p in into.iterdir()), ["alpha", "fix", "update"])
        self.assertFalse(is_link(into / "alpha"))
        self.assertIn("notes-md", out + err)
        self.assertNotIn("gamma", [p.name for p in into.iterdir()])

        code, out, err = self.run_manager("viber", "-A", "qoder")
        self.assertEqual(code, 0, err)
        self.assertTrue(is_link(self.home / ".qoder" / "skills" / "fix"))
        self.assertFalse((self.home / ".junie" / "skills" / "fix").exists())

        code, out, err = self.run_manager("viber", "--list")
        self.assertEqual(code, 0, err)
        self.assertIn("not in registry", out)

    def test_viber_without_manifest_fails_clearly(self) -> None:
        code, out, err = self.run_manager("viber", "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("viber manifest not found", out + err)

    def test_lint_readme_flag_is_opt_in_and_strict(self) -> None:
        (self.registry / "README.md").write_text("# empty\n", encoding="utf-8")
        code, out, err = self.run_manager("lint")
        self.assertNotIn("README issues", out)
        code, out, err = self.run_manager("lint", "--readme")
        self.assertEqual(code, 0, err)
        self.assertIn("README issues", out)
        args = manager.build_parser().parse_args(["lint", "--readme", "--strict"])
        (self.registry / "beta" / "SKILL.md").write_text("---\nname: beta\ndescription: 'Beta.'\n---\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {"MANAGER_HOME": str(self.home)}), \
                mock.patch.object(manager, "display_table"), mock.patch.object(manager, "display_kv"):
            self.assertEqual(manager.cmd_lint(args, self.registry, 1, []), 1)


if __name__ == "__main__":
    unittest.main()
