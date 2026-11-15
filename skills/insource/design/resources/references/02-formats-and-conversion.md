# Formats and conversion

Pick the format from the medium and the job, not from habit. "One format for everything" is how a
project ends up with 4 MB PNG photographs and a favicon the browser ignores.

## Default formats (non-optimized assets)

| Format | Use it for | Notes |
|---|---|---|
| **SVG** | icons, logos, diagrams, anything that scales | editable text; keep as source; crushes raster at icon size |
| **PNG** | raster art that needs transparency or lossless pixels | alpha channel; can get huge for photos |
| **ICO** | favicons | container of several PNG sizes; browsers still expect it at the site root |

## Production formats (optimized for delivery)

| Format | Use it for | Trade |
|---|---|---|
| **WebP** | photos, hero images, any raster on the web | ~25-35% smaller than JPEG at equal quality; alpha supported |
| **AVIF** | same as WebP with newer encoding | smaller still, slower to encode, check target support |
| **JPEG** | photos where maximum compatibility matters | no alpha; flatten transparency onto a background color |
| **WebM / MP4** | video | codec support decides; see `05-optimization.md` |
| **WOFF2** | web fonts | the only web font format worth shipping today |

## Conversion rules

- **JPEG flattens alpha** onto white (or the color you pass). Check the result before shipping a
  logo with transparency as JPEG.
- **Animated GIF → WebP/MP4**: a GIF's animation survives WebP encoding; converting to video needs an
  encoder (ffmpeg-style) and changes how it is embedded.
- **SVG is not converted here.** Rasterizing SVG needs a rasterizer (e.g. cairosvg/resvg) and
  vectorizing a raster needs a tracing tool; `convert.py` reports SVG and stops rather than producing a
  blurry surprise.
- **ICO is built from a square source** at 16/32/48+; `gen_icons.py --favicon` does the whole set.
- **Extension lies are fixed without re-encoding**: `convert.py --fix` sniffs the bytes and renames.

## Quality

- WebP/JPEG `--quality 70-85` is the usual range: 85 for hero imagery, 70-75 for thumbnails.
- PNG has no quality knob; shrinking a PNG means reducing dimensions or converting to WebP.
- Never optimize by resizing a source of truth. Optimize **outputs**; keep the source as authored
  (naming: `photo.jpg` source, `photo-1280.webp` build).

## Colors

Color values are assets too. `color.py` (built on ColorAide, CSS Color 4/5) converts any CSS color
(`#3366ff`, `rgb()`, `hsl()`, `oklch()`, `color(display-p3 …)`, named) into any space, reports
luminance, and computes WCAG contrast:

```bash
python scripts/color.py "#3366FF" --to oklch
python scripts/color.py --contrast "#0F172A" "#FFFFFF"     # ratio + AA/AAA verdict
python scripts/color.py --mix "#FF0000" "#0000FF" --space oklch --ratio 0.5
```

Prefer OKLCH for palettes and interpolation (perceptually even), sRGB/hex for compatibility, Display P3
only where the target supports wide gamut. Do not store a color as a raster swatch when a token value
will do.
