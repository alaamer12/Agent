---
id: wire-globe
name: Wire Globe
family: webgl-f4
renderer: three
poster: assets/posters/wire-globe.jpg
complexity: XL
source_lines: 792
dpr_max: 1.75
deps: [three]
poster_capture: 640x400
---

# Wire Globe — scene reference

## 1. Identity

A cyan wireframe globe turning slowly in the dark, wrapped in a tilted dashed orbit ring, with comet-like arcs of light tracing great circles over its surface and small warm sparks flaring where those arcs land.

## 2. Perceived look

A clean, technical instrument render: the globe is built from thin, evenly spaced latitude and longitude lines, brighter where they face the viewer and dimming to a deep teal on the far side, which is what makes a flat line mesh read as a sphere. A soft radial halo sits behind the globe, lifting the black to a dark petrol blue near the centre and giving the whole object a slight atmospheric bloom without any post-processing. The outer ring is sparse and dashed, drawn in warm amber where its dashes are lit and fading to dim teal elsewhere, and it is tilted steeply — nearly edge-on in the poster — so it reads as an orbital plane rather than a halo. Arcs are the only fast elements: short, bright streaks that run along great circles for 10–22 s, with a hard head and a long fading tail; at their endpoints warm nodes flare. Everything is additive, so crossings and overlaps brighten toward white-cyan. The 3 s screenshot shows a cyan ball of grid lines at centre, roughly two-thirds of frame height, a faint blue vignette of halo behind it, a dashed ring hugging the frame's top and bottom, and a scattering of tiny white sparks.

## 3. Frame anatomy

Six three.js objects, all `transparent`, `depthWrite: false`, additive; five of them `depthTest: false` (stars keep depth test but write nothing):

1. **Clear** — `(0, 0, 0, 0)`; the canvas is transparent so the host backdrop is the field.
2. **Halo** — a 13×13 plane at z = −2.5, re-oriented to face the camera each frame, `renderOrder = −1` so it draws first; radial falloff `falloff = smoothstep(1, 0.05, 2d)` with alpha `falloff²·0.5·breathe`; inner `#0D5F74`, outer `#03141C`.
3. **Stars** — 240 point sprites on a hollow shell 16–30 units out, offset z −8, twinkling, deep teal `#0A5F80`; `gl_PointSize = clamp(0.7 · dpr · (1 + seed·1.6) · 34 / max(−view.z, 1), 1, 6)`, fragment `disc = smoothstep(0.5, 0.05, d)`, colour `deep · (0.4 + twinkle)`, alpha `disc · twinkle · 0.5` (depth test on, depth write off).
4. **Graticule** — 9 parallels (−75°…+75° every 18.75°) × 72 segments + 18 meridians × 48 segments, 1512 line segments; opacity 0.5 × `(0.1 + 0.9·facing)`.
5. **Arcs** — 24 great-circle polylines, 56 segments each (2688 vertices), shader-lit comets.
6. **Nodes** — 48 point sprites (two per arc endpoint), flashed at launch and landing.
7. **Ring** — a 128-segment circle of radius 3.15 built in the XZ plane (`y = 0`) with 30 shader dashes, in scene space (not the globe group); `rotation.x = 1.16 rad` tilts that plane, and because the circle starts horizontal its screen ellipse is nearly circular — vertical semi-axis `3.15 · sin 1.16 ≈ 2.89`, 92% of the horizontal one.

The globe group (graticule + arcs + nodes) turns as one; the ring, halo and stars are independent. Order within the additive stack is irrelevant visually.

## 4. Motion law

