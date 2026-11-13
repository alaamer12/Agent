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

    def test_missing_frontmatter(self) -> None:
        path = self.tmp / "none.md"
        path.write_text("# no frontmatter\n", encoding="utf-8")
        data, error = manager.read_frontmatter(path)
        self.assertIsNone(data)
        self.assertEqual(error, "no frontmatter")


if __name__ == "__main__":
    unittest.main()
