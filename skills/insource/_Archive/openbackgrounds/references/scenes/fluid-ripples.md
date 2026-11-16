---
id: fluid-ripples
name: Fluid Ripples
family: webgl-f7
renderer: webgl1
poster: assets/posters/fluid-ripples.jpg
complexity: XL
source_lines: 562
dpr_max: 1.5
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Fluid Ripples

## 1. Identity

A soft luminous disc floating in darkness, its interior swirling in pale blue
and amber ribbons that deform and eddy wherever the pointer disturbs a small
CPU fluid simulation.

## 2. Perceived look

Dim, atmospheric, and slightly out of focus. The subject is a single circular
lens roughly 55% of the frame height, centered, with a feathered edge that fades
into near-black. Inside the disc the pattern is smooth bands and swirls, not
sharp geometry: cyan-white on one side, warm amber on the other, both dissolving
into a dark teal-grey middle. Contrast is low; the brightest pixels are pale,
never white. Motion is slow and organic at rest, with fast local ripples when
the pointer moves.

## 3. Frame anatomy

1. **Background** — flat dark navy `rgb(0.02, 0.02, 0.05)` covering the whole
   quad.
2. **Water disc** — one procedural pattern sampled inside a smoothstepped circle
   of radius 0.9 in half-height units (±0.12 antialiasing band), modulated by the
   simulated height field. Height maps to display influence in two stages:
   `waterInfluence = clamp(h · 0.55, ±0.5)`, then
   `totalWaterInfluence = clamp(waterInfluence · 0.55, ±0.8)` — so the effective
   range is ±0.275, not ±0.5. The pattern is written to RGB with a separate phase
   per channel, which produces the two-tone fringing.
3. **Edge fade** — with `r = |screenP|` in half-height units
   (`screenP = (2·gl_FragCoord − resolution)/resolution.y`),
   `edgeFade = smoothstep(1.0, 0.2, r)` multiplies both the RGB intensity and the
   alpha.
4. **Composite** — `alpha = inCircle · edgeFade`; background and disc are mixed
   by `alpha · 0.65`, so even the disc center is only 65% of the pattern over the
   ground.

Canvas is opaque (`alpha: false`), blending is enabled but the fragment alpha is
always 1, so blending never actually applies. `premultipliedAlpha: false`.

## 4. Motion law

At rest the interior rotates and slides at the shader rate: `u_speed = 1.3`
rad/s of pattern phase, with an additional radial rotation of `4.0 · |p|` rad
baked into the coordinate transform, so the outside of the disc shears faster
than the center. The height field decays with `damping = 0.913` per step and is
pulled to zero by `tension = 0.02`; the two-step recurrence decays as
`√damping ≈ 0.955` per frame, so a splat falls to ~4% after 1 s and ~0.3% after
2 s — visible for roughly a second, not longer. Pointer moves add splats
throttled to 8 ms (125 Hz); clicks add a 3.0-strength splat. A single
1.5-strength ripple is injected at the center 500 ms after mount, but by the
3.5 s poster its peak has fallen to ~3e-5 of the splat and is invisible — the
poster's central S is the display pattern, not the ripple.

## 5. Technique and math

The simulation runs on the CPU over a 256×256 grid, independent of the display
resolution.

**Wave step** (per interior cell, from the previous height `h_prev` and current
`h`):

- `h ← (h_prev[left] + h_prev[right] + h_prev[up] + h_prev[down]) / 2 − h`
- `h ← h · 0.913 + h_prev · (1 − 0.913)`
- `h ← h + (0 − h_prev) · 0.02`
- add `min(0.1, |v| · 0.01)` from the velocity field
- `h ← h · (1 − 0.01)`, clamped to ±2

This is deliberately **not** the standard leapfrog `2h − h_prev + c²∇²h`: the
neighbour average is taken from `previous` while `current` supplies the negative
term. Port it literally, including the buffer swap: each step writes the new
height into the buffer that then becomes `previous` for the next step. The
resulting two-step recurrence is stable at every wavenumber — its slowest decay
is `√damping ≈ 0.955` per frame — so the ±2 clamp is only a safety net for
extreme splats. Boundary rows and columns are zeroed every step (fixed edges).

