# Optimization - images, fonts, video

Optimization is a medium-specific job. The rule everywhere: **keep the source of truth as authored,
optimize the outputs, and measure before/after** rather than trusting a quality number.

## Images

- **Width variants** for responsive use: `optimize.py --variants 320,640,1280 --format webp`. The app
  then serves the smallest sufficient file instead of the original.
- **Thumbnails**: `--thumbs --thumb-width 240` for lists and previews; never display the full-size
  source as a preview.
- **Downscale past a ceiling**: `--max-width 1600` for hero images; a 6000px source is rarely needed.
- **Format**: WebP (or AVIF where supported) at `--quality 70-85`; JPEG only for compatibility.
- **PNG sources**: optimization means dimensions or conversion, not a quality knob.
- **Budgets** (examples, set the project's own): card thumbnails < 30 KB; inline icons < 10 KB;
  hero images < 200 KB after variants.

```text
source photo.jpg (2800x1600, 1.9 MB)
  -> photo-320.webp   ( 8 KB)
  -> photo-640.webp   ( 26 KB)
  -> photo-1280.webp  ( 91 KB)
```

`optimize.py` prints every output's byte size; quote those numbers when reporting, and use
`benchmark` when the decision needs a measured comparison.

## Fonts

- **Web:** ship WOFF2 only (WOFF as a legacy fallback if the target demands it). TTF/OTF are sources.
- **Subset** to the glyphs actually used: latin subset, not the full CJK table, when the copy is Latin
  only. Subsetting is a dedicated-tool job (e.g. a pyftsubset-style step in the build), not one of this
  skill's scripts.
- **Self-host** the file (localize it) and keep the license text next to it.
- **Limit families/weights**: each weight is a download; variable fonts can replace several.
- **Mobile/desktop:** use the platform's native font packaging, not web formats.

## Video

- **Container/codec:** MP4/H.264 for maximum compatibility, WebM/VP9 or AV1 for smaller modern
  delivery; choose by target support.
- **Resolution and bitrate** go together: 720p at ~2-4 Mbps, 1080p at ~4-8 Mbps are reasonable
  starting points for web delivery; lower for thumbnails/previews.
- **Short previews** (a few seconds, muted) where the UI only needs a hint of motion.
- **Posters:** always generate a still poster image (`transform.py`/`convert.py` on a frame) so the
  video area is not blank before load.
- Conversion is ffmpeg directly: `ffmpeg -i in.mp4 -c:v libvpx-vp9 -crf 32 -b:v 0 -vf scale=1280:-2 out.webm`;
  poster: `ffmpeg -ss 00:00:01 -i in.mp4 -frames:v 1 poster.jpg`.

## Audio

- **Formats:** a compressed lossy format for playback (`MP3`/`AAC`/`OGG` by target), `WAV`/`FLAC`
  only for sources or editing.
- **Bitrate follows purpose:** voice notes ~64-96 kbps mono; music ~128-192 kbps stereo; keep bitrate
  down when the asset is a short UI sound. Sample rate 44.1/48 kHz is the norm; drop to 22/24 kHz for
  speech-only clips.
- **Trim silence** and normalize loudness once, at the source - do not bake fixes per usage site.
- **Sources stay lossless** (`wav`/`flac`); the compressed file is the output.
- Re-encoding is ffmpeg directly: `ffmpeg -i in.wav -vn -c:a libmp3lame -b:a 192k out.mp3`.

## Documents (PDF and friends)

- **Treat a shipped PDF as an asset**: name it by content (`handbook-2026.pdf`, not `doc1.pdf`), keep
  the editable source (`.docx`/`.md`) alongside or referenced, and never overwrite the original.
- **Optimization** usually means: compress images inside the PDF, subset embedded fonts, linearize for
  fast web viewing - done by a PDF toolchain, not by re-saving blindly.
- **Do not flatten a text PDF to images** to save bytes; accessibility and searchability are lost.
- Keep license/attribution pages intact when redistributing third-party documents.

## Measuring

1. Record the source size.
2. Run the optimization.
3. Compare written sizes (the script prints them); confirm visual quality on one representative image
   or clip before applying to the batch.
4. When the choice of format/quality is a real decision, take it to `benchmark` (numbers) and
   `thebest` (verdict) instead of guessing.

## Bun projects - native pipeline instead of Python

When the project runs on Bun (>= 1.3.14), `Bun.Image` is a built-in, zero-dependency, sharp-shaped
pipeline: resize/rotate/convert with SIMD, plus `.placeholder()` which returns a ThumbHash-rendered
<=32px blur as a `data:` URL (a few KB, no client decoder). `scripts/bun-image.ts` wraps it: variants,
optional thumbnail, and the LQIP written next to them. Use it for image-heavy Bun apps; keep the Python
scripts for portability across non-Bun projects.
