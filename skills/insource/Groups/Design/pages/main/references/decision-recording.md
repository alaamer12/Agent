# Recording decisions

`PAGES.md` is valuable because of its **reasons**, not its rows. A list of screens can be
rebuilt by anyone; the memory of why a screen was rejected cannot. Every inclusion, exclusion,
split, merge and redirect gets a record.

---

## Decision classes

| Class | Meaning | Lives in |
|---|---|---|
| **Include** | The product needs this screen | Category table |
| **Exclude** | Considered and deliberately not built | Exclusions |
| **Defer** | Plausible later; not in this scope | Exclusions (`deferred`) or Open Decisions |
| **Redirect** | Route exists only to hand off | Redirects + Exclusions |
| **Split** | One screen divided into several | Splits |
| **Merge** | Two candidates collapsed into one | Splits (as a "not split" note) or Notes |
| **Rename** | Same screen, canonical name changed | Notes + Redirects (old route alias) |
| **Owned elsewhere** | Another skill or surface owns it | Exclusions (`owned-elsewhere`) |

---

## Anatomy of a record

Every decision answers six questions:

1. **What** — the screen or route, in the user's vocabulary.
2. **Decision** — include, exclude, defer, redirect, split, merge.
3. **Why** — the product reason, not a preference.
4. **Evidence** — where the reason came from (doc, route, entity, ticket, user answer, domain
   logic). A reader must be able to open it or trace it.
5. **Confidence** — `confirmed`, `inferred`, or `uncertain`; for exclusions, how settled the no is.
6. **Revisit trigger** — the condition that would make this decision wrong (a new platform, paid
   plans, physical goods, multi-user, a new jurisdiction).

A record without a revisit trigger is a dead end. It cannot be safely challenged later.

---

## Reason quality

A reason must explain the product, not the author's taste.

| Weak reason | Why it fails | Better reason |
|---|---|---|
| "Not needed" | Says nothing; the next agent re-adds it | "No physical goods, so no shipping or returns screens" |
| "Too complex for v1" | No boundary; complexity is not defined | "Deferred: v1 is single-user, so no members, roles or audit log" |
| "Users don't want it" | Unsupported; whose users? | "User interview 2026-10-14: testers used email instead of in-app messages" |
| "Standard practice" | Appeal to fashion, not this product | "Required by PCI scope: payment fields are hosted by the provider, so no card form page" |
| "We already have settings" | Ignores the split tests | "Notifications preferences live under `/settings/notifications`; no separate centre needed because events are low-volume" |
| "Magic link" | Too terse to reconstruct | "Passwordless: `/reset-password` redirects to `/forgot-password` with a notice; no password form exists" |

Good reasons are **specific**, **falsifiable**, and **linked**. If the reason cannot be wrong,
it is not a reason.

---

## Evidence hierarchy

When sources disagree, prefer the more specific and more recent:

1. **User's explicit answer this session** — overrides everything below, but record it as such.
2. **Recorded product decision** (`DECISIONS.md`, ADR, ticket with a date) — the project's memory.
3. **Existing route/page code** — proof a screen exists, not proof it should.
4. **Architecture or data model** — entities imply screens; they do not mandate them.
5. **Product brief / README** — intent, may be stale.
6. **Domain catalog (`data.csv`)** — a candidate generator, never evidence for this product.
7. **General best practice** — the weakest; use only to start a conversation.

A route in code that contradicts a written decision is a **conflict**, not a tie. Surface it in
Open Decisions; do not silently pick one.

---

## Recording exclusions

The exclusion table is the most important part of the map. It has five required fields:

| Field | Rule |
|---|---|
| `Screen` | The name the user would search for |
| `Route` | The route it would have had, if any |
| `Decision` | `excluded`, `deferred`, `redirect`, `owned-elsewhere`, `state` |
| `Reason` | Specific product reason |
| `Source` | Doc section, decision record, user answer, or `domain logic` |
| `Revisit when` | A concrete trigger |

### Worked examples

