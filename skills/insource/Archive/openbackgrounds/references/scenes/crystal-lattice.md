---
id: crystal-lattice
name: Crystal Lattice
family: webgl-f4
renderer: webgl1
poster: assets/posters/crystal-lattice.jpg
complexity: XL
source_lines: 525
dpr_max: 1.5
deps: []
poster_capture: 640x400
---

# Crystal Lattice — scene reference

## 1. Identity

A translucent cube of glowing struts — a 9×9×9 grid of nodes wired into an orthogonal lattice — that ripples like a struck bell, breathes, and tumbles slowly at frame centre on black.

## 2. Perceived look

Thin, evenly bright lines with no anti-aliasing haze beyond the browser's MSAA; the strongest structure is the twelve edges of the outer cube, which read about twice as bright as the interior field and give the object a hard, crystalline silhouette. Interior struts are dimmer and multiply where the projection compresses the back of the cube, so the middle of the object looks denser and softer than its frame. Nodes are small glowing dots with a sharp white core and a wide, faint halo; the brightest beads follow the strut density rather than sitting only on the frame. Colour shifts across the object — cyan along one axis, periwinkle along the second, violet along the third — so the cube reads as three interpenetrating colour fans rather than a single hue. Background is near-black with a very slight blue lift (`ground` 0.008, 0.010, 0.024); contrast is extreme: quiet black around a bright, small object. The 3 s screenshot shows a roughly hexagonal blue-white outline with a dense, softly glowing interior mesh and a handful of bright corner beads.

## 3. Frame anatomy

Back to front, all in one canvas:

1. **Clear colour** — `(0.008, 0.010, 0.024)` at alpha 1; the canvas is opaque, so the holder/parent backdrop never shows through.
2. **Far lattice lines** — struts behind the cube's mid-depth, faded by depth and tinted by the axis they belong to; additive, alpha ≈ 0.28–0.5.
3. **Far nodes** — point sprites at the same depth ranges, small (1–12 px) and dim.
4. **Near lattice lines** — struts in front of mid-depth at full strength; the hull frame (×1.85 alpha) is part of this layer.
5. **Near nodes** — up to 44 px sprites with a `k^2.1` halo and `k^11` white core, the brightest elements.

No depth buffer, no depth writes; draw order is LINES then POINTS in two `drawArrays` calls, so all nodes composite additively over all lines regardless of true depth. Blend is `SRC_ALPHA, ONE` (additive). The canvas is opaque and antialiased (`antialias: true`, `alpha: false`).

## 4. Motion law

- **Phonon wave.** A plane wave travels along the body diagonal `normalize(1,1,1)` at phase speed `waveSpeed / waveFrequency = 1.15 / 2.35 ≈ 0.49` world units per second; temporal frequency 1.15 rad/s ⇒ period ≈ 5.46 s. Amplitude 0.055 world units (≈2.1% of the 2.56-unit cube side). Every vertex, node and strut endpoint alike, is displaced along the diagonal.
- **Secondary shear.** A cross-wave along `normalize(-1,1,0)` at 0.73× the phonon phase plus a 1.1 rad offset, amplitude `0.055 × 0.45 = 0.0248`. This is what makes the cube look twisted rather than simply pumped.
- **Breath.** Uniform scale `1 + 0.035·sin(0.29 t)`; rate 0.29 rad/s ⇒ period ≈ 21.7 s, amplitude ±3.5%.
- **Orientation.** `rotX(0.44 + 0.12·sin(0.21 t)) · rotY(0.11 t) · rotZ(0.035 t)`. Yaw is a steady 0.11 rad/s (one full turn every 57.1 s); roll 0.035 rad/s (one turn every 179.5 s); pitch oscillates ±0.12 rad about 0.44 rad with period 29.9 s.
- **Node excitement.** Each node's brightness and size pulse with `0.5 + 0.5·sin(phase)`, i.e. locked to the phonon wave, so a bright band of nodes sweeps across the cube in step with the visible ripple.
- **Phase at t = 0.** Wave phase = `dot(p, diag)·2.35`; orientation = rotX(0.44)·rotY(0)·rotZ(0). Open-ended: no loop, no state.

