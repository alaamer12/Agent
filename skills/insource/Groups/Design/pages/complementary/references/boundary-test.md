# The boundary test — is this page in this family?

Three questions, all must be YES for a page to belong to this mode:

1. **Conditional display:** does it appear only when a specific triggering condition occurs —
   not by navigating to it in the normal flow?
2. **Dispensability:** can the application operate normally with this page removed entirely?
   (The product still works; the person just loses the *acknowledgment of the moment*.)
3. **Outside ongoing navigation:** is it absent from the normal flow a returning user travels
   day to day? It is a detour the app takes *because something happened*, not a destination.

All three yes → this family. One no → name its owner and hand it back, out loud:

| candidate | verdict | why |
|---|---|---|
| Signup / login | **main** — `/pages main` | reachable anytime by navigating; no special condition. Being *used after* an event does not make a page conditional |
| Dashboard (requires account) | **main** | a prerequisite is not a trigger — "requires login" describes every main page of an authenticated app |
| Payment success page | **complementary** | appears only after a completed transaction; app fine without it |
| Payment failure page | **complementary** | appears only on failure; carries the exits |
| 404 / 500 / offline page | **complementary** | appears only when something broke or is missing |
| Onboarding / first-run | **complementary** | appears only while "new and not yet set up" is true; normal app runs without teaching it |
| Email-verified confirmation | **complementary** | appears only after token redemption |
| ToS / Privacy / Contact | **secondary** — `/pages secondary` | always reachable, never conditional |
| Status page | **secondary** | public always-there document; the *in-app outage interstitial* is complementary |
| Settings → profile | **main** | navigable anytime |
| Empty state on a list | **not a page at all** | a state inside a screen — the owning page's skill handles it |
| Forgot-password screen | **main** (usually) | user-initiated recovery flow, navigable to; only its *completion acknowledgment* ("reset done") is complementary |
| Checkout | **main** | the core flow itself; its outcome screens are complementary |
| OAuth/SSO callback relay, payment return pad, post-logout landing | **complementary** — the relay deviation | conditionally *landed on* by machinery, absent from navigation absolutely; the visible surface is fully dispensable (its blankness is the feature) — see `relay-redirect.md` for why question 2 applies to the surface, not the endpoint |

Two traps that fail the test in disguise:

- **"It appears after something"** — login also appears after a session expires; that is the
  trigger belonging to *this* family (session-gates), with login as the destination *outside*
  it. The condition-acknowledging screen is complementary; the ordinary flow it points into
  is not.
- **"It is rare"** — rarity is not conditionality. An obscure settings sub-page reached by
  deep nav is main; a page no one can navigate to *unless state says so* is complementary.

When a page straddles (onboarding ends by navigating into the app), the boundary is drawn per
*screen*, not per *journey*: each step that only the condition produces is one page of this
family, each step reachable normally belongs to `/pages main` — and PAGES.md records both
sides of the seam.