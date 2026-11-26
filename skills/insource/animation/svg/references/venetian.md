# Recipe: venetian — `/animation svg venetian`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The true 3-D `rotateX` counterpart to 2-D `blinds` and the horizontal counterpart to `accordion`. Six horizontal clipped bands each pivot around their own vertical midpoint.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="0.00" width="300" height="18.63"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="18.33" width="300" height="18.63"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="36.67" width="300" height="18.63"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="55.00" width="300" height="18.63"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="73.33" width="300" height="18.63"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0" y="91.67" width="300" height="18.33"/></clipPath>
  </defs>

  <style>
    .v0 { clip-path: url(#ven-0); transform-box: view-box; transform-origin: 150px 9.2px; opacity: 0; animation: ven-flip 0.72s cubic-bezier(0.22, 0.85, 0.28, 1) 0.040s forwards; }
    .v1 { clip-path: url(#ven-1); transform-box: view-box; transform-origin: 150px 27.5px; opacity: 0; animation: ven-flip 0.72s cubic-bezier(0.22, 0.85, 0.28, 1) 0.125s forwards; }
    .v2 { clip-path: url(#ven-2); transform-box: view-box; transform-origin: 150px 45.8px; opacity: 0; animation: ven-flip 0.72s cubic-bezier(0.22, 0.85, 0.28, 1) 0.210s forwards; }
    .v3 { clip-path: url(#ven-3); transform-box: view-box; transform-origin: 150px 64.2px; opacity: 0; animation: ven-flip 0.72s cubic-bezier(0.22, 0.85, 0.28, 1) 0.295s forwards; }
    .v4 { clip-path: url(#ven-4); transform-box: view-box; transform-origin: 150px 82.5px; opacity: 0; animation: ven-flip 0.72s cubic-bezier(0.22, 0.85, 0.28, 1) 0.380s forwards; }
    .v5 { clip-path: url(#ven-5); transform-box: view-box; transform-origin: 150px 100.8px; opacity: 0; animation: ven-flip 0.72s cubic-bezier(0.22, 0.85, 0.28, 1) 0.465s forwards; }
    @keyframes ven-flip {
      0%   { transform: perspective(420px) rotateX(-86deg); opacity: 0; }
      25%  { opacity: 1; }
      100% { transform: perspective(420px) rotateX(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .v0, .v1, .v2, .v3, .v4, .v5 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="v0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="v1"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="v2"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="v3"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="v4"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="v5"><use href="#path-teal"/><use href="#path-navy"/></g>
</svg>
```

## Notes

- **Per-slat midpoint origin**: `transform-origin: (W/2)px (y_i + h/2)px` with `transform-box: view-box`.
- Use `rotateX(-86deg)` (never `-90deg`) and `+0.3u` vertical overlap on interior `<clipPath>` rects.
- Slat height `h ≥ 3.5·F` (`18.3u` on 110px height).
