# Recipe: crt — `/svg-animate crt`

A TV tube powering on: a bright hot line appears on the centreline, the logo
opens vertically out of it, a scanline texture rides along and fades, and the
logo lands clean. One-shot.

Distinct from `iris`, which grows a circle radially from the centre. This
opens a **1-D band** off a horizontal axis, and clips with CSS `clip-path`
rather than a `url()` reference.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <pattern id="crt-lines" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1.5" fill="#000000"/>
    </pattern>
    <clipPath id="crt-logo">
      <use href="#path-teal"/>
      <use href="#path-navy"/>
    </clipPath>
  </defs>

  <style>
    .crt-band {
      clip-path: inset(50% 0);
      animation: crt-open 0.42s cubic-bezier(0.2, 0.8, 0.2, 1) 0.16s forwards;
    }
    .crt-scan { opacity: 0.38; animation: crt-texture 0.7s linear 0.5s forwards; }
    .crt-hot  { opacity: 0; animation: crt-hotline 0.5s linear 0.16s forwards; }
    @keyframes crt-open    { to { clip-path: inset(0 0); } }
    @keyframes crt-texture { to { opacity: 0; } }
    @keyframes crt-hotline { 0% { opacity: 0; } 14% { opacity: 0.95; } 100% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .crt-band { animation: none; clip-path: none; }
      .crt-scan { animation: none; opacity: 0; }
      .crt-hot  { animation: none; opacity: 0; }
    }
  </style>

  <g class="crt-band">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
    <g clip-path="url(#crt-logo)">
      <rect class="crt-scan" width="300" height="110" fill="url(#crt-lines)"/>
    </g>
  </g>
  <rect class="crt-hot" x="0" y="54.25" width="300" height="1.5" fill="#0494a4"/>
</svg>
```

## Notes

- **Use bare `inset()` — the `view-box` keyword is dead.** `inset(50% 0
  view-box)` was measured to *not* interpolate in Chromium: the animation ran
  and the frame never changed. Plain `inset(50% 0)` → `inset(0 0)` works. The
  cost is that percentages resolve against the element's **object bounding
  box**, not the canvas, so the band closes at the artwork's centreline rather
  than the viewport's. On a logo that nearly fills its frame the difference is
  sub-pixel; on a small mark in a large canvas it will look off-centre.
- **The scanline overlay must be clipped to the logo union.** The first build
  painted the pattern across the whole canvas and the counter gate caught it
  inking every one of the 111 sampled gap pixels mid-beat — the letterform
  holes went milky. Clipping to `url(#crt-logo)` dropped that to 2.
- **Give the pattern a transparent base.** A white `<rect>` behind the dark
  stripe is what washed the counters; dark stripes only, so the overlay only
  ever darkens.
- **Hot line in the brand colour**, not white: it has to read on a light stage
  as well as a dark one. It sits *outside* the clipped band so it is visible
  before the band opens.
- **Texture fades to zero** (`crt-texture`) so the resting logo is pixel-exact
  — measured end drift 0.00% against the source. Leaving scanlines on
  permanently is a different style, not this one.
- Geometry: open duration ≈ 0.35 × H/100 scaled by the timing column, hot line
  `h = max(1.5, H/73)`, pattern pitch 4 with a 1.5 stripe (below ~1.5 the
  stripes vanish at 1× raster).
- **Verified in Chromium 153 only.**