## 5. Technique and math

Domain is a static CPU-built lattice uploaded once, then fully animated in the vertex shader. No textures, no per-frame CPU work.

- **Geometry.** Nodes at `p = (i, j, k)·step − half`, `step = 2·half/(n−1) = 2.56/8 = 0.32`, `n = 9` ⇒ 729 nodes. Each node emits up to three struts (+x, +y, +z toward the next index) ⇒ 1944 struts ⇒ 3888 line vertices. Both sets live in one interleaved float layout: `x, y, z, axisOrKind, hull` (5 floats/vertex).
- **Displacement.** `phase = dot(p, normalize(1,1,1))·2.35 + 1.15 t`; `p += diag·sin(phase)·0.055`; `p += normalize(-1,1,0)·cos(0.73·phase + 1.1)·0.0248`; then `p *= 1 + 0.035·sin(0.29 t)`.
- **Rotation and projection.** `q = Rx(0.44 + 0.12 sin 0.21t) · Ry(0.11t) · Rz(0.035t) · p` — the X rotation is applied last (outermost), matching the explicit rotX·rotY·rotZ product. `w = max(q.z + 7.0, 0.05)`; `gl_Position = (q.xy·focal/w, 0, w)`. Because clip-space w is the same `w`, the hardware divides again, so the effective on-screen scale of a feature of world size `s` is `s·focal/(z+7)²` — an inverse-square perspective, not a plain pinhole. This magnifies near geometry much more aggressively than a conventional camera.
- **Aspect.** `focal` uniform is `(focal/aspect, focal)` with `aspect = drawingBufferWidth/Height`; `focal = 17·min(1, aspect/1.6)`. At aspect ≥ 1.6 the cube is framed identically at any size; below 1.6 both axes shrink together, keeping the object contained on portrait frames.
- **Depth fade.** `fade = (1 − smoothstep(5.0, 9.4, w))^1.45`; with the cube spanning `w ≈ 7 ± 1.28·√3 ≈ 4.78…9.22`, the back face is nearly extinguished and the front face at full strength.
- **Tint.** `a_data.x` is the strut axis (0/1/2) or 3 for nodes. Struts: pick tintX by default, tintY where `a_data.x ≥ 0.5`, tintZ where `≥ 1.5`. Nodes mix `tintX·0.45 + tintZ·0.75`.
- **Hull.** `a_data.y` is 1 for struts on the twelve outer-cube edges, 0.4 for nodes on the hull, and 1 for interior nodes. Alpha is multiplied by `mix(1.0, 1.3, 1.85·flag)`: 1.555 for hull struts and interior nodes, 1.222 for hull nodes, 1.0 for interior struts. There is no separate geometry: the flag is baked into the vertex.
- **Node sprites.** `world = 0.0085·(0.5 + 0.68·excite)`; `gl_PointSize = clamp(world·focal·height·0.5/max(w,0.4), 1, 44)`. Fragment: discard outside the unit disc; `k = 1 − 2d`; halo `k^2.1`; core `k^11` added as near-white `(0.88, 0.97, 1.0)`; final alpha `v_alpha·strength·(0.12 + 0.88·halo)`.
- **Line fragment** is flat colour × `v_alpha·strength` — no width control; the apparent weight comes from overlapping additive struts and MSAA.

## 6. Parameters

