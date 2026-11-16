#!/usr/bin/env python3
"""conflict_blocks.py - capture and reassemble conflict-marked regions.

Parses conflict markers deterministically (variable-width, nesting-aware: a
criss-cross merge with multiple merge bases embeds a conflicted virtual
base INSIDE the file as nested markers of larger width), so an agent can
extract exact candidate blocks and rebuild a resolved file without
hand-editing marker lines.

Commands:
  list FILE [--json]
      Show the region tree: id, line span, marker width, candidates.
  extract FILE --region ID [--candidate ours|base|theirs|all] [--out PATH|DIR]
      Write candidate block(s) verbatim (stdout with --out - or omitted).
      Nested regions stay inside their parent's block exactly as written.
  assemble FILE [--set ID=ROLE] [--set ID=@PATH]... --out PATH
      Replace each region with its chosen candidate (ROLE) or file content
      (@PATH). Selecting a parent takes its block verbatim - nested markers
      survive, so resolve nested ids separately or list them in the same
      run (children are substituted inside parents automatically). Fails
      (exit 1) if any markers remain unless --allow-unresolved.

Line endings are preserved (files are read/written with their own newlines).
Works on worktree files and stage dumps (`git show :2:f > ours.blob`)
alike; a file with no conflicts is valid input (empty tree / identity).

Exit codes: 0 ok, 1 markers left or bad state, 2 usage/parse error.
On Windows run with `python`. stdout is ASCII.
"""

import argparse
import json
import os
import re
import sys

MARKER_RE = re.compile(r"^(<{7,}|={7,}|\|{7,}|>{7,})(?:[ \t].*)?\r?\n?$")


def classify(line):
    """Return (kind, width) for a marker line, else (None, None).
    kind: 'start' '<', 'base' '|', 'sep' '=', 'end' '>'."""
    m = MARKER_RE.match(line)
    if not m:
        return None, None
    token = m.group(1)
    return {"<": "start", "|": "base", "=": "sep", ">": "end"}[token[0]], len(token)


def read_lines(path):
    with open(path, "r", encoding="utf-8", errors="surrogateescape",
              newline="") as fh:
        return fh.read().splitlines(keepends=True)


def write_lines(path, lines):
    with open(path, "w", encoding="utf-8", errors="surrogateescape",
              newline="") as fh:
        fh.write("".join(lines))


def die(msg, code=2):
    print(f"ERROR {msg}", file=sys.stderr)
    sys.exit(code)


def _parse_region(lines, start_idx, width):
    """Parse one region starting at lines[start_idx] (a '<' of `width`).
    Segment content is VERBATIM (nested child blocks included). Returns
    (region, next_idx). Region keeps raw lines for recursive splicing."""
    region = {
        "start": start_idx + 1, "end": None, "width": width,
        "style": "merge", "id": None, "children": [],
        "segments": {"ours": [], "base": [], "theirs": []},
    }
    current = "ours"
    i = start_idx + 1
    while i < len(lines):
        kind, w = classify(lines[i])
        if kind == "end" and w == width:
            region["end"] = i + 1
            region["raw"] = lines[start_idx:i + 1]
            return region, i + 1
        if kind is None:
            region["segments"][current].append(lines[i])
            i += 1
            continue
        if (kind == "base" or kind == "sep") and w == width:
            current = "base" if kind == "base" else "theirs"
            if kind == "base":
                region["style"] = "diff3"
            i += 1
            continue
        if kind == "start" and w != width:
            child, i = _parse_region(lines, i, w)
            region["children"].append(child)
            continue
        # same-width marker seen where a content line is expected: an inner
        # marker of equal width (pathological, e.g. same-size markers from
        # conflict-marker-size=7 rerere trap) - keep verbatim as content.
        region["segments"][current].append(lines[i])
        i += 1
    die(f"unterminated conflict region starting at line {region['start']}")


def parse_file(path):
    lines = read_lines(path)
    regions, i = [], 0
    while i < len(lines):
        kind, w = classify(lines[i])
        if kind == "start":
            region, i = _parse_region(lines, i, w)
            regions.append(region)
        else:
            i += 1
    for idx, r in enumerate(regions, 1):
        _assign(r, str(idx))
    return regions


def _assign(region, prefix):
    region["id"] = prefix
    for k, child in enumerate(region["children"], 1):
        _assign(child, f"{prefix}.{k}")


def flatten(regions):
    out = []
    def walk(r):
        out.append(r)
        for c in r["children"]:
            walk(c)
    for r in regions:
        walk(r)
    return out


def by_id(regions):
    return {r["id"]: r for r in flatten(regions)}


def _simplify(r):
    segs = {"ours": len(r["segments"]["ours"]), "theirs": len(r["segments"]["theirs"])}
    if r["style"] == "diff3":
        segs["base"] = len(r["segments"]["base"])
    else:
        # ours/theirs counts exclude child spans; recompute spans for json
        pass
    return {"id": r["id"], "start": r["start"], "end": r["end"],
            "width": r["width"], "style": r["style"],
            "children": [c["id"] for c in r["children"]],
            "segments_lines": segs}


def cmd_list(args):
    regions = parse_file(args.file)
    if args.json:
        print(json.dumps([_simplify(r) for r in flatten(regions)],
                         ensure_ascii=False, indent=2))
        return 0
    flat = flatten(regions)
    if not flat:
        print(f"{args.file}: no conflict regions")
        return 0
    def render(r, depth):
        kids = sum(len(c["children"]) for c in [r])
        marks = sum(1 for role in ("ours", "theirs")
                    for ln in r["segments"][role] if classify(ln)[0] == "start")
        segtxt = "ours/base/theirs" if r["style"] == "diff3" else "ours/theirs"
        print("  " * depth +
              f"region {r['id']}: lines {r['start']}-{r['end']}, "
              f"marker width {r['width']}, style {r['style']} "
              f"[{segtxt}]"
              + (f", {len(r['children'])} nested child region(s)" if r["children"] else ""))
        for c in r["children"]:
            render(c, depth + 1)
    for r in regions:
        render(r, 0)
    return 0


