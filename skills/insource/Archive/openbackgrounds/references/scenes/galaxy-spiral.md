---
id: galaxy-spiral
name: Galaxy Spiral
family: webgl-f3
renderer: webgl1
poster: assets/posters/galaxy-spiral.jpg
complexity: L
source_lines: 514
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Galaxy Spiral

## 1. Identity

A three-armed spiral galaxy seen near face-on turns slowly in a black sky, a warm
white core surrounded by blue arm ridges and dust, with a sparse starfield behind.

## 2. Perceived look

Additive pointillism. The core is a dense warm-white glow — at 640x400 roughly
40–60 px wide — tapering into three faint blue arms that spiral out to about
two-thirds of the frame height. Arm ridges read as soft blue streaks because the
star sprites are themselves soft (a Gaussian-ish falloff), and their brightness
sums where they overlap. A pink HII tint flecks the mid-radius arms. The
background is nearly black; the sky stars are single, dim points. Edges are all
soft; nothing aliases. Contrast is extreme: the core is near white, the outer
disc ten times dimmer.

## 3. Frame anatomy

One draw call of `POINTS`; every star is a point sprite sized in the vertex
shader. Additive blending (`SRC_ALPHA, ONE`), depth test off, depth write off.
The buffer is cleared to `rgb(0.004, 0.005, 0.013)`.

1. **Clear** — near-black navy ground.
2. **Sky stars** — 1500 points stored in view space, unaffected by galaxy motion.
3. **Arm stars** — up to 7000 authored, surviving a clump gate, sizes 0.0061–0.0113
   for ordinary stars and 0.0132–0.0226 for the 4.5% giants.
4. **Bulge stars** — 2400 points inside radius 0.36, warm and dim.
5. **Arm haze** — 1500 large soft sprites following the arms, alpha 0.02–0.046.
6. **Core haze** — 200 large sprites inside radius 0.34.

Canvas is opaque (`alpha: false`, `antialias: true`); no host backdrop shows.
Points are drawn in buffer order, which is sky first — but additive blending
makes order irrelevant to the result.

## 4. Motion law

Rigid pattern rotation 0.035 rad/s (179.5 s per turn). On top of it a
differential shear `0.5 · (1 − e^(−0.045 t)) · max(0, 1/(0.3 + r) − 0.62)`:
inner radii lead, the term saturates with a 22.2 s time constant, so the arms
overtake once and then drift together instead of winding into a smear. Each star
also wobbles ±0.025 rad (the `wobble` gain 0.5 times 0.05) with a radius-dependent
frequency `0.35 + 1.3/(0.3 + r)`, and ±1% in radius (0.5 times 0.02). The disc tilts
`0.34 + 0.06 sin(0.024 t)` (261.8 s) and yaws `0.12 sin(0.017 t)` (369.6 s);
sky stars twinkle at 1.9 rad/s with per-star phase. Open-ended; no loop.

## 5. Technique and math

**Storage.** Each vertex is 8 floats: `a_polar = (radius, angle, height, isSky)`
and `a_meta = (seed, size, soft, brightness)`. All motion happens in the vertex
shader; the buffer never changes after upload.

**Arm geometry.** A logarithmic spiral: `angle(radius) = 2.25 ln(radius / 0.14)`,
plus `arm · 2π/3` for the three arms. 2.25 rad per e-fold is about one full turn
across `ln(2.5/0.14) = 2.88`, which is what keeps the arms from stacking on each
other at the center. Radius is sampled `0.14 + 2.36 · u^0.58`, biased outward;
azimuth scatter is Gausian with σ = `0.042/(0.22 + r)`, so the arms are tight
inside and diffuse outside. Height σ is `0.03 (1 + 0.9 e^(−2.6 r))`, a thin disc
that thickens at the bulge.

**Clumping.** 2D simplex noise (the `simplex-noise` package, seeded separately
with `seed + 991`) at `(4.6 r, 12 arm)` yields `clump ∈ [0.45, 1.0]`; a star
survives with probability `0.05 + 0.62 clump`, i.e. 33–67%. This, not any
per-star brightness change, is what makes the arms look segmented into star
forming knots. Remove the gate and the arms become continuous ribbons.

**Projection.** Clip position is `(q.xy · focal / w, 0, w)` with `w = q.z + 5.2`,
so after the perspective divide the on-screen radius is `R · focal / (z + 5.2)²`
— an inverse-square magnification, deliberate. `focal = 7.2 · min(1, aspect/1.6)`
so narrow viewports shrink the disc instead of cropping the arms; the x focal is
divided by aspect to keep circles round. At 640x400 and 1920x1080 the disc
diameter covers 0.67 of the short axis.

