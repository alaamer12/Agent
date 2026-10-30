#!/usr/bin/env python3
"""diff_survey.py - deterministic triage of a git change set. ASCII output.

  python scripts/diff_survey.py --range origin/main...HEAD
  python scripts/diff_survey.py --staged
  python scripts/diff_survey.py --worktree
  python scripts/diff_survey.py --merge <sha>              # compared to the merge's first parent
  python scripts/diff_survey.py --range A..B --path src/ --json
  python scripts/diff_survey.py --range A..B --fail-on high   # exit 1 when a HIGH finding exists

Surgical extraction — read ONE function out of a huge diff without loading the diff:

  git diff --output=/tmp/big.diff <range>            # the diff never enters context
  python scripts/diff_survey.py --file /tmp/big.diff --hunks --match compute_totals
  python scripts/diff_survey.py --file /tmp/big.diff --hunk 7,9 --budget 8

  python scripts/diff_survey.py                              # self-test (14 checks)

It classifies files and flags risk candidates. It does not judge code quality and it does not
read hunks: that is the agent's job (SKILL.md, references/01).

Flags: rename copy binary ws-only deleted deleted-test mode-change generated dependency migration ci
       config test no-newline secret-shaped
Risk:  HIGH   secret-shaped added line, deleted test file
       MEDIUM dependency manifest without lockfile (or the reverse), deleted source file, mode change,
              binary change, source changed with no test file in the set
Exit: 0 surveyed, 1 --fail-on triggered, 2 usage/not a repo.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

GENERATED = re.compile(
    r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock|Pipfile\.lock|"
    r"Gemfile\.lock|composer\.lock|go\.sum|bun\.lockb|"
    r"[^/]*\.min\.(js|css)|[^/]*\.map|[^/]*\.snap|"
    r"dist/|build/|out/|target/|vendor/|node_modules/|coverage/|__snapshots__/|\.next/)" , re.I)
DEPENDENCY = re.compile(
    r"(^|/)(package\.json|requirements[^/]*\.txt|pyproject\.toml|Pipfile|Cargo\.toml|go\.mod|"
    r"Gemfile|composer\.json|pom\.xml|build\.gradle[^/]*)$", re.I)
LOCKFILE = re.compile(r"(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock|"
                      r"Pipfile\.lock|Gemfile\.lock|composer\.lock|go\.sum|bun\.lockb)$", re.I)
MIGRATION = re.compile(r"(^|/)(migrations?|alembic|migrate|prisma/migrations)/|\.sql$", re.I)
CI = re.compile(r"(^|/)(\.github/workflows/|\.gitlab-ci\.yml|\.circleci/|Jenkinsfile|azure-pipelines\.yml|"
                r"\.buildkite/)", re.I)
CONFIG = re.compile(r"(^|/)(Dockerfile[^/]*|docker-compose[^/]*|\.env[^/]*|k8s/|helm/|config/[^/]+\.(ya?ml|json|toml))$", re.I)
TEST = re.compile(r"(^|/)(tests?|__tests__|spec)/|[^/]*(_test\.(py|go|rb)|\.(test|spec)\.(js|jsx|ts|tsx|mjs|cjs))$", re.I)
SECRET = re.compile(r"(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|"
                    r"(password|passwd|api[_-]?key|secret|token)\s*[=:]\s*[\"'][^\"']{12,}[\"'])", re.I)


def chomp(line):
    return line[:-1] if line.endswith(chr(10)) else line


def asc(x):
    """ASCII-safe for tables: a cp1252 console must never raise on a unicode path."""
    return str(x).encode("ascii", "replace").decode("ascii")


def emit(text):
    """Verbatim content to stdout as UTF-8 bytes, bypassing the console code page."""
    buf = getattr(sys.stdout, "buffer", None)
    data = text.encode("utf-8", "replace")
    if buf is not None:
        try:
            buf.write(data)
            buf.flush()
            return
        except (OSError, ValueError):
            pass
    sys.stdout.write(data.decode("ascii", "replace"))


def git(args, cwd=None):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=cwd)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip()
        if "usage:" in err or "options:" in err:          # git dumped its manual: keep the first line only
            err = err.splitlines()[0]
        raise RuntimeError(err[:200] or "git failed")
    return r.stdout.decode("utf-8", "replace")


def check_repo(cwd):
    try:
        git(["rev-parse", "--git-dir"], cwd=cwd or ".")
    except RuntimeError as e:
        print("error: not a git repository: %s" % (cwd or os.getcwd()))
        return False
    return True


def check_revs(rng, cwd=None):
    """Validate every revision in the range before calling git diff - a short error beats git's dump."""
    if not rng:
        return True
    parts = [x for x in rng.replace("...", "\0").split("\0") if x]      # A...B → A, B
    parts = [p for part in parts for p in part.split("..") if p]
    for part in parts:
        try:
            git(["rev-parse", "--verify", "-q", part], cwd=cwd or ".")
        except RuntimeError:
            print("error: unknown revision %r (run inside the repo, or pass --cwd)" % part)
            return False
    return True


