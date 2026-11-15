# resources - the project's resource files, managed once

This mode owns **resource files and their references**: how they are named, where they live, how they
are produced, converted, localized, optimized, and how the code points at them. It operates at the
resource-file level - it is not a pipeline, storage layer, or delivery system.

```
project files ──► resources skill ──► correct file, correct name, correct place, correct reference
                 (no application-level processing, no database design, no infrastructure)
```

## Ask before generating - the visual decisions are the user's

When a generated asset carries a design choice, ask - briefly, with concrete options - instead of
assuming. Ask only where the answer changes what the user sees:

- **Web loading screen:** logo, a specific image, or nothing?
- **Mobile splash screen:** logo or plain background? What color/image?
- **Icons:** is there an existing logo/icon to derive from, and does the platform need it flattened
  onto a color (no alpha)?
- **Brand colors / OG template:** which colors and title text?
- **Where new assets live,** if the project has no convention yet.

One batch of these questions, not an interrogation; a project with an established convention answers
them by looking at the folder.

## The capability map

| Need | Script | Shape |
|---|---|---|
| Recolor a whole color family, or replace a picked pixel color | `scripts/recolor.py` | `--in img --to #HEX [--from #HEX \| --pick X,Y] [--mode family\|replace]` |
| Convert format, or fix a lying extension | `scripts/convert.py` | `--in a.png --to webp --out b.webp` · `--fix --in dir --recursive` |
| Rotate, flip, scale, resize, crop | `scripts/transform.py` | `--rotate 90 --flip h --scale 2 --resize 1600x --crop L,T,R,B` |
| Favicon set, or app icons (iOS/Android) | `scripts/gen_icons.py` | `--favicon --out-dir web/` · `--app-icons --platform both` |
| Open Graph share image | `scripts/og_image.py` | `--title ... --subtitle ... --bg color\|image --logo logo.png --font font.ttf` |
| Splash screens per platform | `scripts/splash.py` | `--logo logo.png --bg color\|image --preset both --sizes 1080x1920` |
| Optimize / variants / thumbnails | `scripts/optimize.py` | `--variants 320,640,1280 --format webp --quality 80` · `--thumbs` · `--max-width 1600` |
| Localize CDN assets | `scripts/localize.py` | `--manifest vendor.txt --out assets/vendor` |
| Audit assets: duplicates, unused, external URLs | `scripts/inventory.py` | `--root . --assets assets public` |
| Convert/compare colors across CSS Color 4 spaces | `scripts/color.py` | `"#3366FF" --to oklch` · `--contrast A B` · `--mix A B --space oklch` |
| Bun projects: variants + ThumbHash placeholders (built-in, zero deps) | `scripts/bun-image.ts` | `bun run bun-image.ts in.png --out-dir out --variants 320,640 --placeholder` |
| Conform a sheet or single master into slot files fitted to the BOM | `scripts/conform.py` | `--bom bom/page.md --group avatar --in raw/avatars.png --out assets/avatars` · `--slots hero-home --in raw/hero-home.png` · `--rows 8,8,8,10` |
| Measure a sheet before cutting it: content, row-by-row layout, cut lines, ceiling | `scripts/sheet_probe.py` | `sheet.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"` · `--json` |
| Review delivered slots on a checkerboard, with alpha-edge facts | `scripts/contact_sheet.py` | `assets/avatars --out review.png --skip-density` · `--json` |

Full flags, exit codes and examples: `references/07-scripts.md`. Dependencies, installed **in the
project's own environment** - never globally: `pillow` (image scripts), `numpy` (recolor), `coloraide`
(color); `bun-image.ts` needs Bun >= 1.3.14 and no packages at all. Audio and video are handled with
**ffmpeg directly** (probe, transcode, poster) - no wrapper script; `inventory` and `localize` are
standard library only.

## Naming and organization - the part that outlives the task

- **Descriptive, not serial.** `hero-banner-launch.webp`, never `one.png`, `IMG_2041.png` or
  `final-v2-final.png`. The name answers "what is this and where is it used".
