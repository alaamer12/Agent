#!/usr/bin/env python3
"""List animation seams (leads for discovery) and existing animation in a project.

Usage:
    python find_candidates.py <dir-or-file> [--max 15] [--format text|json]

Candidates are leads, not findings: every one must still pass the gate.
Read-only. Standard library only.
"""
import argparse
import json
import os
import re
import sys

EXTS = {".css", ".scss", ".html", ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".animate", "__pycache__", "coverage", ".turbo", ".cache"}
SKIP_FILE = re.compile(r"(\.test\.|\.spec\.|\.stories\.|\.d\.ts$|__tests__)")

PRESSABLE = re.compile(r"\bonClick\s*=|\bonPress\s*=|@click\b|v-on:click|\bon:click\b")
FEEDBACK = re.compile(r":active|active:|whileTap|onPressIn|hover:|:hover|transition|animate")
COND_RENDER = re.compile(r"&&\s*\(?\s*<[A-Za-z]|&&\s*\(\s*$|\bv-if=|\*ngIf|\{#if\b|\?\s*\(?\s*<[A-Za-z]")
PRESENCE = re.compile(r"AnimatePresence|transition|animate|@starting-style|<Transition")
OVERLAY_NAME = re.compile(r"popover|dropdown|menu|tooltip|dialog|modal|drawer|sheet|toast|combobox|select", re.I)
ORIGIN = re.compile(r"transform-origin|origin-|transformOrigin|originX|originY")
RARE_NAME = re.compile(r"hero|landing|onboarding|welcome|empty|features|pricing|gallery|testimonial|showcase", re.I)
DELIGHT_NAME = re.compile(r"success|empty|onboarding|welcome|complete|congrat|celebrat|confirmation|thank|done", re.I)
GESTURE = re.compile(r"onDrag|onPointerDown|onPointerMove|onTouchStart|onTouchMove|\bdrag=|useDrag|Gesture\.Pan|draggable|swipe", re.I)
PHYSICS = re.compile(r"spring|velocity|withSpring|dragElastic|momentum|inertia", re.I)
LINK_STATE = re.compile(r"setHovered|setSelected|hoveredId|selectedId|highlightId|setHighlight|onMouseEnter|onMouseOver|onHover|activeId", re.I)
MAP_CALL = re.compile(r"\.map\s*\(")
MOTION_EL = re.compile(r"<motion\.|\banimate=\{|v-motion|\bx-transition")
STAGGER = re.compile(r"stagger|delay|transition-delay|animation-delay|delayChildren")
STEPS_NAME = re.compile(r"wizard|stepper|step|tabs|carousel|pager|onboarding|slider|navigation|router", re.I)
FORWARD = re.compile(r"\b(next|forward)\w*", re.I)
BACKWARD = re.compile(r"\b(back|prev|previous)\w*", re.I)
DIRECTION = re.compile(r"direction|custom=|data-dir|\bdir\b\s*[=:]|isForward|isBack|slideDirection", re.I)
EXISTING = re.compile(r"@keyframes|animation\s*:|transition\s*:|(?<![-\w])animate-|<motion\.|\buseSpring\b|\bwithTiming\b|\bwithSpring\b|\banimate\(|\.animate\(|startViewTransition|gsap\.")
LIBS = ["motion", "framer-motion", "gsap", "react-spring", "@react-spring/web", "react-native-reanimated",
        "animejs", "lottie-react", "lottie-web", "tailwindcss-animate", "auto-animate", "@formkit/auto-animate",
        "react-native-gesture-handler"]


def collect(root):
    if os.path.isfile(root):
        return [root]
    out = []
    for r, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if os.path.splitext(n)[1].lower() in EXTS and not SKIP_FILE.search(n):
                out.append(os.path.join(r, n))
    return sorted(out)