def base_args(a, cwd=None):
    if a.range:
        return base_range_args(a.range, cwd)
    if a.merge:
        return [parent_of(a.merge, cwd), a.merge]
    if a.staged:
        return ["--cached", "HEAD"]
    return ["HEAD"]


def _dest(name):
    """Turn numstat's rename notation into the destination path.

    "src/{a.py => b.py}"  -> "src/b.py"
    "old.txt => new.txt"  -> "new.txt"
    """
    if "=>" not in name:
        return name
    m = re.match(r"^(.*)\{(.*) => (.*)\}(.*)$", name)
    if m:
        return (m.group(1) + m.group(3) + m.group(4)).replace("//", "/")
    return name.split("=>")[-1].strip()


def numstat(diff_args, path, cwd=None):
    out = git(["diff", "--numstat", "-M", "-C"] + diff_args + (["--", path] if path else []), cwd=cwd)
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add, rem, name = parts[0], parts[1], "\t".join(parts[2:])
        rows.append({
            "path": _dest(name),
            "raw": name,
            "added": None if add == "-" else int(add),
            "removed": None if rem == "-" else int(rem),
            "binary": add == "-" and rem == "-",
        })
    return rows


def statuses(diff_args, path, cwd=None):
    out = git(["diff", "--name-status", "-M", "-C"] + diff_args + (["--", path] if path else []), cwd=cwd)
    st = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        code = parts[0][0]
        target = parts[-1]
        st[target] = code
        if code in "RC" and len(parts) >= 3:
            st[target] = code + ":" + parts[1]
    return st


def summary(diff_args, cwd=None):
    out = git(["diff", "--summary"] + diff_args, cwd=cwd)
    modes = {}
    for line in out.splitlines():
        m = re.match(r" mode change (\d+) => (\d+) (.+)$", line)
        if m:
            modes[m.group(3)] = m.group(1) + "->" + m.group(2)
    return modes


def secret_lines(diff_args, path, cwd=None):
    out = git(["diff", "-U0", "--no-color"] + diff_args + (["--", path] if path else []), cwd=cwd)
    hits = []
    for line in out.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            m = SECRET.search(line)
            if m:
                hits.append(m.group(0)[:60])
    return hits


def survey(diff_args, path, max_files=40, cwd=None):
    rows = numstat(diff_args, path, cwd)
    st = statuses(diff_args, path, cwd)
    modes = summary(diff_args, cwd)
    ws = {r["path"] for r in numstat(["-w"] + diff_args, path, cwd)}

    findings_high, findings_med = [], []
    for r in rows:
        p = r["path"]
        flags = []
        code = st.get(p, "M")
        if code.startswith("R"):
            flags.append("rename")
        if code.startswith("C"):
            flags.append("copy")
        if code == "D":
            flags.append("deleted")
            if TEST.search(p):
                flags.append("deleted-test")
                findings_high.append("deleted test file: " + p)
        if modes.get(p):
            flags.append("mode-change")
            findings_med.append("mode change %s: %s" % (modes[p], p))
        if r["binary"]:
            flags.append("binary")
            findings_med.append("binary change: " + p)
        if p not in ws and not r["binary"] and (r["added"] or r["removed"]):
            flags.append("ws-only")
        if GENERATED.search(p):
            flags.append("generated")
        if DEPENDENCY.search(p):
            flags.append("dependency")
        if LOCKFILE.search(p):
            flags.append("lockfile")
        if MIGRATION.search(p):
            flags.append("migration")
        if CI.search(p):
            flags.append("ci")
        if CONFIG.search(p):
            flags.append("config")
        if TEST.search(p):
            flags.append("test")
        r["status"] = code
        r["flags"] = flags

    for s in secret_lines(diff_args, path, cwd):
        findings_high.append("secret-shaped added line: " + s)

    paths = [r["path"] for r in rows]
    dep = [p for p in paths if DEPENDENCY.search(p)]
    lock = [p for p in paths if LOCKFILE.search(p)]
    if dep and not lock:
        findings_med.append("dependency manifest changed without a lockfile: " + ", ".join(dep))
    if lock and not dep:
        findings_med.append("lockfile changed without a manifest: " + ", ".join(lock[:3]))
    src = [p for p in paths if not TEST.search(p) and not GENERATED.search(p) and st.get(p) != "D"]
    if src and not any(TEST.search(p) for p in paths):
        findings_med.append("source changed with no test file in the set")

    def rank(r):
        return (0 if any(f in ("deleted-test",) for f in r["flags"]) else 1,
                -(r["added"] or 0) - (r["removed"] or 0))
    rows.sort(key=rank)
    return {
        "baseline": " ".join(diff_args),
        "files": len(rows),
        "added": sum(r["added"] or 0 for r in rows),
        "removed": sum(r["removed"] or 0 for r in rows),
        "renames": sum(1 for r in rows if "rename" in r["flags"]),
        "binary": sum(1 for r in rows if r["binary"]),
        "rows": rows[:max_files],
        "truncated": max(0, len(rows) - max_files),
        "high": findings_high,
        "medium": findings_med,
    }


