---
name: life
description: Designs, builds, reviews, and prototypes UI animation through three commands - micro (a single element), component (a whole component as one visual unit), transition (moving between states, views, or pages, always with forward and backward motion). Resolves vague requests such as "make it feel premium", "an onboarding intro when the app starts" or "that bouncy thing when it opens", finds animation opportunities across a page or project when the user does not know what to animate, proposes creative options as ASCII or HTML prototypes before touching production code, and reviews its own animation against a craft bar. Use whenever the user mentions animation, motion, entrances, exits, intros, onboarding animation, transitions, micro-interactions, easing, springs, scroll reveals, page or route transitions, hover or press feedback, or wants an interface to feel more alive or polished, even if they never say "animate".
compatibility: Works with any agent that can read files and ask the user questions. Optional scripts need Python 3.9+ using only the standard library; the match-existing scripts additionally need ffmpeg, opencv-python, numpy and scipy.
metadata:
  version: "0.2.0"
  commands: "micro component transition"
---

# Life

**Sub-skill of the [`animation`](../SKILL.md) meta-skill** — reached as `/animation life <command> <target>`. This file owns all UI-motion functionality; `animation/` itself owns nothing but the routing.

Life turns "make this move well" into deliberate decisions: what is animated, whether it should animate at all, how its parts relate, and only then which technique and timing. It prefers creative animation where the gate allows, shows options as prototypes before building, and reviews its own work.

This file is the one router: it is the **only** place that maps requests to files. Open a file only when a row here sends you to it; references carry no routing tables of their own.

## In scope

- Designing and implementing UI animation: micro-interactions, component animation, transitions between states, views and pages.
- Entrances and exits, first-run and onboarding intros, hover and press feedback, state and number swaps, scroll-linked motion, gestures and springs, SVG and clip-path motion.
- Relating animations to each other (instant, domino, linked) and designing both directions of every pair.
- Finding where an app should animate and where it should not.
- Prototyping creative options (ASCII by default, live HTML when needed) before implementing.
- Reviewing and debugging existing animation; matching a recorded animation.

## Out of scope

- Layout, styling or logic bugs that are not animation (fix them normally).
- Making video, GIFs, Lottie files or marketing motion graphics; embedding or playing existing ones.
- 3D scenes, games and WebGL engines beyond UI-level motion.
- Redesigning the interface, copywriting, brand or palette work.
- Sound design beyond the optional interface-sound guidance.

## Commands

| Command | Scope | Unit |
|---|---|---|
| `life micro <target>` | Micro | One element or a small visual unit |
| `life component <target>` | Component | A whole component as one visual unit |
| `life transition <target>` | Transition | The move from one state, view or page to another, forward and back |

The target is a file, component, page or route, directory, the whole project, or a recording. Read the command from whatever the user typed (slash command, pasted line or plain language). No command: infer the scope and say which you chose. No target: ask. Command and target disagree: list candidate elements or suggest the fitting command. Mixed scopes: do the command's scope and list the rest as follow-ups.

## Interpret the request

1. Every run reads two mandatory files whatever the job: [classification.md](references/classification.md) (phase 1) and [gate.md](references/gate.md) (phase 2). Unsure what a phase requires or where to stop? [run-procedure.md](references/run-procedure.md) is the sole home of the phase detail.
2. Decide the **scope** (which command) from what changes: one element, a whole unit, or a change between states.
3. Name the **job** from the user's words using the table below. If the wording is vague (a feeling, a loose description), read intent-resolution and vocabulary first to translate it into precise terms, restate it in one line, then continue.
4. Read the job's files from the table. If the job produces code, finish with the **build tail**, in order: timing-and-tokens → exactly one stacks file → performance-and-accessibility → review-standards. Whenever the target is broad or the user does not know what to animate, discovery runs first, whatever the words said.

| Job | The user says (examples) | Typical command | Job files, in order |
|---|---|---|---|
| Entrance | intro, onboarding, welcome, "on starting", appear, show up, fade in, pop in, hero, page load | component (one screen or surface) or transition (between onboarding steps) | intent-resolution, entrances-and-exits, the playbook, synchronization if ordered |
| Exit | close, dismiss, disappear, remove, leave | component | entrances-and-exits, playbooks-component |
| Feedback or state swap | press, hover, focus, toggle, tick, shake, icon swap, count changes, loading button | micro | playbooks-micro |
| Component lifecycle | modal, popover, menu, drawer, toast, card, accordion, list item | component | playbooks-component, entrances-and-exits |
| Transition | steps, wizard, tabs, back, list to detail, route or page change | transition | playbooks-transition, synchronization; nextjs-transitions for routes |
| Synchronization | cascade, one after another, ripple, connected, highlights related, all together | any | synchronization |
| Physics | bouncy, springy, weighty, momentum, alive | any | intent-resolution, springs |
| Gesture | drag, swipe, flick, reorder, knob | micro or component | gestures, springs |
| Scroll | on scroll, parallax, pinned scene, scroll progress | component or transition | scroll, entrances-and-exits |
| Vector or clip | draws itself, wipe, mask, morph a shape, before and after | micro or component | svg-and-clip-path |
| Feeling word | premium, snappy, playful, calm, cinematic | any | intent-resolution, vocabulary |
| Creative | unique, wow, something different, light, reflection, 3D | any | creative-direction, prototype-ascii, prototype-html if needed, review-standards in spec mode |
| Discovery | what should I animate, whole page or project, "the app feels flat" | any | discovery, gate, then the pick's job row |
| Diagnosis | janky, laggy, flickers, "feels off", review my animations | any | debugging, review-standards, performance-and-accessibility |
| Match | "like this recording or GIF", attached media | any | match-existing, then the matching job's files |
| Naming | "what is that effect called", "that thing where..." | any | vocabulary, intent-resolution |
| Sound | sound, click sound | micro | interface-sound |
| Constraints | reduced motion, accessible, performance, 60fps | any | performance-and-accessibility |

