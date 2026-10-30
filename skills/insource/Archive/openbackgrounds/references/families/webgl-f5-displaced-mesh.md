---
family: webgl-f5
name: Displaced Mesh
renderer: three
members: [sombrero-dunes, chromatic-knot, facets-tunnel, voxel-storm, pulse-orb]
---

# WebGL F5 — Displaced Mesh

Five three.js scenes built around a solid form: a wireframe heightfield, a
shaded torus knot, a bore made of instanced prisms, a funnel of instanced cubes,
and a noise-displaced sphere. None of them uses a light. Every surface is shaded
by a hand-written `ShaderMaterial` — a fixed key/fill direction, a fresnel rim, a
travelling lamp, or an emissive gradient — and every scene adds at least one
unlit additive plane as a cheap bloom. This is the family where geometry counts,
vertex-shader arithmetic, and the colour of glow planes do most of the work.

## Members

| id | name | lines | geometry | motion | look |
| --- | --- | --- | --- | --- | --- |
| sombrero-dunes | Sombrero Dunes | 371 | PlaneGeometry 40×24, 360×220 segs, wireframe | vertex displacement, 2 simplex taps | lavender dune field to the horizon |
| chromatic-knot | Chromatic Knot | 546 | TorusKnotGeometry(1.5, 0.42, 168, 24, 2, 3) | slow rigid rotation on three axes | oil-slick knot, 85% of frame height |
| facets-tunnel | Facets Tunnel | 626 | 30 instanced 9-gon prisms, 2.5 units each | instance recycling past a moving lamp | slate faceted bore, violet core |
| voxel-storm | Voxel Storm | 544 | 1,900 instanced cubes, 0.17 base size | shader placement + per-cube spin | blue cube funnel with amber eye |
| pulse-orb | Pulse Orb | 729 | IcosahedronGeometry(1.92, 14) + shell + core | radial noise displacement | purple membrane, cyan rim, glass limb |

Effort: SombreroDunes is the cheapest (L — one dense plane and two noise taps),
then ChromaticKnot (XL only because of its shading stack), VoxelStorm and
FacetsTunnel (XL — instanced placement and per-instance recycling), PulseOrb
(XL — three concentric shells, 13.5k displaced vertices, derived normals).

## Shared scaffold

All five mount into `absolute inset-0 pointer-events-none` holders with a
`block w-full h-full` canvas, take no props, and build everything at mount.
Sizing comes from holder `offsetWidth/Height` with a `window.innerWidth/Height`
fallback, resolved at mount and on `window resize`. Every scene uses
`new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })`,
`setPixelRatio(Math.min(devicePixelRatio || 1, 1.75))`,
`setSize(width, height, false)`, `setClearColor(0x000000, 0)` and
`outputColorSpace = THREE.SRGBColorSpace`. The canvas is therefore transparent
and the scenes are composed against the host backdrop `#000000 → #1A0033`;
black is the clear colour, violet is the page.

Each file has one `THREE.Clock`, one RAF loop reading `clock.getElapsedTime()`,
and one resize handler that updates `camera.aspect` and the projection matrix.
ChromaticKnot and PulseOrb also switch FOV on aspect (`<1.1` → 54° / 56°, else
40° / 42°); the other three keep a fixed lens (Sombrero 52°, Facets 76°, Voxel
50°). Teardown cancels the frame, traverses the scene disposing geometry and
materials, then `renderer.dispose()` + `renderer.forceContextLoss()` — the
gallery runs more scenes than a browser keeps live contexts.

Render state is split by role: solid bodies (`depthWrite: true`, `FrontSide`),
additive planes and point sprites (`transparent`, `depthWrite: false`, usually
`depthTest: false` with a high `renderOrder`), and the Sombrero wireframe
(`transparent`, additive, `depthWrite: false`, `depthTest: true`).

## Math vocabulary

**Noise.** Ashima's 3D simplex (`snoise`/`cnoise`, gradient-noise variant) is
the only noise in the family. SombreroDunes displaces a plane with two octaves,
a 0.95-amplitude base at 0.24 frequency and a 0.095 detail at 0.9, offset in
time along z. PulseOrb uses a base tap at frequency 1.35 and a detail tap at 3.1
weighted 0.32, both evaluated on the normalised direction. ChromaticKnot and
FacetsTunnel use no noise at all; VoxelStorm gets its irregularity from seeded
attributes.

