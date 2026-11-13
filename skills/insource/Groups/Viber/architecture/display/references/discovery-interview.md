# Display Architecture — discovery interview

Ask only what the codebase cannot answer (the parent skill's recon rules apply: existing
`Intl` usage, message files, type tokens, and the AGENTS.md voice section are read first).

## A. What the product displays

1. Which surfaces carry **quantities** users act on or compare? (dashboards, stat cards,
   tables, charts, receipts, counters, progress)
2. Per surface, what is the reader's question — "about how many?", "how big exactly?", or
   "what do I owe?" → seeds the L0/L1/L2/L3 assignment.
3. Any **regulatory or financial exactness** requirement that pins surfaces to L0?
   Anything that may never be rounded (totals, balances, IDs)?

## B. Containers

4. Which slots have **fixed or narrow widths** where a long value could strike through?
   (stat cards, table columns, chips, axis ticks, mobile rows) Get real measurements or
   design tokens, not vibes.
5. Which values **animate or update in place** (counters, live totals) — these need
   tabular figures and widest-frame reservation.
6. On overflow, what is acceptable: compact + tooltip? detail route? press-and-hold?
   (pick the fallback ladder per slot class; "ellipsis" alone is not an answer — probe for
   the exact-value escape.)

## C. Locales and languages

7. Which locales does the product actually serve (repo evidence: message files, locale
   flags)? RTL among them?
8. For Arabic: **Western-Arabic or Arabic-Indic numerals** — a product voice decision, get it
   explicitly; calendar: Gregorian or Hijri display anywhere?
9. Where do numbers/units appear **inside RTL sentences** (notifications, generated text)?
   Confirm the isolation mechanism the stack offers (`<bdi>`, `dir="auto"`, formatter flags).
10. Expansion: worst-case locales for each tight slot (Germanic/Finnish long words,
    Arabic-Indic wide digits) — who owns the test strings in QA?

## D. Voice, medium, typeface

11. What voice register does each surface family speak? (cross-check AGENTS.md section 18
    first — do not re-ask what is recorded)
12. What typeface roster does the product actually ship (tokens, @font-face, bundled)?
13. Build the pairing table together: for each surface class, does
    (voice, typeface + figure style, notation level) tell the same story? Present the four
    coherence checks from `display-principles.md` §4 and let the user veto.
14. Confirm the **precedence statement**: accessibility user-choices override pairings;
    budgets recompute against the widest allowed face.

## Hand-off

Conclude by restating the surface-class table (surface → voice → typeface+figures → level →
budget → fallback) in one block and getting confirmation — the template's section 2 becomes
exactly that block. Anything unanswered goes to the doc's Open Decisions, never defaulted
silently.