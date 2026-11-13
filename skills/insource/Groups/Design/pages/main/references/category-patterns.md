# Category patterns — deriving the screen tree

The catalog is a **starting point ranked by how often real products ship a screen**, not a
checklist to reproduce. Evidence from the project decides what enters `PAGES.md`; prevalence
only decides what to look at first. A 95% screen the product does not need is still excluded, with
the reason written down.

---

## Two layers, plus the project

| Layer | Source | What it answers |
|---|---|---|
| **Universal** | `data.csv` rows where `discipline=universal` | What almost every account product has: auth, shell, settings, billing, error states |
| **Domain** | `data.csv` rows for the project's discipline(s) | What this kind of product typically has: patient portal, CRM, LMS, marketplace, fleet tool |
| **Project** | docs, routes, entities, tickets, decisions | What *this* product actually has, and what it explicitly rejected |

Read all three. The domain layer is the most useful during drafting because it supplies the
vocabulary the user recognises; the project layer has the final say.

---

## `data.csv` — columns and how to read them

```
discipline,category,page,route,kind,prevalence,tier,basis,confidence,aka,notes
```

| Column | Meaning |
|---|---|
| `discipline` | `universal`, or an industry/product family (`healthcare`, `crm`, `banking`, `education`, `logistics`, …) |
| `category` | Functional family inside the product (`auth`, `settings`, `claims`, `records`, …) |
| `page` | Human-readable screen name |
| `route` | Route hint; `-` for states |
| `kind` | `page`, `subpage`, `modal`, `state`. Only `page` and `subpage` become rendered routes; redirects are decided in the map |
| `prevalence` | Estimated share of products in that discipline that ship it, 0–100 |
| `tier` | `core` ≥85, `common` 65–84, `optional` 35–64, `niche` <35 |
| `basis` | `universal`, `product-tour`, `regulation`; extended rows may add `domain-model` or `research` |
| `confidence` | Confidence in the *estimate*: `high`, `medium`, `low` |
| `aka` | Alternate names users may say; match against these before inventing a new screen |
| `notes` | Scope caveats, redirect alternatives, state-vs-page warnings |

**Prevalence is an estimate, not a statistic.** It is calibrated from public product navigation,
documentation and tours across the discipline. Never present it to the user as measured data.
Say "commonly present" or "roughly two-thirds of products in this space", and let the evidence
override it. When prevalence and the project's reality disagree, the project wins.
See [`sources.md`](sources.md) for the method, the representative sources per discipline, and the
limits of the sample.

**Tier is a reading order, not a mandate.** Draft `core` and `common` rows first, then ask about
`optional` ones whose preconditions the project actually meets, and mention `niche` rows only
when the user's own words point at them.

### Query recipes

