---
id: facets-tunnel
name: Facets Tunnel
family: webgl-f5
renderer: three
poster: assets/posters/facets-tunnel.jpg
complexity: XL
source_lines: 626
dpr_max: 1.75
deps: [three]
poster_capture: 640x400
---

# Facets Tunnel — scene reference

## 1. Identity

A flight down an endless nine-sided bore of irregular slate polygons, lit by a lamp that dives ahead and orbits the axis, ending in a small pulsing glow at the vanishing point.

## 2. Perceived look

A dark, cold, architectural tunnel rather than a colourful tube: the walls are neutral blue-grey slabs, each facet flat-shaded with a single normal, so the bore reads as a stack of faceted rings — irregular polygons whose corners were jittered — receding into a smaller and smaller hole. Because the camera sits inside the tube, the nearest walls are seen at grazing angle and fade out; the middle distance is the clearest, and the far rings dissolve into fog, leaving a soft glow at the end. Light is the moving element: one lamp sweeps around and down the bore, so on each passing ring a different set of facets lights up while the rest drop to a very low ambient. The lamp's colour drifts through three stops — hot pink, cyan, amber — over about eighteen seconds, so the tunnel changes temperature quickly. A few bright motes drift inside the bore, tinted by the lamp. The 3 s screenshot shows concentric irregular polygons shrinking toward a violet-pink core at frame centre, the walls a dark slate blue with one or two brighter facets, black at the corners.

## 3. Frame anatomy

Back to front:

1. **Clear** `(0,0,0,0)` — transparent canvas; the host backdrop shows at the frame edges where geometry fades.
2. **Beacon** — 22×22 plane at z = −69 (0.92 of the 75-unit span), `depthTest: false`, `renderOrder = −1`; a lamp-coloured disc with `core³·0.5·pulse`, `pulse = 0.7 + 0.3·sin(0.9t)`; it sits at the end of the bore and shines through the fading far rings.
3. **Tunnel walls** — one 9-sided prism segment (18 triangles) instanced 30 times along z; `FrontSide`, transparent, **`depthWrite: true`**, wound so the visible face is the inside; per-ring tint from slate `#6D7F96` × 0.55–1.0.
4. **Dust** — 240 additive point sprites inside the bore, computed entirely in the shader, renderOrder 3, max 6 px.

Camera `PerspectiveCamera(76°, aspect, 0.1, 140)` at the origin looking down −z, drifting ±0.72 in x and ±0.58 in y and rolling ±0.42 rad. The 76° FOV is what makes the nearest ring wide enough to frame the shot.

## 4. Motion law

- **Travel.** `uTravel = 3.1·t`; each ring's depth is `mod(aZ + travel, 75) − 75 + 2.5`. With 30 rings spaced 2.5 units, one ring passes the camera every **0.81 s**, and the whole 75-unit loop repeats every 24.2 s. The recycle is seamless because rings wrap to the far end.
- **Twist.** Each cross-section is rotated by `depth·0.052` — 0.052 rad per unit, so the polygon rotates 3.9 rad (0.62 turns) over the full span; the wall therefore steps through its facets as it passes, rather than sliding straight.
- **Bend.** The axis wanders: `axis = (sin(0.042·depth + 0.05t), cos(0.031·depth − 0.04t))·0.75`. The z term of 0.042 rad/unit gives a bend wavelength of ~150 units and the time terms drift it slowly (periods 125.7 s and 157 s).
- **Lamp path.** Depth `−2.4 − ((1.06·travel) mod 39)` — the lamp dives from 2.4 to 41.4 units ahead and resets, completing a dive every **11.9 s**. It orbits at radius 1.7: `x = 1.7·cos(0.42t)` (15.0 s), `y = 1.7·sin(0.3234t)` (19.4 s) — an open Lissajous, not a circle.
- **Lamp colour.** `uLampPhase = 0.055·t` is a cycle count (0.055 cycles/s), so
  one three-stop cycle takes **18.18 s**, not 114.5 s. The lobes are a
  triangle-window partition of unity at ⅓-cycle spacing, so the colour passes
  pink → magenta → violet → cyan → teal → amber → pink smoothly.
- **Dust.** Each mote's depth is `mod(seedDepth + 1.28·t, 75) − 75` — they drift *backward* relative to the 3.1 u/s walls, so the bore appears to move faster than the dust inside it. Twinkle period 3.70 s.
- **Camera.** Drift periods 48.3 s (x), 57.1 s (y), roll 89.8 s; gaze wanders on 89.8 s / 125.7 s — a slow, weightless float rather than a dolly.
- **Phase at t = 0.** Rings at their seeded depths and rolls, lamp at 2.4 units ahead, palette at pink. Open-ended.

## 5. Technique and math

three.js; one instanced mesh with a custom shader does the whole tunnel, plus a shader-only point cloud and a billboarded glow.

