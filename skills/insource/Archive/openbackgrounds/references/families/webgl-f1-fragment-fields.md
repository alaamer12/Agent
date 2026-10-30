---
family: webgl-f1
name: Fragment Fields
renderer: webgl1
members: [neural-noise, caustic-pool, nebula-currents, iridescent-film, magma-veins, solar-corona, moire-veil, voronoi-circuit, neon-horizon, hologram-scan, event-horizon]
---

# WebGL F1 — Fragment Fields

Eleven scenes draw one full-screen pass: no textures, no simulation state, no
per-frame allocation. Each pixel is a function of its fragment coordinate, a few
uniforms, and time, in GLSL ES 1.00 on WebGL1.

## Members

| id | name | lines | distinguishing trait |
| --- | --- | --- | --- |
| neural-noise | Neural Noise | 282 | 14 rotated sine cascades |
| caustic-pool | Caustic Pool | 263 | ridge and net off three waves |
| nebula-currents | Nebula Currents | 251 | six self-warping layers, alpha 0.65 |
| iridescent-film | Iridescent Film | 410 | thin-film interference, dry patches |
| magma-veins | Magma Veins | 326 | warped FBM, zero-set cracks |
| solar-corona | Solar Corona | 327 | 3D noise on unit direction |
| moire-veil | Moire Veil | 323 | two orbiting ring grids |
| voronoi-circuit | Voronoi Circuit | 331 | F1/F2 cells, edge pulses |
| neon-horizon | Neon Horizon | 345 | perspective grid, banded sun |
| hologram-scan | Hologram Scan | 333 | four ray-cast planes, RGB split |
| event-horizon | Event Horizon | 325 | lens warp, accretion ring |

## Shared scaffold

Nine scenes draw an oversized triangle, vertices (-1,-1), (3,-1), (-1,3), in one
three-vertex `TRIANGLES` call. NeuralNoise and NebulaCurrents draw a quad as a
four-vertex `TRIANGLE_STRIP`. The vertex shader writes `gl_Position` directly;
only the quad scenes pass a varying, vUv = position·0.5 + 0.5. Everything else
works from `gl_FragCoord`, in drawing-buffer pixels, origin bottom-left.

All bind uniforms by name after link, cache locations once, and re-upload every
frame including static values. Resolution is the drawing-buffer size, never CSS.
Time is seconds since mount except NeuralNoise, which receives milliseconds and
multiplies by 0.00007.

Context flags: nine opaque scenes take `alpha: false, antialias: false,
depth: false, powerPreference: "high-performance"`; NeuralNoise takes `alpha:
true, antialias: true`; NebulaCurrents takes `alpha: true, premultipliedAlpha:
false, antialias: false`. No scene calls `clearColor` or `clear`; the pass
covers every pixel. Depth testing is disabled explicitly only in the two
transparent scenes; culling only in NebulaCurrents.

Ten scenes read the pointer normalized to the window: x = clientX/innerWidth
mapped to -1..1, y likewise with y down. NeuralNoise normalizes to 0..1, flips
y, and lerps 0.05 per frame; it is the only smoothed pointer. Sizes come from
the holder with a window fallback; the DPR clamp is 1.5 except NebulaCurrents at
1.6. All listen to `window.resize`; none uses a ResizeObserver.

## Math vocabulary

**Aspect.** Nine scenes center and divide by the short axis: p = (fragCoord −
0.5·resolution)/min(resolution.x, resolution.y). At 640x400 that is p.x in ±0.8
and p.y in ±0.5; one p unit is 400 CSS px at DPR 1, so features stay constant in
CSS pixels. NeuralNoise uses uv = 0.3·vUv with x times width/height, isotropic in
pixels but windowed on canvas height. NebulaCurrents centers vUv and multiplies
x by aspect, so its radial envelope measures a short half-axis of 0.5.

**Closed forms.** Nothing integrates. CausticPool sums three sines and applies
two powers; MoireVeil multiplies Gaussian line fields; VoronoiCircuit takes the
two nearest of a 3x3 neighbourhood; NeonHorizon divides by a ground depth;
EventHorizon bends its sample by 1/(r² + 0.045). Iteration counts: 14
(NeuralNoise), 6 (NebulaCurrents), 3 plane waves, 9 neighbours, 4 planes, 2
noise octaves (MagmaVeins, SolarCorona).

