# Splitting concerns and choosing redirects

Two decisions keep a page map honest:

1. **Is this one screen or several?** Bloated screens hide mixed concerns.
2. **Is this a page at all?** Some needs are states, modals, or redirects.

Both are recorded as decisions, not left implicit. A split with no reason becomes arbitrary; a
redirect with no record becomes a broken link later.

---

## 1. The unit decision

Before naming a screen, decide what kind of unit it is.

| Unit | Use when | Test it must pass | Example |
|---|---|---|---|
| **Page** (`page`) | Distinct job, reachable by URL, survives refresh | Back button returns somewhere sensible; URL is shareable | Order detail |
| **Sub-page** (`subpage`) | A distinct concern inside a hub, deep-linkable | The parent still makes sense without it; it has its own mental model | `/settings/notifications` |
| **State** (`state`) | Same route, different data condition | Refreshing keeps you in the same job | Empty cart, filtered-empty, loading |
| **Modal** | One decision, short, no need to link | Closing returns to exactly where you were | Delete confirmation, invite member |
| **Drawer / sheet** | Contextual detail beside the current work | The underlying screen stays usable | Contact quick-view from a list |
| **Redirect** | A route that exists only to send you elsewhere | Nothing is rendered except the handoff | `/settings` → `/settings/profile` |

### The four page tests

A candidate is a page only if it passes all four:

1. **Back-button test** — pressing Back returns to a meaningful previous screen, not to a modal
   that has already closed or a state that no longer exists.
2. **Deep-link test** — a user can paste the URL into a new tab and land in the same place, with
   the same object loaded (or a correct 404/403).
3. **Mental-model test** — the user would describe this as "a place I go", not "a thing that
   opens".
4. **Data-complexity test** — it carries enough content or state to justify a surface. A single
   toggle or a one-line confirmation is not enough.

Fail the back-button or deep-link test → modal or state.
Pass all four but shares a hub → sub-page, not a top-level page.
Pass all four and has its own object → page.

### The state test

A candidate is a state, not a page, when:

- it is the same route with different data (`empty`, `loading`, `error`, `filtered-empty`);
- it disappears on refresh because it was transient feedback (`success toast`, `saved`);
- it is a conditional variant of the same job (`permission denied` inline, `upgrade prompt`).

States still belong in `PAGE-MAP.md` — under a **States** column or a shared states table — because
an unplanned state is how empty screens ship.

---

## 2. Concern splitting

### Signals a screen is carrying too many concerns

- The page has more than **5–7 independent sections**, or more than **3 distinct questions** the
  user answers.
- The URL needs a query parameter to reach a section (`/settings?tab=billing`).
- Different roles see disjoint sets of sections on the same page.
- One section has its own save, cancel, validation or permission model.
- Users ask "where do I change X?" and the answer is "scroll down".
- The page title is a conjunction: "Account, Billing and Team".
- A support article has to explain which tab to open.

### The six split tests

Split when **two or more** are true:

| Test | Question | If yes |
|---|---|---|
| **Back** | Would a user expect Back to leave the section, not the hub? | Sub-page |
| **Deep-link** | Do support, emails or docs need to link straight to this section? | Sub-page |
| **Model** | Does the section have a name users already use as a place? ("Billing", "Notifications") | Sub-page |
| **Complexity** | Does it have its own form, table, permissions or save lifecycle? | Sub-page |
| **Audience** | Is it for a different role or scope (personal vs workspace vs org)? | Separate sub-page, often separate route tree |
| **Lifecycle** | Is it read rarely, changed rarely, or dangerous? | Separate sub-page, often out of the main nav |

Do **not** split when the only difference is presentation (tabs over the same data), or when the
sections are short and always read together. A 300px card with three toggles is a section, not a
page.

### Split shapes

