# Recipe: holo — `/animation svg holo`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `crt` (center-out dark scanlines) and `glitch` (horizontal slice offsets). Combines a stuttered top-down bare `inset()` drop with cyan interference bars and projection flicker.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
    <clipPath id="...">
      <use href="#path-teal"/>
      <use href="#path-navy"/>
    </clipPath>
    <pattern id="..." width="4" height="6" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="#00e5ff" fill-opacity="0.45"/>
    </pattern>
  </defs>

  <style>
    .holo-wrap {
      clip-path: inset(0 0 100% 0);
      animation: holo-drop 0.95s cubic-bezier(0.2, 0.85, 0.3, 1) forwards, holo-flicker 1.35s linear forwards;
    }
    .holo-scan { opacity: 0.7; animation: holo-clear 0.5s linear 0.95s forwards; }
    @keyframes holo-drop {
      0%   { clip-path: inset(0 0 100% 0); }
      42%  { clip-path: inset(0 0 42% 0); }
      56%  { clip-path: inset(0 0 48% 0); }
      100% { clip-path: inset(0 0 0 0); }
    }
    @keyframes holo-flicker {
      0% { opacity: 0; } 12% { opacity: 0.85; } 24% { opacity: 0.55; }
      36% { opacity: 0.95; } 58% { opacity: 0.7; } 74% { opacity: 1; } 100% { opacity: 1; }
    }
    @keyframes holo-clear { to { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      .holo-wrap { animation: none; clip-path: none; opacity: 1; }
      .holo-scan { animation: none; opacity: 0; }
    }
  </style>

  <g class="holo-wrap">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
    <g clip-path="url(#holo-logo)">
      <rect class="holo-scan" width="300" height="110" fill="url(#holo-bars)"/>
    </g>
  </g>
</svg>
```

## Notes

- **Bare `inset()` only** (never `view-box`, foundations §6), plus both `holo-drop` and `holo-flicker` listed in one `animation` shorthand on `.holo-wrap`.
- Clip the cyan scan-bar `<pattern>` strictly to `url(#holo-logo)` and fade `.holo-scan` to `0` by `1.45s` for 0.00% resting drift.
