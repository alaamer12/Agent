# Implementing a state

Platform-agnostic. Where the project's own conventions (structure docs, design system, shared shell,
component tier) specify a mechanism, that mechanism wins — this file says only what must be true.

## Depth per state

| Depth | Delivers | Order of magnitude |
|---|---|---|
| **D0** in-place | one honest line of copy where the state occurs; no layout change | a paragraph of text |
| **D1** recoverable | distinct treatment **+ one working recovery control** + doesn't break layout or truncate | a small block |
| **D2** designed | D1 + the project's own state components/tokens, real copy, correct progress representation, perception & operability treatment, safe at text-scale/direction/contrast extremes | a component + assets |
| **D3** proven | D2 + forceable in a dev build and actually rendered — inspected at ≥2 sizes and with the state cleared as well as entered | D2 + a verification pass |

Floors, non-negotiable:

- **Anything scored S1 in the matrix ⇒ ≥ D1**, whatever the budget. Depth is negotiable; the fail-closed law
  is not (`assets/templates/matrix-template.md` §Severity).
- **Anything that blocks the screen's purpose ⇒ ≥ D1.** A message with no way out is not a state,
  it's a wall.
- **The state a first-time viewer lands in ⇒ ≥ D2.** First-run empty is the product's front door.
- **The 3–5 likeliest states ⇒ D3.** Prove them; don't assume them.
- Rare, low-consequence informational states ⇒ D0 is honest and correct.
- **Anything from `hostile-and-unknown-conditions.md` §1–§4 ⇒ ≥ D1 and never fail-open**, whatever
  the budget. Depth is negotiable; the fail-closed law is not.

Depth is per row, never global. "Everything at D2" is how these tasks die; "D0 everywhere" is how
they lie.

## Copy — three parts, in this order

1. **What happened**, in the viewer's terms, naming the specific thing ("We couldn't load *Surah
   Al-Fatiha*" beats "Failed to load content"). No wire codes, no stack traces, no internal service
   names, no paths, no other viewer's identifiers — a stable correlation id if anything at all.
2. **What it means for them.** Did they lose work? Is it coming back? Is anything saved? Is the
   action done or not done? For irreversible actions, an explicit "nothing was sent" or "your booking
   is confirmed" — never an implication.
3. **The one action.** One primary. A secondary (dismiss / go back) is allowed. Three buttons is an
   unanswered question.

Voice: no repeated apologies across states, no blame ("your internet"), no cheerful exclamation over
a data-loss event. Reuse the project's existing strings where equivalents exist — inconsistent
failure voice across screens *is* a finding, and reporting it beats rewriting twelve strings.

## Progress representation — pick by what the screen knows

The web's skeleton-vs-spinner debate is one instance of a general problem: **the user must be able to
tell "working" from "stuck" from "done, and it's empty".** State the principle, then use whatever the
platform's vocabulary offers.

| What the screen knows | Use | Platforms |
|---|---|---|
| nothing yet, structure known | **placeholder mirroring the real structure** (counts, sizes, order, reserved height) | web/mobile skeletons · desktop list placeholders · TUI block/table placeholders |
| working, shape unknown | indeterminate activity marker | spinner · pulse bar · `aria-busy` region · spinning cursor · braille spinner |
| real progress exists (bytes, items, %, stages) | determinate progress **with the number** — never a determinate bar faking progress | progress bar, stepped indicator, `N of M`, log lines with counts |
| already have cached content | keep it + a refreshing signal; blanking on refresh is the anti-pattern | everywhere |
| resolves in well under a beat (~300 ms) | **nothing** — a flash of activity reads as broken | everywhere |
| waiting may exceed patience, budget unknown | elapsed-time signal and/or an **honest cancel** | critical on high-latency links |

Rules that outlive any framework:

- Placeholders **reserve the space** the real content will take. A layout that jumps when content
  arrives is where users click into nothing.
- A cancel must cancel: abandon the work, or tell the truth that it can't be cancelled and what
  ending it means.
- **No progress bar without a real numerator.** Faked progress is a lie that gets caught exactly when
  the link is bad.
- Meaning never rides on motion. Reduced-motion ⇒ a static equivalent that still communicates the
  state, including "this is a placeholder, not an error".
- Long-latency screens need a **decision point**: at the budget's edge, stop looking busy and start
  telling the user what you'd like to do next. A 45-second field link is a state, not a delay.

## Retry semantics

