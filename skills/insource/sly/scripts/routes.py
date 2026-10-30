#!/usr/bin/env python3
"""routes.py - audit a sly route plan: gate access parity, force real diversity, rank on the axes.

Usage:
  python scripts/routes.py                    self-test over 7 fixtures (must catch every injected defect)
  python scripts/routes.py plan.json          audit a plan (JSON, or the YAML subset below)
  python scripts/routes.py plan.yaml --rank   also print the weighted ranking
  echo exit codes: 0 clean, 1 findings, 2 schema/parse error

Windows: run with `python`; `python3` is often a Store stub. Output is ASCII-only.

Plan shape (YAML subset or JSON):

  goal: "the dashboard keeps showing figures we are entitled to defend"
  blocked: "shared spreadsheet access"
  value: "the same derived numbers, from a source we may read"
  acceptance: "figures match the approved export on a week of daily checks"
  class: blocker                     # snag | blocker | consequential
  block:
    verified: true
    evidence: ["their access docs list exports as per-team approved", "our token returns 403 on the sheet resource"]
  attempts:
    - {target: "sheet api", mechanism: "GET /v4/sheets/123", result: "403"}
  routes:
    - id: recompute-from-source-db
      family: rebuild                # reroute | replace | rebuild | reshape | reduce
      summary: "derive the same two columns from the database both teams read"
      access: parity                 # parity | beyond
      hardlines: []                  # auth_bypass | credentials | exploit | degradation | unauthorized
      undocumented: false
      detection: ""                  # how you will notice it broke, required if undocumented
      tradeoff: "needs their metric definitions, in writing"
      axes: {goal: 4, feasibility: 3, reliability: 4, maintainability: 3,
             security: 5, cost: 4, fit: 4, fragility: 4}
  weights: {goal: 3, feasibility: 2, reliability: 2, maintainability: 1,
            security: 2, cost: 1, fit: 1, fragility: 1.5}

Findings:
  parity        a route needs access beyond an ordinary legitimate user - vetoed, never ranked
  hardline      a named hard line is present - vetoed
  diversity     fewer than three routes, or all routes in one family (one option in costumes)
  block         block unverified, no evidence, or evidence thinner than two signals
  goal-drift    the goal still names the blocked thing - the method was never separated from the mandate
  repeat        the same target+mechanism attempted more than once - repetition, not persistence
  unscored      a route missing axes, or an axis outside 1..5
  fragile       undocumented behavior without a fragility score and a detection note
  no-reduce     every route failed the parity gate - report the block and a reduced goal
  tell          class consequential (or a flagged restriction) with no trade-off stated
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any

FAMILIES = ("reroute", "replace", "rebuild", "reshape", "reduce")
AXES = ("goal", "feasibility", "reliability", "maintainability",
        "security", "cost", "fit", "fragility")
HARDLINES = ("auth_bypass", "credentials", "exploit", "degradation", "unauthorized")
CLASSES = ("snag", "blocker", "consequential")
DEFAULT_WEIGHTS = dict(goal=3.0, feasibility=2.0, reliability=2.0, maintainability=1.0,
                       security=2.0, cost=1.0, fit=1.0, fragility=1.5)


# ------------------------------------------------------------------ parsing

def _scalar(text: str) -> Any:
    text = text.strip()
    if text.startswith("[") and text.endswith("]"):
        return [_scalar(p) for p in _split_top(text[1:-1], ",")]
    if text.startswith("{") and text.endswith("}"):
        out = {}
        for part in _split_top(text[1:-1], ","):
            k, sep, v = part.partition(":")
            if not sep:
                raise ValueError("bad inline mapping entry: %r" % part)
            out[k.strip()] = _scalar(v)
        return out
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~", ""):
        return None
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text.strip("'\"")


def _split_top(text: str, sep: str) -> list[str]:
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


def _loads_yaml(text: str) -> dict:
    """Indentation YAML subset: nested maps, block lists, flow maps/lists, comments."""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise ValueError("tabs used for indentation - use spaces")
        lines.append((len(raw) - len(raw.lstrip(" ")), raw.strip()))
    if not lines:
        return {}
    pos = [0]

    def node(indent: int):
        return lst(indent) if lines[pos[0]][1].startswith("- ") else mapping(indent)

    def mapping(indent: int) -> dict:
        out: dict = {}
        while pos[0] < len(lines) and lines[pos[0]][0] == indent:
            key, sep, val = lines[pos[0]][1].partition(":")
            if not sep:
                raise ValueError("expected 'key: value' at: %s" % lines[pos[0]][1])
            key, val = key.strip(), val.strip()
            pos[0] += 1
            if val:
                out[key] = _scalar(val)
            elif pos[0] < len(lines) and lines[pos[0]][0] > indent:
                out[key] = node(lines[pos[0]][0])
            elif pos[0] < len(lines) and lines[pos[0]][0] == indent and lines[pos[0]][1].startswith("- "):
                out[key] = lst(indent)
            else:
                out[key] = None
        return out

    def lst(indent: int) -> list:
        out: list = []
        while pos[0] < len(lines) and lines[pos[0]][0] == indent and lines[pos[0]][1].startswith("- "):
            body = lines[pos[0]][1][2:].strip()
            pos[0] += 1
            if body.startswith("{") or body.startswith("["):
                out.append(_scalar(body))
            elif re.match(r"^[A-Za-z_][\w.-]*:(\s|$)", body):
                key, _, val = body.partition(":")
                item: dict = {}
                child = indent + 2
                val = val.strip()
                if val:
                    item[key.strip()] = _scalar(val)
                elif pos[0] < len(lines) and lines[pos[0]][0] > child:
                    item[key.strip()] = node(lines[pos[0]][0])
                else:
                    item[key.strip()] = None
                while pos[0] < len(lines) and lines[pos[0]][0] == child and not lines[pos[0]][1].startswith("- "):
                    k2, sep2, v2 = lines[pos[0]][1].partition(":")
                    k2, v2 = k2.strip(), v2.strip()
                    pos[0] += 1
                    if not sep2:
                        raise ValueError("expected 'key: value' at: %s" % lines[pos[0]][1])
                    if v2:
                        item[k2] = _scalar(v2)
                    elif pos[0] < len(lines) and lines[pos[0]][0] > child:
                        item[k2] = node(lines[pos[0]][0])
                    else:
                        item[k2] = None
                out.append(item)
            else:
                out.append(_scalar(body))
        return out

    data = node(lines[0][0])
    return data if isinstance(data, dict) else {}


def load_plan(text: str) -> dict:
    stripped = text.lstrip()
    if stripped.startswith("{"):
        return json.loads(text)
    if stripped.startswith("- "):
        raise ValueError("plan must be a mapping with goal/value/routes, not a bare list")
    return _loads_yaml(text)


# ------------------------------------------------------------------ audit

def audit(plan: dict) -> tuple[list[str], list[dict]]:
    findings: list[str] = []
    goal = str(plan.get("goal") or "")
    blocked = str(plan.get("blocked") or "")
    routes = plan.get("routes") or []
    attempts = plan.get("attempts") or []
    block = plan.get("block") or {}
    cls = str(plan.get("class") or "blocker")

    for key in ("goal", "value", "acceptance"):
        if not str(plan.get(key) or "").strip():
            findings.append("schema: %s is required - the hunt needs a stated goal, value and test" % key)
    if not routes:
        findings.append("schema: no routes listed")
    if cls not in CLASSES:
        findings.append("schema: class %r must be one of %s" % (cls, " | ".join(CLASSES)))

    # goal must be stated apart from the blocked method
    if blocked and re.search(re.escape(blocked.split()[0].lower()), goal.lower()):
        findings.append("goal-drift: the goal still names the blocked thing (%r) - restate the outcome, "
                        "not the method" % blocked)

    # the block has to be proven
    if not block:
        findings.append("block: no block record - verify the block before routing around it")
    else:
        if block.get("verified") is not True:
            findings.append("block: verified is not true - one failed attempt is not proof")
        ev = [e for e in (block.get("evidence") or []) if str(e).strip()]
        if len(ev) < 2:
            findings.append("block: %d evidence signal(s) - two independent signals make a block credible"
                            % len(ev))

    # repeats: same target and mechanism more than once
    seen: dict[tuple, int] = {}
    for a in attempts:
        sig = (str(a.get("target", "")).lower(), str(a.get("mechanism", "")).lower())
        seen[sig] = seen.get(sig, 0) + 1
    for (target, mech), n in sorted(seen.items()):
        if n > 1:
            findings.append("repeat: %r via %r attempted %d times - cosmetic retries prove nothing new; "
                            "switch family" % (target, mech, n))

    # diversity across families
    if 0 < len(routes) < 3:
        findings.append("diversity: %d route(s) - generate at least three materially different options"
                        % len(routes))
    fams = {str(r.get("family", "")) for r in routes}
    for r in routes:
        if str(r.get("family", "")) not in FAMILIES:
            findings.append("schema: route %r family %r must be one of %s"
                            % (r.get("id"), r.get("family"), " | ".join(FAMILIES)))
    if len(fams) < 2 and len(routes) >= 2:
        findings.append("diversity: all routes are family %r - that is one option in costumes, not a "
                        "comparison" % (sorted(fams)[0] if fams else "?"))

    ranked, vetoed = [], []
    for r in routes:
        rid = str(r.get("id") or "?" if isinstance(r, dict) else "?")
        rid = str(r.get("id") or "?")
        lines_hit = [h for h in (r.get("hardlines") or []) if str(h).strip()]
        bad_lines = [h for h in lines_hit if str(h) not in HARDLINES]
        for h in bad_lines:
            findings.append("schema: route %s hardline %r is not a known hard line" % (rid, h))
        if str(r.get("access", "parity")) == "beyond" or lines_hit:
            vetoed.append(rid)
            why = ", ".join(str(h) for h in lines_hit) or "access beyond parity"
            findings.append("parity: route %s is vetoed (%s) - a route that needs it is not a route; it is "
                            "excluded from the ranking" % (rid, why))
        axes = r.get("axes") or {}
        missing = [a for a in AXES if a not in axes]
        if missing:
            findings.append("unscored: route %s has no score for %s" % (rid, ", ".join(missing)))
        for a, v in axes.items():
            if a not in AXES:
                findings.append("schema: route %s scores unknown axis %r" % (rid, a))
            elif not isinstance(v, (int, float)) or not 1 <= float(v) <= 5:
                findings.append("unscored: route %s axis %s=%r is outside 1..5" % (rid, a, v))
        if r.get("undocumented") is True:
            if not str(r.get("detection") or "").strip():
                findings.append("fragile: route %s leans on undocumented behavior with no detection note - "
                                "say how you will notice it broke" % rid)
            if isinstance(axes, dict) and "fragility" in axes and float(axes["fragility"]) >= 4:
                findings.append("fragile: route %s claims fragility %s while depending on undocumented "
                                "behavior" % (rid, axes["fragility"]))
        if cls == "consequential" or r.get("restriction"):
            if not str(r.get("tradeoff") or "").strip():
                findings.append("tell: route %s has real cost/contract consequences but no trade-off "
                                "stated - present options and ask" % rid)

        if rid in vetoed or missing:
            continue
        w = {**DEFAULT_WEIGHTS, **(plan.get("weights") or {})}
        total = sum(float(axes[a]) * float(w.get(a, 1)) for a in AXES) / sum(float(w.get(a, 1)) for a in AXES)
        ranked.append({"id": rid, "family": str(r.get("family", "?")), "score": round(total, 3),
                       "tradeoff": str(r.get("tradeoff") or "")})

    if routes and len(vetoed) == len(routes):
        findings.append("no-reduce: every route failed the parity gate - report what is blocked, what "
                        "legitimate access would unblock it, and what reduced goal is still possible")

    ranked.sort(key=lambda x: -x["score"])
    return findings, ranked


# ------------------------------------------------------------------ reporting

def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("-")]
    if not args:
        return selftest()
    try:
        plan = load_plan(open(args[0], encoding="utf-8").read())
    except Exception as exc:                                    # noqa: BLE001 - report, never trace
        print("schema: cannot parse %s: %s" % (args[0], exc))
        return 2
    findings, ranked = audit(plan)
    print("plan %s: %d route(s), %d finding(s)" % (args[0], len(plan.get("routes") or []), len(findings)))
    for f in findings:
        print("  - %s" % f)
    if "--rank" in argv and ranked:
        print("ranking (weighted, parity-vetoed routes excluded):")
        for i, r in enumerate(ranked, 1):
            print("  %d. %s [%s] %.3f%s" % (i, r["id"], r["family"], r["score"],
                                             " - " + r["tradeoff"] if r["tradeoff"] else ""))
    return 1 if findings else 0


# ------------------------------------------------------------------ self-test

CLEAN = {
    "goal": "the dashboard keeps showing figures we are entitled to defend",
    "blocked": "shared spreadsheet access",
    "value": "the same derived numbers, from a source we may read",
    "acceptance": "figures match the approved export on a week of daily checks",
    "class": "blocker",
    "block": {"verified": True, "evidence": ["access docs list exports as per-team approved",
                                             "our token returns 403 on the sheet resource"]},
    "attempts": [{"target": "sheet api", "mechanism": "GET /v4/sheets/123", "result": "403"}],
    "routes": [
        {"id": "recompute-from-source-db", "family": "rebuild", "access": "parity", "hardlines": [],
         "undocumented": False, "tradeoff": "needs their metric definitions in writing",
         "axes": dict(zip(AXES, [4, 3, 4, 3, 5, 4, 4, 4]))},
        {"id": "last-known-with-staleness-label", "family": "reduce", "access": "parity", "hardlines": [],
         "undocumented": False, "tradeoff": "the numbers lag and everyone can see they lag",
         "axes": dict(zip(AXES, [2, 4, 5, 4, 5, 4, 5, 5]))},
        {"id": "approved-export-nightly", "family": "replace", "access": "parity", "hardlines": [],
         "undocumented": False, "tradeoff": "one more job to operate and monitor",
         "axes": dict(zip(AXES, [4, 4, 4, 3, 3, 2, 3, 3]))},
    ],
}


def mutated(patch):
    import copy
    plan = copy.deepcopy(CLEAN)
    patch(plan)
    return plan


FIXTURES = [
    ("clean", CLEAN, []),
    ("parity breach", mutated(lambda p: p["routes"][0].update(
        access="beyond", hardlines=["credentials"])), ["parity"]),
    ("route monoculture", mutated(lambda p: [r.update(family="reroute") for r in p["routes"]]),
     ["diversity"]),
    ("too few routes", mutated(lambda p: p.__setitem__("routes", p["routes"][:2])), ["diversity"]),
    ("unverified block", mutated(lambda p: p["block"].update(verified=False, evidence=["it failed"])),
     ["block"]),
    ("cosmetic retry loop", mutated(lambda p: p["attempts"].append(
        {"target": "sheet api", "mechanism": "GET /v4/sheets/123", "result": "403"})), ["repeat"]),
    ("goal names the blocked thing", mutated(lambda p: p.__setitem__(
        "goal", "get the shared spreadsheet access back so the dashboard works")), ["goal-drift"]),
    ("missing axes plus unflagged fragility", mutated(lambda p: (
        p["routes"][1]["axes"].pop("security"),
        p["routes"][2].update(undocumented=True, detection=""))), ["unscored", "fragile"]),
    ("all vetoed, nothing reduced", mutated(lambda p: [r.update(access="beyond") for r in p["routes"]]),
     ["parity", "no-reduce"]),
    ("consequential without a trade-off", mutated(lambda p: (
        p.__setitem__("class", "consequential"), p["routes"][0].__setitem__("tradeoff", ""))), ["tell"]),
]


def selftest() -> int:
    failures = 0
    for name, plan, expected in FIXTURES:
        findings, _ = audit(plan)
        joined = " | ".join(findings)
        caught = [e for e in expected if e in joined]
        if name == "clean":
            ok = not findings
            detail = "" if ok else "unexpected: " + joined
        else:
            ok = len(caught) == len(expected)
            detail = "" if ok else "missed: %s (got %s)" % (
                [e for e in expected if e not in caught], joined[:160] or "no findings")
        print("%-42s %s %s" % ("fixture %-36s" % name, "PASS" if ok else "FAIL", detail))
        failures += 0 if ok else 1
    print("self-test: %d/%d fixtures behaved" % (len(FIXTURES) - failures, len(FIXTURES)))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