def cmd_extract(args):
    regions = parse_file(args.file)
    allr = by_id(regions)
    if not allr:
        print(f"{args.file}: no conflict regions")
        return 0
    if args.region not in allr:
        die(f"unknown region '{args.region}' (known: {', '.join(sorted(allr, key=_idkey))})")
    r = allr[args.region]
    roles = ["ours", "base", "theirs"] if args.candidate == "all" else [args.candidate]
    if r["style"] != "diff3" and "base" in roles:
        die(f"region {args.region} has no base segment (style {r['style']})")
    if len(roles) == 1:
        content = _block(r, roles[0])
        if args.out in (None, "-"):
            sys.stdout.write("".join(content))
        else:
            write_lines(args.out, content)
            print(f"wrote {args.out} ({len(content)} lines)")
        return 0
    if not args.out:
        die("--candidate all requires --out DIR")
    os.makedirs(args.out, exist_ok=True)
    for role in roles:
        if role == "base" and r["style"] != "diff3":
            continue
        path = os.path.join(args.out, f"region-{args.region}-{role}.txt")
        write_lines(path, _block(r, role))
        print(f"wrote {path}")
    return 0


def _block(region, role):
    """Verbatim lines of a candidate segment, nested child blocks included."""
    return _segment_window(region, role)


def _segment_window(region, role):
    """Compute the original raw-line window for a segment role, verbatim
    with nested child blocks included."""
    raw = region["raw"]
    bounds = []  # (marker_kind, line_index)
    for idx, line in enumerate(raw):
        kind, w = classify(line)
        if kind is not None and w == region["width"]:
            bounds.append((kind, idx))
    # expected order: start, [base], sep, end
    windows = {}
    ours_s = bounds[0][1] + 1
    if region["style"] == "diff3":
        base_i = next(i for i, (k, _) in enumerate(bounds) if k == "base")
        sep_i = next(i for i, (k, _) in enumerate(bounds) if k == "sep")
        windows["ours"] = (ours_s, bounds[base_i][1])
        windows["base"] = (bounds[base_i][1] + 1, bounds[sep_i][1])
        windows["theirs"] = (bounds[sep_i][1] + 1, bounds[-1][1])
    else:
        sep_i = next(i for i, (k, _) in enumerate(bounds) if k == "sep")
        windows["ours"] = (ours_s, bounds[sep_i][1])
        windows["theirs"] = (bounds[sep_i][1] + 1, bounds[-1][1])
    s, e = windows[role]
    return raw[s:e]


def cmd_assemble(args):
    regions = parse_file(args.file)
    allr = by_id(regions)
    sel = {}
    for pair in args.set or []:
        rid, _, val = pair.partition("=")
        if rid not in allr:
            die(f"unknown region '{rid}' (known: {', '.join(sorted(allr, key=_idkey))})")
        if val.startswith("@"):
            sel[rid] = read_lines(val[1:])
        elif val in ("ours", "base", "theirs"):
            r = allr[rid]
            if val == "base" and r["style"] != "diff3":
                die(f"region {rid} has no base segment (style {r['style']})")
            sel[rid] = _segment_window(r, val)
        else:
            die(f"bad selection '{val}' for region {rid}")

    def render(r):
        """Return resolved lines for region r's whole span."""
        if r["id"] in sel:
            return sel[r["id"]]
        lines = r["raw"][:]
        for c in sorted(r["children"], key=lambda c: c["start"], reverse=True):
            cr = render(c)
            if cr is not c["raw"]:
                s = c["start"] - r["start"]
                e = c["end"] - r["start"]
                lines[s:e] = cr
        return lines

    out = read_lines(args.file)
    # apply top-level spans descending so offsets stay valid
    for r in sorted(regions, key=lambda r: r["start"], reverse=True):
        rendered = render(r)
        if rendered is not r["raw"]:
            out[r["start"] - 1:r["end"]] = rendered
    write_lines(args.out, out)
    left = sum(1 for ln in out if classify(ln)[0] == "start")
    if left and not args.allow_unresolved:
        print(f"ERROR {left} conflict region(s) remain unresolved in {args.out} "
              f"(pass --allow-unresolved to keep them)", file=sys.stderr)
        return 1
    print(f"wrote {args.out}: {len(sel)} selection(s), {left} region(s) still marked")
    return 0


def _idkey(s):
    return [int(x) for x in s.split(".")]


def main(argv):
    p = argparse.ArgumentParser(prog="conflict_blocks.py",
                                description="capture/assemble conflict blocks")
    sub = p.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list")
    pl.add_argument("file")
    pl.add_argument("--json", action="store_true")
    pe = sub.add_parser("extract")
    pe.add_argument("file")
    pe.add_argument("--region", required=True)
    pe.add_argument("--candidate", default="ours",
                    choices=["ours", "base", "theirs", "all"])
    pe.add_argument("--out")
    pa = sub.add_parser("assemble")
    pa.add_argument("file")
    pa.add_argument("--set", action="append", metavar="ID=ROLE|@PATH")
    pa.add_argument("--out", required=True)
    pa.add_argument("--allow-unresolved", action="store_true")
    args = p.parse_args(argv)
    return {"list": cmd_list, "extract": cmd_extract, "assemble": cmd_assemble}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
