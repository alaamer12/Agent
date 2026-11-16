---
id: orbit-belt
name: Orbit Belt
family: webgl-f3
renderer: webgl1
poster: assets/posters/orbit-belt.jpg
complexity: L
source_lines: 574
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Orbit Belt

## 1. Identity

Thirteen concentric rings of glowing particles orbit a small warm star, each
particle trailing a short comet tail, the whole system tilted and turning slowly.

## 2. Perceived look

A fine, jewel-like planetary system. The core is a compact amber cluster of
overlapping soft sprites; the belts are thin dotted ellipses, warm gold near the
center grading to blue at the rim, each dot smeared into a short tail along its
direction of travel. Density is low — individual particles and gaps are visible,
not a solid disc. The inclination spread is small, so the rings read as one
flattened system rather than a shell of crossing circles. Background is black
with a warm tint. At 3 s the inner belts are visibly ahead of the outer ones.

## 3. Frame anatomy

One static buffer holding trail segments followed by points; two draw calls share
it with different programs and fragment stages. Additive blending
(`SRC_ALPHA, ONE`), depth test off, depth writes off, clear to
`rgb(0.01, 0.006, 0.006)`.

1. **Clear** — near-black warm ground.
2. **Trails** — 9984 line-segment vertices (832 heads × 6 segments × 2), alpha
   ramped along the tail.
3. **Heads** — 832 point sprites with a bright core.
4. **Dust and corona** — 1200 loose debris points plus 26 large low-alpha
   sprites at radius 0.06 forming the central star, drawn in the same points pass.

Canvas is opaque (`alpha: false`, `antialias: true`). No host backdrop.

## 4. Motion law

Each belt is Keplerian: angular speed `0.42 / r^1.5`, so the inner belt at
r = 0.95 completes a turn in 13.9 s while the outer at r = 3.3 takes 89.6 s. The
differential is the whole visual story. Every particle carries a tail of 0.26
world units behind it, expressed as an angular lag `0.26/r` so all tails are the
same physical length. Each belt's orbital plane also precesses about the world Y
axis at 0.004–0.02 rad/s, randomly signed, which braids the rings on a minute
timescale. The system spins at 0.035 rad/s and is tilted 0.42 rad. Particle
brightness glints at 2.1 rad/s with a per-particle phase. Open-ended.

## 5. Technique and math

**Build.** 13 belts at radii `0.95 + 2.35 · b/12`. Each belt gets an orthonormal
basis from a normal within 0.16 rad of the world Z axis — normal
`(sin i cos φ, sin i sin φ, cos i)` — and an azimuthal basis derived from it, so
the planes stay nearly coplanar. This is deliberate: fully random orientations
produced a shell of crossing rings. 64 heads per belt are placed at uniform
phase with ±0.175 rad jitter; radius jitters ±5.5% (`band` 0.11). 1200 dust
particles fill radii 0.665–3.3 with a `u^0.8` bias, on random great circles. 26
corona sprites sit at radius 0.06.

**Vertex motion.** For a particle with base radius `r0`, phase, angular speed
`ω`, and trail parameter `s ∈ [0, 1]`:
`angle = phase + ω t − s · 0.26 / max(r0, 0.12)`,
`radius = r0 (1 + (jitter − 0.5) · 0.11)`,
point `p = (u cos θ + v sin θ) · radius` in the belt plane. The belt basis is
rotated about Y by `t · precess` (the node drift), then the whole point by
`rotX(0.42)` (tilt) and `rotY(0.035 t)` (spin). Projection is
`q.xy · focal / w` with `w = q.z + 8.0` and clip w set to `w`, so on-screen
radius is `R · focal / (z + 8)²`. `focal = 12.6 · min(1, aspect/1.6)`; coverage
of the short axis is `3.3 · 12.6 / 64 = 0.65`.

**Tail.** Each segment is a line between consecutive `s` samples, so a head
draws 6 short chords rather than a curve; at this length the chords are
indistinguishable from an arc. Alpha is `bright · fade · (1 − s)^1.7`, where
`fade = (1 − smoothstep(5.9, 10.3, w))^1.3` dims the parts of the system that
swing toward and away from the camera — an orbit-ring depth cue, not fog.

**Color.** `rt = (r0 − 0.95)/2.35`; `mix(warm, mid, smoothstep(0, 0.42, rt))`
then `mix(_, cool, smoothstep(0.36, 1, rt))` with warm `(1, 0.58, 0.2)`, mid
`(1, 0.92, 0.7)`, cool `(0.34, 0.62, 1.0)`. Color is multiplied by a glint
`0.85 + 0.3 sin(2.1 t + 31 seed)` before interpolation to the fragment.

