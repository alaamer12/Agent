# Recipe: shimmer — `/animation svg shimmer`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `chrome-liquid` (8s chrome draw + liquid fill sequence) and `pulse` (scale+glow breathing). The solid logo stays completely crisp at rest while a soft skewed white specular sheen glides across periodically.

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
      <stop offset="45%" stop-color="#ffffff" stop-opacity="0.48"/>
      <stop offset="55%" stop-color="#ffffff" stop-opacity="0.48"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .shimmer-bar {
      transform: translateX(-110px) skewX(-22deg);
      animation: shimmer-glide 3.2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }
    @keyframes shimmer-glide {
      0%   { transform: translateX(-110px) skewX(-22deg); }
      36%  { transform: translateX(350px) skewX(-22deg); }
      100% { transform: translateX(350px) skewX(-22deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .shimmer-bar { animation: none; opacity: 0; }
    }
  </style>

  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g clip-path="url(#shimmer-logo)">
    <rect class="shimmer-bar" x="0" y="-10" width="80" height="130" fill="url(#shimmer-grad)"/>
  </g>
</svg>
```

## Notes

- **Clip the sheen strictly to the logo silhouette (`clip-path="url(#shimmer-logo)"`)** so light never spills onto transparent canvas or into letterform counters.
- **Idle dwell is essential**: keep the sweep in the first ~36% of the cycle and park off-edge for the remaining 64%. Continuous back-to-back sweeps feel restless instead of refined.
- Sheen bar width `≈ 0.26·W`, skewed `-22deg`, translating from `-0.36·W` to `+1.16·W`. Peak stop opacity `0.45–0.55` reads cleanly on dark fills without washing out light brand colours.
