# Recipe: blueprint — `/animation svg blueprint`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `draw-fill` (pure pen stroke → fill with no architectural grid) and `crt` (scanlines clipped inside the logo). A faint drafting grid and hairline wireframe draw in first, then true solid fills crossfade in as the drafting scaffolding dissolves to zero.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." fill-rule="evenodd"/>
    <path id="..." d="..." fill-rule="evenodd"/>
    <pattern id="..." width="15" height="15" patternUnits="userSpaceOnUse">
      <rect width="15" height="0.6" fill="#0494a4" fill-opacity="0.22"/>
      <rect width="0.6" height="15" fill="#0494a4" fill-opacity="0.22"/>
    </pattern>
  </defs>

  <style>
    .bp-grid-layer { opacity: 0; animation: bp-grid-fade 2.0s linear forwards; }
    .bp-wire {
      fill: none;
      stroke: #0494a4;
      stroke-width: 1;
      stroke-dasharray: 660;
      stroke-dashoffset: 660;
      animation: bp-draw 1.25s cubic-bezier(0.35, 0, 0.25, 1) 0.1s forwards,
                 bp-wire-out 0.65s linear 1.35s forwards;
    }
    .bp-solid { opacity: 0; animation: bp-solid-in 0.7s ease-out 1.25s forwards; }
    @keyframes bp-grid-fade { 0% { opacity: 0; } 15% { opacity: 1; } 68% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes bp-draw { to { stroke-dashoffset: 0; } }
    @keyframes bp-wire-out { to { opacity: 0; } }
    @keyframes bp-solid-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .bp-grid-layer, .bp-wire { animation: none; opacity: 0; }
      .bp-solid { animation: none; opacity: 1; }
    }
  </style>

  <rect class="bp-grid-layer" x="0" y="0" width="300" height="110" fill="url(#bp-grid)"/>
  <g class="bp-wire">
    <use href="#path-teal" fill="none"/>
    <use href="#path-navy" fill="none"/>
  </g>
  <g class="bp-solid">
    <use href="#path-teal" stroke="none" fill="#0494a4"/>
    <use href="#path-navy" stroke="none" fill="#040c24"/>
  </g>
</svg>
```

## Notes

- **Omit `fill` and `stroke` on the `<path>` defs in `<defs>`** (carry `d` and `fill-rule` only, just like `chrome-liquid`). Presentation attributes placed directly on `<path>` override inherited `fill="none"` on `<use>` in Chromium — omitting them on the def lets the wireframe `<use>` render strictly as strokes while the solid `<use>` carries the verbatim original fill hexes.
- **Single `animation` shorthand on `.bp-wire`** (foundations §6): list both `bp-draw` (`stroke-dashoffset`) and `bp-wire-out` (`opacity`) in one declaration so neither overwrites the other.
- **Dash length**: `≥ max_subpath_length` from `extract_paths.py --lengths` (660 on the 300×110 test logo).
- **Transparent grid base**: paint only the hairline strokes (`fill-opacity="0.22"`), never an opaque background rect, and fade `.bp-grid-layer` to `opacity: 0` so checkerboard review and end-drift stay clean (0.00%).
