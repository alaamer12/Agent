#!/usr/bin/env python3
"""Validate an Inquire content JSON before the user sees it.

usage: check_questions.py content.json [--mode verbose|concise]
Exit code 1 when there are errors. Warnings never fail the check.
"""
import argparse, json, re, sys

KINDS = {"h", "ascii", "code", "table", "list", "steps", "chart", "src"}
TONES = {"good", "bad", "info", "neutral"}
errs, warns = [], []
E = lambda m: errs.append(m)
W = lambda m: warns.append(m)


def words(x):
    if isinstance(x, str): return len(x.split())
    if isinstance(x, list): return sum(words(i) for i in x)
    if isinstance(x, dict): return sum(words(v) for v in x.values())
    return 0


def check_block(b, where):
    if isinstance(b, str):
        return
    if not isinstance(b, dict) or b.get("k") not in KINDS:
        return E(f"{where}: block must be a string or an object with k in {sorted(KINDS)}")
    k = b["k"]
    need = {"h": ["t"], "ascii": ["t"], "code": ["t"], "table": ["h", "r"], "list": ["i"],
            "steps": ["i"], "chart": ["b", "max"], "src": ["i"]}[k]
    for n in need:
        if n not in b: E(f"{where}: {k} block is missing '{n}'")
    if k == "table" and "h" in b and "r" in b:
        for i, r in enumerate(b["r"]):
            if len(r) != len(b["h"]): E(f"{where}: table row {i+1} has {len(r)} cells, header has {len(b['h'])}")
    if k == "steps":
        for s in b.get("i", []):
            if not (isinstance(s, list) and len(s) == 2): E(f"{where}: each step must be [title, detail]")
    if k == "chart" and b.get("b") and b.get("max"):
        for r in b["b"]:
            if r[1] > b["max"]: W(f"{where}: chart value {r[1]} exceeds max {b['max']} (bar is clipped)")
    if k == "ascii":
        t = b.get("t", "")
        lines = t.split("\n") if isinstance(t, str) else t
        if max((len(l) for l in lines), default=0) > 96: W(f"{where}: ascii diagram is wider than 96 columns; it will scroll sideways")
        if len(lines) < 2: W(f"{where}: ascii diagram has a single line; a sentence may say it better")
    if k == "code" and not b.get("l"): W(f"{where}: code block has no language 'l' (no highlighting)")


def check_blocks(x, where):
    for i, b in enumerate(x if isinstance(x, list) else [x]):
        check_block(b, f"{where}[{i}]")