**Point rendering.** Size is `size · focal_y · height · 0.5 / w` clamped to
1–150 px, so sprites shrink with distance but never vanish. The fragment
discards outside radius 0.5 of the point, then `k = 1 − 2d`,
`halo = k^(3.2 − 2·soft)`, `core = k^8 (1 − soft)`. Soft haze sprites therefore
have a linear-ish falloff; hard stars have a bright core. Color is added warm
white at 85% of the core term, which is why every star has a hot center.
About 7% of the galaxy stars (`step(0.93, fract(seed·7.31))`) are HII knots,
gated to mid-radius by `smoothstep(0.28, 0.55, rt)` and mixed 85% toward
`(1.0, 0.4, 0.7)`; the sky field is excluded.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| seed | 20260923 | any | star layout, arm clumping | H |
| arms | 3 | 2–4 | number of spiral arms | H |
| armStars | 7000 | 3000–12000 | arm density before gating | H |
| bulgeStars | 2400 | 800–4000 | core density | H |
| hazeStars | 1500 | 500–3000 | arm glow smoothness | M |
| coreHazeStars | 200 | 0–600 | core glow size | M |
| skyStars | 1500 | 0–4000 | background star density | L |
| rMin | 0.14 | 0.1–0.3 | inner disc radius | M |
| rMax | 2.5 | 1.5–3.5 | outer disc radius / framing | H |
| wind | 2.25 | 1.2–3.2 | arm pitch; higher = more wraps | H |
| armWidth | 0.042 | 0.02–0.08 | arm thickness | H |
| thickness | 0.03 | 0.015–0.06 | disc height | M |
| patternSpin | 0.035 rad/s | 0–0.1 | rigid rotation | M |
| shear | 0.5 | 0–1.0 | differential overtake | M |
| shearRamp | 0.045 | 0.02–0.08 | how fast shear saturates | M |
| tilt | 0.34 | 0.1–0.6 | disc obliquity | H |
| wobble | 0.5 | 0.2–0.8 | per-star wobble gain; ×0.05 rad azimuth and ×0.02 radius | M |
| refAspect | 1.6 | 1.2–2 | aspect below which focal shrinks to keep the disc framed | L |
| distance | 5.2 | 4–8 | camera distance | H |
| focal | 7.2 | 5–10 | disc coverage of the frame | H |
| strength | 0.85 | 0.6–1.0 | global alpha | M |

## 7. Palette and color

Center `#FFBD61` warm gold, mid `#FFF5E0`, outer `#6BA1FF` blue; HII knots
`#FF66B3` at 85%; sky stars `#C7D9FF`. The radial ramp is
`mix(gold, white, smoothstep(0, 0.2, r/2.5))` then
`mix(_, blue, smoothstep(0.15, 0.9, r/2.5))`. Alpha is per-star brightness times
a depth fade (1 down to 0.72 with distance) times 0.85, and each sprite
multiplies by its own falloff. Additive blending in display space means
overlaps go toward white without any explicit tone map; the clear color supplies
the only darkness.

## 8. Composition and camera

The disc is centered and covers 0.67 of the short axis; the bright core occupies
about the central sixth. Wide aspect glimpses the outer arms in full; narrow
aspect shrinks the focal so the disc still fits. Sky stars are spread over
±5.2 × ±3.4 view units, which is wide enough to fill the corners. The bottom of
the frame is usually the emptiest because the tilt pushes the near arm down and
the disc's inverse-square magnification throws the near side slightly out of
frame.

## 9. Randomness and seeds

mulberry32, seed 20260923, plus a second mulberry32 instance at seed + 991 for
simplex noise. Gaussian values use Box-Muller from the same stream. Survival,
size, brightness, and HII membership are all drawn in a fixed order, so the
layout is byte-identical across runs. No warmup: the first frame is the final
distribution.

## 10. Performance budget

One draw call, roughly 8–10k point sprites: the 7000 arm stars survive the clump
gate at 33–67% (2.3–4.7k), plus 4,100 bulge, haze, core-haze and sky points.
Fill rate is the whole cost: additive blending with soft sprites up
to 150 px, average maybe 8–14 px. 60 fps at 640x400 and 1080p on desktop;
integrated GPUs drop at 4K. Cut order: DPR, armStars, haze sprite size, then the
sky field.

## 11. Host integration

Standard contract, no pointer input. Requires the `simplex-noise` package only
for the clump field — any 2D simplex returning −1…1 works. Resize recomputes
buffer size and focal; the composition keys off aspect, so a rotation reflows the
disc instead of cropping it. Teardown deletes buffer and program, drops the
vertex array reference, and loses the context.

## 12. Failure modes and tells

- **Arms are continuous ribbons →** the clump survival gate was removed or its
  probability raised toward 1; the noise segmentation is the texture.
- **Arms wind into a pinwheel smear →** shear is unbounded — the `ramp` term or
  the `max(0, 1/(0.3+r) − 0.62)` clamp is missing.
- **Galaxy is huge and cropped →** `focal` or `distance` changed without
  respecting the inverse-square divide; on-screen radius is `R·focal/distance²`.
- **Galaxy is a tiny dot →** the same ratio, in the other direction; both
  constants must move together.
- **Core is a hard white disc →** star sizes too large or brightness too high;
  additive overlap saturates.
- **Sky stars move with the galaxy →** the `isSky` flag is not forcing `q` back
  to the stored view-space position.
- **Stars flicker as the camera wobbles →** point size is not scaled by `1/w`.
- **Arms are grey →** the radial color ramp endpoints were averaged instead of
  mixed by `r/rMax`.

## 13. Tuning knobs

1. `wind` — arm tightness (1.8–2.8).
2. `focal` with `distance` — how much frame the disc owns.
3. `armStars` — ridge continuity versus graininess.
4. `tilt` — face-on versus a raked disc.
5. `shear` — how strongly the inner arms overtake (0.3–0.8).

## 14. Verification checklist

- Warm white core with three blue arms leaving it, not four.
- Arms visibly brighter along ridges than between them.
- Sparse isolated stars outside the disc.
- No hard edges anywhere; the core's brightest part is a soft blob.
- Rotation is slow and smooth; no frame-to-frame popping.
- Black-to-navy background, never grey.
- Compare with `assets/posters/galaxy-spiral.jpg`: core size and arm pitch
  match; the outer arms are faint in the poster at t = 3.5 s.

## 15. Porting notes

The inverse-square projection is a deliberate look (a wide-angle magnification),
not a bug — reproduce `q.xy·focal/w` with clip w equal to `w`. A conventional
`-1/0` projection will make the disc roughly twice as large. In three.js use
`Points` with a custom `ShaderMaterial`, `sizeAttenuation` handled manually, and
`AdditiveBlending`; disable tone mapping or the core clips to flat white.
