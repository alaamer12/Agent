# Recipe: cyanotype — `/animation svg cyanotype`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `blueprint` (vector wireframe draw + drafting grid) and `exposure` (colorless flash). Combines a Prussian-blue `feColorMatrix` with an inner CSS `brightness(1.7 → 0.95)` development curve.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix"
        values="0.06 0.06 0.06 0 0.04
                0.20 0.25 0.25 0 0.16
                0.45 0.50 0.60 0 0.36
                0    0    0    1 0"/>
    </filter>
  </defs>

  <style>
    .cyano-print { opacity: 0; animation: cyano-dev 1.65s ease-out forwards; }
    .cyano-solid { opacity: 0; animation: cyano-land 0.55s ease-out 1.05s forwards; }
    @keyframes cyano-dev {
      0%   { opacity: 0; filter: brightness(1.7); }
      35%  { opacity: 0.95; filter: brightness(1.0); }
      72%  { opacity: 0.95; filter: brightness(0.95); }
      100% { opacity: 0; filter: brightness(1.0); }
    }
    @keyframes cyano-land { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .cyano-wrap { filter: none; }
      .cyano-print { animation: none; opacity: 0; filter: none; }
      .cyano-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="cyano-wrap" filter="url(#cyano-fx)">
    <g class="cyano-print">
      <use href="#path-teal"/>
      <use href="#path-navy"/>
    </g>
  </g>
  <g class="cyano-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Keep the `filter="url(#cyano-fx)"` on an outer wrapper `<g>` and animate CSS `filter: brightness()` on the inner `<g>` so neither overrides the other (avoiding CSS filter clobbering the SVG filter URL).
- Crossfade to `.cyano-solid` (`1.05s–1.6s`) and dismiss `.cyano-print` to `opacity: 0`.