def render(d):
    print("baseline: %s  files=%d  +%d -%d  renames=%d  binary=%d"
          % (d["baseline"], d["files"], d["added"], d["removed"], d["renames"], d["binary"]))
    print()
    print("%-4s %7s %8s  %-58s %s" % ("ST", "ADDED", "REMOVED", "FILE", "FLAGS"))
    for r in d["rows"]:
        a = "-" if r["added"] is None else r["added"]
        m = "-" if r["removed"] is None else r["removed"]
        flags = ",".join(f for f in r["flags"] if f not in ("test",))
        print("%-4s %7s %8s  %-58s %s" % (r["status"], a, m, r.get("raw", r["path"])[:58], flags))
    if d["truncated"]:
        print("... %d more file(s) not shown" % d["truncated"])
    print()
    if d["high"]:
        for f in d["high"]:
            print("HIGH    " + asc(f))
    if d["medium"]:
        for f in d["medium"]:
            print("MEDIUM  " + asc(f))
    if not d["high"] and not d["medium"]:
        print("risk: none of the classified flags fired")


# ------------------------------------------------------------------ self-test

def _sh(cwd, *args):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True, check=True)


def _write(root, rel, text):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full) or root, exist_ok=True)
    open(full, "w", encoding="utf-8", newline="\n").write(text)


