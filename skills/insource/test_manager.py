"""Tests for manager.py skill version tracking and the report command.

Run: python -m unittest test_manager -v   (or: python test_manager.py)
Uses temporary git repositories so git-aware behaviour is exercised for real.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import manager


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)


def init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.email", "test@example.com")
    git(path, "config", "user.name", "Test")
    git(path, "config", "commit.gpgsign", "false")
    (path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")


def commit(path: Path, msg: str = "commit") -> None:
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", msg)


def make_skill(registry: Path, name: str, version: str | None = "1.0.0",
               files: dict[str, str] | None = None, desc: str = "A test skill.") -> Path:
    directory = registry / name
    directory.mkdir(parents=True, exist_ok=True)
    fm = f"---\nname: {name}\ndescription: {desc}\n"
    if version is not None:
        fm += f"version: {version}\n"
    fm += f"---\n\n# {name}\n"
    (directory / "SKILL.md").write_text(fm, encoding="utf-8")
    for rel, content in (files or {}).items():
        p = directory / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return directory


def set_version(directory: Path, version: str) -> None:
    p = directory / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    out, replaced = [], False
    for line in lines:
        if line.startswith("version:"):
            out.append(f"version: {version}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.insert(1, f"version: {version}")
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def warnings_by_name(warnings) -> dict:
    return {w[0]: w for w in warnings}


class ClassifyChangeTests(unittest.TestCase):
    def test_edit_is_patch(self):
        sugg, _ = manager.classify_change({"a.md": "1"}, {"a.md": "2"})
        self.assertEqual(sugg, "patch")

    def test_new_file_is_minor(self):
        sugg, _ = manager.classify_change({"a.md": "1"}, {"a.md": "1", "b.md": "2"})
        self.assertEqual(sugg, "minor")

    def test_add_and_delete_is_major(self):
        sugg, _ = manager.classify_change({"a.md": "1"}, {"b.md": "2"})
        self.assertEqual(sugg, "major")

    def test_rename_is_patch(self):
        sugg, reason = manager.classify_change({"a.md": "same"}, {"b.md": "same"})
        self.assertEqual(sugg, "patch")
        self.assertIn("renamed", reason)

    def test_delete_only_is_minor(self):
        sugg, _ = manager.classify_change({"a.md": "1", "b.md": "2"}, {"a.md": "1"})
        self.assertEqual(sugg, "minor")

    def test_no_change(self):
        sugg, _ = manager.classify_change({"a.md": "1"}, {"a.md": "1"})
        self.assertIsNone(sugg)

    def test_rename_plus_new_file_is_minor(self):
        sugg, _ = manager.classify_change({"a.md": "x"}, {"b.md": "x", "c.md": "y"})
        self.assertEqual(sugg, "minor")


class VersionCheckTests(unittest.TestCase):
    def setUp(self):
        manager.configure_display(quiet=True, color=False, verbose=False)
        self.tmp = Path(tempfile.mkdtemp(prefix="mgr-ver-test-"))
        self._db_env = os.environ.get("MANAGER_DB")
        os.environ["MANAGER_DB"] = str(self.tmp / "manager.db")
        self.registry = self.tmp / "registry"
        init_repo(self.registry)

    def tearDown(self):
        if self._db_env is None:
            os.environ.pop("MANAGER_DB", None)
        else:
            os.environ["MANAGER_DB"] = self._db_env
        shutil.rmtree(self.tmp, ignore_errors=True)

    def check(self):
        return manager.check_versions(self.registry, jobs=1)

    def state(self):
        return manager.load_versions(self.registry)["skills"]

    def test_missing_version_warns(self):
        make_skill(self.registry, "alpha", version=None)
        commit(self.registry)
        warnings, stats = self.check()
        w = warnings_by_name(warnings)["alpha"]
        self.assertEqual(w[2], "set 1.0.0")
        self.assertIn("missing", w[3])
        self.assertEqual(stats["missing_version"], 1)

    def test_invalid_version_warns(self):
        make_skill(self.registry, "alpha", version="1.0")
        commit(self.registry)
        warnings, stats = self.check()
        w = warnings_by_name(warnings)["alpha"]
        self.assertEqual(w[2], "fix to X.Y.Z")
        self.assertEqual(stats["invalid_version"], 1)

    def test_new_skill_born_is_recorded_without_bump_warning(self):
        make_skill(self.registry, "alpha", version="1.0.0", files={"references/x.md": "hello"})
        commit(self.registry)
        warnings, stats = self.check()
        self.assertEqual(warnings, [])
        self.assertEqual(stats["new"], 1)
        self.assertIn("alpha", self.state())
        self.assertEqual(self.state()["alpha"]["version"], "1.0.0")
        # second run with no change -> unchanged, still no warning
        warnings2, stats2 = self.check()
        self.assertEqual(warnings2, [])
        self.assertEqual(stats2["unchanged"], 1)

    def test_new_skill_born_without_version_warns(self):
        make_skill(self.registry, "alpha", version=None)
        commit(self.registry)
        warnings, stats = self.check()
        self.assertEqual(stats["new"], 1)
        self.assertIn("alpha", warnings_by_name(warnings))
        self.assertIn("missing", warnings_by_name(warnings)["alpha"][3])

    def test_file_edit_suggests_patch_and_persists(self):
        d = make_skill(self.registry, "alpha", files={"references/x.md": "one"})
        commit(self.registry)
        self.check()  # baseline
        (d / "references/x.md").write_text("two", encoding="utf-8")
        warnings, stats = self.check()
        w = warnings_by_name(warnings)["alpha"]
        self.assertEqual(w[2], "patch")
        self.assertEqual(stats["unbumped"], 1)
        # warning persists on a second run without a bump
        warnings2, _ = self.check()
        self.assertIn("alpha", warnings_by_name(warnings2))

    def test_bump_clears_warning_and_rebaselines(self):
        d = make_skill(self.registry, "alpha", files={"references/x.md": "one"})
        commit(self.registry)
        self.check()
        (d / "references/x.md").write_text("two", encoding="utf-8")
        self.check()  # patch warning
        set_version(d, "1.0.1")
        warnings, stats = self.check()
        self.assertEqual(warnings, [])
        self.assertEqual(stats["bumped"], 1)
        self.assertEqual(self.state()["alpha"]["version"], "1.0.1")

    def test_new_file_suggests_minor(self):
        d = make_skill(self.registry, "alpha", files={"references/x.md": "one"})
        commit(self.registry)
        self.check()
        (d / "references/y.md").write_text("new", encoding="utf-8")
        warnings, _ = self.check()
        self.assertEqual(warnings_by_name(warnings)["alpha"][2], "minor")

    def test_add_and_delete_suggests_major(self):
        d = make_skill(self.registry, "alpha", files={"references/x.md": "one"})
        commit(self.registry)
        self.check()
        (d / "references/x.md").unlink()
        (d / "references/y.md").write_text("replacement", encoding="utf-8")
        warnings, _ = self.check()
        self.assertEqual(warnings_by_name(warnings)["alpha"][2], "major")

    def test_file_rename_suggests_patch(self):
        d = make_skill(self.registry, "alpha", files={"references/x.md": "content"})
        commit(self.registry)
        self.check()
        (d / "references/x.md").rename(d / "references/y.md")
        warnings, _ = self.check()
        w = warnings_by_name(warnings)["alpha"]
        self.assertEqual(w[2], "patch")
        self.assertIn("renamed", w[3])

    def test_skill_move_needs_no_bump(self):
        make_skill(self.registry, "alpha", files={"references/x.md": "one"})
        commit(self.registry)
        self.check()
        target = self.registry / "Groups" / "Code"
        target.mkdir(parents=True)
        shutil.move(str(self.registry / "alpha"), str(target / "alpha"))
        warnings, stats = self.check()
        self.assertEqual(warnings, [])
        self.assertEqual(stats["moved"], 1)
        self.assertEqual(self.state()["alpha"]["path"], "Groups/Code/alpha")

    def test_skill_rename_suggests_patch(self):
        make_skill(self.registry, "alpha", files={"references/x.md": "one"})
        commit(self.registry)
        self.check()
        # rename folder and the name field, keep other content identical
        make_skill(self.registry, "beta", files={"references/x.md": "one"})
        shutil.rmtree(self.registry / "alpha")
        warnings, stats = self.check()
        w = warnings_by_name(warnings)["beta"]
        self.assertEqual(w[2], "patch")
        self.assertIn("renamed", w[3])
        self.assertEqual(stats["unbumped"], 1)
        self.assertNotIn("alpha", self.state())
        self.assertIn("beta", self.state())

    def test_deleted_skill_is_pruned(self):
        make_skill(self.registry, "alpha")
        commit(self.registry)
        self.check()
        shutil.rmtree(self.registry / "alpha")
        _, stats = self.check()
        self.assertEqual(stats["deleted"], 1)
        self.assertNotIn("alpha", self.state())

    def test_no_json_data_files_written_to_registry(self):
        make_skill(self.registry, "alpha")
        commit(self.registry)
        self.check()
        for fname in manager.LEGACY_STORE_FILES.values():
            self.assertFalse((self.registry / fname).exists(), f"{fname} must not exist")
        self.assertTrue(Path(os.environ["MANAGER_DB"]).is_file())

    def test_legacy_json_imported_and_removed(self):
        legacy = {"version": 1, "skills": {
            "zeta": {"version": "1.2.3", "name": "zeta", "path": "zeta",
                     "commit": None, "fingerprint": "deadbeef", "file_count": 1,
                     "files": {"SKILL.md": "aaa"}}}}
        legacy_file = self.registry / manager.LEGACY_STORE_FILES["versions"]
        legacy_file.write_text(json.dumps(legacy), encoding="utf-8")
        state = manager.load_versions(self.registry)
        self.assertEqual(state["skills"]["zeta"]["version"], "1.2.3")
        self.assertFalse(legacy_file.exists())  # imported then removed
        # a second load comes from the database with the same content
        self.assertEqual(manager.load_versions(self.registry)["skills"]["zeta"]["path"], "zeta")


class ReportTests(unittest.TestCase):
    def setUp(self):
        manager.configure_display(quiet=True, color=False, verbose=False)
        self.tmp = Path(tempfile.mkdtemp(prefix="mgr-rep-test-"))
        self._db_env = os.environ.get("MANAGER_DB")
        os.environ["MANAGER_DB"] = str(self.tmp / "manager.db")
        self.registry = self.tmp / "registry"
        init_repo(self.registry)

    def tearDown(self):
        if self._db_env is None:
            os.environ.pop("MANAGER_DB", None)
        else:
            os.environ["MANAGER_DB"] = self._db_env
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_report(self, *extra):
        argv = ["report", "--registry", str(self.registry), "-C", *extra]
        args = manager.build_parser().parse_args(argv)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = manager.cmd_report(args, self.registry, jobs=1)
        return code, buf.getvalue()

    def test_report_counts_and_description_length(self):
        make_skill(self.registry, "alpha", files={"references/x.md": "a", "references/y.md": "b"},
                   desc="Short description.")
        make_skill(self.registry, "beta", files={"references/z.md": "c"})
        commit(self.registry)
        code, out = self.run_report("--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        rows = {r["name"]: r for r in data["skills"]}
        # alpha: SKILL.md + 2 references = 3 files
        self.assertEqual(rows["alpha"]["files"], 3)
        self.assertEqual(rows["beta"]["files"], 2)
        self.assertEqual(rows["alpha"]["desc"], len("Short description."))
        self.assertEqual(rows["alpha"]["version"], "1.0.0")

    def test_report_sort_by_files_desc(self):
        make_skill(self.registry, "alpha", files={"references/x.md": "a"})
        make_skill(self.registry, "beta", files={"references/x.md": "a", "references/y.md": "b",
                                                 "references/z.md": "c"})
        commit(self.registry)
        _, out = self.run_report("--json", "--sort", "files", "--reverse")
        data = json.loads(out)
        self.assertEqual([r["name"] for r in data["skills"]], ["beta", "alpha"])

    def test_report_filter_by_name(self):
        make_skill(self.registry, "alpha")
        make_skill(self.registry, "beta")
        commit(self.registry)
        _, out = self.run_report("--json", "alpha")
        data = json.loads(out)
        self.assertEqual([r["name"] for r in data["skills"]], ["alpha"])

    def test_report_git_state_modified(self):
        d = make_skill(self.registry, "alpha")
        commit(self.registry)
        (d / "SKILL.md").write_text((d / "SKILL.md").read_text(encoding="utf-8") + "\nextra\n",
                                    encoding="utf-8")
        _, out = self.run_report("--json")
        data = json.loads(out)
        self.assertEqual(data["skills"][0]["git"], "modified")


def set_name(directory: Path, new_name: str) -> None:
    p = directory / "SKILL.md"
    lines = p.read_text(encoding="utf-8").splitlines()
    out = [f"name: {new_name}" if line.startswith("name:") else line for line in lines]
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


ARCHIVE_STORIES = Path(__file__).resolve().parent / "Archive" / "stories"


@unittest.skipUnless(ARCHIVE_STORIES.is_dir(), "Archive/stories not present")
class EndToEndReportingTests(unittest.TestCase):
    """Drive the real reporting functions with a real archived skill (stories, 4 files)
    and assert on the RENDERED output the user actually sees, for every bump case."""

    def setUp(self):
        manager.configure_display(quiet=True, color=False, verbose=False)
        self._agents = manager.DEFAULT_AGENTS
        manager.DEFAULT_AGENTS = []  # isolate from real global agent folders
        self.tmp = Path(tempfile.mkdtemp(prefix="mgr-e2e-"))
        self._db_env = os.environ.get("MANAGER_DB")
        os.environ["MANAGER_DB"] = str(self.tmp / "manager.db")
        self.registry = self.tmp / "registry"
        init_repo(self.registry)

    def tearDown(self):
        manager.DEFAULT_AGENTS = self._agents
        if self._db_env is None:
            os.environ.pop("MANAGER_DB", None)
        else:
            os.environ["MANAGER_DB"] = self._db_env
        shutil.rmtree(self.tmp, ignore_errors=True)

    def seed_stories(self, version="1.0.0"):
        dst = self.registry / "stories"
        shutil.copytree(ARCHIVE_STORIES, dst)
        if version is not None:
            set_version(dst, version)
        commit(self.registry)
        self.lint()  # establish baseline
        return dst

    def lint(self, *extra):
        args = manager.build_parser().parse_args(
            ["lint", "--registry", str(self.registry), "-C", "-q", *extra])
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = manager.cmd_lint(args, self.registry, 1, [])
        return code, buf.getvalue()

    def report(self, *extra):
        args = manager.build_parser().parse_args(
            ["report", "--registry", str(self.registry), "-C", "-q", *extra])
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = manager.cmd_report(args, self.registry, 1)
        return code, buf.getvalue()

    def test_new_skill_born_reports_clean_and_correct_counts(self):
        self.seed_stories()
        code, out = self.lint()
        self.assertEqual(code, 0)
        self.assertNotIn("Suggested bump", out)  # no version-warning table
        _, rout = self.report("--json")
        row = {r["name"]: r for r in json.loads(rout)["skills"]}["stories"]
        self.assertEqual(row["files"], 4)
        self.assertEqual(row["version"], "1.0.0")
        data, _ = manager.read_frontmatter(self.registry / "stories" / "SKILL.md")
        self.assertEqual(row["desc"], len(data["description"]))

    def test_missing_version_reports_set_initial(self):
        self.seed_stories(version=None)
        _, out = self.lint()
        self.assertIn("missing version", out)
        self.assertIn("set 1.0.0", out)

    def test_invalid_version_reports_fix(self):
        self.seed_stories(version="1.0")
        _, out = self.lint()
        self.assertIn("invalid version", out)
        self.assertIn("fix to X.Y.Z", out)

    def test_edit_reports_patch(self):
        d = self.seed_stories()
        f = d / "references/01-discovery.md"
        f.write_text(f.read_text(encoding="utf-8") + "\nappended\n", encoding="utf-8")
        _, out = self.lint()
        self.assertIn("patch", out)
        self.assertIn("files edited", out)
        self.assertIn("stories", out)

    def test_new_file_reports_minor(self):
        d = self.seed_stories()
        (d / "references/03-extra.md").write_text("new content\n", encoding="utf-8")
        _, out = self.lint()
        self.assertIn("minor", out)
        self.assertIn("new files added", out)

    def test_merge_reports_major(self):
        d = self.seed_stories()
        (d / "references/01-discovery.md").unlink()
        (d / "references/03-new.md").write_text("replacement content\n", encoding="utf-8")
        _, out = self.lint()
        self.assertIn("major", out)
        self.assertIn("files added and removed", out)

    def test_file_rename_reports_patch_renamed(self):
        d = self.seed_stories()
        (d / "references/02-in-code.md").rename(d / "references/02-renamed.md")
        _, out = self.lint()
        self.assertIn("patch", out)
        self.assertIn("files renamed", out)

    def test_skill_move_reports_no_bump(self):
        self.seed_stories()
        target = self.registry / "Groups" / "Code"
        target.mkdir(parents=True)
        shutil.move(str(self.registry / "stories"), str(target / "stories"))
        _, out = self.lint()
        self.assertNotIn("Suggested bump", out)  # move needs no bump
        _, rout = self.report("--json")
        row = {r["name"]: r for r in json.loads(rout)["skills"]}["stories"]
        self.assertEqual(row["path"], "Groups/Code/stories")

    def test_skill_rename_reports_patch_renamed(self):
        self.seed_stories()
        dst = self.registry / "tales"
        shutil.copytree(self.registry / "stories", dst)
        set_name(dst, "tales")
        shutil.rmtree(self.registry / "stories")
        _, out = self.lint()
        self.assertIn("skill renamed", out)
        self.assertIn("patch", out)
        self.assertIn("tales", out)

    def test_bump_clears_warning_and_report_shows_new_version(self):
        d = self.seed_stories()
        f = d / "references/01-discovery.md"
        f.write_text(f.read_text(encoding="utf-8") + "\nappended\n", encoding="utf-8")
        _, out = self.lint()
        self.assertIn("files edited", out)
        set_version(d, "1.0.1")
        _, out2 = self.lint()
        self.assertNotIn("Suggested bump", out2)
        _, rout = self.report("--json")
        row = {r["name"]: r for r in json.loads(rout)["skills"]}["stories"]
        self.assertEqual(row["version"], "1.0.1")

    def test_strict_exit_code_reflects_version_warning(self):
        d = self.seed_stories()
        (d / "references/01-discovery.md").write_text("changed\n", encoding="utf-8")
        code, _ = self.lint("-S")
        self.assertEqual(code, 1)
        set_version(d, "1.0.1")
        code2, _ = self.lint("-S")
        self.assertEqual(code2, 0)

    def test_no_version_flag_suppresses_tracking(self):
        d = self.seed_stories()
        (d / "references/01-discovery.md").write_text("changed\n", encoding="utf-8")
        _, out = self.lint("--no-version")
        self.assertNotIn("Suggested bump", out)
        self.assertNotIn("Version warnings", out)

    def test_report_table_headers_and_sort(self):
        self.seed_stories()
        # add a second real archived skill with a different file count
        src = Path(__file__).resolve().parent / "Archive" / "visual-enhancer"
        if src.is_dir():
            dst = self.registry / "visual-enhancer"
            shutil.copytree(src, dst)
            set_version(dst, "1.0.0")
            commit(self.registry)
            self.lint()
        _, out = self.report()
        for header in ["Skill", "Version", "Files", "Desc chars", "Git", "Path"]:
            self.assertIn(header, out)
        _, jout = self.report("--json", "--sort", "files", "--reverse")
        rows = json.loads(jout)["skills"]
        counts = [r["files"] for r in rows]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_report_git_state_and_verbose_last_commit(self):
        d = self.seed_stories()
        (d / "references/01-discovery.md").write_text("changed\n", encoding="utf-8")
        _, jout = self.report("--json")
        row = json.loads(jout)["skills"][0]
        self.assertEqual(row["git"], "modified")
        manager.configure_display(quiet=True, color=False, verbose=True)
        _, vout = self.report("-v")
        self.assertIn("Last commit", vout)
        manager.configure_display(quiet=True, color=False, verbose=False)

    def test_real_cli_subprocess_report(self):
        self.seed_stories()
        proc = subprocess.run(
            ["python", "manager.py", "report", "--registry", str(self.registry), "--json", "-q"],
            capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["skills"][0]["name"], "stories")
        self.assertEqual(data["skills"][0]["files"], 4)

    def test_real_cli_subprocess_lint_warns(self):
        d = self.seed_stories()
        (d / "references/01-discovery.md").write_text("changed\n", encoding="utf-8")
        proc = subprocess.run(
            ["python", "manager.py", "lint", "--registry", str(self.registry), "-C", "-q", "-S"],
            capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("files edited", proc.stdout)
        self.assertIn("patch", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)