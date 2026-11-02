# Run procedure

> Sole home of the 8-phase run procedure and the stop points; routing lives in `../SKILL.md`.

The detailed steps of every run. The hub (`../SKILL.md`) lists the phases; this file says exactly what to do in each, what to decide, and where to stop for the user.

## Phase 0: Understand

Parse the command and target and interpret the request per the hub (Commands table and "Interpret the request"), translating vague wording via intent-resolution.md and restating it in one line; confirm only if two readings would lead to different builds. If the user asked for several scopes, do the command's scope and list the rest as follow-ups.

## Phase 1: Survey and classify

1. Recon: stack and animation library, existing tokens, existing animations in and around the target, reduced-motion handling, the product's personality (crisp or playful), how often people meet the target. Pick the stack file that matches.
2. Broad target (directory, route tree, page with many parts, whole project) or "I don't know what to animate": run discovery. It is read-only. Present survivors and the rejected list, then wait for the pick. Continue with each pick separately.
3. Recording or reference supplied: run the match workflow first and carry its measurements forward.
4. Existing animation that "feels off": review it first in existing mode (run the audit script, read the debugging symptoms), then decide between improving and redesigning.
5. Classify in order: scope (given), interaction, synchronization, and for transitions the states and direction. Write the classification line.

## Phase 2: Gate

Answer the four questions (frequency, purpose, speed, function) and record the answers. Outcome: animate, reduce or none, plus a tier. If none: say which question failed, offer the closest legitimate alternative if useful, and stop. Do not invent an animation to look useful.

## Phase 3: Style

Ask one question: creative or traditional, with a recommendation (creative for rare or occasional expressive surfaces, traditional or minimal for frequent or functional ones). If the user already stated a preference, use it and skip the question. Do not default to plain fade, slide or scale unless the user chose traditional.

## Phase 4: Options (creative style)

1. Produce two to four options that differ in concept, from different lanes (lanes: creative-direction.md).
2. Review each option against the standards in spec mode (review-standards.md) before showing it.
3. Write the spec and run the validator; fix every error. Build the prototype with the builder (spec format and prototype writing: prototype-ascii.md). Default location: `.animate/prototypes/`, outside the source tree.
4. ASCII is the default. Ask the ASCII-or-HTML question only when an option meets the escalation criteria in prototype-html.md; build live demos only for the options that need them.
5. Give the file path, one line per option, and a recommendation. Offer a remix. Wait for the pick. Write no production code first.

Traditional style: state the spec in a few lines (technique, duration, easing, properties, origin, reverse) and go to the build.

## Phase 5: Build

1. Read the command's playbook, the timing reference, and the performance and accessibility reference. Read the stack file for the project.
2. Implement every state the classification named: enter and exit, forward and reverse, hover and focus and press. Never ship half of a pair.
3. Use the project's tokens when they exist, otherwise the canonical ones. Do not add a dependency unless the animation cannot be done otherwise.
4. Keep it interruptible, compositor-friendly and reduced-motion safe.
5. Keep prototypes out of the source tree; leave them in `.animate/`.

## Phase 6: Review

1. Run the audit script on the files you changed (tier flag matches the gate's tier). The script never edits files.
2. Review against the ten standards in built mode and run the fix loop; the loop, the findings format and the verdict live in `review-standards.md`.
3. State what only a human can judge (feel, timing under real load, gestures on a device) and how to check it.

## Phase 7: Report

Use the output contract from the hub. Keep it short: classification line, decision, files changed, exact values, review result, human checks, follow-ups.

## Stop points

Wait for the user only here: the optional confirmation in phase 0, the pick after discovery, the style question, the option pick, and the ASCII-or-HTML question. Everything else proceeds without asking.

## Mixed scopes and mismatches

- `micro` aimed at a whole component: list the elements inside and ask which one, or suggest the component command.
- `component` aimed at a page: run discovery for components inside it.
- `transition` aimed at a single element with two states: treat as a transition if the point is the change between the states; otherwise micro.
- A request touching all three: do the command's scope; list the others as follow-up commands.

## Resuming after a pick

Restate the pick as a command (`life component SaveBar.tsx`) and continue from phase 2 with the pick's tier. Keep unpicked survivors for the final follow-ups list.
