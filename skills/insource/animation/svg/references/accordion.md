# Recipe: accordion — `/animation svg accordion`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `unroll` (single top-hinged `rotateX`) and `flip` (single centre-hinged `rotateY`). Vertical clipped strips unfold sequentially along Y from individual left hinges like pleated brochure panels flattening into one plane.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0.00" y="0" width="50.40" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="50.00" y="0" width="50.40" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="100.00" y="0" width="50.40" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="150.00" y="0" width="50.40" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="200.00" y="0" width="50.40" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="250.00" y="0" width="50.00" height="110"/></clipPath>
  </defs>

  <style>
    .a0 { clip-path: url(#acc-0); transform-box: view-box; transform-origin: 0.0px 55px; opacity: 0; animation: acc-open 0.78s cubic-bezier(0.22, 0.85, 0.28, 1) 0.04s forwards; }
    .a1 { clip-path: url(#acc-1); transform-box: view-box; transform-origin: 50.0px 55px; opacity: 0; animation: acc-open 0.78s cubic-bezier(0.22, 0.85, 0.28, 1) 0.13s forwards; }
    .a2 { clip-path: url(#acc-2); transform-box: view-box; transform-origin: 100.0px 55px; opacity: 0; animation: acc-open 0.78s cubic-bezier(0.22, 0.85, 0.28, 1) 0.22s forwards; }
    .a3 { clip-path: url(#acc-3); transform-box: view-box; transform-origin: 150.0px 55px; opacity: 0; animation: acc-open 0.78s cubic-bezier(0.22, 0.85, 0.28, 1) 0.31s forwards; }
    .a4 { clip-path: url(#acc-4); transform-box: view-box; transform-origin: 200.0px 55px; opacity: 0; animation: acc-open 0.78s cubic-bezier(0.22, 0.85, 0.28, 1) 0.40s forwards; }
    .a5 { clip-path: url(#acc-5); transform-box: view-box; transform-origin: 250.0px 55px; opacity: 0; animation: acc-open 0.78s cubic-bezier(0.22, 0.85, 0.28, 1) 0.49s forwards; }
    @keyframes acc-open {
      0%   { transform: perspective(420px) rotateY(-88deg); opacity: 0; }
      25%  { opacity: 1; }
      100% { transform: perspective(420px) rotateY(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .a0, .a1, .a2, .a3, .a4, .a5 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="a0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="a1"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="a2"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="a3"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="a4"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="a5"><use href="#path-teal"/><use href="#path-navy"/></g>
</svg>
```

## Notes

- **Use `rotateY(-88deg)`, never `-90deg`** (same browser rule as `unroll` — at exactly 90° a strip collapses to zero width and can drop out for a frame).
- **One `transform-origin` per strip** pinned to that strip's own left edge (`x_i px, H/2 px`) with `transform-box: view-box`. Add `+0.4u` width overlap on interior clips so fractional zoom cannot show vertical seams when flat.
- **Strip count `N = 5–6`** (each strip ≥ 4·F wide). Perspective ≈ `1.4·W` (420px at W=300), consistent with `flip` and `unroll`.