**Radial displacement and normals.** PulseOrb is the textbook case: displace
`dir * (uRadius + height)`, then recover the normal by probing the dominant
octave along two tangents (`eps = 0.06`), forming the tangential gradient, and
setting `normal = normalize(dir − gradient * amp / uRadius)`. Any port that
forgets the `/ uRadius` term gets a normal that is far too steep and a rim that
flickers.

**Fake lighting.** Nothing here is lit by three. VoxelStorm shades each cube
against a fixed view-space key `(0.28, 0.72, 0.63)` and fill `(−0.55, −0.4,
0.35)`, adds `pow(1 − dot(n, view), 3)` rim, and lets hot cubes emit amber.
ChromaticKnot computes fresnel, two specular lobes (exponent 96 warm, 33.6
cold), and a film term from `uv` and time before feeding a cosine palette.
PulseOrb is `0.2 + key·0.8 + bounce·0.2` plus a rim in `#4CF5DF`. FacetsTunnel
multiplies a slate tint by the lamp's angular falloff and a fog term.

**Instanced placement.** VoxelStorm and FacetsTunnel never move vertices on the
CPU. VoxelStorm carries per-instance `aSeed` (radius, angle, height, phase) and
`aTint`, and the vertex shader computes the cylinder position, differential
rotation `omega = swirl / (0.8 + 0.5·r)`, twist, and per-cube spin, rebuilding
the normal with a Rodrigues rotation. FacetsTunnel bakes only a random roll per
ring into the instance matrix; the shader does the rest.

**Recycling and depth fade.** Both tunnels wrap with `mod`: VoxelStorm climbs
`mod(seedZ·H + t·climb, H) − H/2`, FacetsTunnel runs
`mod(aZ + travel, span) − span + segmentLength`. Distance is linear in view
space: `fade = 1 − smoothstep(fogNear, fogFar, −view.z)` — 13–34 for the voxel
column, 32–72 for the bore, with a near-plane `smoothstep(0.5, 7.0, ahead)`
so faceted walls do not pop in at the camera.

**Composition.** Standard perspective cameras, so framing is camera distance
against object extent: orb radius 1.92 at z 7.3, knot radius ~1.9 at z 7.4,
voxel column 13.5 tall at z 15.5, tunnel 75 long at z 0 with a 76° lens.

## Shared helpers

- **`rgb()` raw-palette helper** — `new THREE.Color((r)/255, (g)/255, (b)/255)`
  from a hex literal. Hand-written shaders write `gl_FragColor` and skip three's
  colourspace pass, so palette values must be uploaded as display-space
  channels. `new THREE.Color("#rrggbb")` is converted to linear and comes out
  too dark. `MeshBasicMaterial` colours on the Sombrero base plate are the
  exception and use hex normally.
- **LCG** — `state = (state·1664525 + 1013904223) mod 2³²`, used by every scene
  with randomness: ChromaticKnot 777 (motes), FacetsTunnel 8821 (walls) and
  +991 (dust), VoxelStorm 90210 (cubes) and +41 (embers), PulseOrb 31337
  (motes). SombreroDunes is deterministic with no RNG.
- **Additive glow plane** — a `PlaneGeometry` with an unlit shader, radial or
  columnar falloff, `depthWrite: false`, `depthTest: false`, additive blending,
  high `renderOrder`: 17×17 aura (knot), 22×22 beacon (tunnel), 7.5×13.5 core
  glow (voxel), 15×15 aura (orb), 90×54 halo (dunes). Sombrero's sits below the
  terrain, not behind it.
- **Point-sprite shader** — motes/embers/dust all share the same shape: a small
  `BufferGeometry` of seed positions animated entirely in the vertex shader,
  `gl_PointSize = size · dpr · k / max(−view.z, 1)`, a soft disc in the
  fragment shader, additive blend, `frustumCulled = false`.
- **Billboarding** — the voxel core glow is re-aimed at the camera every frame
  (`lookAt` on x/z only, keeping its height), the only scene that needs it.

## Conventions

