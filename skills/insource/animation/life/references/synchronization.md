# Synchronization and choreography

> Owns how two or more moving elements relate: cast, the five relations, hard rules, moment sync, adaptive timing, direction and exits, interruption, attention loops, reduce behavior, and the timeline artifact. Value ranges belong to timing-and-tokens.md. Implementation patterns: choreography-recipes.md. Routing: `../SKILL.md`.

A group reads as one intentional motion when order, overlap, timing and stillness are *decided* — not when every part animates smoothly on its own. The default failure is choreographing by addition: every child gets a delay, the panel slides then its items trickle in; each piece is nice, and the user waits for the interface to finish performing before using it. Good choreography is mostly **cutting moving parts and running the rest in parallel**.

Sequence only when order carries meaning: reading order, cause → effect, or one thing physically arriving before another. A sequence that means something reads as a **wave** (one gesture); one that doesn't reads as a **queue**. Uniform timing affects a group the way `linear` affects one element.

## Hard rules

1. **One entrance per container.** If the panel slides in, its content is already there. Never animate a parent's entrance *and* stagger its children — that is two entrance layers the user waits through.
2. **Never stagger high-frequency or keyboard-triggered UI.** Dropdown items, menu rows, command palettes, tab content: appear together, or with no animation. A stagger looks nice once and slows every use after.
3. **Uniform stagger is forbidden.** Same delay + same distance + same duration + same easing on every item = metronome. Vary by importance; let gaps shrink as the group goes on.
4. **Choreography never blocks interaction.** Everything on screen is clickable as soon as it is visible; a delayed item must not hold back a button the user is already reaching for.
5. **Every sequence must survive interruption.** If a mid-flight re-trigger replays out of order or stacks animations, it isn't finished. See §Interruption.
6. **Reduced motion collapses the choreography, not just shortens it.** Drop delays and movement, keep opacity, let the group appear together. If the sequence *is* the explanation, jump between frames instead of animating them.

## Step 1 — cast the elements

Before any timing, list every element that moves on the event and give each a role (vocabulary rows in `../data.csv`):

| Role | What it is | Treatment |
|---|---|---|
| **Lead** | the one thing the user must notice — title, new view, acted-on item | moves first, travels most, stays longest |
| **Support** | secondary content following the lead — subtitle, CTAs, rest of list | shorter, smaller motion |
| **Decoration** | pills, badges, accents, dividers | fade only — or nothing at all |
| **Static** | everything else, including containers whose content animates | does not animate |

More than one element wanting to be the lead = a hierarchy problem motion cannot fix; say so. Most groups shrink at this step: a side panel with eight menu items becomes *one* move — the panel slides, the items are simply there.

## Step 2 — pick the relation for each pair

```
Do both elements belong to the same visual object or the same moment?
├── Yes → TOGETHER — same start, one timing family.
└── No → does the order carry meaning (reading order, cause → effect, arrival)?
         ├── No → TOGETHER — order without meaning is just delay.
         └── Yes → would showing both at once look broken (overlap, pass-through,
         │        two rich views fighting)?
         │        ├── Yes → SEQUENCE — second starts as the first finishes, or just before.
         │        └── No → OVERLAP — a stagger; second starts while first moves.
```

Plus a fifth that is not timing at all:

- **CARRY** — when a child's motion can't be steered directly (shared-layout/`layoutId`), animate the **parent** and let children ride. Images fly *into* the bin because the container they belong to moves, not because each image was tuned.

And the relation for interfaces that represent relationships:

- **LINKED** — acting on one element makes related elements react (§Linked below).

### Together, by default

