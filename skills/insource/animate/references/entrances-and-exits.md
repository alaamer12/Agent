# Entrances and exits

> **Connections** (paths are relative to `references/`)
> - Read when: something appears or leaves: first-run or onboarding intros, hero, page load, sections, lists, dialogs opening and closing, dismissal, removal; words like intro, appear, show up, fade in, pop in, close, dismiss.
> - Skip when: the change is between two states that both stay (use the transition playbook) or it is pure press, hover or focus feedback (use the micro playbook).
> - Read next: `playbooks-component.md` (for overlays and containers); `playbooks-transition.md` (for onboarding steps and route changes); `synchronization.md` (for ordered arrivals); `scroll.md` (when the entrance fires on scroll).

How things arrive and leave: first-run and onboarding intros, hero and page load, sections and lists appearing, overlays opening and closing, dismissal and removal. Everything the user describes as "appear", "show up", "intro", "on start", "fade in", "pop in", "close", "dismiss" or "disappear" lands here.

## Contents
- Which kind of entrance
- Entrance anatomy
- First-run and onboarding intros
- Page load and screen mount
- Lists and groups appearing
- Exits
- Pairs table
- Mistakes
- Checklist

## Which kind of entrance

| Situation | Treatment | Tier |
|---|---|---|
| First-run, onboarding, welcome, intro, hero | Staged, a few labeled beats, plays once | rare or showcase |
| Screen or page mount | Shell stays; content eases in; short | routine, rare if first visit |
| Section revealed on scroll | Reveal once, small offset | routine |
| List, grid or cards appearing | Domino stagger with a short total, grouped past about five items | routine, rare if first visit |
| Dialog, popover, drawer, toast opening | Origin-aware, fast (see the component playbook for recipes) | routine |
| Content replacing other content | That is a transition, not an entrance (see the transition playbook) | n/a |

## Entrance anatomy

1. **Start state.** Offset (8 to 16px) plus reduced scale (0.95 to 0.97) plus opacity 0. Never from nothing: no scale from zero.
2. **Origin.** Where the attention is or where it came from: trigger, edge, center.
3. **Easing.** Ease-out: fast start, gentle landing. Use the entrance curve from the tokens.
4. **Duration.** Tier-appropriate; scale with distance.
5. **Container first, content after.** If the container itself moves in, its children are already laid out. If the children stagger, the container does not also move. One level of entrance per container.
6. **Secondary action.** A small blur (2 to 4px) or slight scale layered on the fade adds depth without a second big motion.
7. **Overlap and follow-through.** Parts land slightly after the main move (50 to 100ms) and settle.

## First-run and onboarding intros

The most expressive entrance, and the one most likely to annoy on the tenth visit.

- **Play once.** Gate with a stored flag so returning users get the final state immediately. A reload never replays an intro.
- **Never block.** Input works while the intro plays; offer skip (tap, key, or a visible control). A forced intro longer than a couple of seconds is a defect.
- **Stage in beats.** One idea per beat, in order of importance, with overlap:

```text
0ms     background settles (opacity)
80ms    headline arrives (offset + opacity, ease-out)
220ms   supporting text follows (smaller offset)
360ms   call to action lands last (slight scale 0.97 -> 1)
```

  Keep the total inside the tier cap: about 600ms for rare, longer only at showcase with labeled beats.
- **Staging.** Lead with the element the user should look at first; the call to action arrives last so it is not buried or missed.
- **Variety without clutter.** Keep roughly 90% familiar and 10% novel. One memorable beat beats five.
- **Multi-step onboarding.** The intro is an entrance; the move between onboarding steps is a transition with a designed reverse. Treat them separately.
- **Creative lanes that suit intros:** self-transformation (a logo becomes the first screen), reveal (a mask following the headline), typographic (per-word arrival, hero only), depth (layered parallax settle), ambient (a gentle idle after arrival). Each needs the gate's tier to allow it.
- **Reduced motion.** Show the final state immediately or a short opacity fade; drop travel, scale and parallax.
- **Do not animate what people came to read or act on.** Content the user needs immediately appears fast; decoration may take its time.

## Page load and screen mount

- The shell (header, navigation) is static. Only the content area enters.
- A short ease-out fade with a small offset (250 to 320ms) is plenty. Frequent screens get the lightest version or none.
- Reserve space so nothing shifts after arrival.
- Do not animate on every navigation of a screen visited constantly; the gate decides.

## Lists and groups appearing

- Domino stagger: 30 to 50ms per item, whole list done within about 300ms; section-level offsets 80 to 100ms.
- Past about five items, animate groups or only the first visible items; the rest appear instantly.
- Vary offset and distance by importance; uniform steps feel mechanical.
- Never block interaction while a stagger plays. Items added later (not first load) enter alone, without stagger.

## Exits

- **Quieter and faster than the entrance**: roughly 20% shorter, simpler.
- **Small fixed offset** (4 to 12px) in the direction it leaves, rather than full travel.
- **Same path back** for dismissible surfaces, so swipe-away and button-close feel like one motion.
- **Removal closes the gap**: neighbors move up with a layout animation after the item leaves.
- **Never skip the exit.** A surface that animates in and vanishes out feels broken. In frameworks, exits need the presence wrapper (see the stack file).
- **Dismissal by gesture** continues in the direction of travel with the release velocity.
- **Destructive removals** can be slightly slower than routine ones so the action reads as deliberate.
- **Reduced motion**: opacity only.

## Pairs table

Fill it for the target:

| Entrance | Exit | Notes |
|---|---|---|
| Fade, 8px up, scale 0.97, 240ms | Fade, 4px down, 160ms | Same curve |
| Edge slide, drawer curve, 320ms | Edge slide, 220ms | Gesture can scrub either |

## Mistakes

- Starting from scale zero or from fully offscreen for a small element.
- Animating a container and its children together.
- Intros that replay on every visit, or that cannot be skipped.
- Long staggers on frequent lists.
- Entrance with no exit, or an exit slower than the entrance.
- Center origin on an anchored surface.
- Opacity-only entrances on surfaces that deserve a spatial cue.

## Checklist

- [ ] Kind of entrance chosen from the table, with its tier
- [ ] Start state is offset plus slight scale plus opacity
- [ ] One level of entrance per container
- [ ] Intro plays once, is skippable, never blocks input
- [ ] Exit designed, shorter than the entrance, same path back
- [ ] Reduced-motion variant stated
