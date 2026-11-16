---
id: smoke-wisps
name: Smoke Wisps
family: canvas-a1
renderer: canvas2d
poster: assets/posters/smoke-wisps.jpg
complexity: M
source_lines: 334
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Smoke Wisps

## 1. Identity

Eighty-five translucent lavender puffs rise from four emitters below the frame
and are sheared and rolled by a 3D curl-noise field into loose, twisting plumes.

## 2. Perceived look

Soft and blurred: every mark is a baked radial sprite, so no edge is crisp.
Density is layered — overlapping veils at 33.8–318.8 px diameter build sheets
rather than distinct blobs. Contrast is low; the brightest smoke sits around
30–40% grey against a near-black plum ground. A single cool key glow hangs in the
upper right. No focal point, but the plumes converge lower-centre. At t = 3 s the
wisps reach the middle of the frame in three or four loose columns.

## 3. Frame anatomy

1. **Ground** — diagonal linear gradient from (0, H) to (0.3W, 0):
   `hsl(258, 26%, 7.6%)` → `hsl(250, 24%, 5.2%)` at 0.45 → `hsl(232, 22%, 3.4%)`.
   `source-over`, opaque, repainted every frame.
2. **Key light** — radial at (0.6W + 0.05W·sin(frame·0.0007), 0.2H), radius
   0.66·max(W, H): `rgba(128, 132, 190, 0.1)` → `rgba(78, 74, 128, 0.04)` at
   0.42 → transparent. Drawn in `lighter`, then the composite is reset.
3. **Puffs** — six baked 128 px sprites, `source-over`, per-puff global alpha
   capped at 0.5.
4. **Veil** — vertical gradient `rgba(3, 3, 9, 0.55)` → `rgba(4, 4, 10, 0.1)` at
   0.3 → `rgba(3, 3, 8, 0.16)` at 0.82 → `rgba(2, 2, 6, 0.7)`.
5. **Vignette** — radial at frame centre, radius 0.64·hypot(W, H), inner
   0.3·radius, `rgba(2, 2, 6, 0)` → 0.62.

Canvas alpha is off, so the host gradient is never visible. The puffs are the one
pass that must stay out of the additive composite, and that choice is what sets
the scene's ceiling colour.

## 4. Motion law

Puffs are emitted at y = 1.04H, below the frame, and rise at
`rise·(0.42 + 0.58·(1 − age))·(0.6 + 0.7·depth)` with `rise = 0.0021·H`: 0.84 px
per frame at 640x400, 2.268 px at 1920x1080. At birth that is 0.7098–1.092 px
per frame (42.59–65.52 px/s at 60 fps); at death, 0.2981–0.4586 px per frame
(17.89–27.52 px/s). On top sit the curl velocity and a horizontal wobble of
±0.14 px at 0.004–0.013 rad/frame. Life is 360–620 frames (6–10.33 s), giving
181–481 px of net rise per life at 640x400 (490–1298 px at 1080p). Respawn on
life, off the top at y < −1.4·radius, or past the sides at ±2·radius.
Open-ended.

## 5. Technique and math

Count is `clamp(round(A / 3000), 80, 460)` → 85 at 640x400, 460 at 1920x1080
(691 before the cap). Four strands at 0.22, 0.47, 0.71 and 0.88 of the width, all
at 1.04H, each with a fixed bias uniform in −0.22…0.34.

Initial ages are stratified, not random: puff i takes the strand with index i
modulo 4 and `ageFraction = floor(i / 4) / ceil(count / 4)`, so with 85 puffs the
22 slots per strand give ages 0 … 0.9545 of life. The first frame therefore
already shows a full plume.

Emission jitter widens with age: `column = 0.8·spread·t·W` (0.128W, ±81.9 px at
640x400) plus `bias·t·0.06W`. At t = 0 the jitter is 0.012W.

Radius: `r0 = √A·(0.038 + u·0.052)` → 19.23–45.54 px at 640x400; the drawn radius
is `r0·(1 + 1.5·age)·(0.6 + 0.8·depth)`, so a puff grows 2.5× over its life and
another 1.4× with depth, reaching 67.3–159.4 px (diameter 134.6–318.8 px).

Curl: four 3D simplex samples per puff per frame, at `x ± 7` and `y ± 7`, all at
`0.0021` scale, with the third axis at `frame·0.0009`. Then
`vx = ((n(x, y+7) − n(x, y−7)) / 14)·320` and
`vy = −((n(x+7, y) − n(x−7, y)) / 14)·320`. The 90° rotation of the gradient makes
the field divergence-free, so the plume shears and rolls instead of collapsing
into a column. One noise cell is 476.2 px; 7 px is 0.0147 cell units per sample,
small enough for a clean derivative.

