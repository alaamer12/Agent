---
family: webgl-f2
name: Raymarched Volumes
renderer: webgl1
members: [crystalline-depths, metaball-orbit, liquid-chrome, quantum-foam, endless-range]
---

# WebGL F2 — Raymarched Volumes

Five scenes describe a 3D scene implicitly — an SDF, a heightfield, or a scalar
field — and walk a ray through it per pixel. There is no vertex geometry, no
texture, and no simulation state: the only inputs are fragment coordinates,
time, and the pointer. Each is one draw call over a full-screen quad or
oversized triangle in GLSL ES 1.00 on WebGL1.

## Members

| id | name | lines | primitive | march |
| --- | --- | --- | --- | --- |
| crystalline-depths | Crystalline Depths | 425 | octahedron SDF + lattice carve | 100 sphere-trace steps |
| metaball-orbit | Metaball Orbit | 456 | 10 smooth-min spheres | 64 sphere-trace steps, ortho |
| liquid-chrome | Liquid Chrome | 363 | 5 metaballs, band env | 34 steps, bounded |
| quantum-foam | Quantum Foam | 331 | 3D value-noise iso-surface | 34 volume samples |
| endless-range | Endless Range | 390 | 2D ridged heightfield | 44 world-Z steps + 5 bisections |

Effort profile: LiquidChrome, QuantumFoam, and EndlessRange are L;
MetaballOrbit and CrystallineDepths are XL because of their shading stacks
and multiple march passes.

## Shared scaffold

All five mount into an absolutely positioned holder, size the canvas from the
holder with a window fallback, clamp DPR at 1.5, and render seconds since mount
on a single RAF loop. Resolution uniforms are drawing-buffer pixels, never CSS.
All five re-upload every uniform each frame, including constants, and all five
tear down by cancelling the RAF, removing listeners, deleting the program, and
calling `WEBGL_lose_context` — the gallery outnumbers the browser's live-context
limit.

Three draw an oversized triangle `(-1,-1), (3,-1), (-1,3)`; CrystallineDepths and
MetaballOrbit draw a four-vertex `TRIANGLE_STRIP` quad and pass
`vUv = position·0.5 + 0.5`, though neither fragment shader reads it. No
scene calls `clear`; every pixel is written by the shader.

Context flags differ in ways that matter. CrystallineDepths and MetaballOrbit
request `antialias: true`; MetaballOrbit is also the only one with `alpha: true`
and a CSS radial-gradient on the holder — its transparent black regions are part
of the look. LiquidChrome, QuantumFoam, and EndlessRange take `alpha: false,
antialias: false, depth: false, powerPreference: "high-performance"`.
Blending is enabled unconditionally in the SDF scenes but alpha is written as 1
wherever it matters.

Pointer input is normalized to −1…1 over the window in all five. MetaballOrbit
is the only scene that smooths it: 0.15 lerp per frame plus a velocity term that
decays 0.85 per frame, which produces overshoot. The other four apply the
pointer directly, so the scene jumps with the cursor.

## Math vocabulary

**Aspect.** All five center and divide by `min(res.x, res.y)`, so one p unit is
the short edge and features are isotropic in CSS pixels. Vertical FOV follows
from the camera distance: 36.9° for the two 1.5-depth-ray scenes, 53.1° for
QuantumFoam, and an effectively perspective-free mapping for EndlessRange, whose
horizon is a fixed `p.y = 0.055`.

**Two march topologies.** Three scenes sphere-trace a signed distance: at each
step evaluate the field at the current point and advance by a fraction of it.
CrystallineDepths advances `0.8 d` (under-relaxed so the carved lattice is not
skipped), LiquidChrome `0.92 d` with a relative hit threshold `d < 0.0025 t`,
MetaballOrbit roughly `0.9 d` with a 64-step cap. EndlessRange instead steps in
world Z with `zStep *= 1.115` and accepts the first sample below the heightfield,
then bisects five times — exponential spacing spends samples where perspective
compresses detail. QuantumFoam is not a surface trace at all: it integrates
front-to-back 34 volume samples into emission and transmittance.

