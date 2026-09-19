# Recipe: flip — `/svg-animate flip`

3D card-flip intro: the logo swings in around its vertical axis, edge-on to
the viewer, and settles flat. One-shot; playful but clean.

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <style>
    .logo-group {
      transform-box: fill-box;
      transform-origin: center;
      opacity: 0;
      animation: flip-in 0.9s cubic-bezier(0.22, 1, 0.36, 1) 0.1s forwards;
    }

    @keyframes flip-in {
      0%   { transform: perspective(450px) rotateY(90deg); opacity: 0; }
      55%  { opacity: 1; }
      100% { transform: perspective(450px) rotateY(0deg); opacity: 1; }
    }
  </style>

  <g class="logo-group">
    <path d="..." fill="#0494a4" fill-rule="evenodd"/>
    <path d="..." fill="#040c24" fill-rule="evenodd"/>
  </g>
</svg>
```

## Notes

- **Perspective distance** ≈ 1.5 × W (450px for W=300; 2700px for the 1800
  hero). Too close distorts; too far flattens the 3D read.
- `transform: perspective() rotateY()` needs no special parent — CSS 3D
  transforms on SVG elements work in all modern browsers. `transform-box:
  fill-box` keeps the rotation axis on the logo, not the viewport.
- **Opacity dip** (0% → hidden, visible from 55%) hides the edge-on
  frames where the logo is a hairline — without it the flip looks like a
  glitch.
- Keep the mid keyframe opacity at 55%–65%: appearing just before the flat
  settle gives the snap its punch.
- One-shot `forwards` — this is an intro, not a loop.