Use any search tool (`rg`, `grep`, `Select-String`, a spreadsheet, or the agent's own search):

```text
Everything the discipline typically has   -> discipline is healthcare
The universal baseline                    -> discipline is universal
Find a screen by any of its names         -> search aka for login, sign in, signin
Only the screens most products ship       -> tier is core or common
Every settings split candidate            -> category is settings
```

Match the user's vocabulary against `aka` first. "Preferences", "account", "profile",
"options" and "settings" are often the same intent; the catalog tells you which one normally
owns what.

---

## Category families

Categories are functional, not visual. A category is a job the user hires the product to do.
The slug is for the map; the purpose line is for the reader.

| Category | Owns | Typical screens | Split trigger |
|---|---|---|---|
| `auth` | Identity and access | Login, Signup, Forgot/Reset, Verify, MFA, Invite, SSO | More than 6 screens, or separate invite/SSO flows |
| `onboarding` | First-run activation | Welcome, profile setup, workspace create, invite, plan, tour | Multi-step wizard vs persistent checklist |
| `shell` | Global frame | Dashboard, search, notifications, profile, settings hub, help | Settings hub always splits |
| `work` | The product's core job | Issues, orders, claims, courses, projects, shipments | One category per distinct job, not per entity |
| `records` | Entity detail surfaces | Contact detail, order detail, patient record, listing detail | Tabs → sub-pages when deep-linkable |
| `settings` | Configuration | Profile, account, security, notifications, billing, team | Always split by scope (personal/workspace/org) |
| `billing` | Money in | Pricing, checkout, success, invoices, plan, usage | Payment vs plan vs history are separate concerns |
| `admin` | Operator control | Members, roles, audit, moderation, integrations, retention | Operator surface distinct from user settings |
| `trust` | Safety and transparency | Security center, sessions, blocked accounts, data export | Regulated or multi-user products |
| `system` | Failure and edge | 404, 403, 500, maintenance, offline | One per failure class, not one generic "error" |
| `public` | Unauthenticated marketing | Home, pricing, about, docs, status, changelog | Secondary documents belong to `/pages secondary` |
| `support` | Help and recovery | Help center, contact, ticket, dispute | When support is a product surface, not a mailto |

Do not create a category for a single screen unless that screen is a genuine job. A lone
"Reports" screen belongs in `work` or `admin`, not in a new category.

---

## Universal baseline (abridged)

Read `data.csv` for the full set. The shape almost every account product needs:

- **Auth** — Login, Signup, Forgot Password, Verify Email; Reset Password only if the flow needs
  a dedicated screen. Invite and SSO are team/enterprise additions.
- **Onboarding** — Welcome and Profile Setup are common; workspace, plan and tour are
  conditional. A persistent checklist is often better than a long wizard.
- **Shell** — Dashboard, Search, Notifications, Profile, Settings hub, Help, plus 404/403/500.
  Maintenance and offline are conditional.
- **Settings** — Profile, Account, Security, Notifications; Billing for paid; Team/Roles for
  multi-user; Danger Zone and Data Export for trust.
- **States not pages** — empty, loading, filtered-empty, error, success, unsaved-changes,
  delete-confirmation, session-expired, upgrade-prompt, permission-denied, offline.

---

## Domain signatures

These are the screens that make a discipline recognisable. The CSV carries the full list and
prevalence; this table is the shorthand for drafting.

| Discipline | Signature screens | Common exclusions to check |
|---|---|---|
| `saas-b2b` | Workspace home, projects, members, roles, audit, SSO, integrations, billing | Marketing site, docs, status are separate surfaces |
| `crm` | Contacts/companies/deals/tickets, pipelines, reports, dashboards, imports, workflows | Not every CRM sells products or quotes |
| `project-management` | Inbox, my work, issues, board, backlog, cycles, projects, roadmap, views | Cycles only for time-boxed teams; initiatives only above projects |
| `helpdesk` | Agent inbox, ticket detail, customers, knowledge base, macros, SLA, CSAT | Public help center may be a separate product |
| `hr-recruiting` | Jobs, candidates, pipeline, interviews, scorecards, offers, career site, apply | Requisitions and referrals are enterprise/optional |
| `docs-wiki` | Home, spaces, page viewer/editor, search, templates, history, permissions | Comments and version history are conditional |
| `community` | Feed, spaces, post detail, members, DMs, moderation, roles, invites, events | Leaderboards and events are optional |
| `social` | Feed, explore, post detail, compose, profile, followers, messages, notifications | Stories/live only for media-first products |
| `marketplace` | Search, listing, seller storefront, cart, checkout, orders, messages, reviews, seller dashboard, payouts | Payouts and disputes only when the platform holds money |
| `ecommerce` | Catalog, product, cart, checkout, orders, addresses, wishlist, returns, tracking | Returns only for physical goods; store locator only omnichannel |
| `banking` | Accounts, transactions, transfer, payees, bill pay, statements, cards, controls | Loans/deposits only for banks that offer them |
| `fintech` | Portfolio, transactions, send/receive, cards, budgets, insights, KYC | KYC only for regulated money movement |
| `healthcare` | Appointments, prescriptions, results, messages, records, billing, insurance, consents, dependents | Proxy/dependents only for family care; referrals conditional |
| `education` | Courses, modules, lessons, assignments, submissions, grades, quizzes, discussions, calendar | Certificates only for completion-based learning |
| `travel` | Search, results, property detail, room/rate, booking, payment, confirmation, manage booking, check-in | Loyalty only with a program; check-in only for airlines/hotels |
| `food-delivery` | Restaurants, menu, cart, checkout, tracking, orders, addresses, promos | Promos only with a promotion engine |
| `media-streaming` | Home, browse, title, player, search, watchlist, downloads, profiles, billing | Downloads only for offline-capable apps |
| `real-estate` | Map search, listing, saved homes/searches, mortgage calculator, agent, tour, home value | Seller dashboard and offers only for transaction products |
| `insurance` | Quote, policy dashboard/detail, coverage, claims, file claim, documents, payments, renewals | Beneficiaries only for life/coverage products |
| `logistics` | Shipments, tracking, routes, drivers, vehicles, maintenance, documents, invoices, dispatch | Geofences/fuel only when telematics exists |
| `government` | Services catalog, service detail, application, status, appointments, payments, permits, report issue | Benefits only for administering agencies |
| `fitness` | Dashboard, workouts, programs, activity, progress, goals, classes, devices | Nutrition only for combined products; trainers only for coaching |
| `news-publishing` | Home, section, article, author, search, topic, newsletter, saved, subscription | Live blogs only for live-event publishers |
| `developer-tools` | Projects, code, issues, PRs, actions, deployments, logs, domains, env, keys, usage, docs, status | Code browser and PRs only for source-hosting products |
| `analytics-bi` | Dashboards, explore, query, data sources, datasets, alerts, share | Segments only for customer analytics |
| `booking-services` | Services, staff, date/time, details, payment, confirmation, my bookings, reschedule | Waitlist only for high-demand capacity |
| `gaming` | Store, library, game detail, download, matchmaking, lobby, profile, achievements, leaderboard | Matchmaking/lobby only for multiplayer; inventory only for item economies |
| `crypto` | Portfolio, asset, buy/sell, send/receive, transactions, staking, KYC, security, fees | Staking/earn only where offered; KYC for custodial exchange |
| `email-calendar` | Inbox, compose, message, labels, contacts, calendar, event, tasks, search | Tasks only when the product includes them |

If the project spans disciplines (a health marketplace, a fintech CRM), take the **union** of the
signature screens, then prune per role and per evidence. Do not average the two catalogs.

---

## Signals that imply screens

Read these from docs, routes, entities and tickets — not from imagination.

| Signal in the project | Screens it implies |
|---|---|
| An entity with a collection | List/index, detail, create, edit (or a declared inline alternative) |
| An entity with a lifecycle | Status surface, timeline/history, transition actions |
| A payment or plan | Pricing, checkout, success, invoices, payment methods, plan change |
| A team, org or workspace | Workspace switcher, members, invites, roles, org settings |
| Notifications | Notification center **and** notification preferences — different jobs |
| User-generated content | Composer, feed/list, detail, moderation/report, guidelines |
| Search or filters | Results page, filtered-empty state, saved searches if recurring |
| Physical delivery | Addresses, tracking, shipping status, returns |
| Regulation or money | Consent, KYC/verification, audit log, data export, security center |
| Multi-role product | One home per role, plus a role/surface matrix |
| API or integrations | API keys, webhooks, logs, usage, docs |
| Mobile permissions | Pre-permission primer, settings fallback, offline state |

---

## Pruning: four filters before a screen enters the map

1. **True?** Does the product actually do this? No shipping page without shipping; no claims
   without claims.
2. **Reachable?** Is there a real user journey to it? A screen no role can reach is dead weight.
3. **Distinct?** Does it do a job no existing screen does? If it is the same data with a filter,
   it is a view or state, not a page.
4. **Owned?** Does another skill own it? Legal/policy documents belong to `/pages secondary`;
   marketing pages may belong to a separate site. Record the handoff instead of duplicating.

Apply the full page-vs-state-vs-modal-vs-redirect tests in
[`split-and-redirect.md`](split-and-redirect.md).

---

## Coverage checks before writing the map

- Every entity has a list and a detail route, or a recorded reason why not.
- Every role has a landing surface.
- Every destructive action has a confirmation state.
- Every async surface has loading, empty, error and filtered-empty states planned.
- Every form has validation, success and unsaved-changes behaviour.
- Every external or policy document has an owner (this skill or `/pages secondary`).
- Every "no" has an entry in the exclusions table.

A map that passes these is complete enough to build from.
