#!/usr/bin/env python3
"""agents_lint.py - check an AGENTS.md against the agents-md constraints.

Mechanical, conservative, and deliberately boring: it verifies structure and references, not taste.

Usage:
  python scripts/agents_lint.py AGENTS.md              standard checks
  python scripts/agents_lint.py AGENTS.md --strict     adds vague-mandate and doc-dump heuristics
  python scripts/agents_lint.py --fixtures             write a sample project to a temp dir and lint it
  python scripts/agents_lint.py                        self-test (15 fixtures; every defect must be caught)

Exit: 0 clean, 1 findings, 2 usage/read error. Paths are resolved relative to the AGENTS.md directory.
stdout is ASCII.

Checks:
  section   the ten required sections exist, in canonical order
  size      line budget (soft 420, hard 500) and per-section bloat
  scope     the active-context fence names BOTH what is in scope and what is excluded
  links     every referenced relative path resolves; no absolute or foreign-project paths
  structure "read everything in <dir/>" rows, unbalanced managed-block markers, template leftovers
  pending   unanswered items are counted, never silently filled
  freshness the maintenance section exists, carries the update duty, and has a recent review date
  block     the subagent block: size, required slots, clause-to-section traceability
  vague     (--strict) unfalsifiable obligations
  prose     (--strict) sections that read like documentation
"""
from __future__ import annotations

import argparse
import datetime
import io
import os
import re
import sys
import tempfile

SOFT_LINES, HARD_LINES, SOFT_SECTION = 420, 500, 70

# canonical section -> the heading keywords that count as it (real projects rename things)
SECTIONS = [
    (("agent instructions", "core rules", "ground rules", "behavior", "principles", "general rules"), "1"),
    (("mandatory context", "context", "read first", "source of truth", "steering"), "2"),
    (("development workflow", "workflow", "branching", "release", "versioning", "git"), "3"),
    (("units", "component index", "catalog", "registry"), "4"),
    (("design", "prototype", "mockup", "visual"), "5"),
    (("execution", "shell", "command", "tooling", "tool usage", "terminal"), "6"),
    (("environment", "env", "secrets", "configuration", "config"), "7"),
    (("debugging", "debug", "diagnos", "troubleshoot"), "8"),
    (("startup", "starting", "session start", "bootstrap", "begin work", "agent execution"), "9"),
    (("subagent", "sub-agent", "delegation", "agent pool", "fan-out", "master agent", "orchestrat"), "10"),
    (("rulebook maintenance", "maintenance", "keeping the rulebook", "staying current",
      "up-to-date", "currency"), "11"),
]
SECTION_LABELS = ["agent instructions", "mandatory context", "development workflow", "units", "design",
                  "execution", "environment", "debugging", "startup", "subagent", "maintenance"]
BLOCK_SLOTS = ("TASK-SPECIFIC DOCS", "SCOPE", "OUTPUT CONTRACT")
# clause keyword -> the section that must exist for the clause to be traceable
BLOCK_CLAUSES = {
    "CONTEXT": "mandatory context",
    "SKILLS": "agent instructions",
    "SHELL": "execution",
    "TOOLING": "execution",
    "ENV": "environment",
    "DEBUG": "debugging",
    "UNITS": "units",
    "REPORT": "subagent",
}
VAGUE_PATTERNS = [
    r"\bwrite clean code\b", r"\bbest practices\b", r"\bbe careful\b", r"\buse common sense\b",
    r"\bappropriately\b", r"\bas needed\b", r"\bproperly handle\b", r"\bffollow conventions\b",
    r"\bmake it robust\b",
]
PLACEHOLDER = re.compile(r"<!--\s*(e\.g\.|path|one line|pending|\s*--)")
TODO = re.compile(r"\b(TODO:|FIXME|XXX(?!-)|<placeholder>)\b", re.I)
PATHISH = re.compile(r"(?:^|[\s|`(])((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+\.[a-z]{1,8})")
ABSOLUTE = re.compile(r"(?:^|[\s|`(])((?:[A-Za-z]:[\\/]|\\\\|/(?:home|Users|var|opt|srv|mnt)/)[^\s|`)']*)")
MANAGED_BEGIN = re.compile(r"<!--\s*(?:BEGIN|start)\b", re.I)
MANAGED_END = re.compile(r"<!--\s*(?:END|stop)\b", re.I)


