# State and Condition — the taxonomy

> What the two kinds of fact are, how to tell them apart, and the three axes people collapse into one. Ownership — who created the value and who may destroy it — is [`ownership.md`](./ownership.md). Expressions in specific frameworks: [`../examples/fact-sources-polyglot.md`](../examples/fact-sources-polyglot.md).

## 1. The boundary, and what each axis decides

The definitions are in the skill overview; what matters while working is that every axis changes a concrete decision, and collapsing two of them is where the bugs come from:

| Axis | What the answer decides |
| --- | --- |
| Cause | who may retry, and whether retrying is meaningful at all |
| Lifespan | whether waiting is a strategy |
| Resolver | what the source subscribes to versus what it issues |
| Mutability | whether a setter may exist outside the owner |
| Recovery | a retry control, a reconnect banner, or "contact support" |
| Value shape | what downstream logic keys on — a lifecycle or a posture |

**How each misread shows up.** A Condition read as State produces code that waits or retries against something that will never change on its own — an infinite spinner during maintenance mode, a retry button that cannot fix a revoked permission. A State read as Condition produces code that hoists one consumer's own request into a global source, so two unrelated places now share ownership of one fetch and neither can cancel it cleanly.

## 2. The checklist

Run in order, stop at the first yes.

1. Did *this consumer* trigger it, by making a request or performing an action? → **State**.
2. Does resolving it require something outside this consumer's control — a reconnect, ops ending maintenance, a role being granted, a flag being flipped? → **Condition**.
3. Still unresolved? Ask whether waiting could ever help. Yes → State. No → Condition.

Default to **Condition** when the evidence is exhausted. The appearance ("it looks broken") is identical for both, and it is the cause that differs.

## 3. What counts as a fact

A fact is a value **consulted before deciding what to do next**. Not everything that looks like state belongs to this taxonomy:

```
a constant, a build-time config value   → not a fact; nothing to consult at runtime
a derived value (sum of what you hold)  → not a fact; compute it, don't source it
another object's identity or content     → a fact, but neither State nor Condition
                                           unless a lifecycle or a posture is what it asserts
user input as typed                      → neither; it is data, not a verdict about the world
```

The distinction that matters is *whether the value answers "what is happening to my own work?"* (State) or *"what is the world currently allowing?"* (Condition). If it answers neither, it is ordinary data and does not need either label.

## 4. Cause, scope, and reusability are three separate axes

The classic collapse: "Condition means global, State means local." False, and acting on it puts code in the wrong place.

```
                     LOCAL                          GLOBAL
                (one consumer/feature)         (every consumer at once)

CONDITION     camera permission denied,      offline, maintenance,
(external     one widget down, one           session expired,
 cause)       feature flag                   kill-switch

STATE         search is loading,             app-shell bootstrap
(own          one form failed to submit      ("check auth on load") — rare,
 request)                                    still owned by one thing
```

And a **third** axis sits on top of both: does the *implementation* get shared, or stay bespoke? Also independent. A local Condition (permission denied) can be one reusable source serving camera, mic, and location. A global Condition (kill-switch) can be a one-off, never reused.

Answer the three separately, in this order — cause, then scope, then reusability — because the answers feed different decisions: cause decides ownership ([`ownership.md`](./ownership.md)), scope decides who may consult it, reusability decides whether the file is shared. Collapsing them is how "it's global, so put it in the shared store" ends up naming a bespoke one-off as a public surface.

## 5. Naming, in this skill's terms

A source's name should assert a fact, not a decision:

```
✔  isOnline, maintenanceEta, permissionDenied, submissionStatus
✘  shouldShowSpinner        → that is a consumer's conclusion, not a fact
✘  searchUnavailable        → a verdict; the facts behind it are offline + flag-off + empty
```

A source returns **data and never renders**. Whatever consumes it to pick an outcome is doing a different job — in a UI that job has its own name and its own rules, which the `/pvc` skill owns; this skill deliberately says nothing about it.

## 6. The tells in the code

- The same global Condition check written inline in many consumers — that duplication *is* the diagnosis. One global Condition should be consulted once, by one consumer near the root.
- Hoisting a State source to the root is impossible without the root learning one feature's internal request. When it looks possible, the value is probably a Condition.
- A consumer mutating a Condition it did not cause (calling a setter for `isOnline` from inside a feature) is a defect. Conditions are read.
- A fact source that renders output is no longer a fact source at all.
- If a fact feels awkward to place, that discomfort is diagnostic, not incidental — usually cause and scope have been conflated.

## 7. Quick reference

| Situation | Answer | Why |
| --- | --- | --- |
| Search results loading | State | Caused by this consumer's request; resolves when it completes |
| Search returned zero results | State | Outcome of the consumer's own request |
| Request failed (500) | State | Retry re-triggers the same request the consumer owns |
| Countdown fetched by something already reacting to maintenance | State (nested) | Caused, scoped, and killed by its consumer — real ownership |
| Reading "online" from inside a loading consumer | Condition (read, not owned) | Existed before, will exist after |
| Device has no network | Condition | External, hits every consumer, resolves outside the app |
| Server in maintenance mode | Condition | External, ops-controlled |
| Camera permission denied | Condition (local) | External cause, one feature's scope |
| Session expired / unauthorized | Condition | External to this consumer's own work |
| Feature flag off | Condition | Externally imposed, not tied to one request |
| Sync worker's own queue depth | State | The worker caused it; it resolves as the worker drains |
| Broker/server rejecting the connection | Condition | External posture; waiting inside the worker fixes nothing |
