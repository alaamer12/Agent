"""Convert and compare colors across color spaces, using the CSS Color 4 model.

Built on ColorAide (https://pypi.org/project/coloraide/): every CSS Color 4/5 space - sRGB, HSL,
HWB, Lab, LCH, Oklab, Oklch, Display P3, A98, ProPhoto, Rec. 2020, XYZ, and more - plus gamut
mapping, interpolation and WCAG contrast. Accepts any CSS color string: "#3366ff", "rgb(51 102 255)",
"oklch(0.57 0.23 265)", "color(display-p3 ...)", named colors.

Modes:
  convert   (default)  show the color in the requested space and a standard set of others
  contrast             WCAG contrast ratio between two colors, with AA/AAA verdicts
  mix                  interpolate two colors in a chosen space (oklch keeps chroma/hue natural)

Usage:
    python scripts/color.py "#3366FF" --to oklch
    python scripts/color.py "rgb(51 102 255 / 0.8)" --to display-p3 --json
    python scripts/color.py --contrast "#0F172A" "#FFFFFF"
    python scripts/color.py --mix "#FF0000" "#0000FF" --ratio 0.5 --space oklch

Requires: coloraide.
"""

import argparse
import sys

try:
    from coloraide import Color
except ImportError:  # pragma: no cover - depends on environment
    Color = None

# A readable standard set; any ColorAide space name is accepted via --to.
STANDARD = ["hex", "srgb", "hsl", "hwb", "lab", "lch", "oklab", "oklch", "display-p3", "xyz-d65"]


def parse_color(value):
    if Color is None:
        raise SystemExit("coloraide is not installed - pip install coloraide (in the project's venv)")
    try:
        return Color(value)
    except Exception:
        raise SystemExit("not a color: %r - pass #rrggbb, rgb(), hsl(), oklch(), a named color, ..." % value)


def show(color, space):
    key = space.lower()
    if key in ("hex", "rgb", "rgba"):
        return color.convert("srgb").to_string(hex=True)
    try:
        return color.convert(key).to_string()
    except ValueError:
        raise SystemExit("unknown color space %r - try oklch, display-p3, lab, hsl, srgb, ..." % space)


def describe(color):
    return {
        "hex": color.convert("srgb").to_string(hex=True),
        "srgb": color.convert("srgb").to_string(),
        "hsl": color.convert("hsl").to_string(),
        "hwb": color.convert("hwb").to_string(),
        "lab": color.convert("lab").to_string(),
        "lch": color.convert("lch").to_string(),
        "oklab": color.convert("oklab").to_string(),
        "oklch": color.convert("oklch").to_string(),
        "display-p3": color.convert("display-p3").to_string(),
        "xyz-d65": color.convert("xyz-d65").to_string(),
        "luminance": round(float(color.luminance()), 4),
        "contrast-white": round(float(color.contrast("white", method="wcag21")), 2),
        "contrast-black": round(float(color.contrast("black", method="wcag21")), 2),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("color", nargs="?", help="the color to convert (CSS syntax)")
    parser.add_argument("--to", default=None, help="target color space (e.g. oklch, display-p3, lab)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--contrast", nargs=2, metavar=("A", "B"), default=None,
                        help="WCAG contrast ratio between two colors")
    parser.add_argument("--mix", nargs=2, metavar=("A", "B"), default=None,
                        help="interpolate two colors")
    parser.add_argument("--ratio", type=float, default=0.5, help="mix ratio toward B (default 0.5)")
    parser.add_argument("--space", default="oklch", help="mix space (default oklch)")
    args = parser.parse_args(argv)

    if not (args.contrast or args.mix or args.color):
        parser.error("give a color, or --contrast A B, or --mix A B")

    if args.contrast:
        first, second = parse_color(args.contrast[0]), parse_color(args.contrast[1])
        ratio = float(first.contrast(second, method="wcag21"))
        small = "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "AA-large" if ratio >= 3 else "FAIL"
        print("A     : %s" % describe(first)["hex"])
        print("B     : %s" % describe(second)["hex"])
        print("ratio : %.2f:1 (WCAG 2.1)" % ratio)
        print("size  : %s for normal text, %s for large text" % (small, "AAA" if ratio >= 4.5 else "AA" if ratio >= 3 else "FAIL"))
        return 0

    if args.mix:
        first, second = parse_color(args.mix[0]), parse_color(args.mix[1])
        mixed = first.mix(second, args.ratio, space=args.space)
        data = describe(mixed)
        print("mix   : %s + %s @ %.2f in %s" % (data_hex(first), data_hex(second), args.ratio, args.space))
        for key in ("hex", "srgb", "hsl", "oklch", "display-p3"):
            print("%-11s %s" % (key, show(mixed, key)))
        return 0

    color = parse_color(args.color)
    data = describe(color)
    if args.json:
        import json
        if args.to:
            data["requested"] = {args.to: show(color, args.to)}
        print(json.dumps(data, indent=2))
        return 0

    if args.to:
        print("%-11s %s" % (args.to, show(color, args.to)))
    for key in STANDARD:
        if key == "hex":
            print("%-11s %s" % (key, data["hex"]))
        else:
            print("%-11s %s" % (key, data[key]))
    print("%-11s %.4f" % ("luminance", data["luminance"]))
    print("%-11s %.2f:1 vs white | %.2f:1 vs black" % ("contrast", data["contrast-white"], data["contrast-black"]))
    return 0


def data_hex(color):
    return color.convert("srgb").to_string(hex=True)


if __name__ == "__main__":
    sys.exit(main())
