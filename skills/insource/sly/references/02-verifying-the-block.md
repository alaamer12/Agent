# Verifying the block - and never repeating it

A block has to be **proven** before it is allowed to shape the architecture. "It didn't work" is an
observation about one attempt, not a fact about the system. Confirm first; hunt second.

## The false-block catalog

Work this list before accepting that anything is impossible. Each row is a real cause of a reported
"not supported".

| Symptom | Usual real cause | How to check |
|---|---|---|
| 404 / unknown route | wrong version, path prefix, or environment (sandbox vs prod) | read the actual spec or OpenAPI/IDL, not the quickstart |
| 401 / 403 | missing scope, entitlement, seat role, or region gate | compare token scopes to the docs; try the same call as another entitled user *with their consent* |
| Field absent from a response | it lives in a different endpoint, a `expand`/`fields` param, or a detail call | enumerate related endpoints and params; request the object with field selectors |
| SDK "has no method for it" | the SDK lags the API surface | call the transport directly; check the API reference for the raw operation |
| Feature appears missing | behind a flag, plan tier, beta header, or org setting | search the docs for the exact noun; check admin settings and changelog |
| Rate limit hit | burst shape, not capability | back off, batch, or move to bulk/export routes |
| CORS / browser refused | server-side job mistakenly attempted in the browser | move the call across the boundary (reshape) |
| Library can't do X | wrong API level; X exists one layer down | read the source or type defs for the lower-level surface |
| Format unreadable | container is fine, codec/version is not | inspect headers/magic bytes and the actual encoding params |
| "Legal said no" | restriction on *use*, not on *existence* | separate what is prohibited from what is merely unlicensed |
| Timeout / flaky failure | capacity, payload size, or pagination | retry with smaller pages, longer deadline, partial fetch |
| Data looks empty | wrong time window, locale, or filters | fetch a known-good record and diff the parameters |

## Proof of a block

Write it as a claim with evidence, in the terms the project already uses for "verified":

```text
BLOCKED : no programmatic way to list a user's saved playlists for third-party apps
EVIDENCE: API reference lists only [create] [modify] [delete] under playlists; no read operation;
          the public profile page shows playlists as HTML with no backing JSON call;
          support answer 2024-11 says reads are not exposed.
CONFIDENCE: high (primary docs + observed page behavior agree)
```

Three independent signals make a block credible; one failed attempt does not. Record the source of each
signal so a later reader can re-check it - blocks go stale when a provider ships the missing operation, and
a stale block silently keeps a workaround alive forever.

## The failure ledger

Do not re-attempt a blocked method with cosmetic variations. That is the difference between persistence and
loops. Keep a ledger for the current task:

```text
ATTEMPT  | target            | signature                        | result      | tried
---------+-------------------+----------------------------------+-------------+--------
1        | playlists API     | GET /v1/playlists?user=me        | 404         | 09:14
2        | playlists API     | GET /v1/playlists?user=me&raw=1  | 404         | 09:16  <- same method, noise changed
3        | profile page JSON | in-page fetch discovered         | HTML only   | 09:20
```

A row is a *repeat* when the target and the mechanism are unchanged and only the surface parameters moved.
`scripts/routes.py` flags these. Two strikes on the same method means stop testing it and go generate a
route from a different family.

## Blocks that are actually assumptions

Ask, out loud: *what did I assume about this system that I never checked?* Common invisible assumptions:

- the data must come from this service, at this moment, in this format;
- the user must be logged in for the value to be meaningful;
- one system is the only writer of the value;
- the feature must be automatic (a manual or scheduled path was never offered);
- the limit is on capability when it is actually on volume, price, or your own configuration.

Half of confirmed blocks survive this list. The other half were never blocks at all.
