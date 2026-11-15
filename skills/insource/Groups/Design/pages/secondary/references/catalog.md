# The catalog - every secondary document, by family

The complete list a running agent shows the user, filtered by evidence. **"Page" is shorthand for a
document** - each may live as a [web] route, a [desktop]/[mobile] app surface, or an embedded view;
shared contracts get ONE canon (usually web), other platforms redirect or embed. Each type has its
own reference file. The `Needs it?` column is the over-engineering filter: if the project does not
do the thing, the document stays out - and the report says so.

## The scale gate - recommend inside the evidence, never above it

Type and scale are the filter before any row is suggested. The trigger is the *activity* (selling
goods, processing others' data, hosting content, running a promotion, crossing a revenue
threshold) - never "good sites have these." Proposing a DPA to a solo consumer app, or a refund
policy to a site that earns nothing, is this mode's failure pattern: the document asserts a
reality the project doesn't have.

| Project state | Documents that grow in |
|---|---|
| **Solo / hobby / static** | a real Contact + About line; Privacy one honest page **only if** any tracker/data touches; footer disclaimer paragraph; cookie doc if any non-essential storage - nothing else |
| **Small commercial (earns, accounts)** | + Terms of Service, full Privacy, Cookie (if web trackers), Delete-account, Unsubscribe (if mail), Refund (if paid) - skip DPA, sub-processors, transparency, ESG |
| **Subscription or auto-renewal** | + Cancellation/Withdrawal (self-serve route, not an inbox) - the enforcement-hot document for this tier |
| **Physical goods own-site** | + Terms of Sale, Shipping; Warranty/RMA only if actually warranting |
| **EU users present** | + Legal notice posture (DE etc.), withdrawal/14-day content, accessibility statement (EAA since Jun 2025 for consumer services), GDPR-shaped rights |
| **US users present** | + per-state threshold check (`us-state-privacy.md`) before ANY state artifact is proposed; RI's notice duty is the only near-universal one |
| **Selling to businesses (B2B/EU procurement)** | + DPA, Sub-processor list, Security page becomes due-diligence surface |
| **Hosting user content at scale** | + AUP, Community, Take-down (DSA mechanics), Transparency report once past the EU micro/small line |
| **≥ ~£36M / A$100M turnover, listed, or buyer-audited** | + supply-chain statements (`supply-chain-statements.md`) at their own thresholds; supplier code once procurement asks |

When two states stack, the union applies; when the evidence can't place the project, ASK one
question ("who buys, from where, with what data") before shortlisting.

## The phase gate - what is owed now, what waits for its trigger

The scale gate asks *is this the project's reality*; this asks *has the obligation started*. An
obligation begins when its act begins - a signup created a contract, a tracker created consent
duties, a checkout created a withdrawal right. Phase is bound to acts, not to calendar:

| Phase | The test | Documents |
|---|---|---|
| **P0 - launch set** | the act is already running at launch: absence makes today's site contractless, deceptive, or unlawful; every footer link must land on a truthful page TODAY | ToS + Privacy (first user), Cookie (first tracker), Contact, About line, Delete-account (accounts), legal-notice posture (EU) |
| **P1 - transaction gate** | owed when its act ships, not after: the doc and the feature land in the same release | Refund + Cancellation with the first checkout (the pay button is the contract); AUP / Take-down / Community with public UGC; Child privacy where minors can plausibly arrive; Terms of Sale + Shipping with physical dispatch; Accessibility statement for EU consumer services (statutory since Jun 2025) |
| **P2 - trigger-driven** | a named growth event makes it owed; build on the event, never on a date | DPA + Sub-processor list (first EU/B2B deal), US state notices (first crossed state threshold - run the per-state check), Transparency report (past the DSA micro/small line), supply-chain statements (their own revenue gates), Promotions rules (only while a campaign runs), Warranty/RMA (first deliberate warranty) |

**The balance rule:** a deferral must name its trigger and be recorded as an exclusion with that
trigger in `PAGES.md`; an unnamed deferral is debt - users accumulate faster than pages, and
retroactive re-consent/re-acceptance costs what day-one honesty did not. Even a YouTube-clone
scale plan ships P0 before its first real signup and defers DPA to its first enterprise trial:
big ambition does not pull P2 forward.

