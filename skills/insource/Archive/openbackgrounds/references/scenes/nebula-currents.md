---
id: nebula-currents
name: Nebula Currents
family: webgl-f1
renderer: webgl1
poster: assets/posters/nebula-currents.jpg
complexity: S
source_lines: 251
dpr_max: 1.6
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Nebula Currents

## 1. Identity

Six rotating, self-warping wave layers accumulate into a soft blue-violet
nebular dome that drifts just below center.

## 2. Perceived look

Extremely soft and full-bleed: no lines, no grain, only overlapping gradients
with a 200–400 px core and a 100 px falloff. The center is a saturated blue
(0.07, 0.24, 0.49) that drifts toward violet at the layer edges; all four
corners are near black. There is no focal detail.

## 3. Frame anatomy

1. **Host backdrop** — no ground. Canvas `alpha: true`,
   `premultipliedAlpha: false`; alpha never exceeds 0.65, so the host's
   `#000000`–`#1A0033` gradient darkens the rim.
2. **Layer accumulation** — one four-vertex `TRIANGLE_STRIP`, blending
   `ONE, ONE_MINUS_SRC_ALPHA` (a premultiplied-style blend) while the shader
   emits straight alpha. Depth test and culling are both disabled.

There is no clear call. The context also sets `antialias: false` and
`powerPreference: "high-performance"`. The blend and context flag are
load-bearing: stored color is added at full strength while alpha accumulates, so
mid-alpha regions read brighter than a straight-alpha port.

## 4. Motion law

Time is seconds; the shader scales it by 0.06. Each layer rotates by
time·(0.7 + 0.15i) rad, so layer angular speeds run 0.042–0.087 rad/s, periods
149.6 s to 72.2 s. The per-layer warp oscillates at 0.078–0.138 rad/s and the
wave carriers at 0.072–0.132 rad/s. Each layer is rotated by the previous
output, so the motion is a slow shear, not a spin. Each layer is then rotated a
constant −0.45 + 0.35·layer and scaled 1.1 − 0.04i, so the six copies never
align. Motion is open-ended; no pointer input.

## 5. Technique and math

Let vUv be the quad's 0..1 coordinates, R the width over height. The coordinate
is uv = (vUv − 0.5) scaled by (R, 1), so the short half-axis is 0.5. Time is
T = 0.06·u_time. Starting with flow = uv and accum = 0, mask = 0, for
i = 0…5 with layer L = i/5:

- flow = rotate(flow, T·(0.7 + 0.15i) + sin(flow.y·(1.4 + 0.3i)));
- flow += 0.08·(sin(flow.y·3.2 + T·(1.3 + L)), cos(flow.x·2.8 − T·(0.8 + L)));
- wave = sin(flow.x·(2.4 + 3L) + T·(1.2 + L)) + cos(flow.y·(1.8 + 2.4L) −
  T·(1.0 + L));
- envelope = smoothstep(1.1, 0.05, |flow|);
- energy = envelope·(0.45 + 0.55·|wave|);
- accum += palette(L)·energy; mask += envelope·(0.6 + 0.2L);
- flow = rotate(flow, −0.45 + 0.35L); flow ×= 1.1 − 0.04i.

The envelope is 1 inside 0.05 units and 0 beyond 1.1, so at a 400 px short axis it
is a 440 px radius disc; the frame's own edge sits at 0.5 vertically, where the
envelope is 0.606. The final color is base + 0.2·accum with base = (0.015, 0.02,
0.045), then a vignette smoothstep(0.95, 0.2, |uv|). Alpha is clamp(mask·0.18 +
|accum|·0.06, 0, 0.65)·vignette. At the center mask reaches 4.2, so the 0.65
alpha cap binds across most of the dome; the corners reach 0 alpha.

The palette is mix(mix(deep, highlight, L), accent, 0.35 + 0.25·sin(4L)) with
deep = (0.06, 0.12, 0.35), highlight = (0.35, 0.20, 0.65), accent = (0.10, 0.45,
0.75). At L = 0 that gives (0.074, 0.2355, 0.49); at L = 1, (0.3097, 0.2403,
0.6661). The layers sample a blue-to-violet ramp, not a cycle; accumulations
overlap additively inside the envelope.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| layers | 6 | 4–8 | number of accumulated flows | H |
| layerNorm | 5.0 | 3–7 | divisor mapping index to 0..1 | M |
| swirl | 0.7 + 0.15i | 0.4–1.6 | per-layer rotation rate | H |
| advection | 0.08 | 0–0.15 | per-layer warp displacement | M |
| waveFreq | 2.4 + 3L | 1.5–6 | x carrier frequency | M |
| envelope | 1.1 / 0.05 | 0.8–1.4 | radial mask edges | H |
| paletteAccum | 0.2 | 0.1–0.4 | brightness of accumulated color | H |
| alphaMask | 0.18 | 0.1–0.3 | alpha from layer coverage | H |
| alphaAccum | 0.06 | 0–0.15 | alpha from accumulated energy | M |
| alphaMax | 0.65 | 0.4–0.8 | opacity cap | H |
| vignette | 0.95 / 0.2 | 0.7–1.1 | dome falloff radii | H |

