---
id: metaball-orbit
name: Metaball Orbit
family: webgl-f2
renderer: webgl1
poster: assets/posters/metaball-orbit.jpg
complexity: XL
source_lines: 456
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Metaball Orbit

## 1. Identity

Two clusters of glossy violet metaballs — large spheres fused with smaller
satellites — hang in darkness, slowly orbiting and merging while a cyan rim
traces their silhouettes.

## 2. Perceived look

Soft, liquid, and jewel-like. Each cluster is a smooth blend of three or four
spheres with no visible seam, lit from the upper right so the top-left of every
sphere is a deep purple and the lower-right rim glows cyan. Surfaces are
glossy: a broad specular sweep and a tight Fresnel edge. The background is pure
near-black with a barely visible purple vignette. Around 25–30% of the frame is
covered, split between two separate blobs with a dark gap between them. Edge
falloff is so soft that the blobs appear to fade into the void rather than end.

## 3. Frame anatomy

Single raymarching pass. Blend is enabled with straight alpha, and the canvas is
transparent (`alpha: true`), so the fragment alpha does the compositing against
the host.

1. **Host backdrop** — the component's own holder carries a CSS radial gradient
   from `rgb(5, 0, 10)` at center to `rgb(2, 0, 5)` at the edge. It shows through
   wherever canvas alpha is low.
2. **Background glow** — rays that miss write `(0.02, 0, 0.05)` times a radial
   falloff, with alpha 0.3 of the red channel.
3. **Metaball surface** — 10 spheres (4 fixed, 6 orbiting) merged by smooth
   minimum.
4. **Edge fade** — alpha `smoothstep(2.5, 0.3, |uv|) · 0.9 · vignette`, where
   the vignette is `smoothstep(1.5, 0.5, 0.8|uv|)`.

## 4. Motion law

Six metaballs orbit at 0.3 rad/s base rate scaled per ball by `0.5 + 0.15 i`
(0.5–1.25), on radii 0.5/0.75/1.0 cycling with `i mod 3`, with different
frequency multipliers per axis (1.0, 0.9, 0.6). Each cluster therefore breathes
apart and back together over roughly 20–40 s. The blend radius itself oscillates:
`0.25 + 0.1 sin(t + i)`, so merging is periodic rather than constant. The
pointer shifts the orbit centers by up to ±0.15 units with damped smoothing
(0.15 per frame toward target, plus a velocity term at 0.3 that decays 0.85 per
frame).

## 5. Technique and math

**Camera.** Orthographic: `uv = (2 · fragCoord − resolution) / resolution.y`,
ray origin `(2 uv.x, 2 uv.y, −2)`, direction `(0, 0, 1)`. There is no
perspective divide, so spheres keep their size across the frame and the
composition reads as a flat stage.

**Scene.** Four fixed spheres at `(−1.3, 1.0)`, `(1.3, −1.0)`, `(−0.8, 0.3)`,
`(0.8, −0.3)` with radii 0.7, 0.8, 0.35, 0.4. Six orbiting spheres at
`offset = (sin(t·s + φ)·R, cos(0.9 t·s + 1.5φ)·0.7R, sin(0.6 t·s + φ)·0.4)`
with `s = 0.5 + 0.15 i`, `R = 0.5 + 0.25 (i mod 3)`, `φ = 0.35 π i`, radius
`0.2 + 0.08 (i mod 3)`. Pointer offset adds `(u_mouse − 0.5) · 0.3` to x and y.

Merging uses the polynomial smooth minimum
`min(a,b) − h² k / 4` with `h = max(k − |a − b|, 0)/k`; the orbiting balls use
a per-step `k = 0.25 + 0.1 sin(t + i)`, the fixed ones use 0.35 and 0.25. The
chain starts from a distance of 1000 so the first `smin` is effectively
`min`.

**March.** 64 steps, epsilon 0.001, step multiplier 0.9, far plane 10.
Normals are 6-tap central differences at 1e-3.

