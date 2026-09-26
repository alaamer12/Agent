# Recipe: iris — `/svg-animate iris`

Cinematic circular reveal: a `<circle>` clip starts at r=0 at the logo's
center and expands until the whole logo is visible. One-shot. The logo keeps
its real fills throughout — only visibility is animated.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <clipPath id="iris-clip">
      <circle cx="150" cy="55" r="0">
        <animate attributeName="r" from="0" to="175" dur="1.1s" begin="0.1s"
                 fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1" />
      </circle>
    </clipPath>
  </defs>

  <g clip-path="url(#iris-clip)">
    <path d="..." fill="#0494a4" fill-rule="evenodd"/>
    <path d="..." fill="#040c24" fill-rule="evenodd"/>
  </g>
</svg>
```

## Notes

- **Final radius R** = 0.55 × viewBox diagonal, so corners are covered with
  margin: R = 0.55 × √(W² + H²). For 300×110 → ~176.
- **Center**: viewBox center (W/2, H/2). If the user wants the reveal to
  originate from the logo's visual center instead, compute the paths' bbox
  center with `extract_paths.py` — but default to viewBox center.
- SMIL animates the circle inside `<clipPath>` in all modern browsers; no
  CSS clipping involved, so `fill-rule` behavior inside the clip is
  untouched.
- Slower than draw-fill (1–1.4s) — it is a cinematic beat, not a pen stroke.
- One `<g>` holds all paths; the clip is shared. Keep paths inline here
  (defs/use adds nothing for this style).
