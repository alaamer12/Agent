# Recipe: sprint — `/animation svg sprint`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `flip` (3-D Y rotation) and `rise` (vertical fade). Artwork dashes horizontally into frame leaning forward in italic `skewX`, brakes slightly past centre with a brief counter-skew, and snaps crisp to vertical.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .sprint-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
      animation: skew-sprint 1.0s cubic-bezier(0.18, 0.88, 0.25, 1) forwards;
    }
    @keyframes skew-sprint {
      0%   { transform: translateX(-34px) skewX(-16deg); opacity: 0; }
      24%  { opacity: 1; }
      68%  { transform: translateX(2px) skewX(3.5deg); }
      86%  { transform: translateX(-0.8px) skewX(-1deg); }
      100% { transform: translateX(0px) skewX(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .sprint-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="sprint-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Derive skew and overshoot from edge clearance** (foundations §5). `skewX(θ)` shifts top/bottom edges horizontally by `(H/2)·tan(θ)`. At the brake frame (68%), `translateX(2px) skewX(3.5deg)` shifts corners by `< 5.4px` while the starting `-16deg` lean happens during the `translateX(-34px)` entrance fade-in.
- **The counter-skew at 68% (`+3.5deg`) is what sells the braking inertia.** Without it, the entrance reads as a generic slide-in.
- Ends at `translateX(0) skewX(0)` — 0.00% drift against the source.