- **Globe.** `rotY(0.1t)` — one turn in **62.8 s**; `rotX(−0.34 + 0.07·sin(0.06t))` — a slow ±4° nod with period **104.7 s**.
- **Arcs.** `head = fract(0.045…0.095·t + φ)`; each arc carries a comet head from t = 0 to 1 along its own great circle, with period 10.5–22 s. The trail behind is `exp(−d·15)` in arc-parameter units (≈95% gone after 0.2 of the arc); ahead of the head a faint `exp(2.5·d·15)·0.08` stub hints at where it goes. Because `φ` is per-arc, the 24 heads are spread out in time.
- **Nodes.** Each endpoint flares on `max(exp(−cycle·9), exp(−(1−cycle)·12))` — a sharp rise at launch, a slightly longer settle at landing; both ends of an arc share its phase so the arrival coincides with the next departure.
- **Ring.** Rotates `z = 0.035t` (one turn in **179.5 s**), `x = 1.16 + 0.12·sin(0.05t)` (period 125.7 s). Dashes crawl: `fract(param·30 − 0.21t)`, so the pattern slides 0.007 of the ring per second — one lap in ≈ 143 s.
- **Graticule shimmer.** `0.55 + 0.45·sin(7·y_dir − 0.35t)` — a band of brightness sweeping pole to pole with period **18.0 s**.
- **Camera.** `x = 0.5·sin(0.05t)` (125.7 s), `y = 0.25 + 0.35·sin(0.07t)` (89.8 s), `lookAt(0,0,0)` — a slow orbital sway that parallaxes the ring against the globe.
- **Halo.** `breathe = 0.82 + 0.18·sin(0.27t)` — period 23.3 s, ±18%.
- **Stars.** `0.35 + 0.65·wave²`, `wave = 0.5 + 0.5·sin((0.3 + seed)t + 30·seed)` — each star twinkles at 0.3–1.3 rad/s.
- **Phase at t = 0.** Arc phases and star seeds fixed by the seed; globe at `rotX(−0.34)`; open-ended.

## 5. Technique and math

three.js scene with hand-written `ShaderMaterial`s for every object; no textures, no post-processing.

- **Camera.** `PerspectiveCamera(44°, aspect, 0.1, 90)` at `(0, 0.25, 8.2)`. On resize, FOV switches to **58°** when `aspect < 1.1` so a portrait frame still fits the globe. At the sphere radius 2.35 the half-height at the globe plane is `tan(22°)·8.2 = 3.31`, so the globe subtends **71% of frame height**; the ring radius 3.15 subtends 95% and grazes the top/bottom edges.
- **Graticule.** Parallels: latitude `−75° + i·18.75°` (9 rings, no equator line — the ±3.75° gap around the equator is where an equator would be if `parallels` were even). Meridians: 18 half-circles at 20° longitude spacing, 48 segments each.
- **Facing.** Every line shader computes `objectDir = normalize(position)`, `normal = normalize(mat3(modelMatrix)·objectDir)`, `vFacing = smoothstep(−0.5, 0.55, dot(normal, normalize(cameraPosition − world)))`. Front-hemisphere lines get 1, the limb ~0.5, the back hemisphere 0. This is the entire depth cue — there is no depth buffer.
- **Graticule shade.** `colour = mix(gridDim #0D4A63, grid #3AD7F2, vFacing·vShimmer)`, `alpha = 0.5·(0.1 + 0.9·vFacing)`.
- **Arc geometry.** For each arc: a random unit `origin`, a random unit `axis`, `span ∈ [0.8, 2.3]` rad; `target = origin` rotated about `axis` by `span`. `normal = normalize(origin × target)`, `tangent = normalize(normal × origin)`. Points: `p(t) = origin·cos(t·span) + tangent·sin(t·span)`, scaled by `lift = 2.35 + (0.1 + 0.16·span)·sin(πt)` — so the arc bows up to ~0.47 units off the shell at its midpoint and is welded to the sphere at both ends.
- **Arc lighting.** `head = fract(t·speed + φ)`, `d = head − param`; `lit = d ≥ 0 ? exp(−15d) : exp(37.5d)·0.08`. `vLand = smoothstep(0.06, 0, param) + smoothstep(0.94, 1, param)` marks the terminal 6% at each end. Fragment: `colour = mix(cold, warm, 0.9·land) + cold·glow·1.2 + (0.55, 0.9, 1.0)·glow²·1.5`; `alpha = (0.055 + 0.95·glow)·(0.18 + 0.82·facing)`.
- **Nodes.** `cycle = fract(t·speed + φ)`; `flash = max(exp(−9·cycle), exp(−12·(1−cycle)))`; `gl_PointSize = clamp(dpr·(26 + 46·flash)/max(−view.z, 1), 1, 24)`. Fragment: soft disc `smoothstep(0.5, 0.06, d)`, bloom `exp(−9d²)`, `colour = mix(warm, cold, 0.18)·(0.8 + 1.4·flash) + 0.35·bloom·flash`.
- **Ring.** `walk = fract(param·30 − 0.21t)`; `vDash = smoothstep(0.62, 0.4, walk)·smoothstep(0, 0.14, walk)` — a dash occupying roughly the middle 40% of each 1/30 slot with soft edges. `colour = mix(cold·0.5, warm, dash)`, `alpha = (0.05 + 0.55·dash)·(0.35 + 0.65·facing)`.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `seed` | 4242 | any u32 | arc great circles, speeds, star field | M |
| `maxDpr` | 1.75 | 1–2 | pixel ratio cap (stars bump sizes by DPR explicitly) | M |
| `radius` | 2.35 | 1.6–3.2 | globe radius; sets frame coverage at fixed camera | H |
| `parallels` | 9 | 5–15 | latitude rings | M |
| `parallelSteps` | 72 | 36–120 | segments per parallel | M |
| `meridians` | 18 | 8–36 | longitude half-circles | M |
| `meridianSteps` | 48 | 24–72 | segments per meridian | M |
| `arcs` | 24 | 8–60 | number of comets | H |
| `arcSteps` | 56 | 24–96 | polyline resolution per arc | M |
| `arcTail` | 15.0 | 6–25 | exponential decay of the trail per unit param | H |
| `arcBase` | 0.055 | 0.02–0.15 | unlit arc alpha floor | M |
| `ringSegments` | 128 | 64–256 | ring smoothness | L |
| `ringRadius` | 3.15 | 2.4–4.5 | orbit ring size relative to globe | H |
| `ringDashes` | 30 | 12–60 | dash count around the ring | M |
| `ringDashSpeed` | 0.07 | 0.02–0.2 | crawl rate; the walk advances `0.1 · dashSpeed · dashes` per second | L |
| `stars` | 240 | 80–600 | star count | L |
| `spin` | 0.1 | 0.02–0.3 | globe yaw rate (rad/s) | M |
| `tilt` | −0.34 | −0.6…0.2 | resting globe pitch (rad) | M |
| `cameraZ` | 8.2 | 6–12 | camera distance; sets coverage and parallax | H |
| `fov` | 44 (58 portrait) | 35–60 | vertical FOV; portrait switch at aspect < 1.1 | H |

