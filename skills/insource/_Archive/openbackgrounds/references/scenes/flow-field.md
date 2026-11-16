---
id: flow-field
name: Flow Field
family: canvas-a1
renderer: canvas2d
poster: assets/posters/flow-field.jpg
complexity: S
source_lines: 192
dpr_max: 1.5
deps: [simplex-noise]
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# Flow Field

## 1. Identity

Hundreds of luminous cyan-to-magenta particles drift along a slowly sliding
simplex-noise field, leaving soft curved streaks on near-black.

## 2. Perceived look

Smooth, low-contrast filaments on a black-violet ground. Density is high but
strokes are thin and semi-transparent, so the frame reads as layered smoke
rather than a solid mass. Edges are soft; every stroke fades in and out, so no
line has a hard start or end. There is no focal point — the eye follows curve
directions. At 640x400 there are 220 particles, the clamp floor of the count
formula. The persistence veil fades each stroke over roughly 1.5–2 s, so many
hundreds of segments overlap at any moment and the longest arcs run 200–350 px.
Density looks highest where the field curls and particles bunch — in the poster
that is the centre-right, where the strands gather into a loose knot; the
centre-left carries broader, fainter sweeps.

## 3. Frame anatomy

1. **Backdrop** — one linear gradient painted once at mount and again after each
resize, running from top-left `#04070f` through `#080313` at the midpoint to
`#03050c` at bottom-right. Fully opaque.
2. **Fade veil** — every frame, a full-rect fill of `rgba(3, 5, 12, 0.035)`
   in `source-over`. This is the persistence layer: it never fully clears.
3. **Strokes** — one 1.25 px round-capped segment per particle per frame, drawn
   in `lighter` (additive), then the composite is restored to `source-over`.

Canvas has no alpha (`getContext("2d", { alpha: false })`), so the backdrop is
the scene's own and no host gradient shows through.

## 4. Motion law

Each particle advances 2.6 px per frame times a per-particle weight in
0.7–1.35, giving 109–211 px/s at 60 fps. Direction comes from the noise field,
not from frame history. The field itself slides along the x-sampling axis by
0.0022 noise units per frame (section 5). One noise unit spans about 1111 CSS
px, so that offset is equivalent to 2.44 px per frame, or 146 px/s at 60 fps —
close to the particles' own speed, which is why they trace long coherent paths
instead of morphing in place. Particle lifetime is 90–220 frames (1.5–3.7 s),
but the visible trail is shorter: the veil halves a stroke's alpha every ~20
frames, so even a bright segment fades out in about 1.5 s. There is no loop;
motion is open-ended.

## 5. Technique and math

Per frame:

- `angle = noise2D(x * 0.0009 + frame * 0.0022, y * 0.0009) * 2π * 0.35`
- `x += cos(angle) * 2.6 * weight`, `y += sin(angle) * 2.6 * weight`

`noise2D` is 2D simplex noise in the gradient-noise variant, returning −1..1.
`frame` is a monotonically increasing integer and the offset is added to the
first argument only, so the field slides along one sampling axis rather than
morphing. `0.0009` is the sampling scale in inverse pixels: one noise cell spans
about 1111 px, so the field varies slowly across the viewport and strokes stay
long. The same scale makes the 0.0022-per-frame offset equivalent to 2.44 px of
spatial shift per frame.

The `2π * 0.35` gain maps the −1..1 noise range to ±2.199 rad (**±126°**; the
common misreading `π * 0.35` would give ±1.0996 rad, ±63°). The range
deliberately exceeds ±90°, so a
particle can turn back toward the upper left as well as forward, which is what
produces the S-curves and long sweeping arcs in the poster. Raise `turns` past
about 0.5 and directions wrap repeatedly inside one noise cell: particles orbit
in place and the frame turns to tangled wire. This is the single most important
constant in the scene.

Particle alpha is `sin(min(1, age / life) * π) * 0.62 * weight`, a half-sine
envelope: fade-in over the first half of life, symmetric fade-out, zero at both
ends. Segments with alpha ≤ 0.012 are skipped. The stroke colour is re-evaluated
per segment from the particle's current life fraction (section 7).

Respawn occurs when `age > life` or the particle is more than 30 px outside the
frame. A respawn re-randomizes position, hue, weight, and life. The backing
store is scaled by DPR with a `setTransform(dpr, 0, 0, dpr, 0, 0)` call, so
every number above is CSS px.

Warmup runs the same full draw loop 200 times before the first RAF: `frame`
therefore starts at 200, particles are already aged and respawned, and the
persistence layer is at equilibrium on the first visible frame.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| maxDpr | 1.5 | 1–2 | device pixel ratio clamp | L |
| density | 1500 | 700–3000 | area per particle; count = area / density | H |
| speed | 2.6 | 1.2–4 | px per frame before weight; streak length | H |
| noiseScale | 0.0009 | 0.0004–0.0016 | inverse cell size; lower = longer smoother curves | H |
| drift | 0.0022 | 0–0.006 | field translation per frame; pattern breathing | M |
| fade | 0.035 | 0.015–0.08 | persistence veil opacity; lower = longer trails | H |
| lineWidth | 1.25 | 0.8–2.2 | stroke width in CSS px | M |
| baseAlpha | 0.62 | 0.35–0.9 | peak stroke opacity before weight (effective peak up to 0.84) | M |
| life | [90, 220] frames | 60–400 | lifetime range | M |
| hueRange | [186, 322] | any two hues | cyan→blue→violet→magenta span | H |
| turns | 0.35 | 0.15–0.5 | noise→radian gain (×2π); above ~0.5 particles loop in place | H |
| warmup | 200 frames | 60–400 | pre-roll before first visible frame | M |

