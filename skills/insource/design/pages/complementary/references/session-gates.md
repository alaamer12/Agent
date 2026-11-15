# Session gates

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** the person is mid-intention and the app can no longer act for them — session
expired, re-auth required for a sensitive step, verification pending between stages.

**The family's whole job is the word *resume*.** Every other conditional page ends a moment;
session gates exist to *return* to one. A gate that loses the in-flight draft, the checkout
contents, or the deep-link destination is worse than no gate — it converts a security
mechanism into data loss the person attributes to the product, not to their laptop being open
overnight.

## Required behavior

1. **Preserve the intention** — where they were headed (route + safe query state), what they
   had typed (drafts that are allowed to persist, by policy), what was mid-submit (never
   silently re-submitted after login — that is `transaction-failure`'s pending cousin).
2. **The gate itself is not a page of this family** — login/verify screens are main pages
   (`boundary-test.md`); what is complementary here is the *interstitial that explains why
   they are looking at login right now*: "pick back up — sign in again" beats a naked login
   form dropped mid-flow with no context.
3. **Honest timer** — sessions that end on a schedule should warn before they act (a
   keep-alive offer on real active work), and never log out mid-form while silently
   discarding. If the product cannot warn, it should not pretend the gate is frictionless.
4. **Exits** — after auth, straight to the preserved intention. Fallback when preservation
   was impossible (token links, exports, state the rules forbid caching): say plainly that
   the step restarts, and why.
5. **Reachability states** — cold deep-link with dead session → gate → resume at the
   deep link, not at dashboard; multi-tab: one tab refreshed should not sign the others'
   work out into oblivion without recovery; logged-out revisit of a bookmarked gate page →
   it is just login, correctly.

## Anti-patterns

The redirect-to-login-without-return-url classic; "your session expired, please log in" as a
toast on a page that then *also* shows stale data as if live; gating the verification step
where verification's own destination page belongs to `token-handoff` — the seam is decided in
the map, once.