| Shape | Route | Use when |
|---|---|---|
| **Hub and spoke** | `/settings` → `/settings/profile` | Many sub-pages; hub is a directory |
| **Nested tree** | `/settings/workspace/members` | Two levels of scope (personal → workspace → org) |
| **Tabs that are routes** | `/settings/profile`, `/settings/security` | Few sub-pages; tabs are the nav, routes are real |
| **Section anchors** | `/settings#notifications` | Only for short, always-read-together content — never for forms |
| **Full separate surface** | `/admin/*` | Different audience, permissions and navigation |

Tabs are a visual treatment; the route is the contract. If a tab is worth linking, give it a
route. If it is not worth linking, it is probably a section, not a tab.

---

## 3. The canonical settings split

Settings is the most common bloated screen. Split it by **scope**, then by **concern**.

### Scope model

| Scope | Who owns it | Typical route | Examples |
|---|---|---|---|
| **Personal** | The signed-in human | `/settings/*` | Profile, account, security, notifications, appearance |
| **Workspace** | The current team/workspace | `/w/:workspace/settings/*` or `/settings/workspace/*` | Members, roles, defaults, integrations |
| **Organization** | The billing/legal entity | `/org/:org/settings/*` | Billing, SSO, domains, audit, retention |
| **Admin/operator** | Internal staff | `/admin/*` | Users, moderation, feature flags, impersonation |

Do not put personal and organization settings under one flat `/settings` tree when both exist.
The permission model differs, and a member should never see a billing route they cannot use.

### Personal settings sub-pages

| Sub-page | Contents | Split from | Notes |
|---|---|---|---|
| `/settings/profile` | Name, avatar, bio, public handles | Hub | Safe, frequently edited |
| `/settings/account` | Email, username, locale, timezone | Profile | Identity, not presentation |
| `/settings/security` | Password, MFA, passkeys, recovery | Account | High trust |
| `/settings/sessions` | Active devices, revoke | Security | Often a section; page when multi-device |
| `/settings/notifications` | Channel × event matrix, digest | Hub | Distinct from the notification center |
| `/settings/privacy` | Visibility, blocked users, data sharing | Account | Trust-sensitive |
| `/settings/appearance` | Theme, density, reduced motion | Hub | Section unless themes are rich |
| `/settings/language` | Locale, timezone, date/number format | Account/Appearance | Section in most products |
| `/settings/billing` | Plan, renewal, payment method, invoices | Hub | Paid only |
| `/settings/team` | Members, invites, roles | Hub | Workspace scope, not personal |
| `/settings/integrations` | Connected apps, API keys, webhooks | Hub | Developer/team products |
| `/settings/danger` | Export, deactivate, delete | Hub | Always separated and visually distinct |

### When the hub itself is unnecessary

If there are **three or fewer** sub-pages and they are all short, use one settings page with
clear sections and anchors. Do not build a hub that only links to three cards.

If there are **more than seven** top-level settings destinations, group them under two levels:
`/settings/account/*`, `/settings/workspace/*`, `/settings/billing/*`. Keep the top level
scannable.

### Splitting other common bloaters

| Bloated screen | Split into | Why |
|---|---|---|
| User/company detail | Overview · Activity · Documents · Permissions | Tabs over one record; deep-linkable when shared |
| Project detail | Overview · Work · Files · Settings | Different jobs and permissions |
| Notifications | Center (`/notifications`) · Preferences (`/settings/notifications`) · Email templates (admin) | Reading vs configuring vs authoring |
| Billing | Plan · Payment methods · Invoices · Usage | Different lifecycles and permissions |
| Dashboard | Role dashboards (`/dashboard`, `/admin`, `/analytics`) | Different audiences, not tabs |
| Admin | Users · Content · Moderation · Settings · Audit | Operator-only surface |
| Onboarding | Wizard steps, then a persistent checklist | One-time flow vs ongoing activation |
| Report | Report list · Report builder · Report view | Authoring vs reading |

---

## 4. Redirect instead of page

A redirect is a **decision**, not a missing screen. Use it when a route should exist for
compatibility, naming or flow reasons but must not render its own surface.

### When a redirect is correct

