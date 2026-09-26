# Recipe: pinwheel — `/svg-animate pinwheel`

The logo is revealed by wedges that each scale up from the centre on their own
beat, so the reveal turns like a turbine instead of spreading evenly.
One-shot; ends pixel-exact.

Distinct from `iris`, which grows one circle's radius from the centre. Same
origin, but segmentation plus stagger is what makes it read as rotation.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="pinwheel-clip" clipPathUnits="userSpaceOnUse">
      <polygon points="150,55 550.0,55.0 413.1,207.6"/>
      <polygon points="150,55 413.1,207.6 150.0,330.0"/>
      <!-- … 8 wedges tiling the full turn … -->
    </clipPath>
    <style>
      #pinwheel-clip polygon {
        transform-box: view-box;
        transform-origin: 150px 55px;
        transform: scale(0);
        animation: pin-open 0.85s cubic-bezier(0.3, 0.9, 0.3, 1) both;
      }
      #pinwheel-clip polygon:nth-child(1) { animation-delay: 0.000s; }
      #pinwheel-clip polygon:nth-child(2) { animation-delay: 0.075s; }
      /* … one delay per wedge … */
      @keyframes pin-open { to { transform: scale(1); } }
      @media (prefers-reduced-motion: reduce) {
        #pinwheel-clip polygon { animation: none; transform: none; }
      }
    </style>
  </defs>

  <g clip-path="url(#pinwheel-clip)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **CSS transforms on `<clipPath>` children do animate** — measured, both the
  CSS form and SMIL `animateTransform`. This is the fact that makes the style
  buildable; `iris` only ever proved SMIL on `r`.
- **`transform-box: view-box` is required.** Without it the origin resolves
  against each wedge's own bounding box, so the wedges shrink toward
  themselves rather than toward the centre, and the sweep collapses into a
  mess. Then `transform-origin` in px is in viewBox coordinates.
- **Wedge radius must clear the canvas.** A wedge spanning θ at radius R has a
  chord at distance `R·cos(θ/2)` from the centre; with 8 wedges (θ = 45°) and
  R = 400 that is 369, comfortably past this canvas's maximum corner distance
  of 160. Too small an R leaves the corners permanently clipped — and unlike
  most defects, that one is invisible until you look at the frame edges.
- `transform: scale(0)` as the base value means the logo is hidden before the
  animation starts, so `both` fill is not strictly needed — but keep it, or a
  slow first paint flashes the whole logo.
- Wedge count 6–12. Fewer reads as a shutter opening; more approaches `iris`
  and loses the point. Delay stagger ≈ 0.075s per wedge.
- Reverse the delays for the opposite spin direction.
- **Verified in Chromium 153 only.**
