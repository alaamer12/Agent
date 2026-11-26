# Recipe: diamond — `/animation svg diamond`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `iris` (circular clip) and `pinwheel` (staggered radial wedges). A single 45°-rotated rhombus `<polygon>` expands from the canvas centre, giving crisp chamfered diagonal reveal edges.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse">
      <polygon class="dia-poly" points="150,-170 375,55 150,280 -75,55"/>
    </clipPath>
  </defs>

  <style>
    .dia-poly {
      transform-box: view-box;
      transform-origin: 150px 55px;
      transform: scale(0);
      animation: dia-open 1.2s cubic-bezier(0.22, 0.85, 0.28, 1) forwards;
    }
    @keyframes dia-open { to { transform: scale(1); } }
    @media (prefers-reduced-motion: reduce) {
      .dia-poly { animation: none; transform: none; }
    }
  </style>

  <g clip-path="url(#diamond-clip)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Minimum half-diagonal `R = W/2 + H/2 + 20`.** Under the L1 norm (`|x - cx| + |y - cy| ≤ R`), a diamond covers every corner of `0..W × 0..H` only when `R ≥ W/2 + H/2`. Using `max(W, H)` alone clips the far corners of wide wordmarks.
- **`transform-box: view-box` + `transform-origin: (W/2)px (H/2)px`** locks the expansion centre in viewBox coordinates so asymmetric logos expand cleanly from the frame midpoint.
- Pure CSS transform on a `<clipPath>` polygon — no SMIL required, and ends at `scale(1)` with exact source pixels.
