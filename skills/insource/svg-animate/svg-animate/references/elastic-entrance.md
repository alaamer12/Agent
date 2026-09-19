# Recipe: elastic-entrance — `/svg-animate elastic`

Playful full-logo intro loop: the logo elastically scales/rotates in,
wobbles like it landed with a bounce, glows softly, then fades out and
repeats. The whole `<g>` transforms as one — no stroke/mask work.

Derived from an 1800×1800 reference that also framed the logo with a pulsing
hexagon on black. The hexagon was brand framing — optional here; the core
treatment is the keyframed group + glow filter.

## Template (hero scale, two paths)

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1800" viewBox="0 0 1800 1800" version="1.1">
  <defs>
    <filter id="soft-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="15" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <style>
    .bg { fill: #000000; } /* optional dark stage — drop if source has none */

    .logo-group {
      transform-box: fill-box;      /* robust for any viewBox: center on the */
      transform-origin: center;     /* logo's own bbox, not the viewport    */
      animation: logo-play 8s cubic-bezier(0.25, 1, 0.5, 1) infinite;
    }
    .logo-path { fill: #ffffff; }

    @keyframes logo-play {
      /* 0-2s: elastic entrance */
      0%   { transform: scale(0) rotate(-180deg); opacity: 0; }
      15%  { transform: scale(1.2) rotate(10deg); opacity: 1; }
      25%  { transform: scale(0.9) rotate(-5deg); }
      /* 3-5s: wobble / ripple */
      35%  { transform: scale(1.05) skewX(2deg); }
      40%  { transform: scale(0.98) skewY(-2deg); }
      45%  { transform: scale(1.02) skewX(-1deg); }
      50%  { transform: scale(1) skewY(0); }
      /* 6-8s: stable glow, then exit */
      60%  { filter: url(#soft-glow); transform: scale(1); }
      80%  { filter: url(#soft-glow); opacity: 1; }
      95%  { transform: scale(1); opacity: 0; }
      100% { transform: scale(0); opacity: 0; }
    }
  </style>

  <rect class="bg" width="100%" height="100%" />

  <g class="logo-group">
    <path d="..." fill="#fafbfb" fill-rule="evenodd"/>
    <path d="..." fill="#4a7bf9" fill-rule="evenodd"/>
  </g>
</svg>
```

## Notes

- **Keep every original path as a direct child of the animated group** with
  its real `fill` and `fill-rule` — this recipe transforms, never re-paints.
  Fill colors come from the source, not the reference (`.logo-path { fill:
  #ffffff }` in the reference was a brand-specific override; drop it when
  the source has real colors).
- **`transform-box: fill-box`** centers the scale/rotate on the logo's own
  bounding box. The reference relied on a centered logo in a square viewBox;
  fill-box makes the recipe work on wordmarks and off-center art too.
- **Glow blur** scales with logo size: `stdDeviation ≈ W/120` (reference: 15
  at W=1800). Too-large blur on a small logo turns it to mush.
- **Loop timing**: keep the 8s cycle unless the user asks otherwise — the
  entrance/wobble/glow/fade rhythm is tuned to it. Percentage keyframe
  structure stays fixed; only `s` durations scale.
- **Optional hexagon framing** from the reference (only if the user wants the
  badge look): a `<polygon>` with its own pulse keyframes, drawn around the
  logo. Recreate it relative to the target's viewBox center — never copy the
  1800-space coordinates.
- `filter: url(#soft-glow)` applied via a keyframe only takes effect while
  that keyframe window is active (60–80%) in most browsers — the glow turns
  itself off as the logo fades. That matches the reference behavior.
