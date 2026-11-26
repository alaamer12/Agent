# Recipe: chrome-loop — `/animation svg chrome-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `shimmer` (single one-way gloss) and `chrome-liquid` (8s chrome-draw intro). Two skewed bands (warm white + cool steel) sweep in opposite directions on coprime durations.

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
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#9be7ff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#9be7ff" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="#9be7ff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .cl-a { transform: translateX(-95px) skewX(-22deg); animation: cl-sweep-a 3.8s ease-in-out infinite; }
    .cl-b { transform: translateX(345px) skewX(22deg); animation: cl-sweep-b 4.7s ease-in-out infinite; }
    @keyframes cl-sweep-a {
      0%   { transform: translateX(-95px) skewX(-22deg); }
      40%  { transform: translateX(345px) skewX(-22deg); }
      100% { transform: translateX(345px) skewX(-22deg); }
    }
    @keyframes cl-sweep-b {
      0%   { transform: translateX(345px) skewX(22deg); }
      42%  { transform: translateX(-95px) skewX(22deg); }
      100% { transform: translateX(-95px) skewX(22deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .cl-a, .cl-b { animation: none; opacity: 0; }
    }
  </style>

  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g clip-path="url(#cloop-logo)">
    <rect class="cl-a" x="0" y="-10" width="68" height="130" fill="url(#cl-bright)"/>
    <rect class="cl-b" x="0" y="-10" width="54" height="130" fill="url(#cl-steel)"/>
  </g>
</svg>
```

## Notes

- **Coprime cycle lengths (`3.8s` and `4.7s`)** ensure the crossing point shifts organically every pass so the loop feels alive rather than mechanical.
- Clip both bands strictly to `url(#cloop-logo)`.
