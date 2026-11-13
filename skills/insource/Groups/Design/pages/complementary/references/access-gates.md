# Access gates

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** the person reached a real door that is currently locked *to them* — account
locked, verification outstanding, plan/seat/region not entitled, consent not yet given. The
app is healthy; their permission is the missing condition.

**The tone law:** this page must not read like an accusation. Locked-for-security and
not-in-your-plan are emotionally opposite — anxious vs slighted — and both are handled by
people trained to be defensive. The page owes the person three things, in order: **what is
true, what they can do about it, how long that takes.**

## Per-class anatomy

| class | truth | the one action | fallback |
|---|---|---|---|
| **locked / suspicious activity** | what locked it (as much as security allows), whether data is safe | unlock flow (verify identity), or support if self-service impossible | appeal path with hours stated honestly |
| **verify-first (email/phone/ID pending)** | what is pending, what was already sent (resend obeys rate limits, says so) | complete verification → onward per `token-handoff` | "didn't receive it" path designed *here*, not discovered in support |
| **entitlement gate (plan/seat/region/feature flag)** | exactly what is missing and what they already keep working | the single upgrade/request action that opens *this* door | who to ask (admin/contact) when self-serve doesn't exist |
| **consent/terms outstanding** | what changed, what is being asked, what happens on decline | accept/decline with decline's real consequence honored | the document itself, linked not restated (`/pages secondary` owns the text) |

## Laws specific to this family

- **One gate, one action** — a page offering three exits for four lock reasons is four pages
  or one router that knows which. The condition source says *which* gate this is; generic
  "access denied" walls fail the anatomy.
- **Show what still works** — entitlement gates especially: the person keeps their account,
  their data, their other features; the page says so, or they assume the lock is total and
  churn.
- **Never gate the escape** — support contact, data export, account settings (including
  *downgrade/delete*) stay reachable through every gate; a lock that also hides the key is a
  hostage page, and for delete-access the law agrees.
- **Region/availability truth** — "not available in your country" needs its source (real
  regulatory constraint stated plainly, or the product is lying to itself) and an honest
  horizon: no date unless there is one.

## Anti-patterns

Upselling as the entire content of a security lock; "contact support" as the only exit for a
condition the backend could resolve with a resend; consent gates that bury decline as a tiny
"no thanks"; the locked user seeing the login form again as if that were the new information.