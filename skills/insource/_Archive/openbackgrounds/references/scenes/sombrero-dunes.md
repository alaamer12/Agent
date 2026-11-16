---
id: sombrero-dunes
name: Sombrero Dunes
family: webgl-f5
renderer: three
poster: assets/posters/sombrero-dunes.jpg
complexity: L
source_lines: 371
dpr_max: 1.75
deps: [three]
poster_capture: 640x400
---

# Sombrero Dunes — scene reference

## 1. Identity

An endless violet wireframe desert seen from just above the sand: long dune ridges run to a bright horizon line, with a soft ripple — a sombrero-shaped standing wave — pulsing out from the middle distance.

## 2. Perceived look

A dark, spacious instrument rendering: a grid of 1 px lavender lines on near-black, so fine that at the horizon it fuses into a solid glow and in the foreground it resolves into discrete diamonds. The horizon is the composition's anchor — a thin bright band at roughly 45% frame height where the grid converges and, above it, a small set of ridge silhouettes rising into the dark. Because the wireframe is seen at a shallow angle, line density increases dramatically with distance, and that density *is* the brightness: the foreground reads as a sparse net, the middle distance as a textured carpet, the horizon as a line of light. A soft radial halo lifts the centre of the frame to deep violet, and fog dissolves the far edge of the plane into the same colour, so there is no visible border. The sombrero ripple appears as faint concentric rings around the frame's centre, gently breathing, with the plane's centre flattened so the rings read as a depression rather than a dome. The 3 s screenshot shows a bright violet horizon line across the middle, a dark top half with a couple of low ridge crests, and a glowing, densely woven grid filling the bottom half, brightest at the horizon and fading downward.

## 3. Frame anatomy

Back to front (world), with three meshes plus lights:

1. **Clear** `(0,0,0,0)` — canvas transparent; the host's dark backdrop shows through in the upper half.
2. **Halo** — 90×54 plane lying horizontal at y = −2.2 (below everything), radial `smoothstep` falloff, inner `#160033` → outer `#010008`, additive, alpha `smoothstep(1.1, 0.2, d)·0.5`.
3. **Base slab** — 60×34 plane at y = −1.4, flat colour `#0A0018` at opacity 0.42, `depthWrite: false`; it stops the background from showing through the grid's gaps near the horizon.
4. **Dunes mesh** — `PlaneGeometry(40, 24, 360, 220)` rotated −90° about x (horizontal), translated to y = −0.8, drawn as **wireframe**, additive, `depthTest: true`, `depthWrite: false`, vertex-displaced in world y.
5. **Hemisphere light** `#6655FF` / `#07001A` at 0.45 — irrelevant to the custom shader, left in place from the scene template.
6. **Fog** `#040014`, 18 → 52 — applied by three only to built-in materials; the shader's own colour ramp does the equivalent for the grid.

The shader's fragment alpha is `clamp(0.06 + (1 − vUv.y)·0.22, 0, 0.32) · rim`, where `rim = smoothstep(0.5, 0.18, distance(uv, 0.5))` — so the mesh is brightest at its near edge and centre and fades to nothing at its edges.

## 4. Motion law

- **Terrain drift.** Shader time is `t = 0.16·elapsed`. The noise field is sampled at `cnoise(0.24·x, 0, 0.6·t)` — because the plane's local z is always 0, the ridges vary only along x and the third noise coordinate is *time*; the landscape therefore undulates in place rather than translating. One noise cell in time takes `1/0.6 = 1.67` shader-seconds ⇒ **10.4 s** of wall time.
- **Secondary texture.** `cnoise(0.9·x, 0, 0.84·t)` at one-tenth the amplitude — fine cross-ripples.
- **Ribbon.** `sin(0.32x − π/2)·0.2 = −0.2·cos(0.32x)` — static in time, a long wavelength along x that gives the main ridge its shape.
- **Sombrero.** `0.52·sin((0.3t − 4.6·radius)·π)` — concentric rings marching outward from the plane centre; the phase moves at 0.3π rad per shader-second = 0.048π rad/s of wall time (×0.16), so one ring cycle at a fixed radius takes **41.67 s**; ring spacing is 1/4.6 = 0.217 in uv radius.
- **Mesh sway.** `rotation.z = 0.06·sin(0.08t)` — period 78.5 s, a ±3.4° roll that tilts the horizon.
- **Camera orbit.** `x = 0.24·sin(0.028t)` — period 224 s, ±0.24 units of lateral parallax.
- **Phase at t = 0.** The time terms are zero, but the spatial fields are not:
  the ribbon is −0.2·cos(0.32x) and the sombrero already has rings from the
  centre outward. Open-ended.

## 5. Technique and math

three.js with one custom `ShaderMaterial` in wireframe mode; all displacement in the vertex shader, no CPU geometry work after mount.

