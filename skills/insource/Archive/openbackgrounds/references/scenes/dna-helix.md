---
id: dna-helix
name: DNA Helix
family: webgl-f3
renderer: webgl1
poster: assets/posters/dna-helix.jpg
complexity: XL
source_lines: 616
dpr_max: 2
deps: []
poster_capture: 640x400 @ dpr 1, 3.5 s warm
---

# DNA Helix

## 1. Identity

Two intertwined strands of glowing blue-white points spiral up the frame like a
DNA molecule, each strand a loose ribbon of particles rather than a line.

## 2. Perceived look

Soft, luminous, slightly out of focus. Every strand is a chain of fuzzy dots —
about 6–14 px on a 400 px-tall frame — clumped into segment bands, so the helix
reads as beaded rather than smooth. One strand is cyan-blue, the other more
violet. Dots near the vertical middle are brighter and larger; the alpha ramp
dims the ends, and at 640x400 the column overruns the frame, so both ends are
cropped mid-strand. Background is black-navy. There is no axis line and no
rungs; the impression of a double helix comes from the two phase-shifted sine
columns crossing repeatedly.

## 3. Frame anatomy

One draw call of `POINTS` from three buffers (position updated per frame, color
uploaded once, size static).

1. **Background** — not drawn; the canvas is transparent (`alpha: true`,
   `premultipliedAlpha: false`) and cleared to `(0, 0, 0, 0)`. The host's
   `#000000 → #1A0033` gradient is the visible backdrop.
2. **Particle strands** — 3840 soft point sprites, additive blending
   (`SRC_ALPHA, ONE`), depth test off, depth write off, sizes 1 px up.

No vignette, no fog, no tone map. Transparency plus additive blending means
overlaps brighten and the host gradient supplies the darkness.

## 4. Motion law

The helix rotates about its vertical axis at 0.12 rad/s (52.4 s per turn). The
cross-section of each strand swirls at 0.2 rad/s, so individual particles orbit
their strand center slowly. A band term travels along the column at 0.35 rad/s
(18.0 s per cycle), bunching particles into bright segments; a drift term
oscillates at 0.4 rad/s radially and 0.25 rad/s vertically. The helix rotation
alone repeats every 52.4 s, but 0.12, 0.2, 0.35, 0.4 and 0.25 rad/s are
incommensurate, so the full particle pattern does not loop on that period — it is
open-ended. The pointer
(normalized over the window, smoothed 0.08/frame) shifts the eye ±0.6 units and
the height ±0.36, and leaves the pointer returning home on `pointerleave`.

## 5. Technique and math

**Layout.** 160 segments × 2 strands × 12 points = 3840 particles. Each particle
stores `(t, strandPhase, crossAngle, crossRadius, wobble, drift)` where
`t = i/159`, `strandPhase = 0` or `π`, and the rest are uniform random on mount.
Positions are recomputed on the CPU every frame and uploaded with
`bufferSubData` — this is a per-frame array update of 11,520 floats, not a vertex
shader animation.

**Helix.** `angle = t · 22.62 + strandPhase + 0.12 time` (7.2 half-turns, i.e.
3.6 full revolutions over the length). `baseRadius = 1.05 + 0.12 wobble +
0.0176 sin(8t + 0.4 time + drift)`. The strand center is
`(cos angle · (1.05 + 0.25 baseRadius), y, sin angle · (1.05 + 0.25 baseRadius))`,
giving an effective radius of about 1.31. The 0.25 factor is why baseRadius's
variation barely affects the silhouette; most of the visual width comes from the
cross-section.

**Cross-section.** `swirl = crossAngle + 0.2 time`;
`crossRadius = 0.18 (0.45 + rand·0.55 ± 0.06) + 0.04 sin(0.35 time + drift)`,
where the ±0.06 makes strand 0 slightly fatter than strand 1. Offsets:
`x += cos(swirl) · crossRadius`, `z += sin(swirl) · crossRadius`,
`y += 0.054 sin(2 swirl + drift + 0.25 time)`. A second band term
`0.0396 sin(2πt + 0.35 time)` pushes x by 40% and y by 60% of itself, which is
what produces the knotty segment clustering.

**Projection.** A real perspective matrix, 36° vertical FOV, eye at
`(0.6 px, 0.12 + 0.36 py, 6.4)`, target `(0, 0.4 py, 0)`, near 0.1, far 18. The
column length 5.6 at distance 6.4 fills most of the frame height; the helix is
seen slightly off-axis, so its near and far sides overlap.

**Point size.** `size = 30 (0.7 + rand·0.9)`, i.e. 21–48 world units. The scale
uniform is `height·DPR / 200`, so at 640x400 DPR 1 it is 2 and
`gl_PointSize = max(1, 2·size / clip.w)`; across the helix's depth (w ≈ 5.1–7.7)
that is about 5.5–19 px, or 6.5–15 px at the mean distance 6.4. The fragment uses
`uv = pointCoord − 0.5`,
`alpha = smoothstep(0.24, 0, |uv|²)` and `rim = smoothstep(0.18, 0, |uv|²)`,
mixing color toward 1.05× at the center — a soft disc with a faintly hotter core.

## 6. Parameters

