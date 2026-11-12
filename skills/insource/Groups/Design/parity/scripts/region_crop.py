#!/usr/bin/env python3
"""
region_crop.py — crop an image by *named* region or explicit box.

The point of named regions is agreement: ``similarity.py --regional-score N``
reports numeric cells and the pixel box of each cell. If a crop tool uses its own
coordinate guesses, the crop you inspect is not the region that was scored. This
module reuses the exact same split rule (``np.array_split``) so a region name
means the same pixels in both scripts.

Layouts (``--region-layout``):

  3x3         top-left, top, top-right, mid-left, mid, mid-right,
              bottom-left, bottom, bottom-right      (default)
  3-columns   left, center, right
  3-rows      top, middle, bottom

``--box X,Y,W,H`` is an escape hatch for the worst-cell boxes printed by
``similarity.py`` or hand-picked boxes from a heatmap. It must not be mixed with
region selectors.

Usage:
    # what names exist for a layout?
    python region_crop.py --list-regions --region-layout 3x3

    # one named region
    python region_crop.py shot.png --region mid-left --out crop.png

    # several regions in one pass
    python region_crop.py shot.png --regions top-left,mid,bottom-right --out-dir crops/

    # every region of a layout
    python region_crop.py shot.png --all --region-layout 3-columns --out-dir crops/

    # same mask from the worst-cell box reported by similarity.py
    python region_crop.py shot.png --box 320,600,640,200 --out worst.png

    # expand a crop by 10% of its own size on each side
    python region_crop.py shot.png --region mid --margin-pct 10 --out crop.png

Requires: numpy, pillow
"""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image


# --------------------------------------------------------------------------- #
# Region layouts — identical names and split rule to similarity.py
# --------------------------------------------------------------------------- #

REGION_LAYOUTS = {
    "3x3": [
        ["top-left", "top", "top-right"],
        ["mid-left", "mid", "mid-right"],
        ["bottom-left", "bottom", "bottom-right"],
    ],
    "3-columns": [
        ["left", "center", "right"],
    ],
    "3-rows": [
        ["top"],
        ["middle"],
        ["bottom"],
    ],
}


def list_region_layouts() -> str:
    return "\n".join([
        "Available region layouts (use with --region-layout NAME):",
        "  3x3         - 3 rows x 3 columns (default): top-left...bottom-right",
        "  3-columns   - 1 row x 3 columns: left, center, right",
        "  3-rows      - 3 rows x 1 column: top, middle, bottom",
    ])


def list_regions(layout: str) -> str:
    labels_grid = REGION_LAYOUTS[layout]
    names = [label for row in labels_grid for label in row]
    lines = [f"Regions available for layout '{layout}':"]
    for row in labels_grid:
        lines.append("  " + ", ".join(row))
    lines.append(f"\n(use any of: {', '.join(names)})")
    return "\n".join(lines)


def region_bounds(h: int, w: int, layout: str) -> dict:
    """``{name: (y0, y1, x0, x1)}`` using ``np.array_split`` like similarity.py."""
    if layout not in REGION_LAYOUTS:
        raise ValueError(
            f"Unknown region layout '{layout}'. Available: {', '.join(REGION_LAYOUTS)}")
    labels_grid = REGION_LAYOUTS[layout]
    grid_rows, grid_cols = len(labels_grid), len(labels_grid[0])

    row_chunks = np.array_split(np.arange(h), grid_rows)
    col_chunks = np.array_split(np.arange(w), grid_cols)

    bounds = {}
    for r_idx, row_chunk in enumerate(row_chunks):
        y0, y1 = int(row_chunk[0]), int(row_chunk[-1]) + 1
        for c_idx, col_chunk in enumerate(col_chunks):
            x0, x1 = int(col_chunk[0]), int(col_chunk[-1]) + 1
            bounds[labels_grid[r_idx][c_idx]] = (y0, y1, x0, x1)
    return bounds


def crop_region(image: np.ndarray, region_name: str, layout: str = "3x3",
                margin_pct: float = 0.0) -> np.ndarray:
    """Crop ``image`` to a named region, optionally expanded by ``margin_pct``."""
    h, w = image.shape[:2]
    bounds = region_bounds(h, w, layout)

    if region_name not in bounds:
        raise ValueError(
            f"Unknown region '{region_name}' for layout '{layout}'. "
            f"Available: {', '.join(bounds.keys())}")

    y0, y1, x0, x1 = bounds[region_name]
    if margin_pct:
        dy = int((y1 - y0) * (margin_pct / 100.0))
        dx = int((x1 - x0) * (margin_pct / 100.0))
        y0, y1 = max(0, y0 - dy), min(h, y1 + dy)
        x0, x1 = max(0, x0 - dx), min(w, x1 + dx)

    return image[y0:y1, x0:x1]


