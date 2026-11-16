"""Compose an Open Graph share image (1200x630 by default) from a title, a background and a logo.

Background options: a solid color (--bg "#0F172A") or an image (--bg background.jpg, cover-cropped).
Text: --title (wrapped), optional --subtitle, optional --logo placed in a corner.
Fonts: pass --font path/to/font.ttf for reliable output; when omitted the script searches common
system font locations and falls back to Pillow's built-in bitmap font with a warning (looks rough at
1200px, so pass a font for anything user-facing).

Usage:
    python scripts/og_image.py --title "Ship releases without fear" --subtitle "platform docs" \
        --bg "#0F172A" --logo logo.png --font fonts/Inter-Bold.ttf --out public/og.png
    python scripts/og_image.py --title "..." --bg cover.jpg --out public/og.jpg

Requires: pillow.
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

CANDIDATE_FONTS = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def parse_hex(value):
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise argparse.ArgumentTypeError("'%s' is not #rgb or #rrggbb" % value)
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def load_font(path, size):
    if path:
        return ImageFont.truetype(path, size)
    for candidate in CANDIDATE_FONTS:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    print("warning: no font found - falling back to Pillow's bitmap font; pass --font for a real one")
    return ImageFont.load_default(size)


def cover(image, size):
    target_w, target_h = size
    scale = max(target_w / image.size[0], target_h / image.size[1])
    scaled = image.resize((max(1, round(image.size[0] * scale)), max(1, round(image.size[1] * scale))), Image.LANCZOS)
    left = (scaled.size[0] - target_w) // 2
    top = (scaled.size[1] - target_h) // 2
    return scaled.crop((left, top, left + target_w, top + target_h))


def wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--title", required=True, help="headline text")
    parser.add_argument("--subtitle", default=None, help="smaller second line")
    parser.add_argument("--bg", default="#111827", help="background color (#rrggbb) or image path")
    parser.add_argument("--fg", type=parse_hex, default=(255, 255, 255), help="text color (default white)")
    parser.add_argument("--logo", default=None, help="logo image; placed top-left")
    parser.add_argument("--logo-size", type=int, default=96, help="logo height in px (default 96)")
    parser.add_argument("--font", default=None, help="path to a .ttf/.otf font")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=630)
    parser.add_argument("--out", default="og-image.png")
    args = parser.parse_args(argv)

    if os.path.isfile(args.bg):
        canvas = cover(Image.open(args.bg).convert("RGB"), (args.width, args.height))
    else:
        canvas = Image.new("RGB", (args.width, args.height), parse_hex(args.bg))

    draw = ImageDraw.Draw(canvas)
    margin = 72
    top = margin

    if args.logo:
        logo = Image.open(args.logo).convert("RGBA")
        ratio = args.logo_size / logo.size[1]
        logo = logo.resize((max(1, round(logo.size[0] * ratio)), args.logo_size), Image.LANCZOS)
        canvas.paste(logo, (margin, top), logo)
        top += args.logo_size + 40

    title_font = load_font(args.font, 64)
    subtitle_font = load_font(args.font, 30)

    lines = wrap(draw, args.title, title_font, args.width - margin * 2)
    y = top
    for line in lines:
        draw.text((margin, y), line, font=title_font, fill=args.fg)
        y += 76

    if args.subtitle:
        y += 16
        for line in wrap(draw, args.subtitle, subtitle_font, args.width - margin * 2):
            draw.text((margin, y), line, font=subtitle_font, fill=args.fg)
            y += 40

    if y > args.height - margin:
        print("warning: content is %dpx tall and may be clipped by the %dpx canvas" % (y, args.height))

    canvas.save(args.out)
    print("out : %s (%dx%d)" % (args.out, args.width, args.height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
