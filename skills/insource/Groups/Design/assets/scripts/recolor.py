"""Re-map one color family, or one picked color, in an image onto another color.

Two modes:

  family  (default)  measure a source color - the dominant one, --from, or a pixel picked with
                     --pick - then shift the HUE of every sufficiently saturated pixel within
                     --tolerance degrees, and SCALE saturation/value by the target's ratio to the
                     source. Offsetting instead of substituting keeps gradients, shading and the
                     anti-aliased edges of the artwork intact: they land on the corresponding shade
                     of the new color instead of collapsing into one flat block.
  replace            set every pixel within --rgb-tolerance (RGB distance) of the chosen color to the
                     target exactly - intended for a color picked from the image, including greys
                     and whites whose hue is meaningless.

Neutral (near-grey) pixels and unrelated hues are left untouched in both modes.

Usage:
    python scripts/recolor.py --in logo.png --to "#FFA200" --out logo-orange.png
    python scripts/recolor.py --in logo.png --to "#FFA200" --pick 12,40 --apply
    python scripts/recolor.py --in logo.png --to "#112233" --mode replace --tolerance 12

Requires: pillow, numpy.
"""

import argparse
import colorsys
import sys

import numpy as np
from PIL import Image


def parse_hex(value):
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise argparse.ArgumentTypeError("'%s' is not #rgb or #rrggbb" % value)
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))


def parse_point(value):
    try:
        x, y = value.split(",")
        return int(x), int(y)
    except ValueError:
        raise argparse.ArgumentTypeError("'%s' is not X,Y" % value)


def to_hsv(rgb):
    return colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)


