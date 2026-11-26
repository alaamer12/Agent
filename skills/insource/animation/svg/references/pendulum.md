# Recipe: pendulum — `/animation svg pendulum`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `unroll` (3-D `rotateX` perspective hinge) and `elastic-entrance` (infinite scale+rotate wobble loop). The artwork pivots in 2-D from top-centre `(W/2, 0)` and settles through a damped harmonic swing to exact rest.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .pendulum-logo {
      transform-box: view-box;
      transform-origin: 150px 0px;
      opacity: 0;
      animation: pendulum-swing 1.5s cubic-bezier(0.35, 0, 0.45, 1) forwards;
    }
    @keyframes pendulum-swing {
      0%   { transform: rotate(-7.5deg); opacity: 0; }
      18%  { opacity: 1; }
      30%  { transform: rotate(4.2deg); }
      52%  { transform: rotate(-2.2deg); }
      72%  { transform: rotate(1.0deg); }
      88%  { transform: rotate(-0.35deg); }
      100% { transform: rotate(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .pendulum-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="pendulum-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Check corner clearance before choosing start angle** (foundations §5). Rotating `(x, y)` around `(W/2, 0)` swings the bottom corners laterally by `≈ H · sin(θ)` and vertically by `(W/2) · sin(θ)`. On a tight 300×110 frame, cap peak swing at `±7.5°` (and ramp opacity in by 18% while moving inward) so edges stay clean.
- **Damping ratio**: alternate signs with ~0.55× amplitude decay per half-cycle (`-7.5° → +4.2° → -2.2° → +1.0° → -0.35° → 0°`). Too few oscillations reads as a twitch; too many drags past 2s.
- Always pair `transform-box: view-box` with `transform-origin: (W/2)px 0px` so the hinge stays pinned to the top edge.