- **A leaving element stops taking up space immediately.** Take it out of the layout at the moment of removal so siblings slide into the gap *while* it fades. Otherwise the gap closes only after the exit finishes: both motions smooth, the pause between them makes the whole interaction feel slow. (In Motion: `AnimatePresence mode="popLayout"`; without a library: `position: absolute` at the read offset before animating out.)
- **Swapping views in one container is a crossfade** — old exits while new enters — which means `popLayout` again, not default `sync` (which stacks both until the exit completes).
- **Sub-animations of one component share a timing family**: same duration, same easing family, so the component reads as one entity. A drawer that opens in 500ms then resizes in 200ms reads as two objects. Inner animations may use a *lighter* curve of the same family (slower content fade so the swap stays visible) — never a different family: ease-in-out body inside ease-out container feels out of sync. Set the family once (shared config or one CSS custom property).
- Paired elements (modal + overlay, tooltip + arrow) share duration and easing. Let techniques differ, not clocks.

### Overlap: the stagger

- Order follows **importance, not DOM order**; group title + first paragraph into one beat when they read as one unit.
- **Vary treatment, not just delay:** lead slides furthest, support less, decoration fades in place. Shrinking gaps (or eased delays) read organic; equal gaps read mechanical. Bands and totals: timing-and-tokens.md §Stagger.
- **Long lists stagger only the first handful**; the rest arrive with the last one. Item 20 must never wait 20× the delay.
- Direction follows reading order, or radiates outward from the point the user interacted with.

### Sequence: when to wait

- **Two rich states in a container that changes width *and* height**: the old content leaves before the new starts (safe default `mode="wait"`); to keep a crossfade anyway use the duplicate-view technique (choreography-recipes.md).
- **One element would visibly pass through another**: show the occluding face just as the movers land — a delay, not a full sequence.
- **Cause and effect draws**: the square draws, *then* the checkmark — second starts just before the first ends; both hold their end state (`forwards`/`both`). The slight handoff overlap is what turns a queue into one gesture.

## Step 3 — sync secondary motion to the moment that matters

Supporting effects hook onto a specific moment of the lead — its start, its **impact**, or its **settle** — not a delay that happens to look about right:

- **Sync to the cause, not the previous trigger.** Hover-then-click: the background pulses *on the click*, with the press — not on hover.
- **Land the accents with the lead.** Motion lines/sparkles complete as the main shape finishes (late slice of its timeline); most-important line first, others a few frames behind (values: timing-and-tokens.md §Choreography values).
- **A repeat action skips the buildup.** Once the hover state is set, the click plays immediately: same internal proportions, whole thing earlier.

## Step 4 — adapt timing to what changed

- **Scale duration by distance**: a big container jump needs the full fade; the same fade on a tiny jump flickers. Derive from the delta, clamp (formula + bounds: timing-and-tokens.md).
- **Scale bounce by size**: smaller elements need more bounce to read alive; one bounce value makes large views heavier or slower than their siblings (tuning: springs.md).
- **Few finite states ⇒ hardcode per transition.** A dozen hand-tuned pairs beat a clever formula nobody can fine-tune; formulas only when the state set is too large.

## Step 5 — direction and exits

- **Direction follows the mental model.** Forward moves content left (new enters from right); back reverses. Next and Back sliding the same way contradicts the action. Sibling-menu switches enter from the side of the trigger the user came from.
- **Exits read state at their start**, so the direction passes through to both the presence container and the child — otherwise the leaving element animates with its mount-time direction.
- **Exits are simultaneous, shorter, simpler.** Never reverse-stagger a closing group: the user already decided to leave.
- **An exit mirrors its entry.** Slid in from the right ⇒ leaves toward the right; a fade-only exit teleports the object.

## Interruption

A sequence has more states than a single animation — test each:

