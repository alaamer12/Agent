# Recipe: tumble — `/animation svg tumble`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `pendulum` (top-edge pivot swing) and `elastic-entrance` (infinite 180° spin loop). Centers rotation at `(W/2, H/2)` with gentle damped oscillation.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .tumble-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
      animation: coin-tumble 1.25s cubic-bezier(0.22, 0.85, 0.28, 1) forwards;
    }
    @keyframes coin-tumble {
      0%   { transform: translate(-20px, -6px) rotate(-9deg); opacity: 0; }
      22%  { opacity: 1; }
      52%  { transform: translate(2.5px, 1px) rotate(2.1deg); }
      76%  { transform: translate(-1px, -0.5px) rotate(-0.8deg); }
      100% { transform: translate(0px, 0px) rotate(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .tumble-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="tumble-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Cap post-entry counter-tilt to `≤ 2.2°`** on tight 300×110 frames so corners clear the top/bottom edges (`150 · sin(2.1°) ≈ 5.5px` mitigated by the initial fade-in and quick damping to `-0.8° → 0°`).
- Combine `translate` and `rotate` in one transform list on `.tumble-logo` with `transform-box: view-box`.
