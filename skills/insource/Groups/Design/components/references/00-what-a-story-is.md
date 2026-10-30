# What a story is

A **story** is one component rendered in one state, in isolation, with real-looking props. A **gallery** is
the set of all stories for all components — the coverage matrix. That's the whole idea, and the distinction
from the other two pages in the project matters:

| Page | Answers | Fails to answer |
|---|---|---|
| `pages/<screen>.html` (prototype) | "what does this flow feel like?" | anything about a state the screen isn't currently in |
| `index.pages.html` (prototype gallery) | "which screens exist, and what state can each be driven into?" | whether a component's disabled look is consistent across screens |
| `index.stories.html` (**this skill**) | "what does every component do in every state?" | how the states feel inside a real flow |

The third question is the one that catches bugs, and a screen review structurally cannot ask it: a screen shows
one state per component per moment, so the empty, rejected, overflowing, and unknown variants are simply never
on screen during review.

## What a story is not

- **Not documentation.** A card with a paragraph explaining the component and no live render is a doc, and the
  gallery's value is that everything on it is *the real thing, rendered*.
- **Not a marketing showcase.** The disabled and error states are the point; a gallery that only shows happy
  variants is the same blind spot as the screenshot, with more whitespace.
- **Not a second page set.** If a story needs a whole screen's worth of context to make sense, it is a page.
- **Not a spec sheet.** The registry describes what renders; the *why* belongs in the project's design docs.

## The card contract

Each card is:

```text
[state badge]                                     [permalink]
──────────────────────────────────────────────────────────
        the component, rendered by the renderer
──────────────────────────────────────────────────────────
optional note: what triggers this state in the product
```

Three properties make the gallery trustworthy:

1. **One renderer per component**, shared with the pages where the project chose that mode
   ([`06`](06-integration-with-prototype.md)). A card must be pixel-identical to the component as used for real.
2. **The permalink is real.** Every card links to `?id=<component>&show-only=<state>`, so a reviewer can paste
   one state into a bug report. If a card cannot be reached by URL, it is decoration.
3. **The state is real.** `disabled` sets `disabled` and the matching ARIA state; `invalid` renders the error
   message the product would produce; `loading` shows the shimmer only in the region that actually loads. A
   grey filter over a healthy component is a lie with good taste ([`07`](07-authoring-a-component.md)).

## Why isolation changes decisions

Reviewed alone, a component's state set becomes *cheap* to inspect: five toggles side by side make an
inconsistent disabled treatment obvious in a way that no page walkthrough does. Two consequences worth
internalizing:

- **Inconsistency is the finding.** The gallery's job is to make differences visible; a gallery where every
  card looks the same has either no states or a component that hides them.
- **Copy is part of the state.** A truncated Arabic label, an error message that overflows its slot, a
  90-character name — these are state behaviors, not content problems, and the props must include the ugly
  cases deliberately.

## When not to build one

A single component with two states, in a one-page prototype, does not need a gallery — put the states on the
page and drive them with params, which `prototype` already does. The gallery earns its files when there are
**several components with several states each**, or when the component set is going to be reviewed by someone
who is not the person who built it.
