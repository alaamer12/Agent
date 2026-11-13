# Automatic Retry

- **Description:** Silently re-attempting failed operations after transient faults (network
  blip, timeout, lock contention), including attempt limits and backoff; excludes user-facing
  retry affordances and excludes retry of operations that failed for validation or
  authorization reasons, which must not be retried anywhere.
- **Ownership:** OoU — Backend (Layer 1).
- **Reason:** Only the backend knows which step failed and can apply a bounded policy to that
  step. Frontend-side automatic retry multiplies attempts — three client retries of a request
  the backend already retried three times is nine attempts of one intent — loading the system
  and falsifying the retry UI. Cost paid: the client waits through invisible retries; bounded
  by the policy's own ceiling, which the manual-retry contract then builds on.

## References

- Manual Retry — the frontend's user-initiated retry, permitted only after this policy is
  exhausted; together they prevent the 3 × 3 runaway.

## How To Do It

Retry only classes of failure classified transient, with an explicit attempt ceiling and
backoff; surface the exhausted state to the caller rather than looping longer. Any automatic
retry elsewhere in the stack is a violation of this contract, not a variation of it.