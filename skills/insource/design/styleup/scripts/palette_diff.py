#!/usr/bin/env python3
"""Before/after parity diff for styling migrations.

Capture contract (any stack, any capture tool):
    <baseline>/<state>/<file>      e.g. baseline/home-light/shot.png
    <current>/<state>/<file>       e.g. current/home-light/shot.png

Install into the project you are styling up, or run it from this skill's folder.

Modes
  compare (default)   exact per-pixel diff after masks; exit 1 on any unmasked difference,
                      a size mismatch, or a missing state.
  --propose-masks     diff two captures of the SAME build and write a mask JSON covering the
                      regions that changed between runs (dynamic pixels only). Never mask a
                      region that did not move between two runs of one build.

Mask JSON
  {"global": [[x, y, w, h], ...], "states": {"home-light": [[x, y, w, h], ...]}}

Requires Pillow (install it in a local virtualenv; do not install it globally).

Usage
  python palette_diff.py --baseline before --current after
  python palette_diff.py --baseline run-a --current run-b --propose-masks masks.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import deque

from PIL import Image, ImageChops, ImageDraw

DEFAULT_FILE = "shot.png"
TILE = 16


def max_channel_diff(a: Image.Image, b: Image.Image) -> Image.Image:
    """Per-pixel maximum absolute channel difference, as an L-mode image."""
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    r, g, bl = diff.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), bl)


def load_mask(path: str | None) -> dict:
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def rectangles(mask: dict, state: str) -> list[list[int]]:
    return list(mask.get("global") or []) + list((mask.get("states") or {}).get(state) or [])


def apply_mask(diff: Image.Image, rects: list[list[int]]) -> Image.Image:
    if not rects:
        return diff
    masked = diff.copy()
    draw = ImageDraw.Draw(masked)
    for x, y, w, h in rects:
        draw.rectangle([int(x), int(y), int(x) + int(w), int(y) + int(h)], fill=0)
    return masked


def count_nonzero(img: Image.Image) -> int:
    return sum(img.histogram()[1:])


def compare_state(base: Image.Image, cur: Image.Image, tolerance: int,
                  rects: list[list[int]]) -> dict:
    if base.size != cur.size:
        return {"ok": False, "size_mismatch": [list(base.size), list(cur.size)]}
    if tolerance:
        diff = max_channel_diff(base, cur).point(lambda v: 255 if v > tolerance else 0)
    else:
        diff = max_channel_diff(base, cur)
    masked = apply_mask(diff, rects)
    differing = count_nonzero(masked)
    info = {
        "ok": differing == 0,
        "differing_pixels": differing,
        "total_pixels": masked.width * masked.height,
        "percent": round(100.0 * differing / (masked.width * masked.height), 4),
        "bbox": list(masked.getbbox()) if differing else None,
        "masked_rects": rects,
    }
    return info, masked


def connected_tile_rects(diff: Image.Image) -> list[list[int]]:
    """Merge differing tiles into bounding rectangles (4-connected components)."""
    cols = (diff.width + TILE - 1) // TILE
    rows = (diff.height + TILE - 1) // TILE
    hot = set()
    for row in range(rows):
        for col in range(cols):
            box = (col * TILE, row * TILE,
                   min((col + 1) * TILE, diff.width), min((row + 1) * TILE, diff.height))
            if diff.crop(box).getbbox() is not None:
                hot.add((col, row))
    rects = []
    while hot:
        start = hot.pop()
        queue = deque([start])
        cells = [start]
        while queue:
            col, row = queue.popleft()
            for neighbor in ((col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1)):
                if neighbor in hot:
                    hot.remove(neighbor)
                    queue.append(neighbor)
                    cells.append(neighbor)
        x0 = min(c for c, _ in cells) * TILE
        y0 = min(r for _, r in cells) * TILE
        x1 = min((max(c for c, _ in cells) + 1) * TILE, diff.width)
        y1 = min((max(r for _, r in cells) + 1) * TILE, diff.height)
        rects.append([x0, y0, x1 - x0, y1 - y0])
    return sorted(rects, key=lambda rect: (rect[1], rect[0]))


def state_names(root: str, file_name: str) -> list[str]:
    return sorted(
        entry for entry in os.listdir(root)
        if os.path.isfile(os.path.join(root, entry, file_name))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Exact before/after parity diff for styleup.")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--current", required=True)
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"image name per state (default {DEFAULT_FILE})")
    parser.add_argument("--mask", default=None, help="mask JSON (default <baseline>/masks.json)")
    parser.add_argument("--tolerance", type=int, default=0, help="allowed max channel delta per pixel")
    parser.add_argument("--report", default=None, help="write a markdown report here")
    parser.add_argument("--no-heatmaps", action="store_true")
    parser.add_argument("--intersect", action="store_true", help="compare only states present in both")
    parser.add_argument("--propose-masks", default=None, metavar="OUT.json",
                        help="write masks for regions that changed between two same-build runs")
    args = parser.parse_args()

    if args.propose_masks:
        states = [s for s in state_names(args.baseline, args.file)
                  if os.path.exists(os.path.join(args.current, s, args.file))]
        proposals, all_rects = [], False
        for state in states:
            base = Image.open(os.path.join(args.baseline, state, args.file))
            cur = Image.open(os.path.join(args.current, state, args.file))
            if base.size != cur.size:
                print(f"  SIZE  {state}: {base.size} vs {cur.size}")
                continue
            rects = connected_tile_rects(max_channel_diff(base, cur))
            if rects:
                proposals.append((state, rects))
                all_rects = True
                print(f"  MOVE  {state}: {rects}")
        payload = {
            "_comment": ("Regions that differed between two captures of the same build. Each is a "
                         "dynamic pixel source (clock, animation, focus visual, OS chrome); verify "
                         "the cause before keeping it."),
            "states": {state: rects for state, rects in proposals},
        }
        with open(args.propose_masks, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"{'proposed' if all_rects else 'no dynamic regions found; wrote empty'} masks -> {args.propose_masks}")
        return 0

    mask_path = args.mask
    if not mask_path:
        local_mask = os.path.join(args.baseline, "masks.json")
        mask_path = local_mask if os.path.exists(local_mask) else None
    mask = load_mask(mask_path)

    states = state_names(args.baseline, args.file)
    if args.intersect:
        states = [s for s in states if os.path.exists(os.path.join(args.current, s, args.file))]
    if not states:
        print(f"No comparable states under {args.baseline}")
        return 1

    rows, failures = [], []
    for state in states:
        cur_path = os.path.join(args.current, state, args.file)
        if not os.path.exists(cur_path):
            rows.append({"state": state, "missing": True})
            failures.append(state)
            print(f"  MISSING  {state}")
            continue
        base = Image.open(os.path.join(args.baseline, state, args.file))
        cur = Image.open(cur_path)
        result = compare_state(base, cur, args.tolerance, rectangles(mask, state))
        if isinstance(result, dict):
            info = result
            heat = None
        else:
            info, heat = result
        info["state"] = state
        rows.append(info)
        if not info.get("ok"):
            failures.append(state)
        if heat is not None and not args.no_heatmaps:
            heat.save(os.path.join(args.current, state, "diff.png"))
        verdict = "SIZE" if "size_mismatch" in info else ("OK" if info.get("ok") else "DIFF")
        detail = (str(info["size_mismatch"]) if "size_mismatch" in info
                  else f"{info['differing_pixels']} px ({info['percent']}%), bbox {info.get('bbox')}")
        print(f"  {verdict:5s}  {state}  {detail}")

    lines = [
        "# Style parity — exact before/after diff", "",
        f"Baseline: `{args.baseline}`  ", f"Current: `{args.current}`  ",
        f"File: `{args.file}` | tolerance: {args.tolerance} channel delta | "
        f"mask: `{mask_path or 'none'}`", "",
        "| state | differing px | % | bbox | verdict |", "|---|---|---|---|---|",
    ]
    for row in rows:
        if row.get("missing"):
            lines.append(f"| {row['state']} | — | — | — | MISSING |")
        elif "size_mismatch" in row:
            lines.append(f"| {row['state']} | — | — | — | SIZE MISMATCH |")
        else:
            lines.append(f"| {row['state']} | {row['differing_pixels']} | {row['percent']} | "
                         f"{row.get('bbox', '—')} | {'OK' if row['ok'] else 'DIFF'} |")
    lines += ["", f"FAILED: {len(failures)} state(s)" if failures
              else "PASSED: 0 unmasked differences."]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(report)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