def selftest():
    checks = 0
    fails = 0

    def check(name, cond):
        nonlocal checks, fails
        checks += 1
        print("%-38s %s" % (name, "PASS" if cond else "FAIL"))
        fails += 0 if cond else 1

    with tempfile.TemporaryDirectory() as tmp:
        _sh(tmp, "init", "-q")
        _sh(tmp, "config", "user.email", "t@t")
        _sh(tmp, "config", "user.name", "t")
        _sh(tmp, "config", "core.autocrlf", "false")
        _write(tmp, "src/app.py", "def f():\n    return 1\n")
        _write(tmp, "src/old_name.py", "x = 1\ny = 2\nz = 3\n")
        _write(tmp, "tests/test_app.py", "def test_f():\n    assert True\n")
        _write(tmp, "package.json", '{"name":"t","version":"1.0.0"}\n')
        _write(tmp, "package-lock.json", '{"lockfileVersion":3}\n')
        _write(tmp, "docs/readme.txt", "a\nb\nc\n")
        _sh(tmp, "add", "-A")
        _sh(tmp, "commit", "-qm", "base")

        _write(tmp, "src/app.py", "def f():\n    return 2\n")
        _write(tmp, "docs/readme.txt", "a \nb\nc\n")                 # whitespace-only
        os.rename(os.path.join(tmp, "src/old_name.py"), os.path.join(tmp, "src/new_name.py"))
        os.remove(os.path.join(tmp, "tests/test_app.py"))            # deleted test
        _write(tmp, "src/config.py", 'API_KEY = "abcdefghijklmnop"\n')  # secret-shaped
        _write(tmp, "package.json", '{"name":"t","version":"1.1.0"}\n')  # dep without lock change
        open(os.path.join(tmp, "assets.bin"), "wb").write(b"\x00\x01\x02")
        _sh(tmp, "add", "-A")   # untracked files are invisible to git diff until staged

        old = os.getcwd()
        os.chdir(tmp)
        try:
            d = survey(["--cached", "HEAD"], None)
        finally:
            os.chdir(old)
        flags = {f for r in d["rows"] for f in r["flags"]}
        check("detects modification", "src/app.py" in [r["path"] for r in d["rows"]])
        check("detects rename", "rename" in flags)
        check("detects whitespace-only", "ws-only" in flags)
        check("detects deleted test", any("deleted test file" in f for f in d["high"]))
        check("detects secret-shaped line", any("secret-shaped" in f for f in d["high"]))
        check("detects binary", "binary" in flags)
        check("dependency without lockfile", any("without a lockfile" in f for f in d["medium"]))
        check("no-test medium only when no test file", any("no test file" in f for f in d["medium"]) is False)

    # flag parsing: --fail-on logic lives in main(), exercised via return values
    check("three-dot passes through", base_args(argparse.Namespace(range="A...B", merge=None, staged=False, worktree=False), ".") == ["A...B"])
    check("two-dot splits", base_args(argparse.Namespace(range="A..B", merge=None, staged=False, worktree=False), ".") == ["A", "B"])
    check("worktree default", base_args(argparse.Namespace(range=None, merge=None, staged=False, worktree=True), ".") == ["HEAD"])
    check("staged baseline", base_args(argparse.Namespace(range=None, merge=None, staged=True, worktree=False), ".") == ["--cached", "HEAD"])

    # surgical extraction, on a synthetic diff (no repo needed)
    sample = (
        "diff --git a/src/billing.py b/src/billing.py\n"
        "@@ -10,4 +10,5 @@ def compute_totals(day):\n"
        "-    old = 1\n+    new = 2\n+    extra = 3\n     keep = 4\n"
        "diff --git a/tests/x.py b/tests/x.py\n"
        "@@ -1,2 +1,2 @@ def test_totals():\n"
        "-    assert 1\n+    assert 2\n"
    )
    hs = parse_hunks(sample)
    check("parses two hunks", len(hs) == 2)
    check("names the function", hs[0]["func"].startswith("def compute_totals"))
    check("counts added lines", hs[0]["added"] == 2 and hs[0]["removed"] == 1)
    check("tracks bytes", hs[0]["bytes"] > 0)
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = render_selected(hs, "1,2", 0)          # budget 0 KB = refuse anything non-empty
    check("budget refuses before printing", rc == 1 and "over --budget" in buf.getvalue())
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = render_selected(hs, "99", None)
    check("unknown hunk id errors", rc == 2)

    # hostile inputs: unicode paths, renames, binary rows, CRLF - must not raise on a cp1252 console
    hostile = (
        "diff --git a/café/naïve.py b/café/naïve.py\n"
        "@@ -1,2 +1,2 @@ def r():\n-a = 1\n+b = 2\n"
        "diff --git a/old.py b/new.py\nsimilarity index 95%\n--- a/old.py\n+++ b/new.py\n"
        "@@ -1 +1 @@\n-x\n+y\n"
        "diff --git a/x.png b/x.png\nBinary files a/x.png and b/x.png differ\n"
    )
    hh = parse_hunks(hostile)
    import contextlib
    import io as _io
    buf = _io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            render_hunk_index(hh, None)
            check("unicode/rename/binary survive printing", buf.getvalue().count("ca") >= 1)
    except UnicodeEncodeError:
        check("unicode/rename/binary survive printing", False)
    check("binary file yields no hunk", sum(h["id"] for h in hh) == 3)

    # cross-commit: real repo where c2 adds a line and c4 removes it (aggregate hides both)
    with tempfile.TemporaryDirectory() as t2:
        _sh(t2, "init", "-q", "-b", "main"); _sh(t2, "config", "user.email", "t@t")
        _sh(t2, "config", "user.name", "t")
        _write(t2, "core.py", "a\nb\n")
        _sh(t2, "add", "-A"); _sh(t2, "commit", "-qm", "BASE")
        base = _sh(t2, "rev-parse", "HEAD").stdout.strip()
        _write(t2, "core.py", "a\nexp\nb\n"); _sh(t2, "commit", "-qam", "c2: experiment")
        _write(t2, "core.py", "a\nb\n"); _sh(t2, "commit", "-qam", "c4: revert experiment")
        _write(t2, "core.py", "a\nb\nc\n"); _sh(t2, "commit", "-qam", "c5: real change")
        tip = _sh(t2, "rev-parse", "HEAD").stdout.strip()
        rows, hidden, total = per_commit(base + ".." + tip, None, t2)
        check("per-commit lists every commit", total == 3 and len(rows) == 3)
        check("per-commit churn exceeds aggregate",
              sum(r["added"] for r in rows) == 2 and sum(r["removed"] for r in rows) == 1)
        check("hidden churn detected", any("core.py" in h[0] for h in hidden))
        check("hidden churn counts commits", hidden and hidden[0][5] == 3)
        one = base_range_args(tip, t2)
        check("single rev means that commit", one[0] != tip and one[1] == tip)

    # a merge must not double-count the branch it merged
    with tempfile.TemporaryDirectory() as t3:
        _sh(t3, "init", "-q", "-b", "main"); _sh(t3, "config", "user.email", "t@t")
        _sh(t3, "config", "user.name", "t")
        _write(t3, "shared.py", "a\n")
        _sh(t3, "add", "-A"); _sh(t3, "commit", "-qm", "BASE")
        base = _sh(t3, "rev-parse", "HEAD").stdout.strip()
        _sh(t3, "checkout", "-q", "-b", "side")
        _write(t3, "shared.py", "a\nb\n"); _sh(t3, "commit", "-qam", "s1: add b")
        _write(t3, "shared.py", "a\nb\nc\n"); _sh(t3, "commit", "-qam", "s2: add c")
        _sh(t3, "checkout", "-q", "main")
        _sh(t3, "merge", "-q", "--no-edit", "--no-ff", "side")
        tip3 = _sh(t3, "rev-parse", "HEAD").stdout.strip()
        rows3, hidden3, total3 = per_commit(base + ".." + tip3, None, t3, max_commits=50)
        check("merge row is marked", any("merge" in r["notable"] for r in rows3))
        check("merge does not double-count churn", not any("shared.py" in h[0] for h in hidden3))

    # reading a region of a deleted file (the content-efficiency case)
    with tempfile.TemporaryDirectory() as t4:
        _sh(t4, "init", "-q", "-b", "main"); _sh(t4, "config", "user.email", "t@t")
        _sh(t4, "config", "user.name", "t")
        _write(t4, "gone.py", "".join("G%d" % i + chr(10) for i in range(400)))
        _sh(t4, "add", "-A"); _sh(t4, "commit", "-qm", "B")
        rev = _sh(t4, "rev-parse", "HEAD").stdout.strip()
        os.remove(os.path.join(t4, "gone.py")); _sh(t4, "add", "-A")
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_ok = at_region(rev, "gone.py", t4, lines="10:14")
        got = buf.getvalue()
        check("region read of a deleted file", rc_ok == 0 and "G10" in got and "G3" not in got.replace("G30", ""))
        check("region read prices the whole file, not the slice", "400 lines" not in got and "total file" in got)
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_big = at_region(rev, "gone.py", t4, lines="1:400", budget_kb=1)
        check("over-wide slice refused by default budget", rc_big == 1 and "refused" in buf.getvalue())
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_miss = at_region(rev, "never.py", t4, lines="1:5")
        check("missing path says so with a hint", rc_miss == 2 and "--follow" in buf.getvalue())
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_grep = at_region(rev, "gone.py", t4, grep="G39[5-9]", context=1)
        check("grep returns matches not the blob", rc_grep == 0 and "G395" in buf.getvalue() and "G100" not in buf.getvalue())
        open(os.path.join(t4, "pic.png"), "wb").write(bytes([0x89]) + b"PNG" + bytes([0, 1, 2]))
        _sh(t4, "add", "-A"); _sh(t4, "commit", "-qm", "add image")
        rev2 = _sh(t4, "rev-parse", "HEAD").stdout.strip()
        buf = _io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_bin = at_region(rev2, "pic.png", t4, lines="1:5")
        check("binary blob refused, not dumped as text", rc_bin == 1 and "is binary" in buf.getvalue())

    print("self-test: %d/%d checks passed" % (checks - fails, checks))
    return 0 if fails == 0 else 1


