# The light URL-state contract

The quirk `/prototype` formalized, kept whole at playfile scale: **every meaningful state is reachable,
reproducible and shareable by URL alone.** `settings.html?state=error&theme=dark` shows exactly that, on
first open, on refresh, and in a link pasted to a colleague. What playfile drops is the machinery (central
state helper, spec files, history policies); what it keeps is the contract.

## The rules

1. **Enumerate before you code.** For the screen, list the states a reviewer would want to see: content
   states (`?state=empty|loading|error|partial`), positions (`?step=2`), variants (`?plan=paid`,
   `?me=photo|initials|none`), toggles (`?filled=1`, `?theme=dark`). A state with no plausible reason a
   reviewer wants it gets no param — and a state the screen can genuinely show (an error this request can
   actually hit) is not optional.
2. **One param per piece of state, short role names.** `?state=`, `?step=`, `?tab=`, `?modal=`, `?q=` —
   never `?x=`, never one mega-param coordinating everything. Combination is just more params:
   `?shape=cookie&state=error&theme=dark` isolates one cell of a catalog page for capture.
3. **Names ASCII, values any language, `URLSearchParams` only.** Param *names* are code identifiers
   (`state`, not `الحالة`); *values* may be Arabic or anything else — and then they must travel exclusively
   through `URLSearchParams` (`.get()` / `.set()`), which percent-encodes correctly. Hand-concatenating a
   value into a URL string is a defect that breaks on Arabic, spaces and `&`. Verify once with a real
   Arabic value, not just English.
4. **Invalid falls to default, silently.** `?state=banana` renders the screen's default state; no crash, no
   blank, no warning chrome. The reviewer's URL is never wrong, just uninteresting.
5. **Click path = URL path.** A control that changes a URL-forced state writes that URL (`history` via
   `.href` assignment or `pushState` — either is honest at this scale) and renders through the same code a
   cold URL uses. State reached only by clicking, or state that only appears on load, breaks reproducibility
   in opposite directions; one shared `render(params)` makes them identical by construction.
6. **`?theme=light|dark` + remembered identity.** Read the param first; absent it, read the project's
   `localStorage` key; persist on toggle. Theme is the one thing allowed to survive navigation between
   files, because a reviewer flipping through screens must not re-flip every page.
7. **`?filled=1` is seeded, never `Math.random()` bare.** Default render is sparse-but-real; `?filled`
   paints full crowded realistic data from a **seed** (bare param = the project's default seed,
   `?filled=17` is a different draw). Unseeded randomness kills the first promise: the link would not
   reproduce.
8. **Reviewer-only params are marked as such** in the README Files table (`?theme=dark` (reviewer-only)
   for a product with no theme switch), so the dossier keeps the URL vocabulary honest about what ships.

## What stays out

Hover position, scroll offset, focus, animation frames — mechanics of the browser, not states of the
design. And anything the screen genuinely cannot show: if this request has no failure mode, there is no
`?state=error` here; faking one teaches the reviewer a lie (the same honesty rule `/prototype` enforces
with gates, kept here as judgment).

## The 30-second acceptance check

Open the screen with each documented param combination from a fresh tab — cold, no clicks: right render.
Refresh: identical. Click to the same state: same render, URL matches. One Arabic value through search or
content: survives copy-paste. That is the whole contract; if a combination fails, fix the screen or fix the
README, but never ship the mismatch.
