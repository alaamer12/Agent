# Case 5 - no outbound network on the target machine

**The ask:** "the service must fetch live exchange rates, but the box it deploys to is air-gapped."

## Goal, separated

```text
GOAL  : money amounts convert correctly, and nobody has to remember yesterday's rate
VALUE : a rate table that is current enough for the business rule attached to it
TEST  : conversions match the reference rate within the tolerance the finance rule allows,
        and the staleness of the rate used is always visible to the person approving the transfer
```

Freshness is not a constant; it is a number that belongs to whoever consumes the conversion. Naming it turns
an "impossible" requirement into a design decision.

## Block verification

Outbound connections are policy-blocked at the network layer and no proxy is allowed. Confirmed: a connection
test fails, and the infrastructure owner states the rule in writing. This is not a capability limit and not a
parity problem - it is an authorization boundary *the user's own organization* set. Trying to route around it
is exactly what the hard line about acting beyond what you're authorized to do forbids, even though nobody
outside is being harmed.

## Routes

| Route | Family | Verdict |
|---|---|---|
| A networked build/ingest node fetches the table hourly and drops it into a mount the service reads | reshape | chosen |
| Bundle a published, dated rate file with the release artifact and update it per deploy | reshape | chosen for the slow-changing currencies |
| Use a rate source that the infra team already mirrors internally | reroute | best when it exists; ask before assuming it doesn't |
| Let an operator enter today's rate in an admin screen, with a loud staleness warning | reduce | fallback, and honest |
| Open a covert channel through an allowed host to reach the internet | rejected | defeats a protection that exists on purpose; not a route |

## Chosen

Pull on the networked side, publish into the air-gapped side, service reads a local table with a
`rate_as_of` column that the UI shows. The feature works, the policy holds, and the freshness question is
answered on screen instead of in a Slack message at 2am.

## Said out loud

The rate can be up to N hours stale, tolerance is X, and who accepted that is recorded. When a future
compliance change allows a curated mirror, the ingest job shrinks - the architecture already has the seam.

## What this case teaches

Two things. A block set by the user's own organization is still a hard stop, and the reshape family usually
has an answer - "live" is very often "current enough, fetched somewhere else".
