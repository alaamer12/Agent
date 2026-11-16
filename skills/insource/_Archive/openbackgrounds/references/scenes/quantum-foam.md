---
id: quantum-foam
name: Quantum Foam
family: webgl-f2
renderer: webgl1
poster: assets/posters/quantum-foam.jpg
complexity: L
source_lines: 331
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Quantum Foam

## 1. Identity

Slow violet and cyan membranes — the iso-surfaces of a drifting 3D noise field —
swell and dissolve across the whole frame like soap film seen in a microscope.

## 2. Perceived look

Soft, gaseous, and continuous. There are no silhouettes: the "bubbles" are thin
bright sheets where the field crosses 0.5, embedded in a purple fog that thickens
where the field is high. Edges are soft, feathered over roughly 0.1 of field
value; contrast is mid and low-frequency, with the brightest filaments near the
center. At t = 3 s a diagonal ridge of membrane runs from the upper right to the
lower center, lit cyan on the side facing the camera and violet on the far side.
There is no subject and no horizon — just a volume.

## 3. Frame anatomy

One fragment pass over a full-screen triangle; no geometry besides the quad.

1. **Clear** — opaque deep color, written by the shader, not the GL clear call.
2. **Backdrop** — `deep · 0.6` scaled by the remaining transmittance, so haze
   fills any gap between membranes.
3. **Membranes and gas** — front-to-back emission/absorption accumulation along
   the ray; 34 samples, no sorting, no depth buffer.
4. **Post** — exposure tone map and a soft radial vignette over the corners.

Canvas is opaque (`alpha: false`); the host backdrop never shows. Depth test disabled, blending enabled but the shader writes alpha 1.

## 4. Motion law

The noise domain drifts along Z at 0.22 units/s (one field-period per ~4.5 s at
scale 1.75) while the sample point itself is pushed by a slow three-axis wander
of amplitude 0.6 and periods 48.3, 57.1, and 69.8 s. A secondary ridged
sinusoid of amplitude 0.055 sweeps at 0.8 rad/s. The camera direction yaws at
0.07 rad/s (89.8 s per turn) and pitches `0.28 sin(0.05 t)` (125.7 s period), so
the membranes slide rather than spin. Open-ended, no loop point. Pointer motion
shifts the screen offset by 0.05 and adds up to 0.15 rad of yaw — small,
parallax-only, no damping.

## 5. Technique and math

**Screen and camera.** `p = (fragCoord − 0.5 · res) / min(res.x, res.y)`,
offset by `pointer · 0.05`. Origin `(0, 0, −1.1)`, ray `normalize(p, 1)`.
The ray vector (not the origin) is rotated by yaw `0.07 t + 0.15·pointer.x` and
pitch `0.28 sin(0.05 t) − 0.12·pointer.y`; rotating the eye rather than the field
keeps all bubbles parallaxing coherently instead of boiling independently.

**Field.** `q = 1.75·pos + (0, 0, 0.22 t)`, then
`q += 0.6·(sin 0.13t, cos 0.11t, sin 0.09t)`, then
`f = noise3(q) + 0.055 sin(11 q.x + 8 q.y − 9 q.z + 0.8 t)`.
`noise3` is value noise on the integer lattice with a smoothstep fade
`f·f·(3 − 2f)` and a `hash31` built from `fract(p · (0.1031, 0.103, 0.0973))`
plus a dot-product scramble — the same hash used by Solar Corona. Eight
lattice corners, trilinear mix. Output range 0…1, mean 0.5.

**Integration.** March `tt = 0.1 + 0.13 i` for i < 34 (depth 0.1–4.39). Per
sample: `edge = |f − 0.5|`, `shell = max(0, 1 − edge / 0.1)²`,
`gas = smoothstep(0.5, 0.95, f) · 0.16`. The sign of the field derivative along
the ray, `df`, gives `facing = clamp(0.5 + 6 df, 0, 1)`, which distinguishes
front-facing from back-facing film and drives `tint = mix(violet, cyan, facing²)`.
Contribution is `trans · (1.5·tint·shell + violet·gas) · exp(−0.42 tt) · 0.13 · 1.5`;
transmittance then drops by `1 − (1.4 shell + gas) · 0.13 · 1.5` per step and the
loop exits early below 0.02. This is emission-absorption volume rendering, not a
surface hit test — there is no normal, no lighting.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| fieldScale | 1.75 | 1.0–3.0 | membrane size; higher = smaller bubbles | H |
| shellWidth | 0.1 | 0.04–0.2 | film thickness/softness | H |
| absorb | 1.5 | 0.5–3.0 | how fast membranes occlude behind them | M |
| glow | 1.5 | 0.8–2.5 | emission gain | M |
| fog | 0.42 | 0.2–0.8 | depth dimming | M |
| sample count | 34 | 24–48 | banding vs cost | H |
| sample spacing | 0.13 | 0.08–0.2 | depth resolution | M |
| Z drift | 0.22 units/s | 0–0.5 | forward flow speed | M |
| wander amplitude | 0.6 | 0–1.0 | how much the field breathes | M |
| ridged term | 0.055 | 0–0.1 | fine crinkle | L |
| yaw rate | 0.07 rad/s | 0–0.15 | camera turn | L |
| pitch amplitude | 0.28 | 0–0.5 | camera bob | L |
| pointer yaw | 0.15 | 0–0.3 | parallax strength | L |
| exposure | 1.6 | 1.2–2.2 | brightness | M |
| vignette | 0.5 | 0.2–0.8 | corner falloff | L |
| violet | (0.42, 0.22, 0.95) | — | shadow-side color | H |
| cyan | (0.2, 0.92, 1.0) | — | light-side color | H |

