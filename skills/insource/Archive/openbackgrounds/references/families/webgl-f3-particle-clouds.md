---
family: webgl-f3
name: Particle Clouds
renderer: webgl1
members: [galaxy-spiral, warp-field, orbit-belt, particle-waves, dna-helix, cosmic-anomaly]
---

# WebGL F3 — Particle Clouds

Six scenes are made of point sprites and nothing else: no meshes, no lines, no
textures. Every visual is the sum of thousands of soft additive dots whose size
comes from perspective. Five are hand-written WebGL1 with a custom point shader;
one is three.js with a bloom composer.

## Members

| id | name | lines | points | motion computed | look |
| --- | --- | --- | --- | --- | --- |
| galaxy-spiral | Galaxy Spiral | 514 | ~8–10k | vertex shader, polar storage | spiral disc |
| warp-field | Warp Field | 435 | 2600 + 5200 line verts | vertex shader, phase | radial speed streaks |
| orbit-belt | Orbit Belt | 574 | 2058 + 9984 line verts | vertex shader, Kepler | concentric rings |
| particle-waves | Particle Waves | 583 | ~8–9k | vertex shader, wave sum | lattice ocean |
| dna-helix | DNA Helix | 616 | 3840 | CPU per frame | double helix |
| cosmic-anomaly | Cosmic Anomaly | 532 | ~64.6k | vertex shader + JS group | bloomed sphere |

Effort: the five raw-WebGL scenes are L — WarpField and GalaxySpiral are the
cheapest, ParticleWaves and OrbitBelt add trail topology, CosmicAnomaly is a
single three.js shader on a quad. DNAHelix is XL (616 lines, double-helix
trail topology).

## Shared scaffold

All six use the standard holder/canvas mount, size from the holder with a window
fallback, and clamp DPR — 1.5 for GalaxySpiral, WarpField, OrbitBelt, and
ParticleWaves 1.75, DNAHelix and CosmicAnomaly 2. Five hand-write
`getContext("webgl")`; CosmicAnomaly goes through `THREE.WebGLRenderer`. All
build their geometry once at mount, then either leave it static (GalaxySpiral,
WarpField, OrbitBelt, ParticleWaves) or update it per frame (DNAHelix). Teardown
always deletes every buffer and program and hands the context back — with
`WEBGL_lose_context` in the raw scenes and `forceContextLoss()` in three.js.

Buffer layout is the interesting part. GalaxySpiral and OrbitBelt store polar
coordinates and animate entirely in the vertex shader, so the buffer leaves
JavaScript memory after upload. WarpField stores a cylinder position plus a
depth seed. ParticleWaves stores the flat lattice and computes height in the
shader. DNAHelix is the exception: positions live in a CPU array that is
rewritten and uploaded with `bufferSubData` every frame.

Two scenes listen to `ResizeObserver` as well as `window.resize` (ParticleWaves,
DNAHelix) and three listen to touch events (ParticleWaves, DNAHelix,
CosmicAnomaly). Cosmetic pointer handling differs:
GalaxySpiral has none; WarpField has none; OrbitBelt none; ParticleWaves and
DNAHelix smooth at 0.08 per frame; CosmicAnomaly lags at 0.03 and uses the
pointer only for a highlight.

## Math vocabulary

**Projection.** Four scenes fake perspective as `clip = (xy · focal / w, 0, w)`.
GalaxySpiral, OrbitBelt and WarpField deliberately set clip w equal to `w`, so
the divide lands twice and on-screen radius is `R · focal / (z + d)²`;
ParticleWaves instead builds a conventional perspective matrix. The squared form
magnifies near geometry and is what makes each disc sit in a dark field instead
of filling the frame. The three matrix scenes are ParticleWaves (52°), DNAHelix
(36°) and CosmicAnomaly (70°).

**Sprite size.** Every raw scene writes `gl_PointSize` by hand:
`size_world · focal · height · 0.5 / w`, clamped — 1–150 (galaxy), 1–30 (warp),
1–64 (orbit), 4–120 (waves), 1+ (DNA). three.js writes
`size · 320 / −mv.z · pulse` (cosmic). The clamp minima matter: they keep far
particles visible as a texture instead of sub-pixel noise.

**Additive accumulation.** All six blend `SRC_ALPHA, ONE` (three.js
`AdditiveBlending`) with depth test off and depth write off, except CosmicAnomaly
which leaves depth testing on but sets `depthWrite: false` on the point
materials. Brightness comes from overlap; no scene has a tone map. The fragment
falloffs are the family's shared vocabulary: `pow(1 − 2d, n)` (galaxy, warp,
orbit), `(1 − |uv|²)^2.3` (waves), `smoothstep` rings (DNA),
`exp(−n r)` (cosmic).

