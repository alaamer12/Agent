# Creative direction

> **Connections** (paths are relative to `references/`)
> - Read when: the user chose creative style, or asks for something unique, innovative or 'not the usual fade'.
> - Skip when: the user chose traditional style or the gate said none.
> - Read next: `prototype-ascii.md` (to write and build the option file); `prototype-html.md` (if an option needs light, depth or live behavior).

How to produce animation ideas that are not the default fade or slide, and how to present them so the user can choose.

## Contents
- What creative means here
- When creative is appropriate
- Idea sources
- Idea lanes
- Building the option set
- Anti-clichés
- Constraints that never bend
- Comparing options
- Traditional fallback

## What creative means here

A creative animation expresses the specific change or the specific thing, instead of applying a generic entrance. A traditional animation applies a standard effect: fade, slide, simple scale. Both can be well crafted; creative is the preferred starting point where the gate allows it, because generic effects make every interface feel the same.

## When creative is appropriate

| Context | Style to recommend |
|---|---|
| Rare or first-time moments, onboarding, success, empty states, hero, showcase | Creative |
| Occasional surfaces with a strong brand personality | Creative, restrained |
| Frequent or functional UI, data the user reads, keyboard-driven actions | Traditional or none |

Ask once. State the recommendation and the reason, and let the user decide.

## Idea sources

Ideas come from the subject, not from a technique list. For each target ask:

1. **What is changing for the user?** The meaning of the state change (saved, expanded, handed off, arrived, rejected).
2. **What is the object?** Its material or mechanism (paper, glass, a latch, a counter, a card, a circuit). Motion borrowed from the real behavior of that object feels earned.
3. **Where did it come from and where is it going?** The spatial story: origin, destination, hand-off.
4. **What is the brand temperament?** Precise, warm, playful, technical, calm.
5. **What already exists on screen?** Shapes, colors and lines that can transform instead of new things appearing.

## Idea lanes

Draw options from different lanes so they are genuinely different, not variations of one effect:

| Lane | Idea shape |
|---|---|
| Self-transformation | The element becomes the next state (container morph, shape morph, text morph) |
| Reveal | Content uncovered by a clip, mask or wipe that follows the content's geometry |
| Light and material | Reflection, sheen, glass response, depth shading, pressure |
| Physics | Weight, momentum, spring settle, rubber-banding, magnetic pull |
| Choreography | Domino order or linked propagation that tells a story across elements |
| Typographic | Per-word or per-character motion, number rolls, weight or width shifts |
| Depth | Perspective tilt, parallax layers, orbit, flip |
| Ambient | Idle float, breathing, drifting light that gives a static element life |
| Trace | A line drawing or path that follows the element's outline or meaning |

## Building the option set

1. Produce two to four options, each from a different lane. Three is a good default.
2. For each option write: a name, the concept in one sentence, techniques, synchronization form, timing (duration and easing), the tier it fits, a one-line description of the feel, the reverse behavior (for pairs), and the main risk (performance, accessibility, complexity).
3. Make the options differ in idea, not in duration or easing.
4. Add one restrained option when the others are bold, so the user can see the range.
5. Rank and recommend one with a reason.
6. Run every option through the standards before showing it: no layout-property animation, a reduced-motion plan, interruptibility, and a duration within tier.
7. Decide per option whether ASCII can communicate it. Light, reflection, depth, blur, continuous curves, 3D and pointer response usually cannot; mark those `needs_html` with a reason.

## Anti-clichés

Reject options that are only: fade plus a 20px upward slide on everything, confetti or sparkles by default, bounce on every element, glow on hover everywhere, a spinning or pulsing attention-getter on routine UI, parallax on body text, and any effect added because it is available. If the idea does not come from the subject, it is decoration.

## Constraints that never bend

- Animate transform and opacity (plus small, bounded filter changes). No width, height, top, left, margin or padding, except a deliberate, labeled container tween.
- Interruptible: transitions and springs, not restarting keyframes, for anything triggered rapidly or by gesture.
- Reduced motion has a defined, gentler variant.
- Tier limits on duration.
- Hover effects are gated to devices that hover.
- Looping decoration pauses off-screen.

## Comparing options

Present the options so the user can compare quickly: the prototype file, one line per option (name, concept, feel), and a recommendation. Offer a remix ("A's reveal with C's timing") before building. Record the chosen option in the spec so the build uses its exact values.

## Traditional fallback

If the user chooses traditional, or the gate leaves little room, choose from the playbooks' standard recipes and tokens. State the spec in a few lines. Even traditional animation gets correct origin, easing, interruptibility and a designed reverse.