## 7. Palette and color

Globe grid: `#3AD7F2` bright cyan mixed from `#0D4A63` deep teal by facing × shimmer. Shared cold `#37E0FF`, deep `#0A5F80`, warm `#FFB056`. Arcs are cold with a warm blush only at the last 6% (`vLand`), plus a near-white `(0.55, 0.9, 1.0)` boost where the comet head is brightest. Nodes are `mix(warm, cold, 0.18)` — amber with a cyan bias — flaring toward white at launch. Ring base `cold·0.5` (dim teal) with dashes warm amber. Halo inner `#0D5F74`, outer `#03141C`. The whole palette is additive over a transparent canvas, so the host backdrop dominates the darks: on the source preview the corners read near-black with a faint violet gradient from `#1A0033`. No tone map; `outputColorSpace` is set to sRGB, but because every material is a hand-written shader it receives raw display-space values from the `rgb()` helper — the palette must not be run through three's `Color` conversion twice.

## 8. Composition and camera

Centred globe with the camera 0.25 units above the equator plane, so the frame is very slightly high. Globe ≈ 71% of frame height; ring ≈ 95% and effectively sets the frame's vertical extent — keep at least 2–3% margin or the ring will clip. The ring is a circle in the XZ plane tilted 1.16 rad (66°) about x, so on screen it is a near-circular ellipse 92% as tall as it is wide — not a shallow one. Its far side crosses the top of the frame and its near side the bottom, and its vertical extent is ~95% of frame height. Aspect: landscape uses 44° FOV; below 1.1 aspect the FOV widens to 58°, shrinking the globe so it still fits a portrait frame. Stars sit 16–30 units out, so their parallax with the camera sway is subtle. The halo plane (13×13) is large enough to cover the frame behind the globe.

## 9. Randomness and seeds

Two LCG streams (`state = (state·1664525 + 1013904223) mod 2³²`), **not** mulberry32. Globe/arc stream seeded **4242**: per arc one origin direction, one axis direction, one span (uniform 0.8–2.3), one phase, one speed (0.045–0.095), consumed in that order for all 24 arcs. Star stream seeded **4319** (4242 + 77): each star one direction, one radius (16–30), one seed. Directions use the reject-free "random in cube then normalize" method, which slightly over-weights the cube's corners; this is the original's distribution and is fine for 24 arcs and 240 stars. No warmup.

## 10. Performance budget

