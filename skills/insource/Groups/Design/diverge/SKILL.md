---
name: diverge
description: 'Previews genuinely different design directions for an existing UI before committing a whole project or batch of pages to one of them. Two commands: /diverge taste [n] builds n complete, genuinely different directions and delivers them side by side in a picker page whose "Use this one" button copies a ready-to-paste prompt; /diverge snippet proves one direction on a single representative file with mockup data, never touching source, in a like/dislike loop. Use when someone wants to see real options before a redesign rollout, asks for variations, directions, tastes, or design options side by side, says "show me a few different takes before we commit", names /diverge taste or /diverge snippet, or wants a fast go/no-go proof of a redesign feel on one file. Directions must differ on structural judgment calls, not paint. Not for applying one decided redesign pass (denoise or any redesign skill does that), and not from-scratch design.'
when_to_use: The person is about to commit a project or many pages to one redesign direction and wants real options first, asks for variations/directions/tastes side by side, or wants a one-file mockup proof before rollout.
argument-hint: "[taste [n]|snippet] <file-or-project>"
---

# Diverge

Don't commit a whole project to one design direction sight-unseen. This skill produces the
options: either **several genuinely different directions at once** for a side-by-side choice
(`taste`), or **one direction proven on a single file** in a fast yes/no loop (`snippet`).
It never rolls anything out itself — once a direction is picked, its judgment-call answers
become the standing defaults for whatever redesign work follows, in this skill's session or
any other.

## Read the right reference before you act

This file is the decision procedure. The command mechanics load on demand.

| when | load |
|---|---|
| the person says `taste` or `snippet` — full mechanics, picker filling, post-pick flow | `references/commands.md` |
| deriving which directions are even plausible for this input | `examples/constraint-derivation.md` |

## The one rule: genuinely different, not N minor variations

This is the part most likely to be faked under time pressure — three passes that only differ
by accent hue are not three directions. Each direction must differ on at least one of the
large judgment calls:

- working-surface light/dark direction
- chrome position (side/top/bottom/floating) and chrome colour (dark-neutral/light-neutral/full-brand-hue) — independent axes
- type/spacing scale (comfortable/large/enormous)
- page-split shape and overall density philosophy
- where the input has forms or dialogs: **how far the interaction layer gets reworked** (containers repainted vs. fields re-grouped and re-sequenced vs. the job moved out of a modal altogether)
- **whether states are designed** (empty/zero-result/error as afterthoughts vs. as surfaces)

Two directions that differ only in paint are one direction twice. A direction that changes
how a task is performed is a different product decision — the most useful thing to see side
by side before committing a rollout.

## How to arrive at n directions — derive, combine, spread

Listing the axes is not the same as picking real values on them. Three steps, in order:

1. **Derive the live options from this input's own constraints.** For each axis, ask what
   this specific input's content and structure rule in or out — not what is abstractly
   possible. A dozen long, non-iconic nav labels rules out icon-first chrome; 4–5 short,
   visually distinct items make it live. An axis with no plausible alternative for this
   input must not be the thing that varies between two directions.
   `examples/constraint-derivation.md` works this through on a real input.
2. **Choose n internally coherent combinations.** A direction is a *design*, not a checklist
   of independently-chosen values — the combination must hang together as something a real
   product could plausibly ship. Where two axes' options interact awkwardly, let that rule
   out combinations rather than presenting all of them as equally coherent.
3. **Push for real spread.** Don't pick the n combinations closest to the input's current
   choices — that reproduces the under-delivery this skill exists to avoid. At least one
   direction should represent a genuinely different overall feel, provided step 1 didn't
   rule it out. Not the n most extreme combinations for shock value either; that fails
   step 2 as often as it passes it.

State each direction's defining choices in one line (its "tag") before building it, so the
person can tell at a glance what is actually different about each card.

**Spread is bounded by the constraints — it does not override them.** Step 3 pushes across
the axes step 1 found *open*. The dwell-time rule is a constraint on which axes are open at
all, not one more axis to vary for the sake of variety: for a product whose high-dwell-time
working surface is read for long stretches — a data-dense admin/ops console, a form-heavy
business tool, an analytics table — "dark working surface" is usually **not** a live option,
and building it anyway to reach a count of n manufactures a direction that trades away the
light-surface rationale. Drop it and substitute a different *open* axis (chrome position,
chrome colour, scale, density philosophy, page-split shape). Chrome colour and working-surface
light/dark are independent: a full-brand-hue rail over a light working surface is a real,
unconstrained, genuinely-different direction even when the surface must stay light.

## Depth — stated, not assumed

Each direction is built at the depth the person asks for: in-place polish, restructuring,
or a full re-theme and re-structure. If they haven't said, ask — one line, don't
over-explain. A direction preview is **not a lower-fidelity sketch**: it is the real work at
that depth, done n times with different judgment-call answers. If the person names a
redesign skill's intensity vocabulary (e.g. lite/medium/ultra), honor it as the depth of
each build; this skill does not own that vocabulary and works without it.

## Verify by rendering — every direction, before delivery

Reading the markup you wrote is not verification. **No direction is shown until it has been
rendered and looked at** — an unrendered direction card is an unverified claim. Render each
built direction in a browser, look at the screenshot, name what is wrong in your own words
(clipped text, wrapped rows, a sticky bar over content), fix, re-render. Check the states
that are not the populated view — empty, zero-result, failing — and the narrowest width the
product supports. After three loops without converging on a direction, report what remains
unmet rather than quietly showing it.

## Commands

Both are triggered explicitly — `/diverge taste [n]` and `/diverge snippet` — and neither is
the default. Without one of these keywords, a multi-file input is not this skill's job:
hand it to the redesign skill the person is actually using.

- **`taste [n]`** — build n directions (default **3**), each a complete self-contained file
  or small file set, and deliver them through `assets/taste-picker-template.html`: one card
  per direction with its name, tag, and the built file as the iframe source. The picker is
  what the person interacts with; the direction files are what it loads.
- **`snippet`** — one representative file, rebuilt as a standalone mockup with representative
  **mockup data**, never a modification of the actual source, in any source language. Then
  stop and ask whether it lands; iterate on the same file until it does or the person says
  move on.

Full mechanics — sample-file selection, the picker's copy-prompt contract, the like/dislike
loop, and what happens after a pick — in `references/commands.md`.

## After the pick

The picked direction's judgment-call answers become the **standing defaults** for the rest
of the project: proceed file-by-file without re-litigating the same calls, unless the person
says a specific later page should diverge. A pick can arrive as a chat reply or as a pasted
prompt in a brand-new session — the copied prompt restates the direction's actual choices,
so treat those as sufficient to proceed without asking the person to re-explain.

## Resources

`references/commands.md` — the full mechanics of both commands, loaded when either is named.
`examples/constraint-derivation.md` — the derive-from-constraints method worked through on a
real input, with options ruled in and out and why. `assets/taste-picker-template.html` — the
picker shell, regenerated per `taste` run; it is a shell, not fixed content.