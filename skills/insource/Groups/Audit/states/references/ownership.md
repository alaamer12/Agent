# Ownership — who created the fact, and what that permits

> The one asymmetric relationship in this system: between a fact source and its consumer. Classification of the fact itself is [`state-vs-condition.md`](./state-vs-condition.md); file placement is the `/pvc` skill's concern. Framework shapes for every rule here: [`../examples/fact-sources-polyglot.md`](../examples/fact-sources-polyglot.md).

## 1. The asymmetry

Because consumers can nest, both directions of "consumer A using consumer B's fact" occur. They are **not the same relationship**:

> A consumer reacting to a **Condition** may create and own a **State** — resolving that Condition can legitimately require its own request.
> A consumer reacting to a **State** may only **read** a pre-existing **Condition** — a Condition by definition exists independently of any single consumer's work, so nothing local can own what it did not cause.

```
Condition → may own        → State       (legitimate composition: this consumer caused the work)
State     → may only read   → Condition   (a dependency: this consumer did not cause the fact
                                           and cannot end it)
```

## 2. The test: create vs listen

> **Does the source create the thing, or does it merely listen to a thing that already exists — before this consumer arrived and after it leaves?**

```
issues the request / starts the timer / opens the connection  → creates   → State
subscribes to an event, polls a status, mirrors a signal       → listens   → Condition
```

**Worked contrast.** A maintenance *countdown* exists only because something already reacting to maintenance needed it in order to decide what to show. Nobody else needed that fetch; it is created and destroyed with its consumer — a State, genuinely owned. By contrast "am I online" is true or false whether or not this consumer ever started: not created by it, not destroyed by it, and every consumer asking gets the same answer because every consumer is *reading*.

**Why the asymmetry exists at all.** State and Condition are both fact-*producers*: each is backed by a side effect that somebody caused. Asymmetry only arises between a producer and a consumer, because "who caused this" has an unequal answer by construction — and "Condition" is defined so that local causation is excluded. Nothing can occupy the creator position relative to a Condition. This is a property of fact pairs specifically, not a general law that every pairing in an architecture must be uneven.

## 3. What ownership permits

| | Owner of a **State** | Reader of a **Condition** |
| --- | --- | --- |
| Start / restart the work | Yes | No |
| Cancel it | Yes — and must, on teardown | No |
| Write the value | Yes | **Never** — a setter reachable from a consumer is a defect |
| Assume the same value as another consumer | No — each owner has its own instance | Yes — that is what makes it app-wide |
| Be reused by another consumer | Only through an explicit wrapper or a shared generic source | Naturally, by reading the same source |

The read-only surface for Conditions is not ceremony: it is the only mechanism that keeps a consumer from accidentally claiming causation it does not have. Expose the value, not a way to change it.

## 4. Lifetime and cleanup

Ownership is only real if teardown is handled. The consumer that creates must also destroy:

```
HTTP request        → abort / cancel token, so a late response cannot write into a dead consumer
event subscription  → remove the listener when this consumer goes
polling / timer     → clear it
websocket / stream  → close it, and reconnect only under the new owner
Rust resource       → dropped, or restarted explicitly
Blazor service      → unsubscribe in Dispose / AsyncDisposable
```

The common defect is a subscription whose cleanup is missing, so the source outlives the consumer that believed it owned it — the value then keeps updating something that no longer exists, or is read by a second consumer whose answers were actually written by the first.

## 5. Ownership passes through wrappers untouched

A local source may delegate to a generic shared one — a thin wrapper supplying arguments and adding no decision. Ownership is still decided by *the layer that actually issues the request or registers the listener*, no matter how many delegating layers sit above it:

```
shared generic State source   → issues the request itself  → owns the effect
local State source wrapping it → supplies the fetcher        → still owned by the local caller
shared generic Condition source → registers the listener     → pre-exists, read-only
local Condition source wrapping it → names the events        → still read-only
```

A wrapper that adds *no fact consulting and no selection* can never violate §1 or §3, whichever kind it wraps. The moment a wrapper adds a decision, it has stopped being a wrapper.

## 6. When two consumers want the same State

They cannot own one instance together. This is the one place where the instinct "more than one consumer, so it must be a shared/scoped thing" is wrong: a State's ownership is pinned to exactly one caller by causation, so there is no scenario of two siblings legitimately sharing ownership of one fetch. If two consumers need the same data, either

- each owns its own request (usually correct — they are different questions),
- one owns it and hands the value to the other, or
- the value turns out to be a Condition after all, because it was never caused by either of them.

This is also why fact sources are the documented exception to the placement pole test — ownership is settled here, by causation, before any question of "which folder" is asked. The poles themselves are `/pvc`'s model; they apply to the *file*, never to the *ownership*.

## 7. Beyond UI

Nothing above depends on rendering. The same test decides ownership for:

```
a background sync worker        → its own queue/backlog = State; broker rejection = Condition
a cron or scheduled job          → its run status = State; maintenance window = Condition
a daemon watching a folder       → its own scan progress = State; disk full / permission = Condition
a server session                 → in-flight request = State; expired token = Condition
```

The vocabulary changes, the create-vs-listen question does not.
