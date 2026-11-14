"""Geometric transforms for one image: rotate, flip, scale, resize and crop.

The operations compose in a fixed order - rotate, flip, scale/resize, crop - so a command is
reproducible. Values that would cut pixels off (negative crop, scale below 1px) are refused rather
than silently clamped.

Usage:
    python scripts/transform.py --in logo.png --rotate 90 --out logo-r90.png
    python scripts/transform.py --in photo.jpg --flip h --out photo-mirrored.jpg
    python scripts/transform.py --in icon.png --scale 2 --out icon@2x.png
    python scripts/transform.py --in hero.jpg --resize 1600x900 --out hero-wide.jpg
    python scripts/transform.py --in art.png --crop 10,10,410,210 --out art-detail.png
    python scripts/transform.py --in art.png --rotate 90 --apply

Requires: pillow.
"""

import argparse
import sys

from PIL import Image


def parse_scale(value):
    try:
        return float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("scale must be a number")


def parse_flip(value):
    value = value.lower()
    if value not in ("h", "v", "horizontal", "vertical"):
        raise argparse.ArgumentTypeError("flip must be h or v")
    return "h" if value.startswith("h") else "v"


def parse_resize(value):
    try:
        width, height = value.lower().split("x")
        width = int(width) if width else None
        height = int(height) if height else None
        if width is None and height is None:
            raise ValueError
        return width, height
    except ValueError:
        raise argparse.ArgumentTypeError("resize must be WxH, Wx or xH")


def parse_crop(value):
    try:
        parts = [int(part) for part in value.split(",")]
        if len(parts) != 4:
            raise ValueError
        return parts
    except ValueError:
        raise argparse.ArgumentTypeError("crop must be LEFT,TOP,RIGHT,BOTTOM")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="src", required=True, help="input image")
    parser.add_argument("--out", dest="dst", default=None, help="output path (default: <name>-edited.png)")
    parser.add_argument("--rotate", type=float, default=None, help="clockwise degrees; expands the canvas")
    parser.add_argument("--flip", type=parse_flip, default=None, help="h or v")
    parser.add_argument("--scale", type=parse_scale, default=None, help="factor, e.g. 2 or 0.5")
    parser.add_argument("--resize", type=parse_resize, default=None, help="WxH, Wx or xH (keeps aspect if one side is blank)")
    parser.add_argument("--crop", type=parse_crop, default=None, help="LEFT,TOP,RIGHT,BOTTOM in pixels")
    parser.add_argument("--apply", action="store_true", help="overwrite the input file")
    args = parser.parse_args(argv)

    if not any([args.rotate, args.flip, args.scale, args.resize, args.crop]):
        parser.error("nothing to do: give at least one of --rotate --flip --scale --resize --crop")

    image = Image.open(args.src)
    original = image.size

    if args.rotate is not None:
        image = image.rotate(-args.rotate, expand=True, resample=Image.BICUBIC)

    if args.flip == "h":
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
    elif args.flip == "v":
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

    if args.scale is not None:
        if args.scale <= 0:
            print("error: --scale must be positive")
            return 2
        size = (max(1, round(image.size[0] * args.scale)), max(1, round(image.size[1] * args.scale)))
        image = image.resize(size, Image.LANCZOS)

    if args.resize is not None:
        width, height = args.resize
        if width is None:
            width = max(1, round(image.size[0] * (height / image.size[1])))
        if height is None:
            height = max(1, round(image.size[1] * (width / image.size[0])))
        image = image.resize((width, height), Image.LANCZOS)

    if args.crop is not None:
        left, top, right, bottom = args.crop
        if left < 0 or top < 0 or right > image.size[0] or bottom > image.size[1] or right <= left or bottom <= top:
            print("error: --crop %s is outside %dx%d or inverted" % (args.crop, image.size[0], image.size[1]))
            return 2
        image = image.crop(args.crop)

    destination = args.src if args.apply else (args.dst or args.src.rsplit(".", 1)[0] + "-edited.png")
    image.save(destination)
    print("in   : %s %dx%d" % (args.src, original[0], original[1]))
    print("out  : %s %dx%d" % (destination, image.size[0], image.size[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
