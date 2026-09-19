# Recipe: loading-loop — `/svg-animate load`

Progress-loader feel: outlines draw themselves and reverse, forever. The
fills never appear — this is a pure-line loading treatment.

Derived from an 1800×1800 reference. Scale numbers per the SKILL.md table.

## Template (hero scale, two paths)

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1800" viewBox="0 0 1800 1800" version="1.1">
<style>
  .logo-path {
    stroke-dasharray: 15000;
    stroke-dashoffset: 15000;
    fill-opacity: 0;
    stroke-width: 3;
    stroke-linecap: round;
    stroke-linejoin: round;
    animation: load 4s ease-in-out infinite alternate;
  }
  .path-white { stroke: #fafbfb !important; }
  .path-blue  { stroke: #4a7bf9 !important; }

  @keyframes load {
    0%   { stroke-dashoffset: 15000; }
    100% { stroke-dashoffset: 0; }
  }
</style>
<path class="logo-path path-white" d="..." fill="#fafbfb" fill-rule="evenodd"/>
<path class="logo-path path-blue"  d="..." fill="#4a7bf9" fill-rule="evenodd"/>
</svg>
```

## Notes

- **`fill-opacity: 0` permanently** — unlike draw-fill, the color never
  lands. If the user actually wants the logo to complete and stay filled,
  they want `draw-fill`, not this. This style is for idle/loading states.
- **Both paths animate in sync** in the reference. Stagger them (per-path
  `animation-delay`, e.g. 0s and −2s) if the user wants a chasing effect.
- `infinite alternate` makes the draw reverse smoothly each cycle — do not
  use `forwards` here.
- **Dash values**: same rule as draw-fill — ≥ the target's longest subpath,
  ~1.2–2× ideal. Don't copy the reference's 15000 to a small logo.
- Keep `fill-rule="evenodd"` on every path even though fill is invisible:
  if the user later asks to convert this into a filled variant, the
  attribute must already be there.
- `stroke="none"` from the original must be removed/overridden for the
  stroke to show (the reference uses `!important` in the class).
