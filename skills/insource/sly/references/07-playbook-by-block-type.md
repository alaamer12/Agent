# Playbook by block type

Recipes, keyed to what is actually blocking. Options in each row are illustrative - the right answer may be
a hybrid or something unlisted. Every candidate route still passes [`04`](04-access-parity.md).

---

## "There is no endpoint for it"

| Try | Family |
|---|---|
| Another version, region, or environment of the same API | reroute |
| Bulk export, report download, or scheduled dump instead of per-item reads | reroute |
| Outbound events: webhook, event bus, notification stream you then consume | reroute |
| The public page or feed the product itself renders (RSS/Atom, sitemap, public JSON) | reroute |
| A connector in software you already run: spreadsheet, BI tool, notebook, CLI, plugin | reroute |
| Different provider, or self-hosted open equivalent | replace |
| Derive the value from data you already hold | rebuild-from-pattern |
| Precompute the answer; move the requirement off the live path | reshape |

## "The SDK doesn't expose it"

SDKs lag APIs far more often than APIs lack features. Check the raw service reference for the operation;
call the transport directly behind a thin client so the SDK can catch up later without rewriting callers.
Also check: a beta flag, a newer package version, an "execute raw"/generic-call escape hatch, a lower-level
client one layer down, or the vendor's CLI - which usually wraps the complete surface.

## "The framework/language can't do it"

Almost always a boundary error rather than a capability error:

- Browser sandbox (CORS, storage, filesystem, background work) - move it server-side, or into a worker, an
  extension, a service, or an installed native layer.
- Serverless or platform limits (time, memory, payload, no local disk, no outbound ports) - split the job,
  stream it, push it to a queue, or run the heavy part where heavy things run.
- Mobile OS restrictions (background execution, notification, sensors, app-switching) - use the sanctioned
  pattern for that need; when the need itself can change shape, change it.
- Library API too coarse - go one layer down (the driver, the parser, the codec, the socket) rather than
  forking the library.
- Version conflict between two dependencies - isolate by process, by adapter, or by dropping one
  dependency and replacing its narrow use with code you own.

## "The feature is behind a plan, tier, or entitlement"

First: is it *purchasable*? Then the honest routes are [buy it] [ask the owner to enable it] [use the
lower-tier-compatible subset] [replace it with something you control]. Cracking an entitlement check is a
payment wall, and payment walls are access control working as intended - not a route. If the tier is not
affordable, **Reduce** to the valuable subset and say what was cut, or **Replace** with a component whose
pricing fits.

## "Rate limited / too slow at our volume"

Distinguish protection from capacity. Protection-shaped limits (anti-scraping, abuse controls) are not to be
circumvented - that line is in [`04`](04-access-parity.md). Capacity-shaped limits are an engineering
problem: batch endpoints, field selection to shrink payloads, caching and request coalescing, scheduled
pulls instead of fan-out, ETags and conditional fetches, a queue with backoff, or asking for a higher quota.
Volume you would not defend as "a person using the product" is the wrong shape of route.

## "The file/format/protocol is closed"

Characterize before you parse: magic bytes, envelope, framing, version variants, then field semantics from
any file the user legitimately possesses. Look up the spec, an open implementation, or a standards draft
first - published material beats archaeology. Record unknown fields instead of guessing them, and test
against a golden corpus the user owns.

## "We need behavior we can see but not call"

This is [`03`](03-pattern-extraction.md): source ladder, characterize inputs/outputs/structure/timing/edge
cases, fit your own version, validate on held-out cases, report agreement honestly. Keep observation at
ordinary-user scale and infer the *principle*; do not bulk-collect outputs to imitate a system wholesale.

## "The data we need doesn't exist anywhere we can reach"

Ask where the value could be manufactured rather than fetched: derive from adjacent signals you do have,
infer from aggregate or public statistics, collect it yourself going forward (an event you start logging
today is a model you can train in six weeks), ask the user to supply it once, or generate a synthetic
stand-in **labelled as such and never presented as real**.

## "It requires a human in another system"

Bridge instead of bypass: an adapter that consumes the human's normal output (export file, email, printed
report photographed by OCR), or a scheduled manual step that is honest about being manual. Automating
someone else's account is not a bridge.

## "The blocker is cost"

Score it as an axis rather than treating it as a wall: [cheaper provider] [self-hosted] [smaller model]
[less frequent refresh] [narrower feature] [cache longer] [compute only for active users]. Reduce is a
first-class family for exactly this case.
