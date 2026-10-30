---
id: pulse-orb
name: Pulse Orb
family: webgl-f5
renderer: three
poster: assets/posters/pulse-orb.jpg
complexity: XL
source_lines: 729
dpr_max: 1.75
deps: [three]
poster_capture: 640x400
---

# Pulse Orb — scene reference

## 1. Identity

A lumpy, breathing orb of violet membrane veined with cyan ridges, glowing inside a faint glass shell, on a deep purple field with a few orbiting sparks.

## 2. Perceived look

An organic, slightly ominous body: the surface is not a sphere but a slow, thick liquid that bulges and sags with large soft lumps, and the silhouette is visibly uneven — sometimes nearly round, sometimes visibly knuckled. Its colour is a purple-to-lilac gradient driven by displacement (high bulges lighter, hollows deeper violet), overlaid by a key light from the upper right and a cool bounce from the lower left. The edges are the brightest thing: a saturated cyan fresnel rim wraps the whole body, and a second cyan line system appears as thin ridges wherever the displacement field crosses a level — so the surface looks like a stretched film with stress lines, which is the strongest visual signature. Around the body sits a very faint, much larger glass sphere showing only at the limb, and beyond that a soft purple aura. Small teal motes orbit the outside. The 3 s screenshot shows a purple blob about
85% of frame height with a bright cyan outline, several cyan veins across its
face, and a faint circular shell almost touching the frame on near-black violet.

## 3. Frame anatomy

Back to front:

1. **Clear** `(0,0,0,0)` — transparent canvas; host backdrop (black → `#1A0033`) shows at the edges.
2. **Aura** — 15×15 plane at the origin, `depthTest: false`, `renderOrder = −1`; radial `smoothstep(1,0,2d)` colour `#3D0F66 → #0B0220`, additive, alpha `falloff²·0.45·breathe`.
3. **Inner core** — icosahedron radius 1.152, detail 5, additive, renderOrder 1; facing-weighted `mix(#5A17A8, #E9C8FF, centre²)`, alpha `centre·0.55`, with its own 0.83 rad/s beat.
4. **Membrane** — icosahedron radius 1.92, detail 14 (13,500 vertices, non-indexed), displaced by two snoise octaves; `FrontSide`, transparent, **`depthWrite: true`**, renderOrder 2.
5. **Atmosphere** — icosahedron radius 2.7264 (1.92 × 1.42), detail 8, `BackSide`, additive, renderOrder 3; limb-only glow `#3A1170 → #5FE8FF` with alpha `limb·0.62·breathe`.
6. **Motes** — 120 additive point sprites orbiting at radius 1.7–4.0, renderOrder 4, max 9 px, tint `#69F0E2`.

The orb group is canted `rotation.z = 0.36` so the mote band reads as an ellipse rather than a horizontal line.

## 4. Motion law

- **Breath.** `amp = 0.42·(0.74 + 0.26·sin(0.42t))` — amplitude swings 0.20 → 0.42 with period **15.0 s**; a second, slower `sin(0.63t)·0.1` swell adds ±0.1 to the radius with period 10.0 s. Together they give the body a double-rate heave, one inside the other.
- **Base octaves.** `snoise(dir·1.35 + (0, 0.17t, 0.0765t))` — the lumps drift up and back at ~0.17 units/s of noise space, so the surface appears to churn rather than translate; one noise cell takes about 5.9 s.
- **Ridge octave.** `snoise(dir·3.1 − (0.2125t, 0, 0.068t))` at weight 0.32 — a finer, faster counter-drift that provides the veins.
- **Orb turn.** `rotation.y = 0.075t` (83.8 s), `rotation.x = 0.22·sin(0.045t)` (139.6 s), plus the fixed 0.36 z cant.
- **Atmosphere.** `0.85 + 0.15·sin(0.42t)` — 15.0 s, in step with the breath.
- **Core beat.** `0.72 + 0.28·sin(0.83t)` — 7.6 s, its own faster pulse.
- **Motes.** `angle = a + 0.12t·(0.6 + 0.9·spread)` — 34–87 s per orbit; vertical bob `0.45·sin(0.5t + 3a)`; band rotated 1.2 rad about x, oscillating ±0.1 at 125.7 s.
- **Camera.** `x = 0.42·sin(0.055t)` (114.2 s), `y = 0.3·sin(0.08t)` (78.5 s), `z = 7.3 + 0.4·sin(0.11t)` (57.1 s) — a slow dolly that keeps the rim moving relative to the body.
- **Aura.** `0.8 + 0.2·sin(0.31t)` — 20.3 s.
- **Phase at t = 0.** All time sines are zero, so the breath starts at 0.74 of
  its range (near the low end) and the noise fields sit at their t = 0 offset;
  deterministic. Open-ended.

## 5. Technique and math

three.js; five hand-written shader materials, one geometry type (icosahedra) at three scales.

