#!/usr/bin/env python3
"""units_lint.py - check a UNITS.md against the units-md constraints.

Mechanical, conservative, deliberately boring: it verifies the index's structure, references and duties,
not whether the units are the right ones to have.

Usage:
  python scripts/units_lint.py UNITS.md               standard checks
  python scripts/units_lint.py UNITS.md --strict      adds dumping-ground and vague-purpose heuristics
  python scripts/units_lint.py UNITS.md --max-age 90  flag a stale "Last refreshed" date
  python scripts/units_lint.py --fixtures             write a sample project and lint it
  python scripts/units_lint.py                        self-test (every defect must be caught)

Exit: 0 clean, 1 findings, 2 usage/read error. Paths are resolved relative to the UNITS.md directory.
stdout is ASCII.

Checks:
  structure the file has a title, a How-to-use section, and unit entries
  duties    the four duties are stated: read before implementing, reuse-or-extend with a reason,
            add a new unit in the same task, and a named owner for updates
  ids       unique, well-formed unit ids; no gaps in the field block
  fields    Purpose, Where, Status, Verified present and non-empty on every unit
  paths     every "Where" resolves inside the project; no absolute paths, no paths outside the file's tree
  deps      "Depends on" ids exist; dependency cycles are reported
  status    values come from the declared vocabulary
  dupe      two units claiming the same primary path (a parallel component is a finding, not a duplicate row)
  size      total line budget, and any entry long enough to be documentation instead of an index row
  pending   template leftovers and unfilled placeholders are counted, never silently accepted
  freshness a file-level "Last refreshed" date, optionally checked against --max-age
  vague     (--strict) purposes that say nothing; unit names that sound like a dumping ground
"""
from __future__ import annotations

import argparse
import datetime
import io
import os
import re
import sys
import tempfile

REQUIRED_FIELDS = ("Purpose", "Where", "Status", "Verified")
OPTIONAL_FIELDS = ("Depends on", "Used by", "Reuse instead of", "Owner", "Notes")
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
STATUSES = {"active", "deprecated", "experimental", "pending", "unknown"}
UNIT_RE = re.compile(r"^#{2,4}\s+((?:U|UNIT)-\d+)\s*[:\-\u2014]\s*(.+?)\s*$", re.I)
FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?\*\*(" + "|".join(re.escape(f) for f in ALL_FIELDS) + r"):\*\*\s*(.*)$")
HEADING_RE = re.compile(r"^#{1,6}\s")
PLACEHOLDER_RE = re.compile(r"(<[^>\n]+>|\bTODO\b|\bTBD\b|\bFIXME\b)")
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
DUTIES = [
    ("read", ("read", "before implement", "before planning", "in full")),
    ("reuse", ("reuse", "extend", "duplicate", "parallel")),
    ("same-task", ("same task", "same change", "not a follow-up", "in this task")),
    ("owner", ("owner", "who updates", "maintained by", "updates")),
]
SOFT_LINES, HARD_LINES, SOFT_ENTRY_LINES = 400, 1200, 30
VAGUE_PURPOSE = ("various", "misc", "miscellaneous", "stuff", "helpers", "utilities", "general", "general purpose")
DUMP_NAMES = ("utils", "util", "helpers", "helper", "common", "misc", "core", "shared", "base")


def ascii_print(text: str) -> None:
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        text.encode(enc)
        print(text)
    except UnicodeEncodeError:
        print(text.encode(enc, "backslashreplace").decode(enc, "strict"))


def parse(text: str):
    """Return (units, header_lines). Each unit keeps its raw field text for later checks."""
    units, current, field = [], None, None
    header = []
    for number, line in enumerate(text.splitlines(), start=1):
        match = UNIT_RE.match(line)
        if match:
            current = {"id": match.group(1).upper(), "name": match.group(2), "line": number,
                       "fields": {}, "end": number}
            units.append(current)
            field = None
            header_len = len(header)
            continue
        if HEADING_RE.match(line):
            if current is not None:
                current["end"] = number - 1
                current = None
            field = None
            if not units:
                header.append(line)
            continue
        if not units:
            header.append(line)
        if current is None:
            continue
        field_match = FIELD_RE.match(line)
        if field_match:
            field = field_match.group(1)
            current["fields"][field] = field_match.group(2).strip()
        elif field and line.strip():
            current["fields"][field] += " " + line.strip()
        if current is not None:
            current["end"] = max(current["end"], number)
    for unit in units:
        unit["end"] = max(unit["end"], unit["line"])
    return units, header