6 draw calls, 5,712 line vertices (3,024 graticule + 2,688 arc) + 288 points + 1 large plane. Fill cost is dominated by the halo plane (full-frame additive quad) and the ring's 128 segments at 1 px, not by geometry. At DPR 1.75 this is trivially 60 fps. Cut-first: `meridians` 18→12, `parallels` 9→7, `stars` 240→120, `maxDpr` 1.75→1.5. The halo could be a CSS radial gradient instead of a mesh with no visible difference.

## 11. Host integration

`absolute inset-0 pointer-events-none` holder with a `block w-full h-full` canvas; no input. The renderer is created with `alpha: true` and clears to `(0,0,0,0)` — **the host backdrop is part of the look** (source preview: black→`#1A0033`). Sizing: renderer `setPixelRatio(min(dpr, 1.75))` + `setSize(w, h, false)`; the canvas is CSS-sized by the holder. Resize re-derives FOV from aspect. Both point materials take `uDpr` explicitly because their `gl_PointSize` formulas include the pixel ratio. Teardown traverses the scene, disposes geometry and materials, then `renderer.dispose()` + `renderer.forceContextLoss()`. One instance per page (shared FPS meter). No external assets — no HDR, no textures.

## 12. Failure modes and tells

- **Globe looks like a flat disc of lines** — the facing term is missing or its dot product is inverted; the far hemisphere must fade to alpha ≈ 0.05 (grid) and the limb to ≈0.5.
- **Ring is a solid circle** — the dash function lost one of its two `smoothstep`s; both are needed to carve a soft-edged dash with gaps.
- **Ring is a shallow ellipse or lies on the wrong axis** — the circle must be authored in the XZ plane (`y = 0`) and then tilted by `rotation.x = 1.16`; authoring it in XY and tilting gives a different screen ellipse.
- **Halo is a square, or far too small** — the 13×13 plane at z = −2.5 projects to 1.5× the frame half-height, so its falloff never reaches zero inside the frame; do not rescale the falloff to the viewport.
- **Arcs read as loops rather than streaks** — `lit` must be strictly one-sided (`d ≥ 0` for the tail), and the forward stub must be capped at 0.08; symmetric decay makes every arc glow end to end.
- **Arc heads all move together** — per-arc `phase` not uploaded or shared; 24 arcs should be evenly spread through their cycles.
- **Halo is a visible square** — the plane is not being re-oriented to the camera, or it is smaller than the frame; 13×13 at z −2.5 covers a 44° frustum.
- **Stars strobe** — `wave²` term dropped, leaving a raw sine; the squared wave keeps most stars dim most of the time.
- **Colours look washed out on a modern three.js** — the palette went through `THREE.Color` with colour management on and was converted twice; hand-written shaders bypass the output pass in this project.
- **Globe clips the top/bottom in portrait** — the FOV switch at aspect < 1.1 is missing.
- **Nothing visible** — canvas not transparent over a dark host; or `depthTest: false` was flipped to true and the halo's `renderOrder = −1` plane now occludes the grid.

## 13. Tuning knobs

1. `radius` vs `cameraZ` — globe size; keep at 0.7 of frame height.
2. `arcs` and `arcTail` — traffic density and streak length; 15–60 arcs, tail 10–20.
3. `ringRadius` — how far the orbit ring sits from the globe; 2.8–3.6.
4. `spin` — globe turn rate; 0.05–0.15.
5. `graticule opacity` (0.5) — how much the grid dominates the arcs; 0.35–0.65.

## 14. Verification checklist

- Globe is a circle (not an ellipse) at frame centre; diameter 0.68–0.74 of frame height.
- Front hemisphere grid clearly brighter than back; a visible limb.
- Dominant hue 185–195° (cyan); warm amber only on ring dashes, arc landings and node flares.
- Ring dashed, not solid: ~30 dashes with visible gaps; ring's vertical extent within 2–3% of frame edges.
- At least 5 arc heads visible at any moment, each with a one-sided tail.
- Halo present as a soft radial lift behind the globe; no square edge.
- Transparent canvas: backdrop visible in the corners.
- No clipping of the ring; no flicker on resize through the FOV switch at aspect 1.1.

## 15. Porting notes

This is the only f4 scene in three.js; the `facing` depth cue replaces the depth buffer and must be reproduced (or `depthTest` enabled with a normal buffer, which changes the look). Do not convert the `rgb()` helper to `new THREE.Color(hex)` with colour management enabled — hand-written shaders here expect raw display-space values. `LineSegments` line width is 1 px regardless of platform. The star field's z offset of −8 ensures stars sit behind the globe's far side even without depth testing.
