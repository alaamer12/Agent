---
id: chromatic-knot
name: Chromatic Knot
family: webgl-f5
renderer: three
poster: assets/posters/chromatic-knot.jpg
complexity: XL
source_lines: 546
dpr_max: 1.75
deps: [three]
poster_capture: 640x400
---

# Chromatic Knot — scene reference

## 1. Identity

A fat, glossy torus knot of iridescent chrome — green, cyan, violet and orange sliding over its surface like an oil slick — tumbling slowly in front of a dark violet bloom.

## 2. Perceived look

A product-render aesthetic: one large, smooth, sealed object at frame centre with hard, tight specular highlights and a mirror-like fresnel rim, so the tube reads as wet metal rather than painted plastic. Colour is not a fixed palette but a continuous hue circulation along the tube and around its circumference — the same patch shifts from lime to cyan to deep blue to magenta over tens of seconds, exactly the banding order of thin-film interference. Where the surface turns edge-on the hue compresses and brightens into a saturated rim (blue-white on the left, violet on the right) that separates the knot from the background. Around the silhouette there is a narrow, slightly larger echo of the same iridescence — a fake bloom created by drawing a back-face shell inflated 12 cm — so the object appears to glow into the dark. A large soft violet disc sits behind it, and a few faint coloured motes drift in the depth around the knot. The 3 s screenshot shows a knot filling roughly 80% of frame height, bright white specular caps on the upper-left lobes, green-to-purple gradient across the body and a thin rainbow fringe at the silhouette.

## 3. Frame anatomy

Back to front:

1. **Clear** `(0,0,0,0)` — transparent canvas; the host backdrop forms the outermost field.
2. **Backlight** — 17×17 plane at z = −4.5, `depthTest: false`, `renderOrder = −1`; radial `smoothstep(1.05, 0, 2d)` colour `#2B1046 → #050109`, additive, alpha `falloff²·0.6·breathe`.
3. **Motes** — 80 point sprites on a shell 2.07–5.29 units out, z offset −1.2, additive, renderOrder 3, max 7 px, coloured from the same cosine palette.
4. **Knot** — `TorusKnotGeometry(1.5, 0.42, 168, 24, 2, 3)` drawn `FrontSide`, opaque (`alpha 1.0` in the shader), with fresnel, two Blinn lobes and the cosine palette.
5. **Aura** — the *same geometry buffer*, drawn `BackSide`, vertices inflated 0.12 along their normals, additive, alpha `limb·0.5`, renderOrder 2; it forms a silhouette-wide glow band.

Camera: 40° FOV (54° if aspect < 1.1) at z 7.4. No depth write on aura/motes/backlight; the knot uses default `depthWrite: true` and depth test, so the aura's back faces are hidden wherever the body covers them — that is what confines the glow to the limb.

## 4. Motion law

- **Tumble.** `rig.rotation.x = 0.13t` (period 48.3 s), `y = 0.19t` (33.1 s), `z = 0.55·sin(0.07t)` (89.8 s, ±31.5°). Three unrelated rates mean the pose never repeats.
- **Slick flow.** `film = fresnel·1.35 + uv.x·0.6 + uv.y·0.16 + 0.025t` — the palette phase drifts at 0.025 cycles/s ⇒ **40 s** per full hue cycle at a fixed surface point; `uv.x` (around the knot path, 0–1) contributes 0.6 of a cycle and `uv.y` (around the tube) 0.16, so colours spiral along the body.
- **Aura.** Same flow with a fixed +0.12 phase offset and `limb` instead of `fresnel`; the glow's hue therefore leads the body's by about 5 s.
- **Mote drift.** Each mote wobbles on three sines of ±0.5 units with frequencies 0.06–0.2 (x), 0.05–0.17 (y), 0.035–0.119 (z) rad/s — periods 31–180 s — plus a slow group yaw of −0.02 rad/s (314 s).
- **Twinkle.** `0.3 + 0.7·(0.5 + 0.5·sin(1.3t + 24·seed))²` — period 4.83 s, sharp peaks.
- **Camera.** `x = 0.5·sin(0.06t)` (104.7 s), `y = 0.38·sin(0.085t)` (73.9 s), `lookAt` origin.
- **Backlight.** `0.86 + 0.14·sin(0.23t)` — period 27.3 s.
- **Phase at t = 0.** Knot at identity rotation, palette at `uv`-driven phase, motes at their seeded starting positions. Open-ended.

## 5. Technique and math

three.js with four hand-written `ShaderMaterial`s and one shared cosine palette.