Worked example: "I want an onboarding animation on starting." The job is a first-run **entrance** at the rare tier. One screen appearing is `component`; the move between onboarding steps is `transition`. Read intent-resolution (confirms the job), entrances-and-exits (intro rules: play once, skippable, staged beats), then the playbook, then the build tail.

## The run at a glance

Detail for every phase, including what to decide and where to stop, is in [run-procedure.md](references/run-procedure.md).

```text
0 Understand   parse command and target, translate vague wording
1 Survey       recon, discovery if broad, classify (scope, interaction, sync, direction)
2 Gate         animate, reduce or none, plus a tier
3 Style        ask once: creative or traditional
4 Options      creative only: validate spec, build prototype, user picks
5 Build        every state of every pair, project tokens, safe properties
6 Review       audit script, standards review, fix loop, verdict
7 Report       output contract below
```

Rules that never bend: classify before choosing a technique; the gate comes before creativity; no plain fade, slide or scale unless the user chose traditional; no production code before an option is picked; every enter has an exit and every forward has a reverse; the review runs before the report. Stop for the user only at: a divergent-reading confirmation, the discovery pick, the style question, the option pick, and the ASCII-or-HTML question.

## Directory map

Paths below are relative to this file. Each row says when to open the file and when not to; the job table above says which requests send you there.

### references/: process and diagnosis

| File | Read when | Skip when |
|---|---|---|
| [run-procedure.md](references/run-procedure.md) | starting any run, or whenever you are unsure what a phase requires or where to stop for the user | you are mid-run, know the phase, and only need a value (go to the specific reference instead) |
| [classification.md](references/classification.md) | phase 1 of every run, before choosing any technique, or when unsure whether something is scope, interaction, synchronization, technique or timing | the classification line is already written and unchanged |
| [gate.md](references/gate.md) | phase 2 of every run, before any creative work, and whenever animation is requested on something frequent or keyboard-driven | never skip during a run; skip only for pure vocabulary questions or diagnosis with no build |
| [intent-resolution.md](references/intent-resolution.md) | the request has a feeling (premium, snappy), a loose description, a job word (intro, dismiss, press), or no command | the user already named exact terms and a command |
| [vocabulary.md](references/vocabulary.md) | you must name an effect, or turn a description ('slides off', 'draws itself') into a precise term | the terms are already unambiguous |
| [discovery.md](references/discovery.md) | the target is a directory, a page with many parts, a route tree or the whole project, or the user says 'what should I animate?' or 'the app feels flat' | a single known element or component is targeted |
| [match-existing.md](references/match-existing.md) | the user supplies a recording, GIF, screenshots or says 'like this one' | there is no reference media |
| [debugging.md](references/debugging.md) | existing animation feels off, janky, flickers, jumps, stutters, restarts or goes the wrong way | you are designing new animation with nothing existing to diagnose |
| [review-standards.md](references/review-standards.md) | phase 6 of every build, reviewing a spec before showing it, or reviewing existing animation | you are only answering a vocabulary or naming question |

### references/: design knowledge