- **kebab-case by default**, matching the project's existing convention when it has one.
- **Brand apart from content.** Logos, app icons, splash and OG images are brand assets; images a
  feature ships (gallery photos, sample data artwork) are product content. Different folders, and
  content assets never edited to fit a brand.
- **One kind per home.** `icons/`, `brand/`, `images/`, `fonts/`, `media/` - or the project's existing
  structure; do not mix SVG icons with content raster images.
- **SVG and PNG stay distinct.** The vector source and its raster exports are different assets with
  different purposes, not duplicates to delete.

Detail and folder examples: `references/01-naming-and-organization.md`.

## Formats - by purpose, not by habit

| Purpose | Prefer | Why |
|---|---|---|
| Icons, logos, anything needing clean scaling | `SVG` | resolution-independent, editable, small |
| Raster with transparency | `PNG` | lossless alpha |
| Website favicon | `ICO` (+ PNG fallbacks) | the browser's expected format |
| Production photos / heavy imagery | `WebP`, then `JPEG` for compatibility | far smaller at equal quality |
| Animation, video | `WebM`/`MP4` by target support | format follows the medium |

Conversion caveats: JPEG has no alpha (transparency flattens); SVG is **not** converted by these
scripts - rasterizing/vectorizing needs a dedicated toolchain and this mode says so instead of
guessing. Full guidance: `references/02-formats-and-conversion.md`.

## Platform assets

Web: favicon set + apple-touch + manifest icons (192/512) + OG image (1200x630). Mobile: app icon sets
per platform (iOS up to 1024, Android mipmaps), and a **splash screen that is not optional**. Desktop
and other platforms: their own icon formats. Check the platform's current requirements - and ask the
user before deciding the visual. Sizes and commands: `references/03-platform-assets.md`.

## Localization - stop depending on someone else's CDN

`localize.py` downloads the icons/fonts/media a project loads from external hosts into the repo,
verifying the bytes so an HTML error page never lands as a "font". Keep the license text the source
ships; downloading makes a file local, not licensed. A webfont CSS endpoint needs one extra step:
fetch the CSS, then the font files it references - and note the CDN picks the format from the
User-Agent (localize sends a browser UA so Google Fonts returns WOFF2, not TTF). See
`references/04-localization.md`.

## Optimization - all media, not just images

- **Images:** `optimize.py` produces WebP/JPEG at a chosen quality, width variants for responsive use
  (`name-320.webp`, `name-640.webp`), thumbnails, and a max-width downscale. Every run ends with a
  per-file **before/after table** (source size, output size, saved %, totals) - quote those numbers.
- **Fonts:** ship WOFF2 (web) or the platform's native format; subset to the glyphs actually used.
- **Audio:** lossy at a purpose-appropriate bitrate, lossless source kept.
- **Video:** a modern codec and a sane bitrate per resolution; generate a poster still.
- **Documents:** ship PDFs named by content, keep the editable source; compression is a PDF-tool job.
- **Audio/video:** use **ffmpeg** directly - probe (`ffprobe`), transcode (`ffmpeg -i in.mp4 -c:v libx264 …`),
  poster (`-frames:v 1`). Bun projects can use `Bun.Image` for native-speed image work and
  `.placeholder()` LQIPs instead of the Python image scripts.

There is no script per medium - the rules are fixed across media; guidance and budgets:
`references/05-optimization.md`, and `inventory.py` reports file counts and sizes per category
(images, fonts, audio, video, documents).

## Conform - one generated render, many delivery files

A generated sheet arrives as a grid of subjects (ten avatars in one 2K render). **Probe** it, **conform**
it, then **review** the files the project ships:

- `sheet_probe.py` measures before anything is cut: content bounds and margins, the layout row by row
  (a staggered sheet has no single grid), the gutters, which interior cut lines of an even split land
  on content, per-cell subject boxes, empty cells, and the largest master the subjects can supply. It
  ends with the master spec to paste into the BOM - `1536x1024 sheet rows 8,8,8,10`. Its delivery
  ceiling is what makes a BOM honest: a 269px subject supports `128@2x`, not `128@3x`.
