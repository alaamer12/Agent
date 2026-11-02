# Scroll animation

> Owner of the triggered-versus-scrubbed decision, the reveal observer, scroll timelines, parallax and scrollytelling. Routing lives in ../SKILL.md.

Motion tied to scrolling: reveals, scrubbed progress, parallax, pinned scenes. Scroll is a user's primary control, so motion here must never fight it.

## Gate for scroll motion

Ask first: does motion on scroll serve comprehension or wayfinding? The verdict, tiers and novelty budget are gate.md's; reading-heavy pages, documentation and dense tools get little or no scroll motion, marketing and storytelling pages can carry more.

## Triggered versus scrubbed

| Type | Behavior | Use |
|---|---|---|
| Triggered | Starts when an element enters the viewport and plays on its own clock | Reveals, staggers, counters |
| Scrubbed | Progress equals scroll position, so it reverses when scrolling back | Progress bars, parallax, scenes tied to reading position |

Triggered reveals use an intersection observer; scrubbed motion uses scroll timelines or a motion value mapped to scroll progress (the scroll-listener ban: performance-and-accessibility.md, Main-thread discipline).

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
[data-reveal].is-visible { opacity: 1; transform: none; transition: opacity 300ms var(--ease-enter), transform 300ms var(--ease-enter); }
@media (prefers-reduced-motion: reduce) { [data-reveal] { opacity: 1; transform: none; } }
```

- Reveal once; the ruling is timing-and-tokens.md (Resolved conflicts). Re-animating on every scroll-up feels noisy.
- Content must stay visible without script: the hidden starting state should only apply when script has run (add a class on the root first), or use a no-script fallback.
- Stagger sibling reveals within the list/section offset bands in timing-and-tokens.md and keep the total short.
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
