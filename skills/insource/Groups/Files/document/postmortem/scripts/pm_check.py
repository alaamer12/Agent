#!/usr/bin/env python3
"""pm_check.py - deterministic checks for the postmortem skill. ASCII output, Windows-friendly.

  python scripts/pm_check.py --sanitize "<title>"     # folder name for a postmortem title
  python scripts/pm_check.py --file <pm.md>           # a single-file postmortem
  python scripts/pm_check.py --folder <dir>           # a folder-mode package
  python scripts/pm_check.py [--strict]               # warnings become errors
  python scripts/pm_check.py                          # self-test (12 fixtures)

What it checks (facts, never prose quality):
  file   18 numbered sections; evidence level claimed in section 13; no abbreviated commit SHAs;
         action cap (8), per-person owners, a Second story table; no 12-hour/ambiguous times;
         no 12-hour/ambiguous times; no person-as-cause phrases; no "human error" as a cause;
         vague time and quantity words flagged.
  folder all of the above on index.md, plus: every file present in the Files and Artifacts Index
         (index.md and index.html excepted - they are the document and its reader), every indexed
         path exists, relative links resolve, SHA256 matches, index.html loads index.md and carries
         the title, the H1 is the unsanitized title of the sanitized folder name.
Exit: 0 clean, 1 findings, 2 usage error.
"""

import argparse
import hashlib
import os
import re
import sys
import tempfile

FORBIDDEN_CHARS = '/\\*?"<>|'
SECTION_NAMES = [
    "What the problem was", "When and where", "When it started", "The interval", "Reproducibility",
    "How deep", "The pattern", "How it happened", "Cause category", "Scripts, tools and commands used to FIND",
    "How it was solved", "Scripts, tools and commands used to FIX", "Heuristic or verified",
    "How it was verified", "Rare or untestable", "Prevention", "Supporting sections", "Files and artifacts",
]
VAGUE_TIME = ["yesterday", "last night", "this morning", "recently", "a while", "for a while",
              "latest build", "a few days ago", "some time ago", "lately"]
VAGUE_QTY = ["many users", "some users", "several users", "a number of users", "a few users",
             "lots of", "most users", "a lot of users"]
PERSON_CAUSE = [r"\bhuman error\b", r"\boperator error\b", r"\bdeveloper error\b", r"\bforgot to\b",
                r"\bforgot that\b", r"\bby mistake\b", r"\bcareless(ly)?\b", r"\bnegligen(t|ce)\b",
                r"\bshould have known\b", r"\bfailed to (notice|check|think)\b"]
TWELVE_HOUR = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)\b")
HEX = re.compile(r"\b[0-9a-f]{7,12}\b")
SHA40 = re.compile(r"\b[0-9a-f]{40}\b")
SHA64 = re.compile(r"\b[0-9a-f]{64}\b")


def sanitize(title):
    name = title.replace(":", " -")
    name = "".join(c for c in name if c not in FORBIDDEN_CHARS)
    name = re.sub(r"[ ]{2,}", " ", name).strip(" .")
    return name


