# Recipe: fan — `/animation svg fan`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `pinwheel` (center-pivoted 360° turbine). Pivots off the bottom-left corner `(0, H)` across a ~96° quadrant arc.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse">
      <polygon points="0,110 -14.7,-309.7 108.7,-295.7"/>
      <polygon points="0,110 101.6,-297.5 216.3,-250.0"/>
      <polygon points="0,110 210.0,-253.7 307.2,-176.4"/>
      <polygon points="0,110 302.1,-181.8 374.2,-80.7"/>
      <polygon points="0,110 370.8,-87.2 412.3,29.9"/>
      <polygon points="0,110 410.8,22.7 418.4,146.6"/>
    </clipPath>
  </defs>

  <style>
    #fan-clip polygon {
      transform-box: view-box;
      transform-origin: 0px 110px;
      transform: scale(0);
      animation: fan-open 0.72s cubic-bezier(0.22, 0.88, 0.3, 1) both;
    }
    #fan-clip polygon:nth-child(1) { animation-delay: 0.000s; }
    #fan-clip polygon:nth-child(2) { animation-delay: 0.095s; }
    #fan-clip polygon:nth-child(3) { animation-delay: 0.190s; }
    #fan-clip polygon:nth-child(4) { animation-delay: 0.285s; }
    #fan-clip polygon:nth-child(5) { animation-delay: 0.380s; }
    #fan-clip polygon:nth-child(6) { animation-delay: 0.475s; }
    @keyframes fan-open { to { transform: scale(1); } }
    @media (prefers-reduced-motion: reduce) {
      #fan-clip polygon { animation: none; transform: none; }
    }
  </style>

  <g clip-path="url(#fan-clip)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Wedge radius floor**: `R ≥ hypot(W, H) + 80` (`420u` on 300×110) so the diagonal corner `(W, 0)` is covered cleanly.
- Overlap adjacent wedge angles by `+1.0°` to prevent subpixel radial seam lines at fractional zoom.
- Set `transform-box: view-box; transform-origin: 0px (H)px` (or `(W)px (H)px` for a bottom-right RTL fan).
