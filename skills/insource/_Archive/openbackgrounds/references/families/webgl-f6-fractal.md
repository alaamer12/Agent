---
family: webgl-f6
name: Escape-time fractal
renderer: webgl1
members: [fractal-drift]
---

# Escape-time fractal

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| `fractal-drift` | Fractal Drift | 314 | M | Julia set with tracked derivative; distance-estimate glow and smooth-iteration contour bands |

## Shared scaffold

One fullscreen pass over an oversized triangle, no depth, no blending, no
clearing. The vertex stage only forwards a clip-space position; everything
happens per fragment. Coordinates are centered and divided by the shorter axis
so the effect is aspect-independent. A single `u_time` in seconds drives every
phase; pointer position is an optional small offset. The context is created
with `alpha: false`, `antialias: false`, `depth: false`.

The JS side is the standard raw-WebGL lifecycle: compile and link at mount,
bind uniform locations once, upload one static triangle buffer, resize the
drawing buffer with a DPR clamp, upload uniforms and draw each frame, then
delete the buffer and program and lose the context on teardown.

## Math primer

**Julia iteration.** For a fixed complex parameter `c`, iterate `z ← z² + c`
from the pixel coordinate `z₀ = p`. A pixel belongs to the filled Julia set if
it never escapes. In practice you cap the iteration count and test a bailout
radius; the count and the escape value carry the visual information.

**Derivative tracking.** Differentiate the iteration alongside:
`d ← 2 z d + 1`, `d₀ = 1`. Together with the escape value this yields the
distance estimate `de = |z| ln|z| / |d|`, the approximate distance from the
pixel to the set. Inverse `de` is the glow; it is what separates a smooth
fractal from a noisy one.

**Smooth iteration.** `mu = iter + 1 − log₂(ln|z| / ln 2)` removes the integer
banding of raw iteration counts. Modulating a sine by `mu` gives continuously
moving contours instead of steps.

**Parameter path.** Choosing `c` on a small circle around 0.7885 keeps the set
connected and filamentary while the topology changes continuously. A closed
path (plus a small secondary wobble) guarantees the shape keeps morphing but
never degenerates.

**Palette by escape.** Color is composed from the contour phase, the glow, a
hashed dust term, and a ground color, then tonemapped exponentially. There is
no iteration-index palette; the two-hue split (cool ring / warm ring) is what
makes the frame read as depth rather than heat.

## Shared helpers

- `hash21(p)` — cheap 2D hash in [0,1]; used for dust and speckle fields. Any
  sin-fract or dot-fract hash works; the distribution must be uniform enough
  that a high power isolates a few cells.
- Exponential tonemap `1 − exp(−k·col)` — the standard way to keep additive
  near-white cores from clipping.
- Radial vignette via `smoothstep` on normalized radius.
- Domain rotation by a 2×2 matrix; in GLSL the rotation matrix is built inline
  from cos/sin of the time-scaled angle.

## Conventions

- Complex plane units: the shorter viewport axis spans 1.0.
- Time in seconds; angles in radians.
- Bailout is compared squared (`|z|²`), radius written squared.
- All color math is display sRGB; no linear conversion.

## Variation map

Only one member. The available axes are the parameter path (circle radius,
speed, wobble), the zoom and its breathing, the glow falloff, and the contour
frequency mix. Changing the parameter radius is the highest-leverage edit: it
moves between dust, dendrites, and near-circular lobes.

## Porting

Any shader language works; only `gl_FragColor`, `attribute`, and `varying` need
renaming in WebGL2/GLSL 3.00. On the CPU this is a per-pixel loop and will be
slow at full resolution — precompute at quarter resolution and upscale if a
non-GPU target is required. Keep highp precision; mediump loses the distance
estimate at zoom.

## Failure modes

- **Flat color blobs** — parameter inside the main cardioid, or glow scalar too
  low.
- **Hard bands instead of contours** — raw iteration count used instead of the
  smooth count.
- **Sparkling aliasing at the boundary** — antialiasing disabled plus low DPR;
  the soft tonemap is doing the work, so raise DPR before enabling MSAA.
- **Dust looks like a regular grid** — hash applied to screen pixels instead of
  a rotated or jittered cell coordinate.
- **No depth at all** — contour term removed or its frequency collapsed.

## Verification heuristics

The set boundary must be the brightest region and the interior the darkest.
Contour spacing should shrink monotonically toward the boundary. Two hues, not
a rainbow. Successive frames change slowly (sub-pixel drift at 1 s intervals).
