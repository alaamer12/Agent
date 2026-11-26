# Recipe: wave-loop — `/animation svg wave-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `shimmer` (diagonal X-axis gloss sweep) and `tide` (one-shot wavy reveal). A soft horizontal gradient band bobs smoothly up and down strictly inside the logo clip.

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
    <linearGradient id="..." x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.34"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .wl-band { animation: wl-bob 3.4s ease-in-out infinite; }
    @keyframes wl-bob {
      0%, 100% { transform: translateY(-28px); }
      50%      { transform: translateY(84px); }
    }
    @media (prefers-reduced-motion: reduce) {
      .wl-band { animation: none; opacity: 0; }
    }
  </style>

  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g clip-path="url(#wloop-logo)">
    <rect class="wl-band" x="0" y="0" width="300" height="34" fill="url(#wloop-grad)"/>
  </g>
</svg>
```

## Notes

- **Clip strictly to `url(#wloop-logo)`** so the reflection illuminates only the filled shapes and leaves counters crisp.
- Peak white opacity `0.34` adds calm aquatic depth without washing out midtone brand colors.
