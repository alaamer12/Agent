# Scene index

All 50 backgrounds, grouped by technique family. Every row links to its
reconstruction reference and its rendered poster. `S/M/L/XL` is the
reconstruction effort tier defined in `../SKILL.md`.

## Families

| family | technique | renderer | count | effort | reference |
| --- | --- | --- | --- | --- | --- |
| `webgl-f1` | Closed-form fragment fields | webgl1 | 11 | M/S | [webgl-f1](families/webgl-f1-fragment-fields.md) |
| `webgl-f2` | Raymarched SDF and volumetric | webgl1 | 5 | XL/L | [webgl-f2](families/webgl-f2-raymarch.md) |
| `webgl-f3` | Vertex-projected particle clouds | webgl1, three | 6 | L/XL | [webgl-f3](families/webgl-f3-particle-clouds.md) |
| `webgl-f4` | Line and ribbon geometry | webgl1, three | 5 | L/XL | [webgl-f4](families/webgl-f4-line-geometry.md) |
| `webgl-f5` | Vertex-displaced solid mesh | three | 5 | L/XL | [webgl-f5](families/webgl-f5-displaced-mesh.md) |
| `webgl-f6` | Escape-time fractal | webgl1 | 1 | M | [webgl-f6](families/webgl-f6-fractal.md) |
| `webgl-f7` | CPU simulation to texture | webgl1 | 1 | XL | [webgl-f7](families/webgl-f7-cpu-texture.md) |
| `canvas-a1` | Noise-advected particles | canvas2d | 4 | S/L/M | [canvas-a1](families/canvas-a1-noise-particles.md) |
| `canvas-a2` | Pre-rendered sprite blitting | canvas2d | 4 | M | [canvas-a2](families/canvas-a2-sprite-blit.md) |
| `canvas-a3` | Analytic wave and geometry fields | canvas2d | 4 | M/S | [canvas-a3](families/canvas-a3-analytic-fields.md) |
| `canvas-a4` | Sampled heightfield and isolines | canvas2d | 1 | XL | [canvas-a4](families/canvas-a4-heightfield.md) |
| `canvas-a5` | Accumulating ink | canvas2d | 2 | M/L | [canvas-a5](families/canvas-a5-accumulating-ink.md) |
| `canvas-a6` | Film emulation | canvas2d | 1 | M | [canvas-a6](families/canvas-a6-film.md) |

## All scenes

