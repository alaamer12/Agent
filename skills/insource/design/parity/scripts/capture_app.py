#!/usr/bin/env python3
"""
capture_app.py — capture a running application window in mockup coordinate space.

The single hardest part of a window parity pipeline is turning a raw OS window
capture into a frame that shares a coordinate system with the design reference.
A raw ``PrintWindow`` bitmap contains:

  * the app's own title/caption band (the mockup has no window chrome at all),
  * an invisible DWM resize border on some frameworks,
  * a size that rarely matches the design viewport exactly.

``capture_app`` crops the chrome band using a *detected* boundary (never a blind
constant), then pads/centres the content onto an explicit canvas so every
downstream crop box means the same thing on both sides.

Chrome detection strategies (``--chrome-crop``):

  auto   try a flat-band scan first, then the dark-band scan (default)
  flat   first row that stops matching the title bar's dominant colour
  dark   leading majority-dark band (classic dark caption bars)
  none   keep the full window bitmap
  N      crop exactly N pixels (use only when the chrome height is proven stable)

Usage:
    python capture_app.py --name app.exe --output captures/app.png
    python capture_app.py --pid 12345 --output captures/app.png --target-size 1280x800
    python capture_app.py --title "My App" --chrome-crop 40 --fill "#0F172A"
    python capture_app.py --name app.exe --chrome-crop auto --target-size 1440x900 \
        --fill "#111827" --wait 2

Requirements: pywin32, pillow, psutil (via snip_tool).
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from snip_tool import (  # noqa: E402
    capture_window,
    find_target_windows,
    setup_logging,
)


# --------------------------------------------------------------------------- #
# Chrome detection
# --------------------------------------------------------------------------- #

def detect_dark_chrome_height(img: Image.Image, max_scan: int = 64,
                              dark_threshold: int = 45) -> int:
    """Height of a leading mostly-dark caption band.

    Caption buttons can be light islands, so a row counts as chrome only when a
    majority of sampled pixels are dark. A couple of mixed rows after the band
    are tolerated before the scan stops.
    """
    width, height = img.size
    limit = min(max_scan, height // 4)
    chrome = 0
    px = img.load()
    for y in range(limit):
        dark, samples = 0, 0
        step = max(1, width // 80)
        for x in range(0, width, step):
            r, g, b = px[x, y][:3]
            samples += 1
            if r < dark_threshold and g < dark_threshold and b < dark_threshold:
                dark += 1
        if samples and (dark / samples) >= 0.55:
            chrome = y + 1
        elif chrome > 0 and y > chrome + 2:
            break
    if chrome > 0:
        return min(height // 3, max(chrome, 28))
    return 0


def detect_flat_chrome_height(img: Image.Image, max_scan: int = 80,
                              tolerance: int = 12) -> int:
    """Height of a leading flat-colour band (light or dark title bars).

    Finds row 0's dominant colour, then walks down while each row still matches
    it. The first strongly different row is the app content. This is the more
    robust strategy for WinUI windows that draw their caption *inside* the
    client area.
    """
    width, height = img.size
    if not width or not height:
        return 0
    px = img.load()
    step = max(1, width // 60)

    def row_colors(y):
        return [px[x, y][:3] for x in range(0, width, step)]

    def close(a, b):
        return all(abs(int(x) - int(y)) <= tolerance for x, y in zip(a, b))

    base = row_colors(0)
    reference = max(set(base), key=base.count)
    last_flat = 0
    for y in range(1, min(max_scan, height // 4)):
        colors = row_colors(y)
        matching = sum(1 for c in colors if close(c, reference))
        if matching / len(colors) >= 0.6:
            last_flat = y
        elif last_flat:
            break
    return last_flat + 1 if last_flat else 0


def detect_chrome_height(img: Image.Image, mode: str = "auto") -> int:
    """Resolve ``--chrome-crop`` to a pixel count."""
    if mode == "none":
        return 0
    if mode.isdigit():
        return int(mode)
    if mode == "dark":
        return detect_dark_chrome_height(img)
    if mode == "flat":
        return detect_flat_chrome_height(img)
    if mode == "auto":
        flat = detect_flat_chrome_height(img)
        if flat:
            return flat
        return detect_dark_chrome_height(img)
    raise ValueError(f"Unknown chrome-crop mode: {mode}")


def crop_top(img: Image.Image, pixels: int) -> Image.Image:
    if pixels <= 0:
        return img
    return img.crop((0, min(pixels, img.height - 1), img.width, img.height))


# --------------------------------------------------------------------------- #
# Canvas normalisation
# --------------------------------------------------------------------------- #

def parse_fill(value: str) -> tuple[int, int, int]:
    """Accept ``#RRGGBB``, ``RRGGBB`` or ``r,g,b``."""
    value = value.strip()
    if "," in value:
        parts = [int(p) for p in value.split(",")]
        if len(parts) != 3:
            raise ValueError(f"fill must be r,g,b: {value}")
        return tuple(parts)  # type: ignore[return-value]
    hex_value = value.lstrip("#")
    if len(hex_value) != 6:
        raise ValueError(f"fill must be #RRGGBB or r,g,b: {value}")
    return (int(hex_value[0:2], 16), int(hex_value[2:4], 16), int(hex_value[4:6], 16))


