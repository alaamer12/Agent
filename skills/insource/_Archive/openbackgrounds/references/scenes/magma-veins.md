---
id: magma-veins
name: Magma Veins
family: webgl-f1
renderer: webgl1
poster: assets/posters/magma-veins.jpg
complexity: M
source_lines: 326
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Magma Veins

## 1. Identity

A cooled lava crust split by a branching network of glowing seams. The cracks
are the zero set of a doubly warped value-noise field, so they fork and close
into islands rather than tracing contours.

## 2. Perceived look

Almost black basalt fills the frame, textured by a faint 1.5 px grain. Thin
orange seams wander across it in a closed network; the brightest junctions are
near white-gold, and every seam is bordered by a dim 10–25 px maroon halo. A
second, much finer web of hairlines sits inside the broad plates. In the poster
a main seam forks near center; the upper right is unbroken crust with hairlines.

## 3. Frame anatomy

1. **Crust plate** — one oversized `TRIANGLES` draw, vertices (−1, −1), (3, −1),
   (−1, 3), no index buffer, no depth buffer.
2. **Opaque pass** — alpha is always 1.0. Context flags are `alpha: false,
   antialias: false, depth: false`; blending is off and no clear color is set.

## 4. Motion law

Time is seconds. The sample point drifts by (sin 0.05t, cos 0.042t)·0.35 units,
at most 0.0175 and 0.0147 units/s, with periods 125.66 s and 149.6 s. The field
advects at (0.055, −0.033) units/s (9.17 and 5.5 px/s at a 400 px short axis).
The warp layers move faster: 0.6 and 0.4 units/s for the first, 0.5 and 0.3
units/s before the 1.13 scale for the second. A pressure wave modulates
brightness at 0.4 rad/s (period 15.708 s).
Pointer offsets the sample by 0.25 units, at most 100 px, unclamped. Motion is
open-ended.

## 5. Technique and math

Coordinates are p = (fragCoord − 0.5·resolution)/min(width, height). The sample
is c = 2.4·p + 0.25·pointer + (sin 0.05t, cos 0.042t)·0.35.

The noise is 2-octave value noise. hash21 maps a lattice point by
p ← fract(p·(123.34, 456.21)), then p ← p + dot(p, p + 45.32), returning
fract(p.x·p.y). The offset is scalar and added to both channels, so the two
coordinates stay correlated. vnoise interpolates the four corner hashes with
f·f·(3 − 2f) in each axis. fbm sums a = 0.55 then 0.275 after remapping
x ← 2.1x + (1.7, 9.2), so its range is 0–0.825, not 0–1.

crust(x, t) builds two warp values:

- w.x = fbm(x + (1.3, 4.7) + (0.6t, −0.4t))
- w.y = fbm(1.13x + (8.2, 0.7) − (0.5t, 0.3t))
- crust = fbm(x + 1.5·w + (0.055t, −0.033t))·2.15 − 1.

The signed field spans −1 to +0.774; its zero set sits at fbm = 0.465116, so it
is negative over most of the frame, giving wide dark plates and tight bright
seams.

Main cracks use f = crust(c, t): heat = exp(−8.5|f|), core = exp(−26|f|), and
crack = 0.6·heat² + core. A second evaluation at c·2.7 + (13, 4) with time 0.4t
feeds a hairline term exp(−55|f2|)·0.32. With median |∇f| 0.807 per c-unit
(166.67 px), heat reaches 1/e within 24 px, core within 7.9 px, hairline within
1.4 px.

A breath factor, 0.62 + 0.42·sin(0.8c.x + 0.45c.y − 0.4t), ranges 0.2–1.04;
crack is multiplied by 0.55 + breath, giving 0.75–1.59. Grain is
hash21(floor(p·260)) — 260 cells per unit, a 1.538 px cell — and speck =
0.8 + 0.35·grain.