# ------------------------------------------------------------------ surgical extraction

HUNK_RE = re.compile(r"^@@+ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")


def parse_hunks(diff_text):
    """Split unified-diff text into addressable hunks. The text is parsed, never printed."""
    hunks, cur, fpath = [], None, None
    for line in diff_text.splitlines(keepends=True):
        if line.startswith("diff --git "):
            m = re.match(r"diff --git a/.*? b/(.+)$", line.rstrip("\n"))
            fpath = m.group(1) if m else "?"
            cur = None
        elif line.startswith("@@"):
            m = HUNK_RE.match(line.rstrip("\n"))
            g = m.groups() if m else ("", "", "", "")
            cur = {"id": len(hunks) + 1, "file": fpath, "header": line.strip(),
                   "old_start": int(g[0] or 1), "old_count": int(g[1] or 1),
                   "new_start": int(g[2] or 1), "new_count": int(g[3] or 1),
                   "func": (m.group(5).strip() if m else "") or "(top of file)",
                   "added": 0, "removed": 0, "lines": [line]}
            hunks.append(cur)
        elif cur is not None and line[:1] in "+- ":
            if line[0] == "+":
                cur["added"] += 1
            elif line[0] == "-":
                cur["removed"] += 1
            cur["lines"].append(line)
    for h in hunks:
        h["bytes"] = sum(len(l.encode("utf-8", "replace")) for l in h["lines"])
    return hunks


