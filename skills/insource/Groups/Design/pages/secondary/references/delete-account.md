# Delete account

The exit door. On mobile platforms this moved from courtesy to requirement: [Apple] and [Google
Play] policies demand in-app deletion for apps with account creation - a store review will reject
the product without it (web surfaces should offer it anyway; trust is the reason).

## Must include

1. **The route, on this surface** - the self-service path inside the app/web (Settings → ... →
   Delete), not just an email request; the page states the real click path for the platform it is
   written for (the same document text, platform-specific route lines from config - canon rule).
2. **What deletion does, by data class** - the honest map: deleted immediately (profile, content,
   sessions), deleted within N days (backups), kept with the reason and the period (billing
   records where law requires, abuse-report logs). Every number comes from
   `privacy-policy.md`'s retention table - one owner; this page narrates it for the leaving user.
3. **What happens to content others can see** - posts in shared spaces: deleted, anonymized, or
   kept - the product's real policy (ASK; this question generates support tickets).
4. **The window** - immediate or N-day grace ("log back in within 30 days to undo" only if the
   backend can honor it).
5. **Before you go** - export pointer (`data-rights.md`).
6. **When self-service is impossible** (federated/sponsored accounts): the exact request channel
   and the real response window - stated, not hidden.

## Writing professionally

- Zero dark patterns: no retention-plea gauntlet before the delete button; the page is the door,
  not the argument.
- Deletion is a claim about the backend: every sentence here must match what the code actually
  does - verify against the implementation before publishing, or say `pending`.

## Ask the user - never invent

Grace period; content-of-others handling; the kept-records list with legal reasons; whether
self-service exists today; store obligations (the ASK is quick, the rejection is not).
