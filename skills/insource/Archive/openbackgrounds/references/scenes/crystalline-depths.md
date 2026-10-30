---
id: crystalline-depths
name: Crystalline Depths
family: webgl-f2
renderer: webgl1
poster: assets/posters/crystalline-depths.jpg
complexity: XL
source_lines: 425
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Crystalline Depths

## 1. Identity

A large faceted blue crystal with a square lattice carved through its interior
rotates slowly in darkness, ringed by five smaller octahedra that drift around
it.

## 2. Perceived look

Cold, sculptural, and metallic-blue. The central form reads as a cut gem: flat
faceted planes, a bright rim where the silhouette turns away, and an interior
patterned like a checkerboard of glass tiles because square holes are carved out
of the volume. The smaller crystals sit at the frame edges and are lit the same
way. The background is essentially black with a faint navy cast; there is no
floor, no horizon, no environment. Contrast is high on the facets and low in
the shadowed interior. The single subject fills roughly 70% of the frame height.

## 3. Frame anatomy

One raymarching pass, no separate geometry, no blending that has any effect
(fragment alpha is 1 while blending is enabled).

1. **Background** — `rgb(0.02, 0.02, 0.05)` wherever the ray misses.
2. **Crystal volume** — octahedron SDF, six orbiting sub-octahedra merged with a
   smooth minimum, then a periodic box lattice subtracted from the interior.
3. **Shading** — diffuse + Blinn specular + Fresnel rim + a fake three-sample
   refraction tint, plus sparse internal glow.
4. **Post** — depth fog toward navy, silhouette edge glow, radial vignette,
   gamma 0.9.

Canvas is opaque (`alpha: false`). No host backdrop shows through.

## 4. Motion law

The crystal rotates in object space at 0.08 rad/s around Y and 0.06 rad/s
around X (one Y turn per 78.5 s). Six sub-crystals orbit at 0.1 rad/s with
phase `i · π/3`, at radius 1.5, so they sweep past the central body rather than
merging with it. The camera orbits at the same 0.08 rad/s around Y and bobs
±0.3 units with a 62.8 s period, which is what keeps the facets changing
highlight without spinning the silhouette wildly. Nothing loops exactly.

## 5. Technique and math

**Camera.** Orthographic-looking setup: `uv = (fragCoord − 0.5 · res) / res.y`,
ray origin `(0, 0, −4.5)`, direction `normalize(uv, 1.5)`. The vertical field of
view is `2 atan(0.5 / 1.5) ≈ 36.9°`. Both origin and direction rotate in XZ by
`0.08 t`, and the origin bobs by `0.3 sin(0.1 t)`.

**SDF.** Octahedron distance is the standard `max` reflection form with
`s = 1.2`. Six sub-octahedra at
`offset = 1.5 · (cos θ, sin(0.7 θ), sin θ)` with `θ = i π/3 + 0.1 t`, radius
`0.3 + 0.2 · hash(i)`, merged by smooth minimum `k = 0.3`.

Interior lattice: `q = mod(p + 0.5, 1) − 0.5`, box of half-size 0.15, and the
solid is carved by `max(crystal, −box + 0.1)`. This subtracts a grid of square
tunnels, which is the checkerboard seen through the faces.

**March.** 100 steps, epsilon 1e-4, distance 20, step multiplier 0.8 (slightly
under-relaxed, so the interior lattice is less likely to be stepped over).
Normals are central differences at 1e-4.