- **Mesh.** `PlaneGeometry(40, 24, 360, 220)` — 360×220 = 79,200 quads (158,400 triangles) rendered as wireframe, i.e. ~237k line segments. Local coordinates: x ∈ [−20, 20], y ∈ [−12, 12], z = 0. Rotated −π/2 about x, so local +x → world +x and local +y → world −z (away from the camera).
- **Noise.** Ashima-style 3D simplex (`cnoise`) implemented inline: `mod289`, `permute`, `taylorInvSqrt`, 8-corner gradient mix with quintic fade. One octave per call, two calls total.
- **Height.** `primary = cnoise((0.24x, 0, 0.6t))·0.95`; `secondary = cnoise((0.9x, 0, 0.84t))·0.095`; `ribbon = −0.2·cos(0.32x)`; `sombrero = 0.52·sin((0.3t − 4.6r)·π)` with `r = |uv − 0.5|`. Sum, then:
  `radialAttenuation = mix(0.65, 1, smoothstep(0, 0.28, r))` flattens the centre to 65%;
  `height = mix(h, 0.6h, smoothstep(0.45, 0.82, |h|))` softly compresses peaks so ridges stay thin instead of spiking.
- **Displacement.** `vec3(position.x, position.y, height)` in local space becomes world-y after the mesh's −90° rotation — note the height is written into local **z**, which is the plane's normal.
- **Camera.** `PerspectiveCamera(52°, aspect, 0.1, 80)` at `(0, 3.1, 9.8)`, `lookAt(0, −0.4, 0)`, so the eye is ~3.9 units above the mesh plane and pitched down ~20°. The horizon (where the mesh plane meets the eye ray) lands near 45% frame height.
- **Shading.** `heightGlow = smoothstep(−2.4, 1.9, vHeight)`; `base = mix(#0C001F, #A9A0FF, heightGlow·0.7)` then 6% toward `#294FBA`. Alpha as described in §3. There is no lighting model — the "light" is purely altitude.
- **Screen cost.** Wireframe of 79k quads is ~475k line vertices; additive blending with `depthTest: true` means far lines are correctly hidden behind near ridges, which is what keeps the horizon readable.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.75 | 1–2 | pixel ratio cap | M |
| `uSpeed` | 0.16 | 0.05–0.4 | shader-time multiplier for all motion | H |
| `uElevation` | 0.2 | 0–0.5 | amplitude of the long static ribbon ridge | H |
| `uNoiseRange` | 0.95 | 0.3–1.6 | amplitude of the primary dune noise | H |
| `uSombreroAmplitude` | 0.52 | 0–1.2 | height of the concentric ripple | H |
| `uSombreroFrequency` | 4.6 | 2–9 | ring count across the plane radius | M |
| plane size | 40 × 24 | 20–60 × 14–36 | world extent; larger pushes the horizon further out | H |
| subdivisions | 360 × 220 | 120–500 | wireframe density; the main cost driver | H |
| mesh height | −0.8 | −1.5…0 | plane elevation; raises/lowers the horizon | H |
| `fov` | 52 | 40–65 | widens or narrows the desert | M |
| camera position | (0, 3.1, 9.8) | y 2–5, z 7–14 | view angle; y controls how much grid is visible | H |
| lookAt | (0, −0.4, 0) | y −1…0 | pitch; sets the horizon line height | H |
| fog | 18 → 52 | — | only affects built-in materials (base/halo) | L |
| line colour | `#A9A0FF` | — | crest colour | M |
| glow colour | `#0C001F` | — | trough/base colour | M |
| accent | `#294FBA` | — | 6% tint toward blue | L |
| alpha range | 0.06 → 0.28 | 0.02–0.4 | grid translucency; near edge brightest | H |
| halo | 90 × 54 at y −2.2 | — | central violet lift | L |

## 7. Palette and color

Crest `#A9A0FF` (0.66, 0.63, 1.0) — a pale periwinkle; trough `#0C001F` (0.047, 0, 0.122); accent `#294FBA` (0.16, 0.31, 0.73). The blend is `mix(trough, crest, heightGlow·0.7)` then 6% toward accent, so most of the grid sits between a near-black violet and a desaturated lavender; only the tallest crests approach the pale crest colour. Halo `#160033` inner → `#010008` outer; base slab `#0A0018`; fog `#040014`. Additive wireframe over near-black means line crossings brighten, and near the horizon where hundreds of lines collapse per pixel the field clips toward pale lavender-white — that band is the brightest thing in the frame. No tone map; `outputColorSpace` is sRGB but the custom shader writes display values directly.

## 8. Composition and camera

