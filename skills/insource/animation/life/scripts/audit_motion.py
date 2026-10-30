#!/usr/bin/env python3
"""Flag mechanical animation violations in changed files (Animate review phase).

Usage:
    python audit_motion.py <file-or-dir> [<file-or-dir> ...]
        [--tier routine|rare|showcase] [--format text|json] [--fail-on error|warn|never]

Checks only what a script can check reliably: transition: all, layout-property animation,
ease-in, scale from zero, ungated hover motion, missing reduced-motion handling, parent-variable
drag, durations above the tier cap, large blur, legacy motion package, unmeasured dash arrays.
It never edits files. Judgment items (origin, personality, feel) stay with the reviewer.
Standard library only. Standards are numbered as in references/review-standards.md.
"""
import argparse
import json
import os
import re
import sys

EXTS = {".css", ".scss", ".sass", ".less", ".html", ".htm", ".js", ".jsx", ".ts", ".tsx",
        ".vue", ".svelte", ".mdx", ".astro"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".animate", "__pycache__",
             "coverage", ".turbo", ".cache", "vendor"}
TIER_CAP = {"routine": 300, "rare": 600, "showcase": 1600}
LAYOUT = (r"(?<![-\w])(?:width|height|top|left|right|bottom|"
          r"margin(?:-(?:top|right|bottom|left|inline|block))?|"
          r"padding(?:-(?:top|right|bottom|left|inline|block))?)(?![-\w])")

RULES = [
    # id, standard, severity, regex, message, remedy
    ("transition-all", 7, "error",
     re.compile(r"transition(?:-property)?\s*:\s*[^;{}]*(?<![-\w])all(?![-\w])|(?<![-\w])transition-all(?![-\w])"),
     "transition: all animates unintended properties and can leave the compositor",
     "Name the exact properties (for example transform, opacity)"),
    ("layout-transition", 7, "error",
     re.compile(r"transition(?:-property)?\s*:[^;{}]*" + LAYOUT),
     "Transition on a layout property forces layout every frame",
     "Animate transform (scale or translate) or clip-path instead; label a deliberate container tween"),
    ("ease-in", 3, "error",
     re.compile(r"(?<![-\w])ease-in(?![-\w])(?!-out)|[\"']easeIn[\"']|ease\s*:\s*[\"']?easeIn(?!Out)"),
     "ease-in delays the moment the user is watching and feels sluggish",
     "Use an ease-out curve (see tokens) or a spring"),
    ("scale-zero", 5, "error",
     re.compile(r"scale\(\s*0(?:\.0+)?\s*[,)]|(?<![-\w])scale\s*:\s*0(?:\.0+)?\s*[,;}\s\"']"),
     "Scaling from zero makes things appear from nothing",
     "Start from scale 0.95 to 0.97 together with opacity"),
    ("css-var-drag", 7, "warn",
     re.compile(r"style\.setProperty\(\s*[\"']--[\w-]*?(?:swipe|drag|offset|translate|pan)[\w-]*[\"']"),
     "A CSS variable on a parent recalculates every child on each update",
     "Set transform directly on the moving element"),
    ("legacy-motion-package", 10, "info",
     re.compile(r"from\s+[\"']framer-motion[\"']"),
     "Project imports the older motion package name",
     "Follow the project; flag migration to motion/react as a follow-up"),
    ("dasharray-literal", 10, "info",
     re.compile(r"stroke-?[dD]asharray\s*[:=]\s*[\"']?\d"),
     "Hard-coded dash array: path length may be wrong",
     "Measure with getTotalLength() and use that value"),
    ("will-change", 7, "info",
     re.compile(r"will-change\s*:"),
     "will-change left on permanently costs a layer",
     "Apply it only while animating and remove it after"),
    ("infinite-loop", 8, "info",
     re.compile(r"animation[^;{}]*(?<![-\w])infinite(?![-\w])"),
     "Looping animation: confirm it pauses off-screen and under reduced motion",
     "Pause with an intersection observer; stop under prefers-reduced-motion"),
]

KEYFRAME_LAYOUT = re.compile(r"(?:^|[{;])\s*" + LAYOUT + r"\s*:")
JS_LAYOUT = re.compile(r"\banimate\s*[=(]\s*\{\{?[^}]*?(?<![-\w])(?:width|height|top|left|marginLeft|marginTop|paddingLeft|paddingTop)\s*:")
BLUR = re.compile(r"blur\(\s*(\d+(?:\.\d+)?)px\s*\)")
TIME = re.compile(r"(\d+(?:\.\d+)?)(ms|s)\b")
JS_DURATION = re.compile(r"\bduration\s*:\s*(\d+(?:\.\d+)?)")
TW_DURATION = re.compile(r"(?<![-\w])duration-(\d+)(?![-\w])")
MOTION_SIGNS = re.compile(r"@keyframes|animation\s*:|transition\s*:[^;]*(?:transform|translate|scale|rotate)|"
                          r"(?<![-\w])animate-|from\s+[\"'](?:motion|framer-motion)|(?<![-\w])initial=\{|\bwithTiming\b|\bwithSpring\b")
REDUCED = re.compile(r"prefers-reduced-motion|useReducedMotion|reducedMotion|reduce-motion|motion-reduce|motion-safe|ReduceMotion")
SPATIAL = re.compile(r"transform|translate|scale|rotate|@keyframes|initial=\{|withSpring")
HOVER_MOTION = re.compile(r":hover[^{}]*\{[^{}]*(?:transform|translate|scale)", re.S)
HOVER_GATE = re.compile(r"hover\s*:\s*hover|any-hover|\(hover:")
TW_HOVER = re.compile(r"(?<![-\w])hover:(?:-?translate|scale|-?rotate)")


