# Creative direction

> Owner of the master idea-lanes table and of how creative options are conceived and presented. Routing lives in ../SKILL.md.

How to produce animation ideas that are not the default fade or slide, and how to present them so the user can choose.

## What creative means here

A creative animation expresses the specific change or the specific thing, instead of applying a generic entrance. A traditional animation applies a standard effect: fade, slide, simple scale. Both can be well crafted; creative is the preferred starting point where the gate allows it, because generic effects make every interface feel the same.

## When creative is appropriate

The tier and animate/reduce/none verdict are owned by gate.md, and the style question procedure by run-procedure.md (phase 3). When ideating, state the recommendation and its reason and let the user decide.

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

The phase procedure (spec, validator, review in spec mode, the pick) is owned by run-procedure.md (phase 4); the spec fields by prototype-ascii.md; the `needs_html` escalation criteria by prototype-html.md. Creative-specific guidance for the set itself:

1. Make the options differ in idea, not in duration or easing.
2. Add one restrained option when the others are bold, so the user can see the range.
3. Rank and recommend one with a reason.

## Anti-clichés

Reject options that are only: fade plus a 20px upward slide on everything, confetti or sparkles by default, bounce on every element, glow on hover everywhere, a spinning or pulsing attention-getter on routine UI, parallax on body text, and any effect added because it is available. If the idea does not come from the subject, it is decoration.

## Constraints that never bend

Owned elsewhere: review-standards.md (the ten standards) and performance-and-accessibility.md (properties, interruptibility, reduced motion, hover gating, looping). Every option must satisfy them before it is shown.

## Comparing options

Present the options so the user can compare quickly: the prototype file, one line per option (name, concept, feel), and a recommendation. Offer a remix ("A's reveal with C's timing") before building. Record the chosen option in the spec so the build uses its exact values.

## Traditional fallback

The traditional route and its spec form are owned by run-procedure.md (phases 3 to 5); choose from the playbooks' standard recipes and tokens.