- **Geometry.** A single ring segment: 9 corners at angles `s·2π/9` with radii `3.4·(1 + (r − 0.5)·0.3)`, extruded 2.5 units along z; 18 triangles, one shared outward-facing normal per quad. 30 instances, each with a random z-roll (0–2π) baked in its instance matrix.
- **Recycling.** `base = mod(aZ + uTravel, 75) − 75 + 2.5`, `depth = base + position.z`. The `+ segmentLength` offset keeps the segment from popping in exactly at the far plane.
- **Twist + bend.** `point = (turn(instanceXY, depth·0.052) + axis, depth)` with `axis` as above; normals are twisted by the same rotation but *not* bent (a deliberate simplification — the bend is small).
- **Fade.** `ahead = −view.z`; `vFade = (1 − smoothstep(32, 72, ahead)) · smoothstep(0.5, 7.0, ahead)`. The second term fades the wall passing beside the eye so the frame is never filled by an unlit slab.
- **Shading.** `lambert = max(dot(n, normalize(lamp − p)), 0)`; `reach = 1/(1 + d²·0.008)` (half-brightness at ~11 units); `colour = tint·(0.07 + lampColor·lambert·reach·1.7) + tint·#4E6F9C·pow(straightOn, 3)·0.45`; `colour *= 0.72 + 0.28·straightOn`; `alpha = vFade·(0.35 + 0.65·min(vFade, 1))`; output `colour·vFade`.
- **Lamp palette.** `w = fract(phase)·3`; `lobe(w, centre) = max(0, 1 − circularDistance(w, centre))`; colour `= (A·a + B·b + C·c)/max(a+b+c, 0.4)` — a partition of unity, so brightness is preserved through the blend.
- **Dust.** `angle = seed·2π + travel·0.052·0.35`, `band = fract(seed·7.13)`, `radius = mix(0.2, 1.05, band)·3.4`, `depth = mod(fract(seed·3.71)·75 + 1.28·travel, 75) − 75`.
- **Beacon.** Plane billboard at the end of the bore, re-centred on the bent axis each frame; alpha `core³·0.5·pulse`, additive, drawn first so it reads through the fog.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.75 | 1–2 | pixel ratio cap | M |
| `seed` | 8821 | any u32 | corner jitter, ring tints/rolls, dust (dust at +991) | M |
| `sides` | 9 | 5–16 | polygon sides; 9 gives an irregular, non-round bore | H |
| `rings` | 30 | 12–48 | instance count; density of rings down the bore | H |
| `segmentLength` | 2.5 | 1.5–4 | ring length; sets span = rings × length (75) | H |
| `radius` | 3.4 | 2–5 | bore radius vs the 76° FOV | H |
| `jitter` | 0.3 | 0–0.6 | corner in/out variation; faceting irregularity | H |
| `twist` | 0.052 | 0–0.12 | polygon rotation per unit depth | M |
| `bend` | 0.75 | 0–1.5 | axis wander amplitude | M |
| `speed` | 3.1 | 1–6 | travel speed; ring pass rate | H |
| `dust` | 240 | 0–800 | mote count | L |
| `dustSpeed` | 1.28 | 0–3.1 | mote drift vs wall speed | M |
| `falloff` | 0.008 | 0.003–0.02 | lamp inverse-square constant | H |
| `gain` | 1.7 | 0.8–3 | lamp brightness | H |
| `ambient` | 0.07 | 0.02–0.2 | unlit wall floor | M |
| `fogNear` / `fogFar` | 32 / 72 | 20–45 / 60–90 | far fade window | H |
| `lampSpeed` | 0.42 | 0.2–0.8 | orbit rate of the lamp | M |
| `lampCycle` | 0.055 | 0.02–0.12 | colour cycle rate in cycles/s (period 18.18 s) | M |
| `lampRadius` | 1.7 | 0.5–3 | orbit radius inside the bore | H |

## 7. Palette and color

Walls are neutral slate `#6D7F96` scaled 0.55–1.0 per ring — every colour in the scene comes off the lamp. Lamp stops: A `#FF2F7F` (hot pink), B `#22E0FF` (cyan), C `#FFAB2E` (amber), blended by the triangle window so midpoints are magenta (`A/B`) and orange-pink (`C/A`). Fill light on facets facing the camera: `#4E6F9C` (cold slate blue) × 0.45. Beacon is the lamp colour. Dust is the lamp colour × (0.5 + glow). Because the canvas is transparent and the walls fade at both ends, the corners and the far bore are a dark violet-black from the host backdrop, and the poster's overall cast is cold blue-violet with a pink-cyan core. No tone map; the shader writes display-space values.

## 8. Composition and camera