- **Geometry.** `TorusKnotGeometry(radius 1.5, tube 0.42, tubularSegments 168, radialSegments 24, p = 2, q = 3)`: (168+1)·(24+1) = 4,225 vertices, ~8,064 triangles. `uv.x` runs along the knot path, `uv.y` around the tube.
- **Palette.** `slick(t) = A + B·cos(2π(C·t + D))` with A `#7A7580`, B `#756E78`, C `#FFFFFF`, D `#0047A8`. A grey centre with just-under-half amplitude keeps every hue mid-tone — never crushed to black, never blown to white; the D phase (0, 0.278, 0.659) offsets red ahead of green ahead of blue, which is the oil-slick band order rather than a clean rainbow.
- **Knot shading.** `facing = dot(n, view)`, `fresnel = (1 − facing)³`; `film = fresnel·1.35 + uv.x·0.6 + uv.y·0.16 + 0.025t`; colour = `slick(film)`. Diffuse: `max(dot(n, lightA), 0)·0.9 + max(dot(n, lightB), 0)·0.32` with `lightA (0.6, 0.9, 0.8)`, `lightB (−0.85, −0.2, 0.4)`. Two Blinn lobes: `specA = max(dot(n, halfA), 0)^96` (warm `#FFF6E6` ×1.7); `specB = max(dot(n, halfB), 0)^33.6 × 0.5` (cold `#8EC8FF` ×0.75). Final: `colour·(0.1 + diffuse) + colour·fresnel·1.2 + warm·specA·1.7 + cold·specB·0.75` (the 0.5 is already inside `specB`).
- **Aura.** Vertex position `p + n·0.12` (inflate along the true normal so the band keeps constant thickness); `limb = (1 − |dot(n, view)|)^2.2`; `film = limb·1.35 + uv·(0.6, 0.16) + 0.025t + 0.12`; output `slick(film)` with alpha `limb·0.5`.
- **Motes.** Position on a normalised random direction × `4.6·(0.45 + 0.7r)`, z −1.2; per-vertex drift triple `(0.06–0.2, 0.05–0.17, r)`; wobble `0.5·(sin(t·dx + 9s), cos(t·dy + 5s), sin(t·0.7dy + 3s))`; point size `1.1·dpr·(6 + 12s)/max(−view.z, 1)`, clamp 1–7; fragment `smoothstep(0.5, 0.05, d)` disc, colour `slick(2s + 0.04t)`.
- **Camera.** `PerspectiveCamera(40, aspect, 0.1, 60)`; the knot's outer extent ≈1.9 units, so at z 7.4 (half-height 2.69) it fills ≈71% of frame height at rest, more when tilted toward the viewer.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.75 | 1–2 | pixel ratio cap; specular is sensitive to it | M |
| `radius` | 1.5 | 1.0–2.2 | knot path radius; overall size | H |
| `tube` | 0.42 | 0.25–0.6 | tube thickness; slim vs fat knot | H |
| `tubularSegments` | 168 | 96–256 | smoothness along the path | M |
| `radialSegments` | 24 | 12–48 | smoothness around the tube | M |
| `windings` (p) | 2 | 1–5 | knot topology | H |
| `loop` (q) | 3 | 1–5 | knot topology; p,q coprime gives a knot, else a link | H |
| `film` | 1.35 | 0.6–2.5 | how strongly edge-on surfaces shift hue | H |
| `specular` | 96.0 | 24–200 | tightness of the warm highlight | H |
| `auraInflate` | 0.12 | 0.05–0.25 | glow shell thickness | M |
| `auraGain` | 0.5 | 0.2–1.0 | glow intensity | M |
| `motes` | 80 | 0–300 | dust count | L |
| `moteShell` | 4.6 | 3–8 | dust shell radius | L |
| `cameraZ` | 7.4 | 5.5–10 | camera distance; object size | H |
| `fov` | 40 (54 portrait) | 32–55 | framing; portrait switch at aspect < 1.1 | H |
| palette A / B | `#7A7580` / `#756E78` | — | grey centre and hue amplitude | H |
| palette C / D | `#FFFFFF` / `#0047A8` | — | per-channel frequency and phase offsets | H |
| rig rates x / y / z | 0.13 / 0.19 / 0.55·sin(0.07t) | 0.05–0.3 | tumble speed | M |

## 7. Palette and color

The body colour comes entirely from `A + B·cos(2π(t + D))` with A `#7A7580` and B `#756E78` — a mid-grey oscillation whose extremes are roughly `#EFE3F8` (A+B) and `#050708` (A−B), and whose per-channel phase offsets turn that into an oil-slick ramp: red leads, green follows at 0.278, blue at 0.659. The knot therefore passes through lime `#9BE05A`-ish, teal, blue, violet and warm orange; hue follows the interference-like phase rather than a hue wheel. Highlights: warm white `#FFF6E6` on the tight lobe, cold `#8EC8FF` on the broad lobe, so the specular never reads as a single white speck. Backlight `#2B1046` → `#050109`; clear is transparent so the host backdrop (source preview: black → `#1A0033`) shows at the edges. The knot is opaque and writes depth; the aura is additive and only visible at the limb. No tone map; `outputColorSpace` is sRGB but custom shaders write display-space values via the `rgb()` helper.

