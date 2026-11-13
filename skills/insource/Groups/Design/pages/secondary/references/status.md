# Status page

The availability truth: is it down now, what broke this week, what happens next time. For hosted
products this page is a component of the service, not marketing.

## Must include

1. **Current state, one glance** - overall + per-component; vocabulary fixed:
   [Operational] / [Degraded performance] / [Partial outage] / [Major outage] / [Under maintenance].
   Colors never carry meaning alone (screen-reader parity).
2. **Incident lifecycle** - investigating → identified → monitoring → resolved, with timestamped
   updates and a promised cadence while active ("updates at least every N minutes" - the real
   number).
3. **History** - the last 90 days visible, older archived; each closed incident gets a summary,
   and a postmortem link for anything customer-visible (the `postmortem` skill's documents are the
   detail, this page holds the index).
4. **Subscriptions** - email/RSS/atom per component; the promise that subscribers see updates first.
5. **Maintenance** - scheduled with start + expected window + affected components, posted N days
   ahead (ASK how many).
6. **Machine-fresh** - the status feed must NEVER cache stale state; noindex the page (a status
   page outranking itself in search is how users find last month's incident as current) and link
   it from the app's error screens.

## Extra over the engineering contract
(The build story is owned by `engineering.md` per `../../references/output-contract.md`; this is what a status page adds on top of it.)

- Running the status page inside the app it reports on is the structural failure: if the app is
  down, status must not be. Options: separate host/domain, or a provider ([Instatus], [instatus
  clone], [hosted status pages]) - the choice is the user's (ASK).
- The app's error states link here with the component preselected when known.

## Ask the user - never invent

Component map; update cadence; subscription channels; who on-calls it; hosting decision; the
real incident history to seed (never fabricate a "no incidents" archive).
