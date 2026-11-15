# Worked example — after payment

A filled-in anatomy sheet set for one flow, as `anatomy.md` requires before design. The
product: a subscription app with card + wallet payments, provider redirects back to
`/payments/return`, an `automatic_retry`/`manual_retry` pair already owned in the project's
contracts. Two pages recorded; the third row is an exclusion, because exclusions are decisions
too.

## Payment Success — family: transaction-success

- **Trigger:** provider redirected to return URL **and** `GET /orders/{id}/status` answers
  `settled` at render.
- **Condition source:** order status endpoint (server truth). The return URL's `?status=success`
  is treated as a request to verify, never as the answer.
- **States handled:** fresh in-flow (verify → show proof) · replayed/double-click (idempotent:
  same answer, zero re-capture) · bookmarked next month (status still says settled — shows
  normally, copy stays in past tense) · logged out deep-link → `session-gates` resume → back
  here.
- **Exits:** View receipt (PDF) · Manage subscription · Home. No continuation re-asks for money.
- **Proof block:** order id, amount, method tail 4242, timestamp local+UTC, receipt email +
  address shown.
- **Celebration:** first subscription only; after proof block; dismissible; reduced-motion:
  static.
- **Status:** confirmed with billing owner.

## Payment Failed — family: transaction-failure

- **Trigger:** status endpoint answers `declined|failed` — **or** `unknown` after provider
  timeout, which routes to the pending variant below, not this page's failure copy.
- **Condition source:** same endpoint + provider webhook state; re-checked on render.
- **States handled:** in-flow · replay after fix-and-retry succeeded (shows the *new* state,
  never a stale decline) · bookmarked (re-check; if since settled, this page cannot lie — it
  forwards to success).
- **Exits:** retry per contract (**manual only** — `automatic_retry` exhausted, policy says
  declines are not auto-retried; the button re-issues the attempt with a *fresh* method form,
  no card pre-fill) · change method · "nothing was charged" line shown **only when the status
  endpoint confirms no capture** · Support (order id printed) · Home, cart kept.
- **Cause copy:** human sentence + raw code in a `<details>` for support.
- **Status:** confirmed with payments owner.

## Provider Timeout (pending) — recorded as its own anatomy row

- **Trigger:** status `unknown` and provider webhook not yet settled after N seconds.
- **Behavior:** neither success nor failure graphics; "we could not confirm — checking your
  bank side before asking you to retry"; auto-re-poll the status endpoint (a *read*, permitted;
  it is not an auto-retry of the *action*); manual "check again" affordance.
- **Why a third record:** `transaction-failure.md` names the unknown middle a first-class
  state; splitting it here is what stops an agent next month from collapsing the three screens
  into two and lying about money.
- **Status:** inferred → confirmed with payments owner on the poll ceiling.

## Excluded — "Cancel Confirmation" page

- **Decision:** excluded. Provider cancel returns hit the same return URL with `aborted`;
  `transaction-failure`'s pending-vs-failed anatomy already answers it with a
  "you cancelled, nothing charged (confirmed)" state row. A dedicated page would be a fourth
  exit nobody chose, and dead-end law prefers one failure surface that owns all its states.
- **Status:** excluded (reason above) — recorded so nobody re-invents it.