def dominant_color(pixels):
    """Average color of the largest sufficiently-chromatic group.

    Pixels are bucketed so anti-aliasing noise cannot out-vote a flat background in thin slivers,
    but the value returned is the MEAN of the winning bucket: the bucket label would shift hue and
    saturation by a few units, and those numbers become the scale factors for every repainted pixel.
    """
    bucket = 8
    centered = (pixels.astype(np.int64) // bucket) * bucket + bucket // 2
    packed = (centered[:, 0] << 16) | (centered[:, 1] << 8) | centered[:, 2]
    values, inverse, counts = np.unique(packed, return_inverse=True, return_counts=True)

    for order in np.argsort(-counts):
        members = pixels[inverse == order]
        mean = tuple(int(round(float(v))) for v in members.mean(axis=0))
        _, saturation, value = to_hsv(mean)
        # Saturation excludes white and grey; a brightness ceiling would also discard a
        # fully-saturated background, which may be exactly the color being measured.
        if saturation > 0.15 and value > 0.08:
            return mean

    key = int(values[np.argmax(counts)])
    return tuple(int(c) for c in [(key >> 16) & 255, (key >> 8) & 255, key & 255])


def recolor(image, source_rgb, target_rgb, tolerance_degrees, saturation_floor, mode, rgb_tolerance=24.0):
    source_hsv = to_hsv(source_rgb)
    target_hsv = to_hsv(target_rgb)

    rgba = np.asarray(image.convert("RGBA"), dtype=np.float32) / 255.0
    array = rgba[:, :, :3]
    alpha = rgba[:, :, 3]
    opaque = alpha > 0.01

    if mode == "replace":
        # Replacing a chosen color is an RGB-distance match, not a hue match: the chosen pixel may
        # be grey or white, whose hue is meaningless and whose saturation is below any sane floor.
        source = np.array(source_rgb, dtype=np.float32) / 255.0
        distance = np.sqrt(((array - source) ** 2).sum(axis=2)) * 255.0
        mask = (distance <= float(np.clip(rgb_tolerance, 0.0, 441.7))) & opaque
        color = np.array(target_rgb, dtype=np.float32) / 255.0
        blended = np.where(mask[:, :, None], color, array)
        changed = int(mask.sum())
        out = np.dstack([blended, alpha])
        return (Image.fromarray((np.clip(out, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8), "RGBA"),
                changed, mask.size)

    maximum = array.max(axis=2)
    minimum = array.min(axis=2)
    span = maximum - minimum

    value = maximum
    saturation = np.where(maximum > 0, span / np.maximum(maximum, 1e-6), 0.0)

    # Hue in [0, 360), matching colorsys' sector arithmetic so the comparison against the
    # source hue is meaningful on both sides of the wrap.
    r, g, b = array[:, :, 0], array[:, :, 1], array[:, :, 2]
    with np.errstate(invalid="ignore", divide="ignore"):
        when_r = np.where(span > 0, ((g - b) / np.maximum(span, 1e-6)) % 6.0, 0.0)
        when_g = np.where(span > 0, ((b - r) / np.maximum(span, 1e-6)) + 2.0, 0.0)
        when_b = np.where(span > 0, ((r - g) / np.maximum(span, 1e-6)) + 4.0, 0.0)
    hue = np.where(maximum == r, when_r, np.where(maximum == g, when_g, when_b)) * 60.0

    source_hue = source_hsv[0] * 360.0
    tolerance = float(np.clip(tolerance_degrees, 1.0, 180.0))
    distance = np.abs(hue - source_hue)
    distance = np.minimum(distance, 360.0 - distance)
    mask = (distance <= tolerance) & (saturation >= saturation_floor) & opaque

    hue_shift = (target_hsv[0] * 360.0) - source_hue
    saturation_scale = target_hsv[1] / max(source_hsv[1], 1e-6)
    value_scale = target_hsv[2] / max(source_hsv[2], 1e-6)

    out_hue = (hue + hue_shift) % 360.0
    out_saturation = np.clip(saturation * saturation_scale, 0.0, 1.0)
    out_value = np.clip(value * value_scale, 0.0, 1.0)

    stacked = np.stack([out_hue, out_saturation, out_value], axis=-1)
    converted = np.apply_along_axis(
        lambda h: np.array(colorsys.hsv_to_rgb((h[0] % 360.0) / 360.0, h[1], h[2])), axis=2, arr=stacked)

    blended = np.where(mask[:, :, None], converted, array)
    changed = int(mask.sum())
    out = np.dstack([blended, alpha])
    return (Image.fromarray((np.clip(out, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8), "RGBA"),
            changed, mask.size)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="src", required=True, help="image to read")
    parser.add_argument("--to", required=True, type=parse_hex, help="target color, e.g. \"#FFA200\"")
    parser.add_argument("--from", dest="frm", type=parse_hex, default=None,
                        help="source color; measured from the image when omitted")
    parser.add_argument("--pick", type=parse_point, default=None,
                        help="X,Y pixel to sample the source color from (wins over --from)")
    parser.add_argument("--mode", choices=("family", "replace"), default="family",
                        help="family = hue-offset + sat/value scale (keeps shading); replace = flat fill")
    parser.add_argument("--tolerance", type=float, default=60.0, help="hue window in degrees, family mode (default 60)")
    parser.add_argument("--rgb-tolerance", type=float, default=24.0,
                        help="per-color RGB distance 0-441, replace mode (default 24)")
    parser.add_argument("--saturation-floor", type=float, default=0.12,
                        help="ignore near-grey pixels, family mode (default 0.12)")
    parser.add_argument("--out", dest="dst", default=None, help="where to write (default: <name>-recolored.png)")
    parser.add_argument("--apply", action="store_true", help="overwrite the input file instead of writing a copy")
    args = parser.parse_args(argv)

    image = Image.open(args.src).convert("RGBA")
    rgba = np.asarray(image, dtype=np.uint8)
    opaque_pixels = rgba[rgba[:, :, 3] > 8][:, :3]
    if opaque_pixels.size == 0:
        print("error: the image is fully transparent")
        return 2
    flat = opaque_pixels

    if args.pick is not None:
        width, height = image.size
        x, y = args.pick
        if not (0 <= x < width and 0 <= y < height):
            print("error: --pick %d,%d is outside the %dx%d image" % (x, y, width, height))
            return 2
        picked = image.getpixel((x, y))
        if picked[3] < 8:
            print("error: --pick %d,%d is transparent - pick a visible pixel" % (x, y))
            return 2
        source = tuple(int(c) for c in picked[:3])
    else:
        source = args.frm or dominant_color(flat)

    result, changed, total = recolor(image, source, args.to, args.tolerance, args.saturation_floor,
                                     args.mode, args.rgb_tolerance)

    destination = args.src if args.apply else (args.dst or args.src.replace(".png", "-recolored.png"))
    result.save(destination, optimize=True)

    hex_of = lambda c: "#{:02X}{:02X}{:02X}".format(*c)
    print("in        : %s %dx%d" % (args.src, image.size[0], image.size[1]))
    print("mode      : %s" % args.mode)
    print("from      : %s (hsv %s)" % (hex_of(source), tuple(round(v, 3) for v in to_hsv(source))))
    print("to        : %s (hsv %s)" % (hex_of(args.to), tuple(round(v, 3) for v in to_hsv(args.to))))
    print("tolerance : %s deg, saturation floor %s" % (args.tolerance, args.saturation_floor)
          if args.mode == "family" else "rgb tol   : %s (replace mode)" % args.rgb_tolerance)
    print("repainted : %d of %d pixels (%.1f%%)" % (changed, total, 100.0 * changed / total))
    print("out       : %s" % destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