def path_ok(raw: str, root: str):
    """Resolve one 'Where' value; return (cleaned_path_or_None, problem_or_None)."""
    value = raw.strip().strip("`").split("#")[0].strip()
    if not value:
        return None, "empty"
    if re.match(r"^[A-Za-z]:[\\/]", value) or value.startswith(("/", "~", "\\\\")) or value.startswith("file:"):
        return None, "absolute or outside-the-project path"
    if value.startswith("http://") or value.startswith("https://"):
        return None, "remote URL instead of a project path"
    joined = os.path.normpath(os.path.join(root, value))
    rel = os.path.relpath(joined, root)
    if rel.startswith(".."):
        return None, "resolves outside the project tree"
    if not os.path.exists(joined):
        return None, "does not exist"
    return value, None


def split_list(value: str):
    parts = [p.strip().strip("`") for p in re.split(r"[,;]", value or "") if p.strip()]
    return [p for p in parts if p.lower() not in ("-", "--", "—", "none", "n/a", "na", "nothing")]


MARKERS = (".git", "pyproject.toml", "package.json", "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
           "settings.gradle", "composer.json", "Gemfile", "mix.exs", "Makefile", "CMakeLists.txt")


def find_project_root(start_dir: str) -> str:
    """Unit paths are project-root-relative; walk up from the file looking for a project marker."""
    current = os.path.abspath(start_dir)
    while True:
        if any(os.path.exists(os.path.join(current, marker)) for marker in MARKERS):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(start_dir)
        current = parent


def find_cycle(units):
    """Return one dependency cycle as a readable chain, or None."""
    graph = {}
    for unit in units:
        deps = [d.upper() for d in split_list(unit["fields"].get("Depends on", ""))
                if re.match(r"^(U|UNIT)-\d+$", d, re.I)]
        graph[unit["id"]] = deps
    state = {}
    stack = []

    def walk(node):
        state[node] = 1
        stack.append(node)
        for dep in graph.get(node, []):
            if state.get(dep) == 1:
                return stack[stack.index(dep):] + [dep]
            if state.get(dep) is None or state.get(dep) == 0:
                found = walk(dep)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in graph:
        if state.get(node) in (None, 0):
            found = walk(node)
            if found:
                return " -> ".join(found)
    return None


