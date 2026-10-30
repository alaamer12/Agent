# Step 1 — Extracting the eight facts

What actually determines a screen's state surface. Grep patterns are *starting points across
platforms*, never a contract — adapt to the project's real idioms, and a miss on one pattern never
justifies skipping the fact. Read the screen **and everything it reaches through** (its data layer,
its service and effect bindings, its shell, its entry guards, its local store). A screen that calls
`getVideos()` inherits every state that call can produce, and the call is where the truth lives.

**Name the platform posture first**, because it reweights everything below:

`connected-fat-client` (web/desktop/mobile app) · `offline-first` (local store is the source of
truth, sync is the background) · `thin-client-over-link` (remote desktop, kiosk, high-latency field
link) · `local-only` (no network at all — B collapses, G expands) · `device-paired` (a peripheral or
peer is the provider) · `headless-plus-surface` (a service or agent with a UI riding on it) ·
`static-prototype` (nothing is real; every state must be forceable to be seen)

## 1. Reads

| Look for | Also reveals |
|---|---|
| Any outbound call: HTTP client, RPC/gRPC, GraphQL, IPC/D-Bus/XPC, service locator, direct DB/query, ORM, file read, sensor read, peer/bus message, another process's API | how many round-trips feed one screen, and who owns each |
| Local durable reads: key/value prefs, relational/embedded DB, blob store, config files, memory-mapped or platform storage | **a cache exists ⇒ stale and no-connection-at-entry are real states** |
| Freshness plumbing: ttl, etag/etag-ish validators, `stale`, `swr`, `maxAge`, `expires`, revision vectors, watermarks | revalidating and stale rendering are already wired for somewhere |
| Live feeds: streams, subscriptions, sockets, polling, watchers, reactive signals, callbacks, push, file-system watchers, sensor streams | mid-session updates, partial arrival, and out-of-order delivery are states |
| Entry triggers: init/lifecycle callbacks, first-render effects, navigation or command params, deep links, restored state, CLI flags, stdin | first-read-in-progress — and **what happens when the input is garbage** |

Record: **provider, count, cacheability, and what shows before each one resolves.**

## 2. Writes

Any outbound mutation: POST/PATCH/PUT/DELETE, RPC methods that change state, ORM insert/update/
delete, file writes, preference commits, queue pushes, uploads, device commands, IPC calls with side
effects, shell commands, print/spool, transaction commits. Also: debounced writes, optimistic-update
helpers, rollback/undo support, background-sync or work queues, retry wrappers.

If any exist → the entire action family (taxonomy §C) is in play. If none exist → **say so in the
matrix**; "not applicable, screen is read-only" is a correct and valuable finding. Never pad.

## 3. Failure paths

`catch`/`except`/`rescue`/`recover`, `.catch(`, `onError`, error results/eithers/`Error?` returns,
thrown exceptions, error boundaries, panic handlers, `!res.ok`, `status >= 400`, non-zero exit
codes, `errno`/`GetLastError`, NACK/reject callbacks, promise/event emitter error channels, logging
calls, telemetry reporters, toasts/notice calls.

Two readings matter more than the count:

- **Failure swallowed** (empty handler, log-only, telemetry-only, silent default return) → the user
  gets a permanently stuck progress indicator or a silently empty list. **The highest-severity
  finding this skill makes.** Report it even when the state "technically exists".
- **Failure over-generalised** (one handler rendering a generic "something went wrong" for
  `refused`, `absent`, and `timed-out` alike) → `upgrade`: distinct outcomes have distinct recoveries.
  Map whatever the project's carrier is onto the outcome classes first (`state-taxonomy.md`).

## 4. Gates

Auth/session/token stores, route or command guards, middleware, role/permission/capability checks,
`can(...)`, plan/subscription/tier/entitlement, feature flags and experiments, kill switches, quota
and usage counters, region/locale/age/consent stores, licence/activation state, device attestation,
admin/managed policy, rate-limit wrappers.

