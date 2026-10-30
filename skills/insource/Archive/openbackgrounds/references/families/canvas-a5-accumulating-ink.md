---
family: canvas-a5
name: Accumulating Ink
renderer: canvas2d
members: [harmonograph-trails, pulse-radar]
---

# Canvas A5 — Accumulating Ink

Two scenes whose image is the framebuffer's history, not the current frame.
Neither clears; both erode the previous frame with a translucent fill and then
deposit new light additively. The retained objects (pens, rings, blips) are
emitters; the picture lives in the pixels.

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| harmonograph-trails | Harmonograph Trails | 234 | M | four damped Lissajous pens, 0.02 veil, 340-frame warmup, rosette accumulates |
| pulse-radar | Pulse Radar | 420 | L | 0.1 veil, aged ring array, 26-step sweep wedge, charge-per-blip state machine |

## Shared scaffold

Both are single-file components: holder div at `absolute inset 0` with pointer
events off, block canvas at full size, `getContext("2d", { alpha: false })`.
Resize reads `offsetWidth/offsetHeight` with a `window.innerWidth/Height`
fallback, clamps `devicePixelRatio` to 1.5, floors the backing store, writes CSS
size, sets the transform to `(dpr, 0, 0, dpr, 0, 0)`, then rebuilds scene state.
A passive window resize listener is the only host event.

The loop is `tick, draw, requestAnimationFrame`. Drawing always begins by
eroding: one full-rect fill with alpha well below 1. Nothing else clears the
surface, at mount or on resize — mount and resize both paint an opaque ground
and then restart the accumulation. Warmup runs the real draw function
synchronously before the first visible frame, 340 frames for the harmonograph
and 180 for the radar, so both open at equilibrium.

## Math primer

**Damped Lissajous.** A pen at time `t` (units, not seconds) is
`x = cx + ox + (A·e^(−dt)·sin(2π·fx·t + φx))·cosθ − (A·q·e^(−dt)·sin(2π·fy·t + φy))·sinθ`
and the y term is the same pair rotated by `θ`, with `q` the squash factor.
`t` advances `segment × segments` = `(1/60)·3` = 0.05 per frame, so one time unit
is 20 frames. `fx = ratio_x·0.62·(1 ± 0.0075)`, `fy` likewise; the detune is what
prevents exact closure, so successive passes land a fraction of a pixel apart
and the rosette thickens into a figure instead of a single line.

**Radar sweep.** `sweep = (frame·0.0125) mod 2π`: 0.75 rad/s, one revolution
every 502.65 frames (8.378 s). The wedge spans 1.15 rad behind the leading edge
in 26 slices; slice `i` gets gain `(1 − i/26)^2.3`. A blip at angle `α` is
crossed when `((α − from) mod 2π) ≤ ((to − from) mod 2π)`.

**Rings.** Radius `r = (age/250)·maxR`, one ring emitted every 42 frames, dead
at 251. `maxR = 0.56·hypot(W, H)` = 422.64 px at 640x400, 1233.63 px at
1920x1080, so a ring's last 10.7% of life is entirely outside the frame.

**Charge.** `charge ← charge·0.9925` per frame; set to 1 when the sweep crosses;
raised to `0.3·ringWeight` when a ring's radius passes within 3.2 px. Blips are
not drawn below 0.03 — the reservoir has no floor deposit.

## Shared helpers

**The veil.** One `fillRect` in `source-over` with a fixed rgba, at 0.02
(harmonograph) and 0.1 (radar). The veil colour is not black: `rgba(5, 4, 10)`
and `rgba(4, 12, 10)` respectively, so the settled ground carries the scene's
tint. Steady-state gain for anything deposited every frame is `1/alpha` — 50×
for the harmonograph, 10× for the radar — and the settled colour is the veil
colour itself, not the CSS ground.

**Composite discipline.** Moving light is bracketed by
`lighter` … `source-over`. Fixed marks are drawn outside that bracket: the radar
grid, origin dot and bezel shadow; the harmonograph ground is mount-only. A
standing element inside the additive bracket would be re-deposited every frame
and amplified by the reservoir until it burns out.

**Grounds.** The harmonograph paints a diagonal gradient (top-left `#080610`,
mid `#05040c`, bottom-right `#090711`) once at mount and after each resize. The
radar fills `#020605` on resize only.

**Blip sprite.** One 64x64 radial glow baked at mount: `rgba(198,255,232,0.95)`
at the centre, `rgba(96,255,208,0.5)` at 0.14, `rgba(34,214,168,0.14)` at 0.4,
`rgba(18,140,118,0.03)` at 0.72, transparent at 1. Stamped at a diameter of
`size·(5.2 + charge·7.4)` px.

## Conventions

CSS pixels, y down, angles in radians clockwise from +x. Time is the frame
counter; per-second rates assume 60 fps. Colour is display sRGB. A pen's alpha
is per-stroke peak; a blip's alpha is per-frame deposit. Both scenes assume they
own the canvas for their lifetime; resize is destructive, not continuous.

## Variation map

| if you want | change |
| --- | --- |
| longer trails either scene | halve the veil alpha (0.01 / 0.05) and re-check white clipping |
| a denser rosette | raise `pens` to 5–6, not `baseAlpha` |
| a faster figure | raise `baseFreq`; keep integer ratio pairs |
| more radar returns | lower `blipArea` toward 9000; watch the 190 cap |
| longer radar comet tail | lower `fade` to 0.06 and raise `sweepAlpha` slightly |

## Porting

Framebuffer persistence needs an offscreen or backbuffer of identical size that
is never cleared — a full-screen quad with a feedback texture in GL, or a
`CanvasTexture` in three.js. Do not emulate it with a stack of retained strokes:
the harmonograph retraces every 32.26 frames and the radar deposits per frame,
so retained geometry either explodes in count or looks wrong. Under GL, clear
with a translucent quad rather than `clearColor`, which has no alpha ramp.
Resize must recreate the buffer and accept the loss of history.

## Failure modes

- **Everything glows and never fades →** veil skipped or alpha too low; the
  reservoir gain is 50× / 10×, so small deposits saturate in seconds.
- **Ground turns flat grey →** veil is pure black while the ground is tinted;
  the settled colour must equal the veil colour.
- **Grid burns a bright hole in the radar →** grid drawn inside the `lighter`
  bracket.
- **Rings look like static circles →** the echo ring at 0.974 radius is missing
  or the ring alpha does not fall with `(1 − t)^1.15`.
- **Rosette is a single thin line →** detune removed, so the pen laps exactly.
- **Pens freeze at the centre →** respawn threshold below the reachable decay
  or the decay never reaches 0.1 within the warmup.
- **Resize leaves old ink stretched →** backing store resized without an opaque
  repaint and a state rebuild.

## Verification heuristics

- Ground settles to the veil tint, never pure black, and never greys upward.
- Harmonograph strokes fall to 8.9% of their deposit after 2 s; no permanent
  bright knots.
- Radar sweep completes a revolution in 8.38 s and leaves a wedge-shaped tail
  spanning 1.15 rad (92 frames of travel) behind the leading edge.
- Radar rings are concentric, evenly spaced in time, and die before the canvas
  corner is reached twice.
- No element is brighter than the poster's core without saturating to white.
