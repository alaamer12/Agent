#!/usr/bin/env python3
"""agents_lint.py - check an AGENTS.md against the agents-md constraints.

Mechanical, conservative, and deliberately boring: it verifies structure and references, not taste.

Usage:
  python scripts/agents_lint.py AGENTS.md              standard checks
  python scripts/agents_lint.py AGENTS.md --strict     adds vague-mandate and doc-dump heuristics
  python scripts/agents_lint.py --fixtures             write a sample project to a temp dir and lint it
  python scripts/agents_lint.py                        self-test (30 fixtures; every defect must be caught)

Exit: 0 clean, 1 findings, 2 usage/read error. Paths are resolved relative to the AGENTS.md directory.
stdout is ASCII.

Checks:
  section   all nineteen required sections exist, in canonical order - empty means guide+none-recorded
  how-to    the How To section routes task class to registered docs (no path duplication with
            section 2) with a read-before-duty
  instructs section 1 carries a standing directive or says none recorded - the behavioral contract
            (declaration lines, skill floors, pre-workflows) was asked, not forgotten
  size      line budget (soft 420, hard 500) and the 50-line per-section budget
  scope     the active-context fence names BOTH what is in scope and what is excluded, and every
            dimension states its REACH (what it governs / how to recognize it), not a bare label
  links     every referenced relative path resolves; no absolute or foreign-project paths
  structure "read everything in <dir/>" rows, unbalanced managed-block markers, template leftovers
  privacy   the Privacy section carries the .gitignore-sync duty and the ask-before-cache-clear rule
  resourceful the Resourceful section states local-over-global for dependencies and toolchains
  authority the Authority section names the ask-per-session default and the honest-consult rule
  version-control the Version Control section states operation tiers, a stash policy, and commit authorship
  ambiguity the Ambiguity section names Exact/Broad question modes, the mandatory-ask rule, the pre-anonymous rule
  golden    the Golden Rules section states absolute, violation-shaped rules
  review    the Review section puts AGENTS.md/golden-rule violation-finding first
  facts     the Facts section carries the fixed trust-over-memory paragraph and the recording duty
  rituals   the before-between-after section sets the always-on task phases + the user-override rule
  voice     the Voice section names the chosen register, records the user's own, and governs written docs
  sync-blk  each sync block is one table: locations + line anchors + the meaning law + same-change duty
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

SOFT_LINES, HARD_LINES, SOFT_SECTION = 420, 500, 50

# canonical section -> the heading keywords that count as it (real projects rename things)
SECTIONS = [
    (("agent instructions", "core rules", "ground rules", "behavior", "principles", "general rules"), "1"),
    (("mandatory context", "context", "read first", "source of truth", "steering"), "2"),
    (("how to", "how-to", "how to do things", "procedures", "how things work", "operations guide"), "3"),
    (("design", "prototype", "mockup", "visual"), "4"),
    (("startup", "starting", "session start", "bootstrap", "begin work", "agent execution"), "5"),
    (("subagent", "sub-agent", "delegation", "agent pool", "fan-out", "master agent", "orchestrat", "agents"), "6"),
    (("privacy", "visibility", "confidential", "what to hide", "private paths", "secrecy"), "7"),
    (("resourceful", "local first", "local-first", "project local", "project-local", "local resources",
      "project resources"), "8"),
    (("authority", "permissions", "permission", "what agents may do", "consent", "ask per session"), "9"),
    (("skills", "skill notes", "skill instructions", "skill registry", "per-skill"), "10"),
    (("rulebook maintenance", "maintenance", "keeping the rulebook", "staying current",
      "up-to-date", "currency"), "11"),
    (("version control", "source control", "git", "scm", "commit policy", "git policy", "vcs"), "12"),
    (("ambiguity", "asking style", "question style", "question mode", "exact or broad"), "13"),
    (("golden rules", "golden", "non-negotiable", "hard rules", "commandments"), "14"),
    (("review", "reviewing", "bug hunt", "audit routine"), "15"),
    (("facts", "verified facts", "fact log", "corrections"), "16"),
    (("before-between-after", "before between after", "task rituals", "rituals", "before, between", "always-on routine"), "17"),
    (("voice", "tone", "speaking style", "communication style", "how to talk", "register"), "18"),
    (("sync blocks", "synced blocks", "synchronized blocks", "sync-blocks", "linked blocks",
      "block sync", "shared meaning"), "19"),
]
SECTION_LABELS = ["agent instructions", "mandatory context", "how to", "design",
                  "startup", "subagent", "privacy", "resourceful",
                  "authority", "skills", "maintenance", "version control", "ambiguity", "golden rules", "review", "facts", "before-between-after",
                  "voice", "sync blocks"]
BLOCK_SLOTS = ("TASK-SPECIFIC DOCS", "SCOPE", "OUTPUT CONTRACT")
# clause keyword -> the section that must exist for the clause to be traceable
BLOCK_CLAUSES = {
    "CONTEXT": "mandatory context",
    "SKILLS": "agent instructions",
    "SHELL": "how to",
    "TOOLING": "how to",
    "ENV": "how to",
    "DEBUG": "how to",
    "UNITS": "mandatory context",
    "REPORT": "subagent",
    "PRIVACY": "privacy",
    "RESOURCEFUL": "resourceful",
    "AUTHORITY": "authority",
    "VCS": "version control",
    "GOLDEN": "golden rules",
    "FACTS": "facts",
    "VOICE": "voice",
    "SYNC": "sync blocks",
}
VAGUE_PATTERNS = [
    r"\bwrite clean code\b", r"\bbest practices\b", r"\bbe careful\b", r"\buse common sense\b",
    r"\bappropriately\b", r"\bas needed\b", r"\bproperly handle\b", r"\bfollow conventions\b",
    r"\bmake it robust\b",
]
PLACEHOLDER = re.compile(r"<!--\s*(e\.g\.|path|one line|pending|\s*--)")
TODO = re.compile(r"\b(TODO:|FIXME|XXX(?!-)|<placeholder>)\b", re.I)
PATHISH = re.compile(r"(?:^|[\s|`(])((?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+\.[a-z]{1,8})")
ABSOLUTE = re.compile(r"(?:^|[\s|`(])((?:[A-Za-z]:[\\/]|\\\\|/(?:home|Users|var|opt|srv|mnt)/)[^\s|`)']*)")
MANAGED_BEGIN = re.compile(r"<!--\s*(?:BEGIN|start)\b", re.I)
MANAGED_END = re.compile(r"<!--\s*(?:END|stop)\b", re.I)


def headings(lines: list[str]) -> list[tuple[int, str]]:
    """Candidate section headings at ANY level. A section's identity is its canonical title and its
    order, never the # depth or a numbering scheme - the heading shape belongs to the writer and the
    harness (sections living at ##, ###, or # under a project doc are all valid). A single H1 before
    every other heading is the document title, not a section."""
    inside = False
    out = []
    for i, l in enumerate(lines):
        if re.match(r"^\s*```", l):
            inside = not inside
            continue
        if inside:
            continue
        if re.match(r"^#{1,6}\s", l):
            out.append((i, l))
    return out


def section_map(lines: list[str]) -> dict[str, tuple[int, int]]:
    """Map each canonical section label to its (start, end) line range, by heading keyword.

    A section's range runs to the next heading of ITS OWN level or shallower, so ### subsections
    stay inside their parent section; alias matching is word-bounded so "facts" cannot hide in
    "artifacts".
    """
    hs = headings(lines)
    levels = [len(t) - len(t.lstrip("#")) for _, t in hs]
    # a single level-1 heading standing before all sections is the document title, not a candidate
    title_idx = 0 if levels and levels[0] == 1 and levels.count(1) == 1 else -1
    out: dict[str, tuple[int, int]] = {}
    for idx, (line_no, text) in enumerate(hs):
        if idx == title_idx:
            continue
        low = text.lower()
        end = len(lines)
        for j in range(idx + 1, len(hs)):
            if levels[j] <= levels[idx]:
                end = hs[j][0]
                break
        for aliases, num in SECTIONS:
            label = SECTION_LABELS[int(num) - 1]
            if label not in out and any(re.search(r"(?<![A-Za-z])" + re.escape(a) + r"s?(?![A-Za-z])", low)
                                        for a in aliases):
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
        f.append("section: missing the '%s' section - every section EXISTS when the file is created; an "
                 "unpopulated one keeps its guide paragraph plus 'none recorded yet', it is never deleted "
                 "(see references/00)" % key)
    order = [present[k][0] for k in SECTION_LABELS if k in present]
    if order != sorted(order):
        f.append("section: the sections are out of canonical order (1 agent instructions -> 19 sync blocks); "
                 "identity is title + order - heading depth is the writer's, the order is not")

    # ---------- document title vs section names
    h1 = next((l for l in lines if re.match(r"^# \S", l)), "")
    h1t = re.sub(r"[^a-z ]", "", h1[1:].lower()).strip()
    for _, t in headings(lines):
        if t == h1:
            continue  # the writer's shape is flexible; only a DIFFERENT heading may duplicate the title
        title = re.sub(r"[^a-z ]", "", re.sub(r"^#+\s*\d+\.?\s*", "", t).lower()).strip()
        if h1t and title and h1t == title:
            f.append("structure: the document title '%s' duplicates a section's name - the H1 names the "
                     "rulebook (e.g. '<project> - Agent Rulebook'); a section name belongs to its section "
                     "alone" % h1[2:].strip())
            break

    # ---------- size
    total = len([l for l in lines if l.strip()])
    if total > HARD_LINES:
        f.append("size: %d non-blank lines - over the %d budget; move explanations into referenced docs and "
                 "keep the obligations here" % (total, HARD_LINES))
    elif total > SOFT_LINES:
        f.append("size: %d non-blank lines - approaching the %d budget" % (total, HARD_LINES))
    for key, (a, b) in present.items():
        if b - a > SOFT_SECTION:
            f.append("size: the '%s' section is %d lines - over the %d-line section budget; extract the detail "
                     "to a referenced doc and keep the obligations here"
                     % (key, b - a, SOFT_SECTION))

    # ---------- agent instructions duty (the behavioral contract was asked)
    if "agent instructions" in present:
        a, b = present["agent instructions"]
        iblock = "\n".join(lines[a:b])
        rules = [l for l in iblock.split("\n") if l.startswith("- ") and "<!--" not in l]
        if not rules and not re.search(r"none recorded", iblock, re.I):
            f.append("instructions: section 1 carries no standing directive and no emptiness statement - "
                     "the interview must ASK how every agent is to behave and be followed: [declaration "
                     "lines] (last line names the skills used), [skill-usage floors] (attempt a skill per "
                     "response), [mandatory pre-workflows] (grill-me before implementation) - user-chosen "
                     "examples; if the user chose none, write 'none recorded yet', never blank")

    # ---------- how-to duties (the router)
    if "how to" in present:
        a, b = present["how to"]
        hblock = "\n".join(lines[a:b]).lower()
        if not re.search(r"(read|open)\b[^.\n]{0,80}(before|first)", hblock):
            f.append("how-to: no read-the-doc duty - before acting on a task class, the agent must read "
                     "the routed how-to file; the router without the duty is decoration")
        if not re.search(r"task class|per task|its task|task type", hblock):
            f.append("how-to: the router must map task class to doc (that mapping IS the token "
                     "efficiency: the agent opens only the file the task needs)")
        rows = [l for l in lines[a:b] if l.strip().startswith("|") and "---" not in l]
        if len(rows) - 1 < 3:
            f.append("how-to: a thin router - the split is the point: [execution], [environment], [version], [development], [debugging] each own their doc, and a grown topic splits further (version/main.md, version/canary.md); one or two routing lines means procedures are still squatting in the rulebook")
        if not re.search(r"section 2|registered|one owner", hblock):
            f.append("how-to: paths duplicate section 2's registry - the docs are REGISTERED once in "
                     "the Mandatory Context table; How To maps task class to doc name only, no second path list")
        rows = [l for l in lines[a:b] if l.strip().startswith("|") and "---" not in l]
        if len(rows) - 1 < 4:
            f.append("how-to: a thin router - the split by TASK CLASS is the point (which classes and which "
                     "doc names a project uses is its own - [development], [debugging], [commands], "
                     "[configuration], [releases]... are illustrative pairings, not required rows); one or "
                     "two routing lines mean procedures are still squatting in the rulebook")

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
        if not re.search(r"recogniz\w*|govern\w*|surface|affect\w*|flag|suffix|naming|pattern|applies to",
                         window):
            f.append("scope: a dimension is a bare label with no REACH - state what the active value GOVERNS "
                     "and how the agent recognizes it: the dimension can split the docs tree (docs/[main] vs "
                     "docs/[canary]), the code tree, a [build flag], a file-naming pattern, and which rules "
                     "apply; one word in a cell hides all of that. A dimension that truly reaches nothing "
                     "says so ('docs split only'); an empty label is the shallow fence")

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
        found = set(int(x) for x in re.findall(r"\|\s*(\d{1,2})[ 	][^|]*\|\s*$", block, re.M))
        need = set(range(1, len(SECTIONS) + 1))
        gone = sorted(need - found)
        if gone:
            f.append("freshness: the decision map in section 11 lacks a row for section(s) %s - every section "
                     "needs its trigger row, or changes to it route nowhere and the file rots there"
                     % ", ".join(str(x) for x in gone))
    else:
        f.append("freshness: no maintenance section - the rulebook must carry its own update duty, or it "
                 "silently goes stale (see references/08)")

    # ---------- privacy duties
    if "privacy" in present:
        a, b = present["privacy"]
        pblock = "\n".join(lines[a:b]).lower()
        if "gitignore" not in pblock:
            f.append("privacy: the Privacy section does not require every private path to also appear in "
                     ".gitignore - an ignore rule without the ignore file is only an intention")
        if not re.search(r"ask[^.]{0,60}(cache|clear|delete|remove)|git rm --cached", pblock):
            f.append("privacy: the Privacy section lacks the ask-before-clearing-the-cache rule - a path "
                     "tracked before it was declared private stays visible until the cache is cleared, and "
                     "that removal must be asked for, never assumed")

    # ---------- resourceful duty
    if "resourceful" in present:
        a, b = present["resourceful"]
        rblock = "\n".join(lines[a:b]).lower()
        if "local" not in rblock or "global" not in rblock:
            f.append("resourceful: the Resourceful section does not state the local-over-global rule - "
                     "name what stays project-local (dependencies, toolchains, environments) and that "
                     "global installs are named exceptions")

    # ---------- authority duty
    if "authority" in present:
        a, b = present["authority"]
        ablock = "\n".join(lines[a:b]).lower()
        if "ask" not in ablock and "consult" not in ablock:
            f.append("authority: the Authority section states neither the ask-per-session default nor the "
                     "consult-the-user rule - record which actions need permission and what happens when "
                     "the limit blocks the work")
        if "honest" not in ablock and "consult" not in ablock and "report" not in ablock:
            f.append("authority: the Authority section lacks the honest-blocked rule - when a limit stops "
                     "the requested work, the agent must say what it cannot do and ask, not silently skip")

    # ---------- version control duties
    if "version control" in present:
        a, b = present["version control"]
        gblock = "\n".join(lines[a:b]).lower()
        if not re.search(r"allow|never|forbid|prohibit|read-only|inspect|ask before", gblock):
            f.append("version-control: the Version Control section names no authority tiers - state, for the "
                     "VCS this project uses ([Git], [Unity VCS/Plastic], [Perforce], [SVN]), what is allowed "
                     "(inspect, local check-ins), what needs asking (anything outward: push/submit, shared "
                     "merges), and what is never without explicit order (published-history rewrites, "
                     "destructive restores, workspace purges, hook bypass)")
        if not re.search(r"stash|shelve|suspend|parked", gblock):
            f.append("version-control: no parked-work policy - is suspending unfinished changes allowed "
                     "(git stash / [shelve] / equivalent), and with which naming pattern? in a shared "
                     "workspace a blind pop/undrop collides with other agents")
        if not re.search(r"author|committer", gblock):
            f.append("version-control: no commit authorship rule - which identity do agent-made commits carry "
                     "(human sole author, Co-authored-by trailer, an agent identity)? the commit and branch "
                     "skills hand this decision to this section")

    # ---------- ambiguity duties
    if "ambiguity" in present:
        a, b = present["ambiguity"]
        ablock = "\n".join(lines[a:b]).lower()
        if "exact" not in ablock or "broad" not in ablock:
            f.append("ambiguity: the Ambiguity section names neither the Exact nor the Broad question mode - "
                     "record how the user wants to be asked (Exact: named implementation options; Broad: intent "
                     "only, internals decided by the agent; or both by weight)")
        if not re.search(r"mandatory|always ask|carries weight|weight", ablock):
            f.append("ambiguity: no mandatory-ask rule - state that weight-bearing decisions must be asked and "
                     "trivia (file placement, naming) stays a decision, not a question")
        if "anonymous" not in ablock and "handoff" not in ablock and "hand-off" not in ablock:
            f.append("ambiguity: no pre-anonymous rule - critical questions must be asked before the user "
                     "leaves the loop (any anonymous or delegated mode - never named by one skill), leftovers "
                     "recorded as explicit assumptions")
        if "decisions/" not in ablock or not re.search(r"one file per decision|per-decision", ablock):
            f.append("ambiguity: the Ambiguity section does not own the decision-record convention - "
                     "<docs>/decisions/<slug>.md, one file per decision, anchored Date + Commit + "
                     "App-Version; the ask-or-decide call itself gets a record too")

    # ---------- golden rules and review duties
    if "golden rules" in present:
        a, b = present["golden rules"]
        gblock = "\n".join(lines[a:b]).lower()
        if not re.search(r"never|always|without exception|non-negotiable", gblock):
            f.append("golden: the Golden Rules section states nothing absolute - a golden rule is the one that "
                     "never bends (no hardcoding - values live in [tables]/[config], never in source), phrased so the agent recognizes a "
                     "violation while writing it")
    if "review" in present:
        a, b = present["review"]
        rblock = "\n".join(lines[a:b]).lower()
        if "agents.md" not in rblock and "golden" not in rblock:
            f.append("review: the Review section does not put rulebook-violation hunting first - the highest-"
                     "priority bug hunt is finding violations of AGENTS.md and the golden rules, in code AND "
                     "in the docs, before any named review task runs")

    # ---------- facts duties
    if "facts" in present:
        a, b = present["facts"]
        fblock = "\n".join(lines[a:b]).lower()
        if not re.search(r"training|prior knowledge|from memory|prior belief", fblock):
            f.append("facts: the Facts section's fixed paragraph is missing - it must state plainly that "
                     "these bullets contradict what training or prior knowledge would assume, and that they "
                     "win over memory")
        if not re.search(r"verif|record", fblock):
            f.append("facts: no recording duty - the moment verification contradicts a prior belief, the "
                     "dated bullet (believed / actual / proven) must be appended in the same change")

    # ---------- voice duties
    if "voice" in present:
        a, b = present["voice"]
        vbox = "\n".join(lines[a:b]).lower()
        if not re.search(r"concis\w*|explanat\w*|verbos\w*|ponytail|terse|laconic|minimal", vbox):
            f.append("voice: no register is chosen - state how the agent talks: [concise] / [explanatory] "
                     "/ [verbose] / [ponytail] (the lazy-senior-dev shortest form that still proves the "
                     "point); the modes are illustrative, the CHOICE is mandatory")
        if not re.search(r"user.{0,40}(voice|register|talk|speak|phrase|vocab|direct)", vbox):
            f.append("voice: nothing records how the USER talks - their vocabulary, directness and "
                     "terseness set the level the agent answers at and mirrors in its questions")
        if not re.search(r"write|document|artifact", vbox):
            f.append("voice: the section stops at speech - the same voice governs what the agent WRITES "
                     "(reports, decision records, changelog and release prose): one voice spoken and written")
        if not re.search(r"surface|respond|reply|public|internal|README", vbox):
            f.append("voice: the section assumes ONE voice for everything - the agent can carry several: "
                     "the register for replying to the user, another for PUBLIC documents (README, release "
                     "notes, help), another for INTERNAL docs (decision records, reports, how-to docs); a "
                     "single voice across surfaces is a valid choice, but it must be CHOSEN, not defaulted")

    # ---------- sync blocks duties
    if "sync blocks" in present:
        a, b = present["sync blocks"]
        sblock = "\n".join(lines[a:b]).lower()
        if "meaning" not in sblock:
            f.append("sync-blocks: the MEANING law is absent - blocks sync in what they say, not in letters; "
                     "each home may phrase per its idiom (two SDKs, a doc pair, a config mirror say the "
                     "same rule in different correct words); drift of MEANING is the defect")
        has_table = bool(re.search(r"\|\s*(location|file|path)\w*", sblock)) and "line" in sblock
        delegated = bool(re.search(r"read:?\s*\[?[^\s\]]*\.md", sblock))
        if not (has_table or delegated):
            f.append("sync-blocks: no per-block table and no delegated file - each sync block gets ITS OWN "
                     "table (location | line anchor | what this home carries); tables live inline while tiny "
                     "and in their own file by default (<docs>/sync-blocks.md) because they grow block by "
                     "block; the law and the same-change duty stay here either way; unlisted homes are "
                     "unsynced by definition")
        if not re.search(r"same change|same commit|same edit", sblock):
            f.append("sync-blocks: no sync duty - an edit that changes one side's meaning updates every "
                     "row of that block's table in the same change; section 11 routes it")

    # ---------- before-between-after duties
    if "before-between-after" in present:
        a, b = present["before-between-after"]
        tblk = "\n".join(lines[a:b]).lower()
        if not (re.search(r"before", tblk) and re.search(r"between|while|during", tblk)
                and re.search(r"after", tblk)):
            f.append("rituals: the before-between-after section must name all three phases - what the agent "
                     "always does before a task, while working, and after finishing")
        if not re.search(r"unless|override|did not mention|explicit", tblk):
            f.append("rituals: no override rule - these rituals apply unless the user's current prompt says "
                     "otherwise; state which wins when they collide")

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
        f.append("block: section 6 exists but no pasteable baseline block was found - subagents do not "
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

CLEAN_DOC = """# Fixture Repo - Agent Rulebook

Rules for AI agents in this repository, including work delegated to subagents.

## 1. Agent Instructions

- Do not contradict the steering docs without verifying the codebase first.
- State which skill you used when reporting results.

## 2. Mandatory Context

Read at conversation start; each index is a router, follow its links.

| Dimension | Active | Recognized by - what it governs | Out of scope - do not read or apply |
|---|---|---|---|
| Version | v1 | the `v1/` code tree and docs/v1.md; docs split only | `v2/` - future features only |

| File | Purpose |
|---|---|
| [docs/base.md](docs/base.md) | structure and boundaries |
| [docs/v1.md](docs/v1.md) | current scope |
| [docs/how-to/development.md](docs/how-to/development.md) | how development works - the only registration of its path |
| [docs/how-to/debugging.md](docs/how-to/debugging.md) | how to debug |
| [docs/how-to/debugging/db.md](docs/how-to/debugging/db.md) | how to debug the data layer |
| [docs/how-to/execution.md](docs/how-to/execution.md) | how to run things: shell, chaining, the package manager, scratch scripts |
| [docs/how-to/environment.md](docs/how-to/environment.md) | how to change configuration and what the secrets strategy is |
| [docs/how-to/version.md](docs/how-to/version.md) | how versions are named, bumped, declared, released |
| [docs/UNITS.md](docs/UNITS.md) | reusable-unit index - read before implementing, reuse over duplicate, a new unit's entry lands in the same task (the units duties ride this row) |

## 3. How To

Procedures live in how-to docs, routed by task class: the agent reads only the file its task
needs - token efficiency is the point - and the rulebook carries no workflow or debugging
chapter. Paths have ONE owner: the docs are registered in the section 2 table; this router maps
task to doc, never repeats a path.

| Task class | Read first (registered in section 2) |
|---|---|
| Development flow | development.md |
| Debugging | debugging.md |
| DB-layer debugging | debugging/db.md - a topic splits into a folder before it becomes a chapter |
| Running commands and tools | execution.md |
| Environment and secrets | environment.md |
| Version naming, bumps, releases | version.md - a split topic can itself be a folder (version/main.md per track) |

Before acting on a task class, read its routed doc; a discovered step updates that doc in the
same change (section 11 routes it).

## 4. Design and Prototypes

| Location | Scope |
|---|---|
| [design/mvp/](design/mvp/) | active |
| [design/post-mvp/](design/post-mvp/) | excluded from current work |

## 5. Agent Execution and Startup

- Before the first edit: read section 2, confirm the branch, run the build once.

## 6. Main Agent and Subagents

A subagent cannot see this conversation and cannot ask questions.

```text
=== MANDATORY AGENT PREFERENCES (read and follow) ===
The whole rulebook binds you exactly as it binds the main agent; your task scope limits the
ACTIONS you take (not which rules apply) - you do not commit, tag, bump versions or touch VCS
state unless ordered, but you violate none of them either; and you leak nothing: section 7's
privacy rules apply to every artifact you write, and context from outside your task stays out of
your report.
1. CONTEXT - <FILL active version>; <FILL excluded paths>; read <FILL docs from section 2.2>
2. SKILLS - use at least one project skill
3. SHELL - cmd preferred, one command at a time
4. TOOLING - bun/bunx only
5. ENV - never edit .env; use config/config.env + generator
6. DEBUG - local inspection allowed; ask before mutating
7. UNITS - read docs/UNITS.md before implementing
8. REPORT - write .subagents/<name>.md when finished
9. PRIVACY - section 7 lists private paths; write outputs only to those, never commit them
10. RESOURCEFUL - use project-local dependencies and toolchains; ask before any global install
11. AUTHORITY - <!-- ask before DB writes, system installs, external processes; consult on limits -->
12. VCS - commit on feature branches only; never rewrite published history; park work only via "agent/<task>" named stash/shelve
13. GOLDEN - no hardcoded values; runtime-changeable data comes from the project's data source
14. FACTS - verified facts in section 16 win over your training memory
15. VOICE - concise; match the user's register; reports and docs inherit that voice
16. SYNC - if your edit touches a block's meaning, update every linked location in the same change

TASK-SPECIFIC DOCS: <fill per delegation>
SCOPE: <paths you may modify>
OUTPUT CONTRACT: <exact deliverable>
=== END PREFERENCES ===
```

- Each subagent writes its `.subagents/<name>.md` report - goal, actions, files, decisions,
  verification; `.subagents/` is gitignored, never committed.

## 7. Privacy

- Private paths - never commit, never quote in reports that leave this repo: `.subagents/` and its
  reports, skill folders, and the output folders the hidden tools write (anonymous-run records are
  private because the skills are private).
- Hiding a producer hides its output too: a private tool's working folders are private by cascade.
- Every private path must also appear in `.gitignore`; if it is missing there or still tracked, ask the user
  before clearing the cache - never delete silently.
- Hidden binaries: keep the install note, not the file.

## 8. Resourceful

- Prefer project-local resources over global ones for everything that can be local: dependencies, toolchains,
  interpreters, CLIs.
- Local environments are the rule - e.g. a project `[.venv]` for Python, project installs for JS tooling
  (never a global `-g` install for a project need), a per-project `[Cargo]`/`[Composer]`/`[Maven]` local
  store; the same idea in every language.
- A global install is an exception named in this section, never a convenience default - record it with its
  reason and who needs it.
- Run project binaries through the project's own tooling (the venv, `node_modules/.bin`, the package
  manager's exec), so the version used is the version the project pinned.

## 9. Authority

- Default: ask per session before anything outside the project's own scope - writing to an existing
  database, installing a binary system-wide, running external processes such as an emulator.
- Fixed authority, when the user grants it, is recorded here per action; project-local installs are
  section 8, not this section.
- If an authority limit blocks the requested work, the agent says honestly what it cannot do, what that
  costs, and asks whether to continue under the restriction or to grant authority.

## 10. Skills

| Skill | Use it when | Read or do first |
|---|---|---|
| `plan` | work spans more than one session | `docs/plans/README.md` - the plan format this repo follows |
| `benchmark` | comparing implementations | run it under `scratch/bench/` and delete the folder afterwards |
| `commit` | before any commit | the message map in `docs/commit-craft.md` |

## 11. Rulebook Maintenance

Every session that changes a project rule updates this file in the same change.

- **Last reviewed:** 2026-10-27

| Decision | Section |
|---|---|
| Behavioral rule changes | 1 |
| Channel/context changes | 2 |
| Doc added/renamed/moved | 2 or 4/5 - fix pointer same change |
| Branching/promotion changes | 3 |
| Units index or reuse duty changes | 2 - the duties ride the registry row |
| Design scope changes | 4 |
| Shell, package-manager or command rules change | 3 - the execution how-to doc |
| Env/secrets strategy changes | 3 - the environment how-to doc |
| Debug process/permissions change | 3 - the debugging how-to doc |
| Startup steps change | 5 |
| Delegation rules change | 6 - regenerate the block  |
| Privacy path changes | 7 - and the .gitignore line same change  |
| Local-vs-global rule changes | 8 |
| Authority setting changes | 9 |
| Skill usage note changes | 10 |
| Owner/cadence of this duty changes | 11 |
| VCS rule changes | 12 - VCS clause too  |
| Ask-mode changes | 13 |
| Golden rule changes | 14 - GOLDEN clause too  |
| Review task changes | 15 |
| Version policy changes (scheme, bump, sites, attachments) | 3 - the version how-to doc, same change |
| Prior belief corrected | 16 - dated bullet same change  |
| Ritual revealed mandatory/noise | 17 |
| The agent's speaking/writing register changes | 18 |
| A synced block's meaning changed, or a new multi-home content was found | 19 - every row of that block's table, same change  |

## 12. Version Control

- VCS in use: Git. Inspecting history/state is always allowed (status, log, diff, show); commits on
  feature branches per the development how-to doc (section 3); push and shared-branch merges need asking.
- Never without an explicit user order: `rebase`, amending pushed work, `reset --hard`, `git clean`,
  force-push.
- Parked work: stash allowed only named - `git stash push -u -m "agent/<task-slug>"` (Plastic shelve
  equivalent); restore the exact entry, never bare-pop; drop only entries this agent created.
- Change identity: check-ins keep the repository's configured identity; agent involvement is disclosed
  with a `Co-authored-by:` trailer [exact name to confirm with the user]; never edit VCS config.

## 13. Ambiguity

- Question mode: Broad by default - the user answers intent-level questions; mechanisms and internals
  are the agent's to choose, best for the project's case. Exact only for decisions the user names.
- MANDATORY: ask whenever the question carries weight (irreversible, costly, security, cross-module);
  trivia (which folder, what name) stays a decision, never a question.
- Consequential asks route through the caution skill; before any anonymous run or delegated
  hand-off, critical questions get asked first and leftovers recorded as explicit assumptions.
- Decision records: docs/decisions/<slug>.md - one file per decision, never a combined decisions.md;
  each anchored Date + Commit hash + App-Version; the ask-or-decide call itself is recorded too, and
  the anonymous ledger lives at docs/decisions/states.md.

## 14. Golden Rules

Rules that never bend, whatever the task, deadline, or context:

- **Runtime-changeable values are read only through the typed settings accessor**, which fails fast
  at startup on unknown/missing keys - source literals have no reader, so a wrong value is always a
  boot failure, never silent drift (the sanctioned path plus its loud guard, not a bare "don't").
- <!-- one absolute rule per line, each phrased so a violation is recognizable while writing it -->

## 15. Review

The highest-priority review action is always first - and it applies WHEN a review runs (a named
review task or the self-review of your own diff), not as an always-on job between unrelated tasks:
hunt violations of AGENTS.md and the golden rules - in code AND in the docs. Only then the named tasks:

- **Docs:** read all docs content; find stale/outdated passages; find unlinked docs (nothing
  points to them, so the chain cannot reach them); any doc over 500 lines becomes a folder named
  after the doc, split inside, with an index.md as its map.
- **[DB]:** learn all tables; find hardcoded/mocked-data violations against section 14 (illustrative
  task - only where a database actually exists).

## 16. Facts

These bullets are verified facts that contradict what an agent's training or prior knowledge would
assume. They win over memory; a suspect one gets re-verified, never argued from memory. When
verification contradicts a prior belief during any task, append the dated bullet in the same change:
believed / actual / how it was proven.

- **LibraryX supports Vue** - official Vue bindings ship. Prior belief: React-only. Verified
  2026-11-01 by docs + install test.

## 17. Before-Between-After

Task rituals that apply to every piece of work unless the user's current prompt says otherwise
(an explicit instruction overrides the ritual for that task only):

- **Before:** none unique - reading and scope confirmation belong to sections 2 and 9; a ritual here
  restating them is noise.
- **Between:** the section-4 reuse check is re-run at the moment of writing new logic, not only at
  planning.
- **After:** run the project's type-check gate (tsc --noEmit or its equivalent) and lint; self-review
  against section 14.

## 18. Voice

- Agent voice: concise - the answer first, reasoning on request; explanatory mode when teaching.
- Surfaces may carry different voices: replies to the user [concise]; public documents (README,
  release notes) [explanatory]; internal records and reports [ponytail - shortest that proves it].
  One voice everywhere is a valid choice, made explicitly - not the default by silence.
- The user's own register wins: their vocabulary and directness set the level the agent speaks at.
- Written reflection: the same voice governs every document and artifact the agent writes - reports,
  decision records, changelog entries. One voice, spoken and written.

## 19. Sync Blocks

Content whose meaning has more than one writable home. Blocks sync in MEANING, not in letters -
each home may phrase per its idiom; drift of what they mean is the defect. One table per block;
an edit that changes one side's meaning updates every row in the same change (section 11 routes
it), and a moved anchor is re-anchored in that same change.

