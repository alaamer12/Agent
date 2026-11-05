# Presentation - canon location and how each surface reaches it

Two separate decisions: **where the document canonically lives** (one answer per contract, shared
across platforms) and **how each surface shows it** (per page type, per placement mode).

## Canon location first

| Project shape | The canon | Other surfaces |
|---|---|---|
| Web + [desktop]/[mobile]/[embedded] sharing the same business contracts | the **web route** (single URL per document) | open in system browser / deep link out (redirect); or embed (webview) when the user must stay in-app |
| App-only products (no web surface) | an explicit chosen home: a docs host, the store listing, or the bundled content file - NAMED in the report | every mention links/points to that one home |
| CLI / library | repository file + a published URL (docs page) | `--license`/docs commands print the URL, not a forked copy |

**Why web-by-default:** one URL is citable in the other documents, courts, app-store review forms,
and support replies; it updates without a store release; search finds it. **The one rule:** no
platform may carry its own version of shared contract text. A bundled offline copy (flight mode,
air-gapped desktop) is legal only as a DECLARED synced duplicate - its source is the canon, the
sync is stated in the file header, and regenerating it is part of editing the canon.

## Placement shapes on a web surface - examples, not a menu

The modes below are how documents usually get delivered, not the allowed set: a project may pick
a hybrid or invent its own shape. What is invariant is not the widget but what the reader gets:
the FULL current text reachable in one step, a stable URL for the canon, and consent gating the
whole document rather than an excerpt.

| Mode | Good for | The contract with the reader |
|---|---|---|
| **Standalone route** (`/terms`, `/privacy`) | every legal document - the default and the canon | complete, indexable, permanent URL, footer-linked |
| **Signup/login inline** | ToS + Privacy at the consent moment | one summary sentence + explicit links to the full documents ("By creating an account you agree to the Terms..."); never a wall of legalese in the form |
| **Modal** | showing the document WITHOUT leaving context (in-app "view terms" during signup) | the modal shows the FULL text (or embeds the canon); truncating inside a modal while claiming consent is the dishonest shape |
| **New tab** | links from app surfaces / emails to the web canon | keeps the user's app state; the destination is still the canon URL |
| **Accordion** | FAQ only | each answer one screen max, links own the details; never an accordion for ToS (a contract you must click apart is a contract you cannot read) |
| **Footer block** | the index of all of it: Terms · Privacy · Cookies · Contact · Status · Legal notice | present on every page of the web surface; the machine-readable way to find the canon set |
| **Settings surface (app)** | delete-account, subscriptions, notification preferences | the store-mandated in-app route for deletion is a real surface, not a link out - but the POLICY text behind it is the canon |

## Rules that bind every mode

- **Never split the truth:** the modal/accordion carries pointers, the document carries the fact
  (one owner per fact).
- **Consent needs the real text:** where acceptance gates an action (signup, first paid feature),
  the linked/expanded document must be the full current canon - an excerpt is not a contract.
- **Reachable without JS** in every web mode (the content exists in the first packet; accordions
  must render their content in the DOM, not fetch it).
- **Stable URLs:** document slugs are permanent; renames keep a redirect (a cited URL that 404s is
  a broken promise the user may be legally relying on).
- **Locales:** each language version is the same MEANING; the legal-text pairing (which language
  wins) is a question for the user, never a silent default.