def headings(lines: list[str]) -> list[tuple[int, str]]:
    """Section headings only (level 2-3). The document's H1 title is not a section."""
    inside = False
    out = []
    for i, l in enumerate(lines):
        if re.match(r"^\s*```", l):
            inside = not inside
            continue
        if inside:
            continue
        if re.match(r"^#{2,3}\s", l):
            out.append((i, l))
    return out


def section_map(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Map each canonical section label to its (start, end) line range, by heading keyword."""
    hs = headings(lines)
    out: dict[str, tuple[int, int]] = {}
    for idx, (line_no, text) in enumerate(hs):
        low = text.lower()
        end = hs[idx + 1][0] if idx + 1 < len(hs) else len(lines)
        for aliases, num in SECTIONS:
            label = SECTION_LABELS[int(num) - 1]
            if label not in out and any(a in low for a in aliases):
                out[label] = (line_no, end)
                break
    return out


def find_blocks(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Fenced code blocks that contain the pasteable preferences header."""
    marker = re.compile(r"^\s{0,3}```")
    out, i = [], 0
    while i < len(lines):
        if marker.match(lines[i]):
            body, j = [], i + 1
            while j < len(lines) and not marker.match(lines[j]):
                body.append(lines[j])
                j += 1
            if any("MANDATORY" in x.upper() and "PREFERENCES" in x.upper() for x in body):
                out.append((i, body))
            i = j + 1
        else:
            i += 1
    return out


def lint(path: str, strict: bool = False) -> list[str]:
    raw = io.open(path, encoding="utf-8", errors="replace").read()
    lines = raw.split("\n")
    base = os.path.dirname(os.path.abspath(path))
    f: list[str] = []

    # ---------- sections and order
    present = section_map(lines)
    missing = [label for label in SECTION_LABELS if label not in present]
    for key in missing:
        f.append("section: missing the '%s' section (see references/00) - if it genuinely does not apply, "
                 "say so in one line inside the nearest section" % key)
    order = [present[k][0] for k in SECTION_LABELS if k in present]
    if order != sorted(order):
        f.append("section: the sections are out of canonical order (1 agent instructions -> 10 subagents)")

    # ---------- size
    total = len([l for l in lines if l.strip()])
    if total > HARD_LINES:
        f.append("size: %d non-blank lines - over the %d budget; move explanations into referenced docs and "
                 "keep the obligations here" % (total, HARD_LINES))
    elif total > SOFT_LINES:
        f.append("size: %d non-blank lines - approaching the %d budget" % (total, HARD_LINES))
    for key, (a, b) in present.items():
        if b - a > SOFT_SECTION:
            f.append("size: the '%s' section is %d lines - that is a document with a pointer missing"
                     % (key, b - a))

    # ---------- active scope fence
    ctx_a, ctx_b = present.get("mandatory context", (0, len(lines)))
    window = "\n".join(lines[ctx_a:ctx_b]).lower()
    has_active = bool(re.search(r"active|current version|in scope", window))
    has_excl = bool(re.search(r"out of scope|excluded|do not read|ignore", window))
    if "mandatory context" in present:
        if not has_active:
            f.append("scope: the context section never states which version/channel is ACTIVE")
        if not has_excl:
            f.append("scope: nothing is marked OUT OF SCOPE - reading is not permission; name the paths the "
                     "agent must treat as absent")

    # ---------- maintenance duty and review freshness
    if "maintenance" in present:
        a, b = present["maintenance"]
        block = "\n".join(lines[a:b])
        m = re.search(r"last review\w*[**_ :]*?(\d{4}-\d{2}-\d{2})", block, re.I)
        if not m:
            f.append("freshness: the maintenance section has no 'Last reviewed: YYYY-MM-DD' line - a rulebook "
                     "without a review date is assumed stale")
        else:
            try:
                days = (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days
            except ValueError:
                days = None
                f.append("freshness: 'Last reviewed: %s' is not a valid ISO date" % m.group(1))
            if days is not None and days < 0:
                f.append("freshness: 'Last reviewed' is in the future (%s)" % m.group(1))
            elif days is not None and days > 90:
                f.append("freshness: last reviewed %d days ago - verify the active scope (section 2) and the "
                         "branch/version policy before trusting this file" % days)
        if not re.search(r"(must be updated|same change|in the same|update this file|every session)", block, re.I):
            f.append("freshness: the maintenance section states no duty to update the file in the same change "
                     "as the decision - that sentence is what makes the rule enforced")
    else:
        f.append("freshness: no maintenance section - the rulebook must carry its own update duty, or it "
                 "silently goes stale (see references/08)")

    # ---------- links and paths
    checked = set()
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            continue
        for m in re.finditer(r"\]\(([^)]+)\)", line):
            target = m.group(1).split("#")[0].strip()
            if not target or target.startswith(("http", "mailto:", "<")):
                continue
            checked.add((i, target))
        for m in ABSOLUTE.finditer(line):
            f.append("links: absolute or foreign-project path on line %d (%r) - reference by repo-relative "
                     "path so the rulebook survives a different machine" % (i, m.group(1).strip()[:60]))
    for i, target in sorted(checked):
        if "<" in target or target.startswith(".git"):
            continue
        full = os.path.normpath(os.path.join(base, target))
        if not os.path.exists(full):
            f.append("links: dead reference on line %d -> %s (report it with an owner; do not stub it here)"
                     % (i, target))

    # ---------- directory-as-context smell
    dir_link = re.compile(r"\]\((?!https?:)[^)]+/\)")
    dir_cell = re.compile(r"\|\s*`?[A-Za-z0-9_.-]+/`?\s*\|")
    for i, line in enumerate(lines, 1):
        if (dir_link.search(line) or dir_cell.search(line)) and re.search(
                r"\bread\b|every|all files|everything", line, re.I):
            f.append("structure: line %d asks the agent to read a whole directory - name the specific files "
                     "that govern decisions instead" % i)

    # ---------- managed markers
    begins = sum(1 for l in lines if MANAGED_BEGIN.search(l))
    ends = sum(1 for l in lines if MANAGED_END.search(l))
    if begins != ends:
        f.append("structure: unbalanced managed-block markers (%d begin, %d end) - another tool's region "
                 "cannot be replaced safely" % (begins, ends))
    if begins:
        f.append("structure: note - a managed block exists (%d region(s)); verify it was copied through "
                 "verbatim and mention it in the report" % begins)

    # ---------- placeholders and pending honesty
    leftover = [i for i, l in enumerate(lines, 1) if PLACEHOLDER.search(l) and "pending" not in l.lower()]
    if leftover:
        f.append("pending: unfilled template comments on lines %s - fill them from the interview or delete "
                 "the row" % ",".join(str(x) for x in leftover[:8]))
    todos = [i for i, l in enumerate(lines, 1) if TODO.search(l)]
    if todos:
        f.append("pending: TODO/FIXME markers on lines %s - a rulebook must not carry unfinished rules "
                 "silently; use 'pending - not assumed' and number them" % ",".join(str(x) for x in todos[:6]))
    pend = len(re.findall(r"pending\s*[-–]\s*not assumed", raw, re.I))
    if pend:
        f.append("pending: %d explicit 'pending - not assumed' item(s) - list them for the user at the end"
                 % pend)

    # ---------- subagent block
    blocks = find_blocks(lines)
    if "subagent" in present and not blocks:
        f.append("block: section 10 exists but no pasteable baseline block was found - subagents do not "
                 "inherit this file, so the rules must travel in the prompt")
    for start, body in blocks:
        n = len(body)
        if n > 30:
            f.append("block: the baseline block is %d lines - pasted into every subagent prompt, so keep it "
                     "under 30" % n)
        text = "\n".join(body).upper()
        for slot in BLOCK_SLOTS:
            if slot not in text:
                f.append("block: missing the '%s' slot - the parent must fill it per delegation" % slot)
        for clause, section in BLOCK_CLAUSES.items():
            if re.search(r"^\s*\d+\.\s*" + clause, "\n".join(body), re.M) and section not in present:
                f.append("block: clause '%s' has no matching section ('%s') to trace to - the block is a "
                         "projection, not an original" % (clause, section))
    return f


# ------------------------------------------------------------------ strict

def strict_extras(path: str) -> list[str]:
    lines = io.open(path, encoding="utf-8", errors="replace").read().split("\n")
    f = []
    for i, l in enumerate(lines, 1):
        for pat in VAGUE_PATTERNS:
            if re.search(pat, l, re.I):
                f.append("vague: line %d states an unfalsifiable obligation (%r) - either make it concrete "
                         "or drop it" % (i, l.strip()[:50]))
    present = section_map(lines)
    for key, (a, b) in present.items():
        body = [l for l in lines[a + 1:b] if l.strip()]
        prose = [l for l in body if not re.match(r"^\s*(\||-|\*|\d+\.|`|>|#)", l) and len(l) > 120]
        if len(body) > 8 and len(prose) / len(body) > 0.45:
            f.append("prose: the '%s' section is %d%% long prose - that reads like documentation; move it "
                     "out and keep the obligation" % (key, round(100 * len(prose) / len(body))))
    return f


# ------------------------------------------------------------------ fixtures

CLEAN_DOC = """# Agent Instructions

Rules for AI agents in this repository, including work delegated to subagents.

## 1. Agent Instructions

- Do not contradict the steering docs without verifying the codebase first.
- State which skill you used when reporting results.

## 2. Mandatory Context

Read at conversation start; each index is a router, follow its links.

| Dimension | Active | Out of scope - do not read or apply |
|---|---|---|
| Version | v1 | `v2/` - future features only |

| File | Purpose |
|---|---|
| [docs/base.md](docs/base.md) | structure and boundaries |
| [docs/v1.md](docs/v1.md) | current scope |

## 3. Development Workflow

- Work lands on `canary`; never commit directly to `main`.

## 4. Units Reference

- Read [docs/UNITS.md](docs/UNITS.md) before implementing; add an entry for a new unit in the same task.

## 5. Design and Prototypes

| Location | Scope |
|---|---|
| [design/mvp/](design/mvp/) | active |
| [design/post-mvp/](design/post-mvp/) | excluded from current work |

## 6. Execution and Tool Usage

- Prefer `cmd`; PowerShell hangs on long commands here.
- Use `bun` only; other managers rewrite the lockfile.

## 7. Environment and Secrets

- Do not edit `.env` directly; change values in [config/config.env](config/config.env) then run the generator.

## 8. Debugging

- Inspect local data freely; ask before modifying anything outside local.

## 9. Agent Execution and Startup

- Before the first edit: read section 2, confirm the branch, run the build once.

## 10. Main Agent and Subagents

A subagent cannot see this conversation and cannot ask questions.

```text
=== MANDATORY AGENT PREFERENCES (read and follow) ===
1. CONTEXT - active version v1; ignore `v2/`; read docs/base.md and docs/v1.md
2. SKILLS - use at least one project skill
3. SHELL - cmd preferred, one command at a time
4. TOOLING - bun/bunx only
5. ENV - never edit .env; use config/config.env + generator
6. DEBUG - local inspection allowed; ask before mutating
7. UNITS - read docs/UNITS.md before implementing
8. REPORT - write agents/<name>.md when finished

TASK-SPECIFIC DOCS: <fill per delegation>
SCOPE: <paths you may modify>
OUTPUT CONTRACT: <exact deliverable>
=== END PREFERENCES ===
```

- Each subagent writes [agents/](agents/) report with goal, actions, files, decisions, verification.

## 11. Rulebook Maintenance

Every session that changes a project rule updates this file in the same change.

- **Last reviewed:** 2026-10-27
- New channel/version: update section 2. New or renamed doc: update its row.
"""


def broken_doc(kind: str) -> str:
    d = CLEAN_DOC
    if kind == "missing section":
        d = d.replace("## 7. Environment and Secrets", "## 7. Environment")
        d = d.replace("Environment and Secrets strategy", "x")
        d = re.sub(r"## 7. Environment[\s\S]*?## 8\.", "## 8.", d)
    elif kind == "out of order":
        a = d.index("## 1. Agent Instructions"); b = d.index("## 2. Mandatory Context")
        c = d.index("## 3. Development Workflow")
        d = d[:a] + d[b:c] + d[a:b] + d[c:]
    elif kind == "dead link":
        d = d.replace("docs/v1.md", "docs/does-not-exist.md")
    elif kind == "absolute path":
        d = d.replace("config/config.env", "C:/Users/dev/config.env")
    elif kind == "no excluded scope":
        d = d.replace("| Version | v1 | `v2/` - future features only |", "| Version | v1 | |")
        d = d.replace("Out of scope - do not read or apply", "Notes")
        d = d.replace("ignore `v2/`;", "")
    elif kind == "block slots":
        d = d.replace("OUTPUT CONTRACT: <exact deliverable>", "")
    elif kind == "template leftovers":
        d = d.replace("- Inspect local data freely; ask before modifying anything outside local.",
                      "- <!-- e.g. what is permitted -->")
    elif kind == "over budget":
        d = d + "\n".join("- filler rule %d to blow the budget for the test" % i for i in range(420))
    elif kind == "dir as context":
        d = d.replace("| [docs/base.md](docs/base.md) | structure and boundaries |",
                      "| [docs/](docs/) | read everything in docs |")
    elif kind == "unbalanced markers":
        d = d.replace("## 3. Development Workflow",
                      "<!-- BEGIN pinned-skills -->\n\n## 3. Development Workflow")
    elif kind == "no maintenance section":
        d = re.sub(r"## 11\. Rulebook Maintenance[\s\S]*", "", d)
    elif kind == "stale review":
        d = re.sub(r"\*\*Last reviewed:\*\* \d{4}-\d{2}-\d{2}", "**Last reviewed:** 2020-01-01", d)
    elif kind == "no review date":
        d = re.sub(r"- \*\*Last reviewed:\*\* .*\n", "", d)
    elif kind == "vague":
        d = d.replace("- Do not contradict the steering docs without verifying the codebase first.",
                      "- Write clean code and follow best practices.")
    return d


FIXTURES = [
    ("clean document", CLEAN_DOC, []),
    ("missing section", broken_doc("missing section"), ["section"]),
    ("out of order", broken_doc("out of order"), ["section"]),
    ("dead link", broken_doc("dead link"), ["links"]),
    ("absolute path", broken_doc("absolute path"), ["links"]),
    ("no excluded scope", broken_doc("no excluded scope"), ["scope"]),
    ("block missing a slot", broken_doc("block slots"), ["block"]),
    ("template leftovers", broken_doc("template leftovers"), ["pending"]),
    ("over line budget", broken_doc("over budget"), ["size"]),
    ("directory as context", broken_doc("dir as context"), ["structure"]),
    ("unbalanced markers", broken_doc("unbalanced markers"), ["structure"]),
    ("vague mandate", broken_doc("vague"), []),
    ("no maintenance section", broken_doc("no maintenance section"), ["maintenance", "freshness"]),
    ("stale review date", broken_doc("stale review"), ["freshness"]),
    ("no review date", broken_doc("no review date"), ["freshness"]),
]


def materialize(doc: str) -> str:
    """Write the doc plus the files it references, so link checks run against real paths."""
    root = tempfile.mkdtemp(prefix="agents-md-")
    for rel in ("docs/base.md", "docs/v1.md", "docs/UNITS.md", "config/config.env"):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        io.open(p, "w", encoding="utf-8").write("stub\n")
    for d in ("design/mvp", "design/post-mvp", "agents"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    io.open(os.path.join(root, "AGENTS.md"), "w", encoding="utf-8", newline="\n").write(doc)
    return os.path.join(root, "AGENTS.md")


def selftest() -> int:
    fails = 0
    for name, doc, expect in FIXTURES:
        path = materialize(doc)
        findings = lint(path, strict=(name == "vague mandate"))
        joined = " | ".join(findings)
        if name == "clean document":
            ok = not findings
            detail = "" if ok else "unexpected: " + joined[:220]
        elif name == "vague mandate":
            ok = bool(strict_extras(path))
            detail = "" if ok else "strict mode found nothing vague"
        else:
            caught = [e for e in expect if e in joined]
            ok = len(caught) == len(expect)
            detail = "" if ok else "expected %s, got [%s]" % (expect, joined[:200])
        print("%-28s %s %s" % (name, "PASS" if ok else "FAIL", detail))
        fails += 0 if ok else 1
    print("self-test: %d/%d fixtures behaved" % (len(FIXTURES) - fails, len(FIXTURES)))
    return 0 if fails == 0 else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="agents_lint.py")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--fixtures", action="store_true")
    a = ap.parse_args(argv)
    if a.fixtures:
        path = materialize(CLEAN_DOC)
        print("sample project written; lint it:", path)
        findings = lint(path, a.strict)
        for f in findings:
            print("  - %s" % f)
        return 1 if findings else 0
    if not a.file:
        return selftest()
    if not os.path.exists(a.file):
        print("error: no such file: %s" % a.file)
        return 2
    findings = lint(a.file, a.strict)
    if a.strict:
        findings += strict_extras(a.file)
    print("%s: %d finding(s)" % (a.file, len(findings)))
    for f in findings:
        print("  - %s" % f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:])