- `conform.py` splits each cell, trims dead margin, pads to the target aspect (never squash it),
  resizes once at the largest needed size, emits the DPR ladder, names by slot, then verifies every
  file and writes `conform-report.json`. Cut lines go through the **content box**, not the canvas,
  so uneven margins cannot clip the last column; `--bands` cuts down the middle of the measured
  gutters, and a `sheet rows 8,8,8,10` plan does that per row. A `single` master is one slot: used
  whole (no content-box cut, trim or keying unless requested), then fitted, laddered and verified the
  same way.
- `contact_sheet.py` composites the delivered files on a checkerboard and measures their alpha
  edges. Transparency is invisible against white: a sheet is how a halo, an opaque corner or a
  clipped subject becomes visible, and the per-file facts say whether the background was keyed at
  all. It reads, never writes, the asset files.

- **BOM-driven by default.** `--bom bom/<page>.md` reads the slot ids, master/sheet plan and delivery
  spec (size, aspect, format, quality, DPR) written by `collection`. Encoding and quality stay with
  `optimize.py` - conform computes the widths and hands them over; it does not own a second quality
  vocabulary. BOM format: `collection`'s template (one schema owner, linked not copied).
- **Never invent geometry.** Grid and cell size come from the BOM. Without a BOM, `--grid/--cell` or
  `--rows` is required. When the sheet's gutters are not even, the run says so and points at
  `--bands` instead of cutting through subjects; when the image does not show the rows or columns the
  plan claims, it stops with the counts rather than guessing.

- **Never distort, never silently upscale.** Mismatched aspect is padded (transparent or `--pad-color`);
  a cell smaller than the required master is an error unless `--allow-upscale`.
- **Count mismatch stops the run.** If detection finds 9 subjects where the BOM expects 10, it reports
  and exits non-zero instead of guessing which cell is wrong.
- One run = one master: one sheet or one single slot, scoped by `--slots <ids>` (any ids, in sheet
  order) or `--group <prefix>` when the ids share a hyphen prefix. A set that needs more than one
  render is written as one BOM row per sheet (`avatar-01..04`, `avatar-05..08`); each row is its own
  run.

Scale, trimming and padding rules: `references/08-conform.md`. One-off crops with no BOM row stay
in `transform.py`; every generated BOM row goes through conform so its slot id links the render to
the shipped files.

## References and the small code changes

Assets are files *and* the places code points at them. `inventory.py` finds duplicates, files nothing
references, and external asset URLs. Renaming or moving a file is a shell job (`mv` / `Move-Item`), but
it is only half the change: after moving, grep the old name across the project and fix every path that
named it - the reference update is the part agents forget, and it needs the same review as code. The
skill may edit code **only** for this: the paths that name an asset. It does not implement features or
restructure code. Reference styles per stack and the rename protocol: `references/06-references-and-code.md`.

## Boundaries

| Not this | Go instead |
|---|---|
| Asset pipelines, upload processing, storage services, CDN infrastructure | those are application/infrastructure work - `dtb` for the how, the relevant engineering skill for the build |
| Designing a design system or component library | `components`, `denoise`, `impeccable` |
| Writing application features that display assets | the implementation skills |
| Deciding a stack for media tooling | `techstack`, `thebest` |
| Planning which images a page needs, or writing the prompts for them | `collection` (BOM + prompts), then `generate` |
| Generating brand-new artwork from a description | `generate` - this mode normalizes what it produces |

## Files

| Need | Load |
|---|---|
| Naming rules, folder layout, brand-vs-content separation | `references/01-naming-and-organization.md` |
| Format selection, alpha, production formats, conversion caveats | `references/02-formats-and-conversion.md` |
| Favicon/app icon/splash/OG sizes and platform requirements | `references/03-platform-assets.md` |
| Localizing CDN assets: manifests, licensing, webfont CSS | `references/04-localization.md` |
| Optimization for images, fonts and video, with budgets | `references/05-optimization.md` |
| How each stack references assets; rename and inventory protocol | `references/06-references-and-code.md` |
| Splitting a generated sheet into slots, padding, DPR ladder, report | `references/08-conform.md` |
| Exact commands and flags for all fourteen scripts | `references/07-scripts.md` |
