# Recipe: starburst — `/animation svg starburst`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `pinwheel` (staggered turbine wedges) and `hexagon` (convex 6-gon). A 12-point alternating outer/inner radius `<polygon>` expands rapidly from center.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse">
      <polygon class="star-poly" points="150.0,-305.0 204.4,-147.8 330.0,-256.8 298.5,-93.5 461.8,-125.0 352.8,0.6 510.0,55.0 352.8,109.4 461.8,235.0 298.5,203.5 330.0,366.8 204.4,257.8 150.0,415.0 95.6,257.8 -30.0,366.8 1.5,203.5 -161.8,235.0 -52.8,109.4 -210.0,55.0 -52.8,0.6 -161.8,-125.0 1.5,-93.5 -30.0,-256.8 95.6,-147.8"/>
    </clipPath>
  </defs>

  <style>
    .star-poly {
      transform-box: view-box;
      transform-origin: 150px 55px;
      transform: scale(0) rotate(-18deg);
      animation: star-pop 1.15s cubic-bezier(0.2, 0.9, 0.28, 1) forwards;
    }
    @keyframes star-pop { to { transform: scale(1) rotate(0deg); } }
    @media (prefers-reduced-motion: reduce) {
      .star-poly { animation: none; transform: none; }
    }
  </style>

  <g clip-path="url(#star-clip)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Inner valley radius must clear the farthest canvas corner**: set `r_inner ≥ hypot(W/2, H/2) + 45` (`210u` on 300×110) and `r_outer ≈ 1.7 × r_inner` (`360u`). If `r_inner` is too small, the star's notches stay bitten into the final corners!
- Pure CSS transform inside `<clipPath>` — zero SMIL needed, 0.00% end drift.
