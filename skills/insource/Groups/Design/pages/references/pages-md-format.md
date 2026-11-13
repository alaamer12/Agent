# `PAGES.md` format — the one inventory

One file, written at the project root (or the docs location the project uses). It is the
contract every downstream skill reads: `prototype`, `impeccable`, `planner`, `seo`, and any
implementation skill. **All three page kinds live here, one section per kind** — a page's
section is its kind tag; nothing outside this file maintains a screen list.

Keep the section order stable so tools and humans can find things. Omit a section that has no
rows rather than shipping an empty heading (exclusions are never empty in a real project).

---

## Skeleton

```markdown
# Pages — <Project Name>

> Generated/updated by `pages` on <YYYY-MM-DD>. Source of truth for the page set.
> Changes: update this file in the same change that adds, removes, or renames any page,
> document, or conditional screen.

## 1. Context

| Field | Value |
|---|---|
| Product | <one line> |
| Discipline | <from ../main/references/data.csv, e.g. healthcare + saas-b2b> |
| Platforms | web / iOS / Android / desktop / embedded |
| Roles | <role list> |
| Sources read | <docs, routes, entities, decisions> |
| Scope of this map | <v1 / MVP / whole product> |

## 2. Legend

Status — how settled the entry is (all kinds):

| Mark | Meaning |
|---|---|
| `confirmed` | Direct evidence in docs, routes, entities, or a recorded decision |
| `inferred` | Domain logic implies it; not yet confirmed by the project |
| `uncertain` | Needs a user decision; listed in Open Decisions |
| `excluded` | Considered and deliberately not built; see Exclusions |

Kind — what the unit is (main-table column; secondary and complementary sections carry their
own specialized columns defined in §5/§6):

| Kind | Meaning |
|---|---|
| `page` | Top-level route with its own job |
| `subpage` | Deep-linkable concern inside a hub or parent |
| `modal` | One short decision; not linkable |
| `state` | Not a route; a condition of another screen |
| `redirect` | Route exists only to hand off; see Redirects |

## 3. Roles and surfaces

| Role | Landing route | Sees | Does not see |
|---|---|---|---|
| Member | `/dashboard` | own work, workspace content | billing, admin |
| Guest | `/login` | marketing, auth | anything behind auth |

If a platform has a different screen set, add a **Surface notes** column to the tables rather
than duplicating the whole file.

## 4. Main pages

Grouped by functional category. Each category: slug, one-line purpose, table.

### Auth

Purpose: identity, access, and account recovery.

| Screen | Route | Kind | Status | Confidence | Evidence | Notes |
|---|---|---|---|---|---|---|
| Login | `/login` | page | confirmed | high | `docs/auth.md` | email + password; SSO link |
| Forgot Password | `/forgot-password` | page | confirmed | high | `docs/auth.md` | sends magic link |
| Reset Password | `/reset-password` | redirect | excluded | high | `DECISIONS.md` §auth | magic link only; see Redirects |

## 5. Secondary documents

Always-present trust documents (`/pages secondary` writes them; this section owns the list).
Canon per document — one row, platforms point at it.

| Document | Type family | Canon route | Surfaces | Status | Notes |
|---|---|---|---|---|---|
| Terms of Service | legal | `/legal/terms` | web · [desktop] embed-link · [mobile] open-browser | confirmed | last updated <date> |
| Privacy Policy | legal | `/legal/privacy` | web · bundled offline copy = declared synced duplicate | confirmed | — |
| Status | trust | `/status` | web only | inferred | no ops tooling yet — Open Decisions |

## 6. Complementary screens

Conditional pages (`/pages complementary` designs them; this section registers them with the
anatomy fields that make them auditable).

| Screen | Family | Trigger | Condition source | Exits | Status |
|---|---|---|---|---|---|
| Payment Success | transaction-success | order status `settled` | `GET /orders/{id}/status` | receipt · manage · home | confirmed |
| Payment Failed | transaction-failure | status `declined\|failed` | same + webhook state | retry(manual per contract) · change method · home | confirmed |
| OAuth callback relay | relay-redirect | provider return path hit | server state/nonce check | allowlisted forward only | confirmed |
| Onboarding | onboarding | setup incomplete | account flag | complete · skip · resume | inferred |

## 7. States

Shared states that are not routes — these belong *inside* pages and are listed to prevent
blank-screen shipping; §6 is for whole conditional screens. Per-screen states go in Notes.

| State | Applies to | Planned | Notes |
|---|---|---|---|
| Loading | all async screens | yes | skeleton, no layout shift |
| Empty | list screens | yes | first-run guidance, not a blank page |
| Session expired | authenticated screens | yes | re-auth, return to route (`session-gates`) |
| Offline | mobile / PWA | <yes/no> | cached read-only state |

## 8. Splits

| Was | Became | Tests that justified it | Date |
|---|---|---|---|
| Settings | `/settings/profile`, `/settings/security`, `/settings/billing` | model, complexity, audience, deep-link | <date> |

## 9. Exclusions

Every page considered across **all three kinds** and deliberately not built — one table, the
kind column says which universe it was rejected from.

| Page | Kind | Route | Decision | Reason | Source | Revisit when |
|---|---|---|---|---|---|---|
| Reset Password | main | `/reset-password` | excluded | passwordless product; magic link only | `DECISIONS.md` §auth | password auth is added |
| Shipping Policy | secondary | `/shipping` | excluded | no physical goods | product brief | physical goods launch |
| Cancel Confirmation | complementary | `/payments/cancelled` | excluded | failure page owns all cancel states | `examples/after-payment` anatomy | provider adds distinct cancel webhook |

`decision` is one of `excluded`, `deferred`, `redirect`, `state`, or `owned-elsewhere`.

## 10. Redirects

| From | To | Type | Reason | Source |
|---|---|---|---|---|
| `/settings` | `/settings/profile` | 302 | hub has no standalone content | this file |
| `/reset-password` | `/forgot-password` | alias + notice | passwordless flow | `DECISIONS.md` §auth |

## 11. Open decisions

| Decision | Options | Owner | Needed by |
|---|---|---|---|
| Team accounts in v1? | yes / no / later | <user> | before auth build |

## 12. Coverage

| Check | Result |
|---|---|
| Main routes / confirmed / inferred | <n> / <n> / <n> |
| Secondary documents (canon rows) | <n> |
| Complementary screens registered | <n> |
| Exclusions / redirects / open decisions | <n> / <n> / <n> |
| Every entity has list + detail | yes |
| Every role has a landing route | yes |
| Every destructive action has a confirmation state | yes |
| Every conditional flow has its §6 row registered before build | yes |

## 13. Change protocol

1. Add, remove, or rename any page of any kind only by editing this file in the same change.
2. A removed page moves to **Exclusions** (with its kind) — never disappears silently.
3. A split records the old route in **Redirects**.
4. A changed decision supersedes the old row with a date and a source link.
5. Downstream skills read this file; they do not maintain their own screen list.
```