| name | value | range | effect | sensitivity |
| --- | --- | --- | --- | --- |
| segments | 160 | 80–260 | helix length resolution | M |
| strands | 2 | 1–3 | number of interleaved columns | H |
| pointsPerSegment | 12 | 4–24 | strand density | H |
| turns | 7.2π rad | 2π–12π | revolutions over the length | H |
| radius | 1.05 | 0.6–1.6 | helix radius | H |
| length | 5.6 | 3–8 | vertical extent | H |
| crossSection | 0.18 | 0.05–0.35 | ribbon thickness | H |
| crossJitter | 0.22 | 0–0.4 | radial wobble | M |
| rotationSpeed | 0.12 rad/s | 0–0.3 | spin | M |
| driftStrength | 0.22 | 0–0.4 | band and radius drift | M |
| verticalWave | 0.45 | 0–0.9 | vertical offset amplitude | M |
| basePointSize | 30 | 14–50 | dot size in world units | H |
| pointScaleFactor | 200 | 100–400 | pixels per world unit of size | H |
| maxDpr | 2 | 1–2 | sharpness vs cost | L |
| cameraDistance | 6.4 | 4–10 | how much of the column fills the frame | H |
| cameraHeight | 0.12 | −1–1 | eye level relative to the column | M |
| fov | 36° | 24–50 | perspective | M |
| near / far | 0.1 / 18 | fixed | clip range only | L |
| pointerInfluence | 0.6 | 0–1.2 | parallax amount | L |

## 7. Palette and color

Both strands share the same ramp along `t` from start `#143DFA` to end `#00BFFF`
(a smoothstep), then strand A is tinted 24% toward the accent `#D952FF` and
strand B 48%, so one reads electric blue and the other violet. Alpha ramps 0.32 →
0.68 at mid-column via
`1 − |t − 0.5| · 1.8`, plus ±0.05 from a per-particle sine. Brightness comes from
stacking: additive sprites over a transparent buffer, so the core of a dense band
saturates to white while isolated dots stay saturated blue.

## 8. Composition and camera

The molecule is centered horizontally; the column is longer than the frame
(5.6 units at 6.4 distance and 36° FOV is ~135% of frame height), so both ends
are cropped — the poster shows strands running off the top and bottom edges. Its
width is roughly 40% of the frame. The camera looks nearly straight down the +Z
axis with a 0.12 height offset, so both helix faces are visible and crossings
read as X shapes. Wide aspect leaves dark margins at the sides; tall aspect crops
even more of the column ends.

## 9. Randomness and seeds

`Math.random()` — no seed, no state carried between runs. Cross-section angle and
radius, wobble, drift phase, and point size are independent uniform draws, so two
runs differ in particle placement but not in silhouette or density. There is no
warmup: the first frame is fully formed, since positions are a closed-form
function of `t`.

## 10. Performance budget

One draw call, 3840 points, plus a CPU loop writing 11,520 floats and a
`bufferSubData` upload each frame. Fill is modest (dots under 16 px) but dense in
the bands. 60 fps at 1080p; maxDpr 2 is the only real risk on high-density
screens. Cut order: maxDpr to 1.5, pointsPerSegment to 8, segments to 120.

## 11. Host integration

Transparent-canvas scene relying on the host gradient. Uses a `ResizeObserver`
on the holder plus `window.resize`, and listens to `pointermove`,
`pointerleave`, `touchmove`, and `touchend`. DPR clamp is 2, tied with RibbonFlow
and CosmicAnomaly for the gallery's highest. Teardown removes all five listeners,
disconnects the observer, deletes
three buffers and the program, and loses the context.

## 12. Failure modes and tells

- **Helix reads as two plain sine waves →** cross-section radius is zero; the
  ribbon comes from particles orbiting each strand center.
- **Strands look like one thick column →** `strandPhase` is not π; both strands
  are at the same phase.
- **Column is cut off top and bottom →** `cameraDistance` too small or `length`
  too large for the 36° FOV.
- **Dots are square or hard-edged →** the fragment's `smoothstep` falloff is
  missing or the point size is under 1 px.
- **Ends stay as bright as the center →** the alpha ramp uses `|t − 0.5|` without
  the 1.8 scale, so centerWeight never falls below 0.5.
- **Jitter and stutter every second →** positions are being re-allocated instead
  of reused; the original writes into fixed typed arrays.

## 13. Tuning knobs

1. `turns` — lazy two-turn spiral versus a tight coil (4π–9π).
2. `crossSection` — a clean double line versus a fluffy ribbon (0.1–0.3).
3. `pointsPerSegment` — beaded versus continuous (8–18).
4. `rotationSpeed` — how quickly crossings slide (0.05–0.2).
5. `basePointSize` — crisp specks versus soft bokeh (20–40).

## 14. Verification checklist

- Two distinct phase-shifted strands crossing repeatedly, not one column.
- Dots are soft and round; no square sprites.
- Blue strand and violet strand distinguishable at a glance.
- Brightness peaks near the vertical center, fades at both ends.
- Background black-navy; no visible canvas rectangle.
- Smooth rotation; no shimmer between frames.
- Compare with `assets/posters/dna-helix.jpg`: same pitch and ribbon width;
  particle positions differ because the RNG is unseeded.

## 15. Porting notes

This is the one f3 scene animated on the CPU; a shader port is possible but must
keep the per-particle random cross-section, which is what makes the strand
fluffy. No highp requirement — the shader only reprojects fixed positions.