- **Re-trigger mid-sequence**: hover out halfway, click Next twice fast, switch menus while the first opens. Every run *stops* in-flight animations before starting new ones; never stack.
- **Wait for completion before chaining**: an idle loop resuming after a hover-out starts only when *all* reset animations finish (await them together), or it fights the reset.
- **Rapid view switching** can leave two children mounted: check explicitly; every child has a stable unique key (a missing key is the first suspect when an exit doesn't play).

## Attention loops

An idle animation that invites interaction (a hand that occasionally taps, an icon that wiggles): first run after a beat, repeats rarely, stops while the user interacts, resumes only after the interaction's reset completed. Values: timing-and-tokens.md §Choreography values.

## Linked

An action or animation on one element causes a corresponding effect on related elements. Fits interfaces that represent relationships: canvases, diagrams, graphs, editors, related rows, highlight systems.

### Model the relationship first

1. **Link source.** Where relationships come from (edges, shared id/group, parent relation, query).
2. **Link strength.** Equal reaction for all, or falloff with distance (hops).
3. **Link direction.** Symmetric, or one-way (parent selection affects children only).
4. **Reaction.** Same effect, or corresponding-but-different (source pulses, neighbors brighten, distant nodes dim).

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

Apply by writing one data attribute or custom property per element — not by animating from script every frame:

```ts
for (const [id, s] of linkedStrengths(graph, hoveredId)) {
  nodes.get(id)!.style.setProperty('--link', String(s));   // element-local property
}
```

```css
.node { opacity: calc(0.45 + 0.55 * var(--link, 1)); transition: opacity 160ms var(--ease); }
```

Plain-DOM relationships can ride CSS without script (`:has()` de-emphasis: stacks/css-native.md).

### Linked implementation notes

- Reset on leave/deselect, including elements a fast pointer skipped.
- Batch inside one frame; on large graphs update only changed strengths. Cap `maxHops` — a dense graph fully linked reads as noise and costs frames.
- Never color-only; respond to keyboard focus/selection, not only hover. No hover on touch: tap-to-select carries the link.
- Canvas/SVG: same strength map in the draw loop; avoid per-element listeners.

## Combining and interaction

Forms nest: a selection can be linked while its reaction sequences; a transition can be Together for the container and Overlap for its contents. Name each layer in the classification line. Interactive and synchronized are not exclusive: the interaction drives the animation, the synchronization defines what else moves — the manipulated element stays pointer-locked (no easing), relatives may follow with light easing or a spring.

## Tool choice

Pick the lightest tool that expresses the relationships (patterns: choreography-recipes.md):

- **CSS custom-property delays** on one keyframe — one-shot entrances.
- **Declarative variants with an eased, source-aware stagger** on the parent — groups entering/exiting with state.
- **Imperative orchestration** — only when several elements coordinate across several events and completion must be awaited; more powerful, much harder to maintain, never for a simple stagger.

## The timeline artifact

Before coding a multi-element run, write the timeline: one row per moving element in start order — element · role · start · duration · motion · relationship. Check it against the budgets (timing-and-tokens.md). Then list up to 5 elements motion was deliberately **removed** from, each with its reason ("Menu items: one entrance per container, the panel carries them"). If none were removed, say so.

Finish by feeling-checking: record the interaction and step through it — a wave and a queue look the same at full speed in your head and different on a recording. Then imagine the 50th use today; if you'd skip the animation, cut it.

**Tone:** talk in relationships and moments ("the lines land with the click"), not adjectives. When a sequence is fine as-is, say so; when the right choreography is no choreography, say that too.

## Pitfalls

- Choreographing by addition (more delays, more layers) instead of casting and cutting.
- Parent entrance + child stagger on one container.
- Stagger on high-frequency surfaces; uniform metronome delays anywhere.
- Sequencing when order carries no meaning (a queue, not a wave).
- Gap closing *after* the exit instead of during it (sync mode instead of popLayout).
- Two clocks in one object (open 500ms + resize 200ms; ease families mixed inside one component).
- Secondary effects with feel-delays instead of moments; accents that drift from the lead.
- Fixed duration across very different distances; one bounce across very different sizes.
- Reverse-staggering exits; fade-only exits for objects that slid in; same-direction Next/Back.
- Sequences untested against interruption; idle loops that never stop for input.
- Treating a stagger as the only synchronization tool; unbounded linked reach; linked state that never resets.
- Delayed items gating the interaction; reduced motion that merely shortens instead of collapsing.
