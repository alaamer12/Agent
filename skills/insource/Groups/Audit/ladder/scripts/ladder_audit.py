#!/usr/bin/env python3
"""ladder_audit.py - find the four defects that make an ordered rule list wrong in production.

Checks, in order of how they bite:
  terminal      no rung that always answers, so unknown input falls through
  shadow        an earlier rule whose condition covers a later one (later rule is dead)
  unreachable   a rule no probed input can reach, given the rules above it
  order-mode    the matching mode's promise is violated (all-match mode that still depends on order)
  impure        a condition that reads the clock, randomness, stdin or the network
  schema        duplicate ids, unknown fields, unknown operators

Usage:
  python3 scripts/ladder_audit.py                  # self-test (must report every injected defect)
  python3 scripts/ladder_audit.py rules.yaml       # audit a rule list
  python3 scripts/ladder_audit.py rules.json

Rule format (YAML subset or JSON):

  matching: first            # first | all-strictest | all-permissive | unique
  facts: [tool, cmd, budget]
  rules:
    - id: rm-rf
      when: {field: cmd, op: starts, value: "rm -rf"}
      verdict: deny
    - id: catch-all
      when: {always: true}
      verdict: ask
      terminal: true

Ops: eq ne gt gte lt lte in starts. Conditions nest: {all: [...]}, {any: [...]}, {not: {...}}.
Windows: run with `python` - `python3` is often a Store stub.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field

IMPURE_TOKENS = ("time()", "datetime", "random", "input(", "open(", "fetch(", "http")


# ---------------------------------------------------------------- parsing

def split_top(text: str, sep: str) -> list[str]:
    parts, depth, buf = [], 0, ""
    for ch in text:
        if ch in "[{(":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(buf)
            buf = ""
        else:
            buf += ch
    parts.append(buf)
    return [p.strip() for p in parts if p.strip()]


def scalar(text: str):
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        return [scalar(p) for p in split_top(text[1:-1], ",")]
    if text.startswith("{") and text.endswith("}"):
        out = {}
        for part in split_top(text[1:-1], ","):
            k, _, v = part.partition(":")
            out[k.strip()] = scalar(v)
        return out
    if text in ("true", "false"):
        return text == "true"
    if text.strip("-").isdigit():
        return int(text)
    return text.strip("'\"")


def parse(text: str) -> dict:
    """YAML subset: top-level scalars/lists, `rules:` as a list of one-key-per-line maps."""
    if text.lstrip().startswith("{"):
        return json.loads(text)
    doc: dict = {"rules": []}
    current: dict | None = None
    in_rules = False
    for raw in text.split("\n"):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if line.startswith("- "):
            key, _, val = line[2:].partition(":")
            current = {key.strip(): scalar(val)}
            if in_rules:
                doc["rules"].append(current)
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if not val:
            in_rules = key == "rules"
            continue
        target = current if (indent >= 4 and current is not None and in_rules) else doc
        target[key] = scalar(val)
    return doc


# ---------------------------------------------------------------- conditions

def fields_of(cond: dict) -> list[str]:
    if "always" in cond:
        return []
    if "all" in cond:
        return [f for c in cond["all"] for f in fields_of(c)]
    if "any" in cond:
        return [f for c in cond["any"] for f in fields_of(c)]
    if "not" in cond:
        return fields_of(cond["not"])
    return [cond.get("field", "?")]


def atoms(cond: dict) -> list[tuple[str, str, object]]:
    """Flat list of (field, op, value) triples, negations dropped - used for probing only."""
    if "always" in cond:
        return []
    out: list[tuple[str, str, object]] = []
    if "all" in cond:
        for c in cond["all"]:
            out += atoms(c)
    elif "any" in cond:
        out += atoms(cond["any"][0]) if cond["any"] else []
    elif "not" not in cond:
        out.append((cond["field"], cond["op"], cond["value"]))
    return out


def evaluate(cond: dict, facts: dict, known: list[str]) -> tuple[bool, list[str]]:
    """True when every field the condition reads is present and satisfied. Reports unknown fields."""
    errs: list[str] = []
    if "always" in cond:
        return True, errs
    if "all" in cond:
        results = []
        for c in cond["all"]:
            ok, e = evaluate(c, facts, known)
            results.append(ok)
            errs += e
        return all(results), errs
    if "any" in cond:
        results = []
        for c in cond["any"]:
            ok, e = evaluate(c, facts, known)
            results.append(ok)
            errs += e
        return any(results), errs
    if "not" in cond:
        ok, e = evaluate(cond["not"], facts, known)
        return (not ok), e
    fname, op, want = cond["field"], cond["op"], cond["value"]
    if fname not in facts:
        errs.append(fname)
        return False, errs
    have = facts[fname]
    try:
        if op == "eq":
            return have == want, errs
        if op == "ne":
            return have != want, errs
        if op == "gt":
            return have > want, errs
        if op == "gte":
            return have >= want, errs
        if op == "lt":
            return have < want, errs
        if op == "lte":
            return have <= want, errs
        if op == "in":
            return have in want, errs
        if op == "starts":
            return str(have).startswith(str(want)), errs
    except TypeError:
        return False, errs + [f"{fname}:{op}:type"]
    return False, errs + [f"{fname}:{op}:unknown-op"]


def covers(early: dict, late: dict) -> bool:
    """Conservative: True only when provable that every fact matching `late` also matches `early`."""
    if "always" in early:
        return True
    if "all" in late:                      # a conjunction is covered when one conjunct is
        return any(covers(early, c) for c in late["all"])
    if "all" in early and "all" in late:
        return all(any(covers(e, l) for e in early["all"]) for l in late["all"])
    if "any" in late:
        return all(covers(early, c) for c in late["any"])
    if "all" in early or "not" in late:
        return False
    if {"all", "any", "not"} & set(early) or late.get("field") != early.get("field"):
        return False
    ef, eop, ev = early["field"], early["op"], early["value"]
    lf, lop, lv = late["field"], late["op"], late["value"]
    if eop == "eq":
        return lop == "eq" and ev == lv or (lop == "in" and isinstance(lv, list) and set(lv) <= {ev})
    if eop == "in":
        return lop == "in" and isinstance(ev, list) and isinstance(lv, list) and set(lv) <= set(ev)
    if eop == "starts":
        if lop != "starts":
            return False
        return str(ev) == str(lv) or str(lv).startswith(str(ev))
    if eop in ("gt", "gte"):
        return (lop in ("gt", "gte") and isinstance(lv, (int, float)) and isinstance(ev, (int, float))
                and lv >= ev)
    if eop in ("lt", "lte"):
        return (lop in ("lt", "lte") and isinstance(lv, (int, float)) and isinstance(ev, (int, float))
                and lv <= ev)
    return False


def can_co_hold(a: dict, b: dict) -> bool:
    """Is there any fact set satisfying both? Conservative in the useful direction: it only reports a
    contradiction it can prove (two different equalities on one field, an equality outside an `in`
    set, or an equality that cannot start with a required prefix)."""
    eqs: dict[str, set] = {}
    ins: dict[str, set] = {}
    prefixes: dict[str, list[str]] = {}
    for cond in (a, b):
        for fname, op, value in atoms(cond):
            if op == "eq":
                eqs.setdefault(fname, set()).add(value)
            elif op == "in" and isinstance(value, list):
                ins.setdefault(fname, set()).update(value)
            elif op == "starts":
                prefixes.setdefault(fname, []).append(str(value))
    for fname, values in eqs.items():
        if len(values) > 1:
            return False                       # tool == bash and tool == net cannot both hold
        only = next(iter(values))
        if fname in ins and only not in ins[fname]:
            return False
        for prefix in prefixes.get(fname, []):
            if not str(only).startswith(prefix):
                return False
    for fname, prefixes_here in prefixes.items():
        if len(prefixes_here) > 1 and not any(p2.startswith(p1) or p1.startswith(p2)
                                             for p1 in prefixes_here for p2 in prefixes_here):
            return False
    return True


# ---------------------------------------------------------------- probing

def candidates(rules: list[dict], known: list[str]) -> list[dict]:
    """Sample facts built from the rules' own equality/`in`/`starts` atoms, plus wild cards."""
    out: list[dict] = []
    for r in rules:
        cand: dict = {}
        for fname, op, value in atoms(r.get("when", {})):
            if op == "eq":
                cand[fname] = value
            elif op == "in" and isinstance(value, list) and value:
                cand[fname] = value[0]
            elif op == "starts":
                cand[fname] = str(value)
            elif op in ("gt", "gte") and isinstance(value, (int, float)):
                cand[fname] = value + 1
            elif op in ("lt", "lte") and isinstance(value, (int, float)):
                cand[fname] = value - 1
        for f in known:
            cand.setdefault(f, f"probe-{f}")
        out.append(cand)
    for mixed in ({f: f"probe-{f}" for f in known},):
        for r in rules:
            for fname, op, value in atoms(r.get("when", {})):
                if op == "starts":
                    mixed[fname] = str(value) + "-extra"
        out.append(mixed)
    return out


