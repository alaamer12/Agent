# Recipe: carousel — `/animation svg carousel`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The 90° vertical counterpart to `zipper` (alternating horizontal strips). Six vertical clipped columns slide into lock from alternating `±0.24·H` vertical offsets.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0.00" y="0" width="50.35" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="50.00" y="0" width="50.35" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="100.00" y="0" width="50.35" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="150.00" y="0" width="50.35" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="200.00" y="0" width="50.35" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="250.00" y="0" width="50.00" height="110"/></clipPath>
  </defs>

  <style>
    .c0 { clip-path: url(#car-0); opacity: 0; animation: car-slot-0 0.74s cubic-bezier(0.2, 0.88, 0.25, 1) 0.040s forwards; }
    @keyframes car-slot-0 { 0% { transform: translateY(-26px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(0px); opacity: 1; } }
    .c1 { clip-path: url(#car-1); opacity: 0; animation: car-slot-1 0.74s cubic-bezier(0.2, 0.88, 0.25, 1) 0.120s forwards; }
    @keyframes car-slot-1 { 0% { transform: translateY(26px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(0px); opacity: 1; } }
    .c2 { clip-path: url(#car-2); opacity: 0; animation: car-slot-2 0.74s cubic-bezier(0.2, 0.88, 0.25, 1) 0.200s forwards; }
    @keyframes car-slot-2 { 0% { transform: translateY(-26px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(0px); opacity: 1; } }
    .c3 { clip-path: url(#car-3); opacity: 0; animation: car-slot-3 0.74s cubic-bezier(0.2, 0.88, 0.25, 1) 0.280s forwards; }
    @keyframes car-slot-3 { 0% { transform: translateY(26px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(0px); opacity: 1; } }
    .c4 { clip-path: url(#car-4); opacity: 0; animation: car-slot-4 0.74s cubic-bezier(0.2, 0.88, 0.25, 1) 0.360s forwards; }
    @keyframes car-slot-4 { 0% { transform: translateY(-26px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(0px); opacity: 1; } }
    .c5 { clip-path: url(#car-5); opacity: 0; animation: car-slot-5 0.74s cubic-bezier(0.2, 0.88, 0.25, 1) 0.440s forwards; }
    @keyframes car-slot-5 { 0% { transform: translateY(26px); opacity: 0; } 30% { opacity: 1; } 100% { transform: translateY(0px); opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .c0, .c1, .c2, .c3, .c4, .c5 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="c0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="c1"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="c2"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="c3"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="c4"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="c5"><use href="#path-teal"/><use href="#path-navy"/></g>
</svg>
```

## Notes

- **Clip-path travels with `<g>` transform** (same verified mechanism as `assemble` and `zipper`).
- Add `+0.35u` width overlap on interior columns so zero vertical seams show at rest.
- Ramp opacity to `1` by `30%` so columns glide out of soft fade instead of hard-clipping against the top/bottom viewport boundary.