---

## Field rules

| Field | Rule |
|---|---|
| `Screen`/`Document` | Human-readable name the user would recognise; match their vocabulary. |
| `Route` / `Canon route` | One canonical location. Aliases go in Redirects; `-` only for states. |
| `Kind` | `page`, `subpage`, `modal`, `state`, `redirect` (main table); §5/§6 imply their kind by section. |
| `Status` | `confirmed`, `inferred`, `uncertain`, `excluded`. Never leave blank. |
| `Confidence` | Confidence in existence, not design. `high` needs evidence. |
| `Evidence` | File path, doc section, route file, ticket, or `domain logic`. No vague "common". |
| `Family` (§6) | One of the nine complementary families — must match a `complementary/references/` doc. |
| `Trigger`/`Condition source`/`Exits` (§6) | Per `../complementary/references/anatomy.md`; a §6 row missing any is an audit defect. |
| `Notes` | Scope caveat, split pointer, state note, redirect target. Keep short. |

### Status rules

- `confirmed` requires an `Evidence` source a reader can open.
- `inferred` is the default for domain-logic candidates. Never label a guess `confirmed`.
- `uncertain` must have a row in **Open decisions**.
- `excluded` must have its kind, reason, and revisit trigger in **Exclusions**.
- An `excluded` page may still have a `Route` when a redirect exists.

## Writing rules

- **One row per page.** Two routes never share a cell.
- **No orphan categories, no empty tables** — delete the heading or the row, never ship a
  placeholder.
- **Counts must match.** Coverage is computed from the sections, not estimated.
- **Dates are real.** Session date; no decorative "last updated".
- **Links resolve.** Evidence paths exist at write time.
- **This file is not a design doc.** No layouts, colours, or component choices — those belong
  to `prototype`, `impeccable`, or the design system.

## Downstream contract

| Consumer | Reads | Expects |
|---|---|---|
| `prototype` | §4, §5 placement, §6, §7 | One page per confirmed route; states as variants; conditional screens built per their §6 anatomy rows |
| `impeccable` / design | §3, §4 | Screen set and role surfaces |
| `planner` | §4, §8, §9 | Work breakdown that respects the map |
| `seo` | §5 | Canon routes, sitemap completeness |
| Implementation | Everything | No inventing pages outside the map; §6 missing a row means the conditional screen stops and registers first |

When a downstream skill needs a page this file lacks, the correct move is to update this file
first, then build. A page that exists only in code is a map defect.
