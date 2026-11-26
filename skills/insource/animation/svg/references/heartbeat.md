# Recipe: heartbeat — `/animation svg heartbeat`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Infinite ambient loop. Distinct from `pulse` (slow sinusoidal scale + blur halo). Delivers a crisp double-beat cardiac cadence (*lub-dub*) followed by a calm rest interval, with zero blur.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .hb-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      animation: lub-dub 1.8s ease-in-out infinite;
    }
    @keyframes lub-dub {
      0%   { transform: scale(1); }
      10%  { transform: scale(1.026); }
      20%  { transform: scale(1); }
      30%  { transform: scale(1.018); }
      44%  { transform: scale(1); }
      100% { transform: scale(1); }
    }
    @media (prefers-reduced-motion: reduce) {
      .hb-logo { animation: none; transform: none; }
    }
  </style>

  <g class="hb-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Clamp peak scale strictly below the uniform scale ceiling** (foundations §5). On 300×110, the clearance ceiling is `~1.03`; use `1.026` on the primary beat (10%) and `1.018` on the secondary beat (30%) so nothing ever touches or clips the viewport boundary.
- **Timing ratio**: compress both beats into the first ~44% of the cycle (`1.8s` total at small scale; scale loop duration per foundations §5) and hold steady at `scale(1)` for the remaining 56%.
- Lock `transform-box: view-box; transform-origin: (W/2)px (H/2)px`.