def render_hunk_index(hunks, match, max_hunks=40):
    if match:
        needle = match.lower()
        hunks = [h for h in hunks if needle in (h["file"] or "").lower() or needle in h["func"].lower()]
    total = sum(h["bytes"] for h in hunks)
    print("hunks=%d  their content=%d bytes (~%d tokens)  (nothing of the diff was loaded)"
          % (len(hunks), total, total // 4))
    print("%-4s %-42s %6s %8s  %s" % ("ID", "FILE", "+/-", "BYTES", "FUNCTION / SECTION"))
    for h in hunks[:max_hunks]:
        print("%-4d %-42s %3d/%-3d %8d  %s" % (h["id"], asc(h["file"] or "?")[:42], h["added"],
                                               h["removed"], h["bytes"], asc(h["func"])[:60]))
    print("\nfetch one without loading the rest:  --hunk <id>[,<id>...]  [--budget KB]")


def render_selected(hunks, ids, budget_kb):
    want = {int(x) for x in ids.replace(" ", "").split(",") if x}
    picked = [h for h in hunks if h["id"] in want]
    missing = sorted(want - {h["id"] for h in picked})
    if missing:
        print("error: no such hunk id(s): %s" % ",".join(map(str, missing)))
        return 2
    size = sum(h["bytes"] for h in picked)
    if budget_kb is not None and size > budget_kb * 1024:
        print("refused: selected hunks are %d bytes, over --budget %dKB" % (size, budget_kb))
        for h in picked[:3]:
            f = asc(h["file"] or "?")
            print("  cheaper: read a slice of the pre-change file (rev = the OLD side of your range):")
            print("    python scripts/diff_survey.py --at <rev-before> --path %s --lines %d:%d"
                  % (f, h["old_start"], min(h["old_start"] + 39, h["old_start"] + max(h["old_count"], 40) - 1)))
            print("    python scripts/diff_survey.py --at <rev-before> --path %s --grep '<pattern you wanted>'" % f)
            break
        return 1
    emit("".join("".join(h["lines"]) for h in picked))
    print("\n[extracted %d hunk(s), %d bytes]" % (len(picked), size))
    return 0


# ------------------------------------------------------------------ reading a region

NUL = bytes([0])
DEFAULT_BUDGET_KB = 16      # ~4k tokens; same discipline as --max-files/--max-hunks


def at_region(rev, path, cwd, lines=None, grep=None, context=2, max_matches=20, budget_kb=DEFAULT_BUDGET_KB):
    """Print a slice or the matches of ONE file AT ONE REVISION - never the whole blob, never a diff."""
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], cwd=cwd or ".", capture_output=True)
    if r.returncode != 0:
        print("error: %s did not exist at %s" % (path, rev))
        print("  find its earlier name across a rename:  git log --follow --name-only -- %s" % path)
        return 2
    if NUL in r.stdout[:8000] or r.stdout[:4] == b"%PDF":
        print("refused: %s at %s is binary (%d bytes) - diff and text slices cannot help here"
              % (path, rev, len(r.stdout)))
        print("  content:  git show %s:%s > <out-file>" % (rev, path))
        print("  metadata: git cat-file -s %s:%s ; git log --follow --oneline -- %s" % (rev, path, path))
        return 1
    text = r.stdout.decode("utf-8", "replace")
    body = text.splitlines(keepends=True)
    total_bytes = sum(len(l.encode("utf-8", "replace")) for l in body)
    out = []
    if lines:
        try:
            a, _, b = lines.partition(":")
            start, stop = int(a), int(b or a)
        except ValueError:
            print("error: --lines wants START[:END], got %r" % lines)
            return 2
        if start < 1 or stop < start:
            print("error: --lines must be 1-based and END >= START")
            return 2
        if start > len(body):
            print("error: %s:%s has %d lines, no line %d" % (rev, path, len(body), start))
            return 2
        stop = min(stop, len(body))
        out.append("%s:%s  lines %d-%d of %d  (total file %d bytes ~%d tokens)"
                   % (rev, path, start, stop, len(body), total_bytes, total_bytes // 4))
        out += ["%6d| %s" % (i, chomp(body[i - 1])) for i in range(start, stop + 1)]
    elif grep:
        pat = re.compile(grep, re.I)
        hits = []
        for i, l in enumerate(body):
            if pat.search(l):
                hits.append(i)
        out.append("%s:%s  %d match(es) of /%s/ in %d lines (file is %d bytes ~%d tokens)"
                   % (rev, path, len(hits), grep, len(body), total_bytes, total_bytes // 4))
        shown = hits[:max_matches]
        windows = []
        for i in shown:
            lo, hi = max(0, i - context), min(len(body), i + context + 1)
            if windows and lo <= windows[-1][1]:                     # merge overlapping context
                windows[-1][1] = max(windows[-1][1], hi)
                windows[-1][2].add(i)
            else:
                windows.append([lo, hi, {i}])
        for n, (lo, hi, marks) in enumerate(windows):
            if n:
                out.append("--")
            for j in range(lo, hi):
                out.append("%6d%s %s" % (j + 1, ">" if j in marks else "|", chomp(body[j])))
        if len(hits) > len(shown):
            out.append("... %d more matches (raise --max-matches)" % (len(hits) - len(shown)))
    else:
        print("error: --at needs --lines START[:END] or --grep PATTERN (reading a whole blob defeats the purpose)")
        return 2
    payload = chr(10).join(out).rstrip() + chr(10)
    size = len(payload.encode("utf-8", "replace"))
    if budget_kb is not None and size > budget_kb * 1024:
        print("refused: this region is %d bytes, over the %dKB budget - narrow --lines/--grep,"
              " raise --budget, or pass --force" % (size, budget_kb))
        return 1
    emit(payload)
    return 0


# ------------------------------------------------------------------ across commits

EMPTY_TREE = "4b825dc642cb6eb9a606045cbcdbf0a50a7f6b8b"   # git's empty tree: root-commit diffs


def parent_of(rev, cwd):
    return (git(["rev-parse", "--verify", "-q", rev + "^"], cwd=cwd or ".") or "").strip() or EMPTY_TREE


def base_range_args(rng, cwd=None):
    """One meaning everywhere: a single revision = that commit's own diff."""
    if not rng:
        return ["HEAD"]
    if "..." in rng:
        return [rng]
    if ".." in rng:
        a, b = [x for x in rng.split("..") if x]
        return [a, b]
    return [parent_of(rng, cwd), rng]


def per_commit(rng, path, cwd, max_commits=15, first_parent=False):
    """ONE batched git call: rows per commit + the churn the aggregate hides."""
    fmt = "--format=%x01%H%x09%P%x09%s"
    args = ["log", "--no-color", "--numstat", "-M", "-C", "--diff-merges=first-parent"]
    if first_parent:
        args.append("--first-parent")
    args += [fmt] + ([rng] if rng else ["HEAD"]) + (["--", path] if path else [])
    log = git(args, cwd=cwd)

    rows, per_file, touched = [], {}, {}
    cur = None
    for line in log.splitlines():
        if line.startswith(""):
            sha, rest = line[1:].split("	", 1)
            parents, _, subj = rest.partition("	")
            cur = {"sha": sha[:8], "subject": subj, "files": 0, "added": 0, "removed": 0,
                   "notable": set(), "merge": " " in parents.strip()}
            if cur["merge"]:
                cur["notable"].add("merge")
            rows.append(cur)
            continue
        if cur is None or not line.strip():              # blank lines separate the header from its files
            continue
        parts = line.split("	")
        if len(parts) < 3:
            continue
        add, rem, f = parts[0], parts[1], "	".join(parts[2:])
        a = 0 if add == "-" else int(add)
        m = 0 if rem == "-" else int(rem)
        cur["files"] += 1
        cur["added"] += a
        cur["removed"] += m
        dest = _dest(f)
        for pat, name in ((TEST, "test"), (DEPENDENCY, "dependency"), (MIGRATION, "migration"),
                          (GENERATED, "generated")):
            if pat.search(dest):
                cur["notable"].add(name)
        if add == "-" and rem == "-":
            cur["notable"].add("binary")
        if cur["merge"]:
            continue          # a merge's first-parent diff repeats its branch commits: never accumulate it
        acc = per_file.setdefault(dest, [0, 0])
        acc[0] += a
        acc[1] += m
        touched[dest] = touched.get(dest, 0) + 1

    shown = rows[:max_commits]
    for r in rows:
        r["notable"] = sorted(r["notable"])
    agg = survey(base_range_args(rng, cwd), path, 10000, cwd)
    hidden = []
    for r in agg["rows"]:
        ca, cm = per_file.get(r["path"], [r["added"] or 0, r["removed"] or 0])
        net = (r["added"] or 0) + (r["removed"] or 0)
        if touched.get(r["path"], 0) >= 2 and ca + cm > net:      # they cancelled each other out
            hidden.append((r["path"], r["added"] or 0, r["removed"] or 0, ca, cm, touched[r["path"]]))
    return shown, hidden, len(rows)


def render_commits(rows, hidden, total, max_commits, max_hidden=10):
    print("commits=%d (showing %d)" % (total, min(total, max_commits)))
    print("%-9s %-40s %5s %7s %8s  %s" % ("SHA", "SUBJECT", "FILES", "ADDED", "REMOVED", "NOTABLE"))
    for r in rows:
        print("%-9s %-40s %5d %7d %8d  %s" % (r["sha"], asc(r["subject"])[:40], r["files"],
                                              r["added"], r["removed"], ",".join(r["notable"])))
    if hidden:
        hidden = sorted(hidden, key=lambda h: -((h[3] + h[4]) - (h[1] + h[2])))
        print("")
        print("HIDDEN CHURN - %d file(s) the aggregate diff under-reports, biggest cancellation first:"
              % len(hidden))
        for path, a, m, ca, cm, n in hidden[:max_hidden]:
            print("  %-44s aggregate +%d/-%d  but %d commits sum +%d/-%d"
                  % (asc(path)[:44], a, m, n, ca, cm))
        if len(hidden) > max_hidden:
            print("  ... %d more (raise --max-hidden, or narrow the range)" % (len(hidden) - max_hidden))
        print("  -> read per commit (`--per-commit`) or `git log -L :func:path`: the net diff is not the story")



def main(argv):
    ap = argparse.ArgumentParser(prog="diff_survey.py")
    ap.add_argument("--range", metavar="REV")
    ap.add_argument("--merge", metavar="SHA")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--worktree", action="store_true")
    ap.add_argument("--path")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on", choices=["none", "high"], default="none")
    ap.add_argument("--max-files", type=int, default=40)
    ap.add_argument("--file", metavar="DIFF", help="read a saved diff instead of calling git")
    ap.add_argument("--hunks", action="store_true", help="index hunks (id, file, +/-, bytes, function)")
    ap.add_argument("--match", help="filter the hunk index by file or function substring")
    ap.add_argument("--hunk", help="print these hunk ids verbatim: 7 or 3,9,11")
    ap.add_argument("--budget", type=int, metavar="KB", help="refuse to print more than this")
    ap.add_argument("--force", action="store_true", help="print past --budget")
    ap.add_argument("--max-hunks", type=int, default=40, help="index rows to print (default 40)")
    ap.add_argument("--cwd", help="run git in this directory (another repo, or a sub-agent's workspace)")
    ap.add_argument("--per-commit", action="store_true", help="one row per commit + churn the aggregate hides")
    ap.add_argument("--max-commits", type=int, default=15)
    ap.add_argument("--max-hidden", type=int, default=10, help="hidden-churn rows to print (default 10)")
    ap.add_argument("--at", metavar="REV", help="read one region of a file at a revision (deleted files included)")
    ap.add_argument("--lines", metavar="START[:END]", help="1-based line slice for --at")
    ap.add_argument("--grep", metavar="REGEX", help="matches with context for --at")
    ap.add_argument("--context", type=int, default=2)
    ap.add_argument("--max-matches", type=int, default=20)
    ap.add_argument("--first-parent", action="store_true",
                    help="in merge-heavy history: list the mainline only (HEAD~20..HEAD can be 100 commits)")
    ap.add_argument("--to-file", metavar="PATH", help="write the diff to PATH and print only its size")
    a = ap.parse_args(argv)

    for name in ("range", "merge", "file", "match", "hunk", "to_file", "path", "cwd"):
        val = getattr(a, name)
        if isinstance(val, str):
            setattr(a, name, val.strip())
    for name in ("range", "merge", "file", "match", "hunk", "to_file", "path"):
        if getattr(a, name) == "":
            print("error: --%s was given an empty value" % name.replace("_", "-"))
            return 2

    if a.at:
        if not a.path:
            print("error: --at needs --path <file>")
            return 2
        return at_region(a.at, a.path, a.cwd or ".", a.lines, a.grep, a.context, a.max_matches,
                         None if a.force else (a.budget if a.budget is not None else DEFAULT_BUDGET_KB))

    if a.per_commit:
        if not check_repo(a.cwd):
            return 2
        rng = a.range or (a.merge + "^.." + a.merge if a.merge else None)
        if rng and not check_revs(rng, a.cwd):
            return 2
        try:
            rows, hidden, total = per_commit(rng, a.path, a.cwd or ".", a.max_commits, a.first_parent)
        except (RuntimeError, OSError) as e:
            print("error: %s" % str(e)[:300])
            return 2
        render_commits(rows, hidden, total, a.max_commits, a.max_hidden)
        return 0

    if (a.file or a.hunks or a.hunk or a.to_file) and not a.file:
        if not check_repo(a.cwd):
            return 2
        if a.range and not check_revs(a.range, a.cwd):
            return 2
    if a.file or a.hunks or a.hunk or a.to_file:
        try:
            if a.file:
                text = open(a.file, encoding="utf-8", errors="replace").read()
            elif a.to_file:
                data = subprocess.run(["git", "diff", "--no-color", "-M", "-C"] + base_args(a, a.cwd)
                                      + (["--", a.path] if a.path else []), capture_output=True)
                if data.returncode != 0:
                    print("error: %s" % data.stderr.decode("utf-8", "replace").strip()[:200])
                    return 2
                open(a.to_file, "wb").write(data.stdout)
                print("diff written: %s (%d bytes, ~%d tokens) - git stderr stayed captured"
                      % (a.to_file, len(data.stdout), len(data.stdout) // 4))
                return 0
            else:
                args = base_args(a, a.cwd)
                text = git(["diff", "--no-color", "-M", "-C"] + args + (["--", a.path] if a.path else []),
                           cwd=a.cwd or ".")
        except (RuntimeError, OSError) as e:
            print("error: %s" % (str(e)[:300],))
            return 2
        hunks = parse_hunks(text)
        if a.hunk:
            return render_selected(hunks, a.hunk, None if a.force else a.budget)
        render_hunk_index(hunks, a.match, a.max_hunks)
        return 0

    if not (a.range or a.merge or a.staged or a.worktree):
        return selftest()

    if not check_repo(a.cwd):
        return 2
    if a.range and not check_revs(a.range, a.cwd):
        return 2
    try:
        args = base_args(a, a.cwd)
        d = survey(args, a.path, a.max_files, a.cwd or ".")
    except RuntimeError as e:
        print("error: %s" % str(e)[:200])
        return 2

    if a.json:
        print(json.dumps(d, indent=2))
    else:
        render(d)
    if a.fail_on == "high" and d["high"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