**Shading.** Ambient occlusion is 5 taps at 0.01 + 0.02 i with weight decaying
0.85, giving the soft contact darkening between merged balls. Lights: purple
`(0.8, 0.4, 1.0)` ambient at 0.15·AO, directional `normalize(1.2, 1.5, 1.8)`,
diffuse ×1.5×shadow, Phong specular `pow(V·R, 6) · 3 · Fresnel`, cyan rim
`(0.4, 0.7, 1.0) · Fresnel · 1.2`, inner glow `(0.7, 0.3, 1.0) ·
pow(1 − N·V, 3) · 0.4`. Soft shadows are 16 steps with `k = 16` to a distance
of 5. Tonemapping is `pow(c, 1.8)` followed by `c / (c + 0.6)`, then a 15% fog
toward `(0.02, 0, 0.08)`, then a channel bias `r × 1.1`, `b × 1.2`.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| MAX_STEPS | 64 | 48–96 | surface accuracy; silhouette softness | H |
| EPSILON | 0.001 | 5e-4–3e-3 | hit threshold | M |
| march multiplier | 0.9 | 0.7–1.0 | step size | M |
| fixed spheres | 4 | 2–6 | cluster anchors | H |
| orbiting spheres | 6 | 3–9 | number of satellites | H |
| orbit base rate | 0.3 rad/s | 0.1–0.6 | speed of the cluster | H |
| orbit radius | 0.5 / 0.75 / 1.0 | 0.3–1.4 | spread of satellites | H |
| ball radius | 0.2 + 0.08 (i mod 3) | 0.1–0.4 | satellite size | M |
| blend radius | 0.25 ± 0.1 | 0.1–0.5 | merging strength; higher melts clusters | H |
| AO taps | 5 | 3–8 | contact darkening | M |
| shadow steps | 16 | 8–24 | soft shadow quality | M |
| specular power | 6 | 3–12 | highlight size | M |
| rim strength | 1.2 | 0.4–2.0 | cyan edge | H |
| exposure gamma | 1.8 | 1.2–2.4 | contrast | M |
| fog | 0.15 | 0–0.4 | depth haze | L |
| canvas alpha | true | — | lets the CSS backdrop through | H |

## 7. Palette and color

Base `#0D0026`, light/diffuse `#CC66FF` (the same light colour drives both), rim `#66B3FF`, inner glow
`#B34DFF`, fog `#050014`, host backdrop `#05000A → #020005`. The combined look
is violet bodies with a cyan edge and a purple-black ground. All display sRGB.
The `c / (c + 0.6)` tonemap is what keeps the specular from clipping white and
gives the glossy "candy" finish.

## 8. Composition and camera

Orthographic, centered, no perspective. The two clusters sit left-of-center and
right-of-center at about ±1 unit, each ~30% of the frame height. The alpha edge
fade at radius 2.5 means anything beyond the middle 80% of the shorter axis
dissolves, which frames the composition inside the canvas. Wide frames show more
black between the blobs; portrait frames stack them more vertically.

## 9. Randomness and seeds

No randomness at all beyond the deterministic phase offsets; the only
non-periodic input is the pointer. Because motion is sinusoidal with three
incommensurate frequency multipliers, the composition does not repeat on a short
cycle. No warmup; the first frame is complete.

## 10. Performance budget

64 march steps over a 10-sphere SDF, plus a 6-tap normal, 5-tap AO, and 16-step
soft shadow inside the hit branch. The shadow is the single most expensive term.
At DPR 1.5 this is mid-weight for the family; cut order: shadow steps, DPR, AO
taps, then march steps.

## 11. Host integration

Standard contract plus three deviations: the holder is `pointer-events-none` and the `mousemove` listener sits on the window, mapping coordinates through the canvas rect; the GL context is `alpha: true`; and the holder carries a CSS radial gradient that is part of the look. Mouse is smoothed in JS with a
velocity term. Teardown removes both listeners and loses the context.

## 12. Failure modes and tells

- **Blobs look like separate spheres with hard intersections →** blend radius
  too low or set to zero.
- **One amorphous mass with no structure →** blend radius too high (above 0.5).
- **Black background where the CSS gradient should show →** canvas created with
  `alpha: false`.
- **Silhouettes are hard-edged rectangles at the frame border →** missing alpha
  edge fade.
- **Flat purple surfaces, no gloss →** specular or Fresnel term removed, or
  tonemap replaced with a straight clamp.
- **Pointer makes balls jump →** mouse smoothing removed; the raw target is
  written to the uniform.
- **Spheres pop when orbiting behind each other →** march steps too low for the
  SDF's thin necks.

## 13. Tuning knobs

1. blend radius — how melted the clusters are (0.15–0.4).
2. orbit radius — composition spread (0.4–1.2).
3. rim strength — cyan edge intensity (0.6–1.8).
4. exposure gamma — contrast and depth (1.4–2.2).
5. shadow steps — cost versus softness (8–16).

## 14. Verification checklist

- Two distinct violet clusters, not one, with a dark gap.
- Cyan rim visible on the lower-right of each sphere.
- No visible seams where balls merge.
- Background near-black with a purple center bias from the CSS gradient.
- Edges dissolve smoothly into the background over ~10% of the frame.
- Pointer moves the clusters smoothly, without jumps.
- Compare with `assets/posters/metaball-orbit.jpg`: same violet/cyan balance and
  gloss. Cluster positions depend on time.

## 15. Porting notes

The transparent canvas is load-bearing: without the CSS radial gradient the
scene loses its ground. In a host without CSS behind the canvas, paint the
gradient into the shader background branch instead. Orthographic rays mean the
scene ports without any perspective matrix work.
