# Recipe: trapdoor — `/animation svg trapdoor`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The floor-hinged counterpart to `unroll` (top-edge hinge). Pivots around `(W/2, H)` using positive `rotateX(88deg → 0deg)` so the top edge lifts upward out of the baseline.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .trap-logo {
      transform-box: view-box;
      transform-origin: 150px 110px;
      opacity: 0;
      animation: trap-lift 1.1s cubic-bezier(0.2, 0.85, 0.25, 1) forwards;
    }
    @keyframes trap-lift {
      0%   { transform: perspective(420px) rotateX(88deg); opacity: 0; }
      28%  { opacity: 1; }
      100% { transform: perspective(420px) rotateX(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .trap-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="trap-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Start at `rotateX(88deg)`, never `90deg`**, with `transform-box: view-box; transform-origin: (W/2)px (H)px`.
- Perspective `≈ 1.4 × W` (`420px` at W=300). Lands at `rotateX(0deg)` with 0.00% end drift.
