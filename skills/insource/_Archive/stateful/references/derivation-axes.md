# Deriving states at scale — the axis method

A flat list of states can never be complete, and completeness is the requirement. The way out is to
stop enumerating states and start enumerating the **independent conditions** that compose into them.
A state is a point in this space; the taxonomy is the vocabulary of names for common points.

## The nine axes

Each axis is a condition of one *thing*. Walk every axis independently — that alone gives complete
coverage of single-cause states. Then walk the **edges** between them — that gives the compositional
ones, where the real bugs are.

| # | Axis | Its condition values |
|---|---|---|
| A1 | **Data** — the content the screen shows | never · pending · current · stale · partial · malformed · unvalidated · superseded · withheld-by-policy |
| A2 | **Provider** — the source that owns it | healthy · slow · one-dependency-down (degraded) · unavailable · maintenance window · version-incompatible · rate-limiting · returning-cached · silently-wrong |
| A3 | **Transport** — how the screen reaches it | nominal · high-latency · lossy/jittery · metered/capped · absent · captive-portal · intermittent (flapping) · shape-limited (uplink ≪ downlink) · routed-through-relay |
| A4 | **Viewer** — who is asking | anonymous · authenticated · entitlement-limited · session-expiring · expired · suspended · consent-outstanding · prohibited-by-jurisdiction/age |
| A5 | **Entity** — the thing itself, in time | never-existed · draft · scheduled · pending-review · live · in-progress · ended · withdrawn · removed-by-policy · archived · corrupt |
| A6 | **Action** — what the screen can send | idle · dirty · in-flight · queued-for-retry · accepted · rejected-now · rejected-later · duplicated · lost-in-transit · partially-applied · conflicted |
| A7 | **Host/device** — where it runs | nominal · low-power · thermal-throttle · storage-full · radio-off · peripheral-absent · permission-revoked-after-grant · suspended/resumed · killed-and-restored · mid-update · locked/biometric-prompt · shared-screen/second-display |
| A8 | **Trust** — the integrity of the exchange | intact · payload-unexpected · signature/integrity-failed · client-tampered · credential-exposed · another-user's-data-visible · content-hostile-by-construction · session-replayed/forged · downgraded-transport |
| A9 | **Time & order** — the shape across the sequence | first · retry · concurrent · superseded · out-of-order · late-arriving · abandoned · clock-skewed · raced-with-navigation · elapsed-past-budget |

## The procedure

1. **Single-axis pass.** For each axis, ask: does this screen have a stake in this axis at all?
   (A screen with no writes has no A6 stake.) For every axis it does, walk its values and note which
   would produce a *different rendering or a different recovery*. This is the entire list of
   single-cause states, and it is bounded — roughly 10 values × the 4–6 axes a page actually touches.
2. **Edge pass.** For each high-traffic state from pass 1, ask what happens when a *second* axis
   changes while the user is in it. The four edge families that always produce findings:
   - **In-flight interruption** — action started, transport/host changed mid-way. Does the user's
     input survive? Do they know it didn't send?
   - **Late truth** — a superseded or slow response arrives after a newer one, or after navigation.
     Does the screen regress to old data, or show an error for data it already has?
   - **Recovery asymmetry** — the condition clears by itself (reconnect, wake, entitlement granted).
     Does the screen notice, or does it wait for a tap it never asked for?
   - **Compounding failure** — the retry itself fails, the error state's refresh also fails, the
     cache is corrupt *and* offline. What does the second failure look like?
3. **Unknown pass.** Ask A1/A8's leftover: what does an **unrecognised value on any axis** render?
   The answer must be a designed state, not the happy path (`hostile-and-unknown-conditions.md`).
4. **Collapse.** Run everything through the four gates. Merge aggressively; name the merged causes.
   Most of the theoretical space collapses to a dozen rows — **that is the method working, not
   failing.** Report the number of candidates killed; it's the evidence the pass happened.

## Why this beats a checklist

- **Novel domains work.** A satellite-linked field app, a kiosk, a desktop CAD tool, a TUI — none of
  them appear in any published state list, but they all sit on A3, A7, A9.
- **It is falsifiable.** You can show the user a 3×3 slice: "we covered these axes, we skipped A7
  because the screen reads no local store." A checklist can't say what it didn't do.
- **It catches the second-order states.** "Offline" and "expired session" are on every checklist.
  "Offline while a write is queued, then back online while the session has expired" is not, and it
  is where the silent data loss lives.

## Slicing the space for real budgets

Full coverage of the space is a design artifact, not a work order. Cut it honestly, and say which
slice you took:

| Slice | Take it when |
|---|---|
| Single-axis only | the screen is simple, or you're auditing many surfaces quickly |
| + edges of the top 5 states | default for a real page |
| + compounding failure | money, health, safety, irreversible actions, anything with retries |
| + full A8/A9 treatment | anything security-relevant, multi-tenant, or user-supplied-content-bearing |
| Every axis × every value | never; state it as the theoretical ceiling so the user knows what's unbuilt |

## A worked slice (illustrative, any platform)

Screen: a list the user can open on a device, read from a service, and refresh (by gesture, key
binding, menu item or command — the mechanism does not change the derivation).

- A1 present (pending/current/stale/partial) → 4 candidates
- A2 present (slow/degraded/unavailable/limiting/version) → 4
- A3 present (latency/absent/flapping/metered) → 3 after merge
- A4 present (anon/expired/entitlement) → 3
- A6 present (in-flight/rejected-later/lost) → 3 — a refresh is a write of intent
- A7 present (backgrounded/resumed, killed-and-restored, storage-full-for-cache) → 3
- A5/A8/A9: one row each (withdrawn item in a cached list; unrecognised item shape; refresh racing
  a navigation) → 3

23 candidates → 14 survive the gates → 3 merged pairs → **11 rows presented**, 9 killed and listed
as rejected. That is a normal, honest outcome for one page.
