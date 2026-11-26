# Recipe: domino — `/animation svg domino`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `accordion` (3-D `rotateY` folding pleats) and `louver` (width mask). Each vertical clipped strip pivots in 2-D from its own bottom-left corner (`rotate(-16deg → 0deg)`).

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="0.00" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="37.50" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="75.00" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="112.50" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="150.00" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="187.50" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="225.00" y="0" width="37.85" height="110"/></clipPath>
    <clipPath id="..." clipPathUnits="userSpaceOnUse"><rect x="262.50" y="0" width="37.50" height="110"/></clipPath>
  </defs>

  <style>
    .d0 { clip-path: url(#dom-0); transform-box: view-box; transform-origin: 0.0px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.040s forwards; }
    .d1 { clip-path: url(#dom-1); transform-box: view-box; transform-origin: 37.5px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.115s forwards; }
    .d2 { clip-path: url(#dom-2); transform-box: view-box; transform-origin: 75.0px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.190s forwards; }
    .d3 { clip-path: url(#dom-3); transform-box: view-box; transform-origin: 112.5px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.265s forwards; }
    .d4 { clip-path: url(#dom-4); transform-box: view-box; transform-origin: 150.0px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.340s forwards; }
    .d5 { clip-path: url(#dom-5); transform-box: view-box; transform-origin: 187.5px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.415s forwards; }
    .d6 { clip-path: url(#dom-6); transform-box: view-box; transform-origin: 225.0px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.490s forwards; }
    .d7 { clip-path: url(#dom-7); transform-box: view-box; transform-origin: 262.5px 110px; opacity: 0; animation: dom-fall 0.68s cubic-bezier(0.22, 0.88, 0.28, 1) 0.565s forwards; }
    @keyframes dom-fall {
      0%   { transform: rotate(-16deg) translateY(8px); opacity: 0; }
      26%  { opacity: 1; }
      100% { transform: rotate(0deg) translateY(0px); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .d0, .d1, .d2, .d3, .d4, .d5, .d6, .d7 { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="d0"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d1"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d2"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d3"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d4"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d5"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d6"><use href="#path-teal"/><use href="#path-navy"/></g>
  <g class="d7"><use href="#path-teal"/><use href="#path-navy"/></g>
</svg>
```

## Notes

- **One `transform-origin` per strip** at `(x_i px, H px)` with `transform-box: view-box`.
- Add `+0.35u` width overlap on interior clips so resting strips leave zero hairline seam lines.
- Strip count `N = 8` (`37.5u` wide on 300px, comfortably `> 7·F`).
