"""Generate favicon sets and mobile app-icon sets from one square source image.

Outputs:

  --favicon            favicon.ico (16/32/48) plus the PNG sizes browsers, Apple touch devices and
                       the web-app manifest expect (16, 32, 48, 180, 192, 512).
  --app-icons --platform ios       every icon size the App Store pipeline wants (20..1024).
  --app-icons --platform android   mipmap densities 48/72/96/144/192 as ic_launcher.png.
  --sizes 16,32,64     any custom square sizes.

The source should be square and at least 1024x1024 (iOS requires 1024 for the marketing icon);
smaller sources are upscaled with a warning rather than refused, because a soft icon still ships.

Usage:
    python scripts/gen_icons.py --in logo.png --favicon --out-dir public/
    python scripts/gen_icons.py --in logo.png --app-icons --platform both --out-dir ui/icons/
    python scripts/gen_icons.py --in logo.png --sizes 16,32,64 --out-dir scratch/

Requires: pillow.
"""

import argparse
import os
import sys

from PIL import Image

IOS_SIZES = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024]
ANDROID_DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
FAVICON_PNGS = [16, 32, 48, 180, 192, 512]


def parse_hex(value):
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise argparse.ArgumentTypeError("'%s' is not #rgb or #rrggbb" % value)
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def parse_sizes(value):
    try:
        sizes = sorted({int(part) for part in value.split(",") if part.strip()})
    except ValueError:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers")
    if not sizes or sizes[0] <= 0:
        raise argparse.ArgumentTypeError("sizes must be positive")
    return sizes


def load_square(path):
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    if width != height:
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        image = image.crop((left, top, left + side, top + side))
        print("note  : source was %dx%d - cropped to a centered %dx%d square" % (width, height, side, side))
    if image.size[0] < 1024:
        print("note  : source is %dpx; icons are upscaled (iOS ideally wants 1024)" % image.size[0])
    return image


def render(image, size, pad_color):
    scaled = image.resize((size, size), Image.LANCZOS)
    if pad_color is None:
        return scaled
    flat = Image.new("RGB", (size, size), pad_color)
    flat.paste(scaled, mask=scaled.split()[-1])
    return flat


def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="src", required=True, help="square source image")
    parser.add_argument("--out-dir", default="icons", help="output directory (default: icons)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--favicon", action="store_true", help="web favicon set")
    group.add_argument("--app-icons", action="store_true", help="mobile app icon set")
    group.add_argument("--sizes", type=parse_sizes, default=None, help="custom sizes, e.g. 16,32,64")
    parser.add_argument("--platform", choices=("ios", "android", "both"), default="both",
                        help="with --app-icons (default: both)")
    parser.add_argument("--pad-color", type=parse_hex, default=None,
                        help="flatten transparency onto this color (some stores reject alpha)")
    args = parser.parse_args(argv)

    image = load_square(args.src)
    written = []

    if args.favicon:
        target = ensure(args.out_dir)
        ico_path = os.path.join(target, "favicon.ico")
        render(image, 48, args.pad_color).save(ico_path, format="ICO",
                                               sizes=[(16, 16), (32, 32), (48, 48)])
        written.append(ico_path)
        for size in FAVICON_PNGS:
            path = os.path.join(target, "favicon-%d.png" % size)
            render(image, size, args.pad_color).save(path)
            written.append(path)
        apple = os.path.join(target, "apple-touch-icon.png")
        render(image, 180, args.pad_color).save(apple)
        written.append(apple)

    elif args.app_icons:
        target = ensure(args.out_dir)
        if args.platform in ("ios", "both"):
            if args.pad_color is None and image.mode == "RGBA" and image.getchannel("A").getextrema()[0] < 255:
                print("note  : iOS app icons must be opaque - pass --pad-color to flatten transparency")
            ios_dir = ensure(os.path.join(target, "ios"))
            for size in IOS_SIZES:
                path = os.path.join(ios_dir, "icon-%d.png" % size)
                render(image, size, args.pad_color).save(path)
                written.append(path)
        if args.platform in ("android", "both"):
            for density, size in ANDROID_DENSITIES.items():
                density_dir = ensure(os.path.join(target, "android", "mipmap-" + density))
                path = os.path.join(density_dir, "ic_launcher.png")
                render(image, size, args.pad_color).save(path)
                written.append(path)

    else:
        target = ensure(args.out_dir)
        for size in args.sizes:
            path = os.path.join(target, "icon-%d.png" % size)
            render(image, size, args.pad_color).save(path)
            written.append(path)

    print("source : %s %dx%d" % (args.src, image.size[0], image.size[1]))
    print("wrote  : %d files under %s" % (len(written), os.path.abspath(args.out_dir)))
    for path in written:
        print("  %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
