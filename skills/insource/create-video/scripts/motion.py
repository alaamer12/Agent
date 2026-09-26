#!/usr/bin/env python3
"""Estimate which way the dominant object moved between two frames.

Pure stdlib plus ffmpeg/ffprobe (already required by this skill): both frames
are decoded to downscaled grayscale, then the pixels that *brightened* are
compared against the pixels that *darkened*. A rigid object that moves leaves a
darkened trail where it was and a brightened blob where it went, so the vector
from the darkened centroid to the brightened centroid is the object's
displacement. Its bearing maps to an 8-way compass direction.

Usage:
  motion.py <frameA> <frameB>            one pair, human-readable verdict
  motion.py <frameA> <frameB> --json     same verdict as JSON
  motion.py --seq <dir> [--step N]       every consecutive pair in a frame dump
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

PROBE_WIDTH = 160  # analysis resolution: enough to localise motion, cheap to scan in pure Python

COMPASS = ["top", "top-right", "right", "bottom-right", "bottom", "bottom-left", "left", "top-left"]
GLYPH = {"top": "^", "top-right": "\\", "right": ">", "bottom-right": "/", "bottom": "v",
         "bottom-left": "\\", "left": "<", "top-left": "/"}

MIN_MOVE = 0.012      # below this fraction of frame width there is no translation to report
NOISE_FLOOR = 6.0     # 6/255: JPEG ringing we never want to call motion
STATIC_AREA = 0.008   # under 0.8% of the frame changed, the scene is simply still
CUT_MOVE = 0.95       # a "displacement" this large is geometrically absurd for one object
LOBE_BALANCE = 0.18   # weaker lobe this far under the stronger one: one-sided change
SCATTER_LIMIT = 0.22  # lobe spread this large relative to the frame diagonal: no single object
                      # (uniform noise over a frame measures ~0.29, a compact object ~0.05)


def probe_size(path: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", str(path)],
        capture_output=True, text=True,
    ).stdout
    try:
        stream = json.loads(out)["streams"][0]
        return int(stream["width"]), int(stream["height"])
    except Exception:
        raise SystemExit(f"ffprobe could not read dimensions from {path}")


def target_size(w: int, h: int) -> tuple[int, int]:
    if w <= PROBE_WIDTH:
        return max(2, w - w % 2), max(2, h - h % 2)
    return PROBE_WIDTH, max(2, int(round(h * PROBE_WIDTH / w / 2)) * 2)


def load_gray(path: Path, size: tuple[int, int] | None = None) -> tuple[int, int, list[int]]:
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is not installed. Install with: sudo apt install ffmpeg")
    w, h = probe_size(path)
    tw, th = size or target_size(w, h)
    res = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-vf", f"scale={tw}:{th}:flags=area,format=gray", "-f", "rawvideo", "-"],
        capture_output=True,
    )
    if res.returncode or len(res.stdout) < tw * th:
        detail = res.stderr.decode(errors="replace").strip()
        raise SystemExit(f"ffmpeg could not decode {path}: {detail or 'no pixel data returned'}")
    return tw, th, list(res.stdout[: tw * th])


def box_blur(vals: list[int], w: int, h: int) -> list[int]:
    """3x3 mean, clamped at the borders — kills JPEG block noise before differencing."""
    out = [0] * len(vals)
    for y in range(h):
        y0, y1 = max(0, y - 1), min(h - 1, y + 1)
        row = y * w
        for x in range(w):
            x0, x1 = max(0, x - 1), min(w - 1, x + 1)
            total = 0
            count = 0
            for yy in range(y0, y1 + 1):
                base = yy * w
                for xx in range(x0, x1 + 1):
                    total += vals[base + xx]
                    count += 1
            out[row + x] = total // count
    return out


def mad(vals: list[int]) -> float:
    if not vals:
        return 0.0
    mean = sum(vals) / len(vals)
    return sum(abs(v - mean) for v in vals) / len(vals)


def lobe_stats(indices: list[int], weights: list[int], w: int, h: int) -> dict | None:
    if not indices:
        return None
    total = sum(weights)
    if total <= 0:
        return None
    cx = sum(i % w * wt for i, wt in zip(indices, weights)) / total
    cy = sum(i // w * wt for i, wt in zip(indices, weights)) / total
    spread = math.sqrt(sum(((i % w - cx) ** 2 + (i // w - cy) ** 2) * wt
                           for i, wt in zip(indices, weights)) / total)
    return {
        "x": cx, "y": cy,
        "mass": total,
        "count": len(indices),
        "fraction": len(indices) / (w * h),
        "spread": spread / math.hypot(w, h),
    }


def lobes(a: list[int], b: list[int], w: int, h: int) -> dict:
    """Split the frame-to-frame difference into the brightened and darkened halves."""
    pa, pb = box_blur(a, w, h), box_blur(b, w, h)
    delta = [pb[i] - pa[i] for i in range(len(pa))]

    ordered = sorted((abs(d) for d in delta), reverse=True)
    knee = ordered[min(len(ordered) - 1, int(len(ordered) * 0.04))]
    thr = max(NOISE_FLOOR, knee * 0.6)

    bright_idx, bright_w, dark_idx, dark_w = [], [], [], []
    for i, d in enumerate(delta):
        if d > thr:
            bright_idx.append(i)
            bright_w.append(d)
        elif d < -thr:
            dark_idx.append(i)
            dark_w.append(-d)

    return {
        "bright": lobe_stats(bright_idx, bright_w, w, h),
        "dark": lobe_stats(dark_idx, dark_w, w, h),
        "changed": (len(bright_idx) + len(dark_idx)) / (w * h),
        "threshold": thr,
        "texture": max(mad(pa), mad(pb)),
        "flatness": min(mad(pa), mad(pb)),
    }


def classify(a: list[int], b: list[int], w: int, h: int) -> dict:
    """Decide where the object went, with a reason and a confidence."""
    lob = lobes(a, b, w, h)
    bright, dark = lob["bright"], lob["dark"]
    changed = lob["changed"]
    base = {
        "changed_area": round(changed, 4),
        "threshold": round(lob["threshold"], 1),
        "texture": round(lob["texture"], 1),
    }

    def verdict(direction, bearing, dx, dy, magnitude, confidence, reason, ends=None):
        out = {**base, "direction": direction, "bearing": bearing, "dx": dx, "dy": dy,
               "magnitude": magnitude, "confidence": confidence, "reason": reason}
        if ends:
            out["from"], out["to"] = ends
        return out

    if not bright and not dark:
        # Nothing crossed the noise floor. Only call that "the same shot" if the
        # frames actually carry structure — a low-contrast pair has nothing to
        # compare, and a dark scene is not the same thing as a blank one.
        if lob["flatness"] < 3.0:
            return verdict("cannot-determine", None, None, None, None, 0.0,
                           "no pixel changed above the noise floor and the frames carry no "
                           "structure to track")
        return verdict("in-place", None, 0.0, 0.0, 0.0, 0.99,
                       "no pixel changed above the noise floor; the two frames are the same shot")

    if not bright or not dark:
        side = "brightening" if bright else "darkening"
        return verdict("cannot-determine", None, None, None, None, 0.05,
                       f"only {side} was detected — an object entering or leaving the frame, "
                       "a fade, or a cut, rather than one moving through it")

    masses = sorted([bright["mass"], dark["mass"]])
    balance = masses[0] / masses[1]
    spread = max(bright["spread"], dark["spread"])
    ends = ((round(dark["x"] / w, 3), round(dark["y"] / h, 3)),
            (round(bright["x"] / w, 3), round(bright["y"] / h, 3)))

    if balance < LOBE_BALANCE:
        return verdict("cannot-determine", None, None, None, None, 0.15,
                       "the two lobes are badly unbalanced, so the change is not a single "
                       "object moving (a cut, an overlay, or something entering the frame)", ends)

    if spread > SCATTER_LIMIT:
        return verdict("cannot-determine", None, None, None, None, 0.2,
                       "the change is scattered across the frame instead of forming one object — "
                       "most likely a scene cut or heavy compression noise", ends)

    dx_px = bright["x"] - dark["x"]
    dy_px = bright["y"] - dark["y"]
    dx, dy = dx_px / w, dy_px / h
    magnitude = math.hypot(dx, dy)

    if magnitude > CUT_MOVE:
        return verdict("cannot-determine", None, None, None, round(magnitude, 4), 0.1,
                       "the apparent displacement spans most of the frame, which means the two "
                       "frames share no subject — treat this as a cut", ends)

    if changed < STATIC_AREA:
        return verdict("in-place", None, 0.0, 0.0, round(magnitude, 4), 0.95,
                       "nothing above the noise floor moved; the scene is static", ends)

    if magnitude < MIN_MOVE:
        return verdict("in-place", None, round(dx, 4), round(dy, 4), round(magnitude, 4), 0.8,
                       f"{changed:.1%} of the frame changed but the centre of mass did not shift — "
                       "consistent with the object rotating or deforming about itself", ends)

    bearing = math.degrees(math.atan2(dx_px, -dy_px)) % 360
    tightness = 1.0 - min(1.0, spread / SCATTER_LIMIT)
    strength = min(1.0, math.log10(max(1e-6, changed) * 40) + 1.0)
    confidence = round(max(0.0, min(1.0, 0.45 * balance + 0.35 * tightness + 0.2 * strength)), 2)

    return verdict(COMPASS[round(bearing / 45) % 8], round(bearing, 1), round(dx, 4), round(dy, 4),
                   round(magnitude, 4), confidence,
                   f"the object left {dark['fraction']:.1%} of the frame and arrived at "
                   f"{bright['fraction']:.1%}, {magnitude:.1%} of the frame away", ends)


def motion_map(frm: tuple[float, float], to: tuple[float, float], direction: str,
               cols: int = 15, rows: int = 9) -> list[str]:
    """ASCII view of the frame: o = where it was, # = where it went, glyph = the path."""
    grid = [["."] * cols for _ in range(rows)]

    def cell(point):
        return (min(cols - 1, max(0, int(point[0] * cols))),
                min(rows - 1, max(0, int(point[1] * rows))))

    grid[cell(frm)[1]][cell(frm)[0]] = "o"
    grid[cell(to)[1]][cell(to)[0]] = "#"
    glyph = GLYPH.get(direction, "?")
    steps = max(abs(to[0] - frm[0]) * cols, abs(to[1] - frm[1]) * rows)
    for s in range(1, int(steps) + 1):
        t = s / (int(steps) + 1)
        x, y = frm[0] + (to[0] - frm[0]) * t, frm[1] + (to[1] - frm[1]) * t
        cx, cy = cell((x, y))
        if grid[cy][cx] == ".":
            grid[cy][cx] = glyph
    return ["".join(row) for row in grid]


