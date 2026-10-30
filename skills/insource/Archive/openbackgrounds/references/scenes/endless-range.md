---
id: endless-range
name: Endless Range
family: webgl-f2
renderer: webgl1
poster: assets/posters/endless-range.jpg
complexity: L
source_lines: 390
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Endless Range

## 1. Identity

A camera flies low over an endless ridge-noise mountain range at dusk, the sky a
smouldering red gradient with a small setting sun behind the peaks.

## 2. Perceived look

Matte, airbrushed, almost vector-clean. The mountains are near-black violet-grey
silhouettes with soft snow lit on the upper slopes, layered by haze so the far
range fades toward dusty rose. Sky is a vertical gradient from deep indigo at
the top to burnt orange at the horizon, with a soft sun disc and a bright haze
band. Edges are smooth — no texture, no grain. Contrast is strongest between the
lit rim of the nearest ridge and the sky; the lower third of the frame is dark
foreground slope. At t = 3 s the horizon sits just above center and the sun glow
is slightly right of center.

## 3. Frame anatomy

One fragment pass, no geometry, no blending that takes effect.

1. **Sky** — vertical gradient plus sun disc, wide haze, and a horizon mist band,
   all computed from the ray direction.
2. **Terrain** — a heightfield marched in world-Z, shaded only where hit.
3. **Haze** — exponential depth fog mixed into the terrain color toward a
   haze/sky blend.
4. **Post** — exposure tone map and radial vignette.

Canvas is opaque (`alpha: false`); the clear color is overwritten by the sky on
every pixel, so no host backdrop shows. Depth test off, blend on but alpha 1.

## 4. Motion law

The camera translates forward at 1.05 world units/s along +Z, which is the only
motion the composition needs: the terrain function is infinite, so the range
scrolls without a loop. Lateral sway is `3 sin(0.035 t)` units, period 179.5 s.
The pointer adds ±1.2 units laterally and ±0.35 units of height, directly, with
no damping. Ridges do not animate — only the viewpoint moves, which is why the
scene reads as flight rather than as shifting mountains. Fully open-ended.

## 5. Technique and math

**Camera and ray.** `p = (fragCoord − 0.5 · res) / min(res.x, res.y)`;
origin `(3 sin 0.035t + 1.2 pointer.x, 2.75 + 0.35 pointer.y, 1.05 t)`;
direction `normalize(p.x, p.y − 0.055, 1)`. The −0.055 lifts the horizon slightly
above the frame center. Rays are mostly forward (+Z), not toward a focal point.

**Terrain.** 2D value noise (`vnoise`, same smoothstep fade, corner hash
`fract(p · (123.34, 456.21))` scrambled by a dot product) sampled at
`x = worldXZ · 0.19 + (3.7, 1.9)`. Three ridged octaves:
`n = 1 − |2 vnoise − 1|`, accumulate `a n²`, `a` starting at 0.6 and halving,
each octave `x ← 2.11 x + (3.1, 7.7)`. Height is `clamp(v / 1.05, 0, 1) · 4.1`.
Ridging is the tell — plain fbm would round the peaks and read as dunes.

**March.** Instead of stepping along the ray, step along world Z: start 0, step
0.45, multiply by 1.115 each iteration. The step sum grows fast — it reaches the
far plane 120 after about 32 iterations, and the full 44 would reach ≈466, but
the `t > 120` guard breaks the loop first. Ray parameter `t = z / rd.z`. Accept
the first `pos.y < terrain(pos.xz)`; bail past `t = 120` or when
`pos.y > 4.15` (above any peak — this early-out is what makes it cheap over
sky). Five bisections between the last two z values refine the hit.

**Normal and shading.** Normal from heightfield differences with
`e = 0.05 + 0.006 t`: `(h(x−e,z) − h(x+e,z), 2e, h(x,z−e) − h(x,z+e))` — the
gradient form, giving `n.y ∝ 2e`, so normals soften with distance and distant
peaks don't alias. `slope = max(0, N·L)` toward the low sun
`normalize(0.35, 0.055, 0.93)`; `face = N.y`. Base `rock · (0.35 + 1.1 face)`,
add `lit · slope³ · 0.85` and `sunDisc · slope²⁶ · 0.5`, then snow where
`hitH` is between 2.13 and 3.53 and `N.y` between 0.45 and 0.8, mixed 80% at
`0.45 + 0.9 slope`. Fog `1 − exp(−0.012 t)` toward `mix(haze, skyLow, 0.45)`.

**Post.** `col = 1 − exp(−1.35·col)`, then
`col *= 1 − 0.4·smoothstep(0.5, 1.3, |p|)`.

