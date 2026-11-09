# Sources and method

The catalog is a **research synthesis**, not a survey. It exists to give the agent a
discipline-aware starting vocabulary, then get out of the way.

---

## What the catalog is

- **492 candidate screens** across **30 disciplines** (`universal` plus 29 product families).
- Each row records a functional category, a route hint, a unit kind (`page`, `subpage`, `modal`,
  `state`), an estimated prevalence, a tier, an evidence basis, and alternate names.
- It is **not** a specification. A screen in the catalog is a prompt to ask, not a licence to
  build.

## How prevalence was estimated

Prevalence is the estimated share of public products in a discipline that ship the screen. It was
calibrated by reading published product navigation, help-centre documentation, onboarding tours
and user guides for representative products, then rounding to a defensible band. It is **not** a
statistical sample and must never be quoted as one.

| Tier | Band | Reading |
|---|---|---|
| `core` | 85–100 | Expect it; its absence needs a recorded reason |
| `common` | 65–84 | Most products have it; include when the precondition is met |
| `optional` | 35–64 | Roughly a third to two-thirds; ask |
| `niche` | 0–34 | Only when the user's own words point at it |

`confidence` describes confidence in the *estimate*, not in the screen's necessity. `high` means
several representative products agree; `low` means the pattern is thin or the discipline is
fragmented.

---

## Universal baseline sources

The `universal` rows come from cross-product patterns in authentication, account settings,
billing, notification and error-handling documentation, plus the IA methodology already compiled
in `screen-inventory-research.md` (areas A–G: screen-vs-state, sitemap formats, signals, common
mistakes, platform conventions, multi-role IA, inventory lifecycle).

Representative sources:

- Auth0 and Okta documentation on login, signup, password reset, MFA, email verification and
  invitation flows.
- Stripe and Paddle billing documentation on checkout, invoices, payment methods, plan changes
  and failed payments.
- Web platform guidance on 404/403/500 and maintenance responses.
- Product tours of Linear, GitHub, Vercel, Notion and Figma for shell, settings and notification
  patterns.

---

## Discipline sources