- **Displacement.** For each vertex direction `dir`: `base = snoise(dir·1.35 + (0, 0.17t, 0.0765t))`; `ridge = snoise(dir·3.1 − (0.2125t, 0, 0.068t))`; `height = (base + ridge·0.32)·amp + 0.1·sin(0.63t)`; `displaced = dir·(1.92 + height)`. Two noise taps per vertex (four including the normal probes), Ashima 3D simplex.
- **Normal recovery.** Probe `base` alone at `normalize(dir ± tangent·0.06)` along two tangents built from `dir` and a helper axis; `gradient = (tA·slopeA + tB·slopeB)/0.06`; `objectNormal = normalize(dir − gradient·amp/1.92)`. Cheap, and it is the low-frequency lumps that tilt the rim.
- **Body shading.** `facing = dot(n, view)`; `fresnel = (1 − facing)^2.6`; `body = mix(#22063F, #7D2BC4, clamp(vDisp·0.55 + 0.5))`; key `(0.45,0.72,0.66)` × 0.8, bounce `(−0.6,−0.35,0.2)` × 0.2, base 0.2.
- **Ridges.** `ridge = smoothstep(0.1, 0, |clamp(vDisp,−1,1) − 0.12|)` — a narrow band at a normalized displacement level of 0.12, so it draws contour lines on the bulges, then multiplied by `(0.3 + 0.5·fresnel)` so they only survive near the edge. `vDisp = height/amp`, i.e. normalized to ±~1.
- **Rim.** `+ #4CF5DF · fresnel · 1.5`, plus `#C46BFF · facing⁴ · 0.22` for a soft interior glow. Alpha `mix(0.82, 1.0, fresnel)` — the membrane is nearly opaque but lets the core show at the centre.
- **Atmosphere.** `limb = (1 − |dot(n, view)|)^3.4`; colour `mix(#3A1170, #5FE8FF, limb)`; alpha `limb·0.62·breathe`. `BackSide` so the shell is visible only where the membrane does not cover it.
- **Core.** `centre = facing^1.6`; `mix(#5A17A8, #E9C8FF, centre²)·beat`, alpha `centre·0.55`, additive.
- **Motes.** Orbit rebuilt per frame from an `(angle, radius, spread)` triple; `y = 0.45·sin(0.5t + 3a) + 0.5·sin(5a)`; size `dpr·(10 + 16s)/max(−view.z, 1)`, clamp 1–9.
- **Camera.** `PerspectiveCamera(42°, aspect, 0.1, 60)` at z 7.3; the membrane's max radius ≈2.44 means it spans ≈87% of frame height at rest; the shell (2.73) spans ≈97%.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.75 | 1–2 | pixel ratio cap | M |
| `radius` | 1.92 | 1.4–2.4 | base orb radius; overall size | H |
| `detail` | 14 | 10–20 | icosahedron subdivision (20·(d+1)² faces) | H |
| `shellDetail` / `coreDetail` | 8 / 5 | 4–12 / 3–8 | atmosphere and core subdivision | L |
| `shellScale` / `coreScale` | 1.42 / 0.6 | 1.25–1.6 / 0.4–0.8 | shell and core radii relative to the body | M |
| `frequency` | 1.35 | 0.8–2.2 | spatial scale of the big lumps | H |
| `amplitude` | 0.42 | 0.2–0.7 | displacement height | H |
| `detailWeight` | 0.32 | 0.1–0.6 | weight of the ridge octave | H |
| `detailFrequency` | 3.1 | 1.8–5 | spatial scale of the veins | H |
| `speed` | 0.17 | 0.06–0.35 | noise drift rate | H |
| `pulseSpeed` | 0.42 | 0.2–0.8 | breath rate (period 15.0 s) | M |
| `swell` | 0.1 | 0–0.25 | whole-body radial swell amplitude | M |
| `rimPower` / `rimGain` | 2.6 / 1.5 | 1.5–4 / 0.8–2.2 | edge falloff and brightness | H |
| `ridgeLevel` / `ridgeWidth` | 0.12 / 0.1 | −0.4…0.5 / 0.03–0.2 | contour height and thickness | H |
| `motes` / `moteRadius` | 120 / 3.1 | 0–300 / 2.4–4 | sparks around the orb | L |
| `cameraZ` | 7.3 | 6–10 | distance; orb size in frame | H |
| `fov` | 42 (56 portrait) | 34–50 | framing; portrait switch at aspect < 1.1 | H |
| body deep / lit | `#22063F` / `#7D2BC4` | — | shadow and bulge colour | H |
| rim / core | `#4CF5DF` / `#C46BFF` | — | cyan edge and violet interior glow | H |

## 7. Palette and color

Body shadow `#22063F` (deep violet), bulge `#7D2BC4` (lit purple); rim cyan `#4CF5DF`; interior glow `#C46BFF` (orchid); atmosphere deep `#3A1170` → glow `#5FE8FF`; core cold `#5A17A8` → hot `#E9C8FF`; motes `#69F0E2`; aura `#3D0F66` → `#0B0220`. The composite reads as a purple body with a cyan outline — the two hues are complementary enough to separate the silhouette without any black stroke. Ridges pick up the rim cyan, so the veins and the edge belong to the same light. The additive atmosphere and aura lift the background to a desaturated purple around the orb while the corners stay near-black; there is no tone map, so the rim clips toward white-cyan at its brightest. `outputColorSpace` is sRGB but the shaders write display-space values directly.