def crop_box(image: np.ndarray, box: tuple[int, int, int, int],
             margin_pct: float = 0.0) -> np.ndarray:
    """Crop an explicit ``(x, y, w, h)`` box."""
    h, w = image.shape[:2]
    x, y, bw, bh = box
    if margin_pct:
        dx = int(bw * (margin_pct / 100.0))
        dy = int(bh * (margin_pct / 100.0))
        x, y, bw, bh = x - dx, y - dy, bw + 2 * dx, bh + 2 * dy
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(w, x + bw), min(h, y + bh)
    return image[y0:y1, x0:x1]


def parse_box(value: str) -> tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in value.split(",")]
    if len(parts) != 4:
        raise ValueError(f"--box expects X,Y,W,H, got: {value}")
    return tuple(parts)  # type: ignore[return-value]


def _safe_stem(path: str) -> str:
    stem, _ = os.path.splitext(os.path.basename(path))
    return stem


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Crop an image by named region or explicit box.")
    parser.add_argument("image", nargs="?", help="image to crop")
    parser.add_argument("--region-layout", default="3x3",
                        choices=list(REGION_LAYOUTS.keys()))
    parser.add_argument("--region", help="single region name, e.g. mid-left")
    parser.add_argument("--regions", help="comma-separated region names")
    parser.add_argument("--all", action="store_true", help="crop every region")
    parser.add_argument("--box", help="explicit X,Y,W,H box")
    parser.add_argument("--margin-pct", type=float, default=0.0)
    parser.add_argument("--out", metavar="PATH")
    parser.add_argument("--out-dir", metavar="DIR", default=".")
    parser.add_argument("--prefix", help="filename prefix for multi-region output")
    parser.add_argument("--list-regions", action="store_true")
    parser.add_argument("--list-layouts", action="store_true")
    args = parser.parse_args()

    if args.list_layouts:
        print(list_region_layouts())
        return 0
    if args.list_regions:
        print(list_regions(args.region_layout))
        return 0
    if not args.image:
        parser.error("image is required (unless using --list-regions/--list-layouts)")

    requested = sum(bool(x) for x in [args.region, args.regions, args.all, args.box])
    if requested == 0:
        parser.error("specify one of --region, --regions, --all, or --box")
    if requested > 1:
        parser.error("use only one of --region, --regions, --all, or --box")
    if args.box and args.out is None:
        parser.error("--box requires --out (single explicit crop)")

    try:
        img = np.array(Image.open(args.image).convert("RGB"))
    except FileNotFoundError:
        print(f"Error: file not found: {args.image}", file=sys.stderr)
        return 1

    h, w = img.shape[:2]
    ext = os.path.splitext(args.image)[1] or ".png"
    stem = args.prefix or _safe_stem(args.image)
    saved = []

    if args.box:
        crop = crop_box(img, parse_box(args.box), args.margin_pct)
        out_path = args.out
        out_dir = os.path.dirname(os.path.abspath(out_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        Image.fromarray(crop).save(out_path)
        saved.append(("box:" + args.box, out_path, crop.shape[1], crop.shape[0]))
    else:
        labels_grid = REGION_LAYOUTS[args.region_layout]
        all_names = [label for row in labels_grid for label in row]
        if args.all:
            targets = all_names
        elif args.regions:
            targets = [r.strip() for r in args.regions.split(",") if r.strip()]
        else:
            targets = [args.region]

        invalid = [r for r in targets if r not in all_names]
        if invalid:
            parser.error(
                f"Unknown region(s) for '{args.region_layout}': {', '.join(invalid)}. "
                f"Available: {', '.join(all_names)}")

        for region_name in targets:
            crop = crop_region(img, region_name, layout=args.region_layout,
                               margin_pct=args.margin_pct)
            if len(targets) == 1 and args.out:
                out_path = args.out
                out_dir = os.path.dirname(os.path.abspath(out_path))
                if out_dir:
                    os.makedirs(out_dir, exist_ok=True)
            else:
                os.makedirs(args.out_dir, exist_ok=True)
                out_path = os.path.join(args.out_dir, f"{stem}_{region_name}{ext}")
            Image.fromarray(crop).save(out_path)
            saved.append((region_name, out_path, crop.shape[1], crop.shape[0]))

    print(f"Source image: {args.image} ({w}x{h}), layout: {args.region_layout}")
    print("-" * 56)
    for region_name, out_path, cw, ch in saved:
        print(f"  {region_name:<14} -> {out_path}  ({cw}x{ch})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
