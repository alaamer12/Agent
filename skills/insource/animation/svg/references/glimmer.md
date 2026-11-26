# Recipe: glimmer — `/animation svg glimmer`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `shimmer` (diagonal sweeping sheen bar) and `comet` (contour stroke). Four 8-vertex 4-point `<polygon>` starlets twinkle on prime-staggered periods inside the logo clip.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="...">
      <use href="#path-teal"/>
      <use href="#path-navy"/>
    </clipPath>
  </defs>

  <style>
    .glim { fill: #ffffff; opacity: 0; transform-box: fill-box; transform-origin: center; }
    .g1 { animation: twinkle 2.9s ease-in-out 0.1s infinite; }
    .g2 { animation: twinkle 3.7s ease-in-out 0.9s infinite; }
    .g3 { animation: twinkle 3.1s ease-in-out 1.7s infinite; }
    .g4 { animation: twinkle 4.1s ease-in-out 0.5s infinite; }
    @keyframes twinkle {
      0%, 62%, 100% { opacity: 0; transform: scale(0.4) rotate(0deg); }
      78%           { opacity: 0.92; transform: scale(1.1) rotate(22deg); }
      90%           { opacity: 0; transform: scale(0.5) rotate(45deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .glim { animation: none; opacity: 0; }
    }
  </style>

  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g clip-path="url(#glim-logo)">
    <polygon class="glim g1" points="62,36 65.4,44.6 74,48 65.4,51.4 62,60 58.6,51.4 50,48 58.6,44.6"/>
    <polygon class="glim g2" points="122,49 125.6,58.4 135,62 125.6,65.6 122,75 118.4,65.6 109,62 118.4,58.4"/>
    <polygon class="glim g3" points="206,36 209.4,44.6 218,48 209.4,51.4 206,60 202.6,51.4 194,48 202.6,44.6"/>
    <polygon class="glim g4" points="266,40 269.4,48.6 278,52 269.4,55.4 266,64 262.6,55.4 254,52 262.6,48.6"/>
  </g>
</svg>
```

## Notes

- **Clip all starlets to `url(#glim-logo)`** so sparkles illuminate only inside the brand ink and never bleed onto transparent canvas or into counters.
- Prime-number durations (`2.9s, 3.7s, 3.1s, 4.1s`) prevent all four stars from syncing into a repetitive beat. Draw starlets with `<polygon>`, never `<path>`.
