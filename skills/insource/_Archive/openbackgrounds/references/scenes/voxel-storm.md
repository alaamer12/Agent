---
id: voxel-storm
name: Voxel Storm
family: webgl-f5
renderer: three
poster: assets/posters/voxel-storm.jpg
complexity: XL
source_lines: 544
dpr_max: 1.75
deps: [three]
poster_capture: 640x400
---

# Voxel Storm — scene reference

## 1. Identity

A tornado of tumbling ice-blue cubes — a few of them glowing amber — spiralling upward around a warm, glowing column of embers, all on a near-black violet field.

## 2. Perceived look

Thousands of small, hard-edged cubes, each at its own orientation, catching a key light on one face and a rim on another, so the mass reads as a swarm of solid objects rather than confetti. The layout is a funnel: dense at the top where the cubes spread into a wide, sparse crown; tighter at the bottom; and a narrow, warm vertical core in the middle where the embers and the glow plane show through. Cubes are cool — deep navy through steel blue to pale ice — and the amber ones (about 9%) are small hot accents scattered through the field, denser near the core. Because of the funnel taper and the camera's slight downward tilt, the top edge of the swarm is cut by the frame, which makes the storm feel larger than the view. Depth is communicated by the fog fade and by cube size: near cubes are sharp and large, far ones soft and small. The 3 s screenshot shows a vertical column of blue cubes on black, an amber/orange streak up the centre, and a few warm cubes flaring brightest.

## 3. Frame anatomy

Back to front:

1. **Clear** `(0,0,0,0)` — transparent canvas; host backdrop is the deepest field (source preview: black → `#1A0033`).
2. **Core glow** — a 7.5×13.5 plane at y 0.4, billboarded to the camera each frame, `depthTest: false`, `renderOrder = 5`, additive; column mask `exp(−14·x²)` × vertical window, colour `#2A4C78 → #FF8A2B`, alpha `·0.22`.
3. **Voxel swarm** — 1,900 instanced unit cubes, `FrontSide`, transparent, **`depthWrite: true`** (so cubes occlude each other correctly), placed entirely by the vertex shader from per-instance seeds.
4. **Embers** — 260 additive point sprites inside the funnel, `depthTest: false`, `renderOrder = 4`, max 13 px, warm `#FFB45E`.

The vortex group rotates as a whole (`0.05t`); everything else is per-vertex. `frustumCulled = false` on both instanced meshes because the geometry's bounding box (a unit cube) does not describe where the shader puts the instances.

## 4. Motion law

- **Rise.** `y = mod(seed·13.5 + t·climb, 13.5) − 6.75`, `climb = 1.05·(0.45 + 0.7·(1 − rn))` — the inner cubes (rn → 0) climb at 1.2075 u/s, the outer at 0.4725 u/s. The column is 13.5 tall, so an inner cube traverses it in **11.18 s**, an outer one in **28.57 s**.
- **Rotate.** `ω = 2.15/(0.8 + 0.5r)`; at r ≈ 1 that is 1.65 rad/s (3.8 s per turn), at r ≈ 8 about 0.45 rad/s (14 s per turn). Differential rotation is what shears a random scatter into spiral arms over time.
- **Wind-up.** `θ += hf·0.16·2π` — 0.16 turns of shear from base to crown; subtle, so the arms wind slowly rather than braiding into a rope.
- **Flare.** `flare = mix(0.42, 1.1624, hf^0.85)` — the funnel is 42% of base radius at the floor and 116% at the crown.
- **Cube tumble.** `angle = t·(0.55 + 0.45ω) + 2π·seed`, around per-cube axis `(sin(12s), 1.25, cos(7s))`; speed roughly 1.3–1.8 rad/s near the axis. Cube size pulses `0.74 + 0.32·sin(1.3t + 26s)` — period 4.83 s.
- **Embers.** `y = mod(y0 + t·13.5·(0.13 + 0.11s), 13.5) − 6.75` — 1.76–3.24 u/s, roughly 2× the cubes, so sparks overtake the swarm. They converge from radius ×1.0 at the base to ×0.55 at the crown.
- **Group spin.** `vortex.rotation.y = 0.05t` — 125.7 s, on top of all per-cube rotation.
- **Glow breathe.** `0.72 + 0.28·sin(0.5t)` — 12.6 s; glow alpha 0.22 max, so it is a floor light rather than a lantern.
- **Camera.** `x = 1.5·sin(0.09t)` (69.8 s), `y = 3.4 + 0.5·sin(0.13t)` (48.3 s), gaze y bobs 0.4 ± 0.3 (57.1 s).
- **Phase at t = 0.** Cubes at seeded heights and orientations; embers at seeded heights; deterministic. Open-ended.

## 5. Technique and math

