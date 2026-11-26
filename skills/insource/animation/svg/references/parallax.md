# Recipe: parallax — `/animation svg parallax`

Per-style recipe — shared build rules in [foundations.md](foundations.md),
signature and trigger words in [../method.md](../method.md).

Distinct from `orbit` (opposing curved arcs) and `rise` (vertical bottom-up stagger). Foreground accent layer travels ~2.5× farther than the primary layer in the same direction for a clean cinema camera pan.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="..." d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="..." d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .par-fg { opacity: 0; animation: par-front 1.15s cubic-bezier(0.22, 0.85, 0.28, 1) forwards; }
    .par-bg { opacity: 0; animation: par-back 1.15s cubic-bezier(0.22, 0.85, 0.28, 1) 0.08s forwards; }
    @keyframes par-front {
      0%   { transform: translate(-28px, 6px); opacity: 0; }
      26%  { opacity: 1; }
      100% { transform: translate(0px, 0px); opacity: 1; }
    }
    @keyframes par-back {
      0%   { transform: translate(-11px, 2px); opacity: 0; }
      26%  { opacity: 1; }
      100% { transform: translate(0px, 0px); opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
      .par-fg, .par-bg { animation: none; opacity: 1; transform: none; }
    }
  </style>

  <g class="par-bg"><use href="#path-navy"/></g>
  <g class="par-fg"><use href="#path-teal"/></g>
</svg>
```

## Notes

- **Layer speed ratio ≈ 2.5:1** (`-28px` foreground vs `-11px` background on 300px width) with a subtle `0.08s` lag on the background layer.
- For single-path logos, split into two `<clipPath>` horizontal bands so depth differential still reads cleanly.
