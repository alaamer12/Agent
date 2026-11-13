# State surfaces — empty, loading, error, and the rest are designed screens

Loaded before writing any page's non-happy path, and whenever about to render "nothing" where
the product would show something.

## The rule

**Every state a screen can be in is a surface with a job, not an absence of markup.** A page
whose empty case is a bare div with no content has not rendered the state — it has failed to.
The empty state *is* the product for a new user; the zero-result state is the whole experience
for someone with a typo in their filter; the error state is the difference between a recoverable
glitch and an abandoned session.

The failure this kills is measured: generated prototypes ship fully-populated desktop screens
and leave empty/error/loading as white space, or (worse) as a `No data` string — while the
same screen's happy path got real design attention.

## Anatomy — every non-happy state carries recognition, path, and reassurance

| state | recognition (what happened / what's missing) | path (the one action that fixes it) | tone |
|---|---|---|---|
| **Empty** (first use, nothing exists yet) | headline naming what will live here + one sentence of value | primary CTA that creates the first item — the *same* CTA the populated view uses, not a "Go back" | inviting |
| **Zero results** (filters excluded everything) | echo the active filter back ("nothing matches «Q4 · archived»") | clear-filters / edit-search action; never only "Go back" | helpful |
| **Loading** | skeleton shaped like the real content (rows where rows will be, chart silhouette where the chart will be) — never a spinner floating in a blank page | none; it must resolve | calm |
| **Error** | what failed in product language, not the exception | retry in place; a route onward if retry can't work | accountable |
| **Forbidden / partial** | what they can't see or what arrived damaged, concretely | request-access / reload-partial action | honest |

Icons/illustration: use the project's icon system (Lucide or the `glyphs.js` fallback) inside a
soft token-colored disc — a real visual anchor. No emoji, no "sad-looking" clipart, no ASCII
shrubbery. The anchor is decoration; the headline + CTA are the substance.

## The builders make the failure structural

`ui.js` owns these as builders with required arguments — you cannot produce a bare empty div
because the builder's signature demands the parts:

```js
emptyState({ icon, title, body, cta: { label, href|go } })     // cta required; omit only for a read-only surface, said out loud
loadingState({ rows = 5, kind = 'table' })                      // skeleton: table | cards | chart | text
errorState({ title, body, retry })                              // retry required
stateGate(state, { ok, empty, zero, loading, error })           // every branch designed or explicitly defaulted
```

`stateGate` is the enforcement point: a page whose gate omits a branch it can reach gets the
builder's default — a real designed surface with the app's tokens — not a blank.

## Sparse is not empty

The skill's `?filled` default is **sparse**: a nearly-empty *product* rendered honestly — a
handful of real, plausible rows, one or two gaps. That is populated content, not a blank screen.
The empty state above is a different case: a collection that genuinely has zero items. A page
that shows "no rows" when its realistic sparse state would show 3–6 rows has confused the two —
verify against what the product would actually contain on day one.

## Content fidelity, everywhere (the same rule for the happy path)

Every visible region of every state renders full, plausible product content at first paint:
real domain vocabulary, named entities, realistic amounts/dates/counts, complete sentences in
labels and helper text. "TODO", "Item 1", "Lorem ipsum", an untranslated key, or an empty
table shell while its sibling page has 8 rows are all the same defect. The test for each
screenshot: **could a stranger be told this app exists and believe it?** If the answer is a
polite no, the surface is unfinished — finish the content before declaring the page done.

## Verification

The render-verify pass includes the states: screenshot the empty, zero-result, error, and
narrowest-width case, and look at each. A state you never rendered is a state you never
designed — `?filled=0&status=empty` (or the page's equivalent URL) must produce the designed
surface, and it must hold at mobile width where CTAs and action rows break first.