three.js; one `InstancedMesh` of unit cubes does the entire storm, plus a point cloud and a billboard glow.

- **Placement.** Per instance: `rn = sqrt(random())` (area-uniform on the shell, avoiding an axis cluster), `radius = 1.0 + rn·6.6`, `hf` from the wrapped height, `flare` as above, `r = radius·flare`; `θ = seedAngle + t·ω + hf·1.0053`; centre `= (cosθ·r, y, sinθ·r)`.
- **Pose.** Rodrigues rotation of the unit-cube position and normal about a per-cube axis — cheaper than a matrix and it carries the normal so the facets keep catching light. `local = turn(position·size, axis, angle)`.
- **Shading.** Two fixed view-space directions: key `(0.28, 0.72, 0.63)` × 0.92 and fill `(−0.55, −0.4, 0.35)` × 0.22, base 0.12; rim `(1 − dot(n, view))³`. Fragment: `colour = tint·light + tint·rim·0.55 + amber·isHot·(0.35 + 1.4·rim)·1.15`; alpha `fade·(0.5 + 0.5·min(light, 1))`; output `colour·fade`; discard below 0.004.
- **Fog.** `vFade = 1 − smoothstep(13, 34, −view.z)` — a soft far fade, not scene fog.
- **Tint.** `mix = random()^1.5`; below 0.42 lerp `#1D3A5C → #4A7DB0`, above lerp `#4A7DB0 → #9AD2F5`; then 9% of cubes are replaced by amber `#FF9940` and flagged hot.
- **Embers.** Position `(radius, y0, angle)` from seeded polar data; radius shrinks 45% with height; wobble ±0.14 on x/z at 1.7 and 1.4 rad/s; point size `0.65·dpr·120/max(−view.z, 0.8)`, clamp 1–13; glow `0.45 + 0.55·sin(t·(2.2 + 2s) + 39s)`.
- **Core glow.** `column = exp(−14x²)` in uv, vertical window `smoothstep(0, 0.32, y)·smoothstep(1, 0.62, y)`, alpha `column·vertical·breathe·0.22`, colour `mix(#2A4C78, #FF8A2B, column²)`.
- **Camera.** `PerspectiveCamera(50°, aspect, 0.1, 90)` at `(0, 3.4, 15.5)`, looking at `(0, 0.4, 0)`.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `seed` | 90210 | any u32 | cube layout, tints, hot cubes; embers at +41 | H |
| `voxels` | 1900 | 600–4000 | swarm density | H |
| `embers` | 260 | 0–800 | spark count | M |
| `maxDpr` | 1.75 | 1–2 | pixel ratio cap | M |
| `radiusMin` / `radiusMax` | 1.0 / 7.6 | 0.5–2 / 5–10 | radial band of the funnel | H |
| `columnHeight` | 13.5 | 9–20 | column height; controls loop period | H |
| `swirl` | 2.15 | 1–3.5 | angular speed at the axis | H |
| `lift` | 1.05 | 0.5–2 | vertical speed scale | H |
| `twist` | 0.16 | 0–0.4 | base-to-crown shear in turns | M |
| `flare` | 0.42 | 0.2–0.7 | funnel taper (base radius as a fraction) | H |
| `cubeSize` | 0.17 | 0.08–0.3 | cube edge length | H |
| `hotShare` | 0.09 | 0–0.2 | fraction of amber cubes | M |
| `fogNear` / `fogFar` | 13 / 34 | — | far fade window | M |
| `cameraX` / `cameraY` / `cameraZ` | 0 / 3.4 / 15.5 | −4–4 / 2–6 / 11–22 | view position; X = 0 keeps the column centred | H |
| `fov` | 50 | 40–65 | framing; vertical | M |

## 7. Palette and color

Ice ramp: deep `#1D3A5C` (0.114, 0.227, 0.361), mid `#4A7DB0` (0.290, 0.490, 0.690), bright `#9AD2F5` (0.604, 0.824, 0.961). Amber `#FF9940` (1.0, 0.6, 0.251) for hot cubes — their emission colour is `#FFA347` — ember `#FFB45E`; core inner `#FF8A2B`, outer `#2A4C78`. The lighting multiplies tints by 0.12–1.26 (key + fill), and the rim adds 55% of the tint at grazing angles, so cube colours stay in the blue family and only the 9% amber set and the centre column introduce warmth. Additive embers and the glow plane stack over the frozen cube colours, so the column centre goes orange-white while the crown stays cold. The scene is drawn over a transparent canvas, so the darkest areas are the host backdrop; no tone map, and `outputColorSpace` is sRGB while the shaders write display-space values.

## 8. Composition and camera

