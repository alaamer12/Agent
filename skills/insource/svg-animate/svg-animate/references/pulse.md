# Recipe: pulse — `/svg-animate pulse`

Ambient idle loop: the logo breathes — a slow scale swell with a soft glow
at the peak of each breath. No entrance, no exit; it runs forever behind
content or on a resting screen.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <filter id="soft-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2.5" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <style>
    .logo-group {
      transform-box: fill-box;
      transform-origin: center;
      animation: breathe 4s ease-in-out infinite;
    }

    @keyframes breathe {
      0%, 100% { transform: scale(1); }
      50%      { transform: scale(1.03); filter: url(#soft-glow); }
    }
  </style>

  <g class="logo-group">
    <path d="..." fill="#0494a4" fill-rule="evenodd"/>
    <path d="..." fill="#040c24" fill-rule="evenodd"/>
  </g>
</svg>
```

## Notes

- **Amplitude is small**: 1.02–1.05 scale. Anything larger stops reading as
  breathing and starts reading as hopping.
- **Period**: 3.5–5s. Test at 4s; slow down for large hero logos.
- **Glow only at the peak** (the 50% keyframe) — like the elastic-entrance
  treatment, the filter is active only inside that keyframe window, so the
  halo swells and releases each cycle automatically.
- Paths keep their real fills and `fill-rule` as direct children of the
  animated group; this recipe never re-paints.
- For a "resting screen" use, the user may want the first beat delayed
  (`animation-delay`) so it doesn't fire during page load — ask if relevant.
