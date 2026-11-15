# Privacy Policy

The data truth: what is stored, why, who sees it, for how long, and how a person acts on it.
The reference example of transparency the user named - this document earns or loses trust.

## Must include, in this order

1. **Who you are + how to reach the privacy contact** - entity from config; a real channel; the
   **EU representative** (Art. 27, non-EU sellers to EU users) and DPO contact where one exists.
2. **Plain-language summary at the top** - 4-6 lines answering: what do you collect, why, do you
   sell it, who hosts it, what can I do about it. The rest is the detail. Layered form: summary
   first, per-class tables under it.
3. **Data collected, grouped by source** - a table per group: what you give us (account, content,
   messages); what we record (usage events, logs, crash reports); what we get from others (OAuth
   providers, payment processors). For EACH class: the PURPOSE tied to it - collection without a
   stated purpose is the classic failure. **AI training gets its own line**: whether interactions
   or content train models, on what basis, and how to object - hiding it inside "improve our
   services" is the 2025-26 regulator's favorite finding.
4. **Legal bases** [GDPR-shaped] or **category↔purpose disclosure** [CCPA-shaped] - which frame
   fits depends on the users the project actually has: ASK, don't guess jurisdictions. US in-scope
   reach adds the state-notice artifacts (`us-state-privacy.md`) around this page - the policy
   hosts the state-rights section, the Notice-at-Collection and opt-out pages are separate
   documents.
5. **Sharing** - the named list: processors (hosting, email, payments, analytics), "we do not sell
   or share personal data" ONLY if literally true with the trackers off to match (CalPrivacy's
   FedEx fine, Nov 2026: that sentence plus running ad trackers and a broken GPC path);
   law-enforcement path and policy.
6. **Retention** - explicit period or explicit rule per data class ("deleted within N days of
   account deletion"; "billing records kept N years because law says"). This is the most often
   invented number in all secondary documents - it comes from the user or nothing.
7. **Cookies and trackers** - the summary line; the per-cookie table lives in `cookie-policy.md`.
8. **Rights + how to exercise** - access/export/rectify/delete/object/portability per the actual
   law set; the mechanism is `data-rights.md`; state the real response time; cloud-switching and
   portability duties where the EU Data Act applies (from 12 Sep 2025).
9. **Children** - one accurate line, pointer to `child-privacy.md` if the full page exists.
10. **Transfers** - where data physically lives; the mechanism if cross-border (SCC/adequacy/DPF,
    as `dpa.md` names them - one owner).
11. **Other jurisdictions in scope** - India DPDP (staged: notice/consent duties, consent-
    managers from Nov 2026, grievance route), Brazil LGPD/ANPD, etc. - only the ones the users
    actually come from (ASK); each gets a short named section, not a boilerplate globe.
12. **Changes** - dated header; material-change notice channel. Draft to enacted law: the EU
    Digital Omnibus (Nov 2025) is a **proposal** - useful to know, not something to write pages
    against.

## Writing professionally

- Name the vendors or name the category honestly ("a hosting provider in the EU"); vague "trusted
  partners" is the phrase researchers cite as the opacity marker.
- Verbs over nouns: "we store your email to sign you in", not "email address data storage
  functionality".
- One fact, one owner: the ToS, FAQ, and app copy all LINK here for data answers.
- If the project does not collect something, say so ("we do not track you across other sites") -
  truthful absence is a feature and belongs only if true.

## Ask the user - never invent

Every data class actually collected (verify against the repo's schemas and analytics calls, then
confirm); retention numbers; vendors; jurisdiction frame; privacy contact; the sell/no-sell
literal truth; hosting region.

## Failure patterns

A generic template listing analytics features the product lacks (over-disclosure is still a
false statement); retention "as long as necessary" everywhere; rights described with no mechanism;
a "last updated" date older than the code it describes; "we don't sell or share" next to live ad
trackers; AI-training folded into "improve our services"; drafting pages against proposed law as
if in force.

*Not legal advice: the goal is that a reader can verify every claim against the product; counsel
checks enforceability.*