**Vorticity.** `ω = 0.5 · (v_y(right) − v_y(left) − v_x(top) + v_x(bottom))` —
horizontal neighbours use the y-velocity and vertical neighbours the x-velocity,
i.e. the curl. The confinement force pushes velocity along the gradient of `|ω|`
**rotated 90°**: with `∇|ω| = (gx, gy)` and `L = |∇|ω|| + 1e-5`,
`forceX = (gy/L)·ω·0.2·0.1`, `forceY = (−gx/L)·ω·0.2·0.1`, each clamped to ±0.1
per step. Velocity itself dissipates 8% per step.

**Splat.** A disc of radius 8 cells: the height term
`cos((d / 8) · π/2) · (1 − d/8) · strength · (50000 / 100000)` is added to
`previous`, not `current`; velocity gets 0.2 times that along the radial
direction plus a tangent (`angle + π/2`) swirl of `min(0.3 · that, 0.1)`.
Position is normalized to the window, so splats land correctly under the pointer
regardless of canvas size.

**Pointer strength.** With `d` = CSS px moved since the last event and
`velocity = d / 8`, `velocityInfluence = min(velocity / 10, 2)`,
`base = min(d / 20, 1)`, the splat strength is
`base · velocityInfluence · 1.2 · (0.7 + 0.3 · random())`, applied at the pointer
plus ±1.5 px jitter; events closer than 8 ms or with `d ≤ 1` are dropped. Clicks
always use 3.0.

**Display field.** The height texture is sampled at screen UV and mapped through
the two-stage influence above (`waterInfluence`, then `totalWaterInfluence`).
Then, with `screenP = (2·FC − resolution)/resolution.y`:

- `p = screenP · 1.1`, then `θ = 4 · |p|` and
  `p = p · mat2(cos θ, −sin θ, sin θ, cos θ)` — a GLSL row-vector multiply, which
  rotates counter-clockwise by θ (matrix-times-vector rotates the other way and
  mirrors the poster),
- `l = |p| − 0.7 + totalWaterInfluence · 0.5`,
- `t = 1.3 · time + totalWaterInfluence · 2`,
- `y' = p.y + totalWaterInfluence · 0.3`,
- three copies of `0.5 + 0.5 tanh(0.1 / max(l/0.1, −l) − sin(l + y' · max(1, −l/0.1) + t + φ))`
  with φ = 0, 1, 2,

where tanh is the rational approximation `x(27 + x²)/(27 + 9x²)` clamped to ±1.
The `0.1 / max(l/0.1, −l)` term is singular at `l = 0` on both sides and is what
draws the bright S-shaped boundary through the middle; do not smooth it away.
Per-channel output is **not** a blend of three colours: the shader reads only
`u_color1.r = 1.0`, `u_color2.g = 0.95` and `u_color3.b = 1.0`, so
`o = (pattern₀, 0.95 · pattern₁, pattern₂) · intensity` with
`intensity = (0.7 + 0.4 · totalWaterInfluence) · edgeFade`. The near-white stops
combined with the 1-radian phase offsets produce the amber and cyan split.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| grid resolution | 256 | 128–384 | simulation detail vs CPU cost | M |
| damping | 0.913 | 0.88–0.97 | ripple lifetime and travel | H |
| tension | 0.02 | 0.005–0.05 | restoring pull to rest height | M |
| mouseIntensity | 1.2 | 0.2–3 | splat strength from pointer speed | H |
| clickIntensity | 3.0 | 1–6 | splat strength on click | M |
| rippleRadius | 8 cells | 3–16 | splat radius in grid cells | M |
| splatForce | 50000 | 20000–100000 | global splat amplitude divisor | H |
| vorticityInfluence | 0.2 | 0–0.6 | swirl confinement | M |
| velocityDissipation | 0.08 | 0.02–0.2 | how fast velocity dies | M |
| densityDissipation | 1.0 | 0–2 | height decay scaling (×0.01 per step) | L |
| waterStrength | 0.55 | 0.2–1.2 | height→display scale, applied twice (h·0.55, then ·0.55) | H |
| intensity | 0.7 + 0.4·w | — | base plus influence gain on the pattern, then × edgeFade | H |
| greenScale | 0.95 | — | the only non-unit colour-stop component used (`u_color2.g`) | L |
| animationSpeed | 1.3 | 0.4–2.5 | pattern phase rate in rad/s | M |
| disc radius | 0.9 | 0.5–1.2 | normalized circle radius | H |
| edge fade | 1.0 → 0.2 | — | radial darkening | M |
| composite alpha | 0.65 | 0.3–1 | disc opacity over the background | H |
| DPR | 1.5 | 1–2 | display resolution clamp | L |

## 7. Palette and color

