# Recipe: stamp — `/animation svg stamp`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `drop` (vertical gravity fall with non-uniform squash) and `engrave` (embossed raking light). The logo strikes firmly onto the stage with a tight clearance-safe micro-recoil while a thin brand-coloured concentric shockwave ring expands outward and dissipates.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .stamp-logo {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
      animation: stamp-press 0.95s cubic-bezier(0.2, 0.9, 0.3, 1) forwards;
    }
    .stamp-ring {
      transform-box: view-box;
      transform-origin: 150px 55px;
      opacity: 0;
      animation: stamp-wave 0.72s cubic-bezier(0.15, 0.85, 0.3, 1) 0.14s forwards;
    }
    @keyframes stamp-press {
      0%   { transform: scale(1.03); opacity: 0; }
      16%  { transform: scale(0.985); opacity: 1; }
      38%  { transform: scale(1.008); }
      100% { transform: scale(1); opacity: 1; }
    }
    @keyframes stamp-wave {
      0%   { transform: scale(0.55); opacity: 0.75; stroke-width: 2.2; }
      100% { transform: scale(1.0); opacity: 0; stroke-width: 0.4; }
    }
    @media (prefers-reduced-motion: reduce) {
      .stamp-logo { animation: none; opacity: 1; transform: none; }
      .stamp-ring { animation: none; opacity: 0; }
    }
  </style>

  <ellipse class="stamp-ring" cx="150" cy="55" rx="146" ry="51" fill="none" stroke="#0494a4" stroke-width="2"/>
  <g class="stamp-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Clamp the initial strike scale to the edge-clearance ceiling** (`1.03` on 300×110, foundations §5). The tactile impact comes from the fast opacity snap (`0→1` by 16%) plus the brief compression recoil (`0.985` → `1.008` → `1`), not from an oversized 1.4× zoom that shears off the viewport.
- **Use an `<ellipse>` (or `<circle>` for square logos) for the shockwave**, sized to `(W/2 - 4, H/2 - 4)` so even at final `scale(1.0)` the ring stays strictly inside the viewport and fades to `opacity: 0` cleanly. Never draw the ring with `<path>` (keeps path count equal to source per foundations §4).
- Place the shockwave *behind* the logo group so it radiates outward from under the stamped mark.