def decide(rules: list[dict], mode: str, facts: dict, known: list[str]) -> tuple[str | None, list[str]]:
    hits = []
    for r in rules:
        ok, _ = evaluate(r.get("when", {}), facts, known)
        if ok:
            hits.append(r)
    if not hits:
        return None, []
    if mode == "first":
        return hits[0]["id"], [h["id"] for h in hits]
    order = {"deny": 0, "ask": 1, "allow": 2}
    if mode == "all-strictest":
        win = min(hits, key=lambda h: order.get(h.get("verdict", "ask"), 1))
        return win["id"], [h["id"] for h in hits]
    if mode == "all-permissive":
        win = max(hits, key=lambda h: order.get(h.get("verdict", "ask"), 1))
        return win["id"], [h["id"] for h in hits]
    return hits[0]["id"], [h["id"] for h in hits]


# ---------------------------------------------------------------- audit

VERDICT_RANK = {"deny": 0, "ask": 1, "allow": 2}


@dataclass
class Finding:
    kind: str
    detail: str
    rule: str = ""


@dataclass
class Audit:
    mode: str = "first"
    facts: list[str] = field(default_factory=list)
    rules: list[dict] = field(default_factory=list)


def audit(doc: dict) -> list[Finding]:
    findings: list[Finding] = []
    rules = doc.get("rules", [])
    mode = doc.get("matching", "first")
    known = doc.get("facts") or sorted({f for r in rules for f in fields_of(r.get("when", {}))})

    ids = [r.get("id", "?") for r in rules]
    for dup in {i for i in ids if ids.count(i) > 1}:
        findings.append(Finding("schema", f"duplicate id {dup!r} - ids are the audit trail", str(dup)))

    for i, r in enumerate(rules):
        cond = r.get("when", {})
        text = json.dumps(cond)
        if any(tok in text for tok in IMPURE_TOKENS):
            findings.append(Finding("impure", f"{r['id']} condition reads a mutable/external source", r["id"]))
        for fname in fields_of(cond):
            if known and fname not in known and fname != "?":
                findings.append(Finding("schema", f"{r['id']} reads unknown field {fname!r}", r["id"]))
        for fname, op, _ in atoms(cond):
            if op not in ("eq", "ne", "gt", "gte", "lt", "lte", "in", "starts"):
                findings.append(Finding("schema", f"{r['id']} uses unknown operator {op!r}", r["id"]))
        if r.get("terminal") and i != len(rules) - 1:
            findings.append(Finding("terminal", f"{r['id']} marked terminal but is not the last rule", r["id"]))

    if not any(r.get("terminal") or "always" in r.get("when", {}) for r in rules):
        findings.append(Finding("terminal",
                               "no terminal rung: an input matching nothing falls through as no verdict"))

    for i, early in enumerate(rules):
        for j in range(i + 1, len(rules)):
            late = rules[j]
            if covers(early.get("when", {}), late.get("when", {})):
                findings.append(Finding("shadow",
                                        f"{early['id']} (rule {i + 1}) covers {late['id']} (rule {j + 1}): "
                                        f"the later rule can never win", late["id"]))

    for i, early in enumerate(rules):
        for j in range(i + 1, len(rules)):
            late = rules[j]
            ev, lv = early.get("verdict"), late.get("verdict")
            if ev in VERDICT_RANK and lv in VERDICT_RANK and VERDICT_RANK[ev] > VERDICT_RANK[lv]:
                if covers(early.get("when", {}), late.get("when", {})) or (
                        can_co_hold(early.get("when", {}), late.get("when", {}))
                        and "always" not in late.get("when", {})):
                    findings.append(Finding("severity-inversion",
                                            f"{early['id']} ({ev}) is evaluated before {late['id']} ({lv}) "
                                            f"and both can hold: the permissive rule preempts the strict one. "
                                            f"Reorder, or put the strict verdict in a tier", late["id"]))

    probes = candidates(rules, known)
    for r in rules:
        reached = False
        for facts in probes:
            winner, _ = decide(rules, mode, facts, known)
            if winner == r["id"]:
                reached = True
                break
        if not reached:
            findings.append(Finding("unreachable",
                                    f"{r['id']} won no probe input; a shadow or a dead rule", r["id"]))

    if mode in ("all-strictest", "all-permissive", "unique"):
        for facts in probes:
            base = decide(rules, mode, facts, known)[0]
            for shuffled in (rules[1:] + rules[:1], list(reversed(rules))):
                if decide(shuffled, mode, facts, known)[0] != base:
                    findings.append(Finding("order-mode",
                                            f"mode {mode!r} still depends on list order for "
                                            f"{json.dumps(facts, sort_keys=True)}"))
                    break

    if "ordering_key" not in doc and not any("priority" in r or "rank" in r for r in rules):
        findings.append(Finding("order-mode",
                                "no ordering_key declared and no rule carries priority/rank: the winner "
                                "is list position, which is a policy somebody will change by accident"))
    return findings