**Distance fields.** Metaballs use smooth minimum. Two variants appear:
liquid-chrome's polynomial form `h = clamp(0.5 + 0.5(b−a)/k, 0, 1);
mix(b, a, h) − k h(1−h)`, and the quadratic form
`h = max(k − |a−b|, 0)/k; min(a,b) − h²k/4` used by the others. They agree near
the blend region but not at its edges; do not mix them within one scene. The
octahedron in CrystallineDepths folds the point into a positive octant and
re-expresses the distance with `max(q·n)`; the lattice carve is a periodic box
subtracted with `max(solid, −box + 0.1)`.

**Normals.** CrystallineDepths and MetaballOrbit use central differences at
1e-4 and 1e-3 respectively; LiquidChrome uses the four-tap tetrahedral swizzle
(cheaper, smoother on a metaball neck); EndlessRange uses the heightfield
gradient with a distance-dependent epsilon `0.05 + 0.006 t`, which is also its
anti-aliasing strategy — distant slopes are automatically softened.

**Color.** Every scene closes with `1 − exp(−k c)` (k = 1.35 in EndlessRange,
1.5 in LiquidChrome, 1.6 in QuantumFoam) except MetaballOrbit, which uses
`pow(c, 1.8)` followed by Reinhard-style `c/(c+0.6)`, and CrystallineDepths,
which applies `pow(c, 0.9)` after its fog mix. All then apply a radial
vignette: `1 − smoothstep(inner, outer, |p|) · gain` with gain 0.4–0.5. Values
are authored in display sRGB directly into an 8-bit buffer.

## Shared helpers

- **Value noise** with a smoothstep fade appears twice: 3D trilinear in
  QuantumFoam (`hash31` = `fract(p·(0.1031,0.103,0.0973))` + dot scramble) and 2D
  bilinear in EndlessRange (`hash21` = `fract(p·(123.34,456.21))` + dot
  scramble). Both return 0…1; the iso-level assumptions in each scene depend on
  that range.
- **Cheap angle proxy:** `|L − rd|` for unit vectors stands in for the angle
  between the sun and the view ray (EndlessRange sun disc and halo).
- **Spike function:** `exp(−(min(|x|/w, 4))²)` gives symmetric soft bands in
  LiquidChrome's studio environment; `abs` first because `pow` of a negative
  base is undefined in GLSL.
- **Bounded march:** LiquidChrome's analytic ray/sphere test at radius 2.35
  avoids marching empty space; the same trick works for any isolated cluster.

## Conventions

Handedness is right-handed with the camera on +Z looking down −Z (LiquidChrome,
CrystallineDepths use −Z depth; MetaballOrbit is orthographic with rays along +Z
from −2). Units are world units with no physical meaning; the frame is what
matters. Time is seconds, angles radians. The pointer is screen-space −1…1, y
down, and each scene converts it to rotation or offset itself. Canvas alpha and
blend state are documented per scene; only MetaballOrbit shows a host backdrop.

## Variation map

| if you want | change |
| --- | --- |
| finer crystal facets | raise crystalline-depths march steps toward 120 |
| more separated metaballs | lower liquid-chrome `blend` toward 0.45 |
| a denser chrome studio | raise the band powers in envMap, keep spike widths |
| bigger foam membranes | lower quantum-foam `fieldScale` toward 1.2 |
| higher mountains | raise endless-range `height`, keep cameraHeight under 0.7·height |
| faster flight | raise endless-range `speed` (0.4–2.0) |
| more satellites | raise crystalline-depths sub-crystal count to 8 |
| softer contours | raise the hit epsilon / march multiplier |

## Porting

Nothing here needs extensions, textures, or derivatives: one program, one
buffer. Keep fragment coordinates in device pixels — CSS-space rays change every
angle by the DPR. WebGL2 ports translate the attribute/varying/gl_FragColor
names but must keep the `max(0.0, …)` guards before `pow`. CrystallineDepths and
LiquidChrome require `highp`: their lattices and relative epsilons stair-step in
mediump. In three.js, a `ShaderMaterial` with `depthTest: false` maps directly;
disable the renderer's tone mapping and output color-space conversion, or the
double tone map will wash the scene out. MetaballOrbit's CSS gradient must be
reproduced on the host element, not baked into the shader.

## Failure modes

- **Silhouette crawls and sparkles →** step multiplier at 1.0 or an epsilon well
  below the DPR-scaled pixel footprint; lower the multiplier or raise epsilon.
- **Surface has visible stair-steps →** mediump on a scene with a relative
  epsilon or a subtraction (CrystallineDepths, LiquidChrome); promote to highp.
- **Whole frame black or solid background →** the camera points away from the
  field, or the bounding-sphere gate never opens.
- **Terrain pops and flickers at distance →** exponential Z growth too
  aggressive, too few steps, or a fixed normal epsilon.
- **Volume scenes band into stripes →** sample spacing too large relative to the
  noise frequency; lower spacing or raise sample count.
- **Frame is flat and plastic →** the environment has broad gradients instead of
  tight power bands; narrow the spike widths and raise the powers.
- **Tone map crushes everything →** two exposures stacked (scene tone map plus a
  renderer's ACES/AgX pass).

## Verification heuristics

one draw call, three or four vertices, zero texture units, no `clear` call. The
four opaque scenes never show the page gradient; MetaballOrbit must. Corner gain
is 0.4–0.6 everywhere, so no corner is black and none is full brightness. A
still at t = 3 s reproduces exactly across runs — no RNG exists in this family.
Resize to 1920x1080 keeps feature size in CSS pixels and only widens the frame;
the horizon in EndlessRange must stay 5.5% above centre (44.5% from the top).
