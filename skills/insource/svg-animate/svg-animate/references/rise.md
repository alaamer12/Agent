# Recipe: rise — `/svg-animate rise`

Classic UI reveal: each path floats up from slightly below and fades in,
staggered left-to-right (DOM order). One-shot; ends fully visible.

## Template

Wrap each original path in its own `<g class="rise-item">`; paths stay
untouched inside (fill, fill-rule intact).

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="110" viewBox="0 0 300 110" version="1.1">
<style>
  .rise-item {
    opacity: 0;
    animation: rise-in 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  }
  .rise-item:nth-child(2) { animation-delay: 0.12s; }
  .rise-item:nth-child(3) { animation-delay: 0.24s; }
  /* one nth-child rule per additional path */

  @keyframes rise-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>

<g class="rise-item"><path d="..." fill="#0494a4" fill-rule="evenodd"/></g>
<g class="rise-item"><path d="..." fill="#040c24" fill-rule="evenodd"/></g>
</svg>
```

## Notes

- **Stagger order**: DOM order = paint order. If the accent should rise
  first, put its `<g>` first and reorder the `nth-child` delays.
- **Rise offset** ≈ H/10, clamped to 10–80px (subtle at any size). Keep
  translateY — translateX reads as a slide, a different effect.
- **Timing**: 0.5–0.8s per item, 0.1–0.15s stagger. More than ~4 paths:
  shrink the stagger so the total stays under ~1.5s.
- No defs/uses needed — this is a pure wrapper-group treatment.
