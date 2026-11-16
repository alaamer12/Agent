---
family: canvas-a6
name: Film Emulation
renderer: canvas2d
members: [analog-grain]
---

# Canvas A6 — Film Emulation

Scenes that dress an almost-empty frame as photographed film: a tinted ground,
a wandering warm lamp, one or two rolling gate bands, an exposure flicker, a
vignette, and a grain layer stamped on top. Nothing in the frame moves in
space; all the life is in luminance and texture.

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| analog-grain | Analog Grain | 291 | M | 6 baked 232 px grain tiles, 2 gate bands on 940/1610 periods, 3-sine flicker |

## Shared scaffold

Canvas 2D, opaque context, standard holder and DPR clamp of 1.5. Resize floors
the backing store, writes CSS size, sets the transform, and disables image
smoothing — the only scene-level setting applied on resize rather than per
frame. The grain tiles are baked once at mount, before the first resize, and
never rebuilt; they are size-independent because the tile is stamped in CSS
pixels.

Mount order: context, bake tiles, resize, 46 synchronous frames of warmup,
listener, FPS meter, RAF. Warmup exists only because the gate bands are
off-frame at t = 0; nothing accumulates, so 46 frames is a phase offset, not an
equilibrium. Teardown cancels the frame, removes the listener, drops the context
and the tile array.

The frame is fully repainted in a fixed order and never reads its own history.

## Math primer

**Tile synthesis.** Six 232x232 ImageData tiles. A coarse 78x78 lattice of
random values in −1..1 is nearest-sampled in 3 px blocks; per texel
`v = clamp(0.46·coarse + 0.56·(2·rand − 1), −1, 1)`. Positive v writes warm
silver `rgb(255,243,219)`, negative writes base `rgb(7,5,9)`, and both share
alpha `round(|v|^1.55 · 0.4 · 255)` = 0..102. The 1.55 gamma keeps most grains
faint and a minority bright; linear alpha reads as television snow. The two
terms differ by 0.1, so clumps stay 3 px wide before the fine term breaks them.

**Stamping.** Per frame an integer offset uniform in 0..231 is drawn, then 232 px
tiles are stamped from (−ox, −oy), each cell picking one of the six variants, all
at alpha 0.62: 6–12 stamps at 640x400, 45–60 at 1920x1080. Offsets and variants
re-roll every frame, so the speckle boils with no per-pixel work.

**Ground.** Linear gradient along (0,0)→(0.22W,H) with three HSL stops lifted by
`3.4·breathe` (and 2.38, 1.19 for the lower stops), where
`breathe = 0.5 + 0.5·sin(frame·0.0016)`, period 3927 frames (65.45 s).

**Gate bands.** For direction `d = (cos a, sin a)`, the projected axis is
`u = d·p`; corner projections give uMin..uMax. With span `= min(W,H)·width`, the
centre is
`u = uMin − span + ((frame mod period)/period)·(uMax − uMin + 2·span) + phase`,
and a gradient from `d·(u − span)` to `d·(u + span)` fills the frame: a slab
2·span wide. A: 940 frames, width 0.5, alpha 0.085, angle −0.36. B: 1610 frames,
width 0.86, alpha 0.05, angle 0.52, phase 0.4·min(W,H). The periods share no
small factor, so the highlights never lap.

**Flicker.** Three detuned sines at 0.21, 0.37 and 1.31 rad/frame, weights 0.5,
0.3, 0.2, give a wobble in −1..1; the warm full-frame fill is
`0.026·(0.55 + 0.45·(0.5 + 0.5·wobble))`, alpha 0.0143..0.026. At 60 fps the
components run at 2.0, 3.5 and 12.5 Hz.

**Exposure order.** Ground, then lamp, band A, band B and flicker all in
`lighter`, then vignette and grain in `source-over` at grain alpha 0.62. The
vignette precedes the grain so corners keep texture.

## Shared helpers

**Tile baking.** One canvas per variant, `createImageData`, `putImageData`; each
is stamped at its native 232 CSS px, so no per-stamp resize happens. Regenerate
them only on context loss.

**Projected slab gradient.** The gate band needs no path: because the band is a
slab in a linear projection, two gradient endpoints derived from the corner
projection cover the frame correctly at any aspect ratio.

**Additive warm stack.** Lamp, both bands and flicker all add into the same
buffer, so overlap sums rather than replaces; the composite mode is owned by the
caller and reset before the vignette.

**Radial falloffs.** Lamp: `hypot(W,H)·0.62` at
`(0.5W + 0.32W·sin t, 0.46H + 0.28H·sin(1.37t + 2.1))`, period 5712 frames on
x. Vignette: `hypot(W,H)·0.68` from `(0.5W, 0.48H)`, transparent at 0.3r,
0.16 at 0.62r, 0.8 at r.

## Conventions

CSS pixels, origin top-left, y down, angles in radians. Frame counter is time.
Colour is display sRGB and compositing happens in sRGB; no linear-light pass,
no tone curve. "Gate" here means the light band across the film gate, not a
geometric weave — no layer in the original is displaced.

## Variation map

| if you want | change |
| --- | --- |
| coarser, more visible grain | raise `grainTile` to 320 and `grainPeak` to 0.5 |
| finer, subtler grain | lower `grainAlpha` to 0.4 before touching tile size |
| a darker, cooler stock | lower the ground lightness and shift stop 1 hue from 33 to 20 |
| slower light leak | raise both gate periods together, keeping their ratio off 2:1 |
| stronger flicker | raise `flickerAlpha`, not the sine weights |

## Porting

Bake tiles into textures and stamp quads; do not port the grain as a per-fragment
noise function, which reintroduces the cost the tiles avoid. Keep nearest
sampling and integer CSS offsets — a half-pixel offset turns 1 px grains into
2 px smears. Additive blends must be real additive (`lighter` / `ONE, ONE`), and
the grain must be composited after the vignette. If the target pipeline is
linear-light, convert the ground and warm fills to linear first; adding sRGB
values in linear space shifts the whole frame yellow.

## Failure modes

- **Grain reads as TV snow →** alpha gamma dropped to 1.0; restore 1.55 so the
  histogram stays bottom-heavy.
- **Grain looks like a static screen door →** offsets not re-rolled per frame,
  or one tile reused for every cell.
- **Visible rectangular patches →** tiles drawn larger than 232 px or with
  smoothing enabled.
- **Frame is flat and lifeless →** gate bands omitted or both phases in
  lockstep, so the highlight never crosses.
- **Exposure pumps like a sine →** single-sine flicker; use three detuned
  components.
- **Corners turn to flat black →** grain drawn before the vignette, or the
  vignette painted after the grain.

## Verification heuristics

- Mean luminance stays between 4% and 12%; the frame is dark but never black.
- Grain is visible at 1:1 as 1–2 px speckle with even spatial density.
- A soft diagonal band crosses the frame every 15.7 s and a second every 26.8 s.
- No frame-to-frame colour shift beyond ±2% from the flicker.
- Corners are darker than the centre by about 35% and still grainy.
