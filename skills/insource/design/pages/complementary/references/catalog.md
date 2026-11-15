# Catalog — the families of conditional pages

Present this against the project's real flows; propose only what can actually trigger, ask
which to design, record what is skipped and why. Each row links its method file.

| family | trigger condition | normal exits | reference |
|---|---|---|---|
| **Onboarding & first-run** | new account / fresh install / setup incomplete | complete setup · skip · resume later | `onboarding.md` |
| **Transaction success** | server-confirmed completion of a money/irreversible action | view receipt · next natural action · back to flow origin | `transaction-success.md` |
| **Transaction failure** | server-confirmed failure or timeout of the same | retry (per contract) · change method · abandon safely | `transaction-failure.md` |
| **HTTP / runtime errors** | bad route, server fault, lost connection | guided recovery: search · popular destinations · home | `http-errors.md` |
| **Session gates** | expired session, re-auth required, pending verification between steps | re-login / verify, *then resume where interrupted* | `session-gates.md` |
| **Maintenance & outage** | operator-flagged downtime, feature kill-switch, degradation | retry later · status info (pointer to pages secondary' status doc) | `maintenance-outage.md` |
| **Access gates** | locked account, plan/region/seat not entitled, consent outstanding | the one action that opens the gate: upgrade · request · consent · appeal | `access-gates.md` |
| **Token handoffs** | one-time link landed: email verified, invite accepted, reset done | onward into the flow the token was for | `token-handoff.md` |
| **Relay redirects** | machinery landed the return path: OAuth/SSO callback, provider return URL, post-logout landing | validated forward to an allowlisted target — designed not to be seen | `relay-redirect.md` |

Detection evidence per project (audit inputs, never guesses): route table for outcome/error
paths, webhook/return-url wiring for transactions, auth middleware for session gates,
feature-flag/config surface for maintenance, billing entitlement checks for access gates,
mail templates for which tokens exist at all.

Order of proposing: failures before successes (a product must handle wrong before it celebrates
right), errors before onboarding (broken paths exist in every app; a teaching flow may not).