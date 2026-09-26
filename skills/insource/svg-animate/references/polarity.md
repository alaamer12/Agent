# Recipe: polarity — `/svg-animate polarity`

A band sweeps across the logo and inverts whatever it touches, so a negative
strip runs through the artwork and the plain logo is left behind. One-shot;
ends pixel-exact.

The skill's first use of **`mix-blend-mode: difference`**. Distinct from
`chroma` (which decomposes the artwork into channels and sums them) and from
`chrome-liquid`'s sheen (which *adds light*; this one subtracts it from 255).

## Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
  <defs>
    <path id="path-teal" d="..." stroke="none" fill="#0494a4" fill-rule="evenodd"/>
    <path id="path-navy" d="..." stroke="none" fill="#040c24" fill-rule="evenodd"/>
  </defs>

  <style>
    .pol-band {
      mix-blend-mode: difference;
      animation: pol-sweep 1.3s cubic-bezier(0.4, 0, 0.5, 1) forwards;
    }
    @keyframes pol-sweep {
      from { transform: translateX(-130px); }
      to   { transform: translateX(310px); }
    }
    @media (prefers-reduced-motion: reduce) {
      .pol-band { animation: none; transform: translateX(310px); }
    }
  </style>

  <g style="isolation: isolate">
    <use href="#path-teal"/>
    <use href="#path-navy"/>
    <rect class="pol-band" x="0" y="0" width="130" height="110" fill="#ffffff"/>
  </g>
</svg>
```

## Notes

- **Band width ≈ W/2.3; the end offset must clear the canvas fully** — park it
  at `W + band width` past the right edge, or a sliver of inversion survives in
  the resting frame. Ending off-canvas is what makes the drift 0.08%.
- **What the band does depends on the stage, and this is the design decision to
  make consciously.** Difference against a *transparent* backdrop yields the
  source unchanged, so with no background rect in the file:
  - on a **light** page the band is invisible except where it crosses the
    artwork — you get a bar of inverted logo, which is the cleanest read;
  - on a **dark** page the band is a glaring white bar carrying the inverted
    logo inside it.
  Add a backdrop `<rect>` inside the isolated group if you want the band to
  invert the *whole* image; leave it out to invert only the mark.
- **`isolation: isolate` is required**, on the group containing both the artwork
  and the band. Without it the blend reaches past the SVG's own content and the
  result depends on where the file is embedded.
- The band is a `<rect>`, not a `<path>` — decorative geometry never adds a
  path (see SKILL.md).
- Soft edges: give the band a linear gradient from white to black instead of a
  flat fill and the inversion feathers in. Flat white is a hard cut.
- Pacing: 1.1–1.5s. Slower turns a scan into a crawl; faster loses the read of
  what inverted.
- **Verified in Chromium 153 only.**