def first_durations(line):
    """Return durations in ms: first time value of each comma separated transition segment."""
    out = []
    if "delay" in line.lower() and not re.search(r"(?:transition|animation)\s*:", line):
        return out
    m = re.search(r"(?:transition|animation)(?:-duration)?\s*:\s*([^;{}]*)", line)
    if m:
        for seg in m.group(1).split(","):
            t = TIME.search(seg)
            if t:
                v = float(t.group(1))
                out.append(v if t.group(2) == "ms" else v * 1000)
        return out
    j = JS_DURATION.search(line)
    if j:
        v = float(j.group(1))
        out.append(v * 1000 if v <= 10 else v)
    for t in TW_DURATION.finditer(line):
        out.append(float(t.group(1)))
    return out


def snippet(line):
    s = line.strip()
    return s if len(s) <= 120 else s[:117] + "..."


def audit_file(path, cap, tier):
    try:
        if os.path.getsize(path) > 1_000_000:
            return []
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return []
    findings = []
    lines = text.splitlines()

    def add(i, rule, std, sev, msg, remedy):
        findings.append({"file": path, "line": i, "rule": rule, "standard": std, "severity": sev,
                         "message": msg, "remedy": remedy, "snippet": snippet(lines[i - 1]) if 0 < i <= len(lines) else ""})

    in_kf, depth = False, 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("//", "/*", "*", "<!--")):
            continue
        if "@keyframes" in line:
            in_kf, depth = True, 0
        if in_kf:
            depth += line.count("{") - line.count("}")
            if KEYFRAME_LAYOUT.search(line):
                add(i, "layout-keyframes", 7, "error", "Keyframes animate a layout property",
                    "Animate transform or clip-path instead")
            if depth <= 0 and "}" in line and "@keyframes" not in line:
                in_kf = False
        for rid, std, sev, rx, msg, remedy in RULES:
            if rx.search(line):
                add(i, rid, std, sev, msg, remedy)
        if JS_LAYOUT.search(line):
            add(i, "layout-js-animation", 7, "warn", "Script animation targets a layout property",
                "Animate transform; use a layout animation helper for size or position changes")
        for m in BLUR.finditer(line):
            if float(m.group(1)) > 20:
                add(i, "blur-large", 7, "warn", f"blur({m.group(1)}px) exceeds the 20px cap and is expensive",
                    "Keep blur at 2 to 4px for bridges, up to 8px for rare entrances")
        for d in ([] if re.search(r"(?<![-\w])infinite(?![-\w])", line) else first_durations(line)):
            if d > cap:
                add(i, "duration-over-tier", 4, "warn", f"{d:g}ms exceeds the {tier} cap of {cap}ms",
                    "Shorten, or justify a rare or showcase tier in the report")
                break

    # file-level checks
    if MOTION_SIGNS.search(text) and SPATIAL.search(text) and not REDUCED.search(text):
        add(1, "no-reduced-motion", 8, "warn",
            "Spatial animation here and no reduced-motion handling in this file (it may be handled globally)",
            "Add a prefers-reduced-motion variant that keeps opacity and drops movement")
    m = HOVER_MOTION.search(text)
    if m and not HOVER_GATE.search(text):
        line_no = text[:m.start()].count("\n") + 1
        add(line_no, "hover-ungated", 8, "warn", "Hover motion is not gated to hover-capable devices",
            "Wrap in @media (hover: hover) and (pointer: fine)")
    elif TW_HOVER.search(text):
        mm = TW_HOVER.search(text)
        add(text[:mm.start()].count("\n") + 1, "hover-utility", 8, "info",
            "Hover motion utility: confirm the framework gates hover for touch devices",
            "Inspect the generated CSS; add a hover media query if it is not gated")
    return findings


def collect(paths):
    files = []
    for p in paths:
        if os.path.isfile(p):
            files.append(p)
            continue
        for root, dirs, names in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for n in names:
                if os.path.splitext(n)[1].lower() in EXTS and not n.endswith(".d.ts"):
                    files.append(os.path.join(root, n))
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--tier", choices=sorted(TIER_CAP), default="routine")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--fail-on", choices=["error", "warn", "never"], default="error")
    args = ap.parse_args()
    files = collect(args.paths)
    findings = []
    for f in files:
        findings.extend(audit_file(f, TIER_CAP[args.tier], args.tier))
    counts = {"error": 0, "warn": 0, "info": 0}
    for f in findings:
        counts[f["severity"]] += 1
    if args.format == "json":
        print(json.dumps({"files_scanned": len(files), "tier": args.tier, "summary": counts,
                          "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f'{f["severity"].upper():5} {f["file"]}:{f["line"]} [{f["rule"]}, standard {f["standard"]}] {f["message"]}')
            print(f'      fix: {f["remedy"]}')
            if f["snippet"]:
                print(f'      > {f["snippet"]}')
        print(f'{len(files)} file(s) scanned: {counts["error"]} error(s), {counts["warn"]} warning(s), {counts["info"]} note(s)')
    if args.fail_on == "error" and counts["error"]:
        sys.exit(1)
    if args.fail_on == "warn" and (counts["error"] or counts["warn"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
