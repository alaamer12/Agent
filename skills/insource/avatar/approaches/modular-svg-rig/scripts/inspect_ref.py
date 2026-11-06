#!/usr/bin/env python3
"""Zoom into a reference image, overlay a labelled coordinate grid, sample colors.

  python scripts/inspect_ref.py ref.png --box 95,15,195,100 --zoom 8 --grid 10 \
         --sample 130,40 140,60 --palette 6 --out ref_zoom.png

Grid labels are in ORIGINAL image coordinates, so measurements read off the zoomed
crop can be used directly as drawing coordinates (draw the SVG with
viewBox="x0 y0 w h" equal to the crop box, and no conversion is needed).
"""
import argparse

from PIL import Image, ImageDraw


def parse_box(s):
    x0, y0, x1, y1 = (int(float(v)) for v in s.split(","))
    return x0, y0, x1, y1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--box", help="x0,y0,x1,y1 crop in original pixels (default: whole image)")
    ap.add_argument("--zoom", type=int, default=6, help="integer upscale factor")
    ap.add_argument("--grid", type=int, default=0, help="grid spacing in original px (0 = none)")
    ap.add_argument("--sample", nargs="*", default=[], help="x,y points (original px) to print colors for")
    ap.add_argument("--palette", type=int, default=0, help="print the K dominant colors of the crop")
    ap.add_argument("--out", default="ref_zoom.png")
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGB")
    x0, y0, x1, y1 = parse_box(a.box) if a.box else (0, 0, im.width, im.height)
    crop = im.crop((x0, y0, x1, y1))
    print(f"image {im.width}x{im.height}, crop {x0},{y0},{x1},{y1}")

    for p in a.sample:
        x, y = (int(v) for v in p.split(","))
        r, g, b = im.getpixel((x, y))
        print(f"  ({x},{y}) -> #{r:02x}{g:02x}{b:02x}")

    if a.palette:
        q = crop.quantize(colors=a.palette, method=Image.MEDIANCUT)
        pal = q.getpalette()
        counts = sorted(q.getcolors(), reverse=True)
        total = sum(c for c, _ in counts)
        print("  dominant colors:")
        for c, idx in counts:
            r, g, b = pal[idx * 3: idx * 3 + 3]
            print(f"    #{r:02x}{g:02x}{b:02x}  {100 * c / total:4.1f}%")

    big = crop.resize((crop.width * a.zoom, crop.height * a.zoom), Image.LANCZOS)
    if a.grid:
        d = ImageDraw.Draw(big, "RGBA")
        gx = (x0 // a.grid + 1) * a.grid
        while gx < x1:
            px = (gx - x0) * a.zoom
            d.line([(px, 0), (px, big.height)], fill=(0, 120, 255, 90), width=1)
            d.text((px + 2, 2), str(gx), fill=(0, 70, 200, 255))
            gx += a.grid
        gy = (y0 // a.grid + 1) * a.grid
        while gy < y1:
            py = (gy - y0) * a.zoom
            d.line([(0, py), (big.width, py)], fill=(255, 60, 0, 90), width=1)
            d.text((2, py + 2), str(gy), fill=(200, 40, 0, 255))
            gy += a.grid
    big.save(a.out)
    print(f"wrote {a.out} ({big.width}x{big.height})")


if __name__ == "__main__":
    main()