A landscape with a strong horizontal division: dark sky above ~45% height, wireframe ground below. The camera's 20° downward pitch and 3.9-unit eye height set that line; moving the camera up raises the horizon, moving the look target up lowers it. The plane is 40×24 and the camera at z = 9.8, so the far edge is well beyond the fog and the visible border never enters frame. The grid's brightest band is at the horizon, with a second bright region at the bottom edge where the near lines separate. Aspect: FOV is vertical, so wide frames reveal more desert laterally; portrait frames keep the horizon height but show less width, making the ridges look steeper. The camera's slow lateral orbit (±0.24) produces gentle parallax between the horizon brightness and the foreground grid.

## 9. Randomness and seeds

None. The only stochastic content is procedural simplex noise evaluated from position and time; there is no RNG, no seed, and no warmup. The terrain is a pure function of `(x, t)` — note that it is *one-dimensional in space*: all vertices at a given x share a height, so ridges run perfectly straight toward the horizon regardless of z.

## 10. Performance budget

One wireframe draw call over 158,400 triangles (~475k line vertices), plus two
quads (the base slab and the halo). Vertex work is trivial (two simplex calls); the cost is rasterising hundreds of thousands of 1 px additive lines and the associated overdraw at the horizon. On integrated GPUs this holds 60 fps at DPR 1.75 on a 1920×1080 canvas but is the heaviest scene in the family at the vertex/fill boundary — lower `subdivisions` to 240×150 if it drops. Cut-first: subdivisions → 240×150, then `maxDpr` 1.75→1.5, then plane to 32×20 (fewer quads per unit area at the same subdivision count).

## 11. Host integration

`absolute inset-0 pointer-events-none` holder with `block w-full h-full` canvas; no input. Renderer `alpha: true`, clear `(0,0,0,0)` — **the upper half of the frame is the host backdrop**, so it must be dark (source preview: black → `#1A0033`). Sizing from `clientWidth/clientHeight`, DPR capped at 1.75, `setSize(w, h, false)`. Teardown disposes the three geometries and materials individually, then `renderer.dispose()` + `renderer.forceContextLoss()`. One instance per page (shared FPS meter). No external assets.

## 12. Failure modes and tells

- **Grid is a flat carpet with no ridges** — the noise is being sampled at `position.xz` in *world* space after rotation, or the third coordinate is not time; the original samples local `(x, 0)` and animates via the z input.
- **Ridges run diagonally instead of toward the horizon** — noise sampled with both x and y; in the original the height depends on x only.
- **Horizon line in the wrong place** — camera `lookAt` target or eye height changed; keep y ≈ 3.1 and target y ≈ −0.4.
- **Moiré / shimmering bands in the middle distance** — subdivisions too low relative to line frequency or DPR 1; the wireframe aliases. Raise subdivisions or DPR.
- **Whole plane glows solid violet** — additive wireframe with `depthTest: false`, so far lines draw over near ridges; depth testing must stay on.
- **No sombrero ripple** — `radius` computed from world position rather than uv, or `uSombreroFrequency` too low (<2) so the first ring falls outside the frame.
- **Spiky needles instead of dunes** — the soft-clip `mix(h, 0.6h, smoothstep(0.45, 0.82, |h|))` removed; amplitudes above ~1.5 then spike.
- **Edges of the plane visible** — `rim` mask removed, or the plane smaller than the frustum at the current FOV.

## 13. Tuning knobs

1. camera height and look target — horizon placement and the amount of visible grid; the composition's first lever.
2. `uNoiseRange` — dune height; 0.6–1.2.
3. subdivisions — texture fineness and cost; 240–400.
4. `uSombreroAmplitude`/`uSombreroFrequency` — the ripple's presence; 0.3–0.8 / 3.5–6.
5. `uSpeed` — overall pace; 0.1–0.25.

## 14. Verification checklist

- Horizon line within 40–50% of frame height; sky above it near-black (luma < 6%), grid below.
- Dominant hue 250–270° (violet); brightest band at the horizon, pale lavender.
- Grid resolves into diamonds at the bottom edge and fuses into a line at the horizon — the signature of a wireframe seen at grazing angle.
- Visible concentric ripple around frame centre with a ~41.7 s period.
- No visible plane border on any edge at aspect ≥ 1.0.
- No spiky geometry; ridges rounded.
- Camera-orbit parallax perceptible over ~30 s; no flicker on resize.

## 15. Porting notes

Wireframe mode in three draws triangle edges, so the visual grid is the plane's quads, not a separate line list — a custom line set must reproduce the same diagonal split per quad or the texture looks different. If porting to raw WebGL, use `gl.LINES` with an index buffer of triangle edges, and keep `depthTest` on. The shader's local-`(x,0)` noise sampling is easy to "fix" into 2D noise by mistake; that change makes the dunes isotropic and destroys the ridge-to-horizon structure.