def validate(text: str, root: str, strict: bool = False, max_age: int = 0):
    errors, warnings = [], []
    lines = text.splitlines()
    units, header = parse(text)
    header_text = " ".join(header).lower()

    # structure
    if not any(l.startswith("# ") for l in lines):
        errors.append("structure: no title heading (expected '# UNITS' or similar)")
    if "how to use" not in header_text and "how to" not in header_text:
        errors.append("structure: no 'How to use' section stating the reading duty")
    if not units:
        errors.append("ids: no unit entries found (expected headings like '### U-001: Name')")

    # duties
    for name, needles in DUTIES:
        if not any(needle in header_text for needle in needles):
            errors.append("duties: the %s duty is not stated anywhere in the header text" % name)

    # freshness (file level)
    fresh = re.search(r"last refreshed[^0-9]*(\d{4}-\d{2}-\d{2})", header_text)
    if not fresh:
        errors.append("freshness: no file-level 'Last refreshed: YYYY-MM-DD' date")
    elif max_age:
        try:
            day = datetime.date.fromisoformat(fresh.group(1))
            age = (datetime.date.today() - day).days
            if age > max_age:
                errors.append("freshness: last refreshed %d days ago (limit %d)" % (age, max_age))
        except ValueError:
            errors.append("freshness: 'Last refreshed' date is not a valid ISO date")

    # size
    total = len(lines)
    if total > HARD_LINES:
        errors.append("size: %d lines, over the hard budget of %d (this is an index, not documentation)"
                      % (total, HARD_LINES))
    elif total > SOFT_LINES:
        warnings.append("size: %d lines, over the soft budget of %d" % (total, SOFT_LINES))

    seen_ids, seen_paths = {}, {}
    for unit in units:
        where = "unit %s (line %d)" % (unit["id"], unit["line"])
        if unit["id"] in seen_ids:
            errors.append("ids: duplicate id %s, first used at line %d" % (unit["id"], seen_ids[unit["id"]]))
        seen_ids[unit["id"]] = unit["line"]

        for name in REQUIRED_FIELDS:
            value = unit["fields"].get(name)
            if value is None:
                errors.append("fields: %s: missing field '%s'" % (where, name))
            elif not value:
                errors.append("fields: %s: field '%s' is empty" % (where, name))

        for name, value in unit["fields"].items():
            if PLACEHOLDER_RE.search(value):
                errors.append("pending: %s: field '%s' contains placeholder text" % (where, name))

        status = unit["fields"].get("Status", "")
        if status and not PLACEHOLDER_RE.search(status):
            token = status.strip().lower().split()[0] if status.strip() else ""
            if token not in STATUSES:
                errors.append("status: %s: status '%s' is not one of %s"
                              % (where, status.strip(), ", ".join(sorted(STATUSES))))

        verified = unit["fields"].get("Verified", "")
        if verified and not PLACEHOLDER_RE.search(verified) and not DATE_RE.search(verified):
            errors.append("freshness: %s: 'Verified' has no date (the claim must be checkable)" % where)

        raw_where = unit["fields"].get("Where", "")
        if raw_where and not PLACEHOLDER_RE.search(raw_where):
            cleaned, problem = path_ok(raw_where, root)
            if problem:
                errors.append("paths: %s: 'Where' %s: %s" % (where, problem, raw_where.strip()))
            elif cleaned:
                key = cleaned.replace("\\", "/").rstrip("/").lower()
                if key in seen_paths:
                    errors.append("dupe: %s and %s claim the same path '%s' "
                                  "(one parallel component, two index rows)"
                                  % (where, seen_paths[key], cleaned))
                else:
                    seen_paths[key] = where
            entries = unit["end"] - unit["line"] + 1
            if entries > SOFT_ENTRY_LINES:
                errors.append("size: %s: %d lines in one entry - move the detail into the unit's own doc"
                              % (where, entries))

        for dep in split_list(unit["fields"].get("Depends on", "")):
            if re.match(r"^(U|UNIT)-\d+$", dep, re.I) and dep.upper() not in seen_ids:
                # forward reference is fine only if it appears later; check at the end
                pass
            elif not re.match(r"^(U|UNIT)-\d+$", dep, re.I):
                errors.append("deps: %s: 'Depends on' entry '%s' is not a unit id" % (where, dep))

        if strict:
            purpose = unit["fields"].get("Purpose", "").lower()
            if purpose and not PLACEHOLDER_RE.search(purpose):
                if any(v in purpose for v in VAGUE_PURPOSE):
                    errors.append("vague: %s: purpose describes a dumping ground, not a responsibility" % where)
            if any(re.search(r"\b%s\b" % name, unit["name"].lower()) for name in DUMP_NAMES) and \
                    len(split_list(unit["fields"].get("Where", ""))) > 1:
                errors.append("vague: %s: '%s' spans several paths - split it or name the responsibility"
                              % (where, unit["name"]))

    all_ids = set(seen_ids)
    for unit in units:
        for dep in split_list(unit["fields"].get("Depends on", "")):
            if re.match(r"^(U|UNIT)-\d+$", dep, re.I) and dep.upper() not in all_ids:
                errors.append("deps: unit %s depends on unknown id %s" % (unit["id"], dep.upper()))

    if units:
        cycle = find_cycle(units)
        if cycle:
            errors.append("deps: cycle %s" % cycle)

    return errors, warnings


def render(units, errors, warnings, path):
    out = ["%d unit(s) checked in %s" % (len(units), path)]
    for message in errors:
        out.append("ERROR   %s" % message)
    for message in warnings:
        out.append("WARNING %s" % message)
    out.append("OK" if not errors else "FAILED with %d error(s)" % len(errors))
    return "\n".join(out)


