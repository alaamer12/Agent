# Manual Retry

- **Description:** The user-initiated retry affordance (retry button, progress messaging,
  re-send gesture) offered after an operation's automatic policy has been exhausted; excludes
  any automatic or implicit re-attempt logic.
- **Ownership:** OoU — Frontend (Layer 2).
- **Reason:** This is experience, not execution: when and how the person learns a failed
  operation can be attempted again belongs to the layer that owns their feedback. The actual
  re-attempt, once the user asks, is governed by the backend's policy — the frontend re-issues
  the request; it does not own retry semantics.

## References

- Automatic Retry — defines the policy whose exhaustion is this affordance's precondition;
  never offer manual retry before that state, and never hide it after.

## How To Do It
Show the retry action only in the explicitly-exhausted failure state; a tap re-issues the
original request exactly once. No timers, no silent loops, no "retry automatically next
time" creeping into this layer.