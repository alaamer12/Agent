---
id: contour-map
name: Contour Map
family: canvas-a4
renderer: canvas2d
poster: assets/posters/contour-map.jpg
complexity: XL
source_lines: 457
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Contour Map

## 1. Identity

A survey-chart topographic sheet in motion: six hypsometric bands carrying five
contour levels — two of them bold buff index lines — over a two-octave simplex
surface that slides upward while its shape morphs.

## 2. Perceived look

Banded and faceted rather than smooth. The fill is a muted petrol-to-sand ramp
interrupted every 9 px at 640x400 by three-step hillshade relief. Contours are
crisp 1.2 px lines; the two index levels are 2.9 px buff strokes with a faint
wide halo. Contrast is mid and even, with no focal point beyond wherever the
noise builds a peak. At t = 3 s the frame is full-bleed, with landforms repeating
every 77.63 px.

## 3. Frame anatomy

1. **Ground** — full-rect fill `#020409`, opaque, every frame.
2. **Bands** — 18 paths (6 bands × 3 shades), one rounded cell rect each, alpha
   0.24 in `source-over`.
3. **Depth wash** — gradient (0, 0)→(0.45W, H) in `multiply`:
   `rgba(196, 206, 218, 0.42)` → `rgba(120, 134, 152, 0.6)` at 0.5 →
   `rgba(48, 54, 70, 0.82)`.
4. **Minor contours** — levels 0, 2, 4, alpha 0.2, width 1.2, round joins and
   caps.
5. **Index contours** — levels 1 and 3: 5.0 px halo at alpha 0.05, then a
   2.9 px core at 0.95.
6. **Vignette** — radial at (0.42W, 0.44H), outer radius 0.8·max(W, H), inner
   0.26 of it, `rgba(2, 6, 10, 0)` → 0.52.

Canvas is opaque (`alpha: false`); the host backdrop never shows.

## 4. Motion law

The terrain translates upward at 0.05 px per frame — 3 px/s at 60 fps — by
subtracting `frame·0.05` from the noise y coordinate. Shape change comes only
from the third noise axis advancing 0.00022 per frame (0.0132/s); the second
octave runs 1.6 times faster in z. Because every contour is re-extracted each
frame, lines migrate through the surface rather than travelling with it: a
closed ring around a moving peak opens, splits and closes again. Nothing loops;
the motion is open-ended and frame-rate dependent, with no lifetimes, no
particles and no respawn. At 3 px/s a feature crosses its own 77.63 px width in
25.9 s and the whole 400 px frame in 133.3 s, while one noise cell of z
evolution takes 75.76 s.

## 5. Technique and math

**Grid.** `cell = clamp(sqrt(W·H / 5200), 9, 16)`, `cols = ceil(W/cell) + 1`,
`rows = ceil(H/cell) + 1`, heights in a `Float32Array` of `cols·rows`. At
640x400: cell 9 (raw 7.0165), 73x46 samples, 3240 cells. At 1920x1080: cell 16
(raw 19.9692), 121x69 samples, 8160 cells.

**Height.** With `short = min(W,H)`, `scale = 2π·0.82/short` — one noise unit
per 77.63 px at 640x400, 209.51 px at 1920x1080. `ny = (j·cell −
frame·0.05)·scale`, `nx = i·cell·scale`,
`h = clamp(0.5 + 0.34·(n₁ + 0.2·n₂), 0, 1)` where `n₁ = noise3D(nx, ny,
0.00022·frame)` and `n₂ = noise3D(2.17·nx + 31.4, 2.17·ny + 12.7, 0.000352·frame)`.
Both return −1..1, so h spans 0.092..0.908 and never saturates.

**Bands.** Cell mean of the four corners; `band = floor(mean·6)` clamped 0..5.

**Hillshade.** `g = 14/cell`; `dhdx = (tr + br − tl − bl)·0.5·g`,
`dhdy = (bl + br − tl − tr)·0.5·g`; light `(−0.58, −0.81)`;
`shade = clamp(floor((0.5 + 0.5·(dhdx·lx + dhdy·ly))·3), 0, 2)`. Three steps,
not a gradient, is what reads as relief.

**Contours.** Thresholds `v = (l+1)/6`, l = 0..4: 0.1667, 0.3333, 0.5, 0.6667,
0.8333. Corner bits TL=8, TR=4, BR=2, BL=1; codes 0 and 15 skip, the ten
single-segment codes emit one, and saddles 5 and 10 emit two disjoint segments
with no centre-value test. Crossings interpolate
`t = clamp((v − a)/(b − a), 0, 1)` per edge, 0 when `|b − a| < 1e-6`.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | DPR clamp; backing store 960x600 at 640x400 | L |
| cells | 5200 | 2400–9000 | cell-count budget; cell = sqrt(area/cells) | H |
| minCell | 9 | 6–14 | floor on cell size; thumbnail chunkiness | M |
| maxCell | 16 | 10–24 | ceiling on cell size; facet size at 1080p | H |
| levels | 5 | 3–9 | contour count and band count (levels + 1) | H |
| freq | 0.82 | 0.5–1.4 | noise scale; lower = larger landforms | H |
| octave | 0.2 | 0–0.45 | second-octave amplitude; detail strength | M |
| morph | 0.00022 | 0–0.0006 | z advance per frame; shape evolution speed | M |
| creep | 0.05 | 0–0.2 | px/frame terrain slide, 3 px/s at 0.05 | M |
| shadeStep | 1.2 | 0.6–2.4 | lightness offset between the 3 shade steps | L |
| shadeGain | 14 | 6–20 | slope-to-shade gain, divided by cell | H |
| bandAlpha | 0.24 | 0.12–0.4 | band fill opacity over the ground | H |
| lineWidth | 1.2 | 0.8–2 | minor contour stroke, CSS px | M |
| lineAlpha / indexAlpha | 0.2 / 0.95 | 0.1–0.4 / 0.8–1 | minor and index contour opacity | M |
| indexEvery | 2 | 2–4 | every nth level is an index contour | H |
| indexWidth | 2.9 | 2–4 | index core stroke, CSS px | M |
| glowWidth / glowAlpha | 5.0 / 0.05 | 3–8 / 0–0.12 | index halo; wider reads as mush | M |
| lineSat / lineLight / indexHue / indexSat / indexLight | 34 / 54 / 42 / 62 / 82 | — | minor stroke sat/light; index hue base, sat, light | M |
| warmup | 6 | 0–20 | primed frames before the first paint | L |