def fit_canvas(img: Image.Image, size: tuple[int, int] | None,
               fill: tuple[int, int, int] = (241, 245, 249),
               anchor: str = "top") -> Image.Image:
    """Pad a chrome-cropped capture onto the design canvas.

    ``anchor`` controls vertical placement: ``top`` keeps the header at y=0
    (correct when the crop removed exactly the chrome), ``center`` is useful for
    floating dialogs, ``bottom`` for bottom-anchored shells.
    """
    if not size or size == (0, 0):
        return img
    target_w, target_h = size
    if img.size == (target_w, target_h):
        return img

    canvas = Image.new("RGB", (target_w, target_h), color=fill)
    paste_x = max(0, (target_w - img.width) // 2)
    if anchor == "center":
        paste_y = max(0, (target_h - img.height) // 2)
    elif anchor == "bottom":
        paste_y = max(0, target_h - img.height)
    else:
        paste_y = 0

    # Crop overflow instead of pasting outside the canvas.
    src = img.crop((0, 0, min(img.width, target_w), min(img.height, target_h - paste_y)))
    canvas.paste(src, (paste_x, paste_y))
    return canvas


def normalize_capture(img: Image.Image, chrome_mode: str = "auto",
                      target_size: tuple[int, int] | None = None,
                      fill: tuple[int, int, int] = (241, 245, 249),
                      anchor: str = "top") -> tuple[Image.Image, int]:
    """Chrome-crop + canvas-fit in one call. Returns ``(image, chrome_px)``."""
    chrome = detect_chrome_height(img, chrome_mode)
    cropped = crop_top(img, chrome)
    return fit_canvas(cropped, target_size, fill, anchor), chrome


# --------------------------------------------------------------------------- #
# Capture by target
# --------------------------------------------------------------------------- #

def capture_target(name: str | None = None, pid: int | None = None,
                   title: str | None = None, wait: float = 0.0,
                   flip: bool | None = None,
                   include_hidden: bool = False) -> tuple[Image.Image, dict]:
    """Find and capture the largest matching window. Raises ``SystemExit`` if none."""
    if wait > 0:
        time.sleep(wait)
    candidates = find_target_windows(name=name, pid=pid, title=title,
                                     include_hidden=include_hidden)
    if not candidates:
        raise SystemExit("No matching window found. Check --name/--pid/--title.")
    chosen = candidates[0]
    return capture_window(chosen["hwnd"], flip_override=flip), chosen


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture an app window, crop OS chrome, and fit a design canvas.")
    parser.add_argument("--name", help="process/executable name")
    parser.add_argument("--pid", type=int, help="exact process ID")
    parser.add_argument("--title", help="window-title substring")
    parser.add_argument("--output", required=True, help="output PNG path")
    parser.add_argument("--chrome-crop", default="auto",
                        help="auto | flat | dark | none | <pixels> (default: auto)")
    parser.add_argument("--target-size", default="none",
                        help="canvas WxH, or 'none' to keep the cropped size "
                             "(e.g. 1280x800)")
    parser.add_argument("--fill", default="#F1F5F9",
                        help="canvas background for padded areas (default: #F1F5F9)")
    parser.add_argument("--anchor", choices=["top", "center", "bottom"], default="top",
                        help="vertical placement of the capture on the canvas")
    parser.add_argument("--wait", type=float, default=0.0,
                        help="seconds to sleep before capturing")
    parser.add_argument("--include-hidden", action="store_true")
    flip = parser.add_mutually_exclusive_group()
    flip.add_argument("--flip-horizontal", action="store_true",
                      help="force a horizontal flip correction")
    flip.add_argument("--no-flip-fix", action="store_true",
                      help="disable the flip correction")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    setup_logging(debug=args.debug)

    target_size = None
    if args.target_size.lower() not in {"", "none", "0x0"}:
        if "x" not in args.target_size.lower():
            parser.error("--target-size must be WxH or 'none'")
        w, h = args.target_size.lower().split("x", 1)
        target_size = (int(w), int(h))

    flip = True if args.flip_horizontal else (False if args.no_flip_fix else None)
    image, chosen = capture_target(
        name=args.name, pid=args.pid, title=args.title,
        wait=args.wait, flip=flip, include_hidden=args.include_hidden,
    )
    original_size = image.size

    image, chrome = normalize_capture(
        image, chrome_mode=args.chrome_crop, target_size=target_size,
        fill=parse_fill(args.fill), anchor=args.anchor,
    )

    out_dir = os.path.dirname(os.path.abspath(args.output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    image.save(args.output)
    print(f"Saved: {args.output} ({image.width}x{image.height}) "
          f"chrome={chrome}px original={original_size[0]}x{original_size[1]} "
          f"window={chosen['title']!r} pid={chosen['pid']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
