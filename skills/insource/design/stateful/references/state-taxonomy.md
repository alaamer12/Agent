# The state taxonomy — a net, not a checklist

Vocabulary of names for common points in `derivation-axes.md`. **It is not a checklist**: keep only
what the page's own facts and axis walk produce. A row you cannot tie to an evidence pointer is a
hallucination — delete it before the user sees it. 8–20 rows for one screen is normal; 40 means the
gates were skipped.

Nothing here is web-specific. Where a concept historically comes from a web convention, it is stated
as the principle plus the per-platform carriers.

## Provider-outcome classes — use these, not wire codes

Binding all state to HTTP status codes is vendor coupling: it breaks the moment the transport is a
socket, a local service call, a filesystem, a bus, a device driver, an IPC layer, or an embedded
peer. Classify the **outcome**, then map it from whatever carrier the project actually has
(gRPC status, errno, exit code, DB driver code, exception type, IPC error enum, BLE ATT code,
vendor SDK result).

| Outcome class | Meaning | Typical carriers | Renders as |
|---|---|---|---|
| `unreachable` | never got an answer | connect refused/reset, ENETUNREACH, no route, peer asleep, cable out | offline / can't-reach-service |
| `timed-out` | asked, no answer in budget | deadline exceeded, ack never returned, ioctl hang | timeout, with the budget named |
| `throttled` | answered "not now, later" | 429+retry-after, quota, backpressure, semaphore, token bucket | try-again-at-`<when>` |
| `refused` | answered "you may not" | 401/403, ACL, SELinux, entitlement, capability missing | gated / need-access |
| `absent` | answered "that isn't there" | 404/410, ENOENT, missing key, deleted row | not-found / gone |
| `rejected-input` | answered "your request is wrong" | 4xx validation, schema mismatch, CHECK constraint, NACK | per-field inline error |
| `conflicted` | answer depends on a version | 409, EBUSY, optimistic-lock failure, write-write race | resolve-the-conflict |
| `precondition-failed` | the world changed under the request | ESOFTVER, mismatched capability, migration not applied | incompatible / needs-update |
| `unavailable-degraded` | up, but a dependency behind it isn't | 503, downstream timeout, circuit open, replica lag | partially-working |
| `failed-server` | up, but it broke | 5xx, panic, disk full on the service, OOM | try-again-later |
| `malformed-response` | answered, but not in the agreed shape | schema/contract violation, unknown enum, truncated body | unexpected-data (**see hostile file**) |
| `integrity-failed` | answered, but can't be trusted | checksum/HMAC/signature mismatch, cert or pin mismatch, downgrade | security-problem (**see hostile file**) |
| `succeeded-partially` | some of N things worked | batch NACK, multi-write, fan-out read | partial |
| `succeeded-async` | accepted, not yet done | job id, queued, 202, pending sync | in-progress-with-outcome |

Rules: retry **only** `unreachable`, `timed-out`, `failed-server`, `unavailable-degraded`. `refused`
routes to the viewer axis, `absent` to lifecycle, `rejected-input` to the field, `integrity-failed`
and `malformed-response` never retry — they escalate. And never present `refused` as `absent` or
`unreachable` as `absent`: both leak facts that aren't the viewer's to learn.

---

## A — Data availability and read lifecycle (axis A1)

| State | Evidence | Must offer |
|---|---|---|
| first-read-in-progress | read on entry, nothing on screen yet | a progress representation matching the real structure; never a blank frame |
| background-refresh | cache hit + fresh read | keep the old content, mark it refreshing; never blank on refresh |
| stale | age beyond useful life | freshness line; warn if decision-grade (money, counts, medical, availability) |
| partial | ≥2 sources, some failed | render what arrived; per-region notice; retry only the failed region |
| ready | happy path | — |
| empty-never | zero records, no filter active | explain what belongs here + primary action that creates the first |
| empty-filtered | zero with a filter/search/sort active | clear-the-filter — **never** a create action |
| empty-paged | zero beyond first page | return to previous / reset position |
| empty-by-policy | records exist, hidden | say why, and where the rule or appeal is |
| empty-by-entitlement | records exist, not this viewer's | request access / change identity |
| read-failed | `failed-server` / `unreachable` / `timed-out` | retry; distinguish transient from persistent after the 2nd failure |
| not-found | `absent` | a way back to something real |
| gone | `absent`, permanently | where it went, if anything knows |
| rejected-payload | `rejected-input` on a read (bad params/ids) | fix the input, don't loop |
| too-large-to-present | huge collection, unrenderable | window/summarise, say the limit, say what's omitted |
| unreadable-local-store | cache/DB corruption, migration half-applied | self-heal by discarding + refetch, and log it |
| unknown-value-present | a field whose value isn't recognised | render honestly as unknown; never a silent default |

## B — Provider and transport health (axes A2 × A3)

