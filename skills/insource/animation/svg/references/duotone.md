# Recipe: duotone — `/animation svg duotone`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `colorize` (spatial left-to-right mask wipe) and `cyanotype` (bright-to-deep exposure curve). Uniform editorial `feColorMatrix` wash resolving cleanly into full color.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="..." x="0%" y="0%" width="100%" height="100%" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix"
        values="0.10 0.10 0.10 0 0.02
                0.35 0.45 0.35 0 0.32
                0.40 0.45 0.50 0 0.38
                0    0    0    1 0"/>
    </filter>
  </defs>

  <style>
    .duo-layer { opacity: 0; animation: duo-fade 1.45s linear forwards; }
    .duo-solid { opacity: 0; animation: duo-in 0.55s ease-out 0.85s forwards; }
    @keyframes duo-fade { 0% { opacity: 0; } 18% { opacity: 1; } 65% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes duo-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .duo-layer { animation: none; opacity: 0; filter: none; }
      .duo-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="duo-layer" filter="url(#duo-fx)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g class="duo-solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- Tune the `feColorMatrix` RGB rows to complement the source logo's primary accent color while keeping dark strokes legible on both light and dark stages.
- Always dismiss `.duo-layer` (`opacity: 0`) under `.duo-solid` for exact resting hexes.