| name | value | range | effect | sensitivity |
|---|---|---|---|---|
| `maxDpr` | 1.5 | 1–2 | device-pixel ratio cap; above 1.5 struts thin out | M |
| `nodes` | 9 | 5–13 | lattice resolution per axis; cubic cost (nodes³) | H |
| `half` | 1.28 | 0.8–2.0 | world half-size; scales the cube with no reframing | H |
| `focal` | 17.0 | 10–30 | projection strength; doubles as zoom (inverse-square) | H |
| `distance` | 7.0 | 4–12 | camera Z offset; larger flattens and shrinks the object | H |
| `refAspect` | 1.6 | 1.2–2.0 | aspect below which both axes shrink together | L |
| `waveSpeed` | 1.15 | 0.4–2.5 | temporal frequency of the phonon (rad/s) | H |
| `waveAmp` | 0.055 | 0.01–0.12 | peak vertex displacement along the diagonal | H |
| `waveFrequency` | 2.35 | 1.0–5.0 | spatial frequency of the ripple across the cube | H |
| `shearAmount` | 0.45 | 0–0.9 | scale of the secondary cross-wave relative to `waveAmp` | M |
| `breathAmount` | 0.035 | 0–0.08 | uniform scale pulse amplitude | M |
| `breathRate` | 0.29 | 0.1–0.8 | breath angular rate (rad/s) | L |
| `tilt` | 0.44 | 0.2–0.7 | resting X rotation (rad) | M |
| `tiltSwell` | 0.12 | 0–0.3 | amplitude of slow pitch oscillation | M |
| `spin` | 0.11 | 0.02–0.3 | steady Y rotation rate (rad/s) | M |
| `roll` | 0.035 | 0–0.1 | steady Z rotation rate (rad/s) | L |
| `nodeSize` | 0.0085 | 0.004–0.02 | world radius of node sprites | M |
| `hullBoost` | 1.85 | 1.0–2.5 | alpha multiplier on the twelve frame edges | M |
| `depthNear` / `depthFar` | 5.0 / 9.4 | 4–10 / 8–12 | depth window of the fade | M |
| `lineStrength` / `nodeStrength` | 1.0 / 1.0 | 0.4–1.6 | global alpha of each draw call | H |

## 7. Palette and color

Canvas clear `ground` `#020306` (0.008, 0.010, 0.024 in linear float, treated as sRGB by the browser — these values read as a very dark blue-black). Strut axis tints: X `#38E1FF` (0.22, 0.88, 1.0), Y `#578FFF` (0.34, 0.56, 1.0), Z `#AD5CFF` (0.68, 0.36, 1.0). Node colour is `tintX·0.45 + tintZ·0.75` = (0.609, 0.666, 1.2), clipped to 1.0 in blue on output, i.e. `#9BAAFF` — a warm periwinkle that the white core pushes toward blue-white. Excitation multiplies node colour by `0.7 + 0.55·excite` (0.7–1.25); lines keep flat colour. Additive blending means all overlaps brighten toward white; there is no tone map and no gamma handling, so the brightest intersections clip to white. Effective background is genuinely black because the canvas is opaque.

## 8. Composition and camera

Single object, centred, occupying roughly 44% of the shorter viewport axis face-on and up to ~77% when a body diagonal swings into the image plane — most of the tumble. Because the projection has no look-at and the object is centred at world origin, there is no horizon and no off-centre weighting. Aspect: landscape frames ≥1.6 are identical at any width; narrower frames scale the focal down proportionally, which keeps the cube inside the vertical safe area. Portrait phones (<1.0) end up showing the cube at roughly half the landscape size. The `refAspect` 1.6 clamp means 640×400 (1.6) and 1920×1080 (1.78) match exactly.

## 9. Randomness and seeds

None. The lattice is fully deterministic from `nodes`, `half`, and the integer index loops; there is no RNG call anywhere in the scene, no warmup, and no per-run variation. Two runs on two machines draw the same frame at the same `t`.

## 10. Performance budget

729 points + 1944 line segments in two `drawArrays` calls, no textures, no depth buffer — the cost is dominated by fill rate from additive line overlap in the cube's interior and by the 44 px point sprites on the hull. At DPR 1.5 on a 1920×1080 canvas this is comfortably 60 fps on integrated GPUs; the interior overlap is the first thing to cost. Cut-first list: drop `nodes` 9→7 (729→343 nodes, 1944→882 struts, ~55% fewer verts with a visibly coarser cube), then lower `maxDpr` to 1.25, then clamp `gl_PointSize` from 44 to 28.

