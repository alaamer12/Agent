# Hostile, unexpected and unknown conditions (axis A8, plus A9's worst corners)

The families the persona's **paranoid security reviewer** and **adversary** stances exist to find.
Treat these as first-class states with designed renderings, not as exceptions to be logged. They
have a property no other family has: **the intuitive and correct response are often opposite** —
the right default for a technical failure is to retry, and the right default for an integrity
failure is to stop.

## 1. The fail-closed law

Every unhandled, unexpected or unclassifiable condition resolves to one of two defaults. Which one
is a design decision, and it must be written down — never left to the last branch in the file.

| The screen can… | Default when something unexpected happens |
|---|---|
| show data that is merely stale or absent | **fail open** — degrade to cached, partial, or honest-empty; keep the user moving |
| cause an irreversible effect (spend, send, publish, delete, grant, unlock, transmit, sign, book) | **fail closed** — the action is not taken; say so; offer the safe path |
| expose someone's data (anyone but the entitled viewer, including the viewer's own on a shared surface) | **fail closed** — suppress the data, report the condition, never render it "to help debug" |
| widen a permission or trust boundary (auto-grant, auto-trust a cert/host/device, skip a check) | **fail closed** — always requires an explicit user decision |
| misrepresent a *result* the user will act on (a balance, a status, a countdown, a moderation verdict) | **fail closed** — "unknown" beats a plausible wrong value |

The `else` branch of a screen's condition resolver is the most reviewed line of code you will ever
write. Make it render a designed unknown-state, and make it log. If the type system cannot tell you
which variants you haven't handled, that gap is itself a finding worth reporting.

## 2. Unknown-value handling

The most common unexpected condition is not an attack — it is a **contract change the screen didn't
hear about**: a new enum member, a removed field, a value out of range, a type it wasn't told about,
a timestamp from the future, a payload from a newer server or an older client.

- **Tolerant reader, explicit unknown.** Never crash, never silently drop, and never map an
  unrecognised value onto the *default* case — which is how "under review" renders as "approved" and
  how a new lifecycle state becomes a dead button. Add an unknown value to every enum the screen
  consumes, and render it as visibly unknown.
- **Absence is not zero.** A missing field must not render as `0`, `""`, or a plausible default.
  Distinguish "known to be none" from "not told".
- **Mixed-version fleet is normal.** Old client + new server is a permanent production state, not an
  edge case. Version-gate, and degrade by hiding the affordance rather than rendering a broken one.
- **Cap the plausible range.** A count of 4,000,000,000, a date in 1970, a duration of negative
  seconds: render the anomaly honestly, don't lay it out.
- **Report with a stable id.** The user sees the correlation id; the detail goes to telemetry, not
  to the screen.

## 3. Integrity failures

`integrity-failed` from `state-taxonomy.md` — checksum/HMAC/signature mismatch, certificate or pin
mismatch, transport downgraded, content modified in transit, an update package that doesn't verify,
a response that arrived from somewhere else.

- These are **security states**, and they must not share a message with ordinary technical failure.
  "Connection problem, try again" on a pin mismatch teaches the user to retry through an attack.
- Say what is affected and what you did: content withheld, action not taken, session ended.
- Never offer "continue anyway" as a plain button. If the product legitimately needs an override, it
  is an explicit, deliberate, recorded user decision — different visual weight, different copy, and
  the security posture confirmed with the user before implementing it.
- Fail closed on writes; on reads, withhold rather than render.
- Do not name the mechanism in user copy. "Couldn't verify this came from us" — not "certificate
  pinning failed for api-3.internal".

## 4. Exposure, breach and forced invalidation

Conditions where something leaked, or where the product must assume it did.

| Condition | What the screen owes |
|---|---|
| session/token invalidated server-side (rotation, incident, admin action, password change) | an honest "you were signed out for security reasons" + re-auth, and **unsent local work preserved** |
| a second-party change means credentials must be re-entered | never a silent retry with cached credentials |
| another user's records appear in this viewer's payload | suppress, don't render, and report the anomaly; a leak surfaced *as content* is still a leak |
| incident mode is declared by the service | the screen stops trusting ordinary results: reads are labelled, irreversible writes are blocked or double-confirmed |
| an account is under active compromise | step-up verification before sensitive reads/actions, and a visible way to see/revoke sessions and devices |
| local store may contain data of a previous account (device shared, wipe failed) | clear-on-identity-change, and never render the previous identity's cached content during the swap |
| a security-relevant event happened elsewhere (new device, key added, export performed) | a reachable notification the user can act on later — not a transient that evaporates |

