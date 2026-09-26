# Recipe: unroll — `/svg-animate unroll`

The logo falls into place around a fixed top hinge, like a sheet of paper being
unrolled toward the viewer. One-shot; ends pixel-exact.

Distinct from `flip`, which rotates a card about its **centre** on Y. Different
axis *and* different origin: this one pivots on the top edge, so the bottom
travels and the top stays put.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .logo {
      transform-box: view-box;
      transform-origin: 150px 0px;
      opacity: 0;
      animation: unroll-in 1.1s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    @keyframes unroll-in {
      0%   { transform: perspective(420px) rotateX(-88deg); opacity: 0; }
      28%  { opacity: 1; }
      100% { transform: perspective(420px) rotateX(0deg); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .logo { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **The origin is the effect.** `transform-origin: 150px 0px` puts the hinge on
  the top edge. Move it to `center` and you have rebuilt `flip`. Keep
  `transform-box: view-box` so the px origin is in viewBox space rather than
  resolved against the artwork's own box.
- **`rotateX(-88deg)`, not `-90deg`.** At exactly 90° the sheet is edge-on and
  degenerates to a hairline; some engines drop the element entirely for that
  frame and the entrance flickers.
- **Perspective ≈ 1.4 × W** (420px at W = 300), the same rule `flip` uses.
  Stronger perspective exaggerates the foreshortening and starts to look like a
  funhouse mirror; weaker flattens the fall into a plain scale.
- The opacity ramp finishing at ~28% hides the earliest frames, where the sheet
  is so foreshortened that it is unreadable anyway — same reasoning as `flip`'s
  mid-keyframe opacity dip.
- **No scale, and watch clearance.** The artwork reaches within ~3 units of the
  frame, and a 3D rotation about a top hinge pushes the bottom edge downward in
  screen space early on; the viewport clips that silently. If the bottom row of
  small marks looks like it is being cut in the first frames, reduce the start
  angle rather than the duration.
- Ends at `rotateX(0)` with no residual transform, so the resting frame is the
  source artwork (measured 0.08% drift, 0 of 111 counters filled).
- **Verified in Chromium 153 only.**
