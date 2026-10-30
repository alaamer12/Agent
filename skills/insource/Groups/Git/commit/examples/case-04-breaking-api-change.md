# Case 4 - a breaking change that a stranger can migrate from

**Situation:** the public search endpoint stops returning an array and returns an object. This breaks two
internal consumers and every third-party client.

The job of this commit message is to let someone **without access to you** upgrade without guessing.

## The message

```text
feat(search)!: return { items, suggestions } instead of a bare array

Callers needed suggestions and results in one round trip; returning two arrays
would have doubled the payload for the common case where suggestions are
ignored. The shape now names both.

Migration: read `.items`. A query flag `?compat=1` returns the old array shape
and is supported until 2026-01-15, which covers the two known third-party
integrations. The mobile client is updated in the same release, so no in-house
consumer needs the flag.

Measured: p50 response size grew 3.1 kB (gzip) because suggestions are now
always computed; a follow-up will make them opt-in when the client does not ask.

BREAKING CHANGE: GET /api/search responses are objects with { items, suggestions }
rather than a bare array. Clients must read .items, or pass ?compat=1 until
2026-01-15.

Refs #4970
```

## Why each piece

| Piece | Reason |
|---|---|
| `!` before the colon | release tooling reads it and cuts a major version; a changelog section is generated from it |
| `BREAKING CHANGE:` footer, exact and imperative | the machine-readable statement of what breaks - it belongs in the generated release notes, so it has to stand alone without the body |
| body paragraph 2 = migration path with a deadline | the reader's actual question is "what do I have to change, and for how long is the grace period" |
| who is affected and what is already handled | prevents the panic comment on the release issue |
| measured size delta, honestly labeled | a "no impact" claim nobody verified is worse than an inconvenient number |
| follow-up named but not committed | the caveat is visible without smuggling the next change into this commit |

Both spellings appear (`!` and the footer) deliberately: different tools read different ones
([`05`](../references/05-trailers-and-footers.md)).

## The staging discipline that belongs with a breaking change

```bash
git add src/search/handler.ts src/search/response.ts \
        clients/web/src/api.ts clients/mobile/src/api.ts \
        docs/api/search.md
git diff --cached            # confirm the compat flag, its tests, and the docs are all here
```

A breaking change ships with its compat path, its tests, the in-house consumer updates, and the docs **in the
same commit** - otherwise the tree at that commit is broken for anyone bisecting through it, and the
grace-period promise has no implementation to point at.

## What was not written

No "this is a breaking change, sorry!" and no speculation about adoption. If the date of the compat
removal is not decided, the sentence says "until further notice" rather than inventing a deadline that release
notes will then repeat for a year.
