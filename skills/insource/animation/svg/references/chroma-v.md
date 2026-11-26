# Recipe: chroma-v — `/animation svg chroma-v`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

The vertical-axis counterpart to `chroma`. Separates each original path into exact single-channel R, G, and B `<use>` layers blended with `mix-blend-mode: screen` on a dark stage.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .chv { mix-blend-mode: screen; }
    .cv-r { animation: cv-up 1.2s cubic-bezier(0.3, 0.9, 0.3, 1) forwards, cv-out 0.5s linear 1.2s forwards; }
    .cv-b { animation: cv-dn 1.2s cubic-bezier(0.3, 0.9, 0.3, 1) forwards, cv-out 0.5s linear 1.2s forwards; }
    .cv-g { animation: cv-out 0.5s linear 1.2s forwards; }
    .cv-solid { opacity: 0; animation: cv-in 0.5s linear 1.2s forwards; }
    @keyframes cv-up { from { transform: translateY(-2.4px); } to { transform: translateY(0px); } }
    @keyframes cv-dn { from { transform: translateY(2.0px); } to { transform: translateY(0px); } }
    @keyframes cv-out { to { opacity: 0; } }
    @keyframes cv-in { to { opacity: 1; } }
    @media (prefers-reduced-motion: reduce) {
      .chv { animation: none; opacity: 0; }
      .cv-r, .cv-b { animation: none; transform: none; }
      .cv-solid { animation: none; opacity: 1; }
    }
  </style>

  <g style="isolation: isolate">
    <rect width="300" height="110" fill="#0a0a12"/>
    <use href="#path-teal" class="chv cv-r" fill="rgb(4,0,0)"/>
    <use href="#path-teal" class="chv cv-g" fill="rgb(0,148,0)"/>
    <use href="#path-teal" class="chv cv-b" fill="rgb(0,0,164)"/>
    <use href="#path-navy" class="chv cv-r" fill="rgb(4,0,0)"/>
    <use href="#path-navy" class="chv cv-g" fill="rgb(0,12,0)"/>
    <use href="#path-navy" class="chv cv-b" fill="rgb(0,0,36)"/>
    <use href="#path-teal" class="cv-solid"/>
    <use href="#path-navy" class="cv-solid"/>
  </g>
</svg>
```

## Notes

- **Tight vertical clearance clamping**: cap initial shifts to `-2.4px` (red) and `+2.0px` (blue) on 300×110 (`y_max ≈ 108`), keeping bottom marks inside the viewport.
- Keep `<rect fill="#0a0a12"/>` as the first child of the `isolation: isolate` group, combine both animations in one shorthand per channel, and fade ghosts out under `.cv-solid` (exact same verified math as `chroma`).
