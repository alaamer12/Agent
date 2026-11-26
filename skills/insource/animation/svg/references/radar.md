# Recipe: radar — `/animation svg radar`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `pinwheel` (one-shot reveal of scaling wedges) and `comet` (outline stroke dash). The logo stays crisp and solid while a translucent rotating beacon wedge sweeps 360° inside the artwork silhouette.

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
    <linearGradient id="..." x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.45"/>
      <stop offset="65%" stop-color="#0494a4" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#0494a4" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <style>
    .radar-wedge {
      transform-box: view-box;
      transform-origin: 150px 55px;
      animation: radar-spin 2.8s linear infinite;
    }
    @keyframes radar-spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .radar-wedge { animation: none; opacity: 0; }
    }
  </style>

  <g>
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <g clip-path="url(#radar-logo)">
    <polygon class="radar-wedge" points="150,55 340,-35 340,75" fill="url(#radar-beam)"/>
  </g>
</svg>
```

## Notes

- **Clip the rotating wedge to `url(#radar-logo)`** so the beacon illuminates only the logo body and leaves counters and transparent canvas untouched.
- **Wedge radius must exceed `hypot(W/2, H/2)`** (`≥ 180u` on 300×110; here `190u`) so the beam sweeps cleanly across the farthest corners of wide wordmarks without cutting short.
- Use linear easing (`2.8s linear infinite`) for steady mechanical sweep rotation around `(W/2)px (H/2)px` with `transform-box: view-box`.