Particle count is `clamp(round(width * height / 1500), 220, 2600)`: 220 at
640x400 (the clamp floor), 1382 at 1920x1080.

## 7. Palette and color

Backdrop gradient: `#04070f` → `#080313` → `#03050c`, near-black violet. The
fade veil is `#03050c` at 3.5 percent per frame, so within a few seconds the
gradient converges to flat `#03050c`; the gradient shows mainly on the first
frames and just after a resize.

Strokes: `hsla(hue, 84%, 60 + 14 * (age / life)%, alpha)` with hue uniform in
186–322 (cyan 186, azure 210, indigo 250, violet 280, magenta 322). Lightness
rises monotonically with age while alpha follows the half-sine envelope, so the
newest segment is not necessarily the brightest — mid-life segments are the
strongest. Additive blending pushes overlapping strokes toward white-cyan. All
values are display sRGB.

## 8. Composition and camera

Full-bleed 2D, no camera. Uniform density per unit area, so the framing works at
any aspect ratio. The noise is sampled in CSS px with the same scale on both
axes, so the field is isotropic on screen at every aspect ratio — only the size
of the window onto it changes, and a wide frame simply shows more of the same
flow. No safe margins; strokes are allowed to run off the edges and respawn on
exit. Portrait frames look denser per unit width but keep the same count per
unit area.

## 9. Randomness and seeds

`Math.random()` for all quantities — no seed. Any seed produces the same
distribution: position uniform in the viewport, life uniform 90–220, hue
uniform 186–322, weight uniform 0.7–1.35. Spawn sets age 0, and each frame
increments age before alpha is evaluated, so a stroke's first drawn segment is
at age 1 and nearly transparent. The noise field itself is unseeded
(simplex permutation table is random per construction), so two runs at the same
t differ in every curve while matching in density and hue. Warmup of 200 frames is
mandatory before the first paint, otherwise the scene opens on a near-empty
black frame and only reaches equilibrium after several seconds. The warmup calls
the same `drawFrame` routine as the live loop, so the frame counter and every
particle age advance by 200 before the first visible frame.

## 10. Performance budget

220–2600 particles, one noise sample and one line segment each per frame; no
per-frame allocation except on respawn. Fill cost is dominated by the
full-screen fade rect. DPR capped at 1.5. Runs comfortably above 60 fps on a
laptop iGPU at 640x400 and holds ~60 fps at 1080p. Cut order: particle count,
then DPR, then trail length (higher fade).

## 11. Host integration

Standard contract: mount into a positioned full-bleed container, size from
`offsetWidth/offsetHeight` with a fallback to `window.innerWidth/Height`, listen
to window resize passively, prime 200 frames synchronously, then start the RAF.

Resize is a hard reset: it re-sizes the backing store, repaints the gradient
backdrop, and respawns every particle at age 0, but does **not** reset the frame
counter and does **not** re-run the warmup. The first frames after a resize are
therefore thin and the trail takes ~1.5 s to rebuild; do not read that as a bug.

Teardown cancels the RAF, removes the resize listener, and drops the context,
noise function, and particle array. No external assets.

## 12. Failure modes and tells

- **Tight knotted loops instead of long strokes →** `turns` above about 0.5, so
  a direction wraps inside one noise cell. The source uses 0.35 (±126°); drop
  toward 0.25 for straighter flow.
- **Every particle drifts the same way, no S-curves →** the gain was read as
  ±63° instead of ±126°; check that the multiplier is `2π · 0.35` (= 2.199 rad),
  not `π · 0.35` (= 1.0996 rad).
- **Near-empty frame that slowly fills →** warmup skipped. Prime at least 150
  frames.
- **Strokes vanish too fast / no glow →** `fade` too high. Lower toward 0.02.
- **Frame turns into a flat milky wash →** `baseAlpha` or `lineWidth` too high
  for the particle count; reduce one before the other.
- **Everything one hue →** `hueRange` collapsed or hue re-randomized on every
  frame instead of on respawn.
- **Particles frozen at edges →** respawn margin missing, so escaped particles
  keep sampling off-screen noise.
- **Pattern jumps on resize →** backdrop not repainted or particles not
  rebuilt after the canvas resize.

## 13. Tuning knobs

1. `turns` — raise for curl, lower for long sweeping strokes (0.15–0.5).
2. `fade` — lower for longer trails and more glow (0.02–0.06).
3. `speed` — longer, faster strokes (1.5–3.5).
4. `density` — raise for a finer mesh, lower for bolder strokes (800–2500).
5. `hueRange` — narrow for a monochrome cyan or violet field.

## 14. Verification checklist

- Background reads as near-black with a faint violet cast, never pure #000.
- Dominant hues between 186 and 322; no green or red strokes.
- Strokes are smooth arcs of 40+ px, not loops under 20 px.
- No hard line starts/ends; every stroke fades at both ends.
- Coverage grows to a steady state by t = 2 s and never washes out.
- Motion is continuous with no per-frame flicker or jumping.
- Compare to `assets/posters/flow-field.jpg`: same hue band, same density
  class, same stroke scale. Exact particle positions will differ.

## 15. Porting notes

Any 2D canvas works. Substitute a simplex implementation that returns −1..1 and
preserve the permutation randomness (a deterministic seed is fine, but the
distribution must stay isotropic). If the framework lacks an additive composite,
`globalCompositeOperation = "lighter"` is the exact equivalent in every
browser; on an offscreen buffer, apply it before blitting.