class Report:
    def __init__(self):
        self.errors, self.warns = [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def emit(self, strict):
        for m in self.errors:
            print("ERROR  " + m)
        for m in self.warns:
            print("WARN   " + m)
            if strict:
                self.errors.append(m)
        print("%d error(s), %d warning(s)" % (len(self.errors), len(self.warns)))
        return 1 if self.errors else 0


def check_document(text, rep, label="index.md"):
    heads = {int(m.group(1)) for m in re.finditer(r"^##\s+(\d{1,2})\.", text, re.M)}
    missing = [n for n in range(1, 19) if n not in heads]
    if missing:
        rep.err("%s: missing numbered sections: %s" % (label, ", ".join(map(str, missing))))
    low = text.lower()
    for w in VAGUE_TIME:
        if re.search(r"\b%s\b" % re.escape(w), low):
            rep.warn("%s: vague time wording %r - use a UTC ISO-8601 timestamp" % (label, w))
    for w in VAGUE_QTY:
        if w in low:
            rep.warn("%s: vague quantity %r - give a count and a denominator" % (label, w))
    for pat in PERSON_CAUSE:
        for m in re.finditer(pat, low):
            rep.err("%s: person-as-cause phrase %r - rewrite with the system as the subject"
                    % (label, m.group(0).strip()))
    for m in TWELVE_HOUR.finditer(text):
        rep.warn("%s: ambiguous 12-hour time %r - use 24h UTC (…T03:14:07Z)" % (label, m.group(0)))
    if not re.search(r"\bV[0-5]\b", text):
        rep.err("%s: no evidence level (V0-V5) claimed anywhere - section 13 must state one" % label)
    if re.search(r"\bV5\b", text) and "proven by construction" not in low and "why not v5" not in low:
        rep.warn("%s: V5 claimed without the removal-of-class argument - see references/00" % label)
    m16 = re.search(r"^##\s+16\.", text, re.M)
    if m16:
        block = text[m16.end():]
        nxt = re.search(r"^##\s+", block, re.M)
        if nxt:
            block = block[:nxt.start()]
        ids = re.findall(r"^\|\s*\**([A-Z]+\d+)\**\s*\|", block, re.M)
        if len(ids) > 8:
            rep.warn("%s: %d action items (cap is 8) - fold related ones, keep each finishable" % (label, len(ids)))
        for line in block.splitlines():
            if not line.strip().startswith("|") or not re.match(r"^\|\s*\**A\d+", line.strip()):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 5:
                owner = cells[4].lower().strip("*_ ")
                if owner in ("team", "tbd", "someone", "<team>") or "team" in owner:
                    rep.warn("%s: action %s has no individual owner (owner=%r)" % (label, cells[0], cells[4]))
    if "second story" not in text.lower():
        rep.warn("%s: no 'Second story' table in section 8 - blameless is not nameless" % label)

    for m in HEX.finditer(text):
        before = text[m.start() - 1] if m.start() else ""
        after = text[m.end()] if m.end() < len(text) else ""
        if before in "0123456789abcdef" or after in "0123456789abcdef":
            continue  # part of a longer hash, not an abbreviated id
        rep.warn("%s: abbreviated commit id %r - cite the full 40-character SHA" % (label, m.group(0)))
    return heads


def table_rows(text):
    """Rows of the Files and Artifacts Index table -> (path, sha256-or-None)."""
    m = re.search(r"^###+\s*Files and Artifacts Index\s*$", text, re.M)
    if not m:
        return None
    block = text[m.end():]
    stop = re.search(r"^###+\s", block, re.M)
    if stop:
        block = block[:stop.start()]
    rows = []
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue
        if cells[0].lower() in ("path", "#"):
            continue
        path = cells[0].strip("`").strip()
        sha = None
        for c in reversed(cells):
            mm = SHA64.search(c)
            if mm:
                sha = mm.group(0)
                break
        rows.append((path, sha))
    return rows


def _prose_only(text):
    """Links inside fenced blocks and inline code are samples, not links."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def check_links(text, base, rep, label="index.md"):
    n = 0
    for m in re.finditer(r"\]\(([^)\s]+)\)", _prose_only(text)):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#")[0]
        if not target:
            continue
        n += 1
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            rep.err("%s: link target missing: %s" % (label, target))
    return n


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file(path, strict=False):
    rep = Report()
    text = open(path, encoding="utf-8", errors="replace").read()
    check_document(text, rep, os.path.basename(path))
    check_links(text, os.path.dirname(os.path.abspath(path)), rep, os.path.basename(path))
    return rep.emit(strict)


def check_folder(root, strict=False):
    rep = Report()
    root = os.path.abspath(root)
    index = os.path.join(root, "index.md")
    if not os.path.exists(index):
        print("ERROR  %s has no index.md" % root)
        return 1
    text = open(index, encoding="utf-8", errors="replace").read()
    check_document(text, rep, "index.md")

    if "Files and Artifacts Index" not in text:
        rep.err("index.md: missing 'Files and Artifacts Index' (folder mode section 18)")
    if "How we reached this conclusion" not in text:
        rep.err("index.md: missing 'How we reached this conclusion' narrative")

    actual = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), root).replace("\\", "/")
            if rel in ("index.md", "index.html"):
                continue
            actual.append(rel)

    rows = table_rows(text)
    if rows is None:
        rows = []
    listed = [p for p, _ in rows]
    for rel in sorted(actual):
        if rel not in listed:
            rep.err("folder: file not in the Files and Artifacts Index: %s" % rel)
    for p, sha in rows:
        full = os.path.normpath(os.path.join(root, p))
        if not os.path.exists(full):
            rep.err("index table: listed path does not exist: %s" % p)
        elif sha:
            real = sha256_of(full)
            if real != sha:
                rep.err("index table: SHA256 mismatch for %s (table %s…, file %s…)"
                        % (p, sha[:12], real[:12]))

    nlinks = check_links(text, root, rep, "index.md")

    h1 = re.search(r"^#\s+(.+)$", text, re.M)
    if not h1:
        rep.err("index.md: no H1 title")
    elif sanitize(h1.group(1).strip()) != os.path.basename(root):
        rep.warn("index.md: H1 %r sanitizes to %r, folder is %r"
                 % (h1.group(1).strip()[:60], sanitize(h1.group(1).strip())[:60], os.path.basename(root)))

    reader = os.path.join(root, "index.html")
    if not os.path.exists(reader):
        rep.warn("folder: no index.html - the reader was not copied in")
    else:
        html = open(reader, encoding="utf-8", errors="replace").read()
        if "|| 'index.md'" not in html:
            rep.err("index.html: default SOURCE is not 'index.md'")
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        if not title or title.group(1).strip() in ("Markdown Reader", ""):
            rep.err("index.html: <title> was not set to the postmortem title")
    print("checked: %d artifacts, %d indexed rows, %d relative links"
          % (len(actual), len(rows), nlinks))
    return rep.emit(strict)


# ------------------------------------------------------------------ self-test

def _mk(root, *, title="Postmortem: Sync service — startup crash — 2026-10-12",
        sha_ok=True, link_ok=True, listing_complete=True, reader_ok=True, sections=18,
        bad_phrase=False, n_actions=1, owner="<name>", second_story=True):
    os.makedirs(os.path.join(root, "investigation"), exist_ok=True)
    body_file = os.path.join(root, "investigation", "repro.py")
    open(body_file, "w", encoding="utf-8").write("print('x')\n")
    digest = sha256_of(body_file)
    if not sha_ok:
        digest = "0" * 64
    rows = ["| Path | Role | What it is | How to run it | What it showed | Supports | SHA256 |",
            "|---|---|---|---|---|---|---|",
            "| `investigation/repro.py` | find | repro | `python investigation/repro.py` | failed | §5 | `%s` |"
            % digest]
    if listing_complete:
        pass
    else:
        open(os.path.join(root, "investigation", "extra.log"), "w").write("x\n")
    heads = []
    for i in range(1, sections + 1):
        heads.append("## %d. Section %d" % (i, i))
        if i == 13:
            heads.append("V4 — deterministic reproduction. Decision at 2026-10-12T03:14:07Z by `%s`." % ("a" * 40))
        if i == 18:
            heads.append("### Files and Artifacts Index\n" + "\n".join(rows))
            heads.append("### How we reached this conclusion\n1. Suspected X; ran [repro](%s)."
                         % ("investigation/repro.py" if link_ok else "investigation/missing.py"))
        if i == 8 and bad_phrase:
            heads.append("The developer forgot to check the clock; human error.")
        if i == 8 and second_story:
            heads.append("Second story: on-call rolled back on the runbook; reasonable given the alert.")
        if i == 16:
            arows = ["| ID | Action | Type | Priority | Owner | Due | Ticket | DoD | Status | Verified |",
                     "|---|---|---|---|---|---|---|---|---|---|"]
            for k in range(n_actions):
                arows.append("| A%d | fix %d | prevent | P1 | %s | 2026-10-20 | <link> | green | open | - |"
                             % (k + 1, k + 1, owner))
            heads.append("\n".join(arows))
    open(os.path.join(root, "index.md"), "w", encoding="utf-8").write(
        "# %s\n\n" % title + "\n\n".join(heads) + "\n")
    html = "<title>%s</title><script>const SOURCE = params.get('file') || '%s';</script>" % (
        "Markdown Reader" if not reader_ok else title, "index.html" if not reader_ok else "index.md")
    open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(html)


def selftest():
    cases = [
        ("clean folder", dict(), 0, ""),
        ("too many actions", dict(n_actions=9), 0, "cap is 8"),
        ("team owner", dict(owner="the team"), 0, "no individual owner"),
        ("no second story", dict(second_story=False), 0, "Second story"),
        ("missing sections", dict(sections=17), 1, "missing numbered sections"),
        ("sha mismatch", dict(sha_ok=False), 1, "SHA256 mismatch"),
        ("dead link", dict(link_ok=False), 1, "link target missing"),
        ("unindexed file", dict(listing_complete=False), 1, "not in the Files and Artifacts Index"),
        ("reader not configured", dict(reader_ok=False), 1, "SOURCE is not"),
        ("person as cause", dict(bad_phrase=True), 1, "person-as-cause"),
    ]
    fails = 0
    for name, kwargs, want, want_text in cases:
        with tempfile.TemporaryDirectory() as tmp:
            folder = os.path.join(tmp, sanitize("Postmortem: Sync service — startup crash — 2026-10-12"))
            _mk(folder, **kwargs)
            import io
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = check_folder(folder)
            ok = (rc == want) and (want_text.lower() in buf.getvalue().lower())
            print("%-24s %s" % (name, "PASS" if ok else "FAIL (rc=%d, want %d)\n%s"
                                % (rc, want, buf.getvalue()[:300])))
            fails += 0 if ok else 1
    # sanitizer fixtures
    san = [("Postmortem: Sync service — startup crash — 2026-10-12",
            "Postmortem - Sync service — startup crash — 2026-10-12"),
           ('A: b/c\\d*e?f"g<h>i|j', "A - bcdefghij")]
    for src, want in san:
        got = sanitize(src)
        ok = got == want
        print("%-24s %s" % ("sanitize " + src[:14], "PASS" if ok else "FAIL got %r want %r" % (got, want)))
        fails += 0 if ok else 1
    print("self-test: %d/%d fixtures behaved" % (len(cases) + len(san) - fails, len(cases) + len(san)))
    return 0 if fails == 0 else 1


def main(argv):
    ap = argparse.ArgumentParser(prog="pm_check.py")
    ap.add_argument("--sanitize", metavar="TITLE")
    ap.add_argument("--file", metavar="MD")
    ap.add_argument("--folder", metavar="DIR")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    if a.sanitize:
        print(sanitize(a.sanitize))
        return 0
    if a.file:
        if not os.path.exists(a.file):
            print("error: no such file: %s" % a.file)
            return 2
        return check_file(a.file, a.strict)
    if a.folder:
        if not os.path.isdir(a.folder):
            print("error: no such folder: %s" % a.folder)
            return 2
        return check_folder(a.folder, a.strict)
    return selftest()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