def frame_files(directory: Path) -> list[Path]:
    files = sorted(
        p for p in directory.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    if not files:
        raise SystemExit(f"no image files found in {directory}")
    return files


def run_pair(path_a: Path, path_b: Path, as_json: bool) -> dict:
    w, h, a = load_gray(path_a)
    _, _, b = load_gray(path_b, (w, h))
    verdict = classify(a, b, w, h)
    verdict["frame_a"] = str(path_a)
    verdict["frame_b"] = str(path_b)
    verdict["probe"] = f"{w}x{h}"

    if as_json:
        return verdict

    print(f"# motion: {path_a.name} \u2192 {path_b.name}")
    print()
    print(f"- **Direction:** {verdict['direction']}")
    if verdict["bearing"] is not None:
        print(f"- **Bearing:** {verdict['bearing']}\u00b0 (0\u00b0 = up, clockwise)")
    if verdict["dx"] is not None:
        print(f"- **Shift:** dx={verdict['dx']:+.1%} dy={verdict['dy']:+.1%} "
              f"({verdict['magnitude']:.1%} of the frame)")
    print(f"- **Changed area:** {verdict['changed_area']:.1%} of the frame")
    print(f"- **Confidence:** {verdict['confidence']}")
    print(f"- **Why:** {verdict['reason']}")
    if verdict.get("from") and verdict.get("to"):
        print()
        print("```")
        print("o = where it was, # = where it went")
        for row in motion_map(verdict["from"], verdict["to"], verdict["direction"]):
            print(row)
        print("```")
    return verdict


def run_seq(directory: Path, step: int, as_json: bool) -> dict:
    files = frame_files(directory)
    if len(files) < 2:
        raise SystemExit(f"{directory} holds {len(files)} frame; measuring motion needs at least two")
    if step >= len(files):
        raise SystemExit(
            f"--step {step} spans all {len(files)} frames in {directory}; use --step {len(files) - 1} or less"
        )
    pairs = [(files[i], files[min(i + step, len(files) - 1)]) for i in range(len(files) - step)]
    results = []
    for path_a, path_b in pairs:
        w, h, a = load_gray(path_a)
        _, _, b = load_gray(path_b, (w, h))
        verdict = classify(a, b, w, h)
        verdict["frame_a"] = path_a.name
        verdict["frame_b"] = path_b.name
        results.append(verdict)

    tally: dict[str, int] = {}
    for r in results:
        tally[r["direction"]] = tally.get(r["direction"], 0) + 1
    moving = [r for r in results if r["direction"] in GLYPH]
    dominant = max(tally, key=tally.get) if tally else "in-place"

    summary = {
        "frames": len(files),
        "pairs": len(results),
        "step": step,
        "tally": tally,
        "dominant": dominant,
        "moving_pairs": len(moving),
        "static_pairs": tally.get("in-place", 0),
        "undetermined_pairs": tally.get("cannot-determine", 0),
        "pairs_detail": results,
    }

    if as_json:
        return summary

    print(f"# motion sequence: {directory}")
    print()
    print(f"- **Frames:** {len(files)} · **Pairs compared:** {len(results)} (step {step})")
    print(f"- **Dominant:** {dominant}")
    print(f"- **Moving:** {len(moving)} · **Static/in-place:** {tally.get('in-place', 0)} "
          f"· **Undetermined:** {tally.get('cannot-determine', 0)}")
    print()
    print("```")
    print(f"{'from':<18}{'to':<18}{'direction':<15}{'mag':>8}  conf")
    for r in results:
        mag = f"{r['magnitude']:.1%}" if r["magnitude"] is not None else "-"
        print(f"{r['frame_a']:<18}{r['frame_b']:<18}{r['direction']:<15}{mag:>8}  {r['confidence']}")
    print("```")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="motion",
        description="Which way did the object go between two frames?",
    )
    ap.add_argument("frames", nargs="*", type=Path, help="two frames to compare")
    ap.add_argument("--seq", type=Path, default=None, metavar="DIR",
                    help="compare consecutive frames in a directory instead of one pair")
    ap.add_argument("--step", type=int, default=1,
                    help="with --seq: compare each frame to the one N steps later (default 1)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON only")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise SystemExit("ffmpeg and ffprobe are required. Install with: sudo apt install ffmpeg")

    if args.seq:
        directory = args.seq.expanduser().resolve()
        if not directory.is_dir():
            raise SystemExit(f"--seq expects a directory of frames, got {directory}")
        summary = run_seq(directory, max(1, args.step), args.json)
        if args.json:
            print(json.dumps(summary, indent=2))
        return 0

    if len(args.frames) != 2:
        raise SystemExit("give exactly two frames, or use --seq <dir>")
    path_a, path_b = (p.expanduser().resolve() for p in args.frames)
    for p in (path_a, path_b):
        if not p.is_file():
            raise SystemExit(f"frame not found: {p}")
    verdict = run_pair(path_a, path_b, args.json)
    if args.json:
        print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
