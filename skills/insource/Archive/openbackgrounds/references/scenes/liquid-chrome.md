---
id: liquid-chrome
name: Liquid Chrome
family: webgl-f2
renderer: webgl1
poster: assets/posters/liquid-chrome.jpg
complexity: L
source_lines: 363
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Liquid Chrome

## 1. Identity

Polished mirror spheres drift and fuse in darkness, their surfaces reflecting a
banded studio environment of white rings, blue arcs, and one warm ochre stripe.

## 2. Perceived look

Hard, glossy, product-photography metal. Two or three chrome balls read at once:
one large, cropped by the upper-right corner, one smaller at the lower left, with
thin reflection bands — a white equatorial ring, a blue arc, a vertical warm
gold band — sliding across each. Edges are crisp and slightly aliased; interiors
are near-black with sharp highlights. Background is a deep navy vignette, not
pure black. Focal weight sits with the brightest ring highlight; contrast is
high and the palette is cold except for the ochre reflection.

## 3. Frame anatomy

One full-screen fragment pass; a single oversized triangle covers the viewport.

1. **Background** — a radial navy gradient computed from |p|, plus a faint blue
   glow ring at |p| ≈ 0.02.
2. **Bounding-sphere gate** — analytic ray/sphere against radius 2.35; rays that
   miss are never marched.
3. **Chrome volume** — five metaballs fused by a polynomial smooth minimum,
   ray-marched in object space.
4. **Shading** — reflection vector indexes a procedural band environment;
   Fresnel-weighted, plus a tight glint, plus cavity darkening by step count.
5. **Post** — exposure tone map and radial vignette.

Canvas is opaque (`alpha: false`), blending is enabled but every fragment is
alpha 1, so it has no visible effect. No host backdrop shows through.

## 4. Motion law

All motion is driven by `τ = 0.3·u_time`, so rates quoted in τ must be multiplied
by 0.3 for wall time. The metaball field rotates at 0.21τ rad (0.063 rad/s of
wall time, one turn per **99.7 s**) and wobbles around X by
`0.3 sin(0.17τ)` rad (period **123.2 s**). The five balls orbit at
`0.42–0.66` rad per τ = 0.126–0.198 rad/s, giving wall-time periods of **49.9,
43.6, 38.8, 34.9 and 31.7 s**, each with a fixed phase offset of 1.9 rad per
index. Each radius breathes `±0.14` with a **29.9 s** period. Motion is
open-ended, never loops. The pointer adds a direct (undamped) offset — half a
radian of Y rotation and 0.35 rad of X tilt at full deflection — and holds that
offset when the pointer leaves, since there is no damping.

## 5. Technique and math

**Coordinates.** `p = (fragCoord − 0.5 · res) / min(res.x, res.y)`; camera at
`(0, 0, 3.1)`, ray `normalize(p, −1.5)` looking down −Z, vertical FOV
`2 atan(0.5/1.5) ≈ 36.9°`. The frame never changes projection with aspect.

**Background.** Every pixel starts as `deep · (0.5 + 0.9·(1 − 0.7|p|))` plus
`blue · spike(|p| − 0.02, 0.75) · 0.1`, a faint blue ring just outside the
centre. A hit replaces it with `col = max(background, metal)`, so the dim
reflection still shows the background through it.

**Field.** Let `τ = 0.3·u_time`. Object-space rotations apply to the point, not
the camera: Y by `0.21τ + 0.5 · pointer.x`, then X by
`0.3 sin(0.17τ) − 0.35 · pointer.y`. Component-wise, Y is
`(cy·x + sy·z, y, −sy·x + cy·z)` and X is `(x, cx·y − sx·z, sx·y + cx·z)`.
Five spheres with center
`c = (cos(a + 0.7i)(0.72 + 0.12i), sin(1.13a + i)(0.4 + 0.09i), sin(0.83a + 2.1i)(0.55 + 0.11i))`,
`a = τ(0.42 + 0.06i) + 1.9i`, radius `0.44 + 0.14 sin(2.3i + 0.7τ)`. Fused with
the polynomial smooth minimum at `k = 0.62` — the high k is what lets two
spheres read as separate balls joined by a liquid neck.

**March.** Entry point from the analytic sphere hit at radius 2.35; initialize
the field accumulator at `d = 1e5`, then at most 34 steps, accept when the field
is below `0.0025 · dist` (a relative epsilon, so distant surfaces stop earlier),
advance `0.92 · d`, bail past distance 7. Normals use the four-tap tetrahedral
swizzle at epsilon 0.0025: with `k = (1, −1)`,
`n = normalize(k.xyy·map(p + k.xyy·e) + k.yyx·map(p + k.yyx·e) +
k.yxy·map(p + k.yxy·e) + k.xxx·map(p + k.xxx·e))`, which is cheaper and smoother
on a metaball neck than six central differences.

**Reflection.** `envMap` is a function of direction only:
`c = deep·1.4 + tint·spike(y, 0.07)·1.0 +
(0.8, 0.86, 1.0)·spike(y − 0.6, 0.16)·(0.35 + 0.55·clamp(0.5 + 0.5·d.x, 0, 1)) +
tint·pow(clamp(0.5 + 0.5·sin(15y + 1.2), 0, 1), 14)·0.6 +
blue·pow(max(0, sin(3·azimuth + 1.1)), 16)·1.35 +
warm·pow(max(0, sin(2·azimuth − 2.3)), 20)·1.15 +
blue·clamp(−y, 0, 1)·0.18`, with
`spike(x, w) = exp(−(min(|x|/w, 4))²)` giving the soft-edged bands. Metal =
`env · (0.35 + 1.1·Fresnel) · gloss`, where
`Fresnel = pow(clamp(1 + N·rd, 0, 1), 3.6)`. The glint uses
`L = normalize(0.45, 0.72, 0.55)`, `H = normalize(L − rd)`,
`glint = pow(max(N·H, 0), 90)`: `metal += warm·1.6·glint + tint·1.2·glint²`.
The hit is then darkened by march progress,
`metal *= 1 − min(steps/34, 1)·0.45`, where `steps` is the loop index at the hit
(0–33), and mixed toward deep with depth past the bounding sphere,
`metal = mix(metal, deep, clamp((hitT − tb)·0.14, 0, 1)·0.5)`, which is what
keeps the balls from looking like flat decals.

