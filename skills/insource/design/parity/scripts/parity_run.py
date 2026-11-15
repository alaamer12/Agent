#!/usr/bin/env python3
"""
parity_run.py — launch, capture, normalize, score and localize one parity state.

This is the "one iteration" of the parity loop, scripted. For each
page × theme × variant × state it:

  1. force-kills any stale instance (a single-instance app would otherwise
     redirect the launch and silently capture the wrong state),
  2. launches the app with your templated flags,
  3. waits for the real main window (largest window owned by the target),
  4. settles, captures via ``PrintWindow``, detects and crops the caption band,
  5. fits the content onto the design viewport canvas,
  6. finds the matching design frame,
  7. scores it with ``similarity.run_comparison`` (all five methods),
  8. optionally measures the best-fit translation offset and re-scores the
     aligned pair, so window chrome is not mistaken for a component bug,
  9. prints the global score, the regional grid, the palette report and the
     worst cells' boxes, and writes a heatmap.

Nothing here knows about any particular product. Everything process- or
design-specific arrives as a flag.

Launch templating
-----------------
Every token of ``--launch-args`` is substituted with:

  {page} {theme} {variant} {state}

Example:
  --launch-args "--page={page} --theme={theme} --state={state} --skip-gate"

Design frame resolution
-----------------------
``--design-pattern`` is resolved under ``--design-root``. Placeholders:
``{page} {theme} {variant} {state}``. When the primary pattern is missing,
``--fallback-pattern`` is tried; if both miss, the state is reported as
UNVERIFIED rather than silently scored against the wrong reference.

Usage:
    python parity_run.py --exe build/app.exe \
        --launch-args "--page={page} --theme={theme}" \
        --pages home settings --themes light dark \
        --design-root parity_captures --viewport 1280x800

    python parity_run.py --exe build/app.exe --page home --theme dark \
        --design-root captures --threshold 0.92 --json-out reports/home_dark.json

Exit codes: 0 all states scored and at threshold; 1 at least one state failed,
was unverified, or scored below threshold.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import shlex
import subprocess
import sys
import time

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_app import normalize_capture, parse_fill  # noqa: E402
from similarity import run_comparison  # noqa: E402
from snip_tool import (  # noqa: E402
    capture_window,
    find_target_windows,
    setup_logging,
)


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def parse_px(value: str, default: tuple[int, int] = (1280, 800)) -> tuple[int, int]:
    if not value or value.lower() in {"none", "0x0"}:
        return default
    if "x" not in value.lower():
        raise SystemExit(f"expected WxH, got: {value}")
    w, h = value.lower().split("x", 1)
    return int(w), int(h)


def split_list(value: str | None, default: list[str] | None = None) -> list[str]:
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(",") if item.strip()]


def substitute(template: str, page: str, theme: str, variant: str, state: str) -> str:
    return (template
            .replace("{page}", page)
            .replace("{theme}", theme)
            .replace("{variant}", variant)
            .replace("{state}", state))


def build_state_id(page: str, variant: str, theme: str, state: str) -> str:
    sid = f"{page}__{variant}__{theme}"
    if state and state != "default":
        sid += f"__{state}"
    return sid


def next_version(directory: str, stem: str) -> int:
    versions = []
    for path in glob.glob(os.path.join(directory, f"{stem}_v*.png")):
        match = re.search(r"_v(\d+)\.png$", path)
        if match:
            versions.append(int(match.group(1)))
    return max(versions, default=0) + 1


def state_id_of_image(path: str) -> str:
    stem = os.path.splitext(os.path.basename(path))[0]
    return re.sub(r"_v\d+$", "", stem)


# --------------------------------------------------------------------------- #
# Process control (Windows)
# --------------------------------------------------------------------------- #

def _run_taskkill(args: list[str]) -> None:
    if os.name != "nt":
        return
    subprocess.run(["taskkill"] + args, capture_output=True, text=True)


def kill_by_name(window_name: str, timeout: float = 10.0) -> None:
    """Force-kill every process with this image name and wait for its windows."""
    if os.name != "nt":
        return
    _run_taskkill(["/IM", window_name, "/F"])
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not find_target_windows(name=window_name):
            return
        _run_taskkill(["/IM", window_name, "/F"])
        time.sleep(0.5)


def terminate_proc(proc: subprocess.Popen, window_name: str) -> None:
    _run_taskkill(["/PID", str(proc.pid), "/T", "/F"])
    if os.name == "nt":
        deadline = time.time() + 8
        while time.time() < deadline:
            if not find_target_windows(name=window_name):
                return
            time.sleep(0.4)
        _run_taskkill(["/IM", window_name, "/F"])
    else:
        try:
            proc.terminate()
        except Exception:
            pass


def launch_app(exe: str, tokens: list[str]) -> subprocess.Popen:
    return subprocess.Popen([exe] + tokens, cwd=os.path.dirname(os.path.abspath(exe)))


def wait_for_window(proc: subprocess.Popen, window_name: str,
                    window_title: str | None, wait_s: float,
                    min_area: int = 200_000) -> dict | None:
    """Wait for the largest window of the launched process (falls back to name)."""
    deadline = time.time() + wait_s
    while time.time() < deadline:
        time.sleep(1.0)
        own = [
            w for w in find_target_windows(name=window_name, title=window_title)
            if w["pid"] == proc.pid and w["area"] > min_area
        ]
        if own:
            return max(own, key=lambda w: w["area"])
        if proc.poll() is not None:
            return None
        # The launcher may not own the window (single-instance redirect).
        others = [w for w in find_target_windows(name=window_name, title=window_title)
                  if w["area"] > min_area]
        if others:
            return max(others, key=lambda w: w["area"])
    return None


# --------------------------------------------------------------------------- #
# Alignment (reported, never silently absorbed)
# --------------------------------------------------------------------------- #

def best_fit_shift(design: str, app: str, max_dy: int = 160,
                   max_dx: int = 32) -> tuple[int, int, float, float] | None:
    """Coarse-to-fine translation search that minimises mean absolute difference.

    A similarity score cannot distinguish a wrong component from a correct
    component drawn 34px lower. This measures that offset so it can be reported
    and corrected before the design verdict is trusted.
    """
    import numpy as np

    d = np.asarray(Image.open(design).convert("L"), dtype=np.int16)
    a = np.asarray(Image.open(app).convert("L"), dtype=np.int16)
    h = min(d.shape[0], a.shape[0])
    w = min(d.shape[1], a.shape[1])
    d, a = d[:h, :w], a[:h, :w]

    def mad(dy: int, dx: int) -> float:
        top, bottom = max(0, dy), min(h, h + dy)
        left, right = max(0, dx), min(w, w + dx)
        if bottom - top < h // 2 or right - left < w // 2:
            return float("inf")
        return float(np.abs(
            d[top:bottom, left:right] - a[top - dy:bottom - dy, left - dx:right - dx]
        ).mean())

    best = (mad(0, 0), 0, 0)
    for step in (8, 2, 1):
        cy, cx = best[1], best[2]
        for dy in range(cy - 2 * step, cy + 2 * step + 1, step):
            if abs(dy) > max_dy:
                continue
            for dx in range(cx - 2 * step, cx + 2 * step + 1, step):
                if abs(dx) > max_dx:
                    continue
                score = mad(dy, dx)
                if score < best[0]:
                    best = (score, dy, dx)

    return best[1], best[2], mad(0, 0), best[0]


def shift_copy(app: str, dy: int, dx: int, out: str,
               fill: tuple[int, int, int] = (241, 245, 249)) -> str:
    """Paste the app capture moved onto the design grid, filling the vacated band."""
    img = Image.open(app).convert("RGB")
    canvas = Image.new("RGB", img.size, fill)
    canvas.paste(img, (dx, dy))
    canvas.save(out)
    return out


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def structure_similarity(design: str, app: str, tmp_dir: str) -> dict:
    """Cross-renderer score with a 1px Gaussian blur on both sides.

    GDI/DirectWrite and Chromium land the same glyph outline on different
    pixels. At small text sizes that alone depresses raw MSE even when the
    implementation is faithful. The blurred structural/histogram/hash blend is
    reported next to the raw score: structure-but-not-pixels means a rendering
    engine difference; neither means a real bug.
    """
    paths = []
    try:
        for src, tag in ((design, "m"), (app, "a")):
            p = os.path.join(tmp_dir, f"_struct_{tag}.png")
            Image.open(src).convert("RGB").filter(ImageFilter.GaussianBlur(1.0)).save(p)
            paths.append(p)
        report = run_comparison(
            paths[0], paths[1], resize_mode="pad",
            region_report=False, methods=["ssim", "histogram", "hash"],
        ).to_dict()
        return {
            "overall": report["overall_similarity"],
            "ssim": report["scores"].get("ssim"),
            "histogram": (report["scores"].get("histogram") or {}).get("combined"),
            "hash": (report["scores"].get("perceptual_hash") or {}).get("combined"),
        }
    finally:
        for path in paths:
            try:
                os.remove(path)
            except OSError:
                pass


def score_pair(design: str, app: str, heatmap: str | None,
               methods: list[str] | None = None,
               regional_grid: int = 6, palette: int = 8) -> dict:
    report = run_comparison(
        design, app,
        resize_mode="pad",
        methods=methods,
        region_report=False,
        heatmap_out=heatmap,
        regional_score=regional_grid,
        palette=palette,
    )
    data = report.to_dict()
    grid = data.get("regional_score") or {}
    cells = grid.get("cells") or []
    flat = [value for row in cells for value in row]
    return {
        "overall": data.get("overall_similarity"),
        "ssim": (data.get("scores") or {}).get("ssim"),
        "palette_similarity": (data.get("palette") or {}).get("palette_similarity"),
        "regional_cells": cells,
        "regional_mean": float(sum(flat) / len(flat)) if flat else None,
        "worst": (grid.get("worst") or [])[:5],
        "full": data,
    }


# --------------------------------------------------------------------------- #
# Design frame resolution
# --------------------------------------------------------------------------- #

def resolve_design(root: str, pattern: str, fallback: str | None,
                   page: str, theme: str, variant: str,
                   state: str) -> str | None:
    primary = os.path.normpath(
        os.path.join(root, substitute(pattern, page, theme, variant, state)))
    if os.path.exists(primary):
        return primary
    if fallback:
        alt = os.path.normpath(
            os.path.join(root, substitute(fallback, page, theme, variant, state)))
        if os.path.exists(alt):
            print(f"  WARN: using fallback design frame {alt}", file=sys.stderr)
            return alt
    return None


# --------------------------------------------------------------------------- #
# One state
# --------------------------------------------------------------------------- #

def run_state(args: argparse.Namespace, page: str, theme: str, variant: str,
              state: str, out_root: str) -> dict:
    sid = build_state_id(page, variant, theme, state)
    page_dir = os.path.join(out_root, page)
    os.makedirs(page_dir, exist_ok=True)
    version = next_version(page_dir, f"app_{variant}_{theme}")
    app_png = os.path.join(page_dir, f"app_{variant}_{theme}_v{version}.png")
    heatmap = os.path.join(page_dir, f"diff_{variant}_{theme}_v{version}.png")

    design = resolve_design(args.design_root, args.design_pattern,
                            args.fallback_pattern, page, theme, variant, state)
    entry: dict = {
        "id": sid, "page": page, "theme": theme, "variant": variant,
        "state": state, "status": "pending", "design": design, "app": app_png,
    }
    if not design:
        entry["status"] = "unverified"
        entry["error"] = "no design frame matched --design-pattern/--fallback-pattern"
        print(f"  UNVERIFIED {sid}: {entry['error']}")
        return entry

    tokens = [substitute(token, page, theme, variant, state)
              for token in shlex.split(args.launch_args or "")]

    if args.kill_first:
        kill_by_name(args.window_name)

    proc = launch_app(args.exe, tokens)
    entry["launch_tokens"] = tokens
    try:
        window = wait_for_window(proc, args.window_name, args.window_title,
                                 args.wait, args.min_area)
        if not window:
            entry["status"] = "no-window"
            entry["error"] = f"no window >{args.min_area}px found within {args.wait}s"
            print(f"  FAILED {sid}: {entry['error']}")
            return entry

        time.sleep(args.settle)
        window = (find_target_windows(name=args.window_name, title=args.window_title,
                                      pid=window["pid"]) or [window])[0]

        raw = capture_window(window["hwnd"])
        entry["window_size"] = list(raw.size)
        normalized, chrome = normalize_capture(
            raw, chrome_mode=args.chrome_crop, target_size=args.viewport,
            fill=parse_fill(args.fill), anchor=args.anchor,
        )
        entry["chrome_crop_px"] = chrome
        entry["captured_size"] = list(normalized.size)
        normalized.save(app_png)

        entry["scores"] = score_pair(design, app_png, heatmap, args.methods,
                                     args.regional_grid, args.palette)
        entry["structure"] = structure_similarity(design, app_png, page_dir)

        if not args.no_align:
            shift = best_fit_shift(design, app_png, args.max_shift_dy,
                                   args.max_shift_dx)
            if shift is not None:
                dy, dx, mad_raw, mad_shifted = shift
                aligned = os.path.join(
                    page_dir, f"app_{variant}_{theme}_v{version}_aligned.png")
                shift_copy(app_png, dy, dx, aligned, parse_fill(args.fill))
                aligned_heat = os.path.join(
                    page_dir, f"diff_{variant}_{theme}_v{version}_aligned.png")
                entry["alignment"] = {
                    "dy": dy, "dx": dx,
                    "mad_raw": mad_raw, "mad_aligned": mad_shifted,
                    "aligned_png": aligned,
                }
                entry["aligned_scores"] = score_pair(
                    design, aligned, aligned_heat, args.methods,
                    args.regional_grid, args.palette)

        entry["status"] = "scored"
        score = entry["scores"]["overall"] or 0.0
        entry["meets_threshold"] = score >= args.threshold
        print(f"  OK {sid}: raw {score:.2%} "
              f"structure {(entry['structure']['overall'] or 0):.2%} "
              f"palette {(entry['scores']['palette_similarity'] or 0):.2%} "
              f"(threshold {args.threshold:.0%})")
        for cell in entry["scores"]["worst"][:3]:
            print(f"    worst r{cell['row']}c{cell['col']} "
                  f"sim={cell['similarity']:.3f} box={cell['box']}")
        return entry
    except Exception as exc:  # keep the matrix moving; failure stays visible in JSON
        entry["status"] = "error"
        entry["error"] = f"{type(exc).__name__}: {exc}"
        print(f"  ERROR {sid}: {entry['error']}")
        return entry
    finally:
        if not args.keep_open:
            terminate_proc(proc, args.window_name)


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def md_report(rows: list[dict], threshold: float) -> str:
    lines = [
        "# Parity run",
        "",
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}  ",
        f"Threshold: {threshold:.0%}  ",
        "",
        "| state | status | raw | structure | palette | worst cells (grid) |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        scores = row.get("scores") or {}
        structure = row.get("structure") or {}
        raw = scores.get("overall")
        st = structure.get("overall")
        palette = scores.get("palette_similarity")
        worst = ", ".join(
            f"r{c['row']}c{c['col']}={c['similarity']:.2f}"
            for c in (scores.get("worst") or [])[:4]
        ) or "—"
        lines.append(
            f"| {row['id']} | {row['status']} | "
            f"{'—' if raw is None else f'{raw:.2%}'} | "
            f"{'—' if st is None else f'{st:.2%}'} | "
            f"{'—' if palette is None else f'{palette:.2%}'} | {worst} |"
        )
    scored = [r for r in rows if (r.get("scores") or {}).get("overall") is not None]
    if scored:
        mean = sum(r["scores"]["overall"] for r in scored) / len(scored)
        lines += ["", f"Mean across {len(scored)} scored state(s): **{mean:.2%}**"]
    failed = [r["id"] for r in rows if r["status"] != "scored" or not r.get("meets_threshold")]
    lines += ["", f"FAILED: {len(failed)} state(s): {', '.join(failed)}"
              if failed else "", "PASSED: every state is scored and at threshold."
              if not failed else ""]
    return "\n".join(lines).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch, capture, normalize and score app-vs-design states.")
    parser.add_argument("--exe", required=True, help="path to the built application binary")
    parser.add_argument("--launch-args", default="",
                        help="flag template; supports {page} {theme} {variant} {state}")
    parser.add_argument("--window-name", default=None,
                        help="process image name for window lookup (default: exe basename)")
    parser.add_argument("--window-title", default=None,
                        help="optional window-title substring filter")

    parser.add_argument("--page", default=None)
    parser.add_argument("--pages", default=None,
                        help="comma-separated page ids (overrides --page)")
    parser.add_argument("--theme", default=None)
    parser.add_argument("--themes", default=None,
                        help="comma-separated themes (overrides --theme)")
    parser.add_argument("--variant", default=None)
    parser.add_argument("--variants", default=None,
                        help="comma-separated variants (overrides --variant)")
    parser.add_argument("--state", default=None)
    parser.add_argument("--states", default=None,
                        help="comma-separated interaction states (overrides --state)")
    parser.add_argument("--all", action="store_true",
                        help="run the full cartesian product of pages x themes x variants x states")

    parser.add_argument("--design-root", default=".",
                        help="root folder containing the design frames")
    parser.add_argument("--design-pattern", default="{page}_{variant}/design_{theme}.png",
                        help="primary frame path template under --design-root")
    parser.add_argument("--fallback-pattern", default="{page}/design_{theme}.png",
                        help="fallback frame path template; pass '' to disable")

    parser.add_argument("--viewport", default="1280x800",
                        help="design canvas WxH (default 1280x800)")
    parser.add_argument("--chrome-crop", default="auto",
                        help="auto | flat | dark | none | <pixels> (default auto)")
    parser.add_argument("--fill", default="#F1F5F9",
                        help="canvas background for padded areas")
    parser.add_argument("--anchor", choices=["top", "center", "bottom"], default="top")

    parser.add_argument("--settle", type=float, default=3.0,
                        help="fixed settle delay after the window appears (default 3s)")
    parser.add_argument("--wait", type=float, default=25.0,
                        help="max wait for the main window (default 25s)")
    parser.add_argument("--min-area", type=int, default=200_000,
                        help="ignore helper windows below this pixel area")
    parser.add_argument("--kill-first", action="store_true", default=True,
                        help="kill stale instances before each launch (default on)")
    parser.add_argument("--no-kill-first", dest="kill_first", action="store_false")
    parser.add_argument("--keep-open", action="store_true",
                        help="leave the app running after each capture")

    parser.add_argument("--out-root", default="parity_out")
    parser.add_argument("--threshold", type=float, default=0.90,
                        help="pass threshold on the raw overall score (default 0.90)")
    parser.add_argument("--methods", default=None,
                        help="comma-separated subset for similarity.py methods")
    parser.add_argument("--regional-grid", type=int, default=6)
    parser.add_argument("--palette", type=int, default=8)
    parser.add_argument("--no-align", action="store_true",
                        help="skip the best-fit translation measurement")
    parser.add_argument("--max-shift-dy", type=int, default=160)
    parser.add_argument("--max-shift-dx", type=int, default=32)
    parser.add_argument("--json-out", default=None,
                        help="write the full run JSON here (default: <out-root>/results.json)")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    if sys.platform != "win32":
        print("ERROR: parity_run.py captures Windows windows (PrintWindow). "
              "On other platforms use the platform screenshot tool in the pipeline.",
              file=sys.stderr)
        return 2

    args.window_name = args.window_name or os.path.basename(args.exe)
    args.viewport = parse_px(args.viewport)
    methods = split_list(args.methods) or None

    pages = split_list(args.pages, [args.page] if args.page else None)
    themes = split_list(args.themes, [args.theme or "light"])
    variants = split_list(args.variants, [args.variant or "default"])
    states = split_list(args.states, [args.state or "default"])

    if not pages:
        parser.error("provide --page or --pages (or use --all with pages)")

    combos = [(p, t, v, s) for p in pages for t in themes
              for v in variants for s in states]

    os.makedirs(args.out_root, exist_ok=True)
    rows = []
    for page, theme, variant, state in combos:
        print(f"== {build_state_id(page, variant, theme, state)} ==")
        rows.append(run_state(args, page, theme, variant, state, args.out_root))

    report = md_report(rows, args.threshold)
    print(report)
    report_path = os.path.join(args.out_root, "report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(report)

    json_path = args.json_out or os.path.join(args.out_root, "results.json")
    out_dir = os.path.dirname(os.path.abspath(json_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"generated": dt.datetime.now().isoformat(timespec="seconds"),
                   "threshold": args.threshold, "states": rows},
                  fh, indent=2, ensure_ascii=False, default=str)
    print(f"Artifacts: {args.out_root}  report: {report_path}  json: {json_path}")

    failed = [r for r in rows if r["status"] != "scored" or not r.get("meets_threshold")]
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
