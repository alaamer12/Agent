# Contact

The human route - and in some jurisdictions a legal requirement (the Impressum's fastest-contact
line usually points here). The one page where "we care about feedback" must be mechanically true:
every channel listed is a channel someone actually reads.

## Must include

1. **The routes, separated by intent** - support (product help), privacy requests (owned by
   `data-rights.md`, linked), legal/takedown (`takedown.md`), press (`press.md`, only if real),
   security (`security.md` channel). One form with a topic selector beats five exposed addresses;
   it also kills the support email's spam inbox.
2. **The response promise** - first-reply window per route, real numbers ("support within 2
   business days"); a page that promises nothing reads as unmonitored. ASK for each route.
3. **What we need in the message** - the one line that makes support faster (account id?
   screenshot? device?) - copied from the product's actual triage.
4. **Hours/language coverage** - "we answer in [ar/en] Mon-Sat" or the honest
   "best-effort outside business hours"; only if true.
5. **Escalation** - where a unanswered ticket goes (a second address or "reply with the same
   subject and mark escalation") - only with a real owner.

## Engineering binds

- Every address/phone/agent value from config (the user's exact named case: **contact information
  is never hardcoded**) - a phone number edited by the operator must never need a code change
  across the app's surfaces; the same config renders the form's fallback, the mail template, and
  this page.
- A form without a backend is a lie: if there is no submission handler, use a `mailto:` or the
  config-rendered address and say what happens when it is used.
- Raw emails on a web canon: obfuscate or form-wrap against scrapers.

## Ask the user - never invent

Each route's real owner and window; whether the form exists and where it sends; hours; language
coverage; escalation; the config values.

## Failure patterns

`support@example.com` survived from a template (grep for placeholder domains before publishing);
five channels all pointing to one unmonitored mailbox; a response promise the team breaks weekly -
each broken promise on this page teaches users the documents are decoration.
