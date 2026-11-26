# Recipe: zipper — `/animation svg zipper`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `assemble` (scattered rectangular fragments with rotation) and `blinds` (stationary slats growing height). Horizontal clipped strips slide horizontally from alternating left and right offsets and interlock cleanly into the finished logo.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="0.00" width="300" height="18.58"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="18.33" width="300" height="18.58"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="36.67" width="300" height="18.58"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="55.00" width="300" height="18.58"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="73.33" width="300" height="18.58"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="91.67" width="300" height="18.33"/></clipPath>
  </defs>

  <style>
    .z0 { clip-path: url(#zip-0); opacity: 0; animation: zip-in-0 0.72s cubic-bezier(0.2, 0.88, 0.25, 1) 0.040s forwards; }
    @keyframes zip-in-0 { 0% { transform: translateX(-44px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateX(0px); opacity: 1; } }
    .z1 { clip-path: url(#zip-1); opacity: 0; animation: zip-in-1 0.72s cubic-bezier(0.2, 0.88, 0.25, 1) 0.115s forwards; }
    @keyframes zip-in-1 { 0% { transform: translateX(44px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateX(0px); opacity: 1; } }
    .z2 { clip-path: url(#zip-2); opacity: 0; animation: zip-in-2 0.72s cubic-bezier(0.2, 0.88, 0.25, 1) 0.190s forwards; }
    @keyframes zip-in-2 { 0% { transform: translateX(-44px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateX(0px); opacity: 1; } }
    .z3 { clip-path: url(#zip-3); opacity: 0; animation: zip-in-3 0.72s cubic-bezier(0.2, 0.88, 0.25, 1) 0.265s forwards; }
    @keyframes zip-in-3 { 0% { transform: translateX(44px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateX(0px); opacity: 1; } }
    .z4 { clip-path: url(#zip-4); opacity: 0; animation: zip-in-4 0.72s cubic-bezier(0.2, 0.88, 0.25, 1) 0.340s forwards; }
    @keyframes zip-in-4 { 0% { transform: translateX(-44px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateX(0px); opacity: 1; } }
    .z5 { clip-path: url(#zip-5); opacity: 0; animation: zip-in-5 0.72s cubic-bezier(0.2, 0.88, 0.25, 1) 0.415s forwards; }
    @keyframes zip-in-5 { 0% { transform: translateX(44px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateX(0px); opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .z0, .z1, .z2, .z3, .z4, .z5 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="z0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="z1"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="z2"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="z3"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="z4"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="z5"><use href="#path-teal"/><use href="#path-navy"/></g>
</svg>
```

## Notes

- **Relies on the same browser rule as `assemble`**: a `clip-path: url(#...)` travels with the transformed `<g>` element, so each strip carries its slice of the artwork smoothly into alignment.
- **Strip count `N = round(H / max(18, 3.5·F))`** (6 strips of ~18.3u on the 300×110 test logo). Add `+0.25u` vertical overlap on interior strips to prevent subpixel seam lines at rest.
- **Offset amplitude ≈ `0.15·W`**, alternating sign (`-dx` on even rows, `+dx` on odd rows), with opacity ramping to `1` by 30% so clipped outer edges enter smoothly rather than popping against the viewport boundary.
