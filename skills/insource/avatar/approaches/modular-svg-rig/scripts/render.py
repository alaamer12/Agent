#!/usr/bin/env python3
"""Render an SVG or HTML file to PNG (no server needed).

  python scripts/render.py avatar.svg out.png [--size 600] [--scale 2] [--transparent]
  python scripts/render.py page.html out.png --size 420 --selector ".avatar"

--selector crops the screenshot to one element (HTML only).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _render import Renderer  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--size", type=int, default=600, help="viewport size in CSS px (square)")
    ap.add_argument("--scale", type=int, default=2, help="device pixel ratio (2 = crisp, 4 = inspect details)")
    ap.add_argument("--transparent", action="store_true", help="keep alpha (no page background)")
    ap.add_argument("--selector", help="CSS selector to crop to (HTML input)")
    a = ap.parse_args()

    src = Path(a.input)
    if not src.exists():
        sys.exit(f"input not found: {src}")
    with Renderer(a.size, a.scale) as r:
        if src.suffix.lower() == ".svg":
            img = r.svg(src.read_text(encoding="utf-8"), transparent=a.transparent)
        else:
            img = r.file(src, transparent=a.transparent, selector=a.selector)
    img.save(a.output)
    print(f"wrote {a.output} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