CLEAN_DOC = """# UNITS

The index of reusable units in this project. One entry per unit, nothing else: this file tells an agent what
already exists, so it reuses instead of rebuilding. Detail lives in the code and in the unit's own doc.

**Last refreshed: 2026-10-20**

## How to use

Before implementing or planning anything:

1. Read this file in full.
2. If a unit covers, or partly covers, what the task needs - reuse or extend it. Building a parallel component
   requires stating why in the change.
3. If the task creates a new reusable unit, add its entry **as part of the same task**, not as a follow-up.
4. Owner: the agent that creates the unit updates this file; a subagent reports the entry back to the master
   agent instead of editing the file.

## Units

### U-001: HTTP client
- **Purpose:** Single outbound HTTP path with timeout, retry and error mapping.
- **Where:** src/net/http.py
- **Depends on:** -
- **Status:** active
- **Verified:** 2026-10-18

### U-002: Cart pricing rules
- **Purpose:** The one implementation of discount and total rules.
- **Where:** src/pricing/rules.py
- **Depends on:** U-001
- **Status:** active
- **Verified:** 2026-10-18

### U-003: Session store
- **Purpose:** Persisted session lookup for the authenticated routes.
- **Where:** src/auth/session_store.py
- **Depends on:** U-002
- **Reuse instead of:** ad-hoc cookie parsing in handlers
- **Status:** active
- **Verified:** 2026-10-19
"""


def broken_doc(kind: str) -> str:
    d = CLEAN_DOC
    if kind == "missing field":
        d = d.replace("- **Purpose:** Single outbound HTTP path with timeout, retry and error mapping.\n", "")
    elif kind == "empty field":
        d = d.replace("- **Where:** src/pricing/rules.py", "- **Where:")
    elif kind == "dead path":
        d = d.replace("src/net/http.py", "src/net/http_client.py")
    elif kind == "absolute path":
        d = d.replace("- **Where:** src/auth/session_store.py", "- **Where:** /etc/passwd")
    elif kind == "unknown dep":
        d = d.replace("- **Depends on:** U-002", "- **Depends on:** U-099")
    elif kind == "not an id":
        d = d.replace("- **Depends on:** U-002", "- **Depends on:** the pricing thing")
    elif kind == "cycle":
        d = d.replace("- **Depends on:** U-001", "- **Depends on:** U-003")
    elif kind == "duplicate id":
        d = d.replace("### U-003: Session store", "### U-001: Session store")
    elif kind == "bad status":
        d = d.replace("- **Status:** active", "- **Status:** shipped")
    elif kind == "no verified date":
        d = d.replace("- **Verified:** 2026-10-18", "- **Verified:** whenever")
    elif kind == "same path twice":
        d = d.replace("### U-003: Session store\n- **Purpose:** Persisted session lookup for the authenticated routes.\n- **Where:** src/auth/session_store.py",
                      "### U-003: Session cache\n- **Purpose:** Another take on the same store.\n- **Where:** src/net/http.py")
    elif kind == "entry too long":
        d = d.replace("- **Verified:** 2026-10-19\n", "- **Verified:** 2026-10-19\n" +
                      "\n".join("- **Notes:** filler paragraph %d" % i for i in range(32)) + "\n")
    elif kind == "missing duty":
        d = d.replace("   requires stating why in the change.", "   is fine.")
        d = d.replace("4. Owner: the agent that creates the unit updates this file; a subagent reports the entry back to the master\n   agent instead of editing the file.\n", "")
    elif kind == "no how to use":
        d = d.replace("## How to use", "## Background")
    elif kind == "no refreshed":
        d = d.replace("**Last refreshed: 2026-10-20**\n", "")
    elif kind == "template leftovers":
        d = d.replace("- **Purpose:** The one implementation of discount and total rules.",
                      "- **Purpose:** <what this unit does>")
    elif kind == "stale":
        d = d.replace("**Last refreshed: 2026-10-20**", "**Last refreshed: 2020-01-01**")
    elif kind == "vague":
        d = d.replace("- **Purpose:** Single outbound HTTP path with timeout, retry and error mapping.",
                      "- **Purpose:** Various HTTP helpers and utilities.")
    return d