## 11. Host integration

Mount the canvas into an `absolute inset-0` holder; the canvas itself is `block w-full h-full` and the holder is `pointer-events-none` — there is no pointer input. Sizing is `offsetWidth/offsetHeight` of the holder at mount and on `window resize`, multiplied by `min(devicePixelRatio, 1.5)`, with a `Math.max(1, …)` floor; the CSS size is written back in CSS pixels. Teardown cancels the RAF, deletes both buffers and programs, and calls `WEBGL_lose_context.loseContext()` before nulling `gl` — important because galleries mount many scenes. Only one instance may be live at a time (shared FPS meter). No external assets.

## 12. Failure modes and tells

- **Cube fills the frame / clips** — `focal` too high for the viewport, or `refAspect` clamp bypassed; the inverse-square projection makes `focal` far more aggressive than a pinhole `fov`. Fix by lowering `focal` or raising `distance`.
- **Interior turns into a solid glowing blob** — additive overlap saturating at `nodes ≥ 11`; lower `nodes` or `lineStrength` (0.6–0.8).
- **Struts vanish on retina screens** — DPR allowed above 1.5 with ≤1 px lines; clamp to 1.5 and keep MSAA on.
- **Cube looks like it is pumping, not ringing** — `waveFrequency` too low; the ripple needs ≥3 half-waves across the cube, so keep ≥2.0 at `nodes = 9`.
- **Ripple invisible** — `waveAmp` under ~0.03 world units (≈1% of cube side); raise to 0.05–0.07.
- **Hull edges indistinguishable from the interior** — `hullBoost` at 1.0; the frame needs ≈1.8× to read as a cube rather than a cloud of sticks.
- **Node sprites become hard discs** — `gl_PointSize` clamp hit (44 px) so the halo is cropped; lower `nodeSize` or the clamp.
- **Nothing draws** — a vertex attribute stride mismatch (must be 5 floats / 20 bytes; `a_pos` at 0, `a_data` at 12).

## 13. Tuning knobs

1. `focal` then `distance` — zoom and perspective; keep the on-screen coverage at 0.4–0.6 of the short axis.
2. `waveAmp` then `waveSpeed` — ripple depth and speed; 0.05/1.15 is the rested look.
3. `nodes` — resolution; 9 reads as a lattice, 7 as a frame, 11 as a solid.
4. `hullBoost` — crystalline contrast; 1.6–2.0.
5. `lineStrength` — global exposure of the strut field; 0.7–1.2.

## 14. Verification checklist

- Object centre within ±5% of frame centre; coverage 0.40–0.60 of the short axis in the resting tumble.
- Dominant hue in the cyan→violet band (hue 190°–265°); no warm pixels other than additive white cores.
- Background luma < 2% outside the object; object peak luma near 255 at hull nodes.
- Visible ripple: sample a fixed interior strut over 2 s — its screen position should oscillate by several pixels.
- Full yaw period ≈ 57 s, roll ≈ 180 s; pitch period ≈ 30 s.
- No clipping at the frame edges at any aspect ≥ 1.0; no flicker on resize.
- The shipped poster shows a tighter, smaller object than the current constants produce; trust `focal`/`distance` (0.44 coverage face-on) for scale, and treat the poster as a hue/structure reference.

## 15. Porting notes

The double perspective divide (`gl_Position = (q.xy·focal/w, 0, w)`) is not a standard camera; if you switch to `PerspectiveCamera` in three.js, use a very small FOV (≈12°) at ≈7 units to approximate the framing, and expect the near geometry to be less magnified. In WebGL2, `gl_PointSize` is fine but `enableVertexAttribArray` state persists across programs — re-bind both attributes per program. The scene deliberately omits `depthTest`; adding it will change which struts appear on top, contradicting the additive look.