def refs(c):
    if not c: return []
    if "all" in c or "any" in c: return [r for s in (c.get("all") or c.get("any")) for r in refs(s)]
    if "not" in c: return refs(c["not"])
    return [c]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content")
    ap.add_argument("--mode", choices=["verbose", "concise"], default=None)
    a = ap.parse_args()
    try:
        d = json.load(open(a.content, encoding="utf-8"))
    except Exception as ex:
        print("ERROR: not valid JSON:", ex); sys.exit(1)
    mode = a.mode or d.get("mode") or "verbose"

    for k in ("title", "date", "context", "tldr", "qs"):
        if not d.get(k): E(f"missing or empty '{k}'")
    if errs: return report()
    check_blocks(d["context"], "context")
    cw = words(d["context"])
    if mode == "verbose" and cw < 220: W(f"verbose context has {cw} words; it should cover the whole conversation (background, environment, constraints, decisions, assumptions)")
    if mode == "concise" and cw > 320: W(f"concise context has {cw} words; trim it")
    if len(d["context"]) < 3 and mode == "verbose": W("verbose context should use several blocks (headings, table, diagram, list)")
    if not 1 <= len(d["tldr"]) <= 5: W("TL;DR should have 1 to 5 bullets")
    if len(d["qs"]) > 12: W(f"{len(d['qs'])} questions is a lot; remove the ones that do not change a decision")

    ids, idx = [], {}
    for qi, q in enumerate(d["qs"]):
        w = f"question '{q.get('id', qi)}'"
        for k in ("id", "q", "type", "about", "opts"):
            if not q.get(k): E(f"{w}: missing '{k}'")
        if not q.get("id"): continue
        if q["id"] in ids: E(f"{w}: duplicate id")
        if not re.fullmatch(r"[A-Za-z][\w-]*", q["id"]): E(f"{w}: id must be letters, digits, _ or -")
        if q.get("type") not in ("single", "multi"): E(f"{w}: type must be 'single' or 'multi'")
        if mode == "verbose" and not q.get("why"): W(f"{w}: verbose mode needs 'why' (why the agent is asking)")
        if len(q.get("opts", [])) < 2: E(f"{w}: needs at least 2 options")
        if q.get("vis") is not None: check_blocks(q["vis"], w + ".vis")
        base = [o for o in q.get("opts", []) if not o.get("when")]
        if not base: E(f"{w}: needs at least one option that is always visible")
        for oi, o in enumerate(q.get("opts", [])):
            ow = f"{w} option {oi}"
            if not o.get("t"): E(f"{ow}: missing title 't'")
            shape = o.get("facets") or (o.get("pros") or o.get("cons"))
            if not (o.get("d") or shape or o.get("vis")): E(f"{ow}: needs a description, facets/pros/cons or vis")
            if mode == "verbose":
                if not o.get("d"): W(f"{ow}: verbose mode needs a description 'd'")
                if not shape: W(f"{ow}: verbose mode needs pros/cons or facets (trade-offs, 'choose it when', ...)")
            for f in o.get("facets") or []:
                if not (f.get("h") and f.get("i")): E(f"{ow}: each facet needs 'h' and a non-empty 'i'")
                if f.get("tone") and f["tone"] not in TONES: E(f"{ow}: facet tone must be one of {sorted(TONES)}")
            if o.get("vis") is not None: check_blocks(o["vis"], ow + ".vis")
            for r in refs(o.get("when")):
                if r.get("q") != q["id"] and r.get("q") not in ids: E(f"{ow}: 'when' refers to unknown or later question '{r.get('q')}'")
        ids.append(q["id"]); idx[q["id"]] = q

    # branching rules
    parent = {}
    for qi, q in enumerate(d["qs"]):
        for r in refs(q.get("when")):
            p = r.get("q")
            if p not in idx or p == q["id"] or ids.index(p) >= qi:
                E(f"question '{q['id']}': 'when' must refer to an EARLIER question (got '{p}')"); continue
            pq = idx[p]
            if "custom" not in r:
                for i in r.get("is", []):
                    if not isinstance(i, int) or i >= len(pq["opts"]): E(f"question '{q['id']}': 'when' uses option index {i}, but '{p}' has {len(pq['opts'])} options")
            parent.setdefault(q["id"], p)
    for qi, q in enumerate(d["qs"]):
        p = parent.get(q["id"])
        if not p: continue
        # follow-ups must sit right after their parent (or after a sibling/descendant of it)
        def under(x, anc):
            while x:
                if x == anc: return True
                x = parent.get(x)
            return False
        j = qi - 1
        while j >= 0 and under(d["qs"][j]["id"], p) and d["qs"][j]["id"] != p: j -= 1
        if d["qs"][j]["id"] != p:
            W(f"question '{q['id']}': place it right after its parent '{p}' so the dashed connector stays clean")
    depth = lambda x: 0 if x not in parent else 1 + depth(parent[x])
    for q in d["qs"]:
        if depth(q["id"]) > 3: W(f"question '{q['id']}': nesting deeper than 3 levels is hard to follow")
    if not any(q.get("when") is None for q in d["qs"]): E("every question has a 'when'; at least one must always be visible")
    report()


def report():
    for m in warns: print("WARN :", m)
    for m in errs: print("ERROR:", m)
    print(f"{len(errs)} error(s), {len(warns)} warning(s)")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