| Screen | Decision | Reason | Revisit when |
|---|---|---|---|
| Reset Password | redirect | Passwordless product; magic link only | Password auth is added |
| Shipping Policy | owned-elsewhere | No physical goods; `/pages secondary` does not need it either | Physical goods launch |
| Admin panel | deferred | v1 is single-user | Multi-user or team plans ship |
| Team roles | deferred | No shared workspaces in v1 | Workspace feature enters scope |
| Social login | excluded | Enterprise SSO is the only identity integration | Consumer signup launches |
| Notification center | merge | Low event volume; a dashboard activity feed covers it | Events exceed ~20/day or become actionable |
| Separate mobile screens | state | Same route, responsive layout; no distinct job | Native navigation diverges from web |

An exclusion the user explicitly asked for is recorded with their words, not paraphrased into
something weaker.

---

## Recording splits

A split record needs:

- the **original screen** and its route;
- the **resulting sub-pages** and routes;
- the **tests** that justified the split (back, deep-link, model, complexity, audience,
  lifecycle);
- the **redirect** from the old route, if any;
- what was **deliberately left together**, so the next agent does not split further without
  cause.

Example:

| Was | Became | Tests | Left together | Date |
|---|---|---|---|---|
| `/settings` | `/settings/profile`, `/settings/account`, `/settings/security`, `/settings/notifications`, `/settings/billing` | model, complexity, deep-link, audience | appearance and language remain sections of Account | 2026-11-09 |

---

## Recording redirects

A redirect record needs the source route, the target, the type, the reason, and what the user
sees. "Silent bounce" is only acceptable for pure aliases. If the user expected a screen, the
target must carry a notice explaining the flow.

| From | To | Type | User sees | Reason |
|---|---|---|---|---|
| `/reset-password` | `/forgot-password` | alias + notice | "We email you a sign-in link; there is no password to reset." | Passwordless product |
| `/settings` | `/settings/profile` | 302 | the profile page | Hub has no standalone content |
| `/billing` | `/org/:org/settings/billing` | 301 | the org billing page | Billing moved to organization scope |

---

## Handling uncertainty

| Situation | Record as | Do not |
|---|---|---|
| Docs are silent but the domain strongly implies it | `inferred`, with `domain logic` evidence | Call it `confirmed` |
| The user says "maybe later" | `deferred` with a revisit trigger, or Open Decisions | Build it "just in case" |
| The user is unsure now | `uncertain` + an Open Decision with options | Guess and move on |
| Two docs conflict | Open Decision naming both sources | Pick the one you like |
| A screen exists in code but no doc mentions it | `confirmed` (it exists), with a note that its product rationale is unknown | Delete it |
| A documented decision is stale | Supersede with a dated note and a link | Rewrite history silently |

---

## Supersession

Decisions change. The map must show that they changed.

```markdown
| Screen | Decision | Reason | Supersedes |
|---|---|---|---|
| Team roles | include | Enterprise plan now sells custom roles | 2026-10-02 exclusion "no roles in v1" |
```

Rules:

- Never delete a decision row that a downstream artifact may reference. Mark it superseded.
- Keep the original date and source in the superseded note.
- If a route changes, add the old route to Redirects.
- If a screen is removed, keep the exclusion and change the decision to `excluded`, with the new
  reason.

---

## One-round confirmation

When presenting decisions to the user, do it in one message:

```text
Draft map: 6 categories, 41 screens, 9 exclusions.

Confirmed from docs:
  Login, Signup, Verify Email, Dashboard, Settings (split), Billing.

Inferred (domain logic):
  Forgot Password, Notifications, 404/403/500, Data Export.

Uncertain — need your answer:
  1. Reset Password: page, or magic link only?
  2. Team accounts in v1? If yes: members, roles, invites, audit.
  3. Notification center: separate page, or dashboard activity feed?

Excluded — confirm or correct:
  Shipping (no physical goods), Admin panel (single-user v1),
  Social login (SSO only), Separate mobile screens (responsive web).
```

Then apply the answers and write the file. Do not drip questions one at a time.

---

## Quality checklist

Before the map is considered done:

- [ ] Every screen has a status and a confidence.
- [ ] Every `confirmed` screen has an openable evidence reference.
- [ ] Every `excluded` or `deferred` screen has a specific reason and a revisit trigger.
- [ ] Every `uncertain` screen has an Open Decision row.
- [ ] Every split names the tests that justified it.
- [ ] Every redirect names its type and what the user sees.
- [ ] Every "owned elsewhere" names the owning skill or surface.
- [ ] Conflicts are recorded, not resolved silently.
- [ ] Counts in Coverage match the tables.
- [ ] No row depends on a fact the user never gave.