A vertical subject in a landscape frame. The camera looks slightly downward from y 3.4 at 15.5 units, with a 50° FOV: half-height at the origin plane is 7.23 units, and the column is 13.5 tall, so the crown's top edge sits right at (and occasionally beyond) the frame's top. The widest crown radius is 7.6·1.16 ≈ 8.8 units, inside the ±11.6 horizontal half-width at 16:10, so the swarm is cut vertically, not horizontally. This is deliberate: the cropped crown is what makes the storm feel bigger than the view. Aspect: FOV vertical, so portrait frames crop the crown harder and show less width, which increases the sense of a narrow funnel. The camera sways ±1.5 in x, so the column's position in frame drifts about ±10%.

## 9. Randomness and seeds

Two LCG streams (`state = (state·1664525 + 1013904223) mod 2³²`): **90210** for the cubes — per cube `sqrt(random())` radius factor, angle, height seed, pose seed, tint mix, hot flag, in that order — and **90251** (90210 + 41) for the embers — radius `0.25 + r^0.7·2.6`, height, angle, seed. The scene is seeded specifically so a captured poster and the live background describe the same storm. No warmup: all motion is an analytic function of `t`, so the layout at t = 0 is fully deterministic.

## 10. Performance budget

Three draw calls: 1,900 instances × 12 triangles = 22,800 triangles with transparent, depth-writing material; 260 additive points; one quad. The cube count and the rim/emission per fragment are the cost; at DPR 1.75 this runs at 60 fps on integrated GPUs but is the heaviest geometry in f5. Cut-first: `voxels` 1900→1200, then `maxDpr` 1.75→1.5, then `embers` 260→120, then disable the rim term (it costs a normalization per fragment).

## 11. Host integration

`absolute inset-0 pointer-events-none` holder, `block w-full h-full` canvas, no input. Renderer `alpha: true`, clear `(0,0,0,0)`; host backdrop must be dark. Sizing from holder offsets, DPR capped at 1.75; ember `uDpr` refreshed on resize. Teardown traverses the scene disposing geometry and materials, then `renderer.dispose()` + `forceContextLoss()`. One instance per page (shared FPS meter). No external assets.

## 12. Failure modes and tells

- **Cubes cluster on the axis** — the `sqrt()` radius bias was dropped; without it the cylinder's area weighting is wrong and the storm looks like a bead on a wire.
- **Storm looks like a solid cylinder** — `flare` set too high (or base/top swapped); the funnel needs a 0.4 vs 1.16 ratio.
- **Cubes slide without tumbling** — the Rodrigues rotation of the normal dropped; cubes then read as flat squares.
- **Whole storm is one flat colour** — rim term removed, or tints forced to a single value; the rim is what separates faces at grazing angles.
- **Amber overwhelms** — `hotShare` above ~0.15; the warm accents must stay sparse to read as embers.
- **Storm looks static in depth** — fog window widened or removed; near/far size difference does most of the depth work.
- **Cubes pop out at the top/bottom** — the modulo wrap is correct, but `frustumCulled` left on makes the whole mesh vanish when the camera sways; keep it off.
- **Embers hide behind cubes** — `depthTest` turned on for the embers; they are meant to draw over the swarm.
- **Centre is flat grey** — the core glow lost its `exp(−14x²)` column mask or its billboard orientation.

## 13. Tuning knobs

1. `voxels` and `cubeSize` — density vs individual legibility; 1200×0.22 is a chunkier storm.
2. `flare` — funnel silhouette; 0.3–0.5.
3. `swirl` — how fast the arms turn; 1.6–3.
4. `hotShare` — warmth of the accents; 0.05–0.12.
5. `cameraZ` — how much of the crown is cropped; 13–19.

## 14. Verification checklist

- Vertical column of cubes centred within ±10% of frame centre; crown cropped by the top edge.
- Dominant hue 205–220° (ice blue); amber cubes present but under ~12% of visible cubes.
- Visible warm core along the vertical centre, brightest around the middle height.
- Rotation: a cube at radius 3 completes a turn in ≈6–7 s; inner cubes visibly faster than outer.
- Rise: cubes traverse the column in 11–29 s; no popping at the wrap seam.
- Cube faces shaded differently (key vs rim), not flat.
- No visible hard edge where the fog ends; no flicker on resize.

## 15. Porting notes

`InstancedMesh` here carries only per-instance seeds; positions, sizes and rotations are all computed in the shader. In raw WebGL2, use instanced attributes the same way (`aSeed`, `aTint`); in WebGL1 without instancing, either bake each cube's seed into duplicated vertices or accept a much smaller count. The Rodrigues helper must rotate the normal as well as the position or the lighting collapses. The ember pass is drawn with `depthTest: false` on purpose; enabling it hides most sparks inside the swarm.