| id | name | family | renderer | tier | lines | reference | poster |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `constellation-net` | Constellation Net | `canvas-a1` | canvas2d | L | 428 | [ref](scenes/constellation-net.md) | [jpg](../assets/posters/constellation-net.jpg) |
| `firefly-meadow` | Firefly Meadow | `canvas-a1` | canvas2d | M | 329 | [ref](scenes/firefly-meadow.md) | [jpg](../assets/posters/firefly-meadow.jpg) |
| `flow-field` | Flow Field | `canvas-a1` | canvas2d | S | 192 | [ref](scenes/flow-field.md) | [jpg](../assets/posters/flow-field.jpg) |
| `smoke-wisps` | Smoke Wisps | `canvas-a1` | canvas2d | M | 334 | [ref](scenes/smoke-wisps.md) | [jpg](../assets/posters/smoke-wisps.jpg) |
| `bokeh-drift` | Bokeh Drift | `canvas-a2` | canvas2d | M | 368 | [ref](scenes/bokeh-drift.md) | [jpg](../assets/posters/bokeh-drift.jpg) |
| `data-rain` | Data Rain | `canvas-a2` | canvas2d | M | 420 | [ref](scenes/data-rain.md) | [jpg](../assets/posters/data-rain.jpg) |
| `golden-bloom` | Golden Bloom | `canvas-a2` | canvas2d | M | 276 | [ref](scenes/golden-bloom.md) | [jpg](../assets/posters/golden-bloom.jpg) |
| `kaleido-bloom` | Kaleido Bloom | `canvas-a2` | canvas2d | M | 412 | [ref](scenes/kaleido-bloom.md) | [jpg](../assets/posters/kaleido-bloom.jpg) |
| `aurora-waves` | Aurora Waves | `canvas-a3` | canvas2d | M | 315 | [ref](scenes/aurora-waves.md) | [jpg](../assets/posters/aurora-waves.jpg) |
| `halftone-tide` | Halftone Tide | `canvas-a3` | canvas2d | S | 243 | [ref](scenes/halftone-tide.md) | [jpg](../assets/posters/halftone-tide.jpg) |
| `iso-drift` | Iso Drift | `canvas-a3` | canvas2d | M | 272 | [ref](scenes/iso-drift.md) | [jpg](../assets/posters/iso-drift.jpg) |
| `spectrum-cascade` | Spectrum Cascade | `canvas-a3` | canvas2d | M | 303 | [ref](scenes/spectrum-cascade.md) | [jpg](../assets/posters/spectrum-cascade.jpg) |
| `contour-map` | Contour Map | `canvas-a4` | canvas2d | XL | 457 | [ref](scenes/contour-map.md) | [jpg](../assets/posters/contour-map.jpg) |
| `harmonograph-trails` | Harmonograph Trails | `canvas-a5` | canvas2d | M | 234 | [ref](scenes/harmonograph-trails.md) | [jpg](../assets/posters/harmonograph-trails.jpg) |
| `pulse-radar` | Pulse Radar | `canvas-a5` | canvas2d | L | 420 | [ref](scenes/pulse-radar.md) | [jpg](../assets/posters/pulse-radar.jpg) |
| `analog-grain` | Analog Grain | `canvas-a6` | canvas2d | M | 291 | [ref](scenes/analog-grain.md) | [jpg](../assets/posters/analog-grain.jpg) |
| `caustic-pool` | Caustic Pool | `webgl-f1` | webgl1 | M | 263 | [ref](scenes/caustic-pool.md) | [jpg](../assets/posters/caustic-pool.jpg) |
| `event-horizon` | Event Horizon | `webgl-f1` | webgl1 | M | 325 | [ref](scenes/event-horizon.md) | [jpg](../assets/posters/event-horizon.jpg) |
| `hologram-scan` | Hologram Scan | `webgl-f1` | webgl1 | M | 333 | [ref](scenes/hologram-scan.md) | [jpg](../assets/posters/hologram-scan.jpg) |
| `iridescent-film` | Iridescent Film | `webgl-f1` | webgl1 | M | 410 | [ref](scenes/iridescent-film.md) | [jpg](../assets/posters/iridescent-film.jpg) |
| `magma-veins` | Magma Veins | `webgl-f1` | webgl1 | M | 326 | [ref](scenes/magma-veins.md) | [jpg](../assets/posters/magma-veins.jpg) |
| `moire-veil` | Moire Veil | `webgl-f1` | webgl1 | M | 323 | [ref](scenes/moire-veil.md) | [jpg](../assets/posters/moire-veil.jpg) |
| `nebula-currents` | Nebula Currents | `webgl-f1` | webgl1 | S | 251 | [ref](scenes/nebula-currents.md) | [jpg](../assets/posters/nebula-currents.jpg) |
| `neon-horizon` | Neon Horizon | `webgl-f1` | webgl1 | M | 345 | [ref](scenes/neon-horizon.md) | [jpg](../assets/posters/neon-horizon.jpg) |
| `neural-noise` | Neural Noise | `webgl-f1` | webgl1 | M | 282 | [ref](scenes/neural-noise.md) | [jpg](../assets/posters/neural-noise.jpg) |
| `solar-corona` | Solar Corona | `webgl-f1` | webgl1 | M | 327 | [ref](scenes/solar-corona.md) | [jpg](../assets/posters/solar-corona.jpg) |
| `voronoi-circuit` | Voronoi Circuit | `webgl-f1` | webgl1 | M | 331 | [ref](scenes/voronoi-circuit.md) | [jpg](../assets/posters/voronoi-circuit.jpg) |
| `crystalline-depths` | Crystalline Depths | `webgl-f2` | webgl1 | XL | 425 | [ref](scenes/crystalline-depths.md) | [jpg](../assets/posters/crystalline-depths.jpg) |
| `endless-range` | Endless Range | `webgl-f2` | webgl1 | L | 390 | [ref](scenes/endless-range.md) | [jpg](../assets/posters/endless-range.jpg) |
| `liquid-chrome` | Liquid Chrome | `webgl-f2` | webgl1 | L | 363 | [ref](scenes/liquid-chrome.md) | [jpg](../assets/posters/liquid-chrome.jpg) |
| `metaball-orbit` | Metaball Orbit | `webgl-f2` | webgl1 | XL | 456 | [ref](scenes/metaball-orbit.md) | [jpg](../assets/posters/metaball-orbit.jpg) |
| `quantum-foam` | Quantum Foam | `webgl-f2` | webgl1 | L | 331 | [ref](scenes/quantum-foam.md) | [jpg](../assets/posters/quantum-foam.jpg) |
| `cosmic-anomaly` | Cosmic Anomaly | `webgl-f3` | three | L | 532 | [ref](scenes/cosmic-anomaly.md) | [jpg](../assets/posters/cosmic-anomaly.jpg) |
| `dna-helix` | DNA Helix | `webgl-f3` | webgl1 | XL | 616 | [ref](scenes/dna-helix.md) | [jpg](../assets/posters/dna-helix.jpg) |
| `galaxy-spiral` | Galaxy Spiral | `webgl-f3` | webgl1 | L | 514 | [ref](scenes/galaxy-spiral.md) | [jpg](../assets/posters/galaxy-spiral.jpg) |
| `orbit-belt` | Orbit Belt | `webgl-f3` | webgl1 | L | 574 | [ref](scenes/orbit-belt.md) | [jpg](../assets/posters/orbit-belt.jpg) |
| `particle-waves` | Particle Waves | `webgl-f3` | webgl1 | L | 583 | [ref](scenes/particle-waves.md) | [jpg](../assets/posters/particle-waves.jpg) |
| `warp-field` | Warp Field | `webgl-f3` | webgl1 | L | 435 | [ref](scenes/warp-field.md) | [jpg](../assets/posters/warp-field.jpg) |
| `crystal-lattice` | Crystal Lattice | `webgl-f4` | webgl1 | XL | 525 | [ref](scenes/crystal-lattice.md) | [jpg](../assets/posters/crystal-lattice.jpg) |
| `field-lines` | Field Lines | `webgl-f4` | webgl1 | XL | 698 | [ref](scenes/field-lines.md) | [jpg](../assets/posters/field-lines.jpg) |
| `ribbon-flow` | Ribbon Flow | `webgl-f4` | webgl1 | L | 362 | [ref](scenes/ribbon-flow.md) | [jpg](../assets/posters/ribbon-flow.jpg) |
| `silk-strands` | Silk Strands | `webgl-f4` | webgl1 | XL | 435 | [ref](scenes/silk-strands.md) | [jpg](../assets/posters/silk-strands.jpg) |
| `wire-globe` | Wire Globe | `webgl-f4` | three | XL | 792 | [ref](scenes/wire-globe.md) | [jpg](../assets/posters/wire-globe.jpg) |
| `chromatic-knot` | Chromatic Knot | `webgl-f5` | three | XL | 546 | [ref](scenes/chromatic-knot.md) | [jpg](../assets/posters/chromatic-knot.jpg) |
| `facets-tunnel` | Facets Tunnel | `webgl-f5` | three | XL | 626 | [ref](scenes/facets-tunnel.md) | [jpg](../assets/posters/facets-tunnel.jpg) |
| `pulse-orb` | Pulse Orb | `webgl-f5` | three | XL | 729 | [ref](scenes/pulse-orb.md) | [jpg](../assets/posters/pulse-orb.jpg) |
| `sombrero-dunes` | Sombrero Dunes | `webgl-f5` | three | L | 371 | [ref](scenes/sombrero-dunes.md) | [jpg](../assets/posters/sombrero-dunes.jpg) |
| `voxel-storm` | Voxel Storm | `webgl-f5` | three | XL | 544 | [ref](scenes/voxel-storm.md) | [jpg](../assets/posters/voxel-storm.jpg) |
| `fractal-drift` | Fractal Drift | `webgl-f6` | webgl1 | M | 314 | [ref](scenes/fractal-drift.md) | [jpg](../assets/posters/fractal-drift.jpg) |
| `fluid-ripples` | Fluid Ripples | `webgl-f7` | webgl1 | XL | 562 | [ref](scenes/fluid-ripples.md) | [jpg](../assets/posters/fluid-ripples.jpg) |

