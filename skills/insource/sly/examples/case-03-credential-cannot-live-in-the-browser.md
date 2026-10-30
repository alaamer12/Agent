# Case 3 - the credential cannot live in the browser

**The ask:** "call the paid translation API straight from the SPA so translations appear as I type."

## Goal, separated

```text
GOAL  : typed text turns into a translation quickly enough that reading keeps flowing
VALUE : the translated string, in about the time it takes to read a paragraph
TEST  : median time from paste to visible translation, and cost per active user per day
```

Nothing in the goal says "the browser holds the secret" - that was the method, and it is the part that must
go.

## The block, correctly diagnosed

This is not a capability block and not a parity problem. Translating on behalf of a logged-in user is
exactly what an ordinary user does. The blocker is the **security axis**: a billable key shipped in client
code is readable by every visitor, which means their quota, their bill, and someone else's abuse of it.

Worth naming precisely, because agents get this wrong: putting your own key in public code is not a
*protection bypass* - it is a self-inflicted credential leak. The hard line about credentials is about using
someone else's; this route fails on security scoring instead.

## Routes

| Route | Family | Score driver |
|---|---|---|
| Our server proxies the call, key stays server-side, per-user limits applied there | reshape | the only route that keeps the goal and the secret |
| Cache translations keyed by normalized source hash, so repeats cost nothing | reshape | pairs with the proxy; kills most of the volume |
| Debounce per keystroke, translate on pause or by paragraph | reshape | latency feels better, quota stops burning |
| Provider with a client-safe, quota-managed pricing model | replace | real option, scores worse on cost at our volume |
| Ship only the languages we can pre-translate offline | reduce | fallback if budget is refused |
| Extract the key from another product's public bundle and use it | rejected | not yours, and that is the line |

## Chosen

Proxy plus hash cache plus debounce. Untranslated text stays visible with a quiet "not translated" indicator
rather than a spinner that never ends - unknown renders as unknown.

## Said out loud

Offline translation was cut, and that is stated in the record rather than discovered by a user on a train.
