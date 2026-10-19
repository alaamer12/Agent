"""Capture a running desktop app window (Windows), optionally cropping the title-bar chrome.

Useful for comparing a real app against an HTML mockup that has no window chrome.
Uses the bundled `winshot` module (PrintWindow, so it works even if the window is covered).
Requires Windows + `pip install pywin32 psutil pillow`.

Usage:
  python page.py --list                                   # visible windows, largest first
  python page.py --name MyApp.exe --list --include-hidden # why can't it find my window?
  python page.py --pid 12345 --output .capture/home/app_v{n}.png
  python page.py --name MyApp.exe --output out.png --target-size 1280x800 --pad-color "#F1F5F9"
  python page.py --title "My App" --include-frame --output framed.png    # keep the real title bar
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ensure_parent, resolve_output  # noqa: E402


# Parameters of the pixel-based title-bar detection (used only when --crop-client is not given).
CHROME_MAX_SCAN_PX = 64          # how many rows from the top are examined
CHROME_DARK_THRESHOLD = 45       # a pixel counts as "dark chrome" below this value in every channel
CHROME_DARK_ROW_SHARE = 0.55     # share of dark samples a row needs (caption buttons may be light)
CHROME_MIN_PX = 28               # minimum crop once a dark band is found
CHROME_MAX_FRACTION = 3          # never crop more than 1/N of the image height


def detect_top_chrome_height(img, max_scan=CHROME_MAX_SCAN_PX, dark_threshold=CHROME_DARK_THRESHOLD):
    """Count leading rows that are mostly dark title-bar chrome."""
    w, h = img.size
    limit = min(max_scan, h // 4)
    chrome, px = 0, img.load()
    step = max(1, w // 80)
    for y in range(limit):
        dark = samples = 0
        for x in range(0, w, step):
            r, g, b = px[x, y][:3]
            samples += 1
            if r < dark_threshold and g < dark_threshold and b < dark_threshold:
                dark += 1
        if samples and dark / samples >= CHROME_DARK_ROW_SHARE:
            chrome = y + 1
        elif chrome > 0 and y > chrome + 2:
            break
    return min(h // CHROME_MAX_FRACTION, max(chrome, CHROME_MIN_PX)) if chrome > 0 else 0


def crop_top(img, pixels):
    if pixels <= 0:
        return img
    w, h = img.size
    return img.crop((0, min(pixels, h - 1), w, h))


def parse_color(s):
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", (s or "").strip())
    if not m:
        sys.exit(f"--pad-color must be a 6-digit hex color like #F1F5F9, got {s!r}")
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def parse_target_size(s):
    s = (s or "").strip().lower()
    if s in ("", "none", "0x0"):
        return None
    m = re.fullmatch(r"(\d+)x(\d+)", s)
    if not m or not int(m.group(1)) or not int(m.group(2)):
        sys.exit(f"--target-size must look like 1280x800 (or 'none'), got {s!r}")
    return int(m.group(1)), int(m.group(2))


def add_args(p):
    p.add_argument("--pid", type=int, help="Exact process ID")
    p.add_argument("--name", help="Process/executable name, e.g. notepad.exe (root process preferred over helpers)")
    p.add_argument("--title", help="Window title substring")
    p.add_argument("--list", action="store_true", help="List matching windows instead of capturing (no filter = all visible)")
    p.add_argument("--include-hidden", action="store_true", help="Also consider hidden/untitled top-level windows")
    p.add_argument("--output", help="Output PNG (required unless --list); use {n} for an auto-incrementing number, e.g. app_v{n}.png")
    p.add_argument("--include-frame", action="store_true",
                   help="Capture real screen pixels including the OS title bar/caption buttons (window is brought to the "
                        "foreground and must not be covered); disables auto-cropping unless --crop-top is given")
    p.add_argument("--crop-client", action="store_true",
                   help="Crop exactly to the client area from Win32 window geometry (title bar and borders removed, no pixel "
                        "heuristics). Not combinable with --include-frame, --crop-top or --no-crop")
    p.add_argument("--crop-top", type=int, default=-1, help="Pixels to crop; -1 = auto-detect chrome")
    p.add_argument("--no-crop", action="store_true")
    p.add_argument("--target-size", default="none",
                   help="WxH canvas to pad/crop to after cropping, e.g. 1280x800 (default: none)")
    p.add_argument("--pad-color", default="#FFFFFF", help="Canvas fill when padding (default #FFFFFF)")
    p.add_argument("--wait", type=float, default=0.0, help="Seconds to wait before capturing")
    p.add_argument("--flip-horizontal", action="store_true", help="Force a horizontal flip correction")
    p.add_argument("--no-flip-fix", action="store_true", help="Disable the automatic RTL-mirroring correction")
    p.add_argument("--debug", action="store_true", help="Verbose logging of how windows were found/filtered")


def run(args):
    import winshot

    winshot.setup_logging(debug=args.debug)
    try:
        if args.wait > 0:
            time.sleep(args.wait)
        has_target = args.pid is not None or args.name or args.title
        if not has_target and not args.list:
            sys.exit("Give --pid, --name or --title to pick a window (use --list to see what is open).")
        if not args.list and not args.output:
            sys.exit("--output is required when capturing.")
        size, pad = parse_target_size(args.target_size), parse_color(args.pad_color)   # fail fast, before capturing
        if args.crop_client and (args.include_frame or args.crop_top >= 0 or args.no_crop):
            sys.exit("--crop-client cannot be combined with --include-frame, --crop-top or --no-crop")

        cands = winshot.find_target_windows(name=args.name, pid=args.pid, title=args.title,
                                            include_hidden=args.include_hidden)
        if args.list:
            winshot.print_candidates(cands)
            return
        if not cands:
            winshot.report_no_match(name=args.name, pid=args.pid, title=args.title)
            sys.exit(1)
        chosen = cands[0]
        if len(cands) > 1:
            print(f"{len(cands)} windows matched; using the largest (PID {chosen['pid']}, \"{chosen['title']}\"). "
                  "Use --list to see them all.")

        insets = None
        flip = True if args.flip_horizontal else (False if args.no_flip_fix else None)
        img = (winshot.capture_window_with_frame(chosen["hwnd"]) if args.include_frame
               else winshot.capture_window(chosen["hwnd"], flip_override=flip))
        if args.crop_client:
            insets = winshot.client_insets(chosen["hwnd"])
    except RuntimeError as e:
        sys.exit(str(e))
    original = img.size

    crop_px = 0
    if insets:
        left, top, right, bottom = insets
        img = img.crop((left, top, max(left + 1, img.width - right), max(top + 1, img.height - bottom)))
        crop_px = top
    elif not args.no_crop:
        if args.crop_top >= 0:
            crop_px = args.crop_top
        elif not args.include_frame:
            crop_px = detect_top_chrome_height(img)
        img = crop_top(img, crop_px)

    if size and img.size != size:
        from PIL import Image
        canvas = Image.new("RGB", size, color=pad)
        canvas.paste(img, (max(0, (size[0] - img.width) // 2), 0))   # top-aligned, centered
        img = canvas

    out = resolve_output(args.output)
    ensure_parent(out)
    img.save(out)
    print(f"Saved: {out} ({img.width}x{img.height}) crop_top={crop_px} original={original[0]}x{original[1]}")


if __name__ == "__main__":
    from _common import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    run(ap.parse_args())
