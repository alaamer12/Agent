---
family: webgl-f7
name: CPU simulation to texture
renderer: webgl1
members: [fluid-ripples]
---

# CPU simulation to texture

## Members

| id | name | lines | tier | distinguishing trait |
| --- | --- | --- | --- | --- |
| `fluid-ripples` | Fluid Ripples | 562 | XL | 256×256 CPU wave/vorticity field uploaded as a float texture each frame and used to warp a procedural disc |

## Shared scaffold

The render path is a single textured fullscreen quad. The unique part is
upstream of it: a fixed-size typed-array simulation that advances once per
animation frame, entirely on the CPU, then uploads its scalar field as a
`LUMINANCE`/`FLOAT` texture. The display shader never knows the simulation
exists beyond sampling that one channel.

Order per frame: step the simulation (several typed-array passes), zero the
boundary, swap the double buffer, upload the texture, then draw. The frame is
therefore paced by the CPU sim, not the fill rate; the grid size is the budget
knob.

## Math primer

**Discrete wave equation.** With height `h` and previous height `h_prev` on a
grid, a stable explicit update is
`h' = (h_prev[left] + h_prev[right] + h_prev[up] + h_prev[down]) / 2 − h`.
The `/2` rather than `/4` is the standard trick that keeps the scheme stable at
this grid spacing. Damping blends toward the previous state
(`h ← α h + (1 − α) h_prev`), and tension pulls toward the rest height
(`h ← h − τ h_prev`). Both are per-step coefficients, not per-second; tuning
them means assuming a 60 fps step.

**Vorticity.** Curl of the 2D velocity field is
`ω = 0.5 (∂v_y/∂x − ∂v_x/∂y)`, computed with central differences — the horizontal
neighbours use the y-velocity and the vertical neighbours the x-velocity. The
confinement force is proportional to the gradient of `|ω|` rotated 90°,
which pushes velocity toward existing vortices and keeps swirls from diffusing
into mush. Its magnitude is clamped per step to avoid injection blowups.

**Splat.** Adding a disturbance writes a radial falloff into both the height and
the velocity field: height gets a cosine-shaped bump, velocity gets a radial
push plus a tangential component (30%), which is what makes the eddy rather than
a simple outward pulse.

**Float textures in WebGL1.** `LUMINANCE` + `FLOAT` is the portable way to send
a scalar field; it depends on the float-texture capability, and rendering to it
is not available. Uploading per frame is a 256 KB transfer at 256², which is
why the grid is small.

**Boundary conditions.** Zeroing the outer ring each step creates fixed edges —
ripples reflect off the border. Without it, energy accumulates at the edge and
the field saturates.

## Shared helpers

- Double buffer with a swap, not a copy.
- Throttled pointer sampling (8 ms) so a 1000 Hz mouse cannot inject thousands
  of splats per frame.
- Position normalization from window coordinates so splats land under the
  pointer regardless of canvas size.
- A single scripted splat at mount to guarantee a non-empty opening frame.

## Conventions

- Grid axes: `index = y · resolution + x`; y increases downward in texture
  space, so pointer y is flipped when splatting.
- Heights are dimensionless, clamped to ±2.
- Velocity is in grid cells per step, clamped to ±0.1 at injection.
- Time in seconds only in the display shader; the sim is step-based.

## Variation map

Only one member. The tunable axes are grid resolution, damping/tension (ripple
character), vorticity influence (eddy tightness), splat size and strength, and
how strongly the display shader couples the height field to the pattern.

## Porting

The simulation is plain arrays and ports to any language. Keep the pass order:
velocity dissipation → vorticity → confinement → wave update → boundary →
swap → upload. Uploading a float texture requires the float-texture extension on
WebGL1; on WebGL2 use `R32F`. If a GPU pipeline is available, a ping-pong
render target replaces the CPU loop and the grid can be 512² or larger, but the
visual signature of this scene comes from the low 256² resolution — the smooth,
slightly blurry interpolation — so do not raise it without changing the look.

## Failure modes

- **Field explodes to NaN** — damping/tension combination unstable; keep
  `damping ≤ 0.96` and `tension ≤ 0.05`.
- **Static image** — texture upload skipped or wrong format; check for GL errors
  after every `texImage2D`.
- **Ripples reflect as hard lines** — boundary zeroing omitted.
- **Wash of swirls with no structure** — vorticity influence too high for the
  splat size.
- **CPU spikes** — vorticity loops running over the full grid every frame when
  the influence is zero; gate them.

## Verification heuristics

The field must visibly respond to pointer motion within one frame and decay
within a couple of seconds. Interior detail should be smooth (bilinear), not
pixelated. The display should stay dim: peak values well under white. If the
disc never shows a warm/cool split, the channel phases are wrong.