**Sky.** `up = clamp((rd.y + 0.055) · 1.7, 0, 1)`, gradient
`mix(skyLow, skyHigh, up^0.6)`. Sun disc `exp(−(min(sd/0.06, 4))²) · 0.85`
where `sd = |L − rd|` — the length of the difference of two unit vectors is a
cheap angle proxy. A wider haze glow uses the same form at width 0.34 and gain
0.4; a mist band `exp(−24 |rd.y|) · 0.4` sits on the horizon.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| terrainScale | 0.19 | 0.1–0.3 | ridge wavelength | H |
| height | 4.1 | 2.5–6.0 | peak altitude / camera clearance | H |
| cameraHeight | 2.75 | 1.5–4.0 | viewpoint above the valley | H |
| far | 120 | 60–200 | far clip for the march | L |
| speed | 1.05 units/s | 0.4–2.0 | flight speed | M |
| fog density | 0.012 | 0.005–0.03 | depth separation | H |
| sun direction | (0.35, 0.055, 0.93) | — | sun height and azimuth | H |
| march steps | 44 | 32–64 | far-ridge resolution | M |
| z step start | 0.45 | 0.3–0.7 | near-field sampling | M |
| z step growth | 1.115 | 1.05–1.2 | how fast samples thin out | H |
| bisection steps | 5 | 0–6 | silhouette precision | M |
| normal epsilon | 0.05 + 0.006 t | — | slope softness with distance | M |
| snow band | 0.52–0.86 × height | — | snowline height | M |
| sway amplitude | 3.0 | 0–5 | lateral drift | L |
| pointer gain | 1.2 / 0.35 | 0–2 | look-around strength | L |
| exposure | 1.35 | 1.1–1.8 | brightness | M |
| vignette | 0.4 | 0.2–0.7 | corner falloff | L |

## 7. Palette and color

Rock `#0E0D16`, snow `#D9B8C7`, lit slope `#804233`, haze `#D95C2E`, sky high
`#050412`, sky low `#6B1F24`, sun disc `#FFD173`. HSL: the sky runs from
hue 244 at 4% lightness down to hue 356 at 27%; haze sits at hue 16. Values are
display-space; the exponential tone map `1 − exp(−1.35 c)` keeps the sun disc
from clipping and lifts the rock slightly, and the vignette then pushes the
corners back down.

## 8. Composition and camera

Horizon at `p.y ≈ 0.055`, i.e. 5.5% above center — deliberately near-centered so
the sky/ground split reads as a landscape. Nearest ridge typically fills the
lower 35–45% of the frame; the sun disc sits at the vertical angle implied by
`L`, so it appears just above the horizon. Wide aspect widens the panorama;
tall aspect gives more sky and drops the foreground out of frame. The camera
never pitches, so the horizon line stays level.

## 9. Randomness and seeds

No RNG. Terrain is a deterministic function of world position; the only
time-dependence is the camera Z. Any screenshot at a given t is reproducible, and
there is no warmup: the terrain has no accumulated state.

## 10. Performance budget

One draw call, 44 terrain iterations + 5 bisections + a 4-tap normal (each tap
one 3-octave noise = 12 value-noise evaluations total per hit pixel). Sky pixels
cost almost nothing because the `pos.y > height` early-out fires immediately.
60 fps at 640x400 on any GPU; 4K at DPR 1.5 is the stress case. Cut order: DPR,
steps to 32, octaves to 2.

## 11. Host integration

Standard contract; pointer on the window, normalized to −1…1. No external assets
and no textures. Resize changes the drawing buffer and viewport; the projection
normalizes by the short edge, so the horizon stays at the same height across
aspect ratios. Teardown as usual: listeners, RAF, buffer, program,
`WEBGL_lose_context`.

## 12. Failure modes and tells

- **Mountains look like smooth dunes →** the ridged octave (`1 − |2n − 1|`) was
  replaced by plain fbm; peaks round off.
- **Far ridges stair-step or pop →** z growth too aggressive or fewer than 32
  steps; distant terrain is skipped.
- **Sky is grey →** haze and sky-low colors were averaged instead of mixed by the
  `up^0.6` gradient.
- **Everything is fogged flat →** fog density above 0.03, or fog applied to the
  sky, which already contains its own haze.
- **Sun appears in the wrong place →** using `atan` for the sun angle instead of
  `|L − rd|`; the proxy is only valid for unit vectors.
- **Snow covers the whole range →** snowline band widened below 0.52 × height,
  or the `N.y` gate dropped so steep faces go white.
- **Black band at the horizon →** the `pos.y > height` early-out fires before the
  sky color is written.

## 13. Tuning knobs

1. `terrainScale` — ridge wavelength and how many ranges are visible (0.15–0.25).
2. `height` versus `cameraHeight` — how close the flight feels to the peaks.
3. Fog density — layered depth versus a flat silhouette (0.008–0.02).
4. Sun direction Y — sun on the horizon versus a higher dusk (0.02–0.2).
5. Speed — gliding versus racing (0.6–1.6).

## 14. Verification checklist

- Clear horizon line at roughly the vertical center; sky above, rock below.
- Sun disc visible as a small bright spot with a wide glow around it.
- At least three depth layers distinguishable by haze lightness.
- Ridges are sharp-topped, not rounded.
- Lower third darker than the sky; no light leaks into the foreground.
- Camera moves forward smoothly; no jitter or ridge popping.
- Compare with `assets/posters/endless-range.jpg`: same ridge scale, snowline,
  and sky hue ramp; the specific peaks differ because the camera has advanced.

## 15. Porting notes

Marching in world Z rather than ray distance is the whole performance trick —
port it, don't "fix" it into a sphere-tracing loop. It works because the camera
looks nearly along +Z; a scene with a wider FOV or a tilted camera needs the
`t = z / rd.z` guard raised.
