# Recipe: orbit-loop — `/animation svg orbit-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `orbit` (one-shot path convergence) and `spark` (one-shot linear reveal). Uses SMIL `<animateMotion>` along a closed elliptical track sized inside the viewport.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <radialGradient id="...">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="45%" stop-color="#0494a4"/>
      <stop offset="100%" stop-color="#0494a4" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <style>
    @media (prefers-reduced-motion: reduce) {
      .sat-wrap { display: none; }
    }
  </style>

  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="sat-wrap">
    <circle r="7" fill="url(#sat-glow)">
      <animateMotion dur="3.6s" repeatCount="indefinite"
                     path="M 10,55 A 140,48 0 1,1 290,55 A 140,48 0 1,1 10,55"/>
    </circle>
    <circle r="2.4" fill="#ffffff" stroke="#0494a4" stroke-width="1">
      <animateMotion dur="3.6s" repeatCount="indefinite"
                     path="M 10,55 A 140,48 0 1,1 290,55 A 140,48 0 1,1 10,55"/>
    </circle>
  </g>
</svg>
```

## Notes

- **Track clearance**: keep ellipse radii `rx ≤ W/2 - 10` (`140u`) and `ry ≤ H/2 - 7` (`48u`) so the `r = 7` glow halo never gets shaved off by the SVG edges.
- Duplicate the identical `path` and `dur` on both the soft radial glow `<circle>` and crisp core `<circle>` so they stay locked together. Note: `<animateMotion path="...">` does not add `<path>` elements, keeping path count equal to source.
