# Dead-Control Audit (opt-in command)

> **What this is:** the full procedure for the second entry point of the `design-mockup` skill — taking an **existing** HTML file and wiring the controls that look clickable but do nothing. It is the sibling of the build workflow in [`../SKILL.md`](../SKILL.md), not a step inside it.
> **Read alongside:** [`feedback-heuristics.md`](feedback-heuristics.md) owns the affordance→component mapping and the dropdown/toast code patterns; [`query-param-states.md`](query-param-states.md) owns the param contract and bootstrap; [`viewport-frames.md`](viewport-frames.md) owns the viewport categories. This file owns *the order of operations* and links out for all three.

**Run this only when asked.** Trigger phrases: "this does nothing when clicked", "the kebab doesn't do anything", "add feedback to the interactive elements", "make this feel real", "audit this for dead clicks", "wire up X". Never run it on a mockup you just built — a fresh build already wires every control per the main workflow, so there is nothing to audit.

The shape of the procedure: detect platform → inventory affordances → classify expected feedback → wire it matching the file's own conventions → report.

## 1 — Detect the platform this file targets

Work out what platform idiom the file already speaks, using the same desktop/tablet/mobile categories as [`viewport-frames.md`](viewport-frames.md) — read that file for the definitions; the short version of the signals: a narrow (~360–430px) frameless container, a sticky bottom tab bar, `safe-area-inset` padding, or touch-sized (44px+) targets mean mobile; a wide, pointer-oriented layout with no bottom nav means desktop.

This is not a formality: which *component* correctly answers a given affordance is a function of platform, not just icon shape — and that principle, plus the full mapping, is owned by [`feedback-heuristics.md`](feedback-heuristics.md). Decide the platform before classifying anything, or you will pick a component that is textbook-correct and locally wrong.

If the file mixes signals or it's genuinely unclear, a quick check with the user beats guessing and re-wiring everything.

## 2 — Inventory every affordance

Walk the file and list every element that visually reads as interactive: `<button>`s, `<a>`s, anything with `cursor: pointer`, an `onclick`/`role="button"`, or icon-only controls (kebab/ellipsis/three-dot, chevron/caret, bell, avatar "+" badge, heart/bookmark/share icons) — including ones with no visible label.

For each, check whether it already does something real: a working `href` to another file or section, an existing `onclick` that changes visible state, or an existing query-param-driven state per the convention in [`query-param-states.md`](query-param-states.md). If it already reacts, it is not a candidate. If it's decorative and no reasonable user would expect a reaction (a static logo mark, a divider, a label-only badge), it is not a candidate either.

Everything left over — an icon button with no handler, an `<a>`/`<button>` with an empty or `#`/`javascript:void(0)` target, a row with a chevron that expands nothing — is a candidate.

## 3 — Classify the expected feedback per candidate

Match each candidate's visual affordance to the feedback a user's mental model expects, using the mapping table in [`feedback-heuristics.md`](feedback-heuristics.md), read with the platform from step 1 in mind. Do not default to one component type "because it's the one already documented" — reason about what that platform's own UI would actually show.

Two authoring rules that are this procedure's job, not the lookup table's:

- **Reuse before inventing.** If the file — or a sibling screen visible in the conversation — already has a working sheet, drawer, dropdown or toast, wire the new fix into *that* component and its open/close functions. Internal consistency with the rest of that file beats a textbook-correct but visually different second overlay system.
- **Write real labels.** For any menu-style feedback (dropdown, context menu, sheet, notification panel), the item labels come from what the element sits on: a kebab on a video card gets "Not interested", "Report", "Save to Watch Later" — never "Option 1 / Option 2".

## 4 — Wire it up, matching the file's existing conventions

Implement each fix with the bootstrap pattern from [`query-param-states.md`](query-param-states.md) — params read on load, applied through the *same* functions clicks use — while respecting what's already in the file rather than converting it:

- If the file uses Tailwind utility classes, continue in Tailwind. If it's hand-rolled CSS (custom properties, BEM-ish names, a `<style>` block), match that style for new markup — do not introduce Tailwind into a non-Tailwind file for this pass, and do not restyle unrelated parts of the file.
- Reuse existing helpers where they fit: if a `toggleLike()` already exists, give `toggleSave()` the same shape rather than inventing a parallel convention.
- Keep the diff surgical. Add the missing markup (menu panel, toast element if none exists) and the missing handler/param wiring; don't restructure, rename or re-theme anything that already worked.
- Every newly-wired piece of state still gets a query param per the naming convention, so the fixed state is reachable and reviewable by URL exactly like a freshly-built mockup — `?dropdown=video-1-menu`, `?toast=saved`.

## 5 — Report what changed

Give a short list, not a wall of text: name the control, name what it now does, name the component you chose, and give the param to preview it.

> Kebab on each video card now opens a context menu (Not interested / Report / Save to Watch Later) — try `?dropdown=video-1-menu`. Share now opens a bottom sheet (this is a mobile file) with Copy link / WhatsApp / Telegram — try `?sheet=share-1`.

This is the deliverable's changelog, not optional flavour text: the user needs to know what was touched, and which component answered each affordance, to review it.
