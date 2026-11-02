# Intent resolution

> Owns vague-wording and feeling translation plus the confirmation template; routing lives in `../SKILL.md`.

Turn vague wording into precise animation terms and classification values. The user should leave knowing the name of what they asked for.

## Procedure

1. Read for intent, not keywords. People describe what they see or feel ("springy", "slides off", "draws itself in").
2. Sort the phrase into one of the three kinds below.
3. Map it to glossary terms (see the vocabulary reference) and to classification dimensions.
4. Restate the translation in one line using the precise terms.
5. Confirm only if two readings would lead to different builds. Otherwise proceed and let the report show the interpretation.

## Three kinds of vague input

| Kind | The user says | Map to |
|---|---|---|
| Effect description | "slides off", "grows out of the button", "draws itself", "turns into" | A glossary term: slide out, origin-aware animation, line drawing, morph |
| Feeling | "premium", "snappy", "alive", "playful", "calm" | Timing and technique parameters (next table) |
| Relationship | "when I hover one the others react", "one after another", "all at once" | A synchronization form |

## Feeling to parameters

| Feeling | Duration | Easing or spring | Technique lean | Avoid |
|---|---|---|---|---|
| Snappy, responsive | Short end of the range | Steep ease-out, stiff spring | Transform and opacity, small distances | Delays, long settles |
| Premium, refined | Restrained; one slower hero beat | Soft ease-out or critically damped spring | Subtle blur bridge, light or depth cues, careful stagger | Bounce, exaggerated scale, many simultaneous effects |
| Alive, organic | Mixed durations that do not sync | Springs with slight overshoot only after momentum | Ambient float, idle loops with offset durations, velocity-aware motion | Mechanical uniform loops |
| Playful, friendly | Moderate | Springs with visible bounce (0.2 to 0.3) | Overshoot, squash and stretch, small rotations | Bounce on serious or frequent UI |
| Calm, quiet | Longer, low amplitude | Critically damped | Fades with tiny translation, slow opacity | Sudden movement, strong contrast changes |
| Fast, efficient (tool UI) | Minimal | Ease-out | Often no animation | Anything decorative on frequent actions |
| Dramatic, cinematic | Longer, with labeled beats | Expo-style ease-out | Staged reveals, depth, mask | Using it on routine UI |
| Dead, flat, "needs life" | Not a parameter: a request to find opportunities | n/a | Run discovery before designing | Animating everything |

"Feels dead" or "feels janky" are diagnoses, not briefs: the first leads to discovery, the second to the debugging reference.

## Relationship phrases

Phrases like "all together", "one after another", "the related ones react" name a synchronization form; the forms and their rules: see synchronization.md.

## Routing

Name the job (entrance, exit, feedback, transition, ...) and take it to the hub's job table (`../SKILL.md`); routing is the hub's job, not this file's.

## Disambiguation pairs

Contrast close terms so the user can choose:
- Clip-path vs mask: hard geometric edge vs soft, fadeable edge.
- Pop in vs bounce: overshoot on entry only vs a repeated spring.
- Shared element transition vs layout animation: an element travels between two places vs one element animates to its new size or position.
- Crossfade vs morph: two things overlap in place vs one shape becomes another.
- Stagger vs domino: offset starts of the same effect vs one animation handing off to the next.
- Scroll reveal vs scroll-driven: starts once on entry vs progress follows the scroll position.

## When nothing matches

Name the closest term and say it is an approximation, or describe the effect in glossary words ("a stagger of scale-in entrances"). Do not invent a term. Offer one clarifying question only if the build would differ.

## Confirmation template

```text
I read this as: <precise term(s)> · scope=<>, interaction=<>, sync=<> · feel=<parameters>.
Proceeding on that unless you meant <the other reading>.
```