## 7. Palette and color

Three palette stops: `#0F1F59` deep, `#5933A6` highlight, `#1A73BF` accent,
mixed per layer by L and a `0.35 + 0.25·sin(4L)` accent weight, which across the
six layers (L = 0, 0.2 … 1) runs 0.161–0.600, not 0.35–0.60. Base is `#04050B`.
Effective
layer tints run `#133C7D` (L = 0) to `#4F3DAA` (L = 1), which is why the core
reads blue and the rim violet. Values are display sRGB, no tonemap. Alpha is
capped at 0.65 and multiplied by the vignette, so the canvas is translucent and
the host's dark gradient supplies the corners.

## 8. Composition and camera

Orthographic, centered, full-bleed. The dome is circular in aspect-corrected
space: at 640x400 it spans about 0.94 of the width and the full height, and its
core sits 30 px below center. Wider windows reveal more of the disc horizontally
without stretching it; portrait crops the sides. The vignette reaches zero at
|uv| = 0.95, so at 16:9 the corners are black, at 4:3 nearly so. No safe margins.

## 9. Randomness and seeds

None. The field is a deterministic function of position and time; no RNG, seed,
or warmup. There are only two uniforms, resolution and time, and the first frame
is a valid render at t = 0. Nothing resembles grain, so missing warmup is
invisible.

## 10. Performance budget

One draw call, four vertices, six loop iterations with roughly 42 sin/cos calls
(four sin and three cos per layer; the final constant rotation folds away), one
highp length per iteration, and no textures. At DPR 1.6 the poster is
1024x640 = 655,360 fragments; 1080p is 5,308,416. Fill-bound; the six rotations
dominate. Holds 60 fps on integrated graphics at poster size. Cut layers first,
then DPR.

## 11. Host integration

Standard mount and window resize with the holder size times 1.6; the backing
store is only reassigned when its pixel size changes. The resolution uniform is
uploaded inside resize; the time uniform is uploaded every frame. No pointer
listeners, unique in this family.
Teardown removes the resize listener, deletes program and buffer, and calls
`WEBGL_lose_context`. No ResizeObserver, so panel resizes are missed.

## 12. Failure modes and tells

- **Milky grey rectangle →** alpha composited twice, or `premultipliedAlpha:
  true`; colors then square and darken.
- **Flat blue disc with no violet rim →** palette accent weight fixed at 0.35
  instead of varying with L.
- **Hard concentric rings →** per-layer rotation removed; rotations smear the
  layers.
- **Corners glow instead of black →** vignette edges inverted or missing.
- **Frame too transparent →** alphaMax below 0.5 or alphaAccum dropped.
- **Stretched ellipse on a wide window →** x not multiplied by width/height.

## 13. Tuning knobs

1. `layers` — raise for more internal structure (4–7).
2. `vignette` — lower the outer edge for a tighter dome (0.8).
3. `paletteAccum` — raise for a brighter core (0.25).
4. `alphaMax` — lower for a subtler hero overlay (0.5).
5. `swirl` — raise for faster shear (0.9 + 0.2i).

## 14. Verification checklist

- Center color near `#133C7D`; rim shifts toward `#4F3DAA` and magenta.
- Corners at zero alpha; host gradient visible at the extreme edges.
- No line, ring, or grain structure anywhere.
- Rotation periods 72.2–149.6 s; no visible repeat in 30 s.
- Compare to `assets/posters/nebula-currents.jpg`: same violet upper-right
  crescent and black corners.

## 15. Porting notes

Reproduce `premultipliedAlpha: false` with `ONE, ONE_MINUS_SRC_ALPHA` together,
or the dome darkens. If the target has no straight-alpha canvas, premultiply the
color and keep `ONE, ONE_MINUS_SRC_ALPHA`. Keep highp; mediump loses the low
bits of the accumulated palette. Bind the two uniforms once; the original
re-uploads the time each frame and the resolution only when the backing store
changes.