| File | Read when | Skip when |
|---|---|---|
| [synchronization.md](references/synchronization.md) | two or more elements animate together, in order, or react to each other (cascade, ripple, hover affecting neighbors, connected nodes) | a single element animates alone |
| [entrances-and-exits.md](references/entrances-and-exits.md) | something appears or leaves: first-run or onboarding intros, hero, page load, sections, lists, dialogs opening and closing, dismissal, removal; words like intro, appear, show up, fade in, pop in, close, dismiss | the change is between two states that both stay (use the transition playbook) or it is pure press, hover or focus feedback (use the micro playbook) |
| [principles.md](references/principles.md) | a judgment call the playbooks do not settle, or when you need to explain why a choice is right | a recipe already fixes the decision |
| [timing-and-tokens.md](references/timing-and-tokens.md) | you are about to write any duration, easing, stagger, scale or blur value, or the project has no tokens — **the single owner of every value range**; other files link here instead of re-listing numbers | you are only naming, classifying or discovering, not choosing values |
| [performance-and-accessibility.md](references/performance-and-accessibility.md) | building (every run): choosing properties, reduced motion, hover on touch, loops, focus — owner of property tiers and input-device rules | you are only classifying, naming or running discovery |
| [springs.md](references/springs.md) | physics, bounce, momentum, interruption, gestures, 'feels alive', layout animation | plain fade or ease motion with no physics |
| [gestures.md](references/gestures.md) | drag, swipe, flick, pull, reorder, knob, detents, swipe to dismiss | nothing is directly manipulated |
| [scroll.md](references/scroll.md) | motion tied to scrolling: reveal on scroll, parallax, progress, pinned scenes | the motion is not scroll-linked |
| [svg-and-clip-path.md](references/svg-and-clip-path.md) | line drawing, path morphs, clip or mask reveals, before and after sliders, hold-to-fill, animated SVG icons | elements animate with plain transform and opacity |
| [interface-sound.md](references/interface-sound.md) | the user asks for sound, or the product already plays interface audio | always, unless one of those is true; never add sound unprompted |

### references/: playbooks (one per command)

| File | Read when | Skip when |
|---|---|---|
| [playbooks-micro.md](references/playbooks-micro.md) | the command is micro: a button, icon, badge, toggle, number, text swap, hover, press, focus, loading indicator, success or error feedback | the command is component or transition |
| [playbooks-component.md](references/playbooks-component.md) | the command is component: dialog, popover, dropdown, drawer, toast, card, menu, accordion, list item, container morph | the command is micro or transition |
| [playbooks-transition.md](references/playbooks-transition.md) | the command is transition: steps, wizard, tabs, list to detail, route or page change, shared element, state graph | the command is micro or component |

### references/: creative options and prototypes

| File | Read when | Skip when |
|---|---|---|
| [creative-direction.md](references/creative-direction.md) | the user chose creative style, or asks for something unique, innovative or 'not the usual fade' — owner of the master idea-lanes table | the user chose traditional style or the gate said none |
| [prototype-ascii.md](references/prototype-ascii.md) | phase 4: writing the prototype spec or building the options file | traditional style, or no options are being shown |
| [prototype-html.md](references/prototype-html.md) | an option depends on light, reflection, depth, 3D, blur, continuous curves or pointer response, or the user asks for a live prototype — owner of the HTML-escalation criteria | every option reads clearly in ASCII |

### references/stacks/: implementation notes per stack (read exactly one that matches the project)

| File | Read when | Skip when |
|---|---|---|
| [stacks/react-motion.md](references/stacks/react-motion.md) | implementing in a React project that uses Motion or framer-motion | the project is not React or has no animation library (use css-native.md) |
| [stacks/css-native.md](references/stacks/css-native.md) | plain CSS, Web Animations, view transitions, scroll-driven CSS, Tailwind, or Vue or Svelte without an animation library | React with Motion already covers the need |
| [stacks/nextjs-transitions.md](references/stacks/nextjs-transitions.md) | Next.js App Router route or page transitions, especially with exit animation | other frameworks, or in-page transitions |
| [stacks/react-native.md](references/stacks/react-native.md) | implementing in React Native or Expo | the target is web |

### scripts/: run, never read

| Script | Run when | Do not run when |
|---|---|---|
| `scripts/find_candidates.py <dir>` | Discovery of a broad target, to list animation seams and existing animation | A single known target |
| `scripts/validate_spec.py <spec.json>` | Before building a prototype, always | Traditional style (no prototype) |
| `scripts/build_prototype.py <spec.json>` | After the spec validates | The spec has errors, or no options are shown |
| `scripts/audit_motion.py <changed files>` | Phase 6 of every build, on the files you changed | Before any code exists; do not scan the whole repo unless asked |
| `scripts/match/*.py` | A recording is supplied (needs ffmpeg and Python packages) | No reference media |

Each script prints usage with `--help`. If scripts cannot run, use the manual fallback described in the matching reference.

### assets/ and examples/

| Path | Open when | Otherwise |
|---|---|---|
| `assets/tokens.json` | You need the machine-readable tokens and the project has none | Use timing-and-tokens instead |
| `assets/prototype-template.html` | Never during a run; the build script fills it | Do not read or edit |
| `examples/*.md`, `examples/*.json` | You are unsure what a finished run, discovery report or prototype spec looks like (one example only) | Skip; the references are sufficient |

## Output contract

```text
Classification   scope=<> · interaction=<> · sync=<> · direction=<> · technique=<> · timing=<>
Decision         animate | reduce | none, tier=<routine|rare|showcase>, style=<creative|traditional>
Built            files changed, one line each
Values           properties, durations, easing, stagger, origin, reverse behavior
Review           audit script result, verdict (Approve or Block with reasons)
Needs a human    what only feel or a device can confirm, and how to check it
Follow-ups       other scopes or opportunities noticed but not done
```
