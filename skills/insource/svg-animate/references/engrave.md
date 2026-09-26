# Recipe: engrave — `/svg-animate engrave`

The logo appears as blind embossed paper — a highlight sweeps across the relief
like light raking a seal — and then the real colours land on top. One-shot;
ends as the plain logo.

The skill's first use of the **lighting primitives** (`feDiffuseLighting`).

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <filter id="engrave-relief" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2.42" result="soft"/>
      <feDiffuseLighting in="soft" surfaceScale="3" diffuseConstant="1.1" lighting-color="#ffffff" result="lit">
        <feDistantLight azimuth="235" elevation="38">
          <animate attributeName="azimuth" values="235;140;55" dur="1.8s" fill="freeze"
                   calcMode="spline" keyTimes="0;0.55;1" keySplines="0.4 0 0.6 1;0.3 0 0.2 1"/>
        </feDistantLight>
      </feDiffuseLighting>
      <feComposite in="lit" in2="SourceAlpha" operator="in"/>
    </filter>
    <style>
      .relief { animation: relief-out 0.72s linear 1.08s forwards; }
      .solid { opacity: 0; animation: engrave-land 0.72s linear 1.08s forwards; }
      @keyframes relief-out { to { opacity: 0; } }
      @keyframes engrave-land { to { opacity: 1; } }
      @media (prefers-reduced-motion: reduce) {
        .relief { animation: none; opacity: 0; filter: none; }
        .solid { animation: none; opacity: 1; }
      }
    </style>
  </defs>

  <g class="relief" filter="url(#engrave-relief)">
    <use href="#path-teal" fill="#8d96a6"/>
    <use href="#path-navy" fill="#8d96a6"/>
  </g>
  <g class="solid">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
</svg>
```

## Notes

- **The relief must fade out, not just be covered.** It is built from a blurred
  `SourceAlpha`, so its light spreads *past* the letterforms. Leaving it under
  the solid layer measured 2 filled counters and 1.38% end drift; fading it
  with the landing layer brought drift to 0.08%. Scaffolding that is merely
  hidden is still scaffolding.
- **`feDiffuseLighting` reads `SourceAlpha` as a height map**, which is why the
  blur comes first: a hard alpha edge makes hard lighting. `stdDeviation` ≈ F/2
  keeps the relief soft without letting adjacent thin strokes merge — on the
  test logo (F = 4.84) anything larger began fusing the small marks.
- **`feSpecularLighting` with an animated `fePointLight` measured DEAD** — no
  frame change at all, and 0.8% final ink. Do not reach for specular as the
  primary here; if you want a glint, add it over a diffuse base and re-probe.
- `surfaceScale` is the relief *height*; 2–4 reads as embossed paper, above ~6
  as extruded plastic. `elevation` 35–45 gives a raking angle; straight overhead
  kills the effect.
- The grey `#8d96a6` on the relief `<use>` elements is the "paper" tone. It is a
  **new colour, not a replacement** — the originals still appear verbatim on
  the solid layer, so `validate.py`'s colour check passes.
- Sweep the azimuth across ~180°; a shorter arc reads as a flicker.
- **Verified in Chromium 153 only.**
