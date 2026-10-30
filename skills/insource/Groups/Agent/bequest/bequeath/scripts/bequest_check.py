#!/usr/bin/env python3
"""bequest_check.py - scaffold and validate a project's bequest/ directory. ASCII output.

  python scripts/bequest_check.py --scaffold <project-root>   # create bequest/ + INDEX.md (idempotent)
  python scripts/bequest_check.py --check <project-root>      # validate assets, cards, index, hygiene
  python scripts/bequest_check.py [--strict]                  # warnings become errors
  python scripts/bequest_check.py                             # self-test (10 fixtures)

Checks (deterministic facts only):
  every asset directory has README.md with the eight required sections
  the verification status is one of the four allowed phrases
  relative links in cards resolve; tests/ mentioned when tests/ exists
  INDEX.md rows and directories agree in both directions
  no absolute/temp machine paths; no secret-shaped strings; no byte-identical duplicates
Exit: 0 clean, 1 findings, 2 usage error.
"""

import argparse
import hashlib
import os
import re
import sys
import tempfile

REQUIRED = [
    ("what it does", "what it does"),
    ("when to use", "when to use"),
    ("how to use", "how to use"),
    ("inputs", "input"),
    ("outputs", "output"),
    ("dependencies", "dependenc"),
    ("assumptions", "assumption"),
    ("verification", "verification"),
]
STATUSES = ["verified (automated)", "verified (manual)", "partially verified", "unverified"]
ABS = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\\|/home/[A-Za-z]|/Users/[A-Za-z]|/tmp/|\\AppData\\")
SECRETS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(password|passwd|api[_-]?key|secret|token)\b\s*[=:]\s*[\"']?[A-Za-z0-9_\-]{12,}"),
]
PLACEHOLDER = re.compile(r"<[^>]+>|\$\{[^}]+\}|\$[A-Z_]{3,}|example|changeme|your[_-]|xxx+|\*\*\*")

INDEX_HEADER = """# Bequest index

<!-- One row per asset. Wording in "What it does" is the card's first sentence. -->

| Asset | Type | What it does | Verification | Path |
|---|---|---|---|---|
"""


class Report:
    def __init__(self):
        self.errors, self.warns = [], []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warns.append(m)

    def emit(self, strict):
        for m in self.errors:
            print("ERROR  " + m)
        for m in self.warns:
            print("WARN   " + m)
        if strict:
            self.errors.extend(self.warns)
        print("%d error(s), %d warning(s)" % (len(self.errors), len(self.warns)))
        return 1 if self.errors else 0


def scaffold(root):
    bq = os.path.join(root, "bequest")
    made = []
    if not os.path.isdir(bq):
        os.makedirs(bq)
        made.append("bequest/")
    idx = os.path.join(bq, "INDEX.md")
    if not os.path.exists(idx):
        open(idx, "w", encoding="utf-8", newline="\n").write(INDEX_HEADER)
        made.append("bequest/INDEX.md")
    if made:
        print("scaffolded: " + ", ".join(made))
    else:
        print("nothing to do: bequest/ and INDEX.md already exist")
    return 0


def prose_only(text):
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def headings(text):
    return [h.strip().lower() for h in re.findall(r"^#{1,4}\s+(.+)$", text, re.M)]


def index_rows(text):
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue
        if cells[0].lower() in ("asset", "#"):
            continue
        path = cells[-1].strip("`/ ")
        rows.append((cells[0].strip("`"), path))
    return rows


def check(root, strict=False):
    rep = Report()
    bq = os.path.join(root, "bequest")
    if not os.path.isdir(bq):
        rep.err("no bequest/ directory under %s - run --scaffold first" % root)
        return rep.emit(strict)
    idx_path = os.path.join(bq, "INDEX.md")
    if not os.path.exists(idx_path):
        rep.err("bequest/INDEX.md is missing")
        idx_text = ""
    else:
        idx_text = open(idx_path, encoding="utf-8", errors="replace").read()

    assets = sorted(d for d in os.listdir(bq)
                    if os.path.isdir(os.path.join(bq, d)) and not d.startswith("."))
    for slug in assets:
        adir = os.path.join(bq, slug)
        card = os.path.join(adir, "README.md")
        if not os.path.exists(card):
            rep.err("%s/: no README.md asset card" % slug)
            continue
        text = open(card, encoding="utf-8", errors="replace").read()
        low = text.lower()
        hs = headings(text)
        for label, needle in REQUIRED:
            if not any(needle in h for h in hs):
                rep.err("%s: card is missing the '%s' section" % (slug, label))
        if not any(s in low for s in STATUSES):
            rep.err("%s: verification status must be one of: %s" % (slug, ", ".join(STATUSES)))
        if os.path.isdir(os.path.join(adir, "tests")) and "tests/" not in text:
            rep.warn("%s: has tests/ but the card never says how to run them" % slug)
        for m in re.finditer(r"\]\(([^)\s]+)\)", prose_only(text)):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(adir, target.split("#")[0]))):
                rep.err("%s: card link target missing: %s" % (slug, target))

    listed = index_rows(idx_text) if idx_text else []
    listed_dirs = {p.rstrip("/") for _, p in listed if p}
    for slug in assets:
        if slug not in listed_dirs:
            rep.err("INDEX.md: no row for asset directory %s/" % slug)
    for name, path in listed:
        if path and path not in assets:
            rep.err("INDEX.md: row %r points at %s/ which does not exist" % (name, path))

    seen = {}
    for dirpath, _, files in os.walk(bq):
        for f in files:
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, bq).replace("\\", "/")
            try:
                if os.path.getsize(full) > 1_000_000:
                    continue
                data = open(full, "rb").read()
            except OSError:
                continue
            if f != "README.md":
                h = hashlib.md5(data).hexdigest()
                if h in seen:
                    rep.warn("duplicate content: %s and %s are byte-identical" % (seen[h], rel))
                else:
                    seen[h] = rel
            txt = data.decode("utf-8", "replace")
            for pat in ABS.finditer(txt):
                rep.warn("%s: machine path %r - use an argument or a relative path" % (rel, pat.group(0)))
            for pat in SECRETS:
                for m in pat.finditer(txt):
                    if PLACEHOLDER.search(m.group(0)):
                        continue
                    rep.err("%s: secret-shaped string (%s...)" % (rel, m.group(0)[:24]))

    print("checked: %d asset(s), %d index row(s)" % (len(assets), len(listed)))
    return rep.emit(strict)


