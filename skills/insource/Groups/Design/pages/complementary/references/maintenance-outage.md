# Maintenance & outage

**Output contract:** this file owns content laws only. Registration is one PAGES.md §6 row per `anatomy.md`; canon location and build follow `../../references/output-contract.md`.

**Trigger:** operator-controlled truth — a flag, a feature kill-switch, a deployment window,
or a degradation the backend knows about. Without such a switch there is no page in this
family to design (`catalog.md` detection evidence); building an outage page nobody can flip
on is decoration for a fire that cannot happen.

**The two flavors are different jobs:**

- **Scheduled maintenance** — known in advance, shown with a *window*: "back by 03:00 your
  time", in the person's timezone, stated before they lose access, not after. Works saved
  or lost — said explicitly.
- **Unplanned outage/degradation** — unknown end; **never a time promise**. "We know, we're
  on it, last update HH:MM" with a real update source. Confidence beats comfort: the page
  either knows something or says it doesn't.

## Laws specific to this family

- **The page must survive the outage** — serve from whatever still works: static HTML
  reachable when the API is down, cached at the edge, no dependency on the broken service to
  render "the service is broken". This is the family's engineering constraint, not copy.
- **State what is affected** — reads vs writes vs just billing jobs; a product that says
  "everything is fine except exports" keeps people productive; a vague "we'll be back" idles
  everyone.
- **Pointer, not duplication** — the public status *document* belongs to `/pages secondary`;
  this interstitial links it and shows the operational truth the app has (per-feature flags,
  ETA when real). One owner per fact.
- **Return honesty** — when the switch flips off, what was mid-flight? Writes queued or
  refused must be stated from the queue's truth, never assumed; the resume story belongs to
  `session-gates` when it's an auth question and to this page when it's a durability one.

## Anti-patterns

The 503 styled as the app's own shell (renders the lie that the app is up); cute downtime
theater (status pages get read seriously — humor is fine, ambiguity is not); countdowns that
keep counting after the window passed; maintenance banners the ops team cannot actually
toggle (trigger without a condition source = anatomy violation).