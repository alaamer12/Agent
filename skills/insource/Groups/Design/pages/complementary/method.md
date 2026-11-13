# complementary — conditional screens (`/pages complementary`)

Owns `PAGES.md` §6 rows (registered conditional screens with their anatomy), §7 state-vs-page
calls, exclusions with kind=complementary, and the boundary test that decides what this mode
may touch at all. Family content lives in `references/`; this file is the workflow.

**The family:** screens that appear only when a triggering condition fires and whose absence
never breaks normal operation — onboarding, transaction outcomes, HTTP errors, session gates,
maintenance/outage, access gates, token handoffs, and relay redirects. Not: prerequisites
("must have an account" describes every authenticated main page), and not states inside
screens (empty results and validation errors belong to their pages, §7).

## Laws specific to this mode

| Law | Meaning |
|---|---|
| **Server truth owns the condition** | the success page verifies with the backend; failure reports current state; a gate re-checks before showing. A URL param is a request to verify, never the answer |
| **No dead ends** | every page declares exits: a primary way forward + a fallback for when the primary is impossible. "Go back" is not a design |
| **Owe the retry to the contract** | retry affordances obey the project's ownership contracts (`automatic_retry`/`manual_retry` from the `contract` skill when they exist); this mode renders what the policy permits and invents none |
| **Never invent the condition** | no outage page without an operator switch, no success celebration for a silently-completing flow. Candidates are confirmed against real flows; skipping is a recorded, correct answer |
| **Blankness is a security feature** | relay pages validate state, forward only to allowlisted targets, render zero content, log proven-dropped — see `references/relay-redirect.md` |

## Workflow

1. **Boundary first** — every candidate passes `references/boundary-test.md`'s three
   questions. Failures get named and handed: main (§4), secondary (§5), or states (§7).
2. **Inventory candidates** — walk `references/catalog.md` against the project's real
   evidence: routes, webhook/return wiring, auth middleware, feature flags, entitlement
   checks, mail templates (which tokens actually exist). Present the set; ask which to design.
3. **Fill the anatomy** (`references/anatomy.md`) before design: trigger as a predicate,
   condition source, the wayward reachability states (cold deep-link, bookmarked replay,
   logged-out arrival), primary + fallback exits, continuation ownership, announcement.
4. **Build per the family reference** — each of the nine `references/<family>.md` files owns
   the per-class copy laws and anti-patterns.
5. **Register in PAGES.md §6** — one row per screen per `../references/output-contract.md`:
   family, trigger, condition source,
   exits, status. Exclusions (e.g. a cancel page the failure screen already owns) go to §9
   with kind=complementary; worked shape in `examples/after-payment/anatomy-sheets.md`.
6. **`audit <routes-dir>`** — sweep real routes for conditional pages that violate a law:
   URL-guessed success, dead-end failure, unregistered §6 absence, relay pages rendering
   content. Report per page with the law cited; fix the map and the page in one change.

## References (this mode)

| File | Owns | Read when |
|---|---|---|
| `references/boundary-test.md` | the three questions + the misfit table (signup, dashboard, checkout, status-page seam) | deciding whether anything belongs here at all |
| `references/catalog.md` | the nine families with triggers, exits, detection evidence | presenting candidates |
| `references/anatomy.md` | the six-field contract every page signs + the §6 row shape | designing any page |
| `references/onboarding.md` · `transaction-success.md` · `transaction-failure.md` · `http-errors.md` · `session-gates.md` · `maintenance-outage.md` · `access-gates.md` · `token-handoff.md` · `relay-redirect.md` | per-family copy laws, states, anti-patterns | working that family |
| `examples/after-payment/anatomy-sheets.md` | a filled-in success/failure/pending trio with one recorded exclusion | seeing the method end to end |