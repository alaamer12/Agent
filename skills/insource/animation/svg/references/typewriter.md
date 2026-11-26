# Recipe: typewriter — `/animation svg typewriter`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `spark` (smooth continuous motion path + radial mask bulge) and `draw-fill` (path stroke). A discrete `steps(N, end)` horizontal reveal marches across in mechanical ticks behind a blinking brand-coloured vertical cursor.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .tw-logo {
      clip-path: inset(0 100% 0 0);
      animation: tw-reveal 1.2s steps(15, end) 0.08s forwards;
    }
    .tw-caret {
      opacity: 0;
      animation: tw-step 1.2s steps(15, end) 0.08s forwards, tw-blink 1.45s linear 0.08s forwards;
    }
    @keyframes tw-reveal {
      from { clip-path: inset(0 100% 0 0); }
      to   { clip-path: inset(0 0 0 0); }
    }
    @keyframes tw-step {
      from { transform: translateX(0px); }
      to   { transform: translateX(296px); }
    }
    @keyframes tw-blink {
      0%   { opacity: 1; }
      82%  { opacity: 1; }
      88%  { opacity: 0; }
      94%  { opacity: 0.9; }
      100% { opacity: 0; }
    }
    @media (prefers-reduced-motion: reduce) {
      .tw-logo { animation: none; clip-path: none; }
      .tw-caret { animation: none; opacity: 0; }
    }
  </style>

  <g class="tw-logo">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
  </g>
  <rect class="tw-caret" x="0" y="6" width="2.5" height="98" fill="#0494a4"/>
</svg>
```

## Notes

- **Bare `inset()` only — never `view-box`** (foundations §6). `clip-path: inset(0 100% 0 0)` → `inset(0 0 0 0)` with `steps(N, end)` steps cleanly across the artwork bounding box.
- **Step count `N`**: pick `N ≈ round(W / max(18, 4·F))` (15 steps on 300px) so each tick advances by roughly one glyph width rather than slicing thin strokes mid-stem.
- **Combined `animation` shorthand on the caret** (foundations §6): `.tw-caret` runs both `tw-step` (horizontal advance) and `tw-blink` (visibility + final fade-out) in one `animation` declaration.
- Caret width `max(2, W/120)` in the primary brand colour so it reads on both light and dark stages.