## Legal core (contracts with the user)

| Type | What it settles | Reference | Needs it? |
|---|---|---|---|
| Terms of Service | the contract: accounts, content, violations, enforcement, termination | `terms-of-service.md` | any product with users |
| Privacy Policy | what data is stored, why, who sees it, how long, user rights | `privacy-policy.md` | anything that touches personal data |
| Cookie / Tracking Policy | every non-essential tracker, named, with consent state | `cookie-policy.md` | web surfaces with anything beyond strictly-necessary cookies |
| US State Privacy Notices | notice-at-collection, opt-out page, GPC — the artifacts around the policy | `us-state-privacy.md` | only when the state thresholds are actually met (per-state check in the doc) |
| Acceptable Use Policy | what counts as a violation + the enforcement ladder it leads to | `acceptable-use.md` | products with accounts or UGC |
| Legal Notice / Impressum | WHO the operator legally is: entity, registration, address | `legal-notice.md` | mandatory in some jurisdictions (DE/EU); good anywhere |
| Data Processing Agreement | controller↔processor terms for business customers | `dpa.md` | B2B/data-processor products only — never for consumer-only |
| Sub-processor List | the named third parties + change-notice rights (Art. 28(2) made visible) | `subprocessors.md` | once EU business customers / procurement exist; a DPA annex below that line |
| Child Privacy / Age Assurance | age policy, the assurance method, what changes under the threshold | `child-privacy.md` | children can plausibly arrive, or store categories/UK-OSA-type law demands it; otherwise one statement line |
| Take-down / Abuse | how to report infringing/abusive content + counter-notice (+ DSA mechanics) | `takedown.md` | anything hosting user content |
| Refund Policy | windows, conditions, process — the money after the exit | `refund-policy.md` | paid products |
| Cancellation / Withdrawal | how to get OUT: the right, the working button, the confirmation | `cancellation-withdrawal.md` | any subscription/auto-renewal; EU/UK consumer sales; else a section in refund |
| Terms of Sale | per-order contract: acceptance trigger, price-error, delivery, risk | `terms-of-sale.md` | own-site sales of goods / one-time digital purchases |
| Warranty / RMA | the express promise + the claim path | `warranty-rma.md` | only those who warrant or produce own-brand goods |
| Shipping Policy | methods, lead vs delivery times, zones, customs | `shipping-policy.md` | physical goods ONLY |
| EULA / Software License | the grant for installed software | `eula.md` | direct-distributed desktop/on-prem/SDK only — store-only apps don't need one |
| Disclaimers | what the content ISN'T: advice, warranty, relationship, human | `disclaimer.md` | advice-adjacent content or licensed professions; else a footer paragraph |

## Trust & safety (proving the product is honest)

| Type | What it settles | Reference | Needs it? |
|---|---|---|---|
| Security / Vulnerability Disclosure | how researchers report, safe harbor, response times (+ `security.txt`, RFC 9116) | `security.md` | every shipped product |
| Status | is it up now, incident history, subscriptions | `status.md` | hosted services |
| Accessibility Statement | conformance target, known gaps, feedback channel | `accessibility.md` | strongly: public-facing; REQUIRED for consumer e-commerce/banking/etc under the EU EAA since Jun 2025 |
| Transparency Report | removal/handover counts, moderation stats | `transparency-report.md` | hosting platforms above the DSA micro/small line; below it, "How we handle requests" or nothing |
| Community Guidelines | behavioral norms in human voice (the friendly face of the AUP) | `community-guidelines.md` | products where people interact |
| Anti-fraud / Official Channels | the ONLY domains/accounts; impersonation warning | `anti-fraud.md` | money-adjacent or regionally popular apps |

## Commerce & marketing documents

| Type | Reference | Needs it? |
|---|---|---|
| Affiliate / Endorsement Disclosure | `affiliate-disclosure.md` | affiliate income, gifted product, or influencer programs - any of them; per-post disclosure stays the operative act |
| Promotions & Sweepstakes Rules | `promotions-rules.md` | only while a prize promotion runs; nothing for plain discounts |

## Corporate & scale-triggered statements