Envelope is `sin(π·age)^1.25`; puffs below 0.004 are skipped. Alpha is
`0.58·u` with u in 0.62…1 → 0.3596–0.58, multiplied by the envelope and clamped to
0.5; since `u > 0.5/0.58 = 0.862` clips, **36.3%** of puffs clip at their peak.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device-pixel-ratio clamp | L |
| puffArea | 3000 | 1800–5000 | area per puff; 85 at 640x400 | H |
| minPuffs | 80 | 40–120 | floor for small surfaces | M |
| maxPuffs | 460 | 300–700 | cap at 1080p | L |
| strands | [0.22, 0.47, 0.71, 0.88] | 1–6 values | emitter x positions as width fractions | H |
| emitterY | 1.04 | 0.95–1.15 | emitter line as height fraction | M |
| radiusRange | [0.038, 0.09] | 0.02–0.12 | base radius as √A fraction | H |
| grow | 2.5 | 1.6–4 | radial growth over one life | H |
| riseShare | 0.0021 | 0.001–0.004 | rise per frame as height fraction | H |
| life | [360, 620] frames | 240–900 | plume height and turnover | H |
| noiseScale | 0.0021 | 0.0008–0.004 | inverse curl cell; 476.2 px | H |
| epsilon | 7 | 2–20 | finite-difference step in px | H |
| swirl | 320 | 100–600 | curl→px/frame gain | H |
| evolution | 0.0009 | 0–0.003 | third-axis advance per frame | M |
| spread | 0.16 | 0.05–0.4 | emission column width at end of life | M |
| puffAlpha | 0.58 | 0.3–0.8 | pre-envelope alpha; capped at 0.5 | H |
| warmup | 300 | 120–500 | hidden frames before first paint | M |

## 7. Palette and color

Ground `hsl(258, 26%, 7.6%)` → `hsl(250, 24%, 5.2%)` → `hsl(232, 22%, 3.4%)`:
a dark plum to blue plum. Key light `rgba(128, 132, 190, 0.1)`, a cool violet-grey.
Tints are neutral lavender at low saturation: `rgb(178, 170, 208)` ≈ hsl(252.6,
28.8%, 74.1%), `rgb(150, 158, 196)` ≈ hsl(229.6, 28%, 67.8%), `rgb(204, 190,
214)` ≈ hsl(275, 22.6%, 79.2%). Hard sprites peak at alpha 0.84, soft ones at
0.66, both authored in display sRGB; the gradient stops interpolate in sRGB.
Because overlaps are `source-over`, the plume saturates at the sprite colour,
never at white.

## 8. Composition and camera

No camera. Emitters span 22–88% of the width and start below the frame, so the
plume bases are cut off and the composition has no visible floor. Smoke fills the
lower two-thirds; the top tenth stays within a few percent of black. Emitter
spacing scales with width while plume height scales with height, so wide frames
show broader, more separated columns. Density thins at 1080p: 3.32×10⁻⁴ puffs per
px² at 640x400 against 2.22×10⁻⁴ at 1920x1080.

## 9. Randomness and seeds

`Math.random()`, no seed; any seed gives the same distribution. Random: depth
0.35–1, r0 fraction, sprite index (6), wobble, seed 0–90, alpha multiplier
0.62–1, and the per-strand bias. Deliberately not random: the initial age ramp,
which is stratified by slot so the plume is full on frame 1. Warmup: 300 frames
(5 s).

## 10. Performance budget

85–460 puffs, four 3D noise samples each per frame (340–1840 samples), one sprite
`drawImage` each, sprites upscaled as far as 319 px. Fill rate dominates: 250 px
translucent quads overlapped many times. DPR capped at 1.5. Holds 60 fps at
1080p on a laptop iGPU. Cut order: puff count, then `grow`, then DPR, then swap
the 3D curl for two 2D noise gradients.

## 11. Host integration

Standard contract. Six sprites are baked at mount; the context is `alpha: false`.
Resize recomputes `rise` from the new height, then rebuilds strands and puffs —
which reinstates the stratified age ramp immediately, with no second warmup. A
passive window resize listener is the only event. Teardown cancels the RAF,
removes the listener, stops the meter and drops sprites, strands and puffs.

## 12. Failure modes and tells

- **Plume turns white or chalky** → puffs drawn with `lighter`; they must be
  `source-over`.
- **Stack of identical bubbles** → only one sprite family; the mix of hard and
  soft falloffs is what breaks the repetition.
- **Smoke never leaves the bottom** → warmup skipped (300) or `rise` not
  recomputed after resize.
- **Marked vertical columns** → `swirl` at 0, or curl from two independent noise
  calls instead of one rotated gradient.
- **Cone fans instantly** → `spread` or emission jitter raised.
- **Visible square edges** → last sprite stop above 0, or nearest-neighbour
  upscaling.
- **Milky grey frame** → the 0.5 alpha cap removed, or count raised with
  `puffAlpha` unchanged.
- **Wisps mid-air after resize** → expected: the rebuild seeds a full age ramp.

## 13. Tuning knobs

1. `swirl` — 180 for a lazy drift, 500 for fast rolling.
2. `life` — longer for taller plumes, shorter for a busier turnover.
3. `grow` — 1.8 for tighter puffs, 3.5 for billowing sheets.
4. `puffArea` — lower for density, raise before touching `puffAlpha`.
5. `riseShare` — 0.0012 for a low haze, 0.003 for fast risers.

## 14. Verification checklist

- 85 puffs at 640x400, 460 at 1920x1080.
- Upper 10% of the frame within a few percent of black.
- Background hue 232–258; puffs neutral, hue 230–275, saturation under 30%.
- No pixel in the smoke brighter than about 60% grey.
- Every puff edge reaches zero before the sprite boundary; no boxes.
- Plumes lean and roll; no perfectly vertical column.
- Compare to `assets/posters/smoke-wisps.jpg` for plume height and softness.

## 15. Porting notes

Use a true 3D simplex; a 2D curl loses the rolling and reads as flowing hair.
Keep `source-over` and, in a premultiplied pipeline, premultiply the sprite. The
sprites are upscaled up to 2.5×, so bilinear filtering is required — nearest
sampling shows facets on every puff.
