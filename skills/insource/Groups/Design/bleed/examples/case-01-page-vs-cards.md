# Case 01 — a showcase page converted from framed to full-bleed

An RTL mockup set for a desktop app: a fixed 64px rail, a 3-zone page header, and several sibling
pages that all share one section grammar. A new page — `showcase.html`, a summary of one entity with
its stats, its charts and the fields the user still has to fill — was generated in the same folder.
It rendered as "a document inside an app".

The user's words, which are the reason this skill exists:

> *"dont make it like main-section inside a page, make it the whole page, not sections inside it,
> make it take full page dimensions, like the other files"*

## Diagnosis

The siblings were read first. Their grammar: `section-head` (sticky, title + kicker, bottom hairline)
then `section-block` (uniform padding, bottom hairline), both direct children of one scroll canvas,
with no max-width anywhere at page level.

`showcase.html` was in a different register — both at once:

```css
.sheet  { max-width: 1120px; margin: 0 auto; }
.dossier{ display: grid; grid-template-columns: 312px 1fr;
          background: var(--surface); border: 1px solid var(--line);
          border-radius: 20px; overflow: hidden; }
```
```html
<div class="flex-1 overflow-y-auto"><div class="min-h-full">
  <div class="sheet">
    <section class="dossier">          <!-- one outer card -->
      <div class="portrait">…</div>    <!-- left column -->
      <div class="side">…</div>        <!-- right column, holding everything else -->
    </section>
  </div>
</div></div>
```

Outer chrome **and** an inner capped card: the nested-frame smell. Target register: `page`.

## Moves

1. Deleted `.sheet` and `.dossier`; promoted the content to direct children of the canvas.
2. Replaced the card's two column headings with the set's own `section-head` + `section-block`.
3. Split the crowded right column into **three** sections — typed fields, read history, gated data.
   The card had been hiding that three different subjects shared one container.
4. Moved save/refresh into the set's standard footer row.
5. Touched no chart, pill, tooltip, script or state parameter.

## Before → after

| | before | after (measured) |
|---|---|---|
| page-level cap | `max-width: 1120px` on `.sheet` | none |
| content width at a 1440 viewport | ~1072px (derived: 1120 − 48 padding) | **1376px** = 1440 − 64 rail |
| dead margin per side | ~152px | 0 |
| sections / heads / sticky heads | 1 card / 2 column titles / 0 | **5 / 4 / 4** |
| document height | 1349px | 1488px (taller: three sections replaced one compressed column) |
| horizontal overflow at 1440 and 900 | none | none |
| console errors | none | none |

Height going **up** was correct and is worth flagging: full-bleed is not a compression tool. When the
user also said *"it is very long"*, that was a density complaint, not a register one — see
`references/vocabulary.md`, near-miss table.

## The false positive that changed the probe

After the pass, the probe reported `cappedWrappers: 1` — a supposed failure. The element was:

```css
.skills { max-width: 720px; }   /* wraps a row of chips so they don't run 1300px wide */
```

An inner component cap, entirely legitimate, and it wraps no sections. The assertion was rewritten to
scope on ancestry rather than existence — *"no capped element that is an ancestor of a
`section-block`"* — which is what `references/verification.md` now says. A probe that flags correct
code is worse than no probe: it trains the next pass to delete something that was working.

## Also found by looking, not measuring

- A row of stat boxes rendered value and caption on one line, colliding a fraction with its unit.
  Inline `<span>`; fixed with `display: block`. No measurement catches this.
- A class named `ring` collided with a utility framework that already owns `.ring`, painting a box
  around a circular element. Renamed to `arc`.

Both were visible in one screenshot and invisible to every assertion. Measure first, then look once.
