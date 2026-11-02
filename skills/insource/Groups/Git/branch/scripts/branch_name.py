#!/usr/bin/env python3
"""branch_name.py - check and build branch names against the project's chosen convention.

Mechanical only: it validates shape and suggests a spelling. It never decides what a branch
should be called, and it never installs a hook or CI rule.

Conventions:
  conventional   <type>/<description> per Conventional Branch v1.1.0 (types incl. AI prefixes)
  gitflow        feature|bugfix|hotfix|release|develop + trunk
  issue-first    <tracker>-<number>-<summary>, e.g. 1234-login-page
  owner-first    <owner>/<type>/<summary>, e.g. amrmar/feat/login-page
  flat           single-token or hyphenated name with no slash at all
  regex=...      the project's own pattern (put it in AGENTS.md and pass --regex)

Usage:
  python branch_name.py check feature/login-page --convention conventional
  python branch_name.py check main --convention conventional          # trunk names are always valid
  python branch_name.py check FIX/Login --convention conventional     # exit 1, with the reason
  python branch_name.py suggest login page --type feature --issue 1234
  python branch_name.py conventions                                    # list what each allows
  python scripts/branch_name.py                                        # self-test

Exit: 0 valid (or suggestion printed) · 1 invalid · 2 usage error. stdout is ASCII.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

TRUNKS = ("main", "master", "develop", "trunk")
CB_TYPES = {
    "feature": ["feat"], "bugfix": ["fix"], "hotfix": [], "release": [], "chore": [],
    "ai": [], "claude": [], "codex": [], "copilot": [], "cursor": [],
}
GF_TYPES = {"feature": [], "bugfix": [], "hotfix": [], "release": [], "support": []}
# Conventional Branch v1.1.0 grammar, transcribed:
#   desc-segment = 1*(ALPHA / DIGIT) *("." 1*(ALPHA / DIGIT))
#   description  = desc-segment *("-" desc-segment)
SEGMENT = r"[a-z0-9]+(?:\.[a-z0-9]+)*"
DESC = r"%s(?:-%s)*" % (SEGMENT, SEGMENT)

CONVENTIONS = {
    "conventional": r"^(?:%s|(?:%s)/%s)$" % ("|".join(TRUNKS),
                                             "|".join(sorted(set(list(CB_TYPES) +
                                                                 [a for v in CB_TYPES.values() for a in v]))),
                                             DESC),
    "gitflow": r"^(?:%s|(?:%s)/%s)$" % ("|".join(TRUNKS), "|".join(sorted(GF_TYPES)), DESC),
    "issue-first": r"^\d+(?:-%s)?$" % DESC,
    "owner-first": r"^[a-z0-9][a-z0-9.-]*/(?:%s)/%s$" % (
        "|".join(sorted(set(list(CB_TYPES) + [a for v in CB_TYPES.values() for a in v]))), DESC),
    "flat": r"^%s$" % DESC,
}

TYPE_MEANING = {
    "feature": "new functionality; long enough to build, short enough to merge",
    "feat": "alias of feature",
    "bugfix": "a fix that is not urgent",
    "fix": "alias of bugfix",
    "hotfix": "urgent fix, usually against a released version",
    "release": "preparing a release (version in the description)",
    "chore": "maintenance that is not a feature or a fix",
    "support": "git-flow: branch supporting an old release line",
    "ai": "work produced by an AI agent (vendor-neutral)",
    "claude": "work produced by Claude Code",
    "codex": "work produced by OpenAI Codex",
    "copilot": "work produced by GitHub Copilot",
    "cursor": "work produced by Cursor",
}

BAD_REASON = [
    (re.compile(r"[A-Z]"), "uppercase letters: refs are files under .git/refs/heads and macOS/Windows "
                           "filesystems are case-insensitive, so Feature/x and feature/x collide there and not on Linux"),
    (re.compile(r"\s"), "whitespace: unusable in shell commands and pathspecs"),
    (re.compile(r"_"), "underscore: use hyphens between words"),
    (re.compile(r"--"), "consecutive hyphens"),
    (re.compile(r"\.\."), "consecutive dots"),
    (re.compile(r"-\."), "hyphen next to a dot"),
    (re.compile(r"\.-"), "dot next to a hyphen"),
    (re.compile(r"^[-.]|[-.]$"), "leading or trailing hyphen/dot"),
    (re.compile(r"[^a-zA-Z0-9._/-]"), "characters outside a-z 0-9 . _ - /"),
]


def emit(text=""):
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        text.encode(enc)
        print(text)
    except UnicodeEncodeError:
        print(text.encode(enc, "backslashreplace").decode(enc, "strict"))


def check(name, convention, custom=None):
    """Return (ok, reason, parsed) for one branch name."""
    if convention.startswith("regex=") or custom:
        pattern = custom or convention[len("regex="):]
        try:
            ok = re.fullmatch(pattern, name) is not None
        except re.error as e:
            return False, "the configured pattern is not a valid regex: %s" % e, {}
        return ok, ("" if ok else "does not match the project's pattern %s" % pattern), {}
    if convention not in CONVENTIONS:
        return False, "unknown convention %r (try: %s)" % (
            convention, ", ".join(sorted(CONVENTIONS))), {}
    for rule, reason in BAD_REASON:
        if rule.search(name):
            return False, reason, {}
    if re.fullmatch(CONVENTIONS[convention], name):
        parsed = {}
        if "/" in name:
            head, _, tail = name.partition("/")
            parsed = {"prefix": head, "description": tail}
            if head in TYPE_MEANING:
                parsed["meaning"] = TYPE_MEANING[head]
        else:
            parsed = {"trunk": name in TRUNKS}
        return True, "", parsed
    if convention == "conventional" and "/" not in name:
        return False, "no type/ prefix and not a trunk name (main, master, develop)", {}
    if convention in ("conventional", "gitflow"):
        allowed = CB_TYPES if convention == "conventional" else GF_TYPES
        aliases = [a for v in allowed.values() for a in v]
        prefix = name.split("/", 1)[0]
        if prefix not in allowed and prefix not in aliases:
            return False, "'%s/' is not an allowed type in %s (choose: %s%s)" % (
                prefix, convention, ", ".join(sorted(allowed)),
                ", ".join(", " + a for a in sorted(aliases)) if aliases else ""), {}
    if convention == "conventional":
        prefix = name.split("/", 1)[0]
        if prefix not in CB_TYPES and prefix not in [a for v in CB_TYPES.values() for a in v]:
            return False, "'%s/' is not an allowed type: %s" % (prefix, ", ".join(sorted(CB_TYPES))), {}
    return False, "does not match the %s pattern" % convention, {}


def suggest(words, type_name, issue, convention):
    desc = re.sub(r"[^a-z0-9]+", "-", words.lower()).strip("-.")
    if not desc:
        return None, "nothing usable in the description"
    if convention == "issue-first":
        if not issue:
            return None, "issue-first needs --issue <number>"
        name = "%s-%s" % (issue, desc)
    elif convention == "owner-first":
        return None, "owner-first needs the owner: pass --owner"
    elif convention in ("conventional", "gitflow"):
        alias = {"feat": "feature", "fix": "bugfix"}.get(type_name, type_name)
        allowed = CB_TYPES if convention == "conventional" else GF_TYPES
        if alias not in allowed:
            return None, "type %r is not part of %s (choose: %s)" % (
                type_name, convention, ", ".join(sorted(allowed)))
        name = "%s/%s" % (type_name, ("%s-%s" % (issue, desc)) if issue else desc)
    else:
        name = ("%s-%s" % (issue, desc)) if issue else desc
    ok, reason, _ = check(name, convention)
    if not ok:
        return None, "%s would be invalid: %s" % (name, reason)
    return name, None


def selftest():
    n = bad = 0

    def expect(name, cond, detail=""):
        nonlocal n, bad
        n += 1
        emit("%-52s %s %s" % (name, "PASS" if cond else "FAIL", "" if cond else str(detail)[:110]))
        bad += 0 if cond else 1

    ok, why, _ = check("feature/login-page", "conventional"); expect("valid feature", ok, why)
    ok, _, _ = check("feat/login-page", "conventional"); expect("feat alias", ok)
    ok, _, _ = check("fix/header-bug", "conventional"); expect("fix alias", ok)
    ok, _, _ = check("release/v1.2.0", "conventional"); expect("dots for versions", ok)
    ok, _, _ = check("feature/issue-123-new-login", "conventional"); expect("ticket inline", ok)
    ok, _, _ = check("claude/refactor-auth", "conventional"); expect("AI agent prefix", ok)
    ok, _, _ = check("main", "conventional"); expect("trunk needs no prefix", ok)
    ok, _, _ = check("develop", "gitflow"); expect("develop is trunk", ok)
    ok, why, _ = check("Feature/Login", "conventional"); expect("uppercase rejected", not ok, why)
    ok, why, _ = check("feature/new--login", "conventional"); expect("double hyphen rejected", not ok, why)
    ok, why, _ = check("release/v1.-2.0", "conventional"); expect("hyphen next to dot rejected", not ok, why)
    ok, why, _ = check("feature/-login", "conventional"); expect("leading hyphen rejected", not ok, why)
    ok, why, _ = check("feature/login page", "conventional"); expect("space rejected", not ok, why)
    ok, why, _ = check("feature/login_page", "conventional"); expect("underscore rejected", not ok, why)
    ok, why, _ = check("unknown/some-task", "conventional"); expect("unknown prefix rejected", not ok, why)
    ok, why, _ = check("login-page", "conventional"); expect("missing type/ reported", not ok and "prefix" in why, why)
    ok, _, _ = check("1234-login-page", "issue-first"); expect("issue-first form", ok)
    ok, _, _ = check("1234", "issue-first"); expect("bare number allowed (no summary)", ok)
    ok, why, _ = check("feat-1234-login", "issue-first"); expect("issue-first rejects prefix", not ok, why)
    ok, _, _ = check("amro/feature/login-page", "owner-first"); expect("owner-first form", ok)
    ok, _, _ = check("login-page", "flat"); expect("flat form", ok)
    ok, why, _ = check("feature/x", "flat"); expect("flat rejects slash", not ok, why)
    ok, _, _ = check("any/thing-1", "regex", custom=r"[a-z0-9/-]+"); expect("custom regex honored", ok)
    ok, why, _ = check("x", "regex", custom="("); expect("broken custom regex reported, not crashed",
                                                        not ok and "regex" in why, why)
    ok, why, _ = check("feature/x", "nonsense"); expect("unknown convention reported", not ok, why)
    name, err = suggest("Add login PAGE", "feature", None, "conventional")
    expect("suggest normalizes words", name == "feature/add-login-page", (name, err))
    name, err = suggest("login", "feature", "1234", "conventional")
    expect("suggest inserts the issue", name == "feature/1234-login", (name, err))
    name, err = suggest("login", "refactor", None, "conventional")
    expect("suggest refuses a non-type", name is None and "not part of" in (err or ""), (name, err))
    name, err = suggest("login", None, None, "issue-first")
    expect("issue-first suggest needs --issue", name is None, (name, err))
    name, err = suggest("", "feature", None, "conventional")
    expect("empty description refused", name is None, (name, err))
    _, _, parsed = check("hotfix/security-patch", "conventional")
    expect("parse reports meaning", parsed.get("meaning", "").startswith("urgent"), parsed)
    emit("self-test: %d/%d checks passed" % (n - bad, n))
    return 0 if bad == 0 else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = argparse.ArgumentParser(prog="branch_name")
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check")
    c.add_argument("name")
    c.add_argument("--convention", default="conventional")
    c.add_argument("--regex", dest="custom")
    c.add_argument("--json", action="store_true")
    s = sub.add_parser("suggest")
    s.add_argument("words", nargs="+")
    s.add_argument("--type", default="feature")
    s.add_argument("--issue")
    s.add_argument("--owner")
    s.add_argument("--convention", default="conventional")
    sub.add_parser("conventions")
    args = ap.parse_args(argv)

    if not argv:
        return selftest()
    if args.cmd == "check":
        ok, reason, parsed = check(args.name, args.convention, args.custom)
        if args.json:
            emit(json.dumps({"name": args.name, "convention": args.convention, "valid": ok,
                             "reason": reason, "parsed": parsed}, indent=2))
        else:
            emit("%-6s %s" % ("VALID" if ok else "INVALID", args.name))
            if reason:
                emit("  why: %s" % reason)
            if parsed:
                emit("  parsed: %s" % ", ".join("%s=%s" % kv for kv in sorted(parsed.items())))
        return 0 if ok else 1
    if args.cmd == "suggest":
        conv = args.convention
        if conv == "owner-first":
            owner = args.owner or "owner"
            emit("pattern: %s/<type>/<description>  e.g. %s/%s/..." % (owner, owner, args.type))
            return 0
        name, err = suggest("-".join(args.words), args.type, args.issue, conv)
        if err:
            emit("CANNOT SUGGEST: %s" % err)
            return 2
        emit(name)
        return 0
    emit("conventions and what each accepts:")
    for key, pattern in sorted(CONVENTIONS.items()):
        emit("  %-13s %s" % (key, pattern))
    emit("")
    emit("types (Conventional Branch v1.1.0):")
    for key, aliases in sorted(CB_TYPES.items()):
        emit("  %-9s %s%s" % (key, TYPE_MEANING.get(key, ""), "  aliases: " + ", ".join(aliases) if aliases else ""))
    emit("  trunks: %s (no prefix)" % ", ".join(TRUNKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