**Sprites.** Size in world units: heads 0.0078–0.0151, dust 0.0017–0.0044,
corona 0.0244–0.0658. Pixel size is `size · focal_y · height · 0.5 / max(w, 0.2)`
clamped 1–64. The head fragment computes `k = 1 − 2d`, `halo = k^2.6`,
`core = k^10`, adds warm white at 80% of core, and scales alpha by
`0.16 + 0.84 halo`; strengths are 1.0 for trails and 1.2 for heads.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| seed | 20260925 | any | belt precession signs, jitter | M |
| belts | 13 | 5–20 | ring count | H |
| headsPerBelt | 64 | 24–120 | dots per ring | H |
| trailSamples | 7 | 2–14 | tail segmentation and smoothness | M |
| dust | 1200 | 0–3000 | inter-ring debris | M |
| corona | 26 | 0–60 | central star size | M |
| rMin / rMax | 0.95 / 3.3 | 0.6–5 | system extent | H |
| inclMax | 0.16 rad | 0–0.6 | coplanar vs shell of rings | H |
| kepler | 0.42 | 0.2–0.8 | orbital speed scale | H |
| trailArc | 0.26 | 0.1–0.6 | tail length in world units | H |
| band | 0.11 | 0.02–0.2 | radial scatter of a ring | M |
| precessMin / precessMax | 0.004 / 0.02 | 0–0.05 | node drift / braiding | M |
| spin | 0.035 rad/s | 0–0.1 | whole-system rotation | L |
| tilt | 0.42 rad | 0.2–0.7 | viewing angle | H |
| focal / refAspect | 12.6 / 1.6 | 9–15 / 1.2–2 | system coverage; focal shrinks by aspect/refAspect on narrow frames | H |
| distance | 8.0 | 6–10 | camera distance | H |
| depthNear / depthFar | 5.9 / 10.3 | 4–8 / 8–14 | depth fade window on w | M |
| trailStrength | 1.0 | 0.5–1.0 | tail alpha | M |
| headStrength | 1.2 | 0.8–1.5 | dot alpha | M |

## 7. Palette and color

Warm `#FF9433`, mid `#FFEBB3`, cool `#579EFF`, ground
`#030202`. The ramp is keyed on orbital radius, not screen position, so a ring
keeps its color all the way around even as it dips toward the camera. Additive
blending makes the corona and dense inner rings climb toward white without
clipping logic; depth fade multiplies alpha rather than color, keeping hue
constant. Values are display sRGB.

## 8. Composition and camera

Centered system, nearly face-on but tilted 0.42 rad, so the rings are wide
ellipses. Coverage is 0.65 of the short axis; on a 640x400 canvas the outer belt
radius is about 130 px. The empty black margin around it is deliberate — the
scene reads as a small object in space, not a full-bleed pattern. Wide aspect
adds lateral margin; narrow aspect shrinks the focal so the system still fits.
The corona sits exactly at frame center.

## 9. Randomness and seeds

mulberry32 with seed 20260925, drawn in a fixed order: per belt the precession
magnitude and sign, then the basis; then per head the phase jitter, seed, size
and brightness; then
dust and corona. Uniform sampling for phases, `u^0.8` for dust radius, a
Gramm-Schmidt perpendicular for great-circle dust planes. No warmup; phases are
uniform at t = 0.

## 10. Performance budget

Two draw calls: 9984 trail vertices and 2058 points. GL lines dominate vertex
count but are cheap; sprite overdraw is bounded by the 64 px clamp, and only the
corona reaches it. 60 fps at 1080p on integrated graphics. Cut order: DPR,
trailSamples to 4, dust to 600, belts to 9.

## 11. Host integration

Standard contract, no pointer input, no external assets. Resize recomputes
buffer size, viewport, and focal x by aspect. The vertex data is released after
upload (`vertexData = null`), so the JS heap holds nothing per frame. Teardown
deletes the single buffer and both programs, then loses the context.

## 12. Failure modes and tells

- **Rings cross like a wire cage →** `inclMax` raised past ~0.3; the common
  disc is what makes the system readable.
- **Inner rings spin at the same speed as outer ones →** the `r^1.5` law was
  dropped or `kepler` folded into a constant.
- **Tails point sideways or detach →** the angular lag sign is wrong, or the
  tail uses a screen-space offset instead of the orbit-plane lag.
- **Rings vanish where they tilt toward the camera →** the depth fade band is
  too narrow; widen `depthNear`/`depthFar`.
- **System is a tiny dot →** focal/distance ratio changed; coverage is
  `rMax·focal/distance²`.
- **Corona is a hard disc →** too few overlapping sprites or sizes too uniform;
  the star is built from 26 large low-alpha sprites, not one.
- **Rings look solid, not dotted →** head count raised far beyond 64 per belt
  or trails lengthened; the gaps are part of the look.
- **Color banding around the rim →** the two smoothsteps in the ramp were
  replaced by a single `mix` with a hard threshold.

## 13. Tuning knobs

1. `belts` — how many rings the system has (9–16).
2. `trailArc` — dust specks versus clear comet tails (0.15–0.4).
3. `inclMax` — flat disc versus slightly 3D (0.08–0.25).
4. `focal` with `distance` — system size in frame.
5. `kepler` — how violent the inner/outer speed split is.

## 14. Verification checklist

- One central amber cluster, brighter than any ring.
- Concentric ellipses, not intersecting circles.
- Warm gold near the center, blue at the rim.
- Individual dots with short tails; gaps visible between dots.
- Inner rings visibly faster than outer ones over a few seconds.
- No solid filled disc and no hard-edged sprites.
- Compare with `assets/posters/orbit-belt.jpg`: ring count, color ramp, and
  tail-to-gap ratio. The shipped poster shows an earlier, tighter camera; trust
  the `focal`/`distance` constants for scale.

## 15. Porting notes

`highp` is required in the vertex stage: the projection divides by a squared
depth, and mediump lands the outer belts with visible stepping. The trail is a
polyline, so a 2D-canvas port can draw the same chords directly; the only
math that must survive is the Keplerian `ω = 0.42 / r^1.5` and the constant
world-space tail length.
