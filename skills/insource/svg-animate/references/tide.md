# Recipe: tide — `/svg-animate tide`

The logo fills from below behind a **wavy** waterline that rises and flattens.
One-shot; ends fully visible.

The skill's first use of an **animated `d` attribute**. `chrome-liquid` also
fills bottom-to-top, but its meniscus is a straight edge on a sliding rect; the
moving curve is what makes this read as liquid rather than a rising bar.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <mask id="tide-mask" maskUnits="userSpaceOnUse" x="-10" y="-10" width="320" height="140">
      <path fill="#fff" d="M -10,120 C 40,120 80,120 150,120 C 220,120 260,120 310,120 L 310,130 L -10,130 Z">
        <animate attributeName="d" dur="1.6s" fill="freeze"
                 calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.3 0 0.4 1"
                 values="M -10,120 C 40,120 80,120 150,120 C 220,120 260,120 310,120 L 310,130 L -10,130 Z;
                         M -10,55 C 40,46 80,64 150,55 C 220,46 260,64 310,55 L 310,130 L -10,130 Z;
                         M -10,-10 C 40,-19 80,-1 150,-10 C 220,-19 260,-1 310,-10 L 310,130 L -10,130 Z"/>
      </path>
    </mask>
    <style>
      @media (prefers-reduced-motion: reduce) { .logo { mask: none; } }
    </style>
  </defs>

  <g class="logo" mask="url(#tide-mask)">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **Every `values` stop must have the identical command sequence and
  cardinality.** `M C C L L Z` in all three, or the animation silently refuses
  to interpolate. This is the same rule as number-list attributes on filters,
  and it is easy to break while retuning the wave by hand.
- Generate the three paths from one function (line height + amplitude), which
  is what keeps the structure aligned. Hand-editing them is where the bug
  comes from.
- **The wave must flatten at both ends** (amplitude 0 below the canvas, and the
  final crest above it) or the resting frame is a wavy cut through the artwork
  instead of the logo. The middle stop carries the amplitude — here ±9 units,
  about H/12.
- Mask contents white, as always. The mask region extends past the canvas so
  the wave's own overflow is not what limits the reveal.
- Amplitude ≈ H/12; wavelength = one full sine across the canvas width. Shorter
  wavelengths start to look like a saw edge rather than water.
- If the user wants the water to keep moving after the fill, that is a loop
  style, not this one — add a fourth and fifth stop that returns to the third
  and mark the animation `infinite`.
- **Verified in Chromium 153 only.**
