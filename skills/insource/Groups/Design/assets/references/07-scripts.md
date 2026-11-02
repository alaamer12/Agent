# Script reference

Most scripts are Python 3, run from the skill's `scripts/` directory (or with the full path to the
script file); `bun-image.ts` runs under Bun. Image scripts need `pillow`; `recolor.py` also needs `numpy`. Install them **in the
project's own environment** - never globally:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install pillow numpy        # Windows
# .venv/bin/python -m pip install pillow numpy          # macOS/Linux
```

`inventory.py` and `localize.py` use the standard library only; `color.py` needs `coloraide`;
`bun-image.ts` needs Bun >= 1.3.14 and no packages. Audio/video: use ffmpeg directly (see
`05-optimization.md`) - no wrapper script.

Exit codes: `0` success; `1` a handled failure (nothing to do, some downloads failed); `2` usage error
(bad flag, path outside the image, missing input).

## recolor.py

Re-map a color family (hue offset + saturation/value scaling, keeps shading) or replace a chosen color
(RGB distance).

```bash
python scripts/recolor.py --in logo.png --to "#FFA200" --out logo-orange.png
python scripts/recolor.py --in logo.png --to "#FFA200" --pick 12,40 --apply
python scripts/recolor.py --in logo.png --to "#112233" --mode replace --rgb-tolerance 12 --out flat.png
```

Flags: `--in` `--to` `--from` `--pick X,Y` `--mode family|replace` `--tolerance` (degrees, family)
`--rgb-tolerance` (replace) `--saturation-floor` `--out` `--apply`.

## convert.py

```bash
python scripts/convert.py --in photo.jpg --to webp --out photo.webp --quality 82
python scripts/convert.py --in banner.png --to ico
python scripts/convert.py --fix --in assets/ --recursive
```

Formats: png, jpeg/jpg, webp, bmp, gif, tiff, ico. `--fix` renames to the real format without
re-encoding. SVG is reported, never converted.

## transform.py

```bash
python scripts/transform.py --in logo.png --rotate 90 --flip h --scale 0.5 --out logo-t.png
python scripts/transform.py --in photo.jpg --resize 800x --out photo-800.jpg
python scripts/transform.py --in art.png --crop 10,10,410,210 --out art-detail.png
```

Order: rotate → flip → scale → resize → crop. Out-of-bounds crops are refused (exit 2).

## gen_icons.py

```bash
python scripts/gen_icons.py --in logo.png --favicon --out-dir public/
python scripts/gen_icons.py --in logo.png --app-icons --platform both --out-dir ui/icons/
python scripts/gen_icons.py --in logo.png --sizes 16,32,64 --out-dir scratch/
```

Non-square sources are cropped to a centered square (reported); sources under 1024 are upscaled with a
note. `--pad-color` flattens alpha (iOS marketing icon requires it).

## og_image.py

```bash
python scripts/og_image.py --title "Ship releases without fear" --subtitle "platform docs" \
    --bg "#0F172A" --logo logo.png --font "C:/Windows/Fonts/arialbd.ttf" --out og.png
python scripts/og_image.py --title "..." --bg cover.jpg --out og.jpg
```

Default 1200x630; `--width/--height` to override; `--fg` sets text color. Pass `--font` for acceptable
type - the fallback is Pillow's bitmap font.

## splash.py

```bash
python scripts/splash.py --logo logo.png --bg "#0F172A" --preset both --out-dir res/splash/
python scripts/splash.py --logo logo.png --bg splash-bg.jpg --sizes 1080x1920,1440x2560 --out-dir out/
python scripts/splash.py --bg "#FFFFFF" --sizes 1080x1920 --out-dir out/   # plain splash, no logo
```

Presets: ios (6 portrait sizes), android (5), both. `--logo-width` is the logo width as a percentage of
screen width (default 30).

## optimize.py

```bash
python scripts/optimize.py --in assets/raw --out assets/build --format webp --quality 80 --max-width 1600
python scripts/optimize.py --in hero.jpg --variants 320,640,1280 --out assets/build
python scripts/optimize.py --in gallery/ --thumbs --thumb-width 240 --out assets/thumbs
```

Directory mode processes every image file; output names derive from the source stem. Prints each output
with its byte size.

## localize.py

```bash
python scripts/localize.py --manifest vendor-assets.txt --out assets/vendor
python scripts/localize.py --url https://example.com/logo.svg --out assets/icons/logo.svg
```

Manifest: one `URL [destination]` per line, `#` comments allowed. Each download is sniffed
(png/jpg/gif/webp/woff/woff2/ttf/otf/svg/pdf/media); HTML or unknown payloads are warned about. Exit 1
if any download failed.

## inventory.py

```bash
python scripts/inventory.py --root . --assets assets public
python scripts/inventory.py --root . --json > inventory.json
```

Reports duplicates by content hash, files whose filename appears in no scanned text file, and external
asset URLs. Text scanning means dynamic references can look unreferenced - state that caveat when
reporting.

## color.py

Color conversion, contrast and mixing over CSS Color 4/5 (via ColorAide). Accepts any CSS color.

```bash
python scripts/color.py "#3366FF" --to oklch
python scripts/color.py "rgb(51 102 255 / 0.8)" --to display-p3 --json
python scripts/color.py --contrast "#0F172A" "#FFFFFF"
python scripts/color.py --mix "#FF0000" "#0000FF" --ratio 0.5 --space oklch
```

Flags: `--to <space>` (oklch, display-p3, lab, hsl, srgb, hex, ...) `--json` `--contrast A B`
`--mix A B --ratio --space`. Reports hex/srgb/hsl/hwb/lab/lch/oklab/oklch/display-p3/xyz, luminance,
and contrast against white and black.

## bun-image.ts

Bun-only (>= 1.3.14), zero dependencies, built on `Bun.Image` (sharp-shaped API).

```bash
bun run scripts/bun-image.ts logo.png --out-dir assets/build --variants 320,640,1280
bun run scripts/bun-image.ts logo.png --out-dir assets/build --thumbnail 240 --format avif --placeholder
```

Writes `<stem>-<width>.<ext>` per variant (or one thumbnail), reports source/output sizes and the
percentage saved, and with `--placeholder` writes `<stem>.lqip.txt` - a ThumbHash-rendered data URL for
inline low-quality previews.

No package install is needed for this script - `Bun.Image` ships with the runtime, so `bun run` executes
it directly. For batteries-included generators (manifest + splash + favicons in one go), the Node tool
`pwa-asset-generator` can be run without adding a project dependency: `bun x pwa-asset-generator ...`
(fetched at run time, pinned by version when reproducibility matters).
