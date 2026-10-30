# Glossary

Terms used across the scene references. One entry per term, alphabetical.

**Additive blending** — Compositing where source and destination are summed
(`lighter` in canvas 2D). Overlapping bright elements push toward white, which
is what makes particles and glows read as light rather than paint.

**Aspect correction** — Scaling x by `height / width` (or the inverse) so a
circular or isotropic function stays circular on a non-square canvas.

**Billboard** — A point or quad that always faces the camera. Particle clouds
draw every star as a billboard so a flat sprite can be scaled by depth.

**Bokeh** — Out-of-focus highlights rendered as soft discs with a brighter rim,
mimicking a defocused lens.

**Caustics** — Bright interference net patterns formed where refracted light
converges, typically from overlapping wavefronts.

**Curl noise** — A divergence-free vector field built from the curl of a scalar
noise field, used for smoke because it produces swirling flow with no sources
or sinks.

**DDA / ray marching** — Stepping a ray forward and testing a distance function
at each step. Fixed-step volumetric marching uses a constant step; sphere
tracing uses the distance returned by an SDF.

**Domain warping** — Sampling a noise field through coordinates that are
themselves displaced by another noise field. Produces filaments and marbling
that plain FBM does not.

**DPR** — Device pixel ratio. Backing-store size is CSS size times DPR; all
scenes clamp it (1.5 typical) to control fill cost.

**Escape-time** — Iterating a complex function until a magnitude threshold is
crossed; the iteration count is the color. Julia and Mandelbrot sets are
escape-time fractals.

**FBM** — Fractional Brownian motion: summing octaves of noise at increasing
frequency and decreasing amplitude, typically amplitude halving and frequency
roughly doubling (lacunarity ~2.0–2.1).

**Fresnel** — Rim light proportional to how grazing the view angle is; brightens
silhouettes and is the cheapest way to make a dark object read as 3D.

**Frustum / clip space** — The normalized volume a vertex shader writes to.
Perspective divide by `w` produces the screen position; dividing twice (by
also setting `w` from depth) is what gives the particle families their
inverse-square depth magnification.

**Halftone** — A dot grid whose dot radius encodes a continuous field, so the
image reads as a printed screen at a distance.

**Harmonograph** — Two damped sinusoids driving x and y; the trace produces
Lissajous rosettes that decay toward the center.

**HDR environment** — A high-dynamic-range image used for reflections. Only
CosmicAnomaly uses one, and it is remote.

**Instancing** — Drawing many copies of one geometry with per-instance
attributes in a single draw call. VoxelStorm and FacetsTunnel rely on it.

**Marching squares** — Extracting isolines from a sampled grid by classifying
each cell corner against a threshold. ContourMap uses five levels.

**Metaball** — An implicit surface from summed radial falloffs; smooth-minimum
(SDF) or thresholded scalar field variants both appear here.

**Moiré** — Low-frequency interference fringes produced by two near-identical
periodic patterns at slightly different angles or frequencies.

**Phyllotaxis** — Placing points at the golden angle (≈137.5°) on a spiral with
radius proportional to the square root of the index; yields the sunflower seed
arrangement used by GoldenBloom.

**Ping-pong buffer** — Alternating two render targets so a simulation can read
the previous frame while writing the current one. No original uses this; the
only simulation (FluidRipples) runs on the CPU.

**Point sprite** — A GL point expanded to a screen-aligned square; its size is
set by `gl_PointSize` in device pixels and clamped by the GPU (often 63 px).

**Power curve / easing** — Remapping a normalized value through a power or sine
to control perceived acceleration. Most scenes use `sin` half-waves for fades.

**Premultiplied alpha** — Color stored already multiplied by alpha. Canvas 2D
expects it on `putImageData`-derived paths; GL contexts differ, and
FluidRipples disables it explicitly.

**SDF** — Signed distance function: returns the distance to the nearest surface,
negative inside. Ray marching steps by this distance; smooth-min blends
surfaces without a hard seam.

**Simplex noise** — Gradient noise on a simplex grid, returning −1..1, cheaper
and less axis-aligned than classic Perlin at 3D and above.

**Tone mapping** — Compressing HDR values into display range. Hand-written GLSL
scenes mostly do this with a `1 - exp(-x)` style curve or a clamped power.

**Value noise** — Noise from interpolated random values at lattice points,
cheaper than gradient noise and visibly blockier at low octave counts.

**Warmup (priming)** — Running N hidden frames before the first visible frame so
trail or simulation scenes open at equilibrium instead of empty.

**WebGL1 / GLSL ES 1.00** — The shader generation all raw scenes target:
`attribute`, `varying`, `gl_FragColor`. No `in/out`, no integer textures.
