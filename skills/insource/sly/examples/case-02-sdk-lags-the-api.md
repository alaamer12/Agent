# Case 2 - "the SDK has no method for it"

**The ask:** "list every record changed since a timestamp."

**Reported block:** "the SDK has no such method." Class initially looked like a blocker; it was a snag
wearing a blocker's clothes, which is why Step 0 exists.

## Verification

The SDK wraps a subset of the service surface. Reading the service reference for the same resource shows a
`modified_since` parameter on the list operation. Two signals: the API reference documents the parameter; the
vendor CLI - which usually wraps the complete surface - has a flag for it. The block dissolves.

## Routes considered before the block dissolved

- **reroute** - call the transport directly through the SDK's generic-call escape hatch. Chosen.
- **replace** - a different client library that exposes the operation. Rejected: inherits the same lag, adds
  a dependency.
- **rebuild** - poll everything and diff locally to synthesize "changed since". Viable but absurdly costly
  once the real parameter exists.
- **reshape** - ask the service to push a changelog into a queue we own. Right answer at 100x the volume, not
  at today's.

## Implementation shape that keeps the win clean

One thin module owns the hand-rolled call, so the SDK can catch up without touching callers; one test
asserts the parameter is actually honored server-side, because a silently ignored filter is the worst
failure mode here - it returns *something*, so nothing looks broken.

## What this case teaches

Verify the block before generating workarounds. Most of the time the door exists and you were knocking on a
wall next to it. The ledger row that proves it: attempt 1 "SDK has no method" is not a block, it is an
observation about the SDK.