Background `#05050D`. Pattern stops are effectively white with a blue bias —
`#FFFFFF`, `#E6F2FF`, `#CCE5FF` — but each channel receives a different phase,
so the visible result is amber `≈#C08A4A` and pale cyan `≈#9FC4CC` rather than
white. Only three scalar components are actually used — `u_color1.r` (1.0),
`u_color2.g` (0.95) and `u_color3.b` (1.0) — so the green channel sits 5% below
the other two. The disc is composited at 65% over the background, which keeps the
whole frame dim. No tonemapping; values are display sRGB.

## 8. Composition and camera

Orthographic, centered. The disc radius is 0.9 in units where the shorter axis
is 1.0, so it fills about 90% of the shorter dimension before the edge fade and
65% composite make it read smaller. On wide frames the disc stays circular and
the surround grows; on portrait frames it nearly touches top and bottom. The
pointer mapping uses window coordinates, not the canvas rect, for splats —
identical here because the canvas is full-viewport.

## 9. Randomness and seeds

`Math.random()` for splat jitter (±1.5 px) and a 0.7–1.0 intensity variation
per mouse splat. The simulation is otherwise deterministic, but pointer input
makes any run unique. The only scripted event is the center ripple at 500 ms; it
has decayed to invisibility by the 3.5 s poster, so the poster does not show it.

## 10. Performance budget

65,536 cells × 5 passes per frame on the CPU: velocity dissipation, vorticity,
vorticity force, wave update, boundary zeroing — roughly 300k simple operations,
plus a 256×256 float texture upload (256 KB) every frame. This is the most
CPU-heavy scene in the set. Display cost is one textured quad. Cut order:
grid to 192, vorticity influence to 0, then splat radius.

## 11. Host integration

Standard mount, plus three window listeners: resize, mousemove (throttled to
8 ms), click. The canvas rect is used only for pointer-to-canvas mapping; splats
normalize by window size. Teardown deletes program and texture and loses the
context. No external assets. Note the float texture path: `LUMINANCE`/`FLOAT`
upload requires the WebGL1 float-texture capability; on contexts without it the
texture must be uploaded as bytes after remapping the height to 0..255.

## 12. Failure modes and tells

- **Disc looks flat and static →** `waterStrength` too low, or the texture
  upload is failing silently (check the GL error state).
- **Ripples last forever or the field explodes →** `damping` above 0.97 or
  tension missing; the wave equation becomes unstable.
- **Field pins to ±2 and the surface turns into a mottled checkerboard →** the
  two-step buffers are swapped in the wrong order (the neighbour average must
  come from the state written last step, not the one being written now); the
  documented recurrence is stable and should not pin.
- **Disc is too bright or the amber/cyan split too strong →** the two-stage 0.55
  height scale or the `(0.7 + 0.4·w)·edgeFade` intensity was dropped; the green
  channel is also 0.95, not 1.0.
- **Whole frame is a bright wash →** composite alpha raised toward 1; the
  pattern is meant to sit at 65%.
- **Swirl is radial spokes instead of eddies →** vorticity force sign flipped.
- **Pointer ripples appear offset or mirrored →** v coordinate not flipped when
  converting from client space to grid space.
- **Pattern looks monochrome white →** the three per-channel phase offsets were
  collapsed to one.
- **Stutter at high resolution →** density scale applied per pixel instead of at
  the 256 grid resolution.

## 13. Tuning knobs

1. `waterStrength` — how strongly ripples deform the pattern (0.4–0.9).
2. `damping` — ripple lifetime (0.90–0.94).
3. `mouseIntensity` — interactive response (0.6–2.0).
4. `animationSpeed` — at-rest swirl rate (0.8–1.8).
5. `vorticityInfluence` — eddy tightness (0.1–0.4).

## 14. Verification checklist

- One centered, soft-edged disc on near-black; no hard circle.
- Interior shows both a warm and a cool region, not a single hue.
- The disc edge is feathered over ~10% of its radius.
- Peak luminance stays below pure white (the 0.65 composite).
- Moving the pointer leaves visible ripples that decay within ~1 s.
- No simulation grid artifacts (blockiness) at DPR 1.5.
- Compare with `assets/posters/fluid-ripples.jpg`: same disc size and same
  amber/cyan split; the exact swirl phase depends on time.

## 15. Porting notes

The simulation is plain typed arrays and ports directly. On WebGL2, upload as
`R32F` instead of `LUMINANCE` + `FLOAT`. In a worker, the sim can run off the
main thread, but the float texture upload must then happen on the main thread
from a shared buffer.