def detect_stack(root):
    base = root if os.path.isdir(root) else os.path.dirname(root) or "."
    found = {}
    cur = os.path.abspath(base)
    for _ in range(4):
        pj = os.path.join(cur, "package.json")
        if os.path.isfile(pj):
            try:
                with open(pj, encoding="utf-8") as fh:
                    data = json.load(fh)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                for lib in LIBS:
                    if lib in deps:
                        found[lib] = deps[lib]
                for fw in ("react", "next", "vue", "svelte", "react-native", "tailwindcss", "astro"):
                    if fw in deps:
                        found[fw] = deps[fw]
            except (OSError, json.JSONDecodeError):
                pass
            break
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--max", type=int, default=15, help="max candidates shown per seam")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    args = ap.parse_args()

    seams = {k: [] for k in ("feedback_gap", "teleporting_state", "missing_spatial_story", "group_entrance",
                              "gesture_seam", "flat_delight_moment", "unlinked_relatives",
                              "unordered_group", "missing_reverse")}
    existing = []
    reduced_global = False
    files = collect(args.target)
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        lines = text.splitlines()
        name = os.path.basename(path)
        if re.search(r"prefers-reduced-motion|useReducedMotion|reducedMotion", text):
            reduced_global = True

        def lead(seam, i, why):
            seams[seam].append({"file": path, "line": i, "why": why,
                                "snippet": (lines[i - 1].strip()[:110] if 0 < i <= len(lines) else "")})

        ex = len(EXISTING.findall(text))
        if ex:
            existing.append({"file": path, "count": ex})
        has_feedback = bool(FEEDBACK.search(text))
        has_presence = bool(PRESENCE.search(text))
        for i, line in enumerate(lines, 1):
            if PRESSABLE.search(line) and not has_feedback:
                lead("feedback_gap", i, "pressable element in a file with no press, hover or transition styling")
            if COND_RENDER.search(line) and not has_presence:
                lead("teleporting_state", i, "conditional content with no enter, exit or transition in this file")
            if MAP_CALL.search(line) and RARE_NAME.search(name) and not STAGGER.search(text):
                lead("group_entrance", i, "list on a rarely seen surface renders all at once")
            if GESTURE.search(line) and not PHYSICS.search(text):
                lead("gesture_seam", i, "gesture handling with no spring, velocity or boundary friction")
        if OVERLAY_NAME.search(name) and not ORIGIN.search(text):
            lead("missing_spatial_story", 1, "overlay-type component with no transform origin set")
        if DELIGHT_NAME.search(name):
            lead("flat_delight_moment", 1, "rare, high-emotion surface by name; check how it arrives")
        if LINK_STATE.search(text) and MAP_CALL.search(text):
            m = LINK_STATE.search(text)
            lead("unlinked_relatives", text[:m.start()].count("\n") + 1,
                 "hover or selection state alongside a rendered group: related items may need a linked reaction")
        motion_els = len(MOTION_EL.findall(text))
        if motion_els >= 3 and not STAGGER.search(text):
            m = MOTION_EL.search(text)
            lead("unordered_group", text[:m.start()].count("\n") + 1,
                 f"{motion_els} animated elements with no designed order (consider domino or instant sync)")
        if STEPS_NAME.search(name) and FORWARD.search(text) and BACKWARD.search(text) and not DIRECTION.search(text):
            lead("missing_reverse", 1, "forward and back both exist but no direction handling: reverse motion likely not designed")

    existing.sort(key=lambda e: -e["count"])
    result = {
        "target": args.target,
        "files_scanned": len(files),
        "stack": detect_stack(args.target),
        "reduced_motion_handling_found": reduced_global,
        "existing_animation": existing[:20],
        "seams": {k: {"total": len(v), "shown": v[:args.max]} for k, v in seams.items()},
        "note": "Leads only. Gate every candidate before suggesting it.",
    }
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return
    print(f'Scanned {len(files)} file(s) under {args.target}')
    print(f'Stack: {", ".join(f"{k} {v}" for k, v in result["stack"].items()) or "not detected"}')
    print(f'Reduced-motion handling in code: {"yes" if reduced_global else "NOT FOUND"}')
    print("\nExisting animation (files, by amount):")
    for e in result["existing_animation"][:10] or [{"file": "none found", "count": 0}]:
        print(f'  {e["file"]}  ({e["count"]})')
    for k, v in result["seams"].items():
        print(f'\n[{k}] {v["total"]} lead(s)')
        for c in v["shown"]:
            print(f'  {c["file"]}:{c["line"]}  {c["why"]}')
            if c["snippet"]:
                print(f'      > {c["snippet"]}')
    print("\n" + result["note"])


if __name__ == "__main__":
    main()
