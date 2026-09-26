# Recipe: mosaic — `/svg-animate mosaic`

The logo dissolves in through a grid of square tiles, each opening on its own
slightly-jittered beat, so a wave crosses the artwork. One-shot; ends fully
visible. Nothing in the other styles is tiled.

## Template

Tiles are hand-expanded — 15 × 6 = 90 rects here. Generate them, do not type
them; the `begin` values are arithmetic.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="mosaic-mask" maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="0" y="0" width="20" height="20" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.35s" begin="0.05s" fill="freeze"/></rect>
      <rect x="20" y="0" width="20" height="20" fill="#fff" opacity="0"><animate attributeName="opacity" values="0;1" dur="0.35s" begin="0.11s" fill="freeze"/></rect>
      <!-- … one rect per tile, begin written as a literal … -->
    </mask>
  </defs>

  <style>
    /* The tiles are SMIL, which no media query can pause — but the CSS mask
       property outranks the mask attribute, so dropping the mask outright
       reveals the finished logo. */
    @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
  </style>

  <g class="logo" mask="url(#mosaic-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Every mask child is white.** A `<mask>` keys on *luminance* by default, and
  the artwork's own navy `#040c24` is almost black — a `<use>` of the real
  paths inside the mask hides nearly everything. The mask is a separate
  black-and-white drawing of *where*, never a copy of *what*.
- **`begin` must be a literal value in the file.** SMIL cannot compute
  `0.7 * gx/14` at runtime, so the generator writes each resolved number in.
  Formula used: `begin = 0.05 + 0.70·(gx/maxGx) + 0.15·(gy/maxGy) + jitter(≤0.12)`,
  per-tile `dur = 0.35s`, total ≈ 1.34s.
- **Tile size ≈ W/15, and never below 4·F.** At 20u on this logo the tiles are
  ~4× the 4.84px thinnest feature, so no mark is stranded across a tile
  boundary. Below that, small glyphs pop in as fragments.
- **Reveal origin is a knob.** The wave above runs left→right; on an Arabic
  wordmark that reads against the direction of the text. Move the origin by
  changing the distance term (`gx` → `maxGx - gx`, or a radial
  `hypot(gx-ox, gy-oy)`) and regenerate.
- Mask region extends 5u past the canvas on every side so edge tiles are not
  cut by the mask itself rather than by their own timing.
- **Do not implement this with `<pattern>` instead of expanded rects.** A
  pattern tile is instantiated repeatedly, so one animation drives every tile
  identically — you get a dot-thickness change, not a wave. (Separately: SMIL
  *inside* a pattern was measured to repaint fine in Chromium 153, which is why
  the reason to avoid it here is the look, not browser support.)
- Cost check: 90 tiles ≈ 14KB of extra markup. Above ~200 tiles, drop to a
  coarser grid.
- **Verified in Chromium 153 only.**