- **Alias** — a common name maps to the canonical route: `/signin` → `/login`,
  `/preferences` → `/settings`, `/account` → `/settings/account`.
- **Collapsed flow** — the user asked for a screen that the product deliberately handles
  elsewhere: `/reset-password` → `/forgot-password` (magic-link flow), with a notice.
- **Hub root** — `/settings` has no content of its own: redirect to the first sub-page or show a
  hub. Choose one and record it.
- **Legacy route** — an old URL must not 404: `/pricing` → `/#pricing`, `/dashboard-old` →
  `/dashboard`.
- **Auth wall** — an unauthenticated deep link redirects to `/login?next=/original`, then back.
- **Locale root** — `/` → `/en` (or content negotiation), never a chain of locale redirects.
- **Platform handoff** — a desktop/mobile build opens the web canon for a policy page.
- **Moved section** — a settings section moved to a new scope: `/settings/billing` →
  `/org/acme/settings/billing`.

### When it is not

- The user wants a real screen and you are avoiding the work. A redirect is not a substitute for
  a page the product needs.
- The target requires the user to understand something first. Show the notice on the target, not
  a silent bounce.
- The redirect would loop. Every redirect chain must terminate in a `page` in one hop, or two at
  most with a recorded reason.

### Redirect types

| Type | Use |
|---|---|
| `301` permanent | Canonical rename; old route never returns |
| `302/307` temporary | Auth wall, maintenance, experiment |
| Client `replace` | In-app route alias; do not pollute history |
| `alias` (record only) | Same surface, alternate name; no server route needed |
| `handoff` | Another platform or canonical host owns the target |

### Recording redirects

Every redirect gets a row in the **Redirects** table of `PAGE-MAP.md`:

| From | To | Type | Reason | Source |
|---|---|---|---|---|
| `/reset-password` | `/forgot-password` | alias + notice | Passwordless product; no reset screen | `DECISIONS.md` §auth |
| `/settings` | `/settings/profile` | 302 | Settings hub has no standalone content | this session |

If the redirect replaces a screen the user asked for, the **Exclusions** table also carries the
decision, with the same reason. One decision, two views: the redirect tells the router what to
do; the exclusion tells the next agent why not to build it.

---

## 5. Route conventions

- One canonical route per screen. Aliases redirect; they never render a second copy.
- Nested resources reflect ownership: `/projects/:id/issues`, not `/issues?project=:id`, when the
  issue cannot exist without the project.
- Settings scope is in the path, not a query: `/org/:org/settings/billing`.
- Use stable slugs for public content; use IDs for private objects. Do not put both in the same
  route family.
- Query parameters are for view state (filters, sort, pagination), not for selecting a different
  screen.
- A route that only changes a tab's visual state is a bug in the map: either promote it to a
  sub-page or keep it as local state.

---

## 6. Anti-patterns

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| One giant settings page | Unfindable, unlinkable, permission-blind | Split by scope and concern |
| A route per tab | Tabs become fake pages with no independent job | Promote real sub-pages; keep the rest as sections |
| A modal for a multi-step flow | Back button breaks; cannot deep-link or resume | Page or wizard route |
| A page for one confirmation | Dead-end surface; refresh re-asks | Modal or state |
| A page per filter | Infinite route sprawl | Query params + one results page |
| Redirect as a substitute for a needed screen | Users cannot do the job | Build the page; record the real exclusion |
| Silent redirect with no explanation | Users think the link is broken | Notice on the target + recorded reason |
| Splitting by database table | Users think in jobs, not schemas | Split by concern, not entity |

---

## 7. Record the decision

For every split or redirect, write:

- **What was one screen** and **what it became**.
- **Which test** justified it (back, deep-link, model, complexity, audience, lifecycle).
- **The old route** and its redirect, if any.
- **What was deliberately not split** and why.

Then add the split to the **Splits** section of `PAGE-MAP.md` and the redirect to the
**Redirects** table. If the split changes a previously recorded decision, supersede it with a
date and a link — never silently rewrite history.
