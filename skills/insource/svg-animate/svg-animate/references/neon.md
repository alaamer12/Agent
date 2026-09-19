# Recipe: neon — `/svg-animate neon`

Neon-sign switch-on: each outline flickers alight in its own color with a
colored halo, sputtering like a real tube for the first second, then the
fills fade in underneath. One-shot; ends fully lit. Designed for dark
backgrounds.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <filter id="neon-glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="2.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <style>
    .neon-stroke {
      fill: none;
      stroke-width: 1.5;
      stroke-linecap: round;
      stroke-linejoin: round;
      filter: url(#neon-glow);
      opacity: 0;
      animation: flicker-on 1.1s linear forwards;
    }
    .neon-fill {
      opacity: 0;
      animation: fill-in 0.6s ease-in 0.9s forwards;
    }
    .c-teal { stroke: #0494a4; fill: #0494a4; }
    .c-navy { stroke: #040c24; fill: #040c24; }

    /* hard-step flicker: sputter, catch, steady */
    @keyframes flicker-on {
      0%   { opacity: 0; }
      7%   { opacity: 1; }
      11%  { opacity: 0.15; }
      16%  { opacity: 1; }
      24%  { opacity: 0.35; }
      30%  { opacity: 1; }
      42%  { opacity: 0.65; }
      48%  { opacity: 1; }
      100% { opacity: 1; }
    }
    @keyframes fill-in { to { opacity: 1; } }
  </style>

  <rect width="100%" height="100%" fill="#0a0a12" /> <!-- dark stage: recommended -->

  <path class="neon-stroke c-teal" d="..." fill-rule="evenodd" />
  <path class="neon-stroke c-navy" d="..." fill-rule="evenodd" />
  <path class="neon-fill c-teal"    d="..." fill-rule="evenodd" />
  <path class="neon-fill c-navy"    d="..." fill-rule="evenodd" />
</svg>
```

## Notes

- **Dark stage strongly recommended** — neon reads as nothing on white. Use a
  near-black rect (`#0a0a12`); skip only if the user's context supplies its
  own dark background.
- **Neon color = the path's own fill color**, stroke and fill share it via
  one class per path. Never recolor to a generic "neon green" — the tube
  glows in the brand color.
- **Flicker pattern**: sharp opacity steps (no easing on the flicker itself).
  Keep ~5–7 sputters in the first half, then steady. Fill fades in only once
  the tube is stable (`0.9s` here).
- **Glow blur** scales like the other filters: stdDeviation ≈ W/120.
- `stroke-width` ≈ 1.5 at small sizes (slightly heavier than draw strokes —
  a tube has thickness); scale per the SKILL.md table.
- If a path's own color is very dark (like #040c24), the glow is subtle on
  the dark stage — acceptable; the tube still reads via its halo against
  near-black.