Also read what sits *upstream* of the screen: guards attached at the navigation layer, the shell, or
the command entry produce states the screen never sees as data. A redirect is a state handled
elsewhere — record where.

## 5. Entity lifecycle

Field names are the tell: `status`, `state`, `stage`, `phase`, `visibility`, published/scheduled/
start/end/expires/deleted/archived timestamps, moderation or review state, version/revision,
is-live/is-upcoming/is-expired, sync or delivery state, job/queue status.

For each lifecycle field: **what does the screen show for every value that field can hold?** A
five-value enum rendered by a two-branch conditional has three missing states. Go find the enums —
this is the single richest source of screen-specific states. Note also where the enum's *unknown*
value lives (or that it has none — a finding, see `hostile-and-unknown-conditions.md` §2).

## 6. Composition

Count independent providers per screen region. One failed panel taking down a whole dashboard — in a
web app, a desktop window, or a TUI — is a structural defect, not a data bug. Note whether each
region has its own loader or whether one screen-level flag gates everything (usually wrong above
one source).

## 7. Emptiness multiplicities

For every collection that can come back with nothing:

| Cause | The tell | Correct recovery |
|---|---|---|
| never had any | first run, no records for this viewer | teach + a primary action that creates the first item |
| filtered away | a filter/search/sort/group is active | clear-the-filter — **never** a create action |
| paged past end | position > 1 with no results | go back / reset position |
| hidden by policy | items exist, moderated/private/consent-blocked | say why; link the rule or the appeal |
| not this viewer's | ownership/entitlement narrowed it | request access / change identity |
| provider unreachable | nothing was answered | connection state, **not** empty — see the precedence rule |

A single generic "No data" across these is a finding. A filter-active empty state offering "Create
your first…" is a **defect**, not an incompleteness.

## 8. Host, device and environment dependencies

| Class | Signals to look for |
|---|---|
| connectivity | interface/reachability APIs, network-status listeners/streams, radio state, airplane mode, VPN/proxy, link-quality or effective-type hints, data-saver settings |
| power & thermal | battery level/state, low-power modes, thermal throttling, doze/background budget, unplugged behavior |
| storage | free-space queries, quota APIs, write failures, "cache too big", removable-media presence/removal |
| permissions | OS permission request + revocation callbacks, capability checks, sensor/camera/mic/notification/accessibility entitlements |
| peripherals | device attach/detach events, printer/scanner/camera/adapter availability, paired-peer connection state |
| lifecycle | suspend/resume, foreground/background, screen lock, app-will-terminate, process death + state restoration, update/upgrade callbacks |
| presentation | size/breakpoint or window-geometry signals, orientation, text scale, contrast mode, colour scheme, writing direction, reduced-motion/transition, font availability |
| input | pointer vs touch vs keyboard vs gamepad/remote vs voice vs assistive tech; hover capability; text-entry cost |
| identity of the run | debug vs release, dev-only flags leaking to production, version/client-compat checks, managed/policy/kiosk mode |
| time | clocks, timezones, monotonic vs wall-clock, countdowns and freshness maths |

## Recording the facts

Fill this in **before** opening the taxonomy — it is what Step 3's evidence gate draws on:

```
TARGET    <path or screen id>       MODE  static-prototype | real source
PLATFORM  <posture from the list above>            STACK  <what it actually is>
READS     <n providers, which cacheable>  <what shows before each resolves>
WRITES    <yes/no — which, optimistic?, irreversible? (feeds the fail-closed list)>
FAILS     <per call: which outcome class, handled how — swallowed / generic / specific>
GATES     <auth? role? flag? quota? policy? enforced where>
LIFECYCLE <status-ish fields and every value each can hold — and its unknown case>
COMPOSE   <regions with independent providers>
EMPTY     <each collection + which of the 6 causes apply>
HOST      <which of the §8 classes this screen truly depends on>
```