| Type | Reference | Needs it? |
|---|---|---|
| Supply-chain & corporate statements (modern slavery, supplier code, ESG, conflict minerals) | `supply-chain-statements.md` | revenue/listing/buyer-audit thresholds ONLY - see the gate table below; premature publication is theatre |

## Contact & company (reaching the humans)

| Type | Reference | Needs it? |
|---|---|---|
| Contact | `contact.md` | yes - some laws demand a human route |
| About | `about.md` | yes - thin and honest beats missing |
| FAQ | `faq.md` | when real questions exist (support volume) |
| Support / Help | `support.md` | products with accounts/complexity |
| Careers | `careers.md` | only if hiring; a "no openings" line otherwise |
| Press / Media Kit | `press.md` | only when real assets exist - never fabricated |

## Lifecycle & utility

| Type | Reference | Needs it? |
|---|---|---|
| Delete Account | `delete-account.md` | any product with accounts (some stores REQUIRE the in-app route) |
| Data Rights Requests (export/access/rectify) | `data-rights.md` | where privacy law gives the rights |
| Unsubscribe / Email Preferences | `unsubscribe.md` | any product sending non-transactional mail |
| Changelog / Release Notes | `changelog.md` | shipping products (section-20's attachment in agents-md terms) |
| HTML Sitemap | cataloged, no reference: small-site accessibility aid; skip on large sites | rarely |
| Error / Maintenance pages | cataloged, no reference: a line in `engineering.md`'s spirit - honest, on-brand, with a status link | any web surface |
| AI Usage Policy | cataloged, no reference: ask the user's actual stance before writing any | only if AI touches the product |

## Who owns which fact

One owner per cross-cutting fact; every other document LINKS, never restates (the mechanism is
`../../references/output-contract.md`). When drafting any document, facts in its row are
gathered from the user/config once and referenced forever after:

| fact | canonical owner |
|---|---|
| data classes, retention periods, legal bases | Privacy Policy |
| US notice-at-collection / opt-out / GPC mechanics | US State Privacy Notices doc |
| what counts as a violation | Acceptable Use |
| enforcement consequences | ToS (ladder) + AUP (list) — stated once between them |
| refund windows and stance | Refund Policy |
| cancel/withdrawal mechanics, the exit button | Cancellation/Withdrawal |
| per-order acceptance, price-error, delivery, risk | Terms of Sale |
| warranty promise, RMA steps | Warranty/RMA |
| shipping terms | Shipping Policy |
| governing law, venue | ToS (purchase precedence: ToS → Terms of Sale → confirmation) |
| operator identity, registration, address | Legal notice / About (config-sourced) |
| subprocessor identities and change notice | Sub-processor List |
| material-connection policy | Affiliate Disclosure |
| prize terms | Promotions Rules |
| availability promises, incident history | Status |
| security response and disclosure | Security |
| contact routes and hours | Contact |
| deletion mechanics and timelines | Delete-account |
| moderation/handover statistics | Transparency Report |

## How to present this to the user (the ask)

## The ask — three buckets, one round

(The question law is `method.md`'s; this section owns the *format*.) Never dump the table.
From the repo evidence, place the project in the scale gate first, then
phase-gate the survivors, then ask in three buckets - launch set (why now), deferred-with-trigger
(the named event), not-applicable (why the act does not exist). Skips carry reasons; deferrals
carry triggers; there is no "later" bucket. Example:

```text
Evidence says: web + desktop app, accounts, paid subscription, UGC, EU + US users.
Launch now (P0/P1 - these acts ship with you): ToS, Privacy, Cookies, AUP, Community, Take-down,
  Refund + Cancellation (checkout launches = both launch), Delete-account, Contact, About,
  Security, Status, Accessibility (EAA), Legal-notice posture, Unsubscribe, Changelog.
Defer with trigger (P2): DPA + Sub-processors → first EU/B2B deal; US-state notices → first
  crossed state threshold (run the check, not a feeling); Transparency report → past DSA
  micro/small line; Press/Careers → real assets / real hiring; EULA → only if the desktop
  build ships outside stores (it does → that is a trigger you already passed).
Not applicable: Shipping, Terms of Sale, Warranty (no physical goods).
Which of these do you want created?
```
