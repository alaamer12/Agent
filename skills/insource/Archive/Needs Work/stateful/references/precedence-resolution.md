# One resolver, one order

The rendering is the easy half. The bug — live in most screens — is that the screen decides what to
show with several independent booleans that were never reconciled. Language-agnostic: every stack
that renders state has this problem and every stack has a construct that fixes it.

## Why boolean soup fails

```
show = !inProgress && !errored && items.length > 0
```

Three flags, eight combinations, and the code considered one of them. Concretely:

- `inProgress && errored` — the retry is in flight. Does the error win? Nobody decided, so the
  *source order of the branches* decides, and it changes when someone reorders them.
- `!inProgress && !errored && empty` — the no-connection-at-launch viewer is told they have nothing.
  This is where the false-empty physically comes from.
- An error from a **stale** request arriving after a **fresh** one — the screen shows a failure for
  data it already has.
- `errored` from a read *and* from a write, one flag — so a failed refresh looks like a lost form.

The invalid combinations are reachable because they are **representable**. Fix the ground.

## The shape

Model the screen's condition as **one value with one variant per state**, derived in exactly one
place. The name changes per stack — discriminated union, sealed class, enum with payloads, tagged
struct, sum type, a single computed record — the shape does not:

```
condition :=  Blocked     (why: incompatible | maintenance | incident | unreachable-no-cache)
            | Gate        (why: not-signed-in | expired | entitlement | consent | policy)
            | Absent      (why: not-found | gone)
            | Refused     (why: permission | quota | identity-mismatch)
            | Failed      (outcome: unreachable | timed-out | provider | integrity, retryable)
            | Unexpected(what: unrecognized-shape | invariant-violation)   ← the else branch
            | Pending     (kind: first | retry, progress: known | indeterminate)
            | Empty       (why: never | filtered | paged | policy | entitlement | unreachable)
            | Loaded      (items, freshness: current | stale | refreshing)
            | Partial     (ok: [regions], failed: [regions])
```

`examples/polyglot-walkthrough.md` has this in six idioms across the paradigm quadrants, before/after, plus
where each stack's exhaustiveness check actually lives.

Rules that keep it honest:

- **Content and action state coexist.** `Pending-write`, banners and notices are **not** variants of
  the screen condition; they ride on top of `Loaded`. One value mixing both makes "editing while
  refreshing" unrepresentable, so people bolt flags back on. Two axes: **screen condition**,
  **activity layer**.
- **Every producer writes the same value.** The transport wrapper, the connectivity listener, the
  session store all feed the resolver. None of them renders directly.
- **`Refused` never renders as `Empty`; `Blocked` never renders as `Empty`.** If the type can't
  express the confusion, the render can't get it wrong.
- **The `Unexpected` variant is mandatory.** Anything unclassified lands there and renders a designed
  unknown-state, not the happy path. See `hostile-and-unknown-conditions.md` §1.
- **Exhaustiveness is the point.** Where the language can check it — a match on a sum type, an
  exhaustive switch, a lookup keyed by variant, a table with a compile-time or startup assertion —
  prefer the form that **fails to build or fails fast** when a variant is unhandled. That is the
  mechanism that turns "all states covered" from an aspiration into a checked property. Where the
  language can't check it, the matrix is the checklist and the test is a test.

## Precedence — one decision, written down

When two conditions are simultaneously true, one renders. The order below is a **starting point, not
a law**; several positions are genuine product trade-offs. Present the contested ones in Step 4 and
record the agreed order as a comment beside the resolver — the ordering *is* the decision.

```
1  incompatible (client can't speak to the provider)   nothing else is trustworthy
2  maintenance (planned)                               a stated plan beats a storm of live errors
3  incident (unplanned, provider-wide)                 one broad truth beats N per-request failures
4  integrity / security posture                        refuses rather than retries; never mixed with
                                                       ordinary failure (hostile file §3)
5  gate (session / entitlement / consent)              can't be satisfied without leaving the screen
6  absent / refused                                    answered; the answer is "no"
7  failed / unexpected                                 didn't answer, or answered unclassifiably
8  pending                                             nothing yet — first read only
9  empty                                               asked, and there is genuinely nothing
10 loaded (+ stale / refreshing flags)
11 partial                                            region-scoped: per region, not over the screen
-- activity layer, drawn over whichever of 1–11 is active --
12 write in flight / queued / notices / dialogs
```

**Contested positions — ask, don't assume:**

| Position | The two defensible answers |
|---|---|
| 4 vs 5–7 | Fail closed on integrity above everything, *or* only for the affected capability. Depends on whether the breach is local or global. |
| 2 vs 3 | Planned maintenance above an incident reassures but can hide a real outage during the window. |
| 5 vs 6 | Gate above absent means a signed-out viewer can't learn an identifier exists; below, it leaks existence. A **privacy decision**, not a UI one. |
| 8 vs 9 | Pending above empty is obvious; the reverse (show cached empty while refreshing) is the offline-first idiom. Depends on which axis owns the truth. |
| 1 vs everything | Hard takeover vs "keep browsing, can't act". Depends on how broken the old client actually is. |

Notes on the parts people get wrong:

- **4 (no-connection-at-entry) before `empty`.** Offline with no cache must beat empty. This single
  ordering removes the most common false-empty in production.
- **`maintenance` before `failed`.** During a planned window every request fails; N error states
  instead of one plan is noise that buries the message.
- **No-connection-mid-session is *not* in this list.** It is a notice (family F). Content on screen
  stays; only what the viewer can *do* changes. Taking a screen down on a dropped link is a
  regression, not a state.
- **Consent before the read** for anything privacy-gated: the request must not start until consent
  exists. Precedence there is compliance, not cosmetics.

## Per-region resolution

On a composed screen (fact #6), each region resolves its own condition with screen-level
`Blocked`/`Gate`/`incompatible` hoisted (a signed-out viewer shouldn't get three identical prompts),
while `failed`/`empty`/`pending` stay local. One screen-level flag gating every region is a defect
the moment two providers can disagree.

## Where the resolver lives — a trade-off, not a rule

| Situation | Options, with the cost |
|---|---|
| one screen, one provider | **in the screen** — cheapest, zero indirection, and the ordering decision is local. Cost: the next screen repeats it. |
| same mechanism across many screens | **shared layer, once** (transport wrapper / session store / connectivity service / entry guard) — one behavior, one fix. Cost: screens lose local nuance; needs an escape hatch that isn't a fork. |
| a reusable state shell (empty/failed/pending/notices) | **the design-system tier**, consumed by screens. Cost: a coupling layer; never re-skinned locally. |
| agent/headless system with a UI on top | **the producing side owns the state**, the surface renders it. Cost: the surface can't invent a recovery the producer didn't offer. |

Decide *with* the user when the project hasn't already. Whatever the project's own structure docs
designate outranks all of the above — read them first (SKILL.md Step 5, conventions hook).