**Lock-screen, cast, and screenshot surfaces.** Anything shown where the screen is not the viewer's
eyes gets a deliberately thinner rendering: redact or mask sensitive values by default, honor a
hide-on-background/hide-in-recents affordance where the platform provides one, and never put secrets,
codes, or another person's data in a place a passive observer reads. Copying a sensitive value to a
shared clipboard is an action, not a convenience — say so, and clear it where the platform lets you.

**Disclosure discipline during any of this**: name the affected thing, not the internal topology. No
service names, hosts, regions, record identifiers belonging to others, stack traces, absolute paths,
SQL fragments, or key material — in the message, in the logs the message renders, or in the error
payload that reaches the client. A correlation id is the only diagnostic detail a user should ever
see.

## 5. Content that is data to you and an attack to someone else

Anything a user or an external source authored, rendered inside a privileged surface — names,
captions, messages, filenames, descriptions, link previews, avatars, rich text, markup from a feed.

- **No execution, ever.** Sanitise to the platform's declared capability level; a preview renderer is
  still a renderer. Inert by default; a link is a link only after the user chooses it.
- **Never let authored content impersonate the system.** Reserve the product's own voice, chrome,
  and layout primitives; a record whose *text* is styled like a button, a banner, or a system dialog
  is a phishing surface.
- **Direction and invisible-character attacks.** Bidirectional overrides, zero-width joins, RTL
  spoofs that reverse a filename's extension, homoglyphs that make one name look like another,
  emoji widths that hide the tail of a link or path: render with a visible boundary around foreign
  text, and never let authored text set the surrounding layout.
- **Bounds.** Oversized, absurdly nested, or unbounded-length payloads need a limit and an honest
  "too long to display" — not a frozen screen.
- **Untrusted media and previews.** Dimensions and type are claims, not facts. Reserve space from
  your own constraint, not theirs.
- **Reported/removed content** still occupies a slot; say it was removed rather than deleting the row
  and letting the user conclude the item never existed.

## 6. Tampered and misbehaving clients

A user editing local state, spoofing a clock, replaying a request, running a debug build, or on a
modified device.

- **Server truth wins; the screen never argues about it.** When local and authoritative state
  disagree, authoritative wins, and the screen says it reloaded rather than accusing the user.
- **Clock-skew is usually innocent** — a wrong device clock, not a cheat. Degrade: show no countdown
  rather than a lie; never block a legitimate user over it.
- **Replay and double-submit** are ordinary accidents (button mashing on a slow link). Idempotency is
  the state design, not the error handler.
- **Rooted/jailbroken/attestation signals are policy inputs**, and policy varies: what the screen
  shows is the product's decision. Implement whatever it decides — usually a capability restriction
  with a plain explanation, never a silent failure that reads as a bug. Confirm before inventing one.
- **Support-tool presence** (screen readers, magnifiers, remote control, developer overlays, kiosk
  lockdown) is never a hostile condition; don't gate it under the previous bullet.

## 7. Crash-adjacent and recovery states

- **Last-resort boundary.** If the screen fails, something must still render: an honest error with a
  recovery path (retry, go back, restart, report) — never a blank frame, and never a stack trace.
- **Repeated-failure escape hatch.** If a screen crashes on entry, it must be reachable in a
  degraded mode; otherwise the user is locked out by the thing they were using. Offer "open without
  this content" or the equivalent.
- **Restart-and-land-back.** After an OS kill or update, the user should return to where they were —
  or be told plainly that they won't. Losing an unfilled form is a data-loss event.
- **Self-heal before asking.** Discard a corrupt local store and refetch; the user shouldn't see
  internal bookkeeping failures. Log it; don't interrogate them about it.
- **Partial application** (a migration or update that half-applied) is a *state*, with an exit that
  does not require the user to reinstall to recover their data.

## 8. Quiet-failure prohibition

The hostile case most often is the one the app does to its own user.

- Never swallow an error into a spinner that never ends.
- Never render an error as an empty state (it tells the user the world is empty, not that you couldn't
  look).
- Never claim success for `succeeded-async` before the outcome exists, or for `lost-in-transit` at
  all. An unknown outcome is one state and must be presented as one — with a way to find out.
- Never report a bug so softly that telemetry cannot reconstruct it; the correlation id the user sees
  is how that reconciliation happens.

## 9. Consult before implementing this family

Rows from §3–§6 are policy, not craft: the correct behavior depends on the product's risk posture,
its legal position, and who else owns the security story. In Step 4, flag every such row explicitly
(`policy` verdict) and get the answer, along with: which irreversible actions exist on this screen
(so the fail-closed list is bounded), and what the project's existing rule is for disclosure in
errors. If the project has a security or compliance document, it outranks everything in this file.
