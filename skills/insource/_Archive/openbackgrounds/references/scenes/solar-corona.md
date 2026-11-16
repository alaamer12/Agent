---
id: solar-corona
name: Solar Corona
family: webgl-f1
renderer: webgl1
poster: assets/posters/solar-corona.jpg
complexity: M
source_lines: 327
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Solar Corona

## 1. Identity

A black solar disc ringed by a white-hot limb, with orange-gold filaments
streaming outward into a dark field. Sampled in direction space, the corona
converges without a polar seam.

## 2. Perceived look

At 640x400 the disc is 160 px across and pure black except for its 5–6 px rim,
which peaks near white. Filament streaks run 100–300 px outward, densest within
80 px of the limb and fading by 350 px; they are thin, ragged and often forked.
The far field is nearly black with a faint warm haze and a few single-pixel
blue-white stars. The disc is centered.

## 3. Frame anatomy

1. **Single pass** — one oversized `TRIANGLES` draw, vertices (−1, −1), (3, −1),
   (−1, 3); no index buffer, no depth.
2. **Opaque** — alpha is always 1.0; the context uses `alpha: false, antialias:
   false, depth: false`, blending is off and no clear color is written.

## 4. Motion law

Time is seconds. The noise's radial coordinate is advected by 0.13t, so
filaments stream outward at 0.0765 units/s (30.6 px/s at a 400 px short axis);
the second octave moves at 0.065 units/s (26 px/s). Filaments flicker at 2.1
rad/s (2.99 s period) with phase 28n. A slower arc system modulates them at 0.5
rad/s (12.566 s period). The direction term has no time, so the corona does not
rotate. Stars are static except for pointer parallax. Pointer shifts the whole
frame by 0.03 units, about 12 px.

## 5. Technique and math

With p = (fragCoord − 0.5·resolution)/min(width, height), add 0.03·pointer, take
r = |p| and dir = p/r. The field samples 3D value noise on a cylinder: the first
two coordinates are dir·4.4, a circle of radius 4.4, and the third is
1.7r − 0.13t. Hence radial threads and no atan seam.

n = (vnoise3(dir·4.4, 1.7r − 0.13t) + 0.55·vnoise3(10.56·dir + 7.3, 3.4r −
0.221t))/1.55, so n spans 0–1, mean 0.5, median 0.464. fil =
max(0, n)^4.6·2.4, then multiplied by 0.72 + 0.42·sin(2.1t + 28n), which spans
0.30–1.14, and by 0.55 + 0.9·loop, where loop = 0.55 + 0.45·sin(9r − 0.5t +
2·dir.x + 3·dir.y) spans 0.1–1.0, so the second factor is 0.64–1.45.
Approximately 61% of fragments have fil above 0.05, 18% above 0.2, and the
maximum is 1.306.

Three radial envelopes:

- atten = exp(−max(0, r − 0.2)·1.15), 1/e at Δr = 0.8696 (348 px);
- limb = exp(−(min(|r − 0.2|/0.014, 5))²), a 5.6 px Gaussian;
- halo = 0.28·exp(−(min(max(0, r − 0.2)/0.42, 5))²), a 168 px Gaussian.

The disc is covered by cover = 1 − 0.998·(1 − smoothstep(0.19, 0.204, r)), so it
is 0.002 inside the disc and 1 outside — effectively a black silhouette with a
5.6 px transition (the same width as the limb).

Stars are one per 150-cell grid (2.667 px cells): a 7th-power point of radius
0.24 px, shown only where hash21(cell) ≥ 0.972, about 2.8% of cells. They are
static in screen space.

Color accumulates as deep + (0.6, 0.7, 1.0)·star·cover + orange·(0.55·fil +
halo)·atten·cover + gold·fil·atten·cover + hot·0.55·fil²·atten·cover +
hot·0.85·limb + mix(orange, gold, 0.5)·1.4·halo·cover, then tonemaps
1 − exp(−1.5·col) and vignettes by 1 − 0.55·smoothstep(0.5, 1.25, r). The limb
is the only term without cover or atten, so it stays a bright ring over the black
disc, and the halo is added twice — once attenuated, once not.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| discRadius | 0.2 | 0.1–0.3 | limb and disc size | H |
| angularFreq | 4.4 | 2–8 | number of angular lobes | H |
| radialFreq | 1.7 | 1–3 | radial filament scale | M |
| flow | 0.13 | 0–0.3 | outward stream speed | M |
| filamentSharpness | 4.6 | 2–8 | filament thinness | H |
| fade | 1.15 | 0.5–2 | corona falloff | H |
| limbWidth | 0.014 | 0.006–0.03 | rim thickness | H |
| haloWidth | 0.42 | 0.2–0.8 | broad glow reach | M |
| haloGain | 0.28 / 1.4 | 0.1–0.6 | attenuated and unattenuated halo weights | M |
| starGrid / starGate | 150 / 0.972 | — | star cells per unit and presence gate | L |
| exposure | 1.5 | 1–2.5 | tonemap strength | H |
| vignette | 0.55 | 0.3–0.8 | outer darkening | M |