The camera sits on the axis of the bore, so the composition is a centred, nested set of polygons — a tunnel-perspective shot with no horizon. The 76° FOV makes the nearest ring (radius 3.4 at ~2.5 units) extend well beyond the frame, so the walls run off all four edges and the frame is entirely tunnel; only the far bore is a discrete shape. The camera drifts ±0.72/±0.58 and rolls ±0.42 rad, so the vanishing point moves around the frame over about a minute — at any instant it is within ~15% of centre. `bend` moves the axis, which shifts the far rings and the beacon laterally. Aspect: FOV is vertical; wide frames show more wall, portrait frames compress the bore's apparent width. Nothing clips because nothing is a discrete object except the far glow.

## 9. Randomness and seeds

Two LCG streams (`state = (state·1664525 + 1013904223) mod 2³²`): **8821** for the tunnel (9 corner jitters, 30 ring tints, 30 roll angles, in that order), and **9812** (8821 + 991) for the 240 dust seeds. Dust positions, radii and depths are *derived* from each seed in the shader via `fract(seed·7.13)`, `fract(seed·3.71)` and `seed·2π`, so the CPU only uploads one float per mote. No warmup; the ring layout is fixed at build time.

## 10. Performance budget

Three draw calls: 30 instances × 18 triangles (540 triangles) for the walls, 240 points, one quad. The cost is fill rate — the walls cover the whole frame with transparent, depth-writing geometry, and the near ring is heavily overdrawn at grazing angle. 60 fps at DPR 1.75 on integrated GPUs is comfortable; this is the least expensive scene in f5 geometrically. Cut-first: `maxDpr` 1.75→1.5, then `rings` 30→22 (visible as a shorter loop), then `dust` 240→120.

## 11. Host integration

`absolute inset-0 pointer-events-none` holder, `block w-full h-full` canvas, no input. Renderer `alpha: true`, clear `(0,0,0,0)`; the host backdrop must be dark. Sizing from holder offsets, DPR capped at 1.75, dust `uDpr` updated on resize. Teardown disposes geometry/materials via scene traversal, then `renderer.dispose()` + `forceContextLoss()`. One instance per page (shared FPS meter). No external assets.

## 12. Failure modes and tells

- **Camera sees the outside of the tube** — winding or `side` flipped; the visible face must be the inside (`FrontSide` with inside winding here, `BackSide` if you rebuild with outward winding).
- **Walls are solid grey with no facets** — normals smoothed or per-vertex; each quad must share one flat normal.
- **Tunnel stops looking endless** — the modulo recycle or the `+ segmentLength` offset dropped, so rings pop in at the far plane.
- **Near walls glare across the frame** — the `smoothstep(0.5, 7.0, ahead)` side of `vFade` removed.
- **Ring steps stutter** — `speed` not dividing the 2.5-unit ring spacing into a plausible cadence; at 3.1 u/s a ring passes every 0.81 s, which is the intended rhythm.
- **Colour jumps instead of blending** — the lobe window replaced by a straight mix without the `max(a+b+c, 0.4)` renormalisation; the brightness pulses at the switch.
- **Dust flies forward with the walls** — dust speed must stay well below wall speed (1.28 vs 3.1) or the tunnel loses its sense of rushing.
- **Beacon invisible through the bore** — `depthTest` left on, or `renderOrder` above the walls.
- **Far bore is a flat grey disc** — the fog window collapsed (fogFar ≤ fogNear) or the beacon alpha lost its `core³`.

## 13. Tuning knobs

1. `speed` — the sense of flight; 2–4.
2. `sides`/`jitter` — how irregular and how faceted the bore is; 7–12 / 0.2–0.4.
3. `lampCycle` — colour pace; 0.03–0.09.
4. `fogNear`/`fogFar` — how much depth is visible; 26/65 gives a longer bore.
5. `falloff`/`gain` — how tight and how bright the lamp pool is; 0.006/1.4 is more atmospheric.

## 14. Verification checklist

- Frame centre filled by nested irregular polygons; vanishing point within 15% of centre at all times.
- Walls dark slate blue (hue 210–230°) with one or two lamp-lit facets; warm pink/amber only where the lamp is near.
- Far bore shows a small pulsing glow, not a hard disc.
- Ring cadence ≈ 0.81 s; travel loop ≈ 24.2 s.
- Near walls fade smoothly into the frame edges; no unlit slab visible.
- 5–8 motes visible at any time, tinted by the current lamp colour.
- No pop when rings recycle; no flicker on resize.

## 15. Porting notes

`InstancedMesh` is used only to vary the z-offset, tint and roll — in raw WebGL2 use instanced attributes with the same three values; in WebGL1 without instancing, bake 30 copies or reconstruct ring depth per-vertex from a ring index. The inside-wound `FrontSide` + `depthWrite: true` combination is what gives the walls their solidity while remaining transparent; switching to `depthWrite: false` makes the far rings visible through the near ones and destroys the bore.
