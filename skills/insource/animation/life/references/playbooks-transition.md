# Playbook: transition

> Owns the state-graph workflow, direction awareness, and the rule that navigation is never blocked on the animation. Routing lives in ../SKILL.md.

Animating the move from one state, view or page to another. The question is always: how does the interface move from the current state to the next, and back?

## Workflow

1. Map the **state graph**: list every state and every permitted move between them (including jumps, such as step 1 to step 4, and direct reverse).
2. Write a **forward and reverse table** with one row per move. Fill both columns.
3. Gate the transition: how often is it taken? Core navigation used constantly gets a minimal, fast transition; onboarding gets expressive treatment.
4. Classify: what persists across the change (shared elements), what is replaced, and the synchronization form (often domino or instant; linked for related elements).
5. Choose technique and timing; design the reverse as its own motion.
6. Test rapid back-and-forth, interruption mid-flight, skipped steps and reduced motion.

## Forward and reverse table

| Move | Forward motion | Reverse motion | Notes |
|---|---|---|---|
| Step 1 to 2 | Content slides left 24px, fades; next enters from the right | Mirror, slightly shorter | Same easing family |
| Step 2 to 3 | ... | ... | ... |
| Open detail from list | Shared element expands | Collapses back to the item's position | Reverse follows the pointer or gesture when swiped |

A row with an empty reverse column is an unfinished design: the never-bend rule (every forward has a reverse) lives in ../SKILL.md.

## Direction awareness

Content moves in the direction of the navigation: forward steps travel the reading direction, backward steps the opposite. In right-to-left layouts the physical directions flip; derive direction from the layout, not hard-coded signs. Tabs move toward the newly selected tab; hierarchical navigation moves deeper on forward and shallower on back.

## Standard recipes

Step or tab content swap (directional, interruptible)

```css
[data-dir="forward"] .incoming { animation: in-forward 260ms var(--ease-move) both; }
[data-dir="forward"] .outgoing { animation: out-forward 200ms var(--ease-move) both; }
[data-dir="back"]    .incoming { animation: in-back 260ms var(--ease-move) both; }
[data-dir="back"]    .outgoing { animation: out-back 200ms var(--ease-move) both; }
@keyframes in-forward  { from { opacity: 0; transform: translateX(24px); } }
@keyframes out-forward { to   { opacity: 0; transform: translateX(-24px); } }
@keyframes in-back     { from { opacity: 0; transform: translateX(-24px); } }
@keyframes out-back    { to   { opacity: 0; transform: translateX(24px); } }
```

Crossfade with bridge: when two states overlap in place, add a 2 to 4px blur to the outgoing and incoming content so the eye reads one object changing.

Tab indicator: move and resize the indicator with transform (position) and clip-path or scale (size); the active label color fades.

Text and number swaps inside a transition follow the micro playbook.

Progress through steps: progress bar scales on X with the content swap sharing easing and duration.

## Page and route transitions

- Keep them short — the page-transition band in timing-and-tokens.md governs the duration. Navigation used all the time is a candidate for the platform's view transitions or for a subtle crossfade only.
- Shell preservation during a route change: entrances-and-exits.md (page load and screen mount).
- Mount-based exit animation on route change needs the framework's exit-aware wrapper; see the Next.js stack file for the App Router pattern and the CSS-native file for view transitions.
- Never block navigation on the animation: the new route starts loading immediately; the animation covers the wait.

## Shared elements and morphs

- Use a shared element transition when an element travels between two places (thumbnail to hero). Give both ends one identifier.
- Use a container morph when the trigger becomes the next surface. Open with a slight overshoot, close with a clean ease.
- Fallback to a crossfade when a shared identifier is not available on one end.

## Interruption, skipping, loading

- **Interruption**: the user taps back mid-flight. Retarget from the current state; with springs, preserve velocity. Do not queue the animations.
- **Skipping**: a jump across several states plays one transition, not three. Choose direction from the index difference.
- **Rapid toggling**: retargeting versus restarting is owned by performance-and-accessibility.md (Implementation order).
- **Loading**: when the next state needs data, animate the container to its destination and show a skeleton; avoid a spinner that blocks the move.
- **Gesture-driven**: back-swipe scrubs the reverse motion with the finger and completes on release based on velocity.

## Creative lanes for transition

The idea lanes are owned by creative-direction.md (master lanes table); pick lanes there that suit a move between two states.

## Checklist

- [ ] State graph written; every move has a forward and reverse entry
- [ ] Direction derived from layout (including right-to-left)
- [ ] Reverse is designed, not a default
- [ ] Rapid back-and-forth and mid-flight interruption tested
- [ ] Skipped steps play one transition
- [ ] Navigation does not wait for the animation
- [ ] Reduced-motion variant (opacity only, no travel)
