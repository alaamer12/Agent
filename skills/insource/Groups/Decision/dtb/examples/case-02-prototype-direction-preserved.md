# Case 02 — the prototype's direction was right; its internals were not

> Worked example, invented for teaching. The lesson is the split between what the drawing asserts and what it
> merely happens to be doing.

**The situation.** The user hands over a three-screen prototype — a dashboard, a detail view, a settings sheet —
built by hand as a single HTML file with inline styles and hard-coded arrays, and says: *"this is the feel I
want, build it properly."* They had already said twice that they liked the density and the color direction.

## What the prototype asserted, and what it did not

| In the file | Reading | Owned by |
|---|---|---|
| three screens, that order, that hierarchy | the journey and information density | user — not to change |
| a sort dropdown with no handler, a filter chip that does nothing | **required behavior**, drawn as a wish | user asked, agent implements |
| inline styles, one 900-line file, hard-coded arrays | an artifact of prototyping, not a decision | agent — rebuild freely |
| no loading, error, or no-results screen | never drawn by prototypes | agent — invent inside the approved style |
| data shape: an array of objects with `id`, `title`, `updatedAt` | the model the user believes in | agent may extend, must not rename meaning |

The first temptation, and the common failure: *"this design is dated, I'd use a card grid with a sidebar."*
The user praised this direction twice. Preferring something else is not evidence. The second temptation, the
opposite failure: honoring the drawing so literally that the 900-line file and the inline styles get
transcribed into the product "to match the prototype."

## What was actually wrong underneath

Found by reading, not guessing:

1. The two screens each re-implement their own fetch and their own date formatting; the formats disagree
   (`10/27` vs `27 Oct`), which reads as a bug in the product, not in the code.
2. State lives in module-level variables, so navigating away and back loses the active filter — the user sees
   this as a flicker of wrongness, not as a state bug.
3. The hard-coded arrays were the only data path: there is no request layer, so "wire it to the real API" had
   nowhere to land.
4. Nothing handles a slow or failed load; on the mobile profile the screen is blank for ~1.4 s and then jumps.
5. The filter chips are keyboard-invisible and their click target is 14 px — a real user on a phone cannot hit
   them, and a keyboard user cannot reach them at all.
6. A "delete" action has no confirmation and no undo, and its copy is apologetic in a voice the rest of the
   product does not use.

Every one of those is **implementation-territory** — invisible to the design's intent, visible in use.

## What was decided, and how the surface stayed identical

```text
kept exactly   layout, spacing scale, type sizes, color tokens, copy that already existed, screen order,
               the density the user praised
changed freely how state is owned (one store, survives navigation); one fetch layer + one formatter for both
               screens; a skeleton that matches the final layout so nothing jumps; error and no-results
               states written in the product's existing voice; confirmation + undo on the destructive action;
               chips rebuilt as real buttons with visible focus and a 44 px target
```

The chips are the instructive one: making them reachable and focusable changed **nothing a user could see as
design** and everything about whether they could be used. Same shape, same label, same position.

```tsx
// one seam: the screens talk to a store, the store talks to a fetch layer.
// Nothing above this line knows whether data is real, cached, or a prototype fixture.
const useDash = () => useStore(s => ({ rows: s.rows, filters: s.filters, status: s.status }));
```

## The two things proposed rather than done

- The detail screen's title wraps to three lines for real data (the prototype's short fixture titles hid it).
  A one-line truncation would change the visual rhythm, so it was **proposed**, not applied; the fix shipped
  was a `min-height` reservation that keeps the rhythm either way.
- The settings sheet has no save-error surface at all. Adding one means inventing visible UI the user did not
  draw — the smallest possible line in the existing voice, flagged in the report as new visible UI rather than
  slipped in.

## The report

> Built behind your design: same three screens, density and colors untouched. Fixed underneath — one data and
> formatting path (the two screens disagreed on dates), filters now survive navigation, real request layer,
> loading/error/no-results states added in your voice, destructive action gets confirm + undo, filter chips are
> now keyboard-reachable with a 44 px target. Two things I did **not** change: title truncation on the detail
> screen, and one line of save-error UI — both need your word choice, proposed in `docs/` notes.

The user's vision left intact; the execution left stronger. That is the whole job.
