---
family: webgl-f4
name: Line Geometry
renderer: webgl1 + three
members: [crystal-lattice, field-lines, silk-strands, ribbon-flow, wire-globe]
---

# WebGL F4 — Line Geometry

Five scenes whose structure is drawn as lines: a strut lattice, magnetic field
arcs, sheets of silk filaments, a single shaded ribbon, and a wire globe. Four
are hand-written WebGL1 with static geometry and a vertex shader that animates
and projects; the globe is three.js. `gl.LINES` is the default medium, which means
1 px strokes, additive accumulation, and no depth buffer anywhere in the family.

## Members

| id | name | lines | geometry | motion | look |
| --- | --- | --- | --- | --- | --- |
| silk-strands | Silk Strands | 435 | 12,220 line verts (6,110 segs) | vertex shader, 5 sine waves | stacked gauze sheets |
| ribbon-flow | Ribbon Flow | 362 | 32,768 triangles (129² grid) | vertex shader + derivatives | one shaded violet ribbon |
| crystal-lattice | Crystal Lattice | 525 | 3,888 line + 729 point verts | vertex shader, phonon | glowing strut cube |
| field-lines | Field Lines | 698 | 9,362 line + 2,640 point verts | vertex shader, orbital sines | dipole arc cage + caps |
| wire-globe | Wire Globe | 792 | 5,712 line + 288 point verts | three.js + shaders | cyan sphere with comets |

Effort: RibbonFlow is the cheapest (L — one mesh, one shader, no topology).
SilkStrands, CrystalLattice, FieldLines, and WireGlobe are all XL: two passes
plus derived polar/parametric geometry, no shared scaffold to lean on, and in
the globe six objects with a facing-based depth cue under three.js colour rules.

## Shared scaffold

All five mount into `absolute inset-0 pointer-events-none` holders with a
`block w-full h-full` canvas and no pointer input. Sizing comes from holder
offsets with a `window.innerWidth/Height` fallback, floored at 1 px, resolved at
mount and on `window resize`. DPR caps: 1.5 for CrystalLattice, FieldLines,
SilkStrands; 1.75 for WireGlobe; 2 for RibbonFlow. Teardown cancels the RAF,
deletes every buffer and program, and hands the context back —
`WEBGL_lose_context.loseContext()` for the raw scenes,
`renderer.forceContextLoss()` for the globe. All build geometry once at mount;
nothing in this family uploads vertex data per frame.

Blending is the family's main fork. CrystalLattice, FieldLines, and SilkStrands
use `SRC_ALPHA, ONE`; WireGlobe uses three's `AdditiveBlending`; RibbonFlow is
the exception and uses ordinary `SRC_ALPHA, ONE_MINUS_SRC_ALPHA`. Depth testing
is disabled everywhere; the globe replaces it with a facing term, the lattice
with a depth fade, and RibbonFlow with a slope-based alpha.

## Math vocabulary

**Projection.** CrystalLattice, FieldLines and SilkStrands share one camera
convention: `w = max(q.z + distance, 0.05)`, then
`gl_Position = (q.xy · focal / w, 0, w)`. Because the clip-space w is the same
`w`, the hardware divides a second time, so an object of world size `s` spans
`s · focal / (z + distance)²` on screen. This inverse-square falloff is the
family's signature: near geometry grows fast, the back of each form fades
quickly, and the object sits in a large dark field instead of filling the
frame. Composition is therefore governed by `extent · focal / distance²` —
0.44–0.77 (lattice), 0.62 (field lines), ≈0.4 NDC half-width (silk). The other
two members use real perspective matrices: RibbonFlow (the fourth raw scene) a
75° hand-built camera, WireGlobe three's 44° camera. Those two are the only
scenes where changing FOV widens the field of view rather than merely zooming.

**Depth fade.** `fade = (1 − smoothstep(near, far, w))^p`, with `p` 1.2–1.5, and
windows chosen so the back face nearly vanishes and the front sits at full
strength: lattice 5.0–9.4 at distance 7, field lines 8.4–16.6 at distance 11 (its
shells span 6.2–15.8), silk 2.4–6.0 at distance 3.6. RibbonFlow has no fade —
its alpha is slope-driven — and WireGlobe substitutes `smoothstep(−0.5, 0.55,
dot(normal, view))` for the same purpose.

**Polyline build.** Three scenes bake a curve into segment pairs on the CPU:
silk strands (2D simplex meander along x), field lines (dipole `r = L sin²θ`
truncated at the core sphere), and arcs on the globe (great circles
`p = origin·cos + tangent·sin` lifted by `bulge·sin(πt)`). The lattice is
orthogonal and index-driven. In every case the vertex shader receives a static
position plus a small data vector (`u, v, phase`; `L, θ, kind`; `axis, hull`) and
derives motion from `u_time` alone.

**Point sprite size.** `gl_PointSize = size · focal · height · 0.5 / w`, clamped —
1–44 (lattice nodes), 1–90 (field-line charges), 1–24 (globe nodes), 1–6 (globe
stars). The 0.5 factor converts NDC to pixels; the clamp floor keeps far nodes
visible and the ceiling stops near nodes from cropping their halos.

**Noise.** SilkStrands is the only scene using the `simplex-noise` package (2D
simplex, one octave, phase-locked across a sheet). RibbonFlow uses 3D value noise
(`fract(sin(n)·43758.5453)` hash, trilinear smoothstep, one octave). The lattice
and field lines use pure sinusoids; the globe uses none.

## Shared helpers