## 8. Composition and camera

A single centred object with no horizon. The membrane spans ≈87% of frame height at rest and the glass shell ≈97%, so the shell is what nearly touches the frame — keep it under 1.0 of the half-height or it clips. The 0.36 rad z-cant tilts the mote band and gives the otherwise symmetric orb a slight lean. Camera motion (±0.42 x, ±0.3 y, ±0.4 z) shifts the orb by a few percent and changes the fresnel rim subtly, which is the point: the rim is the scene's main animation and it needs the relative angle to change. Portrait frames widen the FOV to 56° at aspect < 1.1 to keep the shell off the edges.

## 9. Randomness and seeds

Only the motes use randomness: LCG (`state = (state·1664525 + 1013904223) mod 2³²`) seeded **31337**, drawing per mote an angle, a radius factor `0.55 + 0.75r`, and a spread; positions are placeholders rebuilt in the shader. The orb itself has no seed — its shape is a pure function of vertex direction and time, identical on every machine. No warmup.

## 10. Performance budget

Five draw calls: membrane 13,500 vertices / 4,500 triangles with 4 noise taps and a fragment rim; shell 1,620 faces; core 720; 120 points; 1 quad. The membrane dominates — at detail 14 the vertex shader is the most expensive in the family, but the geometry is still small by GPU standards. 60 fps at DPR 1.75 on integrated GPUs. Cut-first: `detail` 14→11 (silhouette goes lumpy), then `maxDpr` 1.75→1.5, then drop the second normal probe (rim flattens), then `motes` 120→60.

## 11. Host integration

`absolute inset-0 pointer-events-none` holder, `block w-full h-full` canvas, no input. Renderer `alpha: true`, clear `(0,0,0,0)`; host backdrop must be dark. Sizing from holder offsets, DPR capped at 1.75, mote `uDpr` refreshed on resize. Teardown disposes every geometry and material via scene traversal, then `renderer.dispose()` + `forceContextLoss()`. One instance per page (shared FPS meter). No external assets.

## 12. Failure modes and tells

- **Orb facet does not read as liquid** — `frequency` too high or `detail` too low; big lumps need ≥1.2 noise cells around the sphere and ≥12 subdivisions.
- **Silhouette goes lumpy/jagged** — `detail` below ~11; the low-frequency normal recovery cannot hide a coarse mesh.
- **Ridges appear everywhere** — the `(0.3 + 0.5·fresnel)` gate dropped, or `ridgeWidth` raised past 0.2; ridges are edge-only contour lines.
- **Whole orb turns cyan** — `rimGain` too high or `rimPower` too low; the cyan must stay on the rim and the veins.
- **Glow fills the orb** — atmosphere switched to `FrontSide` or `depthTest` off; it must be a back-side, depth-tested shell.
- **Inner core invisible** — membrane alpha forced to 1.0, or core `depthWrite` on and `renderOrder` above the membrane.
- **Orb breathes like a balloon, not a body** — `pulseSpeed` raised; the breath is slow (15 s) and the churn is what sells it.
- **Shell clips the frame** — `shellScale` > 1.45 or portrait FOV switch missing.
- **Motes drawn as a straight line** — the orb z-cant removed and the mote band rotation dropped.

## 13. Tuning knobs

1. `amplitude`/`frequency` — how lumpy the body is; 0.35/1.2 for a subtle orb, 0.55/1.6 for a stroppy one.
2. `detailWeight`/`detailFrequency` — vein density; 0.25/2.6 subdued.
3. `rimPower`/`rimGain` — edge thickness and brightness; 2.2/1.8 for a neon outline.
4. `ridgeLevel` — where the contour lines sit; −0.1…0.3.
5. `shellScale` — how much glass surrounds the body; 1.3–1.45.

## 14. Verification checklist

- Orb centred within ±3%; membrane 0.8–0.9 of frame height, shell ≤1.0 and fully inside frame.
- Two-hue composition: violet body, cyan rim/veins; no green or orange.
- Uneven silhouette — at least one visible bulge/dimple at any moment.
- Breath period ≈15 s; ridge pattern visibly moves over 5 s.
- Rim continuous around the limb, brighter than the body interior.
- Glass shell visible as a faint large circle at the limb, not as a solid disc.
- Ridges only near the edge; no full-face contour map.
- No clipping, no flicker on resize, backdrop visible in the corners.

## 15. Porting notes

`IcosahedronGeometry` is non-indexed: every face has its own three vertices, which is what makes per-vertex displacement crack-free under flat shading only if normals are recomputed per-vertex — here the recovered normal is smooth (function of `dir`), so the surface reads soft. If you rebuild on an indexed sphere, keep the same noise sampling in `dir` space, not in object space, or the lumps shear with the orb's rotation. The atmosphere shell must be larger than the maximum displaced radius (`radius + amplitude + swell` ≈ 2.44; the shell is 2.73) or bulges will poke through it.
