# Relay redirects — the pages designed not to be seen

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** a return path landed on by machinery, not by navigation — the OAuth/SSO
callback, the payment provider's return URL, the post-logout landing, a token-scoped
forward. The person passes through it in under a second, if they notice it at all; its
purpose is to be the *last place secrets are allowed to exist* before the flow is handed to a
page that renders them useless.

**Why it is in this family though nobody "sees" it:** it is conditionally landed on (only the
return-path hits it), absent from normal navigation absolutely, and the *visible surface* is
dispensable — the endpoint itself is flow machinery, which is the one honest deviation from
the boundary test's question 2: the route exists because security says it must; the page's
*content* is what must stay empty. It is a complementary page whose correct design measures
zero seconds of attention.

## The reason blank is the feature

Security handoffs are where URL-borne secrets (codes, tokens, state, PII echoes) arrive in
places that get logged, referrer-leaked, extension-read, and crash-rendered. The page's job:

1. **Validate before anything else** — `state`/nonce checked server-side (mismatch ends the
   flow *here*, as an honest error, not a forward); the token/action redeemed by a POST or
   server-side exchange, never left in a location the DOM can show.
2. **Forward only to allowlisted targets** — the destination is chosen from a server-known
   set. A `?next=/whatever` or provider-supplied redirect URL is **accepted as an identifier
   to look up, never as a URL to visit**: this is the open-redirect vulnerability in its
   native habitat, and the blank page is the layer that catches it.
3. **Render nothing that could leak** — no app shell, no analytics (they beacon the URL —
   which is the secret), no console logging of params, no error strings quoting the token.
   `Referrer-Policy: no-referrer` + `rel="noopener noreferrer"` on the one manual link (below);
   static empty HTML body, framework-free — a crash here must have nothing to show.
4. **Never strand anyone** — JS-less or blocked-forward case needs a manual continue link that
   appears *after* validation and points only at the allowlisted target; or, when even that is
   unsafe (logout relays), honest one-line copy: "done — return to the app from where you
   closed this tab." The no-dead-ends law still applies, in the most minimal form a page can
   take.

## Laws specific to this family

- **Content Security Policy: the page's only content.** The correct audit finding count for a
  relay is: zero text nodes with data, zero scripts beyond the forward, one hidden form or
  meta refresh or 200-with-JS only when the provider contract forces GET-200 instead of a 302.
  When the server *can* answer with a real redirect, it should — the page exists for the cases
  where protocol or provider demands an origin-rendered landing.
- **Exchanges belong to `token-handoff`/`session-gates`** — the relay *moves*; it does not
  redeem-then-celebrate. The seam: relay = validated hand, never the acknowledged moment.
- **Logging discipline** — log the event (source origin, outcome, correlation id) with the
  secret fields **proven dropped**, not redacted-in-place; a relay log line containing a raw
  code turns an invisible page into an invisible breach.
- **Return-URL honesty with providers** — registered return URLs must be exactly these relay
  routes; a provider return pointing straight at a rendering page (dashboard, success) means
  the secret arrived where content lives, and this family's whole premise is violated at the
  integration, not the code.

## Anti-patterns

The `?redirect=` free-pass (open redirect — this family's namesake crime); showing a spinner
skeleton for 2s "while it works" (the wait is the attack window for DOM token scraping —
blank and instant is *safer* than polished); forwarding without state validation because the
provider "always returns it"; logging full URLs at info level; a relay page that 500s to a
framework error screen quoting the query string; using it to sneak analytics/firepixl beacons
in "while the user is in transit".