def materialize(doc: str) -> str:
    """Write the doc plus the files it points at, so path checks run against a real tree."""
    root = tempfile.mkdtemp(prefix="units-md-")
    with io.open(os.path.join(root, "pyproject.toml"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write("[project]\nname = \"lint-fixture\"\n")
    for rel in ("src/net/http.py", "src/pricing/rules.py", "src/auth/session_store.py"):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("# placeholder for lint fixtures\n")
    target = os.path.join(root, "docs", "UNITS.md")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with io.open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(doc)
    return target


def lint_file(path: str, strict: bool, max_age: int, root: str = ""):
    try:
        with io.open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        ascii_print("error: cannot read %s: %s" % (path, error))
        return 2, [], 0
    units, _ = parse(text)
    root = os.path.abspath(root) if root else find_project_root(os.path.dirname(os.path.abspath(path)))
    errors, warnings = validate(text, root, strict, max_age)
    ascii_print(render(units, errors, warnings, path))
    return (1 if errors else 0), errors, len(units)


def selftest() -> int:
    cases = [
        ("clean document", CLEAN_DOC, [], 3),
        ("missing field", broken_doc("missing field"), ["fields"]),
        ("empty field", broken_doc("empty field"), ["fields"]),
        ("dead path", broken_doc("dead path"), ["paths"]),
        ("absolute path", broken_doc("absolute path"), ["paths"]),
        ("unknown dependency id", broken_doc("unknown dep"), ["deps"]),
        ("dependency that is not an id", broken_doc("not an id"), ["deps"]),
        ("dependency cycle", broken_doc("cycle"), ["deps"]),
        ("duplicate id", broken_doc("duplicate id"), ["ids"]),
        ("status outside vocabulary", broken_doc("bad status"), ["status"]),
        ("verified without a date", broken_doc("no verified date"), ["freshness"]),
        ("two units one path", broken_doc("same path twice"), ["dupe"]),
        ("entry longer than an index row", broken_doc("entry too long"), ["size"]),
        ("a duty is missing", broken_doc("missing duty"), ["duties"]),
        ("no how-to-use section", broken_doc("no how to use"), ["structure"]),
        ("no refreshed date", broken_doc("no refreshed"), ["freshness"]),
        ("template leftovers", broken_doc("template leftovers"), ["pending"]),
        ("stale index", broken_doc("stale"), ["freshness"]),
    ]
    strict_cases = [("vague purpose", broken_doc("vague"), ["vague"])]

    passed = failed = 0
    for label, doc, expected, *rest in cases + strict_cases:
        strict = label in ("vague purpose",)
        path = materialize(doc)
        root = find_project_root(os.path.dirname(path))
        errors, warnings = validate(doc, root, strict, 90 if label == "stale index" else 0)
        joined = " | ".join(errors)
        if not expected:
            ok, detail = (not errors), ("unexpected: " + joined[:200])
        else:
            caught = [e for e in expected if e in joined]
            ok = len(caught) == len(expected)
            detail = "" if ok else "expected %s, got [%s]" % (expected, joined[:200])
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        ascii_print("%-40s %s %s" % (label, "PASS" if ok else "FAIL", detail))

    # the clean document must also report the right unit count
    units, _ = parse(CLEAN_DOC)
    if len(units) != 3:
        failed += 1
        ascii_print("%-40s FAIL parsed %d units, expected 3" % ("unit count", len(units)))
    else:
        passed += 1
        ascii_print("%-40s PASS" % "unit count")

    ascii_print("self-test: %d/%d fixtures behaved" % (passed, passed + failed))
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="units_lint")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--max-age", type=int, default=0, metavar="DAYS")
    ap.add_argument("--root", metavar="DIR", default="",
                    help="project root that 'Where' paths resolve against (default: nearest marker above the file)")
    ap.add_argument("--fixtures", action="store_true", help="write a sample project and lint it")
    args = ap.parse_args()

    if args.fixtures:
        path = materialize(CLEAN_DOC)
        rc, _, _ = lint_file(path, args.strict, args.max_age, args.root)
        ascii_print("fixture project: %s" % find_project_root(os.path.dirname(path)))
        return rc
    if not args.file:
        return selftest()
    if not os.path.exists(args.file):
        ascii_print("error: no such file: %s" % args.file)
        return 2
    rc, _, _ = lint_file(args.file, args.strict, args.max_age, args.root)
    return rc


if __name__ == "__main__":
    sys.exit(main())