### Block: version-declaration-sites

| Location | Line anchor | Carries |
|---|---|---|
| project file | `<Version>` property | the external base, the release identity |
| platform manifests | version field | the same base, store format |
| build counter file | constant | the internal track (the version how-to doc's rule bumps it) |
"""


def broken_doc(kind: str) -> str:
    d = CLEAN_DOC
    if kind == "missing section":
        d = d.replace("## 4. Design and Prototypes", "## 4. Design")
        d = re.sub(r"## 4. Design[\s\S]*?## 5\.", "## 5.", d)
    elif kind == "out of order":
        a = d.index("## 4. Design and Prototypes"); b = d.index("## 5. Agent Execution and Startup")
        c = d.index("## 6. Main Agent and Subagents")
        d = d[:a] + d[b:c] + d[a:b] + d[c:]
    elif kind == "dead link":
        d = d.replace("docs/v1.md", "docs/does-not-exist.md")
    elif kind == "absolute path":
        d = d.replace("config/config.env", "C:/Users/dev/config.env")
    elif kind == "no excluded scope":
        d = d.replace("docs/v1.md; docs split only | `v2/` - future features only |",
                      "docs/v1.md; docs split only | |")
        d = d.replace("Out of scope - do not read or apply", "Notes")
    elif kind == "shallow context":
        d = d.replace("| Dimension | Active | Recognized by - what it governs |",
                      "| Dimension | Active |")
        d = d.replace(" the `v1/` code tree and docs/v1.md; docs split only |", "")
    elif kind == "block slots":
        d = d.replace("OUTPUT CONTRACT: <exact deliverable>", "")
    elif kind == "template leftovers":
        d = d.replace("- Before the first edit: read section 2, confirm the branch, run the build once.",
                      "- <!-- e.g. what to read before editing -->")
    elif kind == "over budget":
        d = d + "\n".join("- filler rule %d to blow the budget for the test" % i for i in range(420))
    elif kind == "privacy duties":
        d = re.sub(r"- Private paths[\s\S]*?note, not the file\.",
                   "- Skill folders and their run outputs stay out of commits.\n", d)
    elif kind == "authority duties":
        d = re.sub(r"## 9\. Authority[\s\S]*?(?=## 10\.)",
                   "## 9. Authority\n\n- The user grants permissions.\n\n", d)
    elif kind == "version control duties":
        d = re.sub(r"## 12\. Version Control[\s\S]*",
                   "## 12. Version Control\n\n- Commit when the work is done.\n", d)
    elif kind == "ambiguity duties":
        d = re.sub(r"## 13\. Ambiguity[\s\S]*",
                   "## 13. Ambiguity\n\n- Ask when unsure.\n", d)
    elif kind == "golden review duties":
        d = re.sub(r"## 14\. Golden Rules[\s\S]*?## 15\. Review[\s\S]*",
                   "## 14. Golden Rules\n\n- Try not to hardcode things.\n\n"
                   "## 15. Review\n\n- Read the code carefully.\n", d)
    elif kind == "rituals duties":
        d = re.sub(r"## 17\. Before-Between-After[\s\S]*",
                   "## 17. Before-Between-After\n\n- Do the usual steps.\n", d)
    elif kind == "facts duties":
        d = re.sub(r"## 16\. Facts[\s\S]*",
                   "## 16. Facts\n\n- This library is great.\n", d)
    elif kind == "voice duties":
        d = re.sub(r"## 18\. Voice[\s\S]*",
                   "## 18. Voice\n\n- Talk to the user the usual way.\n", d)
    elif kind == "sync duties":
        d = re.sub(r"## 19\. Sync Blocks[\s\S]*",
                   "## 19. Sync Blocks\n\n- Keep duplicated things identical.\n", d)
    elif kind == "how-to missing":
        d = re.sub(r"## 3\. How To[\s\S]*?## 4\.",
                   "## 3. How To\n\n- Ask a senior developer how things work.\n\n## 4.", d)
    elif kind == "thin router":
        for row in ("| Running commands and tools | execution.md |\n",
                    "| Environment and secrets | environment.md |\n",
                    "| Version naming, bumps, releases | version.md - a split topic can itself be a folder (version/main.md per track) |\n"):
            d = d.replace(row, "")
    elif kind == "instructions empty":
        d = re.sub(r"## 1\. Agent Instructions[\s\S]*?## 2\.",
                   "## 1. Agent Instructions\n\nStable behavioral rules, independent of version, "
                   "channel, or phase.\n\n## 2.", d)
    elif kind == "resourceful duties":
        d = re.sub(r"## 8\. Resourceful[\s\S]*?## 9\.",
                   "## 8. Resourceful\n\n- Use the tooling that is available.\n\n## 9.", d)
    elif kind == "fat section":
        d = d.replace("\n## 2. Mandatory Context",
                      "".join("\n- filler rule %d for the per-section budget test" % i for i in range(55))
                      + "\n## 2. Mandatory Context")
    elif kind == "dir as context":
        d = d.replace("| [docs/base.md](docs/base.md) | structure and boundaries |",
                      "| [docs/](docs/) | read everything in docs |")
    elif kind == "unbalanced markers":
        d = d.replace("## 3. How To",
                      "<!-- BEGIN pinned-skills -->\n\n## 3. How To")
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
    ("shallow active context", broken_doc("shallow context"), ["scope"]),
    ("block missing a slot", broken_doc("block slots"), ["block"]),
    ("template leftovers", broken_doc("template leftovers"), ["pending"]),
    ("over line budget", broken_doc("over budget"), ["size"]),
    ("fat section", broken_doc("fat section"), ["size"]),
    ("privacy missing duties", broken_doc("privacy duties"), ["privacy"]),
    ("resourceful missing duties", broken_doc("resourceful duties"), ["resourceful"]),
    ("authority missing duties", broken_doc("authority duties"), ["authority"]),
    ("version control missing duties", broken_doc("version control duties"), ["version-control"]),
    ("ambiguity missing duties", broken_doc("ambiguity duties"), ["ambiguity"]),
    ("golden+review missing duties", broken_doc("golden review duties"), ["golden", "review"]),
        ("facts missing duties", broken_doc("facts duties"), ["facts:"]),
    ("rituals missing duties", broken_doc("rituals duties"), ["rituals:"]),
    ("voice missing duties", broken_doc("voice duties"), ["voice:"]),
    ("sync blocks missing duties", broken_doc("sync duties"), ["sync-blocks:"]),
    ("instructions never asked", broken_doc("instructions empty"), ["instructions:"]),
    ("how-to router missing duties", broken_doc("how-to missing"), ["how-to:"]),
    ("thin router", broken_doc("thin router"), ["how-to:"]),
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
    for rel in ("docs/base.md", "docs/v1.md", "docs/UNITS.md", "config/config.env",
               "docs/how-to/development.md", "docs/how-to/debugging.md",
               "docs/how-to/execution.md", "docs/how-to/environment.md",
               "docs/how-to/version.md",
               "docs/how-to/debugging/db.md"):
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
    sys.exit(main(sys.argv[1:]))