| State | Evidence | Must offer |
|---|---|---|
| high-latency-but-working | read > ~1–2 s, structure known | elapsed/progress signal so waiting ≠ stuck; a cancel that actually cancels |
| budget-exhausted | request past its deadline | `timed-out` with the budget named; never an unbounded spinner |
| no-connection-at-entry | transport absent **and** no usable cache | honest "nothing to show without a connection" + resume-on-reconnect; **never** `empty-never` |
| no-connection-with-cache | transport absent, cache present | serve cached content + freshness line; suppress retry-storm affordances |
| connection-lost-mid-session | transport dropped with content on screen | keep content; non-blocking notice; queue writes if the screen has them |
| flapping | repeated up/down | debounce: don't thrash the UI or fire a request storm on each edge |
| captive-portal / partial-connectivity | link up, egress blocked | "connected but no service" — a third truth, not a failure of the app |
| metered/throttled-link | data-saver, quota, satellite, roaming | lighter payload path; say what was withheld and why |
| provider-degraded | `unavailable-degraded`, circuit open | scope the message to the affected capability, not the whole screen |
| maintenance-planned | flag/endpoint/status feed | the window + what still works; dismissible with remind-me if long |
| incident-unplanned | broad `failed-server` across endpoints | what's affected, status link, auto-clear on recovery |
| client-incompatible | `precondition-failed`, version gate | the upgrade path; **beats nearly everything in precedence** |
| thundering-herd-after-outage | mass reconnect + unthrottled refetch | jittered backoff, single in-flight read — the recovery state that takes the service back down |
| succeeded-async | `succeeded-async` | progress + reachable outcome, not a spinner that outlives the call |

`no-connection` and `read-failed` are never one row: different truth, action, and copy.

## C — Action lifecycle (axis A6) — only if fact #2 found writes

| State | Evidence | Must offer |
|---|---|---|
| idle / dirty | editable content | dirty marker; save-on-exit path |
| validating-inline | client-side rules | per-field message at the field; focus moves to the first error |
| blocked-by-validation | action disabled by rules | say what's missing — never a mute unresponsive control |
| in-flight | mutation sent, no answer | action-local progress, duplicate-guard, navigation warned |
| queued-offline | write held for connectivity | show it's queued and unsent; real send state, not a fake success |
| multi-part | several writes, some done | which remain; no silent partial success |
| rejected-now-retryable | `unreachable`/`failed-server` | retry with **every entered value intact**; idempotency guard |
| rejected-now-fixable | `rejected-input`/`conflicted` | map each error back onto its field or offer the resolution |
| accepted-then-refused | `succeeded-async` that later fails | a reachable notification, not a transient that expired |
| accepted-pending-review | async pipeline | what happens next and when |
| optimistic-rolled-back | optimistic + failed commit | revert visibly, say it reverted, keep the user's edit |
| lost-in-transit | sent, no ack, unknown outcome | **never** claim success; verify-then-offer-retry with an idempotency key |
| duplicated | double-tap, retry, replay | suppression, and honest dedupe messaging |
| needs-entitlement-to-act | read allowed, action gated | re-auth/upgrade that returns with the draft intact |
| quota-exhausted | write-side `throttled` | the limit, current usage, path to more |
| conflict-on-write | `conflicted` | compare and choose; never silently overwrite |
| exit-with-unsaved | dirty + leaving | a real confirm, in the product's voice, not the platform default |

## D — Viewer and entitlement (axis A4)

| State | Evidence | Must offer |
|---|---|---|
| not-signed-in | auth gate | sign-in preserving intent (target, filters, draft) |
| expiring-soon | token TTL | silent refresh, or a prompt that doesn't destroy context |
| expired-mid-session | later `refused` | re-auth without losing typed work or position |
| entitlement-limited | role/plan/flag | what's gated and what unlocks it — no dead end, no fake success |
| capability-absent | hardware/OS/API missing | say it's this device, not the user; degrade the feature, keep the screen |
| consent-outstanding | consent store | the reason and the path through it; compliance copy verbatim from the compliance doc |
| jurisdiction/age-gated | locale, birthdate | the gate's reason; legal copy is not yours to rewrite |
| account-restricted | suspension/ban | duration, reason, appeal |
| identity-mismatch | signed-in-as ≠ owner of this data | switch or step back; never show one identity's data to another |

## E — Entity lifecycle in time (axis A5 — derive from the enums in fact #5)

never-existed · draft/unpublished · scheduled-not-yet (countdown; "not started" ≠ "empty") ·
pending-review · live/in-progress (suppress contradictory actions) · processing/transcoding (honest
indeterminate) · partially-available (offer what works, mark what doesn't) · ended/expired (what it
became) · withdrawn/deleted-by-owner · removed-by-policy (rule + appeal + date) · archived/read-only
(writable affordances gone) · superseded (link to the current one) · corrupt/unrecoverable.

