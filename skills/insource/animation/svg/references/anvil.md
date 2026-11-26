# Recipe: anvil — `/animation svg anvil`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `stamp` (uniform scale + radial ellipse shockwave) and `drop` (falling from top). Expands vertically from `scaleY(0.16)` anchored at the floor with twin escaping baseline ticks.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .anvil-logo {
      transform-box: view-box;
      transform-origin: 150px 108px;
      opacity: 0;
      animation: anvil-hit 0.95s cubic-bezier(0.2, 0.9, 0.28, 1) forwards;
    }
    .anvil-bar-l { opacity: 0; animation: impact-l 0.55s ease-out 0.28s forwards; }
    .anvil-bar-r { opacity: 0; animation: impact-r 0.55s ease-out 0.28s forwards; }
    @keyframes anvil-hit {
      0%   { transform: scaleY(0.16); opacity: 0; }
      28%  { transform: scaleY(1.022); opacity: 1; }
      54%  { transform: scaleY(0.978); }
      78%  { transform: scaleY(1.006); }
      100% { transform: scaleY(1); opacity: 1; }
    }
    @keyframes impact-l {
      0%   { transform: translateX(0px); opacity: 0.9; }
      100% { transform: translateX(-28px); opacity: 0; }
    }
    @keyframes impact-r {
      0%   { transform: translateX(0px); opacity: 0.9; }
      100% { transform: translateX(28px); opacity: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      .anvil-logo { animation: none; opacity: 1; transform: none; }
      .anvil-bar-l, .anvil-bar-r { animation: none; opacity: 0; }
    }
  </style>

  <g class="anvil-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <rect class="anvil-bar-l" x="115" y="106.5" width="32" height="2" rx="1" fill="#0494a4"/>
  <rect class="anvil-bar-r" x="153" y="106.5" width="32" height="2" rx="1" fill="#0494a4"/>
</svg>
```

## Notes

- **Anchor `transform-origin` at `(W/2)px (y_max)px`** (`150px 108px`) and clamp vertical overshoot to `scaleY(1.022)` so top marks stay safely inside the viewport.
- Decorative impact bars are `<rect>` elements (never `<path>`) that fire at `0.28s` and fade to `opacity: 0` cleanly.
