#!/usr/bin/env python3
"""
run_suite.py — drive a full parity matrix: mockups + app captures + scoring.

This is the orchestration layer above ``parity_run.py``. A single state is useful
for debugging; a suite is what proves the *whole product* stays in parity across
pages, themes, data variants and interaction states.

It adds three things a per-state run cannot do:

  * a real HTTP server for the mockup folder (query-param state forcing and
    relative assets need a URL, never ``file://``),
  * capture reliability (blank/splash detection, frame-stability checks,
    recapture with longer settle before a frame is ever scored),
  * two output modes:
      - ``--all``          score every state against its mockup,
      - ``--capture-only`` capture the app side into
                           ``<out>/<state>/app.png`` + ``manifest.json`` for
                           ``pixel_regression.py`` baseline/after runs.

Configuration
-------------
Everything product-specific lives in a JSON config (``--config``) or in flags.
Flags win over the config. Minimal config:

    {
      "exe": "build/app.exe",
      "window_name": "app.exe",
      "viewport": [1280, 800],
      "mockup_dir": "design",
      "launch_args": ["--page={page}", "--theme={theme}", "--state={state}"],
      "mockup_url_template": "{base}/{page}.html?theme={theme}&state={state}",
      "pages": ["home", "settings"],
      "themes": ["light", "dark"],
      "variants": ["default"],
      "states": ["default"],
      "splash_colors": [[255, 255, 255]]
    }

The full cartesian product is pages × themes × variants × states. To pin an
explicit list instead, provide ``matrix`` in the config:

    "matrix": [
      {"page": "home",   "theme": "light", "variant": "default", "state": "default"},
      {"page": "home",   "theme": "dark",  "variant": "default", "state": "filters-open"}
    ]

Optional keys: ``blank_std`` (3.0), ``blank_dominant`` (0.985), ``settle`` (5.0),
``min_area`` (200000), ``storage`` ({"theme": "{theme}"}), ``fill`` ("#F1F5F9"),
``chrome_crop`` ("auto"), ``threshold`` (0.90).

Usage:
    python run_suite.py --config parity.json --all
    python run_suite.py --config parity.json --page home --theme dark
    python run_suite.py --config parity.json --all --update-baseline
    python run_suite.py --config parity.json --all --capture-only --out after/
    python run_suite.py --config parity.json --all --capture-only --out baseline/

Exit codes: 0 = every state scored at/above threshold (or captured in
capture-only mode); 1 = a blank/unstable capture, an error, or a below-threshold
score.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import glob
import json
import os
import shlex
import socket
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_app import normalize_capture, parse_fill  # noqa: E402
from capture_mockup import capture as capture_mockup  # noqa: E402
from similarity import run_comparison  # noqa: E402
from snip_tool import (  # noqa: E402
    capture_window,
    find_target_windows,
    setup_logging,
)


# --------------------------------------------------------------------------- #
# Config + state matrix
# --------------------------------------------------------------------------- #

DEFAULTS = {
    "window_name": None,
    "viewport": [1280, 800],
    "mockup_dir": "design",
    "launch_args": [],
    "mockup_url_template": "{base}/{page}.html?theme={theme}{variant_query}{state_query}",
    "pages": [],
    "themes": ["light", "dark"],
    "variants": ["default"],
    "states": ["default"],
    "matrix": None,
    "splash_colors": [],
    "storage": {},
    "blank_std": 3.0,
    "blank_dominant": 0.985,
    "settle": 5.0,
    "min_area": 200_000,
    "fill": "#F1F5F9",
    "chrome_crop": "auto",
    "threshold": 0.90,
}


def load_config(path: str | None) -> dict:
    config = dict(DEFAULTS)
    if path:
        with open(path, encoding="utf-8") as fh:
            config.update(json.load(fh))
    return config


def split_list(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def build_states(config: dict) -> list[dict]:
    explicit = config.get("matrix")
    if explicit:
        return [
            {"page": s["page"], "theme": s.get("theme", "light"),
             "variant": s.get("variant", "default"),
             "state": s.get("state", "default")}
            for s in explicit
        ]
    return [
        {"page": page, "theme": theme, "variant": variant, "state": state}
        for page in config["pages"]
        for theme in config["themes"]
        for variant in config["variants"]
        for state in config["states"]
    ]


def state_id(state: dict) -> str:
    sid = f"{state['page']}__{state['variant']}__{state['theme']}"
    if state.get("state") and state["state"] != "default":
        sid += f"__{state['state']}"
    return sid


def substitute(template: str, state: dict, base: str = "") -> str:
    variant = state.get("variant", "default")
    return (template
            .replace("{base}", base.rstrip("/"))
            .replace("{page}", state["page"])
            .replace("{theme}", state["theme"])
            .replace("{variant}", variant)
            .replace("{state}", state.get("state", "default"))
            .replace("{variant_query}", "" if variant in {"", "default"}
                     else f"&variant={variant}")
            .replace("{state_query}", "" if state.get("state", "default") == "default"
                     else f"&state={state['state']}"))


# --------------------------------------------------------------------------- #
# Mockup server
# --------------------------------------------------------------------------- #

def free_port() -> int:
    with contextlib.closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def mockup_server(directory: str):
    """Serve ``directory`` on a free localhost port; yields the base URL."""
    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1",
         "--directory", directory],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with contextlib.closing(socket.create_connection(("127.0.0.1", port), 0.4)):
                    break
            except OSError:
                time.sleep(0.2)
        yield f"http://127.0.0.1:{port}"
    finally:
        proc.terminate()
        with contextlib.suppress(Exception):
            proc.wait(timeout=5)


# --------------------------------------------------------------------------- #
# Process control
# --------------------------------------------------------------------------- #

def _taskkill(args: list[str]) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill"] + args, capture_output=True, text=True)


def kill_by_name(window_name: str, timeout: float = 12.0) -> None:
    if os.name != "nt":
        return
    _taskkill(["/IM", window_name, "/F"])
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not find_target_windows(name=window_name):
            return
        _taskkill(["/IM", window_name, "/F"])
        time.sleep(0.5)


def launch(exe: str, tokens: list[str], env_extra: dict | None = None) -> subprocess.Popen:
    env = dict(os.environ, **(env_extra or {}))
    return subprocess.Popen([exe] + tokens, cwd=os.path.dirname(os.path.abspath(exe)), env=env)


def find_app_window(pid: int, window_name: str, min_area: int) -> dict | None:
    own = [w for w in find_target_windows(name=window_name)
           if w["pid"] == pid and w["area"] > min_area]
    if own:
        return max(own, key=lambda w: w["area"])
    others = [w for w in find_target_windows(name=window_name) if w["area"] > min_area]
    return max(others, key=lambda w: w["area"]) if others else None


# --------------------------------------------------------------------------- #
# Capture reliability
# --------------------------------------------------------------------------- #

def is_blank(img: Image.Image, std_threshold: float = 3.0,
             dominant_threshold: float = 0.985) -> bool:
    arr = np.asarray(img.convert("L"), dtype=np.float64)
    if float(arr.std()) < std_threshold:
        return True
    small = img.resize((max(1, img.width // 2), max(1, img.height // 2))).convert("RGB")
    rgb = np.asarray(small)
    colors, counts = np.unique(rgb.reshape(-1, 3), axis=0, return_counts=True)
    dominant = float(counts.max()) / float(counts.sum()) if len(counts) else 1.0
    return dominant > dominant_threshold


def is_flat_splash(img: Image.Image, splash_colors: list, tolerance: int = 18) -> bool:
    """True when at least 3 of 4 corners match a declared splash colour."""
    if not splash_colors:
        return False
    rgb = img.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    corners = [px[4, 4], px[w - 5, 4], px[4, h - 5], px[w - 5, h - 5]]

    def close(color, expected):
        return all(abs(int(a) - int(b)) <= tolerance for a, b in zip(color, expected))

    return sum(1 for color in corners
               if any(close(color, expected) for expected in splash_colors)) >= 3


def frames_stable(a: Image.Image, b: Image.Image, threshold: float = 2.0) -> bool:
    ga = np.asarray(a.convert("L").resize((320, 200)), dtype=np.int16)
    gb = np.asarray(b.convert("L").resize((320, 200)), dtype=np.int16)
    return float(np.abs(ga - gb).mean()) < threshold


def client_box_in_capture(hwnd: int) -> tuple[int, int, int, int] | None:
    """Client rectangle inside a PrintWindow bitmap (derived from sizes)."""
    try:
        import win32gui

        wl, wt, wr, wb = win32gui.GetWindowRect(hwnd)
        client = win32gui.GetClientRect(hwnd)
        cw, ch = client[2], client[3]
        if cw <= 0 or ch <= 0 or cw > wr - wl or ch > wb - wt:
            return None
        inset_x = (wr - wl - cw) // 2
        return inset_x, 0, inset_x + cw, ch
    except Exception:
        return None


def _trim_dark_borders(img: Image.Image, max_trim: int = 12) -> Image.Image:
    """Remove uniform near-black DWM resize-border strips from a capture."""
    arr = np.asarray(img.convert("L"))
    left = right = bottom = 0
    for x in range(max_trim):
        if arr[:, x].mean() < 12:
            left = x + 1
        else:
            break
    for x in range(max_trim):
        if arr[:, arr.shape[1] - 1 - x].mean() < 12:
            right = x + 1
        else:
            break
    for y in range(max_trim):
        if arr[arr.shape[0] - 1 - y, left:arr.shape[1] - right or None].mean() < 12:
            bottom = y + 1
        else:
            break
    if not (left or right or bottom):
        return img
    return img.crop((left, 0, img.width - right, img.height - bottom))


def normalize_app(raw: Image.Image, hwnd: int, viewport: tuple[int, int],
                  chrome_crop: str, fill: tuple[int, int, int]) -> tuple[Image.Image, dict]:
    """Crop to the client rect (when measurable), remove chrome, fit the canvas."""
    info: dict = {}
    box = client_box_in_capture(hwnd)
    if box is not None:
        client = raw.crop(box)
        info["crop_method"] = "client-rect"
        info["client_box_px"] = list(box)
        content = _trim_dark_borders(client)
    else:
        content = _trim_dark_borders(raw)
        info["crop_method"] = "window-bitmap"

    normalized, chrome = normalize_capture(
        content, chrome_mode=chrome_crop, target_size=viewport, fill=fill,
    )
    info["chrome_crop_px"] = chrome
    info["content_size_px"] = [content.width, content.height]
    return normalized, info


def capture_app_state(config: dict, state: dict, exe: str, window_name: str,
                      out_png: str, log) -> tuple[bool, dict]:
    """Launch one app state and capture it, with blank/splash retries."""
    tokens = [substitute(token, state) for token in config["launch_args"]]
    viewport = tuple(config["viewport"])
    fill = parse_fill(config["fill"])
    min_area = int(config["min_area"])
    settle = float(config["settle"])
    meta: dict = {"flags": tokens, "retries": 0}

    for attempt in range(3):
        kill_by_name(window_name)
        proc = launch(exe, tokens, config.get("env"))
        try:
            deadline = time.time() + 25 + settle + 20 * attempt
            window = None
            while time.time() < deadline:
                time.sleep(1.0)
                window = find_app_window(proc.pid, window_name, min_area)
                if window:
                    break
                if proc.poll() is not None:
                    break

            if not window:
                meta["retries"] = attempt + 1
                log(f"  attempt {attempt + 1}: no window found")
                continue

            budget = settle + 15.0 + 15.0 * attempt
            deadline = time.time() + budget
            normalized = None
            while time.time() < deadline:
                time.sleep(2.5)
                window = find_app_window(proc.pid, window_name, min_area) or window
                try:
                    first = capture_window(window["hwnd"])
                    n1, info = normalize_app(first, window["hwnd"], viewport,
                                             config["chrome_crop"], fill)
                    time.sleep(2.5)
                    window2 = find_app_window(proc.pid, window_name, min_area) or window
                    n2, _ = normalize_app(capture_window(window2["hwnd"]),
                                          window2["hwnd"], viewport,
                                          config["chrome_crop"], fill)
                except Exception:
                    continue
                if first.size[1] < 600:
                    continue
                meta.update(info)
                meta["window_size"] = [first.width, first.height]
                if (frames_stable(n1, n2)
                        and not is_blank(n2, config["blank_std"], config["blank_dominant"])
                        and not is_flat_splash(n2, config["splash_colors"])):
                    normalized = n2
                    break

            if normalized is None:
                meta["retries"] = attempt + 1
                log(f"  attempt {attempt + 1}: splash/blank/unstable, retrying")
                continue

            out_dir = os.path.dirname(os.path.abspath(out_png))
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            normalized.save(out_png)
            meta["retries"] = attempt
            return True, meta
        finally:
            _taskkill(["/PID", str(proc.pid), "/T", "/F"])
            if os.name == "nt":
                for _ in range(8):
                    if not find_target_windows(name=window_name):
                        break
                    time.sleep(0.4)
    return False, meta


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #

def structure_similarity(design: str, app: str, tmp_dir: str) -> dict:
    """Gaussian-blurred structural blend: renderer noise separated from bugs."""
    paths = []
    try:
        for src, tag in ((design, "m"), (app, "a")):
            path = os.path.join(tmp_dir, f"_struct_{tag}.png")
            Image.open(src).convert("RGB").filter(ImageFilter.GaussianBlur(1.0)).save(path)
            paths.append(path)
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
            with contextlib.suppress(OSError):
                os.remove(path)


def score_pair(design: str, app: str, heatmap: str, config: dict) -> dict:
    report = run_comparison(
        design, app,
        resize_mode="pad",
        region_report=False,
        heatmap_out=heatmap,
        regional_score=4,
        palette=8,
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
        "regional_mean": float(np.mean(flat)) if flat else None,
        "worst4": [c["similarity"] for c in (grid.get("worst") or [])[:4]],
        "meets_threshold": (data.get("overall_similarity") or 0) >= config["threshold"],
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def md_table(rows: list[dict], config: dict) -> str:
    lines = [
        "# Parity suite",
        "",
        f"Run: {rows[0]['run'] if rows else '?'} | "
        f"frame {config['viewport'][0]}x{config['viewport'][1]} | "
        f"threshold {config['threshold']:.0%}",
        "",
        "| state | page | variant | theme | ItC state | raw | structure | palette | worst 4 | status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        scores = row.get("scores") or {}
        structure = row.get("structure") or {}
        raw = scores.get("overall")
        st = structure.get("overall")
        palette = scores.get("palette_similarity")
        worst = ", ".join(f"{v:.2f}" for v in (scores.get("worst4") or [])) or "—"
        status = ("BLANK" if row.get("blank") else
                  "ERROR" if row.get("error") else
                  "OK" if row.get("meets_threshold") else "LOW")
        lines.append(
            f"| {row['id']} | {row['page']} | {row['variant']} | {row['theme']} | "
            f"{row['state']} | "
            f"{'—' if raw is None else f'{raw:.2%}'} | "
            f"{'—' if st is None else f'{st:.2%}'} | "
            f"{'—' if palette is None else f'{palette:.2%}'} | {worst} | {status} |"
        )
    scored = [r for r in rows if (r.get("scores") or {}).get("overall") is not None]
    if scored:
        mean = float(np.mean([r["scores"]["overall"] for r in scored]))
        lines += ["", f"Mean across {len(scored)} scored state(s): **{mean:.2%}**"]
    failed = [r["id"] for r in rows if r["status"] != "scored"]
    lines += ["", f"FAILED: {len(failed)} state(s): {', '.join(failed)}"
              if failed else "",
              "PASSED: every state scored." if not failed else ""]
    return "\n".join(lines).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# Modes
# --------------------------------------------------------------------------- #

def run_states(config: dict, states: list[dict], exe: str, window_name: str,
               out_root: str, log) -> list[dict]:
    run_dir = os.path.join(out_root, dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(run_dir, exist_ok=True)
    rows: list[dict] = []

    server = (contextlib.nullcontext(config["base_url"])
              if config.get("base_url") else mockup_server(config["mockup_dir"]))

    with server as base_url:
        log(f"mockup server: {base_url}")
        for state in states:
            sid = state_id(state)
            log(f"== {sid} ==")
            entry = {**state, "id": sid, "run": os.path.basename(run_dir),
                     "blank": False, "scores": None, "status": "pending"}
            mock_png = os.path.join(run_dir, f"{sid}__mockup.png")
            app_png = os.path.join(run_dir, f"{sid}__app.png")
            heat_png = os.path.join(run_dir, f"{sid}__diff.png")
            try:
                capture_mockup(
                    url=substitute(config["mockup_url_template"], state, base_url),
                    output=mock_png,
                    width=config["viewport"][0], height=config["viewport"][1],
                    full_page=False, wait_ms=1200, theme=state["theme"],
                    device_scale_factor=1.0, reduced_motion=True,
                    storage={k: substitute(v, state, base_url)
                             for k, v in (config.get("storage") or {}).items()},
                )
                entry["mockup"] = os.path.relpath(mock_png, os.getcwd())
                ok, meta = capture_app_state(config, state, exe, window_name,
                                             app_png, log)
                entry["app_meta"] = meta
                if not ok:
                    entry["blank"] = True
                    entry["status"] = "blank"
                    rows.append(entry)
                    log(f"  {sid}: BLANK after retries — not scored")
                    continue
                entry["app"] = os.path.relpath(app_png, os.getcwd())
                entry["scores"] = score_pair(mock_png, app_png, heat_png, config)
                entry["structure"] = structure_similarity(mock_png, app_png, run_dir)
                entry["meets_threshold"] = entry["scores"].get("meets_threshold", False)
                entry["status"] = "scored"
                log(f"  raw {entry['scores']['overall']:.2%} "
                    f"structure {(entry['structure']['overall'] or 0):.2%} "
                    f"palette {(entry['scores']['palette_similarity'] or 0):.2%}")
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
                entry["status"] = "error"
                log(f"  ERROR: {entry['error']}")
            rows.append(entry)

    with open(os.path.join(run_dir, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False, default=str)
    report = md_table(rows, config)
    with open(os.path.join(run_dir, "report.md"), "w", encoding="utf-8") as fh:
        fh.write(report)
    print(report)
    log(f"artifacts: {run_dir}")
    return rows


def git_commit(path: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=path,
            capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "?"


def run_capture_only(config: dict, states: list[dict], exe: str,
                     window_name: str, out_dir: str, log) -> list[dict]:
    """Capture the app side only: ``<out>/<state>/app.png`` + manifest."""
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for state in states:
        sid = state_id(state)
        state_dir = os.path.join(out_dir, sid)
        os.makedirs(state_dir, exist_ok=True)
        app_png = os.path.join(state_dir, "app.png")
        log(f"== {sid} ==")
        try:
            ok, meta = capture_app_state(config, state, exe, window_name, app_png, log)
        except Exception as exc:
            ok, meta = False, {"error": f"{type(exc).__name__}: {exc}"}
        results.append({**state, "id": sid, "ok": ok, "app_png": app_png, "meta": meta})
        log(f"  {'captured' if ok else 'FAILED'}")

    manifest = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "exe": exe,
        "exe_mtime": (dt.datetime.fromtimestamp(os.path.getmtime(exe))
                      .isoformat(timespec="seconds") if os.path.exists(exe) else None),
        "git_commit": git_commit(os.path.dirname(os.path.abspath(exe))),
        "settle_s": config["settle"],
        "frame": list(config["viewport"]),
        "states": results,
    }
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False, default=str)

    failed = [r["id"] for r in results if not r["ok"]]
    if failed:
        log(f"capture gate: {len(failed)} failed state(s): {', '.join(failed)}")
    else:
        log(f"captured {len(results)} states -> {out_dir}")
    return results


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a full parity matrix (mockups + app + scoring).")
    parser.add_argument("--config", default=None, help="JSON matrix config")
    parser.add_argument("--exe", default=None, help="application binary path")
    parser.add_argument("--window-name", default=None,
                        help="process image name for window lookup")
    parser.add_argument("--mockup-dir", default=None, help="folder to serve as mockups")
    parser.add_argument("--base-url", default=None,
                        help="use an already-running server instead of starting one")
    parser.add_argument("--viewport", default=None, help="canvas WxH")
    parser.add_argument("--launch-args", default=None,
                        help="launch template; supports {page} {theme} {variant} {state}")
    parser.add_argument("--mockup-url-template", default=None,
                        help="URL template for the mockup page")
    parser.add_argument("--pages", default=None, help="comma-separated page ids")
    parser.add_argument("--themes", default=None, help="comma-separated themes")
    parser.add_argument("--variants", default=None, help="comma-separated variants")
    parser.add_argument("--states", default=None, help="comma-separated ItC states")
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--settle", type=float, default=None)

    parser.add_argument("--all", action="store_true", help="run every matrix state")
    parser.add_argument("--page", default=None, help="run one page (with --theme/--variant/--state)")
    parser.add_argument("--theme", default=None)
    parser.add_argument("--variant", default=None)
    parser.add_argument("--state", default=None)

    parser.add_argument("--capture-only", action="store_true",
                        help="capture app frames only (no mockups/scoring)")
    parser.add_argument("--out", default=None, help="output directory")
    parser.add_argument("--out-root", default="parity_out")
    parser.add_argument("--update-baseline", action="store_true",
                        help="copy the latest report.md to <out-root>/baseline.md")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    if sys.platform != "win32":
        print("ERROR: run_suite.py captures Windows windows. "
              "Use the platform screenshot path in the pipeline elsewhere.",
              file=sys.stderr)
        return 2

    config = load_config(args.config)
    if isinstance(config.get("launch_args"), str):
        config["launch_args"] = shlex.split(config["launch_args"])

    # Flags override config.
    if args.exe:
        config["exe"] = args.exe
    if args.window_name:
        config["window_name"] = args.window_name
    if args.mockup_dir:
        config["mockup_dir"] = args.mockup_dir
    if args.base_url:
        config["base_url"] = args.base_url
    if args.viewport:
        w, h = args.viewport.lower().split("x", 1)
        config["viewport"] = [int(w), int(h)]
    if args.launch_args is not None:
        config["launch_args"] = shlex.split(args.launch_args)
    if args.mockup_url_template:
        config["mockup_url_template"] = args.mockup_url_template
    if args.pages:
        config["pages"] = split_list(args.pages)
    if args.themes:
        config["themes"] = split_list(args.themes)
    if args.variants:
        config["variants"] = split_list(args.variants)
    if args.states:
        config["states"] = split_list(args.states)
    if args.threshold is not None:
        config["threshold"] = args.threshold
    if args.settle is not None:
        config["settle"] = args.settle

    if not config.get("exe"):
        parser.error("provide --exe or set 'exe' in --config")
        return 2
    exe = config["exe"]
    window_name = config.get("window_name") or os.path.basename(exe)
    config["window_name"] = window_name

    if not os.path.exists(exe):
        print(f"ERROR: binary not found: {exe}", file=sys.stderr)
        return 2

    states = build_states(config)
    if args.page:
        states = [{"page": args.page, "theme": args.theme or "light",
                   "variant": args.variant or "default",
                   "state": args.state or "default"}]
    if not states:
        parser.error("no states resolved; set pages/matrix in --config or --pages")
        return 2

    log = lambda msg: print(msg, flush=True)  # noqa: E731

    if args.capture_only:
        out_dir = args.out or os.path.join(args.out_root, "capture")
        results = run_capture_only(config, states, exe, window_name, out_dir, log)
        return 0 if all(r["ok"] for r in results) else 1

    rows = run_states(config, states, exe, window_name, args.out_root, log)

    if args.update_baseline:
        latest = max(glob.glob(os.path.join(args.out_root, "*", "report.md")),
                     key=os.path.getmtime, default=None)
        if latest:
            with open(latest, encoding="utf-8") as fh:
                content = fh.read()
            with open(os.path.join(args.out_root, "baseline.md"), "w",
                      encoding="utf-8") as fh:
                fh.write(content)
            log(f"baseline written: {os.path.join(args.out_root, 'baseline.md')}")

    failed = [r["id"] for r in rows if r["status"] != "scored" or not r.get("meets_threshold")]
    if failed:
        log(f"acceptance gate: {len(failed)} state(s) failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