**Derivatives.** NeonHorizon computes exact screen derivatives of its grid,
ds/dy = camHeight·rowFreq/y² and dx/dx = camHeight·colFreq/y, and divides world
distance by them, keeping lines one pixel wide without the derivatives
extension. IridescentFilm takes its normal from a central difference with
eps = 0.006 units despite a comment calling it analytic. HologramScan scales
line width by ray hit distance.

**Color.** Eight scenes close with c = 1 − exp(−k·col); CausticPool and
NeuralNoise clamp; NebulaCurrents clamps only alpha. Every scene ends with a
radial vignette, keeping 0.40–0.60 of centre brightness at the corner. Palettes
are two to five vec3 constants mixed by a scalar, authored in display sRGB and
written straight to an 8-bit backbuffer.

## Variation map

| if you want | change |
| --- | --- |
| bigger, calmer lobes | raise neural-noise uvScale or lower baseScale |
| a finer caustic mesh | raise caustic-pool scale toward 8, keep netSharpness 9 |
| a warmer nebula | raise the accent mix above 0.6 in nebula-currents |
| thicker interference bands | lower iridescent-film carrier values, not thicknessUm |
| fewer, bolder magma seams | lower magma-veins scale toward 1.6, warp toward 1.0 |
| longer corona filaments | raise solar-corona radialFreq, keep angularFreq 4.4 |
| a denser moire lattice | raise moire-veil ringFreq, keep thickPx below 1 |
| a stronger glitch | widen hologram-scan's zoom split from ±0.006 |

## Precision

`mediump` covers the nine sine-and-distance scenes and is what the originals
ship. Three places break on mobile GPUs. Hashes multiplying by 123.34, 456.21,
or 43758.5453 lose low bits and turn into blocks (MagmaVeins, SolarCorona,
VoronoiCircuit, EventHorizon, MoireVeil); promote the hash to highp. Sine
arguments above roughly 100 rad lose phase and band (IridescentFilm's carrier
110 times q). And `pow` with exponents 26, 44, or 55 turns precision loss into
speckle.

## Blend and clear state

Nine scenes leave blending off and write alpha 1, so they are opaque regardless
of the canvas flag; the host gradient never shows. NeuralNoise enables
`SRC_ALPHA, ONE_MINUS_SRC_ALPHA` and writes alpha up to 0.6, so the host backdrop
is part of the image. NebulaCurrents enables `ONE, ONE_MINUS_SRC_ALPHA` — a
premultiplied blend — while emitting straight alpha, and asks for
`premultipliedAlpha: false`; mid-alpha regions composite brighter than a
straight-alpha port predicts. Reproduce blend function and flag together. No
scene clears; an opaque clear erases the gradient behind NeuralNoise.

## Porting

No textures, extensions, or derivative instructions: one program, one buffer.
Keep fragment coordinates in device pixels and divide by the drawing-buffer
short axis; CSS pixels change every feature size by the DPR. WebGL2 or GLSL
3.00 ports must translate `attribute`/`varying`/`gl_FragColor` and keep the rule
that `pow` of a negative base is undefined — every original guards with
`max(0.0, …)`. In three.js a `ShaderMaterial` with `depthTest: false` and the
same blend constants maps directly; stop the renderer injecting tone mapping or
color-space conversion.

## Failure modes

- **Entire frame black →** full-screen triangle culled or wound backwards;
  disable culling.
- **Pattern stretched into ovals →** aspect from CSS size or the long axis
  instead of the short one.
- **Motion 1000x off →** seconds where NeuralNoise expects milliseconds.
- **Uniform changes do nothing →** locations fetched before link, or a re-link
  with stale locations.
- **Opaque rectangle over the page gradient →** canvas without alpha, or an
  opaque clear.
- **Banding and speckle on phones →** mediump hash or a large `pow` exponent;
  promote to highp.

## Verification heuristics

One draw call, three or four vertices, zero texture units. Nine frames fully
opaque; NeuralNoise alpha never above 0.6; NebulaCurrents never above 0.65.
Corner gain between 0.40 and 0.60, so no corner is black or full brightness. A
still at t = 3 s matches a second run: no RNG, no warmup. Resizing to 1920x1080
leaves CSS feature size unchanged and only reveals more field.