**Seeded vs unseeded.** GalaxySpiral (mulberry32, seed 20260923 + noise seed
20260923+991), WarpField (20260922), OrbitBelt (20260925) are reproducible.
ParticleWaves is fully deterministic (lattice). DNAHelix and CosmicAnomaly use
`Math.random()` and differ per mount.

## Shared helpers

- **mulberry32**: `state = (state + 0x6D2B79F5) >>> 0` followed by two `imul`
  mixes; returns `state / 2³²`. Used by the three seeded scenes.
- **Point fragment with core**: `k = 1 − 2d`, `halo = k^p`, `core = k^q`,
  `rgb += white · core` — galaxy (p 3.2−2·soft, q 8), warp (2.4/9), orbit
  (2.6/10). The white core is what makes additive dots read as stars rather than
  blobs.
- **Depth color ramp**: warp maps `depthT^0.7` from white to blue; orbit maps
  radius from warm to cool; galaxy maps radius from gold to blue. All are
  two-stop `mix` chains over normalized radius/depth.
- **Perspective point size** with a ratio like `focal · height · 0.5 / w`.

## Conventions

World units are arbitrary; the ratio of scene extent to camera distance sets
composition. Time is seconds on a RAF origin. Angles in radians. Pointer is
normalized to −1…1 over the window, y down. Colors are display sRGB written
directly to 8-bit buffers. Canvas alpha: opaque for GalaxySpiral, WarpField,
OrbitBelt; transparent for ParticleWaves and DNAHelix, which depend on the host
`#000000 → #1A0033` gradient; CosmicAnomaly is transparent but usually covered by
its HDR background.

## Variation map

| if you want | change |
| --- | --- |
| a denser galaxy core | raise galaxy-spiral bulgeStars, keep haze alpha low |
| slower warp | lower warp-field speed toward 0.1 |
| longer comet tails | raise orbit-belt trailArc toward 0.4 |
| rougher ocean | raise particle-waves amplitude toward 32 |
| a tighter DNA coil | raise dna-helix turns toward 9π |
| a softer anomaly | lower cosmic-anomaly bloom strength toward 0.6 |
| more rings | raise orbit-belt belts, keep inclMax under 0.25 |
| a wider star fan | raise warp-field focal toward 1.5 |

## Porting

**WebGL1.** All raw scenes are GLSL ES 1.00: `attribute`/`varying`/`gl_FragColor`.
`highp` is required in WarpField (phase is a `fract` of elapsed time), GalaxySpiral
and OrbitBelt (squared-depth divide); mediump is fine in ParticleWaves and
DNAHelix. Point sprites larger than the implementation's `ALIASED_POINT_SIZE_RANGE`
are silently clamped, so the 120–150 px roofs may be lower on mobile.

**three.js.** CosmicAnomaly's shaders are `ShaderMaterial`s with
`vertexColors: true`; the `size` attribute is custom, so `PointsMaterial` cannot
replace them. Bloom must run in an `EffectComposer` after `RenderPass`. Do not
enable tone mapping — the original relies on the bloom pass alone to roll off
highlights. `outputColorSpace = SRGBColorSpace` is the only color management.

## Failure modes

- **Dots but no glow →** additive blend replaced by alpha-over, or the white
  core term dropped.
- **Far particles disappear →** minimum `gl_PointSize` clamp removed.
- **Density surges/vanishes over time →** a per-particle timer wrapped with
  `if (t > life) respawn` instead of a modular phase function.
- **Scene stretches into ovals on resize →** focal x not divided by aspect.
- **Everything is flat grey →** sRGB framebuffer with linear-authored colors, or
  a renderer tone map stacked on an already saturated additive scene.
- **CPU cost grows every frame →** typed arrays re-allocated instead of reused
  (DNAHelix is the only scene that should upload positions per frame).
- **Huge point sprites on one GPU only →** the point-size clamp exceeds the
  driver's max aliased size.

## Verification heuristics

Each raw scene issues one or two draw calls; CosmicAnomaly issues ten plus
composer passes. Count the points from the buffer sizes above. Additive scenes
must have a white or near-white core in dense regions and saturated hue at the
edges. The four deterministic scenes (three seeded plus ParticleWaves) reproduce
exactly at t = 3 s; DNAHelix and CosmicAnomaly use `Math.random()` and do not,
so poster comparison must allow for that. Transparent scenes must
show the host gradient in empty areas — if they are black, the canvas alpha flag
or clear color is wrong.
