# Classification

> **Connections** (paths are relative to `references/`)
> - Read when: phase 1 of every run, before choosing any technique, or when unsure whether something is scope, interaction, synchronization, technique or timing.
> - Skip when: the classification line is already written and unchanged.
> - Read next: `synchronization.md` (if two or more elements animate); `gate.md` (the next phase).

Animation is described along five independent dimensions. Mixing them up is the most common reason an animation feels arbitrary: "fade" is a technique, not a role. Decide the roles first.

## Contents
- The five dimensions
- Design order
- Interaction
- Scope
- Synchronization (summary)
- Direction
- Technique and timing
- The classification line

## The five dimensions

```text
1 Synchronization   how animations relate to each other
2 Interaction       whether the animation responds to the user
3 Scope             what part of the interface is animated
4 Technique         how the visual movement is performed
5 Timing            how the animation progresses over time
```

They are independent. An animation can be interactive and linked and component-scoped, using a scale technique with an ease-out timing. Changing one dimension does not force a change in the others.

## Design order

```text
1 Scope             given by the command
2 Interaction       does the user's action drive or shape it?
3 Synchronization   do several animations need a defined relationship?
4 Direction         for transitions: forward and backward
5 Technique         what movement represents the change?
6 Timing            how does it progress, and for how long?
```

Technique and timing come last because they are the cheapest decisions to change and the easiest to get wrong when made first. Ask, in order: what is being animated, why, does it respond to input, does it relate to other animations, is it a move between states, which visual technique expresses it, which timing produces the feel.

## Interaction

| Value | Meaning | Examples |
|---|---|---|
| Non-interactive | Plays on a trigger the user does not shape | Entrance on mount, success confirmation, ambient loop |
| Interactive | The user's action drives or modulates it | Hover, press, drag, touch, scrub, pointer tracking |

Interactive animations need immediate response: press at 0ms, drag locked to the pointer with no easing, easing only after release. Interactive and synchronized are not exclusive: one element's interaction can drive others.

## Scope

| Scope | Unit | Typical decisions |
|---|---|---|
| Micro | One element or a small part of one | Which states exist, how often it is seen, which technique expresses feedback |
| Component | The component as one visual unit | Enter, exit, move, emphasis; relation between container and children |
| Transition | The change from state A to state B | State graph, forward and backward, direction awareness, interruption |

Micro animations stay small in scope but can use any technique and can be interactive. A component animation treats the component as one thing even though it contains many parts. A transition always answers: how does the interface move from the current state to the next, and back?

## Synchronization (summary)

```text
Synchronized animation
├── Instant synchronous   elements share the same timing
├── Domino / sequential   elements follow one another in order
└── Linked                elements respond through a defined relationship
```

Synchronization does not require identical animations. Different elements can use different techniques and still be synchronized through shared timing, sequence, or relationship. Patterns and code are in the synchronization reference.

## Direction

Only transitions require explicit direction, and a professional transition defines both. For every forward step there is a designed reverse. The reverse is usually not a mirror image: it can be shorter, quieter, or use a different curve. Never design only the forward path and let the backward path fall back to a default.

The equivalent pairs elsewhere: enter and exit for components; press and release, hover in and hover out for micro animations. Design both halves of every pair.

## Technique and timing

Technique answers "what movement": fade, slide, scale, move, rotate, reflect, morph, mask, blur, stagger, spring. Timing answers "how it progresses": duration, delay, easing or spring, stagger offset. These terms describe behavior, not role, and never replace the scope, interaction and synchronization decisions.

## The classification line

Write the result as one line and keep it visible through the run:

```text
scope=component · interaction=non-interactive · sync=domino · direction=enter/exit · technique=<later> · timing=<later>
```

Fill technique and timing only after the gate and the style decision. If a dimension is unknown, say so and resolve it before building.
