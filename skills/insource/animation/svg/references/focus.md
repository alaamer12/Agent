# Recipe: focus — `/animation svg focus`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../SKILL.md](../SKILL.md).

This is the skill's only **animated-sharpness** style. The three glow styles
(`neon`, `elastic-entrance`, `pulse`) halo an already-sharp source and never
soften the artwork itself — that difference is the whole point, so protect it.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <style>
    .logo {
      opacity: 0;
      animation: rack-focus 1.4s linear forwards;
    }
    @keyframes rack-focus {
      0%   { filter: blur(2.42px); opacity: 0; }
      22%  { opacity: 1; }
      66%  { filter: blur(0px); }
      82%  { filter: blur(1.21px); }
      100% { filter: blur(0px); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .logo { animation: none; opacity: 1; filter: none; }
    }
  </style>

  <g class="logo">
    <path d="..." fill="#0494a4" fill-rule="evenodd"/>
    <path d="..." fill="#040c24" fill-rule="evenodd"/>
  </g>
</svg>
```

No defs, no uses — paths stay exactly as the source had them, inside one
animated group.

## Notes

- **Softness σ = min(F/2, W/120)** (F derivation per foundations §5). CSS
  `blur(x)` takes a standard deviation, so σ is used directly.
- **The overshoot at 82% is the effect.** Delete it and this is a fade-in.
  Real rack focus hunts: sharp, a touch soft again, then locked.
  Overshoot ≈ 0.5σ.
- **No scale settle** — style decision; the viewport clips any push-in (foundations §5).
- Blur mid-flight *does* bleed across counters — measured at 81 of 111 sampled
  gap pixels. That is correct behaviour, not the #1 failure: what must hold is
  that they are clean again at the end (measured drift 0.08%).
- `filter: blur()` is a CSS shorthand, fully interpolable, and needs no
  `<filter>` element. Animating `stdDeviation` on a real `<feGaussianBlur>`
  instead requires SMIL (foundations §6). Both spellings were measured to
  work; the shorthand is shorter.
