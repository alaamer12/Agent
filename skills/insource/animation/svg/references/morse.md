# Recipe: morse — `/animation svg morse`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `draw-fill` (continuous single pen line) and `comet` (infinite single white spark). Uses a repeating dot-dash `stroke-dasharray: 5 4 14 4 5 6` scrolling smoothly before fading into exact fills.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." fill-rule="evenodd"/>
    <path id="..." d="..." fill-rule="evenodd"/>
  </defs>

  <style>
    .morse-sig {
      fill: none;
      stroke: #0494a4;
      stroke-width: 1.25;
      stroke-linecap: round;
      stroke-dasharray: 5 4 14 4 5 6;
      stroke-dashoffset: 240;
      opacity: 0;
      animation: morse-run 1.35s linear forwards, morse-fade 1.65s linear forwards;
    }
    .morse-solid { opacity: 0; animation: morse-in 0.6s ease-out 1.05s forwards; }
    @keyframes morse-run { from { stroke-dashoffset: 240; } to { stroke-dashoffset: 0; } }
    @keyframes morse-fade { 0% { opacity: 0; } 12% { opacity: 1; } 72% { opacity: 1; } 100% { opacity: 0; } }
    @keyframes morse-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .morse-sig { animation: none; opacity: 0; }
      .morse-solid { animation: none; opacity: 1; }
    }
  </style>

  <g class="morse-sig">
    <use href="#path-teal" fill="none"/>
    <use href="#path-navy" fill="none"/>
  </g>
  <g class="morse-solid">
    <use href="#path-teal" stroke="none" fill="#0494a4"/>
    <use href="#path-navy" stroke="none" fill="#040c24"/>
  </g>
</svg>
```

## Notes

- **Bare `<path>` defs in `<defs>`** (no `fill`/`stroke` on the `<path>` definition) so `.morse-sig` `<use fill="none">` renders strictly as dashed strokes while `.morse-solid` carries verbatim brand hexes.
- Combine `morse-run` and `morse-fade` in a single `animation` shorthand on `.morse-sig` (foundations §6).
