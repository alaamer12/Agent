# Mechanics This Logo Rejects

> Read **only** when asked for an effect outside the 25 named styles, or when inventing a new recipe.
> Four candidates were built, measured, and cut. Nobody should re-derive these failures.

- **`bloom`** (`feMorphology` dilate swell → sharpen). Technically animates — `radius` is animatable and
  it landed exact — but a square dilate kernel closes every counter narrower than 2·radius. On this logo
  the wordmark fuses into one blob for most of the beat, and it duplicates `focus`'s "sharpness settles"
  read anyway.
- **`halftone`** (dot-grid mask growing in place). SMIL inside `<pattern>` was predicted fragile and
  actually *does* repaint in Chromium 153 — but a periodic mask aperture cannot resolve features smaller
  than the tile, and this logo's thinnest mark is 4.84px. Measured: the 5px bar came back as a row of
  semicircles. Per-tile growth also reads as a dot-thickness change, not a spreading reveal. `mosaic` is
  the same idea at a scale that resolves.
- **`aperture`** (camera iris from rotating blades). Rotating a tiling of the plane by a common angle
  leaves the union unchanged — measured **zero frames of change** with full coverage throughout. Blades
  must change their *own* extent to open; `pinwheel` gets the segmented-radial read by scaling wedges
  instead.
- **`dropshadow`** (offset silhouette that stays). Physically correct, and it filled **92 of 111**
  letterform counters at rest: an offset shadow of a letter's stroke falls inside its own hole. A
  permanent offset shadow is incompatible with a logo that has small counters.
