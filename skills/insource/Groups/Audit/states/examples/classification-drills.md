# Classification drills

> Each case gives a value some code is consulting, the question, then the answer with the reasoning. Rules being exercised: [`../references/state-vs-condition.md`](../references/state-vs-condition.md) and [`../references/ownership.md`](../references/ownership.md). Answer each with three things — **kind** (State/Condition/neither), **scope** (local/app-wide), **reusability** (shared source/bespoke) — in that order. Collapsing the three is the most common failure, so name them separately even when two of the answers feel obvious.

## 1. "Search is spinning"

A results panel shows a spinner. Someone proposes a single app-wide `useAppLoadingCondition()` so every panel can share it.

<details>
<summary>Answer</summary>

**State**, local, reusable-as-a-wrapper only. This panel caused the request; waiting resolves it; the app-shell has no business knowing about it. Hoisting one consumer's own fetch to a global source is the §1 misread in reverse — two unrelated places would then share ownership of one request and neither could cancel it cleanly ([`state-vs-condition.md`](../references/state-vs-condition.md) §4).
</details>

## 2. "Search is spinning" — but the network is dead

Same spinner, and the request will never finish.

<details>
<summary>Answer</summary>

Two different facts wearing one appearance: the request's own **State** (`loading`) *and* a **Condition** (`offline`). The tell is recovery — `loading` is fixed by waiting; `offline` is fixed by reconnecting, which no retry inside the panel can cause. Code that keys only on the spinner will wait forever.
This is the single most valuable split in the taxonomy ([`state-vs-condition.md`](../references/state-vs-condition.md) §1).
</details>

## 3. Zero results

`results.length === 0` after a successful request.

<details>
<summary>Answer</summary>

**State** (an outcome of the consumer's own request — "empty" is a lifecycle value like `success` or `error`), local, not reusable as a source: it is derived from the request, so compute it rather than sourcing it ([§3](../references/state-vs-condition.md)).
</details>

## 4. The app-wide "maintenance?" check, copy-pasted

The same `fetch('/api/status')` call is inline in six sections.

<details>
<summary>Answer</summary>

One **Condition** (external, ops-caused, app-wide), reusable — and the duplication *is* the diagnosis: it should be consulted once by one consumer near the root, and read elsewhere ([§6](../references/state-vs-condition.md)). Six owners of one subscription also means six polling loops nobody stops.
</details>

## 5. Someone calls `setIsOnline(true)` after a successful request

"It reconnected, so flip the flag."

<details>
<summary>Answer</summary>

Defect. A Condition is read, never written, by the consumers that consult it ([`ownership.md`](../references/ownership.md) §3). The request succeeding is a State outcome; it is evidence, not causation. If the app genuinely learns connectivity from a probe, that probe belongs in the Condition source itself, which then owns the write.
</details>

## 6. Camera permission denied

Local to the photo feature; but mic and location will need the same shape next sprint.

<details>
<summary>Answer</summary>

**Condition** (external cause — the user/OS decided), local **scope**, **reusable** implementation. Note all three answers are independent: scope says who consults it, reusability says whether the source file is shared. Write one generic permission Condition source; instantiate it per capability ([§4](../references/state-vs-condition.md)).
</details>

## 7. The kill-switch

Read once at shell start; nothing else will ever ask; it is specific to this deployment.

<details>
<summary>Answer</summary>

**Condition**, app-wide **scope**, **not reusable**. Global does not mean shared: a bespoke one-off lives with its owner (the app shell), not in the public shared location, precisely so nobody treats it as a general-purpose source ([§4](../references/state-vs-condition.md)).
</details>

## 8. A countdown during maintenance

Only the maintenance banner needs the ETA.

<details>
<summary>Answer</summary>

**State**, nested — a **Condition** (`maintenance`) owns a **State** (the ETA fetch), legitimately, because the consumer already reacting to maintenance caused that fetch and it dies with it ([`ownership.md`](../references/ownership.md) §1–§2). This is the one allowed direction.
</details>

## 9. A banner shows the ETA and the consumer is torn down

Does the countdown keep running?

<details>
<summary>Answer</summary>

No, and that is the test of ownership. The consumer that created the request must cancel it — abort, unsubscribe, clear, close, restart-scoped ([`ownership.md`](../references/ownership.md) §4). A subscription whose cleanup is missing is a source that outlived the consumer that believed it owned it.
</details>

## 10. A local source wraps `useAsyncState`

Does the wrapper own the request?

<details>
<summary>Answer</summary>

Ownership still lands on *the layer that actually calls `fetch`* — the generic source issues it, the calling consumer owns its lifecycle through that call. Adding wrapper layers changes nothing, as long as no wrapper adds a fact read or a decision of its own ([`ownership.md`](../references/ownership.md) §5).
</details>

## 11. Two panels want the same user profile

Both mount and both fetch `/api/profile`.

<details>
<summary>Answer</summary>

Work the causation, not the convenience. Either each panel genuinely owns its own request (two States — fine, and each cancels on its own teardown), one panel owns it and passes the value down, or the profile turns out not to be caused by either consumer and belongs in a shared read-only source. What is *not* valid is "shared ownership of one State fetch" — ownership there is pinned to one caller by causation ([`ownership.md`](../references/ownership.md) §6).
</details>

## 12. A sync worker's backlog is growing

Should the UI show a spinner, or a "server is rejecting us" banner?

<details>
<summary>Answer</summary>

Backlog and in-flight count are the worker's own **States** — waiting helps. Broker rejection, a maintenance window, or a full disk are **Conditions** — waiting does not. The worker example in [`fact-sources-polyglot.md`](./fact-sources-polyglot.md) §6 is exactly this, in code with no rendering at all. The UI that displays either is a different question, owned by `/pvc`.
</details>

## 13. `isPremium`

Read by a results list to choose a layout.

<details>
<summary>Answer</summary>

**Condition** (granted externally by billing, indefinite, read-only to every consumer), app-wide scope, reusable. It is a *posture*, not a lifecycle — even though the code reads it inside an `if` that looks like loading logic ([§7](../references/state-vs-condition.md)).
</details>

## 14. `shouldShowSpinner`

A teammate proposes this as a shared source.

<details>
<summary>Answer</summary>

Not a fact at all — it is a **conclusion** drawn from facts (`status === loading` + `isOnline`), i.e. a decision about what to display. Sources assert values; deciding belongs to the consumer that reads them, which in a UI has its own role and rules in `/pvc`. Naming it as a source is how decision logic leaks into the data layer ([§3](../references/state-vs-condition.md), §5).
</details>