## 7. Palette and color

Ground `#020409`. Hypsometric stops, HSL: (199, 62%, 8%), (187, 58%, 18%),
(171, 48%, 29%), (118, 32%, 37%), (66, 40%, 50%), (43, 55%, 65%), (38, 68%, 79%)
at t = 0, 0.22, 0.42, 0.58, 0.73, 0.87, 1. Bands sample this at b/5 and offset
lightness ±1.2. Minor lines: hue + 6 at 34% saturation, lightness clamped
34..54. Index lines: `hsl(44.33, 62%, 82%)` and `hsl(49, 62%, 82%)` — warm buff.
Depth and vignette are near-black teal at low alpha. All values are display
sRGB; the `multiply` wash is what pulls the lower right toward 45% luminance.

## 8. Composition and camera

Full-bleed orthographic top-down, no camera and no perspective. The grid budget
keeps contour density close to constant across sizes, and the noise scale keys
off the short axis, so features stay isotropic in pixels. Wide frames show more
landforms across, tall frames fewer; neither is letterboxed. No safe margins —
contours run off all four edges and are clipped. At very tall aspect ratios the
cell clamp bites later, so the sheet gets finer relative to width.

## 9. Randomness and seeds

Simplex permutation tables are generated at construction and unseeded; any seed
gives the same distribution of terrain. No per-frame `Math.random()` at all.
Warmup of 6 frames advances z to 0.00132 and creep to 0.3 px, which only avoids
opening on the z = 0 slice; the composition is not primed into any particular
state and every seed produces a different, equally valid sheet.

## 10. Performance budget

Per frame: 3240 cells (8160 at 1080p), 2 noise calls per sample, 5 threshold
tests per cell, one rounded rect per cell, 18 band fills plus 7 contour strokes,
and 5 full-frame passes (ground, bands, depth, contours, vignette). 23 Path2D
objects are reallocated every frame. Backing store 960x600 at 640x400 and
2880x1620 at 1080p. Holds 60 fps on a laptop iGPU; the per-cell loop, not
fill-rate, is the cost. Cut order: `levels`, then `cells`, then the index halo.

## 11. Host integration

Standard contract. Mount: get the opaque 2D context, build the noise function,
build the palette once, resize (which allocates heights and paths), run 6
synchronous frames, add a passive resize listener, start the FPS meter, start
RAF. Resize rebuilds the grid and path store from the new CSS size but not the
palette. Teardown cancels the frame, removes the listener, stops the meter and
drops the context, noise function and all arrays. Only external dependency is
`simplex-noise`; no assets.

## 12. Failure modes and tells

- **Long straight chords →** a positive-clamped delta guard flings every
  descending crossing outside its cell → guard on `|b − a|`.
- **Faint grid of seams →** band rects not rounded, so cells overlap and
  double-blend at 0.24.
- **Stair-step contours →** crossings snapped to corners, not interpolated.
- **Coloured static →** too many levels or minor lines above 34% saturation.
- **Contours lost under the fill →** `bandAlpha` raised without `indexAlpha`;
  the 0.95 core must dominate.
- **Engraved relief →** shade sign or light vector flipped.
- **Grey wash →** depth gradient drawn `source-over` instead of `multiply`.

## 13. Tuning knobs

1. `levels` — 3 bold bands, 7 busy chart (3–7).
2. `freq` — 0.6 larger landforms, 1.1 smaller (0.6–1.1).
3. `shadeGain` — 10 flatter, 18 dramatic (8–18).
4. `bandAlpha` — 0.3 heavier fill (0.18–0.34).

## 14. Verification checklist

- Contours closed or edge-terminated; no segment longer than one cell diagonal.
- Six band values countable; two index levels clearly heavier.
- Hues 170–200°; index ink near 45°.
- Bottom-right darker than top-left.
- Full coverage by t = 3 s.
- Compare `assets/posters/contour-map.jpg` for palette, band count and density
  only; its axis-aligned chords are the section 12 bug, so correct output shows
  rings.

## 15. Porting notes

Any 2D canvas works. `Path2D` can be replaced by per-level segment arrays, but
keep one stroke call per level and keep pixel snapping. The noise substitute must
be continuous 3D gradient noise returning −1..1; a 2D substitute loses the morph.
Do not move the per-cell work to a fragment shader without keeping the 3-level
shade quantization and the saddle handling.
