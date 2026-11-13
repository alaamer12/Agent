# Transaction success

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** server-confirmed completion of a consequential, ideally irreversible action —
payment settled, order placed, filing submitted. The provider's return URL is a *request to
verify*, never the confirmation itself.

**The one sentence that matters most:** this page exists at the exact moment the person most
wants to believe it worked. That trust is the page's whole budget — spend it on *proof*, not
celebration.

## Must-haves

1. **Reference artifact** — order/receipt id, amount, timestamp, method tail, the thing the
   person will be quoted back at them later. Absence of proof here reads as failure to the
   anxious user and fraud to the careful one.
2. **Delivery promise** — where the receipt is going, to which address, by when; if the
   product emails nothing, say nothing about emails.
3. **Next true action** — the honest continuation: track order, download invoice, add to
   calendar. If there is none, home.

## Laws specific to this family

- **Re-verify on render** against the condition source (order status endpoint, not the URL's
  `?success=1`), and design for the three wayward arrivals: bookmark-and-return-months-later
  (still true, still shows), replayed return (idempotent — same answer, zero re-capture),
  deep-link while logged out (login via `session-gates`, *resume here*, never lose the proof).
- **Confetti is seasoning** — a celebration for a first-time/irreversible milestone is fine
  *after* the proof block, dismissible, never blocking, and `prefers-reduced-motion` honored
  (a shaking screen reads as a crash to some, and reads as broken to their assistive tech).
- **Never claim what the system cannot know yet** — "your order ships today" only if the
  backend actually set that. The success page overstates; the support ticket undercuts; the
  product loses both times.
- **Upsell only after the receipt is readable**, one slot, relevant. This page has the
  project's best conversion heat and the worst trust fragility — one greedy banner poisons
  both.

## Anti-patterns

Redirecting straight to dashboard "because success is its own reward" (that is the dead-end
law inverted: no proof surface, no recovery anchor, and support loses the reference id);
fireworks loop as the hero; showing the card number tail the person never entered this
session; a second pay button "to confirm" on a settled payment — capture here is a
double-charge with a party hat on.