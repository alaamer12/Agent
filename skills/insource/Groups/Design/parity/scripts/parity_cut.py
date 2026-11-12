#!/usr/bin/env python3
"""
parity_cut.py — compare named sub-regions of a design frame and an app frame.

A full-frame score tells you a screen is 71% similar. A region cut tells you
*which component* is responsible, at the exact same coordinates on both sides.
This is the tool for "the header card is wrong but the feed is fine": define the
boxes once, get a side-by-side pair plus a scored heatmap per box.

Both sides must already share a coordinate system (same client size). If you
pass live inputs, the design is captured with ``capture_mockup`` at the client
viewport and the app window is captured and cropped to its client rectangle
before chrome removal, so a box means the same pixels on both sides.

Regions
-------
Provide boxes as JSON and/or repeated flags:

    regions.json:
    {
      "header_card": [1120, 0, 1280, 104],
      "search_row":  [64, 104, 1028, 184],
      "side_panel":  [1020, 104, 1280, 800]
    }

    --regions-file regions.json
    --region header_card:1120,0,160,104

Boxes are ``X,Y,W,H`` in client space. ``--all-grid N`` compares every cell of
an NxN grid instead (useful as a first pass when nothing is named yet).

Usage:
    python parity_cut.py --design-image design.png --app-image app.png \
        --regions-file regions.json --out cuts/
    python parity_cut.py --url http://localhost:8000/home.html --theme dark \
        --window-name app.exe --regions-file regions.json --out cuts/
    python parity_cut.py --design-image design.png --app-image app.png \
        --all-grid 4 --out cuts/

Exit codes: 0 always after writing artifacts (this is a diagnostic, not a gate).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_app import normalize_capture, parse_fill  # noqa: E402
from capture_mockup import capture as capture_design  # noqa: E402
from similarity import run_comparison  # noqa: E402
from snip_tool import (  # noqa: E402
    capture_window,
    find_target_windows,
    setup_logging,
)


def parse_px(value: str) -> tuple[int, int]:
    if "x" not in value.lower():
        raise SystemExit(f"expected WxH, got: {value}")
    w, h = value.lower().split("x", 1)
    return int(w), int(h)


def parse_region(value: str) -> tuple[str, tuple[int, int, int, int]]:
    if ":" not in value:
        raise SystemExit(f"--region expects name:x,y,w,h, got: {value}")
    name, box = value.split(":", 1)
    parts = [int(p.strip()) for p in box.split(",")]
    if len(parts) != 4:
        raise SystemExit(f"--region expects name:x,y,w,h, got: {value}")
    return name.strip(), tuple(parts)  # type: ignore[return-value]


def load_regions(path: str) -> dict[str, list[int]]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain an object of name -> [x,y,w,h]")
    return data


def grid_regions(size: tuple[int, int], grid: int) -> dict[str, list[int]]:
    w, h = size
    regions = {}
    for row in range(grid):
        for col in range(grid):
            regions[f"r{row}c{col}"] = [
                int(w * col / grid), int(h * row / grid),
                int(w / grid), int(h / grid),
            ]
    return regions


def make_pair(design: Image.Image, app: Image.Image, path: str) -> None:
    gap, label_h = 12, 22
    pair = Image.new("RGB", (design.width * 2 + gap, design.height + label_h),
                     (241, 245, 249))
    pair.paste(design, (0, label_h))
    pair.paste(app, (design.width + gap, label_h))
    draw = ImageDraw.Draw(pair)
    draw.text((6, 5), "DESIGN", fill=(15, 23, 42))
    draw.text((design.width + gap + 6, 5), "APP", fill=(15, 23, 42))
    pair.save(path)


# --------------------------------------------------------------------------- #
# Live app capture (client rectangle)
# --------------------------------------------------------------------------- #

def client_box_in_capture(hwnd: int) -> tuple[int, int, int, int] | None:
    """Client rectangle inside a PrintWindow bitmap, in capture pixels.

    Derived from the window/client size difference. ``ClientToScreen`` is not
    used because RTL-layout windows mirror the point it returns.
    """
    try:
        import win32gui

        wl, wt, wr, wb = win32gui.GetWindowRect(hwnd)
        client = win32gui.GetClientRect(hwnd)
        cw, ch = client[2], client[3]
        if cw <= 0 or ch <= 0 or cw > wr - wl or ch > wb - wt:
            return None
        inset_x = (wr - wl - cw) // 2
        inset_y = wb - wt - ch
        return inset_x, 0, inset_x + cw, ch
    except Exception:
        return None


def capture_app_client(window_name: str | None, pid: int | None,
                       client_size: tuple[int, int], chrome_mode: str,
                       fill: tuple[int, int, int]) -> Image.Image:
    candidates = find_target_windows(name=window_name, pid=pid)
    if not candidates:
        raise SystemExit("No matching app window found. Launch the app first.")
    hwnd = candidates[0]["hwnd"]

    try:
        import win32gui

        win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
        time.sleep(0.4)
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        cr = win32gui.GetClientRect(hwnd)
        border_x = (r - l) - cr[2]
        border_y = (b - t) - cr[3]
        win32gui.SetWindowPos(
            hwnd, 0, l, t,
            client_size[0] + border_x, client_size[1] + border_y,
            0x0004 | 0x0010,  # SWP_NOZORDER | SWP_NOACTIVATE
        )
        time.sleep(0.8)
    except Exception as exc:  # pragma: no cover - window manager differences
        print(f"WARN: could not size the window exactly: {exc}", file=sys.stderr)

    img = capture_window(hwnd)
    box = client_box_in_capture(hwnd)
    if box is not None:
        img = img.crop(box)
    normalized, _ = normalize_capture(img, chrome_mode=chrome_mode,
                                      target_size=client_size, fill=fill)
    return normalized


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare named regions of a design frame and an app frame.")
    parser.add_argument("--design-image", help="reuse an existing design frame")
    parser.add_argument("--app-image", help="reuse an existing app frame")
    parser.add_argument("--url", help="design page URL to capture live")
    parser.add_argument("--theme", choices=["light", "dark"], default="light")
    parser.add_argument("--variant", default="default")
    parser.add_argument("--set-storage", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--init-js", action="append", default=[], metavar="JS")
    parser.add_argument("--dpr", type=float, default=1.0)
    parser.add_argument("--reduced-motion", action="store_true")
    parser.add_argument("--wait-ms", type=int, default=700)

    parser.add_argument("--window-name", help="app process image name")
    parser.add_argument("--pid", type=int, help="app process id")
    parser.add_argument("--client-size", default="1280x800",
                        help="shared client coordinate space (default 1280x800)")
    parser.add_argument("--chrome-crop", default="auto",
                        help="auto | flat | dark | none | <pixels>")
    parser.add_argument("--fill", default="#F1F5F9")

    parser.add_argument("--regions-file", help="JSON object of name -> [x,y,w,h]")
    parser.add_argument("--region", action="append", default=[],
                        metavar="NAME:X,Y,W,H", help="inline region (repeatable)")
    parser.add_argument("--all-grid", type=int, default=None,
                        help="compare every cell of an NxN grid instead")
    parser.add_argument("--out", default="parity_cuts", help="output directory")

    parser.add_argument("--methods", default="ssim,histogram,hash")
    parser.add_argument("--regional-grid", type=int, default=4,
                        help="inner grid used to localise within each region")
    parser.add_argument("--palette", type=int, default=8)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    setup_logging(debug=args.debug)
    client_size = parse_px(args.client_size)
    fill = parse_fill(args.fill)
    os.makedirs(args.out, exist_ok=True)

    if args.design_image:
        design = Image.open(args.design_image).convert("RGB")
    elif args.url:
        design_path = os.path.join(args.out, f"design_full_{args.theme}.png")
        storage = {}
        for item in args.set_storage:
            if "=" in item:
                k, v = item.split("=", 1)
                storage[k] = v
        capture_design(
            url=args.url, output=design_path,
            width=client_size[0], height=client_size[1],
            full_page=False, wait_ms=args.wait_ms, theme=args.theme,
            device_scale_factor=args.dpr, reduced_motion=args.reduced_motion,
            init_scripts=args.init_js, storage=storage,
        )
        design = Image.open(design_path).convert("RGB")
    else:
        parser.error("provide --design-image or --url")
        return 2

    if args.app_image:
        app = Image.open(args.app_image).convert("RGB")
    elif args.window_name or args.pid:
        app = capture_app_client(args.window_name, args.pid, client_size,
                                 args.chrome_crop, fill)
        app.save(os.path.join(args.out, "app_full.png"))
    else:
        parser.error("provide --app-image or --window-name/--pid")
        return 2

    if design.size != client_size:
        design = design.resize(client_size, Image.LANCZOS)
    if app.size != client_size:
        app = app.resize(client_size, Image.LANCZOS)
    print(f"design={design.size} app={app.size}")

    regions: dict[str, list[int]] = {}
    if args.regions_file:
        regions.update(load_regions(args.regions_file))
    for value in args.region:
        name, box = parse_region(value)
        regions[name] = list(box)
    if args.all_grid:
        regions.update(grid_regions(client_size, args.all_grid))
    if not regions:
        parser.error("provide --regions-file, --region, or --all-grid N")
        return 2

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    summary = []
    for name, box in regions.items():
        x, y, w, h = box
        crop = (x, y, x + w, y + h)
        d = design.crop(crop)
        a = app.crop(crop)
        d_path = os.path.join(args.out, f"design_{name}.png")
        a_path = os.path.join(args.out, f"app_{name}.png")
        d.save(d_path)
        a.save(a_path)
        make_pair(d, a, os.path.join(args.out, f"pair_{name}.png"))

        report = run_comparison(
            d_path, a_path,
            resize_mode="stretch",
            methods=methods,
            region_report=False,
            regional_score=args.regional_grid,
            palette=args.palette,
            heatmap_out=os.path.join(args.out, f"heatmap_{name}.png"),
        )
        ssim = report.scores.get("ssim", 0.0)
        ssim = ssim if isinstance(ssim, (int, float)) else 0.0
        palette = (report.palette_report or {}).get("palette_similarity", 0.0)
        cell = {
            "name": name, "box": box,
            "overall": report.overall_score, "ssim": ssim, "palette": palette,
            "worst": (report.regional_score_grid or {}).get("worst", [])[:3],
        }
        summary.append(cell)
        print(f"\n== {name} {tuple(box)} ==")
        print(f"overall={report.overall_score:.4f} ssim={ssim:.4f} palette={palette:.4f}")
        for worst in cell["worst"]:
            print(f"  worst r{worst['row']}c{worst['col']} "
                  f"sim={worst['similarity']:.3f} box={worst['box']}")

    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    print(f"\nArtifacts: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