For each lifecycle field: **what does the screen show for every value that field can hold?** A
five-value status rendered by a two-branch conditional has three missing states. This is the
richest source of screen-specific states — go find the enums.

## F — Transient attention (axis A9 partly; overlays content, never replaces it)

transient notice · inline field error · non-blocking banner (connection, power, storage, quota,
maintenance) · blocking dialog · progress-with-cancel · background-task-in-flight · consent prompt ·
first-run coaching · "N new — show them" pill.

Rules: one primary action per interruption; a single arbitration queue for what may overlap (a
dialog over a banner over a notice is three fights for one attention); auto-dismiss only
recoverable low-stakes messages; **never** auto-dismiss a failure the user hasn't seen; anything
worth knowing must be recoverable after it disappears.

## G — Host and device condition (axis A7)

low-power / battery-saver-reduced · thermal-throttle (work deferred) · storage-full (writes, cache,
and downloads all fail differently) · radio-off (wifi/bt/cellular/airplane) · peripheral-absent or
disconnected-mid-use (headset, printer, camera, sensor, cable, second display) · permission-revoked-
after-grant (OS took it back) · suspended-then-resumed (background budget exhausted, session stale)
· killed-and-restored (process gone, must the screen rebuild its state?) · mid-update /
upgrade-restart (an action survives the binary changing underneath it?) · locked / biometric-prompt
· shared-screen, casting, or second-display (what must not appear) · multi-instance /
another-process-holds-the-lock (desktop: file locked, port taken, single-instance conflict) ·
resource-exhaustion (memory, fds, handles) · clock-changed-by-user · reduced-capability-mode
(safe mode, kiosk lockdown, managed-device policy).

Device and OS lifecycle is where silent data loss lives: the screen's state must survive the things
the OS does to it without asking.

## H — Presentation and access modality (per-platform, always relevant)

narrow/short-region reflow · orientation · text-scale overflow · writing-direction mirror (icons,
arrows, progress, swipe semantics) · reduced-motion (never let meaning ride on animation) ·
high-contrast · colour-scheme · **colour-only or icon-only signalling** (unreadable; must have a
label) · assistive-tech path (screen reader, magnification, switch/d-pad/remote control, no touch) ·
input-modality switch (hover-only, or gestures with no visible equivalent) · audio-only or no-audio
· situational impairment (gloved hands, one hand, bright sunlight, noise, motion sickness) ·
timing pressure (does an expiring action say so and can the user extend it?) · text-entry cost
(a 40-character reason field typed on a remote or a small screen is a dead control) ·
localisation (untranslated string, no plural rules, truncation in longer locales, mixed-direction
inner text).

## I — Time, order and concurrency (axis A9)

superseded-response (a newer read was answered by an older one) · late-arrival-after-navigation
(a response landing on a screen that left) · concurrent-edit (two places, one record) ·
out-of-order-stream (delta before base) · duplicate-delivery (at-least-once is the default) ·
clock-skew (countdowns, "posted 3 minutes ago", retry-after maths) · raced-with-own-write (read
before commit lands: `refused` or `absent` for something the user just created) · budget-elapsed ·
backgrounded-mid-operation · retry-storm (self-inflicted DoS after a recovery).

## J — Integrity, trust and abuse (axis A8)

Deliberately thin here — this family has its own procedure, because the correct behavior is usually
the *opposite* of the intuitive one (fail closed, disclose minimally, never reveal existence).
`hostile-and-unknown-conditions.md`.

---

## Cross-axis confusions

Each pair collapses into one row somewhere, at the user's expense:

| Collapsed | Why they differ |
|---|---|
| no-connection-at-entry vs empty-never | nothing fetched ≠ nothing exists |
| waiting vs blocked | waiting on the world vs waiting on the user's decision |
| `absent` vs `refused` | doesn't exist vs exists-but-not-yours — one leaks the other's fact |
| read-failure vs write-failure | refreshing a list ≠ losing a form |
| stale vs cached-and-current | only worth a signal if age changes what the user should do |
| `unavailable-degraded` vs `failed-server` | one capability vs the whole provider; scopes the retry |
| high-latency vs hung | still coming vs never coming — needs a budget to tell them apart |
| capability-absent vs entitlement-limited | the device can't vs you may not; different fix, different feelings |
| empty-by-policy vs empty-never | invites creation vs invites appeal |
| maintenance vs incident | planned reassures; unplanned needs an ETA |
| disabled-without-reason vs absent-affordance | greyed-out with no explanation is the worst of both |

## Merges that are correct

Merge only when **message and recovery are both identical**: all `unreachable`+`timed-out`+
`failed-server` into one `read-failed` (variant for the `refused` that routes to re-auth); merge the
entitlement states into one `gated` row if the product's copy is identical. Name the merged causes
in the row so one can be un-merged later without redoing the analysis.
