# HTTP & runtime errors

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** a route that does not resolve (404), a server fault (5xx), a resource gone
(410), no connection (offline), or an unhandled runtime crash. Distinct from
transaction-failure: nothing was *done*, so nothing needs undoing or reassurance about money.

**The honest framing:** these pages apologize for the wrong things. The person did not do
anything wrong, and the product should not pretend a 404 is a crisis — it is a dead end, and
the page's job is to hand them back to a working road as fast as possible.

## Per-class copy law

| class | truth the page must tell | exits |
|---|---|---|
| **404** | this address is not part of the app — *their* link may be old, or *ours* may have moved; say both are possible | search, top destinations, home. If we renamed a route, redirect properly first (`/pages main` records redirect-vs-page) |
| **410 / gone** | it existed and is deliberately gone; where it went | one pointer to the successor; then exits above |
| **5xx** | our side is broken *now*; their retry may or may not help; no time promise we cannot keep | retry-this-page, home, status pointer (pages secondary' doc) when the product has one |
| **offline / degraded network** | what they can still see (cached surfaces) and what waits for connection | keep-what-you-have + auto-recheck indicator, not a dead "please check your wifi" lecture |
| **crash boundary** | the app survived them failing; state is kept | reload the view, not "the app", when possible; report-once affordance with a real destination for the report |

## Laws specific to this family

- **Zero leak, always** — stack traces, framework banners, internal paths, other users'
  fragments: never rendered, never in the DOM, never in the page source a crawler sees. The
  human line carries a correlation id *if the logs know that id*; an id pointing at nothing
  is theater.
- **These are the app's most-crawled pages** — correct status codes (a styled 200-OK 404 is a
  SEO wound), no robots-blocking on the error routes themselves, fast to first paint with no
  JS dependency: the 500 page must survive the thing that broke the app. Static render is the
  safe default (`/pages secondary`' light-content law applies here too).
- **No dead ends, no guilt** — exits before explanations; the helpful link list is the page,
  the shrug illustration is garnish.
- **One family, one system** — every error class from the same anatomy sheet and shell, so a
  410 reads like a 404's cousin, not a different product's page.

## Anti-patterns

Emoji-only apologies; the "oops!" brand voice on a 5xx that lost work; 404 pages that are
really ad inventory (link farms to "popular pages" nobody visits); auto-refresh loops on
5xx; treating the offline case as a 404 with worse copy.