- Retry **only** transient outcomes: `unreachable`, `timed-out`, `failed-server`,
  `unavailable-degraded`. Never `refused` (→ gate), `absent` (→ lifecycle), `rejected-input` (→
  field), `throttled` (→ wait for the stated when, don't hammer), and **never** `integrity-failed`
  or `malformed-response` (→ escalate).
- Bound it: max attempts, backoff **with jitter**, and surface the failure once the budget is spent
  instead of retrying silently forever.
- Manual retry re-issues the *same* request with the viewer's current filters and position, and cannot
  stack concurrent retries.
- Auto-retry on the connection returning (false→true edge), debounced — a flapping link must not
  produce a request storm, and after a broad outage, mass reconnect must not take the provider back
  down.
- Retry preserves input and position. **Losing a filled form to a network blip is the worst defect in
  family C.**
- Cancel on leaving, and supersede by sequence, so a late response cannot overwrite newer data or
  render a failure for data that already arrived.
- Writes need an idempotency key or guard, or "retry" duplicates the viewer's action. If the outcome
  is genuinely unknown, that's a state — verify, then offer, don't assume either way.

## Perception and operability, per state

Platform-neutral obligations first, then the carrier the platform provides.

- **The state must be announced where announcements exist.** Non-blocking changes → polite; blocking
  failure and data-loss risk → assertive. Never assertive for a background refresh, and never announce
  on every keystroke — announce the settled result.
- **When content is replaced, move focus** to the state block or its control, and return it on
  recovery. Otherwise a keyboard, d-pad, remote or screen-reader user is left wherever they were on a
  screen that no longer contains it.
- **Every signal needs a text equivalent.** A state known only by colour, glyph, position, or animation
  is unreadable — including for the person on a monochrome display, in sunlight, or with the display
  mirrored.
- **Every recovery control is a real control**: reachable by the platform's non-touch paths, named,
  sized for the input method in use (a 12px retry link is unreachable on a touchscreen in a moving
  vehicle), and operable without a hover state.
- **Don't make a state dismissible only by an action the state has disabled.**
- Read the platform's accessibility contract before implementing rather than assuming the web's: ARIA
  live regions, Android `TalkBack`/`Explore by touch`, iOS VoiceOver/`accessibilityLabel`,
  Windows UIA automation peers, macOS `NSAccessibility`, TUI — screen-reader-friendly text output and
  `NO_COLOR`/`TERM` honesty, plus a non-colour channel for every distinction.

## Forcing a state (required for D3)

A state nobody has rendered is a state that doesn't work. Whatever the platform, **the trigger is
simulatable even though the data must never be faked in production code**:

| To force | How, in dev builds |
|---|---|
| high latency / slow link | network conditioner, OS traffic shaping, proxy with artificial delay, emulator radio profile — measure at ~1 s, ~8 s, past-budget |
| no connection | radio off / airplane mode / block the host at the resolver or firewall / pull the cable / stop the container |
| provider down or degraded | stop the dependency, kill the port, return a contract-violating fixture, open the circuit deliberately |
| throttled | drive the quota counter, or return the "later" outcome from a mock |
| expired session / revoked entitlement | shorten the token TTL, revoke from the admin surface, expire the licence |
| permission revoked after grant | OS settings, then return to the screen mid-use |
| device lifecycle | suspend/resume, background/foreground, force-kill then relaunch, lock/unlock, thermal or low-power mode |
| storage full | fill the volume, or lower the simulated quota |
| unknown enum / malformed payload | a fixture or mock returning a value outside the contract — the single most valuable test in this family |
| clock skew | move the system clock forward/back across a countdown or freshness boundary |
| race / late arrival | inject delay into one of two calls, then navigate away before it lands |
| a whole state at will | dev-only state override: URL query param, launch argument, env var, dev menu, hidden gesture, key binding |

Build the override **once, in the shared layer**, so every screen gets it for free — that's the
cheapest D3 in the product, and its absence is why states rot.

## Anti-patterns — check your own work

1. Boolean soup — several flags reconciled at render time (`precedence-resolution.md`).
2. `else` renders the happy path; unknown values render as defaults; missing fields render as zero.
3. A placeholder whose height doesn't match the content, or a determinate bar with no numerator.
4. A failure state with no action, or with several actions of equal weight.
5. Retrying a non-retryable outcome; unbounded silent retries; a progress state that can outlive its
   request.
6. One generic "something went wrong" for `refused`, `absent`, `unreachable`, and `failed-server`.
7. Empty state that ignores an active filter, and invites creating what was filtered out.
8. No-connection rendered as empty; empty rendered as failure.
9. Optimistic update with no rollback path — the UI asserts a success the provider refused.
10. A transient notice as the *only* record of a failure or of a security event.
11. Per-screen bespoke versions of a shared state shell — implemented twice, diverged by next month.
12. A disabled control with no reason, and no platform-disabled semantics.
13. A state with no dev trigger, therefore never seen, therefore broken since the refactor.
14. Motion or colour as the sole carrier of meaning.
15. Integrity failure sharing a message with ordinary failure — teaching the user to retry through it.
16. Detail leaked into user-facing copy "to help support" — internal topology, other viewers' ids.
17. Faked data in real source to make a state look designed. It ships as a lie.
