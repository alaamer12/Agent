# Recipe: draw-fill — `/svg-animate draw`

Self-drawing logo, one-shot: every outline traces itself with its own color,
then the fills fade in on top. Calm, precise, "pen signing the logo" feel.

Derived from an 1800×1800 reference. Scale numbers per the SKILL.md table.

## Template (hero scale, two paths)

The whole treatment is a `<style>` block plus the original paths with classes
added — no defs/uses needed. fill-rule stays inline on each path, untouched.

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
    animation: draw 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards,
               fill-in 1s ease-out 2s forwards;
  }
  .path-white { stroke: #fafbfb !important; fill: #fafbfb; }
  .path-blue  { stroke: #4a7bf9 !important; fill: #4a7bf9; }

  @keyframes draw    { to { stroke-dashoffset: 0; } }
  @keyframes fill-in { to { fill-opacity: 1; } }
</style>
<path class="logo-path path-white" d="..." stroke="none" fill="#fafbfb" fill-rule="evenodd"/>
<path class="logo-path path-blue"  d="..." stroke="none" fill="#4a7bf9" fill-rule="evenodd"/>
</svg>
```

## Notes

- **Dash values**: `15000` fit the reference's ~3000-unit contours. Set
  `stroke-dasharray/-offset` ≥ the target's longest subpath from
  `extract_paths.py --lengths` (a value 1.2–2× the longest subpath is ideal —
  large enough for a complete draw, small enough for a visible stroke).
- **Two animations on one element**: the draw runs first; `fill-in` starts at
  `2s` (just before draw ends at 2.5s) so color lands as the pen finishes.
  Scale both timings together: fill delay ≈ draw duration − 0.5s.
- Each path draws in its own color (stroke matches fill) — keep that pairing
  per path, renaming classes to the actual color roles.
- `stroke="none"` inline is overridden by the class `stroke` via `!important`
  in the reference; cleaner is to drop the inline `stroke="none"` entirely.
  Either works — pick one and keep the file consistent.
- One-shot (`forwards`, no `infinite`) — the logo ends fully drawn and filled.