# ------------------------------------------------------------------ self-test

def _mk(root, *, card=True, sections=True, status="verified (manual)", secret=False,
        abspath=False, index_row=True, tests=True, dup=False, card_only=False):
    bq = os.path.join(root, "bequest")
    adir = os.path.join(bq, "find-slow-requests")
    os.makedirs(adir if (not tests or card_only) else os.path.join(adir, "tests"), exist_ok=True)
    script = "print('ok')\n"
    if not card_only:
        open(os.path.join(adir, "run.py"), "w", encoding="utf-8").write(
        script + ("TOKEN='ghp_aaaaaaaaaaaaaaaaaaaaaa'\n" if secret else "")
        + ("# read C:\\Users\\dev\\data.json\n" if abspath else ""))
    if dup:
        open(os.path.join(adir, "copy.py"), "w", encoding="utf-8").write(script)
    if card:
        parts = ["# find-slow-requests\n"]
        if sections:
            parts.append("## What it does\nFlags slow rows.\n")
            parts.append("## When to use it\nWhen an export looks slow.\n")
            parts.append("## How to use it\n```bash\npython run.py --input x.json\n```\n")
            parts.append("## Inputs\n`--input` json export\n")
            parts.append("## Outputs\nstdout lines; exit 0/1/2\n")
            parts.append("## Dependencies\nPython 3.9+\n")
            parts.append("## Assumptions and limitations\nUTF-8 JSON\n")
        parts.append("## Verification\n**Status:** %s\n" % status)
        if tests:
            parts.append("Run tests/test_run.py.\n")
        open(os.path.join(adir, "README.md"), "w", encoding="utf-8").write("\n".join(parts))
    idx = INDEX_HEADER
    if index_row:
        idx += "| find-slow-requests | script | flags slow rows | %s | `find-slow-requests/` |\n" % status
    open(os.path.join(bq, "INDEX.md"), "w", encoding="utf-8").write(idx)


def selftest():
    cases = [
        ("clean asset", dict(), 0, "0 error(s)"),
        ("no card", dict(card=False), 1, "no README.md asset card"),
        ("missing sections", dict(sections=False), 1, "missing the 'what it does'"),
        ("bad status", dict(status="works great"), 1, "verification status must be"),
        ("secret", dict(secret=True), 1, "secret-shaped string"),
        ("missing index row", dict(index_row=False), 1, "no row for asset directory"),
        ("absolute path", dict(abspath=True), 0, "machine path"),
        ("duplicate file", dict(dup=True), 0, "byte-identical"),
        ("tests not documented", dict(tests=False), 0, "0 error(s)"),
        ("procedure, card only", dict(sections=True, tests=False, card_only=True), 0, "0 error(s)"),
    ]
    fails = 0
    for name, kwargs, want, want_text in cases:
        with tempfile.TemporaryDirectory() as tmp:
            _mk(tmp, **kwargs)
            import contextlib
            import io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = check(tmp)
            ok = rc == want and want_text.lower() in buf.getvalue().lower()
            print("%-22s %s" % (name, "PASS" if ok else "FAIL (rc=%d want=%d)\n%s"
                                % (rc, want, buf.getvalue()[:300])))
            fails += 0 if ok else 1
    with tempfile.TemporaryDirectory() as tmp:
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            scaffold(tmp)
            scaffold(tmp)
        ok = buf.getvalue().count("scaffolded:") == 1 and os.path.exists(os.path.join(tmp, "bequest", "INDEX.md"))
        print("%-22s %s" % ("scaffold idempotent", "PASS" if ok else "FAIL"))
        fails += 0 if ok else 1
    total = len(cases) + 1
    print("self-test: %d/%d fixtures behaved" % (total - fails, total))
    return 0 if fails == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(prog="bequest_check.py")
    ap.add_argument("--scaffold", metavar="ROOT")
    ap.add_argument("--check", metavar="ROOT")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    if a.scaffold:
        if not os.path.isdir(a.scaffold):
            print("error: no such directory: %s" % a.scaffold)
            return 2
        return scaffold(os.path.abspath(a.scaffold))
    if a.check:
        if not os.path.isdir(a.check):
            print("error: no such directory: %s" % a.check)
            return 2
        return check(os.path.abspath(a.check), a.strict)
    return selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
