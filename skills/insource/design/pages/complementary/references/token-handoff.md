# Token handoffs

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** a one-time link landed — email verified, invitation accepted, password reset
done, magic sign-in completed. The token *worked*; the page acknowledges the moment and hands
the person into the flow the token was *for*.

**This family is small and where most products waste it:** the acknowledgment exists because
the person just clicked an unknown link from an email and needs to know *the click did the
thing*, then needs to not wonder what next. Two jobs, one screen, thirty seconds of
attention.

## Laws specific to this family

1. **Verify server-side at render** — token state (used, expired, forged) comes from the
   condition source, and the three failure classes get their own answers, designed here
   because they arrive here constantly: *expired* (resend path with its real rate limits),
   *already used* (the action's result, if viewable, plus onward — double-clicking email links
   is normal human behavior, punish nobody for it), *invalid/foreign* (the error family's
   honesty, no detail leak).
2. **The onward is the point** — verified → into the app *at the purpose of verification*
   (the email-change confirm lands on settings, not the dashboard); invite accepted → the
   workspace the invite named, straight into onboarding-of-that-space (`onboarding.md` seam);
   reset done → signed in, if policy permits, or login with the success pre-announced. A
   handoff page with only "thank you" and no destination is a dead end wearing manners.
3. **Single-use is single-use** — the page never re-activates the token; replay shows the
   already-used answer. And nothing sensitive prints on the acknowledgment: no full email the
   link was sent to beyond what the session proves, no token fragments in copy.
4. **Expired is not denied** — the access-gates family answers "not yet allowed"; here the
   condition itself died, and the copy difference ("this link expired" + new one arriving in
   under a minute, *with its real delay*) must not read like the lock page.

## Anti-patterns

Redirecting verified → login → dashboard, teaching the user nothing about what the click
achieved; showing a success for a token whose verification failed and got silently ignored;
welcome-to-team pages that are actually onboarding with the name swapped — run
`boundary-test.md` and let each step belong to its family; "check your email" loops when the
token page can see the email was already confirmed.