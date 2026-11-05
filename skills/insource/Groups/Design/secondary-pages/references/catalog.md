# The catalog - every secondary document, by family

The complete list a running agent shows the user, filtered by evidence. **"Page" is shorthand for a
document** - each may live as a [web] route, a [desktop]/[mobile] app surface, or an embedded view;
shared contracts get ONE canon (usually web), other platforms redirect or embed. Each type has its
own reference file. The `Needs it?` column is the over-engineering filter: if the project does not
do the thing, the document stays out - and the report says so.

## Legal core (contracts with the user)

| Type | What it settles | Reference | Needs it? |
|---|---|---|---|
| Terms of Service | the contract: accounts, content, violations, enforcement, termination | `terms-of-service.md` | any product with users |
| Privacy Policy | what data is stored, why, who sees it, how long, user rights | `privacy-policy.md` | anything that touches personal data |
| Cookie / Tracking Policy | every non-essential tracker, named, with consent state | `cookie-policy.md` | web surfaces with anything beyond strictly-necessary cookies |
| Acceptable Use Policy | what counts as a violation + the enforcement ladder it leads to | `acceptable-use.md` | products with accounts or UGC |
| Legal Notice / Impressum | WHO the operator legally is: entity, registration, address | `legal-notice.md` | mandatory in some jurisdictions (DE/EU); good anywhere |
| Data Processing Agreement | controller↔processor terms for business customers | `dpa.md` | B2B/data-processor products |
| Child Privacy | age policy, what changes under the threshold | `child-privacy.md` | only if minors can plausibly arrive; one statement line otherwise |
| Take-down / Abuse | how to report infringing/abusive content + counter-notice | `takedown.md` | anything hosting user content |
| Refund Policy | windows, conditions, process | `refund-policy.md` | paid products |
| Shipping Policy | methods, lead vs delivery times, zones, customs | `shipping-policy.md` | physical goods ONLY |
| EULA | license terms for installed software | `terms-of-service.md` covers overlap; add per-platform | distributed desktop/mobile apps |

## Trust & safety (proving the product is honest)

| Type | What it settles | Reference | Needs it? |
|---|---|---|---|
| Security / Vulnerability Disclosure | how researchers report, safe harbor, response times (+ `security.txt`, RFC 9116) | `security.md` | every shipped product |
| Status | is it up now, incident history, subscriptions | `status.md` | hosted services |
| Accessibility Statement | conformance target, known gaps, feedback channel | `accessibility.md` | strongly: public-facing; required in some jurisdictions |
| Community Guidelines | behavioral norms in human voice (the friendly face of the AUP) | `community-guidelines.md` | products where people interact |
| Anti-fraud / Official Channels | the ONLY domains/accounts; impersonation warning | `anti-fraud.md` | money-adjacent or regionally popular apps |

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

## How to present this to the user (the ask)

Never dump the table. From the repo evidence, shortlist the plausible rows per family (one line
each, with the `needs it?` verdict), then ask which to create - the rest of the catalog stays as
the pointer list. Example:

```text
Evidence says: web + desktop app, accounts, paid plans, UGC, EU users.
Likely needed: ToS, Privacy, Cookies, AUP, Legal notice (EU), Refund, Security, Status,
Contact, About, Community, Delete-account, Unsubscribe, Changelog.
Skip unless you say otherwise: Shipping (no physical goods), Careers, Press, DPA (not B2B yet).
Which of these do you want created?
```