The color is deep + crustColor·speck·(0.35 + 1.6·heat) + magma·crack·0.9 +
ember·crack²·1.1 + crustLit·heat²·0.55, then tonemapped 1 − exp(−1.6·col) and
vignetted by 1 − 0.6·smoothstep(0.35, 1.1, |p|). The crust color is modulated
only by the positive heat term and the grain — the signed field is not multiplied
into the color — so plates stay dark wherever heat is near zero.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| scale | 2.4 | 1.2–4 | vein density | H |
| warp | 1.5 | 0–3 | branchiness of the network | H |
| crackGlow | 8.5 | 4–14 | halo width | H |
| crackCore | 26 | 10–40 | white-hot core width | H |
| detail | 2.7 | 1.5–4 | frequency of the hairline web | M |
| hairlineFreq | 55 | 30–90 | hairline falloff steepness | M |
| pointerGain | 0.25 | 0–0.6 | pointer sample offset, units | L |
| flow | 0.055 | 0–0.12 | field advection speed | M |
| hairlineGain | 0.32 | 0.1–0.6 | fine crack brightness | M |
| breathRate | 0.4 | 0.1–0.8 | pressure-wave period | M |
| grainCell | 260 | 100–400 | grain size | L |
| exposure | 1.6 | 1–2.5 | tonemap strength | H |
| vignette | 0.6 | 0.3–0.9 | corner darkening | M |

## 7. Palette and color

Deep `#030202`, crust `#0E0D10`, crust-lit `#6B210A`, magma `#FF4D05`, ember
`#FFDB57`. All are display sRGB constants fed into the exponential tonemap, not
applied after it. The
magma term is thin (0.9·crack) while ember is quadratic (1.1·crack²), so only
the seam cores reach gold; halos stay at the darker orange. The vignette removes
53% of brightness at the poster corners and 58% at 16:9.

## 8. Composition and camera

Orthographic top-down on an infinite sheet, full-bleed, no horizon. Plates span
100–250 px at poster size. The eye follows the brightest continuous seam. Wider
windows reveal more network, unscaled, since p uses the short axis. The vignette
starts at |p| = 0.35, well inside the frame.

## 9. Randomness and seeds

Fully deterministic: hash21 is a pure function of lattice position, and there is
no RNG, seed or warmup. The first frame at t = 0 is valid. A texture-based noise
changes the seam layout.

## 10. Performance budget

Two crust evaluations per fragment, each three fbm calls, each two vnoise calls
of four hashes: 48 hash21 evaluations plus one for grain. At DPR 1.5 the poster
backs 960x600 = 576,000 fragments; 1080p is 2880x1620 = 4,665,600. It is
arithmetic-bound. Mediump shows no banding because values stay small.

## 11. Host integration

Standard holder sizing: `offsetWidth`/`offsetHeight` times DPR, clamped at 1.5,
backing store reassigned on resize. `pointermove` is bound to the window and
normalized there, so pointer influence depends on window size, not canvas size.
Pointer is unsmoothed, so the plate can jump 100 px. Teardown cancels the frame,
removes both listeners, deletes buffer and program, and releases the context with
`WEBGL_lose_context`. Only window resizes are observed.

## 12. Failure modes and tells

- **Cracks follow smooth noise contours →** warp layers omitted; the zero set of
  raw fbm is rounded and closed, not branching.
- **Bright blobs instead of branching seams →** the `2.15·fbm − 1` remap is
  missing; without it the field no longer cuts into dark plates and bright
  regions.
- **Whole frame glows uniformly →** the absolute value was dropped or the signed
  field clamped, so heat saturates everywhere; keep `abs(f)` only inside the
  exponentials.
- **Seams pulse in unison →** breath term removed; the 0.55 + breath product is
  what makes veins swell locally.
- **Washer look →** exposure or ember gain raised; cores must stay small.

## 13. Tuning knobs

1. `scale` — lower for larger plates and fewer seams (1.8).
2. `warp` — raise for more tortured branching (2.2).
3. `crackGlow` — lower for tighter halos (6.5).
4. `detail` — raise for a denser hairline web (3.4).

## 14. Verification checklist

- Crust is neutral black, not brown, away from seams.
- Seam cores are near `#FFDB57`; halos fade through `#FF4D05` and `#6B210A`.
- Hairlines are visible inside plates at 1.4 px scale.
- Grain is present but never larger than about 2 px.
- Corners fall to roughly half brightness; no hard vignette edge.
- `assets/posters/magma-veins.jpg`: same fork-and-rejoin layout at the center.

## 15. Porting notes

Keep the exact 2.15 − 1 remap of the field and the 0.825 fbm ceiling; normalizing
fbm to 0–1 shifts the zero set and changes the plate-to-seam ratio. Preserve the
scalar hash offset — a vector offset gives a different, more uniform layout. The
two warp layers must move at their own speeds; freezing them leaves a static,
contour-like network. Sample the hairline field at 2.7x frequency and 0.4x time.
