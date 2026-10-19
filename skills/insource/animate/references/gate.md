# Gate

> **Connections** (paths are relative to `references/`)
> - Read when: phase 2 of every run, before any creative work, and whenever animation is requested on something frequent or keyboard-driven.
> - Skip when: never skip during a run; skip only for pure vocabulary questions or diagnosis with no build.
> - Read next: `discovery.md` (if the target is broad); `creative-direction.md` (if the outcome is animate or reduce and the style is creative).

Decide whether and how much to animate before any creative work. Expect to reduce or refuse often; an interface that needs little animation is a good result.

## Contents
- The four questions
- Frequency tiers
- Valid purposes
- Speed budget
- Function
- Tiers
- Outcomes
- Novelty and one-shot rules

## The four questions

Answer in order and record the answers.

1. **Frequency.** How often will a user see this?
2. **Purpose.** Why does it animate? It must be one of the valid purposes below.
3. **Speed.** Can it stay within the budget for its element type?
4. **Function.** Does motion help or hinder here?

## Frequency tiers

| Frequency | Verdict |
|---|---|
| 100+ times a day (keyboard shortcuts, command palette, core navigation) | No animation. Animating makes repeated actions feel slow and disconnected. |
| Tens of times a day (hover states, list navigation, frequent toggles) | Reject, or near-imperceptible, very fast, subtle motion only. |
| Occasional (modals, drawers, toasts, settings) | Standard animation. |
| Rare or first time (onboarding, empty states, success, celebration) | Eligible for delight and creative treatment. |

Keyboard-initiated actions are a disqualifier, not a judgment call. Focus and repeated navigation stay immediate; a state transition may animate only if focus and task completion do not wait for it.

## Valid purposes

- **Feedback**: confirms the interface heard the user (press, hold-to-confirm).
- **Spatial consistency**: shows where something came from or went (a panel grows from its trigger).
- **State indication**: makes a change legible (a morphing button, an expanding section).
- **Preventing a jarring change**: bridges content that would otherwise teleport.
- **Explanation**: demonstrates how something works (marketing, onboarding).
- **Delight**: only at the rare or first-time tier.

"It looks cool" is not a purpose. If you cannot name one, reject the candidate.

## Speed budget

| Element | Duration |
|---|---|
| Press feedback | 100 to 160ms |
| Tooltips, small popovers | 125 to 200ms |
| Dropdowns, selects | 150 to 250ms |
| Modals, drawers | 200 to 350ms |
| Rare moments | up to about 600ms |
| Showcase or marketing | longer, with labeled beats |

Routine UI stays under 300ms. A steep curve can afford a longer duration because most of the distance is covered early.

## Function

Decoration on functional, information-dense UI hinders. Data the user is reading or acting on should not move for style. A pointer-tracking effect is fine on a marketing page and wrong on a financial chart.

## Tiers

The gate outputs a tier that scopes every later value:

| Tier | Where | Latitude |
|---|---|---|
| Routine | Frequent or functional UI | Short, restrained, no flourish |
| Rare | Occasional or first-time moments | Medium durations, small flourish, creative welcome |
| Showcase | Marketing, hero, onboarding story | Longer, staged beats, strongest creative latitude |

## Outcomes

- **Animate**: proceed with the tier.
- **Reduce**: fewer properties, shorter, smaller transform. Say what was removed and why.
- **None**: stop and explain with the question that failed. Offer the closest legitimate alternative (an instant state change with a clear visual cue) if useful.

When recommending style: rare and showcase tiers favor creative; routine favors traditional or minimal.

## Novelty and one-shot rules

- Keep most of a surface familiar: roughly 90% expected animation and 10% novel. Do not stack high-novelty beats in consecutive sections.
- First-run staggers, intro morphs and login flourishes play once. Gate them with a stored flag so a reload is instant.
