# Scroll animation

> **Connections** (paths are relative to `references/`)
> - Read when: motion tied to scrolling: reveal on scroll, parallax, progress, pinned scenes.
> - Skip when: the motion is not scroll-linked.
> - Read next: `entrances-and-exits.md` (for the reveal itself); `stacks/css-native.md` (for scroll timelines).

Motion tied to scrolling: reveals, scrubbed progress, parallax, pinned scenes. Scroll is a user's primary control, so motion here must never fight it.

## Contents
- Gate for scroll motion
- Triggered versus scrubbed
- Reveal on entry
- Scroll-driven progress
- Parallax
- Scrollytelling
- Rules
- Checklist

## Gate for scroll motion

Ask first: does motion on scroll serve comprehension or wayfinding? Reading-heavy pages, documentation and dense tools get little or no scroll motion. Marketing and storytelling pages can carry more, within the novelty budget.

## Triggered versus scrubbed

| Type | Behavior | Use |
|---|---|---|
| Triggered | Starts when an element enters the viewport and plays on its own clock | Reveals, staggers, counters |
| Scrubbed | Progress equals scroll position, so it reverses when scrolling back | Progress bars, parallax, scenes tied to reading position |

Triggered reveals use an intersection observer, never a scroll listener that writes state. Scrubbed motion uses scroll timelines or a motion value mapped to scroll progress.

## Reveal on entry

```js
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    e.target.classList.add('is-visible');
    io.unobserve(e.target);              // reveal once
  }
}, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el));
```

```css
[data-reveal] { opacity: 0; transform: translateY(12px); }
[data-reveal].is-visible { opacity: 1; transform: none; transition: opacity 400ms var(--ease-enter), transform 400ms var(--ease-enter); }
@media (prefers-reduced-motion: reduce) { [data-reveal] { opacity: 1; transform: none; } }
```

- Reveal once. Re-animating on every scroll-up feels noisy.
- Content must stay visible without script: the hidden starting state should only apply when script has run (add a class on the root first), or use a no-script fallback.
- Stagger sibling reveals by about 40 to 80ms and keep the total short.
- Reserve space so content does not shift as it reveals.

## Scroll-driven progress

Where supported, use scroll timelines in CSS (`animation-timeline: scroll()` or `view()`) with `animation-range`; otherwise map a motion value to scroll progress in the animation library. Scrubbed motion uses a linear easing so it follows the scrollbar exactly.

## Parallax

Offsets small (5 to 15% of travel), applied with transform to layers behind the content, never to body text. Disable under reduced motion and on small screens where it adds jank.

## Scrollytelling

A pinned scene advances as the user scrolls. Keep each beat short, give the user an exit (skip link, normal scroll resumes), and avoid pinning more than a couple of screens. Never hijack the scroll position, speed or direction.

## Rules

- Never intercept wheel or touch scrolling to implement animation.
- Compositor properties only.
- Reduced motion: show final states immediately; remove scrubbing and pinning.
- Large sticky or pinned regions must still work with keyboard scrolling and find-in-page.

## Checklist

- [ ] The gate says scroll motion helps here
- [ ] Triggered reveals use an observer and fire once
- [ ] Content visible without script and under reduced motion
- [ ] No layout shift from reveals
- [ ] Scrubbed motion is linear and compositor-only
- [ ] Scroll never hijacked