Seconds since the first RAF; radians everywhere; three's y-up, camera looking
at the origin with a slow sinusoidal drift. World units are consistent within a
scene but not across scenes. Solid bodies write depth; glow planes never do.
Canvas alpha is transparent in all five scenes, so empty regions show the host
`#000000 → #1A0033` gradient — a white or grey page will wash the palettes out.
Instanced and shader-placed meshes set `frustumCulled = false`, because their
geometry bounds describe the unit cube/prism, not where instances end up.

## Variation map

| if you want | change |
| --- | --- |
| a calmer dune field | sombrero-dunes base amplitude 0.95→0.6, ribbon term 0.2→0.12 |
| a denser knot | chromatic-knot torus segments 168→240, tubular 24→32 |
| a shorter tunnel | facets-tunnel `span` 75→48, keep `segmentLength` 2.5 |
| a warmer tunnel | facets-tunnel palette lobes red/amber instead of pink/cyan |
| a wider storm funnel | voxel-storm `radiusMax` 7.6→9.5, `flare` 0.42→0.32 |
| fewer, larger cubes | voxel-storm `voxels` 1900→900, `cubeSize` 0.17→0.24 |
| a lumpier orb | pulse-orb `detailWeight` 0.32→0.5, `frequency` 1.35→1.8 |
| a harder rim | pulse-orb `rimPower` 2.6→1.8, `rimGain` 1.5→2.0 |

## Porting

**Colour management is the trap.** Keep the three-argument `Color` for every
palette entry consumed by a `ShaderMaterial`. Do not turn off
`outputColorSpace = SRGBColorSpace` to compensate — that only changes built-in
materials.

**three version.** Built on a modern three (r150+) with `outputColorSpace`;
older releases call it `outputEncoding = THREE.sRGBEncoding`. `InstancedMesh`,
`setMatrixAt`, `instanceMatrix.needsUpdate`, `TorusKnotGeometry`, `Fog`, and
`forceContextLoss` exist in every version used here. No post-processing library
is involved; the glow is all geometry.

**Fog.** SombreroDunes sets `scene.fog = new THREE.Fog(0x040014, 18, 52)` but
only the `MeshBasicMaterial` base plate honours it — the custom dune shader
fades itself. Do not assume three's fog chunks are injected into a
`ShaderMaterial`.

**Lifecycle.** Framework-neutral: build on mount, size from the holder, listen
to `window resize`, dispose every geometry/material on unmount and lose the
context. `useFpsMeter()` is a singleton for one mounted scene; do not mount two
of these backgrounds on one page with it.

## Failure modes

- **Everything is too dark →** palette hex passed through `new THREE.Color("#…")`
  into a raw shader; switch to the three-argument helper.
- **Instanced meshes vanish at some camera angles →** `frustumCulled` left true;
  the unit-cube bounds say nothing about shader placement.
- **Bore wall is inside-out or see-through →** the prism winding must face the
  inside with `FrontSide` and `depthWrite: true`; flipping to `BackSide` loses
  the far wall and the tunnel reads hollow.
- **Cubes pop at the top/bottom of the funnel →** recycling range does not match
  the drawn height (`uHeight` vs the ±half-height offset).
- **Orb rim crawls with noise →** normal probe epsilon too small, or the
  gradient not divided by radius; keep eps 0.06 and the `/ uRadius` term.
- **Dune field disappears into black →** additive wireframe with no base plate
  and no halo; the scene needs its dark ground planes to read at all.
- **Orb or knot looks flat →** fresnel driven by screen UV instead of
  `dot(normal, view)`.
- **Glow hides the object →** additive plane left depth-tested, or its
  `renderOrder` below the solid body.

## Verification heuristics

Draw calls: Sombrero 3 (dunes, base, halo), Chromatic 4 (knot, aura, motes,
backlight), Facets 3 (tunnel, dust, beacon), Voxel 3 (cubes, embers, core),
Pulse 5 (membrane, core, atmosphere, motes, aura). Measure coverage on the short
axis: orb ≈ 0.85, knot ≈ 0.85, voxel ≈ 0.8, dunes fill width with a horizon near
45%, tunnel fills the frame with a bright centre. Empty areas must show the
violet page gradient, not flat black. Seeded scenes (knot, facets, voxel, orb)
reproduce exactly at t = 3 s; SombreroDunes is deterministic. Watch for the
additive planes saturating to white in the brightest region — that is the
family's usual over-threshold symptom.
