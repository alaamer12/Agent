# Choreography recipes

> Copy-ready patterns for the relations in synchronization.md. Values are starting points — tune on a recording (scrub, don't remember). Patterns distilled 2026-11-14 from Emil Kowalski's published choreograph recipes; read from source, not re-executed here — stack APIs may drift, check the current docs when implementing. Routing: `../method.md`.

## Overlap — CSS delay variable (one-shot entrances)

Each element carries its own delay in a custom property: no per-item class, gaps shrink as the group goes on (0, 0, 120, 200 — the wave), `both` so delayed items never flash their final state.

```css
.stagger > * {
  animation: enter 0.6s ease both;
  animation-delay: var(--delay, 0ms);
}
@keyframes enter { from { opacity: 0; transform: translateY(10px); } }

@media (prefers-reduced-motion: reduce) {
  .stagger > * { animation-name: fade; animation-delay: 0ms; }
  @keyframes fade { from { opacity: 0; } }
}
```

```html
<div class="stagger">
  <h1 style="--delay:0ms">Title</h1>
  <p style="--delay:0ms">First paragraph — same beat as the title</p>
  <p style="--delay:120ms">Supporting paragraph</p>
  <div style="--delay:200ms">CTAs</div>
</div>
```

- `both` = `backwards` (hold first keyframe through the delay) + `forwards` (keep end state). Omitting `to` animates to the element's own styles.
- Reduce collapses the whole thing to a plain fade, zero delays.
- Don't drive per-frame values (a drag) through an inherited custom property on a large tree — the recalculation cost lands on every descendant.

WAAPI equivalent keeps the wave in one array:

```js
const delays = [0, 0, 120, 200];                     // importance-grouped beats
items.forEach((el, i) => el.animate(
  [{ opacity: 0, transform: 'translateY(10px)' }, {}],
  { duration: 600, delay: delays[i], easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'both' },
));
```

## Overlap — declarative variants with a non-uniform stagger

Each role gets its own variant (distance, duration); the stagger only decides *when*. Eased delays shrink the gaps automatically; `from` radiates from an index (the item the user touched) or the center.

```tsx
import { motion, stagger } from "motion/react";

const list = {
  hidden: {},
  show: { transition: { delayChildren: stagger(0.06, { ease: "easeOut" }) } },
};
const lead       = { hidden: { opacity: 0, y: 12 },
                     show:   { opacity: 1, y: 0, transition: { duration: 0.5 } } };
const support    = { hidden: { opacity: 0, y: 6 },
                     show:   { opacity: 1, y: 0, transition: { duration: 0.4 } } };
const decoration = { hidden: { opacity: 0 },
                     show:   { opacity: 1, transition: { duration: 0.3 } } };
```

- Long lists: items past the first handful get the 5th item's delay — the group never outruns its budget (timing-and-tokens.md §Stagger).
- Older versions name this `staggerChildren: number`; current API wins when both exist.

## Together — remove the exiting element from the flow

Siblings close the gap **while** the removed item fades, not after it.

```tsx
<AnimatePresence mode="popLayout" initial={false}>
  {chips.map((chip) => (
    <motion.li key={chip.id} layout exit={{ opacity: 0, scale: 0.95 }}>
      {chip.label}
    </motion.li>
  ))}
</AnimatePresence>
```

Without a library — take it out of flow at the removal moment:

```js
const { top, left } = el.getBoundingClientRect();
el.style.position = 'absolute';            // parent is position: relative
el.style.top = `${top}px`; el.style.left = `${left}px`;
el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 200, fill: 'forwards' });
// siblings reflow now — animate them with FLIP if the jump reads harsh
```

## Together — crossfade views in a resizing container

One object: container height and content swap share duration and easing family; the fade **scales with the height delta** (big jump keeps the full fade, tiny jump doesn't flicker), clamped.

```tsx
const fadeDuration = useMemo(() => {
  const MIN = 0.15, MAX = 0.27;
  const delta = Math.abs(bounds.height - prevHeight.current ?? bounds.height);
  prevHeight.current = bounds.height;
  return Math.min(Math.max(delta / 500, MIN), MAX);
}, [bounds.height]);

<motion.div animate={{ height: bounds.height }}
            transition={{ duration: 0.27, ease: [0.25, 1, 0.5, 1] }}
            style={{ overflow: "hidden" }}>
  <AnimatePresence initial={false} mode="popLayout">
    <motion.div key={view}
      initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ duration: fadeDuration, ease: "easeOut" }}>
      {content}
    </motion.div>
  </AnimatePresence>
</motion.div>
```

- Container rides the strong ease-out; content a lighter curve **of the same family**.
- If the container belongs to a bigger component (a drawer), bring the component's own open duration into the same family — one entity.

## Sequence — direction-aware steps

`custom` on **both** the presence wrapper and the child, so the exit reads the direction chosen *now*, not at mount:

```tsx
const [[step, direction], setStep] = useState([0, 0]);
const go = (d: 1 | -1) => setStep(([s]) => [s + d, d]);

const variants = {
  initial: (d: number) => ({ x: `${110 * d}%`, opacity: 0 }),
  active:  { x: "0%", opacity: 1 },
  exit:    (d: number) => ({ x: `${-110 * d}%`, opacity: 0 }),
};

<AnimatePresence mode="popLayout" initial={false} custom={direction}>
  <motion.div key={step} custom={direction} variants={variants}
              initial="initial" animate="active" exit="exit" />
</AnimatePresence>
```

Small containers or very similar views: swap the 110% slide for a crossfade with an ~8px shift and a light blur — the eyes barely move, the change still reads.

## Sequence — one draw after another (cause → effect)

Second starts **just before** the first ends; `forwards` holds both end states; `pathLength="100"` makes the dash math round regardless of real path length.

```css
.square, .checkmark { stroke-dasharray: 100; stroke-dashoffset: 100;
                      animation: draw var(--d) var(--ease) forwards; }
.square    { --d: 0.6s; }
.checkmark { --d: 0.4s; animation-delay: 0.5s; }   /* lands while the square settles */
@keyframes draw { to { stroke-dashoffset: 0; } }
```

## Sequence (kept as a crossfade) — duplicate-view morph

When a container changes width *and* height between two dense views, `mode="wait"` is the safe default. To crossfade anyway:

1. Render the active view twice. Copy A only **enters**. Copy B is `position: absolute` at `opacity: 0` and becomes visible only while **exiting** — its exit keyframe starts at `opacity: 1` and fades out.
2. Give the exiting copy its own transform per destination: scale **up** if the next state is larger, down if smaller; pull `scaleX` toward the center when the container narrows so nothing bleeds past the edges.
3. Few states ⇒ hardcode the values (and the spring bounce — smaller states get more bounce) per pair, passed through `custom`.

## Carry — steer a shared-layout animation through its parent

A `layoutId` path can't be customized; the container it lands in can:

```tsx
<motion.div animate={{ y: 73 }}
            transition={{ delay: 0.13, duration: 0.3, ease: [0.23, 1, 0.32, 1] }}>
  {selected.map((img) => <motion.img key={img.id} layoutId={img.id} src={img.src} />)}
</motion.div>
```

The images morph into the bin *and* drop with it. Reveal the bin's front face on a delay timed to just-before-landing so they never visibly pass through it.

## Imperative orchestration — only when events multiply

Use it when several elements coordinate across several events (hover, click, idle timer) and completion must be awaited. Never for a simple stagger.

Core discipline (any orchestrating API):

```js
const running = [];
function play(steps) {
  running.forEach((a) => a.stop());     // never stack sequences
  running.length = 0; running.push(...steps);
  return Promise.all(steps);            // await ALL when durations differ
}

// accents land with the lead: last ~20% of its window, leader first
async function onEnter() {
  await play([
    animate(icon, { y: -4 }, { duration: 0.3 }),
    ...lines.map((el, i) =>
      animate(el, { strokeDashoffset: [1.05, 0] },
        { duration: 0.5, times: [0.7, 0.9], delay: i === 1 ? 0 : 0.04 })),
  ]);
}

// the idle loop resumes only after every reset finished
async function onLeave() { await play(resetAll()); startIdle(); }
```

- Target by `data-animate` selectors inside a scope instead of a ref per element.
- Attention-loop numbers (first wait, repeat gap): timing-and-tokens.md §Choreography values.
- Awaiting one animation of a differing-duration set is the race the interruption bug hides in; `Promise.all` the lot.