- **mulberry32** — `state = (state + 0x6D2B79F5) >>> 0` + two `imul` mixes. Used
  by FieldLines (20260927), SilkStrands (20260926, plus a noise stream at
  +313 = 20261239), CrystalLattice (no RNG).
- **LCG** — `state = (state·1664525 + 1013904223) mod 2³²`, used only by
  WireGlobe (4242, stars at 4319).
- **Point fragment with core** — `k = 1 − 2d`, `halo = k^p`, `core = k^q`, plus a
  near-white core colour: lattice (2.1/11), field lines (2.2/12). Both output
  `alpha · (0.12 + 0.88·halo)`.
- **Hand-rolled rotX/rotY/rotZ mat3** — column-major constructors repeated
  verbatim in each vertex shader (`rotY` is `(c,0,−s | 0,1,0 | s,0,c)`); there is
  no shared module. GLSL helpers are concatenated by template string where two
  programs in one file need them (FieldLines).
- **Tint by axis/kind** — CrystalLattice selects one of three colours by
  `a_data.x`, FieldLines by `kind`, WireGlobe by facing — the pattern is "bake a
  small categorical id into the vertex, mix in the shader".

## Conventions

World units are arbitrary and internally consistent; each scene's `half` /
`lMax` / `length` sets the extent, and composition comes from the ratio to
`distance`. Time is seconds since the first RAF. Angles are radians everywhere.
Vertex order and handedness are OpenGL-standard (x right, y up, z toward the
viewer); the three raw scenes with the hand-built camera use no matrix, so
positive z is toward the camera and `w = z + distance` is the pinhole depth.
RibbonFlow is the raw exception with a matrix stack. Colours are display-space sRGB
written to the framebuffer with no tone map and no gamma step. Canvas alpha:
opaque for CrystalLattice, FieldLines, SilkStrands; transparent for RibbonFlow
and WireGlobe, which therefore depend on the host `#000000 → #1A0033` backdrop.

## Variation map

| if you want | change |
| --- | --- |
| a coarser, more crystalline cube | crystal-lattice `nodes` 9→7, raise `hullBoost` to 2.1 |
| a brighter lattice ripple | crystal-lattice `waveAmp` 0.055→0.08, `waveFrequency` 2.35→3.0 |
| longer field-line trails | field-lines lower `swingMax` toward 0.18 (slower charges pool longer) |
| a denser dipole cage | field-lines `shells` 7→10, `longitudes` 12→16 |
| calmer silk | silk-strands `amplitude` 0.44→0.3, `flowSpeed` 0.16→0.1 |
| less spaghetti in the silk | silk-strands `strandsPerSheet` 26→18, keep noise index shared |
| a thinner ribbon | ribbon-flow fold amplitude 0.2→0.12 |
| more arcs on the globe | wire-globe `arcs` 24→48, keep `arcBase` 0.055 |
| a tighter orbit ring | wire-globe `ringRadius` 3.15→2.8 |

## Porting

**WebGL1.** All raw scenes are GLSL ES 1.00 (`attribute`, `varying`,
`gl_FragColor`); `highp` is used in every vertex shader. RibbonFlow needs
`OES_standard_derivatives` for `dFdx`/`dFdy`; in WebGL2 it is core. `gl.LINES`
ignores `lineWidth` above 1 on almost all drivers — a thicker line means a quad
ribbon, which changes the additive balance and is not the original.

**three.js.** WireGlobe's materials are `ShaderMaterial`s with custom attributes;
`LineBasicMaterial` cannot supply the facing fade or the per-vertex comet glow.
The palette is uploaded as raw display-space channels via a custom `rgb()` helper
— deliberately bypassing three's colour management, because hand-written shaders
skip the output colour-space pass. Setting `outputColorSpace = SRGBColorSpace`
still matters for anything using built-in materials.

**Vue / React / vanilla.** There is no framework coupling: the lifecycle is
"build on mount, resize on window, dispose on unmount". The only shared service
is `useFpsMeter()`, a singleton that assumes exactly one scene is mounted.

## Failure modes

- **Scene fills the frame or vanishes on resize →** focal x not divided by
  aspect, or the `refAspect` clamp dropped.
- **Object looks like a flat card →** the depth fade (or, on the globe, the
  facing term) is missing; without it every line has equal weight.
- **Interior turns into a solid glow →** additive overlap saturated; lower the
  global strength or the geometry count (lattice `nodes`, field `shells`, silk
  sheets).
- **Lines look like they were drawn with a marker →** a canvas 2D port using a
  stroke width above 1, or MSAA disabled at DPR 1.
- **RibbonFlow becomes a flat tinted rectangle →** derivatives extension missing
  (`c` falls back to a constant 0.35).
- **Dust or haze rotates with the object →** view-space data passed through the
  object rotation (FieldLines).
- **Silk reads as spaghetti →** per-strand random noise offsets instead of
  shared sheet coordinates.
- **Globe colours washed out →** palette double-converted through
  `THREE.Color` with colour management on.

## Verification heuristics

Count the draw calls: CrystalLattice and FieldLines issue exactly two
(`LINES` + `POINTS`), SilkStrands one, RibbonFlow one `drawElements`, WireGlobe
six. All additive scenes must show brightness rising with overlap and no
visible line-order artifacts. Composition: check that each form occupies its
stated fraction of the short axis (0.6–0.8 for lattice/field lines, 0.7 for the
globe) rather than the whole frame. Transparent scenes (RibbonFlow, WireGlobe)
must show the host backdrop in empty areas. The three seeded scenes (SilkStrands,
FieldLines, WireGlobe) reproduce exactly at t = 3 s; CrystalLattice and
RibbonFlow are deterministic without a seed.
