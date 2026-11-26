# Recipe: pendulum-loop — `/animation svg pendulum-loop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The calm infinite counterpart to one-shot `pendulum` and distinct from `float` (vertical levitation). Rocks softly around `(W/2, 0)` with zero blur.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .ploop-logo {
      transform-box: view-box;
      transform-origin: 150px 0px;
      animation: metro-sway 4.2s ease-in-out infinite;
    }
    @keyframes metro-sway {
      0%, 100% { transform: rotate(0deg); }
      25%      { transform: rotate(1.1deg); }
      75%      { transform: rotate(-1.1deg); }
    }
    @media (prefers-reduced-motion: reduce) {
      .ploop-logo { animation: none; transform: none; }
    }
  </style>

  <g class="ploop-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Ultra-tight angle clamp**: cap swing at `±1.1°` on 300×110 (`150 · sin(1.1°) ≈ 2.9px` vertical corner lift, safely within edge margins). Larger angles require extra viewBox padding.
- Smooth `ease-in-out` across `0% → 25% → 75% → 100%` keeps reversals weightless.