## 7. Palette and color

Violet `#6B38F2`, cyan `#33EBFF`, deep navy `#030409`. The mix parameter is
`facing²`, so front film is nearly all cyan and back film nearly all violet,
with a narrow transition — that sharp split is what gives the sheets their
electric edge. Accumulation happens in display space; the final
`1 − exp(−1.6 c)` compresses highlights so overlapping films go white rather
than clipping. Vignette reaches 50% at radius 1.3.

## 8. Composition and camera

Full-bleed with no subject placement: the field decides composition. Vertical
FOV is `2 atan(0.5) = 53.1°`. Center of frame is the most likely place for a
bright membrane only because the vignette is weakest there. Wide aspect extends
the field sideways; tall aspect crops it. The bottom fifth is usually darker
because the vignette and the accumulated depth both fall off.

## 9. Randomness and seeds

`hash31` is a stateless 3D integer hash with fixed constants; no seed and no
state. The field is deterministic in time and position, so the frame at t = 3 s
is identical on every run. No warmup — first frame is valid, since the field has
no history.

## 10. Performance budget

One draw call; 34 samples × (one value-noise evaluation = 8 hashes + 7 mixes).
That is roughly 270 hash evaluations per pixel — heavier than a surface march
because every sample counts, not just hits. 60 fps at 640x400 and DPR 1.5 on
desktop; integrated GPUs benefit from DPR 1.0. Cut order: DPR, samples to 24,
`noise3` to a single octave with the ridged term removed.

## 11. Host integration

Standard contract; pointer listener on the window, normalized to −1…1. No
external assets. Resize changes drawing buffer and viewport only. Teardown
removes both listeners, deletes buffer and program, and calls
`WEBGL_lose_context`.

## 12. Failure modes and tells

- **Visible horizontal banding →** sample spacing too large or count too low;
  the membranes alias into stripes.
- **Everything is uniformly purple →** `shellWidth` too wide, so every sample
  contributes and the film distinction disappears.
- **Bubbles look frozen while the camera moves →** the ray is rotated but the
  field is static; the Z drift term was dropped.
- **Bubbles boil independently instead of parallaxing →** the field is rotated
  instead of the camera direction.
- **Frame blooms to white →** `absorb` too low or `glow` too high; transmittance
  never falls.
- **Cyan never appears →** derivative `df` is nearly zero because the sample
  spacing is far below the noise frequency; raise spacing or field scale.
- **Hard banding at the vignette edge →** using `step` instead of `smoothstep`.

## 13. Tuning knobs

1. `fieldScale` — bubble size (1.2–2.4).
2. `shellWidth` — thin electric film versus soft fog (0.06–0.15).
3. `glow` and `absorb` — ethereal versus dense.
4. Z drift — how fast the volume flows past the camera (0.1–0.35).
5. Sample count — smoothness of the accumulated haze (28–44).

## 14. Verification checklist

- Frame is dominated by violet with cyan on the camera-facing side of sheets.
- No hard silhouette anywhere; all edges feathered over several pixels.
- Dark navy gaps visible between membranes, especially near the corners.
- Motion is a slow slide/swell, not a spin; no periodic pop.
- No horizontal banding at 640x400.
- Compare with `assets/posters/quantum-foam.jpg`: same membrane thickness and
  hue split; exact sheet positions differ by time.

## 15. Porting notes

Mediump is sufficient; the field is smooth and no subtraction is precision-
critical. If a library noise is substituted, it must return 0…1 with mean 0.5 —
the 0.5 iso-level and the shell width are absolute, so a −1…1 noise rescales the
whole look.