**Shading.** Base `(0.15, 0.25, 0.45)` at 30%; diffuse
`(0.4, 0.6, 1.0) · N·L · 0.5` with `L = normalize(1, 1, 1)` and
`H = normalize(L + view)`; Blinn specular `pow(N·H, 32) · 1.5`;
Fresnel `pow(1 − N·V, 3) · 0.8`. The refraction is faked: refract with IOR 1.5,
sample the position at 0.95/1.00/1.05 of a 0.3 offset, evaluate a sine tint per
channel, add the three at 0.4, and mix at 60%. Sparse internal glow adds
`(0.3, 0.6, 1.0) · hash3(floor(4 p)) · 0.12` (the hash's 0.3 is scaled by 0.4).

**Post.** Fog `1 − exp(−0.15 t)` mixed 30% toward `(0.05, 0.08, 0.15)`; edge
glow `pow(1 − |N·V|, 2) · 0.3`; vignette `smoothstep(0.3, 1, 1 − 0.4|uv|)`
applied twice on hit pixels — once to the colour, then again through the
background mix — so it effectively squares; gamma `pow(c, 0.9)`.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | resolution clamp | L |
| MAX_STEPS | 100 | 64–160 | march quality; faceting at low values | H |
| MAX_DIST | 20 | 10–30 | far plane | L |
| EPSILON | 0.0001 | 1e-4–1e-3 | hit threshold; higher = softer corners | M |
| march multiplier | 0.8 | 0.7–1.0 | step relaxation | M |
| main octahedron size | 1.2 | 0.9–1.6 | subject scale | H |
| sub-crystal count | 6 | 3–8 | satellite crystals | M |
| sub-crystal offset | 1.5 | 1.0–2.2 | how far they orbit | M |
| sub-crystal size | 0.3 + 0.2 hash | — | satellite scale | M |
| smin k | 0.3 | 0.1–0.6 | how much satellites melt into the body | H |
| lattice cell | 1.0 | 0.6–1.6 | checkerboard pitch | H |
| lattice box | 0.15 | 0.08–0.25 | hole size | H |
| rotation Y | 0.08 rad/s | 0–0.2 | body spin | M |
| rotation X | 0.06 rad/s | 0–0.2 | body tumble | M |
| specular power | 32 | 16–64 | highlight tightness | M |
| fog density | 0.15 | 0.05–0.4 | depth falloff | L |
| edge glow | 0.3 | 0–0.8 | silhouette rim | M |
| gamma | 0.9 | 0.8–1.2 | overall contrast | L |

## 7. Palette and color

Ground `#05050D`. Crystal base `#263F73`, diffuse `#6699FF`, specular
`#CCE6FF`, refraction tints `#66B3FF`, `#8080FF`, `#9966FF`, edge glow
`#66B3FF`. Interior glow `#4D99FF` at low amplitude. Everything is display
sRGB; the final `pow(c, 0.9)` lifts midtones, which is why the crystal reads as
luminous glass rather than stone.

## 8. Composition and camera

The main crystal is centered and occupies about 70% of the frame height
(octahedron radius 1.2 at distance 4.5 with a 36.9° FOV). Satellites orbit at
radius 1.5, so they enter and leave the frame edges as the camera turns. Wide
aspect shows more empty space between satellites; portrait crops the side
crystals. No horizon, no floor; composition is purely object-vs-void.

## 9. Randomness and seeds

Two stateless hashes: `fract(sin(n) · 43758.5453123)` for satellite sizes and
`fract(sin(dot(p, (127.1, 311.7, 74.7))) · 43758.5453123)` for internal glow.
No seed, no state; both are deterministic across runs. No warmup — the first
frame is complete.

## 10. Performance budget

100 march steps × an SDF of 6 octahedra + a box, plus a 6-tap normal and a
23-line shading path. This is the heaviest per-pixel cost of the family besides
MetaballOrbit. At DPR 1.5 and 640x400 it holds 60 fps on a discrete GPU and
lands around 30–45 fps on weak integrated graphics. Cut order: DPR, march
steps to 72, satellite count to 4.

## 11. Host integration

Standard contract, no pointer input, no external assets. Teardown deletes the
program and loses the context. Resize only changes the viewport; the projection
normalizes by `resolution.y`, so the composition is aspect-stable.

## 12. Failure modes and tells

- **Crystal looks smooth rather than faceted →** march step multiplier above
  0.95 or epsilon too large; the surface is being clipped early.
- **Interior is solid glass with no lattice →** the box carve sign is inverted,
  or the lattice cell is so large that the subtraction misses the body.
- **Satellites fuse into one blob →** `smin k` too high.
- **Satellites missing →** orbit radius grew past the far plane or the hash
  produced a near-zero size.
- **Everything is flat navy →** diffuse light direction parallel to the view
  direction.
- **Aliased silhouette →** MSAA off; the original enables antialias.
- **Frame drifts/rotates too fast →** object and camera rotations are applied in
  the same space instead of object space.

## 13. Tuning knobs

1. `smin k` — how crystalline versus how molten the body is (0.2–0.4).
2. lattice cell / box — the checkerboard pitch and hole size.
3. march steps — facet crispness (72–120).
4. satellite offset — composition density at the edges (1.2–1.8).
5. edge glow — silhouette pop (0.2–0.6).

## 14. Verification checklist

- One dominant blue faceted form, centered, occupying ~70% of the height.
- Visible square lattice through at least one face.
- Bright rim on the silhouette, dark interior.
- Five smaller octahedra near the frame edges.
- Background is near-black with a faint navy cast, never grey.
- Specular highlights move as the body rotates; no flicker.
- Compare with `assets/posters/crystalline-depths.jpg`: same facet scale and
  lattice pitch. Satellite positions depend on time.

## 15. Porting notes

Requires highp in practice: the lattice carve is a subtraction at 1e-4 epsilon
and mediump produces stair-stepping on the holes. Keep the step multiplier below
1.0 or the lattice will be skipped in places.
