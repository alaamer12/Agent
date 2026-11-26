# Recipe: drop — `/animation svg drop`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `rise` (staggered bottom-up translate) and `elastic-entrance` (infinite loop with glow). The logo drops from above and lands with a tight, clearance-safe squash-and-stretch settle anchored to its baseline.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .drop-logo {
      transform-box: view-box;
      transform-origin: 150px 108px;
      opacity: 0;
      animation: squash-drop 1.1s cubic-bezier(0.25, 0.8, 0.3, 1) forwards;
    }
    @keyframes squash-drop {
      0%   { transform: translateY(-22px) scaleX(0.96) scaleY(1.04); opacity: 0; }
      22%  { opacity: 1; }
      46%  { transform: translateY(0px) scaleX(1.024) scaleY(0.93); }
      66%  { transform: translateY(-3px) scaleX(0.988) scaleY(1.022); }
      84%  { transform: translateY(0px) scaleX(1.008) scaleY(0.99); }
      100% { transform: translateY(0px) scaleX(1) scaleY(1); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .drop-logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="drop-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Anchor `transform-origin` at the bottom baseline** (`W/2, y_max`, e.g., `150px 108px`). That way downward squash (`scaleY < 1`) compresses toward the floor instead of floating mid-air.
- **Clamp `scaleX` and `scaleY` strictly to the edge-clearance ceiling** (foundations §5). On 300×110 (`x_max ≈ 296`), `scaleX(1.024)` expands each side by only `3.5px` (inside the 4px margin), and rebound `scaleY(1.022)` expands upward by `2.3px` (inside the 4px top margin). Never copy cartoon `scaleX(1.25)` values onto tight viewBoxes — the viewport will shear the edges off.
- Opacity finishes by 22% so the initial drop-in from `-0.2·H` blends smoothly.
