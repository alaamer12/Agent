# Recipe: book — `/animation svg book`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `unroll` (top-edge `rotateX`) and `flip` (center-axis `rotateY`). Pins the hinge to the left spine `(0px, H/2)` so the right edge sweeps forward into view.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .book-logo {
      transform-box: view-box;
      transform-origin: 0px 55px;
      opacity: 0;
      animation: book-open 1.15s cubic-bezier(0.2, 0.85, 0.25, 1) forwards;
    }
    @keyframes book-open {
      0%   { transform: perspective(440px) rotateY(88deg); opacity: 0; }
      26%  { opacity: 1; }
      100% { transform: perspective(440px) rotateY(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .book-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="book-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Start at `rotateY(88deg)`, never `90deg`** (avoids zero-width edge-on dropout in Chromium).
- Pin `transform-box: view-box; transform-origin: 0px (H/2)px` (use `(W)px (H/2)px` with `rotateY(-88deg)` for right-to-left Arabic book covers).
- Perspective `≈ 1.45 × W` (`440px` at W=300); ramp opacity to `1` by `26%` to mask early foreshortening.
