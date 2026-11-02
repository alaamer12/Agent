# Synchronization

> Owns the instant/domino/linked forms (definitions, propagation, per-form rules, pitfalls); routing lives in `../SKILL.md`.

How animated elements relate to each other. Choose the form from the relationship, then implement it.

## Choosing the form

| Question | Answer | Form |
|---|---|---|
| Should elements start and end together? | Yes | Instant synchronous |
| Does one element's animation hand off to the next? | Yes | Domino |
| Does acting on one element mean its relatives should react? | Yes | Linked |
| Are the elements independent? | Yes | No synchronization; keep them simple |

Different techniques can share one relationship: one element fades out, another slides out, a third scales, all under the same timing, order, or link.

## Instant synchronous

Elements start together and share one clock. Use it when the parts read as one object (a card whose image, title and badge arrive together) or when different techniques express one change.

Rules
- One shared duration and easing, or deliberately related ones. Mismatched timing in a group is the usual cause of "something feels off".
- Paired elements (modal and overlay, tooltip and arrow) must share easing and duration.
- Let techniques differ, not clocks.

```css
.group > * { transition-duration: var(--dur); transition-timing-function: var(--ease); }
```

```js
// WAAPI: one timing object reused by every member
const timing = { duration: 240, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'both' };
members.forEach((el, i) => el.animate(keyframesFor(i), timing));
```

## Domino / sequential

One animation depends on or follows another, so motion travels through the interface in order. The order carries meaning: it should match reading order, importance, or causality.

Rules
- Order by hierarchy: the primary element leads, supporting elements follow, the call to action lands last.
- Overlap beats waiting. Start the next element before the previous finishes (a stagger offset smaller than the duration) unless a hard hand-off is the point.
- Keep the total short: domino uses the list-item and section stagger bands, and each band's numbers belong to timing-and-tokens.md §Stagger.
- Never block interaction while a chain plays.
- Vary delay and distance by importance. A uniform offset reads as a metronome.
- A chain of more than about five items needs grouping, or the later items feel slow. Animate groups as units.

```css
.item { animation: enter var(--dur) var(--ease) both; animation-delay: calc(var(--i) * var(--stagger-list)); }
```

```js
// Explicit hand-off: B starts when A finishes
await elA.animate(kfA, timing).finished;
await elB.animate(kfB, timing).finished;
```

Motion `staggerChildren` on the parent: see stacks/react-motion.md.

Choose one level of entrance per container. If the container animates in, its children are already visible on arrival; if the children stagger, the container does not also move.

## Linked

An action or animation on one element causes a corresponding effect on elements it is related to. This fits interfaces that represent relationships: canvases, diagrams, graphs, editors, tables with related rows, highlight systems.

Examples
- Selecting a node highlights its neighbors.
- Hovering one item highlights related items.
- Interacting with one element changes the state of connected elements.
- Animating one element animates its linked elements correspondingly.

### Model the relationship first

Linked synchronization needs data, not just CSS. Decide:
1. **Link source.** Where do relationships come from (edges in a graph, a shared id or group, a parent relation, a query)?
2. **Link strength.** All linked elements react equally, or the reaction falls off with distance (hops).
3. **Link direction.** Symmetric or one-way (selecting a parent affects children but not the reverse).
4. **Reaction.** Same effect, or a corresponding but different effect (the source pulses, neighbors brighten, distant nodes dim slightly).

### Propagation pattern

```ts
// Breadth-first propagation with falloff. Returns element id -> strength in (0, 1].
function linkedStrengths(graph: Map<string, string[]>, source: string, maxHops = 2, falloff = 0.5) {
  const out = new Map<string, number>([[source, 1]]);
  let frontier = [source];
  for (let hop = 1; hop <= maxHops; hop++) {
    const next: string[] = [];
    for (const id of frontier) {
      for (const n of graph.get(id) ?? []) {
        if (out.has(n)) continue;            // cycle guard
        out.set(n, Math.pow(falloff, hop));
        next.push(n);
      }
    }
    frontier = next;
  }
  return out;
}
```

Apply the result by writing one data attribute or one property per element, not by animating from script every frame:

```ts
for (const [id, s] of linkedStrengths(graph, hoveredId)) {
  nodes.get(id)!.style.setProperty('--link', String(s));   // element-local property
}
```

```css
.node { opacity: calc(0.45 + 0.55 * var(--link, 1)); transition: opacity 160ms var(--ease); }
```

For plain DOM relationships, CSS can carry the link without script (`:has()` de-emphasis pattern: see stacks/css-native.md).

### Implementation notes
- Reset on leave or deselect: restore all linked elements, including ones a fast pointer skipped.
- Batch updates inside one frame. On large graphs update only elements whose strength changed.
- Cap the reach (`maxHops`). Linking a whole dense graph reads as noise and costs frames.
- Linked effects must not rely on color alone, and must also respond to keyboard focus and selection, not only pointer hover.
- On touch devices there is no hover. Use tap to select, and keep the link effect tied to selection.
- Canvas and SVG: update the same strength map in the draw loop; avoid per-element listeners.

## Combining forms

The forms nest. A selection can be linked (neighbors react) while the reaction itself is a domino (neighbors respond in order of distance at list-item offsets, timing-and-tokens.md §Stagger). A transition can run instant for the container and domino for its contents. Name each layer in the classification line.

## Interaction with synchronization

Interactive and synchronized are not exclusive. The interaction drives the animation; the synchronization defines what else moves. During direct manipulation the manipulated element stays locked to the pointer with no easing, while linked elements may follow with light easing or a spring.

## Pitfalls

- Treating a stagger as the only synchronization tool; it only covers the domino form.
- Domino chains that delay the useful content.
- Uniform offsets and distances.
- Linked reactions with unbounded reach.
- Linked state that never resets after a fast pointer exit.
- Animating both a container and its staggered children.
- Different clocks inside a group that should read as one object.
