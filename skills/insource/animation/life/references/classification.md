# Classification

> Owns the six descriptive dimensions and the classification line; routing lives in `../SKILL.md`.

Animation is described along six independent dimensions. Mixing them up is the most common reason an animation feels arbitrary: "fade" is a technique, not a role. Decide the roles first.

## The six dimensions

```text
1 Synchronization   how animations relate to each other
2 Interaction       whether the animation responds to the user
3 Scope             what part of the interface is animated
4 Direction         for transitions: forward and backward
5 Technique         how the visual movement is performed
6 Timing            how the animation progresses over time
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

The three scopes, their units and their commands: the hub's Commands table (`../SKILL.md`). A transition always answers: how does the interface move from the current state to the next, and back?

## Synchronization

The three forms (instant, domino, linked), their rules and patterns: see synchronization.md. Synchronization does not require identical animations: different elements can use different techniques and still be synchronized through shared timing, sequence, or relationship.

## Direction

Only transitions require explicit direction, and a professional transition defines both halves of every pair (enter/exit, press/release, forward/reverse); the pairs and their design rules: see entrances-and-exits.md.

## Technique and timing

Technique answers "what movement": fade, slide, scale, move, rotate, reflect, morph, mask, blur, stagger, spring. Timing answers "how it progresses": duration, delay, easing or spring, stagger offset. These terms describe behavior, not role, and never replace the scope, interaction and synchronization decisions.

## The classification line

Write the result as the Classification row of the hub's Output contract (`../SKILL.md`) and keep it visible through the run. Fill technique and timing only after the gate and the style decision; if a dimension is unknown, say so and resolve it before building.
