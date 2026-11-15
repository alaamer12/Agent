#!/usr/bin/env python3
"""
pixel_regression.py — exact app-vs-app pixel regression across state directories.

Similarity scoring answers "does the app resemble the design?". This answers a
different question: "did the refactor change *anything* it was not supposed to?".
The gate is exactness: the two capture trees must be byte-identical except for
regions you explicitly declare dynamic.

Both trees must be produced by the same capture pipeline (``run_suite.py
--capture-only`` or ``parity_run.py``), so each state directory contains one
normalized frame. A build-version manifest is not required, but capturing
baseline and current with the same viewport and DPR is.

Mask schema (JSON; auto-loaded from ``<baseline>/masks.json`` when --mask is
omitted):

    {
      "global": [[x, y, w, h], ...],
      "states": {
        "home__default__light": [[x, y, w, h], ...]
      }
    }

Masked rectangles are zeroed before comparison, so genuinely dynamic content
(live clocks, avatars, animations, randomised feeds) does not fail the gate.
Every masked rectangle should be documented — a mask that hides a real
regression is worse than no regression gate.

Usage:
    python pixel_regression.py --baseline parity_out/before --current parity_out/after
    python pixel_regression.py --baseline B --current C \
        --mask masks.json --tolerance 2 --report C/report.md
    python pixel_regression.py --baseline B --current C --intersect

Exit codes: 0 = every compared state is identical outside the mask; 1 = at
least one state differs, is missing, or has a size mismatch.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image


def load_mask(path: str | None) -> dict:
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def rectangles(mask: dict, state_id: str) -> list[list[int]]:
    return (list(mask.get("global") or [])
            + list((mask.get("states") or {}).get(state_id) or []))


def apply_mask(diff: np.ndarray, rects: list[list[int]]) -> np.ndarray:
    if not rects or not diff.size:
        return diff
    h, w = diff.shape[:2]
    for x, y, rw, rh in rects:
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(w, int(x) + int(rw)), min(h, int(y) + int(rh))
        if x1 > x0 and y1 > y0:
            diff[y0:y1, x0:x1] = 0
    return diff


def compare_state(base_png: str, cur_png: str, tolerance: int,
                  rects: list[list[int]], diff_png: str | None) -> dict:
    a = np.asarray(Image.open(base_png).convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(cur_png).convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        return {"size_mismatch": [list(a.shape), list(b.shape)], "ok": False}

    delta = np.abs(a - b)
    masked = apply_mask(delta, rects)
    per_pixel = masked.max(axis=2)
    differing = per_pixel > tolerance
    count = int(differing.sum())
    total = int(differing.size)

    info = {
        "ok": count == 0,
        "differing_pixels": count,
        "total_pixels": total,
        "percent": round(100.0 * count / total, 4) if total else 0.0,
        "max_delta": int(per_pixel.max()) if total else 0,
        "masked_rects": rects,
    }
    if count:
        ys, xs = np.nonzero(differing)
        info["bbox"] = [int(xs.min()), int(ys.min()),
                        int(xs.max()) + 1, int(ys.max()) + 1]
    if diff_png:
        heat = np.clip(per_pixel, 0, 255).astype(np.uint8)
        out_dir = os.path.dirname(os.path.abspath(diff_png))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        Image.fromarray(heat, mode="L").save(diff_png)
    return info


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exact pixel diff between two capture trees.")
    parser.add_argument("--baseline", required=True, help="baseline capture dir")
    parser.add_argument("--current", required=True, help="after-change capture dir")
    parser.add_argument("--image-name", default="app.png",
                        help="frame filename inside each state dir (default app.png)")
    parser.add_argument("--mask", default=None,
                        help="mask JSON (default: <baseline>/masks.json if present)")
    parser.add_argument("--tolerance", type=int, default=0,
                        help="allowed max channel delta per pixel (default 0 = exact)")
    parser.add_argument("--report", default=None,
                        help="write a Markdown report here")
    parser.add_argument("--json-out", default=None,
                        help="write the machine-readable result here")
    parser.add_argument("--no-heatmaps", action="store_true",
                        help="skip per-state diff PNGs")
    parser.add_argument("--intersect", action="store_true",
                        help="compare only states present in BOTH dirs")
    args = parser.parse_args()

    if not os.path.isdir(args.baseline):
        print(f"Baseline directory not found: {args.baseline}", file=sys.stderr)
        return 1

    mask_path = args.mask or os.path.join(args.baseline, "masks.json")
    mask = load_mask(mask_path)

    states = sorted(
        d for d in os.listdir(args.baseline)
        if os.path.isfile(os.path.join(args.baseline, d, args.image_name))
    )
    if args.intersect:
        states = [s for s in states
                  if os.path.exists(os.path.join(args.current, s, args.image_name))]
    if not states:
        print(f"No comparable states under {args.baseline}")
        return 1

    rows, failures = [], []
    for sid in states:
        base_png = os.path.join(args.baseline, sid, args.image_name)
        cur_png = os.path.join(args.current, sid, args.image_name)
        if not os.path.exists(cur_png):
            rows.append({"id": sid, "ok": False, "missing": True})
            failures.append(sid)
            print(f"  MISSING  {sid}")
            continue

        diff_png = (None if args.no_heatmaps
                    else os.path.join(args.current, sid, "diff.png"))
        info = compare_state(base_png, cur_png, args.tolerance,
                             rectangles(mask, sid), diff_png)
        info["id"] = sid
        rows.append(info)
        if not info.get("ok"):
            failures.append(sid)

        status = ("OK" if info.get("ok")
                  else "DIFF" if "size_mismatch" not in info else "SIZE")
        detail = (
            f"{info.get('differing_pixels', '?')} px "
            f"({info.get('percent', '?')}%), max {info.get('max_delta', '?')}, "
            f"bbox {info.get('bbox', '-')}"
            if "size_mismatch" not in info else str(info["size_mismatch"])
        )
        print(f"  {status:5s}  {sid}  {detail}")

    lines = [
        "# Pixel regression",
        "",
        f"Baseline: `{args.baseline}`  ",
        f"Current: `{args.current}`  ",
        f"Tolerance: {args.tolerance} channel delta  ",
        f"Mask: `{mask_path if os.path.exists(mask_path) else 'none'}`",
        "",
        "| state | differing px | % | max delta | bbox | verdict |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row.get("missing"):
            lines.append(f"| {row['id']} | — | — | — | — | MISSING |")
        elif "size_mismatch" in row:
            lines.append(f"| {row['id']} | — | — | — | — | SIZE MISMATCH |")
        else:
            lines.append(
                f"| {row['id']} | {row['differing_pixels']} | {row['percent']} | "
                f"{row['max_delta']} | {row.get('bbox', '—')} | "
                f"{'OK' if row['ok'] else 'DIFF'} |")
    lines += ["", (f"FAILED: {len(failures)} state(s)"
                   if failures else "PASSED: 0 unmasked differences.")]
    report = "\n".join(lines) + "\n"
    print(report)

    if args.report:
        out_dir = os.path.dirname(os.path.abspath(args.report))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(report)

    if args.json_out:
        out_dir = os.path.dirname(os.path.abspath(args.json_out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"baseline": args.baseline, "current": args.current,
                       "tolerance": args.tolerance, "states": rows},
                      fh, indent=2, ensure_ascii=False)

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