## 7. Palette and color

Deep `#050201`, orange `#FF520D`, gold `#FFC74D`, hot `#FFF2CC`. Values are
display sRGB constants fed into the exponential tonemap, not applied after it.
Filaments read gold because the gold
term is linear in fil while hot is quadratic and only reaches 0.55·fil²; orange
appears in the halo and at filament edges. The limb is hot white. The vignette
keeps 65.1% of brightness at the poster corners and 57.3% at 16:9.

## 8. Composition and camera

Orthographic, full-bleed, no horizon; the disc is a flat circle. Because noise
lives on the direction vector, the flat frame still reads as spherical:
filaments fan out in every direction and bunch near the limb. The disc spans
160 px at 640x400 and 432 px at 1080p; narrower windows crop the corona, wider
ones reveal more black sky. No safe area; the only offset is the pointer shift.

## 9. Randomness and seeds

None. hash31 is a pure lattice hash and hash21 supplies the star mask; there is
no RNG, seed or warmup. The first frame is valid. Stars never twinkle; neither
mask nor position depends on time.

## 10. Performance budget

Two vnoise3 evaluations, eight hash31 each, plus one hash21 for stars: 17 hashes
per fragment, with two pow calls and several exp. At DPR 1.5 the poster backs
960x600 = 576,000 fragments; 1080p is 2880x1620 = 4,665,600. Arithmetic-bound;
mediump suffices because noise coordinates stay below 30.

## 11. Host integration

The holder is sized by `offsetWidth`/`offsetHeight` times DPR, clamped at 1.5;
the backing store is reassigned on resize. `pointermove` is bound to the window
and normalized by window size, so a small canvas in a large window sees smaller
parallax. Teardown cancels the frame, removes both listeners, deletes buffer and
program, and releases the context with `WEBGL_lose_context`. Container-only
resizes are missed; there is no ResizeObserver.

## 12. Failure modes and tells

- **Visible pie seam →** direction replaced by atan; sampling dir directly is
  what removes it.
- **Blobby clouds, no threads →** angular and radial frequencies swapped, or the
  radial coordinate not stretched by 1.7.
- **Filled disc →** cover omitted, so filaments brighten the interior.
- **Grey disc instead of black →** the 0.998 factor lowered toward 0, letting
  additive terms leak inside; at 0.998 the interior cover is only 0.002.
- **No rim →** limb multiplied by cover or atten.
- **Uniform glow with no streaks →** filament sharpness lowered below about 3.

## 13. Tuning knobs

1. `discRadius` — raise for a larger disc and wider limb (0.26).
2. `angularFreq` — raise for finer, more numerous filaments (6.0).
3. `filamentSharpness` — raise for thinner threads (6.0).
4. `fade` — lower for a corona that reaches the corners (0.8).

## 14. Verification checklist

- Disc interior is black to within a few code values; only the rim is bright.
- Rim thickness is about 5.6 px at 640x400 and falls off both inward and outward.
- Filaments are radial, forked and denser near the limb than at r = 0.8.
- Stars are sparse single-pixel points, not twinkles.
- Corner brightness is 65% of center at poster size.
- `assets/posters/solar-corona.jpg`: centered black disc, white limb, gold
  radial filaments on black.

## 15. Porting notes

Sample the noise with a 3D coordinate (dir·angularFreq, radialFreq·r − flow·t),
not with polar angle and radius separately; that cylinder yields seamless radial
threads. Keep the limb outside the cover multiplication, or the rim disappears
inside the silhouette. Preserve the 0.55/0.45 octave weight and the 1.55
normalizer; they set both contrast and the 0.464 median. The star grid is
screen-space and sub-pixel, so keep DPR at 1.5 or higher.