## 8. Composition and camera

A single centred object, no horizon. At z 7.4 with 40° FOV the knot spans ≈0.71 of frame height at rest, growing toward ≈0.85 as the rig tilts a lobe toward the camera (the source comment notes the knot is widest on its own diagonal). Below aspect 1.1 the FOV widens to 54° so a portrait frame still contains it. The camera orbits ±0.5 in x and ±0.38 in y, which parallaxes the motes and the backlight disc against the knot without changing the framing much. The far edge of the aura sits within a few percent of the frame at the poster's pose — keep `cameraZ` ≥ 6.8 unless deliberately cropping.

## 9. Randomness and seeds

Motes only: an LCG (`state = (state·1664525 + 1013904223) mod 2³²`) seeded **777**, drawing per mote a random-in-cube direction (normalised), a shell factor 0.45–1.15, a drift x 0.06–0.2, a drift y 0.05–0.17, and a seed 0–1. Everything else is deterministic: the knot is analytic, the palette is parametric. No warmup.

## 10. Performance budget

Three draw calls (knot, aura, motes) plus the backlight quad; ~8k triangles twice (front + inflated back faces). Cost is fill rate at the silhouette and the aura's additive shell, plus the high-exponent specular (cheap). 60 fps trivially at DPR 1.75. Cut-first: `radialSegments` 24→16, then `tubularSegments` 168→120 (specular may staircase), then `maxDpr` 1.75→1.5, then drop `motes` to 30.

## 11. Host integration

`absolute inset-0 pointer-events-none` holder, `block w-full h-full` canvas, no input. Renderer `alpha: true`, clear `(0,0,0,0)`, DPR capped at 1.75. Sizing from holder offsets, FOV re-derived from aspect on resize. Motes receive `uDpr` explicitly. Teardown traverses the scene disposing geometry and materials (the knot and aura share one geometry; three's second `dispose()` is a no-op), then `renderer.dispose()` + `forceContextLoss()`. One instance per page. No external assets.

## 12. Failure modes and tells

- **Knot looks painted, not metallic** — the two Blinn lobes collapsed into one, or exponents equal; the warm/cold pair is what reads as wet chrome.
- **Flat rainbow instead of oil slick** — palette D set to zeros; the 0/0.278/0.659 phase offsets are what order the hues.
- **Colours crush to black or clip to white** — palette B amplitude raised past A; keep B ≲ A and A near mid-grey.
- **Glow fills the whole knot** — aura drawn `FrontSide` or without depth test, so it covers the body; it must be `BackSide`, inflated, and depth-tested.
- **Glow band thicker on the inside of bends** — scaling the geometry instead of inflating along normals.
- **Knot clips the frame when it tilts** — `cameraZ` too small or the portrait FOV switch missing.
- **Specular staircases** — `tubularSegments`/`radialSegments` too low for a 96-exponent highlight.
- **Washed-out colours on modern three.js** — the palette double-converted through `THREE.Color` colour management; the custom shaders expect raw channels.
- **Motes flicker as hard dots** — the size clamp ceiling (7 px) hit, or `smoothstep` disc replaced by a hard circle.

## 13. Tuning knobs

1. `tube` vs `cameraZ` — how fat and how large the knot reads; 0.36/7.8 is a good airy variant.
2. `film` — iridescence strength; 0.8–1.8.
3. `specular` — highlight size; 60–140.
4. `auraGain`/`auraInflate` — glow strength and thickness; 0.35–0.7 / 0.08–0.16.
5. rig yaw rate 0.19 — how quickly the pose changes; 0.12–0.28.

## 14. Verification checklist

- Knot occupies 0.7–0.85 of frame height, centred within ±3%.
- Surface hue spans at least four distinct families (green, cyan, blue, violet/magenta) at once.
- At least two tight white specular caps; rim brightening at the silhouette.
- Aura visible as a thin coloured fringe outside the silhouette, not as an interior haze.
- Slick hue at a fixed surface point cycles in ≈40 s.
- No visible polygon edges along the tube at rest; no clipping at any aspect ≥ 1.0.
- Backdrop visible only outside the knot and its fringe.

## 15. Porting notes

`TorusKnotGeometry` in three uses p = 2, q = 3 for the classic trefoil; other engines' knot builders may swap p/q, which changes the silhouette entirely. The aura trick depends on drawing the same buffer with `BackSide` and normals inflated in the vertex shader — in raw WebGL, keep a single VBO and toggle `gl.cullFace` between passes, and keep the body's depth write on so the back faces are occluded. The cosine palette is the whole look; do not replace it with HSV.
