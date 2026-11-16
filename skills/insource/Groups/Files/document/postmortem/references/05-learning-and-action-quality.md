# Learning, and action quality — why most postmortems change nothing

A postmortem is not a document, it is a feedback loop: incident → understanding → changed system → a different
future incident. The loop breaks in predictable places, and each has a fix.

## The second story

Blameless does not mean "no people in the document". It means the *analysis* never ends at a person.

Dekker's **second story** (popularised for engineering by John Allsop's Etsy work): the first story is "the
operator rolled back the migration and made it worse". The second story asks what the operator saw, believed and
was trained to do — the alert that said "replication lag", the runbook step that said roll back, the pager at
03:11, the last similar incident where rolling back *did* help. In that story the action was **rational** given
the information available; the defect is that the system presented that information and that runbook.

```text
first story:   operator error            -> no action possible except "be careful"
second story:  local rationality         -> actions: fix the alert, fix the runbook, fix the load path
```

Write it as a table (§8 of the template): human step → what they saw → why it was rational → what the system
should have shown or prevented. No names.

**Blameless ≠ accountability-free.** The *analysis* is blameless; the *follow-up* is owned. An action item with
"the team" as owner is an action item nobody owns.

## Why postmortems become ritual

| Symptom | What is really happening | Fix |
|---|---|---|
| Document is thorough, nothing changes | actions are vague ("improve monitoring", "be more careful") | every action names a command, an alert string, a test, or a diff |
| Same incident recurs, each has its own postmortem | no link between them; the pattern tag in §7 is never searched | tag → trend query → a single recurring-pattern owner |
| Actions pile up forever | 20 actions, none finishable in a month | cap at 8, prefer small, ship within 30 days |
| Actions close on status change | "done" means the ticket moved | close only with evidence of the definition of done |
| Nobody reads it | published in a place the team does not use | publish where work happens + link from the tickets |
| Only the author understands it | written as a personal narrative, not a traceable record | §18 narrative + artifacts index + permalinks |
| Review is a rubber stamp | reviewer only reads | reviewer re-runs at least one command |

## Action-item rules

1. **At most 8.** Past that, the list is a wish. If the incident genuinely produced more, fold related items into
   one with a checklist inside it.
2. **At least one `mitigate` and one `prevent`** — Google's postmortem guidance asks for actions in at least
   these two categories: what limits the next blast radius, and what makes the defect impossible or caught at
   build time. `detect` and `learn` are additional, not substitutes.
3. **Finishable within 30 days**, or explicitly marked long-running with an interim mitigation.
4. **One named owner** — a person, not a team. The team can share the work; it cannot own the ticket.
5. **A verifiable DoD** — a command that exits 0, an alert that fires in a staged test, a test that fails on the
   old SHA. "Documented" is not a DoD unless the document is the deliverable and its location is stated.
6. **Verified by someone else** — the "Verified by / date" column stays empty until a second person checks the
   DoD. This is also the cheapest defence against the completion gap below.

## Metrics for the loop, not for vanity

| Metric | Definition | Reasonable target | Why it matters |
|---|---|---|---|
| Time to publish | incident end → postmortem published | ≤ 5 business days (3–7 is the common window) | memory decays; a late postmortem is archaeology |
| Action completion | actions done by due date | > 90% | the loop's actual output |
| Verified completion | closed actions with evidence of DoD | trending to 100% | separates done from marked done; a low verification pass rate (< 80%) signals execution-quality problems |
| Recurrence | incidents sharing a §7 pattern tag | < 10% | the only metric that says prevention worked |
| Review depth | reviewer commands re-run per postmortem | ≥ 1 | reading is not reviewing |

Publish these per quarter, not per document; the point is the trend, and a target of zero postmortems is a
target of zero recorded incidents.

## The review meeting

Thirty to forty-five minutes, agenda fixed:

1. Author walks the causal chain in five minutes (not the whole document).
2. Reviewer's four checks: every claim has a source · the V-level matches the evidence · no sentence blames a
   person · actions are few and verifiable.
3. Reviewer re-runs one command and states the result aloud.
4. Owners confirm dates they can actually meet; anything unmeetable gets a smaller action now.
5. Publish, link from the tickets, set the 30-day check.

Half of the value is in step 2 — the author hears which claims were unsupported, which is exactly the list of
things to fix before publishing.

## What "change nothing" looks like, precisely

- A postmortem whose actions are all `learn` (a doc, a meeting) and none `prevent`/`mitigate`.
- A root-cause sentence that ends at a person's name or at "human error".
- A V-level claimed without N, or a V5 claimed while the shared state that caused it still exists.
- A timeline that stops at detection because nobody kept the earlier timestamps.
- An action table identical to the previous incident's action table.

If any of these is present, the postmortem is a record of an incident, not a change to the system — say so in
review rather than publishing it as learning.

## Sources

- Google SRE Workbook, *Postmortem Culture: Learning from Failure* — ownership and concreteness of action items;
  actions to mitigate and prevent. <https://sre.google/workbook/postmortem-culture/>
- Google SRE Book, *Postmortem Culture: Learning from Failure* — blameless framing and template metadata.
  <https://sre.google/sre-book/postmortem-culture/>
- Lunney & Lueder, *Postmortem Action Items*, USENIX ;login: (2017) — action categories and tracking.
  <https://www.usenix.org/system/files/login/articles/login_spring17_09_lunney.pdf>
- incident.io, *SRE incident post-mortem best practices* (2026) — measuring effectiveness: action completion,
  recurrence. <https://incident.io/blog/sre-incident-postmortem-best-practices>
- SRE.wang, *Postmortem Action Items Tracking* (2026) — verification pass rate as a quality signal.
  <https://www.sre.wang/en/posts/sre-postmortem-action-items-tracking/>
- Pertama Partners, *AI Incident Post-Mortem* (2025) — 3–7 day publication window, > 90% on-time completion,
  < 10% recurrence.
  <https://www.pertamapartners.com/insights/ai-incident-post-mortem>
- Dekker, *Just Culture* / Allspaw's second-story framing — used above as the reasoning model, not as a mandate.
  <https://www.sherlocks.ai/blog/blameless-postmortems-explained-lessons-from-real-outages>
