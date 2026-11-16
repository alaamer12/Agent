---
family: canvas-a1
name: Noise-Advected Particles
renderer: canvas2d
members: [constellation-net, firefly-meadow, flow-field, smoke-wisps]
---

# Canvas A1 — Noise-Advected Particles

Four Canvas-2D scenes with the same core: a point population stepped along a
sampled simplex field every frame, where the look is decided by compositing.
Three repaint a fresh ground; one keeps a persistence veil. Three draw additive
light; one deliberately does not.

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| constellation-net | Constellation Net | 428 | L | spatial hash re-links pairs every frame into five alpha buckets; star and 4-point flare sprites; three depth bands |
| firefly-meadow | Firefly Meadow | 329 | M | per-mote blink with a 58% dark duty; three tinted 128 px halos plus a core disc |
| flow-field | Flow Field | 192 | S | the only persistence scene — a 3.5% fade veil, no ground repaint; 1.25 px strokes |
| smoke-wisps | Smoke Wisps | 334 | M | 3D curl noise; six puff sprites; `source-over` overlaps |

## Shared scaffold

All four are single-file components with one holder div at `absolute inset 0`,
pointer events disabled, containing a block canvas at full width and height. The
context is `getContext("2d", { alpha: false })`, so the scene always owns an
opaque ground and the host's `#000000 → #1A0033` gradient is never visible.

Resize reads `holder.offsetWidth/offsetHeight` with a `window.innerWidth/Height`
fallback, clamps `devicePixelRatio` to 1.5, floors the backing store to
`width·dpr` by `height·dpr`, writes the CSS size in pixels, sets the 2D
transform to `(dpr, 0, 0, dpr, 0, 0)`, then rebuilds the population. Resize is a
re-deal, not a scale: every position is re-randomized and the scene visibly
jumps. A passive window resize listener is the only host event.

Mount order is identical everywhere: create context, construct the noise
function, bake sprites (all but Flow Field), resize (which builds the
population), run a synchronous warmup of `drawFrame()` calls, start the FPS
meter, start the RAF loop. The loop body is `frame += 1`, then advance, then
draw. Teardown removes the listener, cancels the frame, stops the meter and
drops the context, noise function and arrays.

Warmup counts all matter: Flow Field 200, Constellation Net 120, Firefly Meadow
96, Smoke Wisps 300.

## Math primer

**Counts are area-derived and clamped**, never fixed:

- Constellation nodes: `clamp(round(A / 7600), 42, 460)` → 42 at 640x400 (34
  before the floor), 273 at 1920x1080.
- Constellation dust: `clamp(round(A / 2900), 90, 1500)` → 90 and 715.
- Firefly motes: `clamp(round(A / 5200), 26, 320)` → 49 and 320.
- Smoke puffs: `clamp(round(A / 3000), 80, 460)` → 85 and 460.
- Flow strokes: `clamp(round(A / 1500), 220, 2600)` → 220 and 1382.

**Lengths scale with the square root of area.** Constellation's link distance is
`1.24·√(A/n)`; Firefly's halo and Smoke's base radius are `√A` times a fraction;
Flow's stroke is constant. At 1080p — 8.1× the area — elements are 2.846×
larger, so the relative scale holds and only the population count rises.

**Advection** is a first-order Euler step, `p ← p + v(p, t)`, one step per
frame, with `v` sampled at the particle's own position. No path integration and
no cached velocity: the field is re-evaluated every frame, which is why the
motion never drifts out of equilibrium. Constellation and Firefly blend a fixed
personal heading with a noise offset; Smoke takes both components from the curl.

**Curl** is a 90° rotation of the noise gradient: `vx = ∂n/∂y · s`,
`vy = −∂n/∂x · s`, with the gradient taken by central difference over ±ε. That
is divergence-free, so the field has no sources or sinks and the population
cannot pile into a point. The scalar's third axis advances by a per-frame
evolution term, so the field changes shape rather than sliding.

**Envelopes** are the second shared language. Flow uses a half-sine over
lifetime; Constellation a two-sine pulse that never reaches zero; Firefly a
strike-then-decay over a 42% duty window; Smoke `sin(π·age)^1.25`.

## Shared helpers

**Radial sprite baking.** A square offscreen canvas, a radial gradient at the
centre with radius exactly half the sprite, final stop alpha 0. Constellation
64 px; Firefly halo 128 px; Smoke puffs 128 px. Baked once at mount, never per
particle.

**Torus wrap.** Every scene wraps by adding or subtracting `size + 2·pad` when a
particle leaves the padded box, so no particle is respawned for leaving the frame
and the population stays constant. Constellation uses a fixed 24 px pad; Firefly
and Smoke pad by their own halo or radius. Flow Field respawns instead.

**Additive bracketing.** The `lighter` composite is set immediately before the
light pass and reset to `source-over` after it, every frame. A pass that forgets
the reset (vignette, veil) becomes additive and the frame loses its corners.

**Area-based rebuild.** Building functions recompute the count and re-seed the
whole array; nothing is preserved across resize.

## Conventions

Space is CSS pixels, origin top-left, y down. Angles are radians from +x and
increase clockwise on screen. Time is the frame counter: per-second values are
frame values times 60. Noise is 2D simplex (3D for Smoke) in the gradient
variant, returning −1..1. Colour is display sRGB, 8-bit, authored as hex or
`rgba`/`hsla` strings. All four repaint an opaque ground or veil every frame;
none accumulates beyond one frame except Flow Field's fade.

## Variation map

| if you want | change |
| --- | --- |
| more, smaller stars | raise Constellation `nodeArea`; lower `starGlow` |
| a tighter, more legible net | lower Constellation `linkSpan` toward 1.15 |
| a busier meadow | lower Firefly `period` range or raise `duty` |
| longer, more tangled trails | lower Flow Field `fade` |
| taller, faster smoke | raise Smoke `riseShare` or `swirl` |

## Porting

Any 2D canvas works. Substitute a simplex that returns −1..1 and stays
continuous; blocky value noise shows up as visible direction steps. `lighter` is
the exact additive composite in every browser. Where Path2D or offscreen canvases
are unavailable, batch by alpha bucket and bake sprites into an `ImageData`.
Never drive the frame counter from wall-clock time: pulses, blink periods and
lifetimes are authored in frames.

## Failure modes

- **Frame turns milky or white** → too much alpha per additive mark, or Smoke's
  puffs drawn with `lighter` instead of `source-over`.
- **Particles bunch and stall** → velocity cached instead of resampled, or curl
  built from two independent noise calls instead of one rotated gradient.
- **Empty first second** → warmup skipped; each scene has its own count.
- **Population drifts to one edge** → wrap pad missing, so escapees sample
  off-canvas noise forever.
- **Everything one brightness** → depth not applied to size and alpha.
- **Faint square halos** → last gradient stop above alpha 0, or sprite drawn
  larger than its baked square.
- **Corners never darken** → vignette inherited the additive composite.

## Verification heuristics

- Population count matches the area formula at 640x400 and 1920x1080.
- Mean frame luminance between 2% and 12%; no large white region.
- No particle pops at an edge; motion is continuous frame to frame.
- Overlaps brighten in the additive scenes and converge on mid grey in Smoke.
- Background is never pure black; each scene has a coloured ground or field.
- After warmup the density is at steady state and does not keep filling.
