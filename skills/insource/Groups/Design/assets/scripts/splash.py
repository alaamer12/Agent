"""Generate splash-screen images from a logo and a background.

Presets cover the common portrait sizes for each mobile platform; --sizes adds any custom WxH.
The background can be a solid color or an image (cover-cropped); the logo is centered at
--logo-width percent of the screen width (default 30%).

Whether the splash should carry the logo, a different image, or nothing at all is a product
decision: ask the user before generating - this script executes the chosen answer.

Usage:
    python scripts/splash.py --logo logo.png --bg "#0F172A" --preset both --out-dir res/splash/
    python scripts/splash.py --logo logo.png --bg splash-bg.jpg --sizes 1080x1920,1440x2560 --out-dir out/

Requires: pillow.
"""

import argparse
import os
import sys

from PIL import Image

PRESETS = {
    "ios": [(1125, 2436), (1170, 2532), (1242, 2688), (1290, 2796), (1536, 2048), (2048, 2732)],
    "android": [(320, 480), (480, 800), (720, 1280), (1080, 1920), (1440, 2560)],
}
PRESETS["both"] = PRESETS["ios"] + PRESETS["android"]


def parse_hex(value):
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise argparse.ArgumentTypeError("'%s' is not #rgb or #rrggbb" % value)
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def parse_sizes(value):
    sizes = []
    for part in value.split(","):
        part = part.strip().lower()
        if not part:
            continue
        try:
            width, height = part.split("x")
            sizes.append((int(width), int(height)))
        except ValueError:
            raise argparse.ArgumentTypeError("'%s' is not WxH" % part)
    if not sizes:
        raise argparse.ArgumentTypeError("no sizes given")
    return sizes


def cover(image, size):
    target_w, target_h = size
    scale = max(target_w / image.size[0], target_h / image.size[1])
    scaled = image.resize((max(1, round(image.size[0] * scale)), max(1, round(image.size[1] * scale))), Image.LANCZOS)
    left = (scaled.size[0] - target_w) // 2
    top = (scaled.size[1] - target_h) // 2
    return scaled.crop((left, top, left + target_w, top + target_h))


def render(logo, size, background, logo_width_percent):
    if os.path.isfile(background):
        canvas = cover(Image.open(background).convert("RGB"), size)
    else:
        canvas = Image.new("RGB", size, parse_hex(background))
    if logo is None:
        return canvas

    target_w = max(1, round(size[0] * logo_width_percent / 100.0))
    ratio = target_w / logo.size[0]
    scaled = logo.resize((target_w, max(1, round(logo.size[1] * ratio))), Image.LANCZOS)
    x = (size[0] - scaled.size[0]) // 2
    y = (size[1] - scaled.size[1]) // 2
    canvas.paste(scaled, (x, y), scaled)
    return canvas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--logo", default=None, help="centered logo (omit for a plain background splash)")
    parser.add_argument("--bg", default="#FFFFFF", help="background color (#rrggbb) or image path")
    parser.add_argument("--preset", choices=sorted(PRESETS), default=None, help="ios/android/both size set")
    parser.add_argument("--sizes", type=parse_sizes, default=None, help="custom WxH list")
    parser.add_argument("--logo-width", type=float, default=30.0, help="logo width as %% of screen (default 30)")
    parser.add_argument("--out-dir", default="splash", help="output directory")
    args = parser.parse_args(argv)

    if args.preset is None and args.sizes is None:
        parser.error("give --preset and/or --sizes")
    sizes = []
    if args.preset:
        sizes.extend(PRESETS[args.preset])
    if args.sizes:
        sizes.extend(args.sizes)

    logo = Image.open(args.logo).convert("RGBA") if args.logo else None
    os.makedirs(args.out_dir, exist_ok=True)
    written = []
    for width, height in sizes:
        path = os.path.join(args.out_dir, "splash-%dx%d.png" % (width, height))
        render(logo, (width, height), args.bg, args.logo_width).save(path)
        written.append(path)

    print("wrote : %d splash images under %s" % (len(written), os.path.abspath(args.out_dir)))
    for path in written:
        print("  %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