def render(findings: list[Finding]) -> str:
    if not findings:
        return "CLEAN: terminal rung present, no shadows, every rule reachable, mode matches ordering."
    by: dict[str, list[Finding]] = {}
    for f in findings:
        by.setdefault(f.kind, []).append(f)
    lines = []
    for kind in ("terminal", "shadow", "severity-inversion", "unreachable", "order-mode", "impure", "schema"):
        for f in by.get(kind, []):
            lines.append(f"FINDING {kind:12} {f.detail}")
    return "\n".join(lines)


# ---------------------------------------------------------------- self-test

SELF_TESTS = [
    ("missing terminal", {
        "matching": "first", "ordering_key": "position", "facts": ["tool"],
        "rules": [{"id": "a", "when": {"field": "tool", "op": "eq", "value": "bash"}, "verdict": "allow"}]},
     {"terminal"}),
    ("shadow by equality", {
        "matching": "first", "ordering_key": "position", "facts": ["tool", "cmd"],
        "rules": [
            {"id": "broad", "when": {"field": "tool", "op": "eq", "value": "bash"}, "verdict": "allow"},
            {"id": "specific", "when": {"all": [{"field": "tool", "op": "eq", "value": "bash"},
                                                 {"field": "cmd", "op": "starts", "value": "git push"}]},
             "verdict": "ask"},
            {"id": "catch", "when": {"always": True}, "verdict": "ask", "terminal": True}]},
     {"shadow", "unreachable"}),
    ("shadow by prefix", {
        "matching": "first", "ordering_key": "position", "facts": ["cmd"],
        "rules": [
            {"id": "l-loose", "when": {"field": "cmd", "op": "starts", "value": "l"}, "verdict": "allow"},
            {"id": "ls-la", "when": {"field": "cmd", "op": "starts", "value": "ls -la"}, "verdict": "ask"},
            {"id": "catch", "when": {"always": True}, "verdict": "ask", "terminal": True}]},
     {"shadow", "unreachable"}),
    ("unique mode with overlapping rules still picks by position", {
        "matching": "unique", "facts": ["cmd"],
        "rules": [
            {"id": "any-cmd", "when": {"always": True}, "verdict": "allow"},
            {"id": "rm-rf", "when": {"field": "cmd", "op": "starts", "value": "rm -rf"}, "verdict": "deny"}]},
     {"order-mode", "shadow"}),
    ("impure predicate", {
        "matching": "first", "ordering_key": "position", "facts": ["cmd"],
        "rules": [
            {"id": "flaky", "when": {"field": "cmd", "op": "eq", "value": "random()"}, "verdict": "ask"},
            {"id": "catch", "when": {"always": True}, "verdict": "ask", "terminal": True}]},
     {"impure"}),
    ("schema drift", {
        "matching": "first", "ordering_key": "position", "facts": ["tool"],
        "rules": [
            {"id": "typo", "when": {"field": "toool", "op": "equals", "value": "bash"}, "verdict": "allow"},
            {"id": "catch", "when": {"always": True}, "verdict": "ask", "terminal": True}]},
     {"schema", "unreachable"}),
    ("permissive rule before a strict one", {
        "matching": "first", "ordering_key": "priority", "facts": ["tool", "cmd"],
        "rules": [
            {"id": "any-bash", "priority": 10, "when": {"field": "tool", "op": "eq", "value": "bash"},
             "verdict": "allow"},
            {"id": "rm-rf", "priority": 20, "when": {"field": "cmd", "op": "starts", "value": "rm -rf"},
             "verdict": "deny"},
            {"id": "catch", "priority": 99, "when": {"always": True}, "verdict": "ask", "terminal": True}]},
     {"severity-inversion"}),
    ("clean ladder", {
        "matching": "first", "ordering_key": "tier+priority", "facts": ["tool", "cmd"],
        "rules": [
            {"id": "rm-rf", "priority": 1, "when": {"field": "cmd", "op": "starts", "value": "rm -rf"}, "verdict": "deny"},
            {"id": "git-push", "priority": 2, "when": {"field": "cmd", "op": "starts", "value": "git push"}, "verdict": "ask"},
            {"id": "read-only", "priority": 3, "when": {"field": "tool", "op": "eq", "value": "read"}, "verdict": "allow"},
            {"id": "bash", "priority": 4, "when": {"field": "tool", "op": "eq", "value": "bash"}, "verdict": "allow"},
            {"id": "catch", "priority": 99, "when": {"always": True}, "verdict": "ask", "terminal": True}]},
     set()),
]


def self_test() -> int:
    failures = 0
    for label, doc, expect_kinds in SELF_TESTS:
        found = audit(doc)
        kinds = {f.kind for f in found}
        if expect_kinds:
            ok = expect_kinds <= kinds
            print(f"{'PASS' if ok else 'FAIL'}  {label:32} expected {sorted(expect_kinds)} got {sorted(kinds)}")
        else:
            ok = not found
            print(f"{'PASS' if ok else 'FAIL'}  {label:32} expected no findings, got {render(found)}")
        failures += not ok
    print("\nOK" if not failures else f"\n{failures} FAILED")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if not argv:
        return self_test()
    text = open(argv[0], encoding="utf-8").read()
    doc = parse(text)
    findings = audit(doc)
    print(f"rules={len(doc.get('rules', []))} matching={doc.get('matching', 'first')}")
    print(render(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