**Post.** `col = 1 − exp(−1.5·col)`, then
`col *= 1 − 0.5·smoothstep(0.45, 1.2, |p|)`.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| blend (smin k) | 0.62 | 0.3–0.9 | how much balls fuse vs stay separate | H |
| gloss | 1.0 | 0.5–1.6 | reflection strength | M |
| bound | 2.35 | 1.8–3.0 | bounding-sphere entry radius | M |
| sphere count | 5 | 3–7 | number of lobes | M |
| base radius | 0.44 | 0.3–0.6 | ball size | H |
| radius modulation | 0.14 | 0–0.25 | size breathing | M |
| orbit amplitude | 0.72 + 0.12i | 0.5–0.9 | how far lobes swing | M |
| march steps | 34 | 24–48 | surface precision | H |
| step multiplier | 0.92 | 0.8–1.0 | under-relaxation | M |
| relative epsilon | 0.0025 | 1e-3–5e-3 | hit threshold | M |
| max dist | 7.0 | 5–10 | far bail | L |
| rotation Y rate | 0.21 rad/s | 0–0.4 | body spin | M |
| pointer rotation | 0.5 rad | 0–1.0 | cursor spin influence | L |
| glint power | 90 | 40–160 | highlight tightness | M |
| Fresnel power | 3.6 | 2–6 | rim reflection width | M |
| exposure | 1.5 | 1.2–2.2 | tone-map brightness | M |
| vignette | 0.5 | 0.2–0.8 | edge falloff | L |

## 7. Palette and color

Tint `#D1DEFF`, blue `#1A61FF`, warm `#FFB352`, deep `#040408`. The environment
mixes these in display space with hard power falloffs, so the bands stay
saturated. The final `1 − exp(−1.5 · c)` is a per-channel exponential tone map
that compresses the glint toward white without clipping the background to zero.
Background gradient uses `deep · (0.77 … 1.4)` — always navy, never grey.

## 8. Composition and camera

Normalization by the short edge means the FOV is fixed and the frame simply crops
wider. The subject cluster is centered; at 640x400 the large ball typically sits
upper-right and the small one lower-left, both partly cut. Ultra-wide aspect adds
empty navy at the sides; tall aspect crops the outer balls. Vignette reaches half
strength by |p| = 1.2, keeping the corners dark.

## 9. Randomness and seeds

None. Every position, radius, and phase is an explicit constant or a closed-form
function of index and time. No hash, no RNG, no warmup; any screenshot at a given
t is reproducible.

## 10. Performance budget

One draw call, three vertices, 34 march steps plus four normal taps per hit
pixel. Cost is dominated by the five-ball SDF evaluation (each step evaluates
five `length` calls). Holds 60 fps at DPR 1.5 on desktop; integrated GPUs
usually 40–60 fps at 640x400. Cut order: DPR to 1.0, steps to 24, spheres to 4.

## 11. Host integration

Standard contract. Listens to `pointermove` on the window and normalizes to
−1…1 without clamping to the canvas, so a cursor over surrounding UI still
tilts the chrome. No external assets. Resize recomputes the drawing buffer and
viewport; teardown deletes buffer, program, removes both listeners, and loses
the context.

## 12. Failure modes and tells

- **Balls look like plastic →** the environment bands are too broad; raise the
  band powers or narrow `spike` widths.
- **Balls split apart instead of fusing →** `blend` below ~0.4, or orbit
  amplitudes pushed past 0.9 so centers cannot reach each other.
- **Interiors show marching stair-steps →** step multiplier at 1.0 or epsilon
  too small; lower the multiplier to 0.9.
- **Whole frame fades to black →** `bound` smaller than the cluster radius, so
  the entry sphere clips the balls; the analytic gate never opens.
- **Highlights crawl and shimmer →** glint power too high combined with DPR 1.0.
- **Subject drifts off-center after mouse leave →** pointer is applied directly
  without damping in the original; that is intended, not a bug.
- **Muletone bands instead of bright rings →** tone exposure below 1.2 crushes
  the mid-tones.

## 13. Tuning knobs

1. `blend` — separate balls versus a single melted mass (0.45–0.75).
2. Base radius — subject weight and how much of the frame it occupies.
3. `gloss` and glint power — mirror versus satin finish.
4. Band powers in the environment — thick reflective stripes versus thin rings.
5. Exposure — how hot the highlights burn (1.3–1.9).

## 14. Verification checklist

- At least two distinct chrome spheres visible, one cropped by an edge.
- Thin bright reflection bands crossing each sphere, not a uniform sky gradient.
- Background reads as deep navy with a soft vignette; no pure-black corners.
- Highlights move smoothly with time; no flicker between frames.
- Warm ochre band present; the rest of the palette is blue/white.
- Compare with `assets/posters/liquid-chrome.jpg`: ball count and band widths
  match; positions differ with time.

## 15. Porting notes

The original renders a three-vertex oversized triangle instead of a quad; either
works. `atan(d.z, d.x)` must use the two-argument form — `atan(z/x)` loses the
azimuth sign and puts both warm and blue arcs on one side.