| Discipline | Representative sources read | What they informed |
|---|---|---|
| `saas-b2b` | Linear docs (navigation, projects, inbox), Vercel/GitHub settings, HubSpot account navigation | Workspace home, members, roles, audit, SSO, integrations, billing |
| `crm` | [HubSpot navigation guide](https://knowledge.hubspot.com/help-and-resources/a-guide-to-hubspots-navigation), HubSpot CRM product pages, Salesforce-style record patterns | Contacts/companies/deals/tickets, pipelines, reports, imports, workflows |
| `project-management` | [Linear: navigating](https://linear.app/enablement/guides/navigating-linear), [Linear projects](https://linear.app/docs/projects), [Linear inbox](https://linear.app/docs/inbox), [Linear cycles](https://linear.app/enablement/guide/cycles-guide) | Inbox, my work, issues, board, backlog, cycles, projects, roadmap, views, triage |
| `helpdesk` | Zendesk/Intercom/Front navigation and help-centre patterns | Agent inbox, ticket detail, customers, knowledge base, macros, SLA, CSAT |
| `hr-recruiting` | [Greenhouse ATS](https://www.greenhouse.com/ats), [Workday Recruiting datasheet](https://www.workday.com/content/dam/web/en-us/documents/datasheets/datasheet-workday-recruiting.pdf), Greenhouse support docs | Jobs, candidates, pipeline, interviews, scorecards, offers, career site, apply |
| `docs-wiki` | Notion/Confluence-style space and page patterns | Home, spaces, page viewer/editor, search, templates, history, permissions |
| `community` | [Circle moderation settings](http://help.circle.so/p/administration/moderation/manage-moderation-settings), [Discord channel/thread docs](https://docs.discord.com/developers/resources/channel), [Discord rules screening](https://support.discord.com/hc/en-us/articles/1500000466882) | Feed, spaces, post detail, members, DMs, moderation, roles, invites, guidelines |
| `social` | Consumer feed/profile/messaging patterns from public product tours | Feed, explore, post, compose, profile, followers, messages, notifications, topics |
| `marketplace` | Etsy/eBay/Airbnb-style listing, seller and order patterns; [Liferay Commerce storefront pages](https://learn.liferay.com/w/dxp/commerce/creating-store-content) | Search, listing, seller storefront, cart, checkout, orders, messages, reviews, payouts |
| `ecommerce` | Liferay Commerce page types, Shopify-style storefront and account patterns | Catalog, product, cart, checkout, orders, addresses, wishlist, returns, tracking |
| `banking` | [KS Bank online/mobile guide](https://www.ksbankinc.com/assets/files/Rlmu7o3x), retail banking portal tours | Accounts, transactions, transfer, payees, bill pay, statements, cards, controls |
| `fintech` | Consumer money-app tours (portfolio, send/receive, budgets, KYC) | Portfolio, transactions, send/receive, cards, budgets, insights, verification |
| `healthcare` | [athenahealth patient portal quick reference](https://help.athenahealth.com/Ohelp/Content/Features/aCom_Patient_Portal_Quick_Reference_new_GUI_A.htm), patient-portal tours from hospital systems | Appointments, prescriptions, results, messages, records, billing, insurance, consents, dependents |
| `education` | [Canvas/LMS guidance](https://online.illinois.edu/getting-started/learning-management-systems), Moodle/Canvas navigation | Courses, modules, lessons, assignments, submissions, grades, quizzes, discussions, calendar |
| `travel` | Booking.com/Airbnb/airline booking flows | Search, results, property detail, room/rate, booking, payment, confirmation, manage booking, check-in |
| `food-delivery` | DoorDash/Uber Eats-style ordering flows | Restaurants, menu, cart, checkout, tracking, orders, addresses, promos |
| `media-streaming` | Netflix/Spotify-style browse, title, player and profile patterns | Home, browse, title, player, search, watchlist, downloads, profiles, billing |
| `real-estate` | [Zillow saved searches/saved homes](https://zillow.zendesk.com/hc/en-us/articles/213395508-Saved-Searches-and-Saved-Homes), [HomeStack app overview](https://homestack.zendesk.com/hc/en-us/articles/360040977313-App-Overview), [RealScout app overview](https://support.realscout.com/en/articles/11954675-realscout-home-search-app-overview) | Map search, listing, saved homes/searches, mortgage calculator, agent, tour, home value |
| `insurance` | [Brock-Norton client portal](http://www.brocknorton.com/clientportal.html), [Emirates Insurance customer portal](https://eminsco.com/customer-portal), [Mercury account](https://www.mercuryinsurance.com/myaccount), [TRUE member portal](https://trueins.com/member-portal) | Quote, policy dashboard/detail, coverage, claims, file claim, documents, payments, renewals |
| `logistics` | [Oracle Fleet Management](https://docs.oracle.com/en/cloud/saas/transportation/26c/otmol/asset_mgt/about_fleet_management.htm), [MetraFleet features](https://metrafleet.com/features), [Otiggo fleet](https://www.otiggo.com/en/fleet-management), [UrbanTMS](https://urban-tms.com/) | Shipments, tracking, routes, drivers, vehicles, maintenance, documents, invoices, dispatch |
| `government` | [Accela Citizen Access (Tempe)](https://epermits.tempe.gov/citizenaccess/default.aspx), [Madison County citizen portal](https://www.madisoncountytn.gov/574/Citizen-Portal), [Annapolis CSS guide](https://www.annapolis.gov/2345/Managing-Your-Online-Application) | Services catalog, application, status, appointments, payments, permits, report issue |
| `fitness` | Training/nutrition app tours and wearable integrations | Dashboard, workouts, programs, activity, progress, goals, classes, devices |
| `news-publishing` | News site section/article/author/newsletter patterns | Home, section, article, author, topic, newsletter, saved, subscription |
| `developer-tools` | GitHub/Vercel project, deployment and settings patterns | Projects, code, issues, PRs, actions, deployments, logs, domains, env, keys, usage |
| `analytics-bi` | Looker/Metabase-style dashboard, explore and data-source patterns | Dashboards, explore, query, data sources, datasets, alerts, sharing |
| `booking-services` | Salon/clinic/restaurant reservation flows | Services, staff, date/time, details, payment, confirmation, my bookings, reschedule |
| `gaming` | Steam/console store, library, matchmaking and profile patterns | Store, library, game detail, download, matchmaking, lobby, profile, achievements |
| `crypto` | Exchange and wallet tours | Portfolio, asset, buy/sell, send/receive, transactions, staking, KYC, security |
| `email-calendar` | Gmail/Outlook and calendar product tours | Inbox, compose, message, labels, contacts, calendar, event, tasks, search |

---

## Limits

1. **Prevalence is an estimate.** No claim of statistical validity. Bands are deliberately wide.
2. **Public surfaces skew the sample.** Internal admin tools are under-represented because they
   are rarely documented publicly; admin rows are marked lower confidence.
3. **Disciplines are not silos.** Real products blend families (health marketplace, fintech CRM,
   education marketplace). Take the union, then prune by role and evidence.
4. **The catalog is not exhaustive.** A missing row means "not surveyed", never "does not exist".
   Add new rows when a real product reveals a pattern worth remembering.
5. **Regulation varies.** `regulation` rows indicate a common obligation, not legal advice. The
   project's jurisdiction and counsel decide.

---

## Extending the catalog

When a project reveals a screen the catalog lacks:

1. Add a row with the discipline, category, names, route, kind, estimated prevalence, tier,
   basis, confidence, alternate names and a short note.
2. Cite the product or document in this file under the discipline.
3. Keep the tier consistent with the band table.
4. Prefer a new discipline over stretching an existing one beyond recognition.

The catalog grows by evidence. Do not add a row because it "feels standard".