## Pick by look

- **aurora, silk, ribbons** — aurora-waves, silk-strands, ribbon-flow
- **galaxy, starfield** — galaxy-spiral, warp-field, constellation-net
- **nebula, smoke, haze** — nebula-currents, smoke-wisps, bokeh-drift
- **flowing particles** — flow-field, particle-waves, firefly-meadow
- **crystal, raymarch** — crystalline-depths, crystal-lattice, liquid-chrome
- **liquid, metaball** — fluid-ripples, metaball-orbit, liquid-chrome
- **wire, grid, horizon** — wire-globe, hologram-scan, neon-horizon
- **tunnel, depth fall** — facets-tunnel, data-rain, iso-drift
- **radar, scan lines** — pulse-radar, hologram-scan, moire-veil
- **film, print, contour** — analog-grain, halftone-tide, contour-map
- **bloom, fractal** — golden-bloom, kaleido-bloom, fractal-drift
- **organic fields** — magma-veins, voronoi-circuit, caustic-pool

## Known cross-cutting facts

- Posters are 640x400 at DPR 1, captured 3.5 s after mount (see `poster_capture` in `manifest.json`).
- The preview host paints a `#000000 → #1A0033` vertical gradient behind every scene; transparent-canvas scenes depend on it.
- All 50 originals are single-scene: the FPS meter is a singleton and assumes exactly one mounted background.
- 27 of the 34 WebGL scenes lose their GL context explicitly on teardown; gallery hosts cycle many contexts.
- A few posters predate the current constants — notably `crystal-lattice` and
  `field-lines`, whose live objects are much larger and dimmer than the poster.
  Read posters as hue and structure targets; when they disagree with a reference,
  the reference values win.
