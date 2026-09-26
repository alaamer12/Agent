# Recipe: comet — `/svg-animate comet`

The logo stays fully drawn at all times; a bright dash segment travels
endlessly along its outlines like a spark tracing the letterforms. Infinite
loop — an ambient "energy" treatment, not a loader.

## Template

Each path appears twice: once with a dim base stroke (its own color), once
with the bright comet dash on top.

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
<style>
  .comet-base {
    stroke: currentColor;
    stroke-width: 1;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.35;
  }
  .comet {
    fill: none;
    stroke: #ffffff;
    stroke-width: 1;
    stroke-linecap: round;
    filter: drop-shadow(0 0 2px rgba(255,255,255,0.9));
    stroke-dasharray: 96 704;
    animation: comet-run 3s linear infinite;
  }
  .c-teal { color: #0494a4; fill: #0494a4; }
  .c-navy { color: #040c24; fill: #040c24; }

  @keyframes comet-run {
    from { stroke-dashoffset: 800; }
    to   { stroke-dashoffset: 0; }
  }
</style>

<path class="comet-base c-teal" d="..." fill-rule="evenodd"/>
<path class="comet-base c-navy" d="..." fill-rule="evenodd"/>
<path class="comet c-teal" d="..." fill-rule="evenodd"/>
<path class="comet c-navy" d="..." fill-rule="evenodd"/>
</svg>
```

## Notes

- **Dash pattern** (the critical numbers): `stroke-dasharray: C G` where
  **C = 0.15 × max_subpath_length** (the comet's tail) and **G = the
  remainder**, so each contour carries roughly one comet. Get
  `max_subpath_length` from `extract_paths.py --lengths`. Here: 0.15 × 639 ≈
  96, gap 704, pattern 800.
- The `comet-run` keyframes animate dashoffset by exactly one full pattern
  (800 → 0) per cycle — seamless because the phase wraps.
- **Comet color** is near-white by default; `currentColor` ties the base
  stroke to each path's own color while the fill class carries `fill`.
- Loop ~2.5–3.5s. Faster reads as buzzing; slower as a lazy highlight.
- Unlike `loading-loop`, fills are ON the whole time — this decorates a
  finished logo rather than building it.
- If the logo has many short subpaths, several short sparks appear at once
  (one per contour) — that's expected and looks good.
