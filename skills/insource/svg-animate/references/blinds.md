# Recipe: blinds — `/svg-animate blinds`

Horizontal slats open one after another, each growing its own height, so the
logo appears through venetian shutters. One-shot; ends fully visible.

Distinct from `mosaic`, which is a 2-D grid of tiles gated on **opacity**. Here
the mask geometry itself animates — each slat's `height` grows — in a single
column, so the reveal has hard moving edges instead of squares appearing.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="blinds-mask" maskUnits="userSpaceOnUse" x="-5" y="-5" width="310" height="120">
      <rect x="-5" y="-5" width="310" height="120" fill="#000"/>
      <rect x="-5" y="0.00" width="310" height="0" fill="#fff"><animate attributeName="height" values="0;10" dur="0.26s" begin="0.05s" fill="freeze"/></rect>
      <rect x="-5" y="10.00" width="310" height="0" fill="#fff"><animate attributeName="height" values="0;10" dur="0.26s" begin="0.13s" fill="freeze"/></rect>
      <!-- … one rect per slat, begin written as a literal … -->
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#blinds-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **The black base rect is load-bearing.** A mask starts transparent, and each
  slat only covers its own band; without an explicit black backdrop the gaps
  between slats are *undefined* rather than hidden. Draw black first, then the
  white slats on top.
- **Slats must tile the canvas exactly**: `slat_h = H / count`, and the last one
  has to reach the bottom edge. 11 slats at 10 units each on a 110-tall canvas;
  a count that does not divide H leaves a permanently hidden strip.
- `begin` values are literals — SMIL cannot evaluate `0.05 + i*0.075` at
  runtime, so the generator writes each resolved number in.
- Slat count ≈ H/10, clamped so each slat stays ≥ 4·F wide... on the test logo
  F = 4.84, which means slats below ~10 units start resolving *inside* single
  strokes and the artwork appears sliced. Fewer, taller slats is the safe
  direction.
- Vertical slats (swap `height`→`width`, `y`→`x`) read as a louver opening
  left-to-right; same mechanic, different axis.
- To make it a *loop* (blinds opening and closing), animate `height`
  `0;10;0` with `repeatCount="indefinite"` and stagger the `begin` on the way
  back — but that is an idle treatment, not an intro.
- **Verified in Chromium 153 only.**
