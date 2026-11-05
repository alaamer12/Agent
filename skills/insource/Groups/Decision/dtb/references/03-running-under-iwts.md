# Running under iwts (and alone)

dtb is the **decision method**; [`iwts`](../../iwts/SKILL.md) is the **ownership contract**. One skill answers
"how do I choose well and what do I owe the reader"; the other answers "may I choose at all, and when do I stop
and wake the user". Neither duplicates the other, and an iwts run without dtb's discipline produces confident
unrecorded choices — which is the failure mode this file exists to prevent.

## Division of labor

| Question | Owner |
|---|---|
| may the agent decide this without asking | **iwts** (the authority line applies in both modes, but iwts defines stop conditions) |
| how to enumerate the real systems behind a requirement | **dtb** |
| how to compare options and pick | **dtb** |
| where files live, how state survives a dead session, task separation | **iwts** |
| what a decision record must contain | shared: the template is `../iwts/assets/decision-record-template.md` — one copy, linked, never forked |
| when to stop: completion vs a user-owned call | **iwts** |
| when the change is a requirement change, not an implementation change | **dtb** ([`00`](00-the-authority-line.md)) |

## The shared path

dtb and iwts are **thin operating modes** - they decide how to operate anonymously; the *recording
convention* belongs to the project's rulebook (agents-md's Ambiguity section). Both skills write to the
same place, so the user finds one ledger, not two:

```text
<docs>/decisions/               <docs> = wherever the project keeps its docs; create docs/ if none
  states.md                     the run ledger: status, remaining, decisions as links, uncertainties, findings
  <slug>.md                     one file per lasting decision (dtb's template defines the content)
```

- **One file per decision, always.** A combined `decisions.md` is the explosion anti-pattern - the index
  role belongs to `states.md`, never to a growing document.
- Each record carries its **anchors: Date + Commit hash + App-Version** (version stated whenever it changed
  between decisions) so any record can be placed on the timeline exactly.
- **The ask-or-decide call is itself a decision:** what was decided without asking, what was assumed because
  the user was asleep - recorded, because that is the first thing the waking user audits.
- If the project's `AGENTS.md` names another decisions location or ADR numbering, **it wins**; follow it.
  If no docs folder exists anywhere, create `docs/decisions/` and say so in one line. Records written there
  are normal repo content - commit them with the work; there is no staging folder and no later "move".
- If neither iwts nor an AGENTS.md is active, the same default applies in a supervised session; most
  decisions still stay in the conversation - only lasting ones earn a file.

## What changes when nobody is awake

The method is identical. The **duties** around it get heavier, in three specific ways:

1. **Record more, because there is no conversation to consult.** In a live session the user watched you choose;
   unsupervised, the file is the only surviving evidence. Any decision that is architectural, behavioral, or
   hard to reverse gets a record — and one you would have mentioned out loud counts.
2. **Flag uncertainty in `states.md`.** The `uncertainties:` line is where a guess with thin evidence goes, plus
   what measurement would overturn it. An unflagged guess becomes a fact the next run builds on.
3. **Park, do not fix, unrelated discoveries.** Autonomy plus good taste is a tempting engine for scope creep:
   the `findings:` list is where "this would be better" goes when it is not required for the objective.

And the stop conditions stay **iwts's**: stop only for completion, or for a call that genuinely belongs to the
user — irreversible destruction with unclear intent, external consequences (pushes, publishes, purchases), real
cost, missing authorization, or ambiguity where the options would *materially* change the outcome. A dtb-quality
judgment about internals is never a reason to wake someone; "which of these two fine designs do you prefer" is
exactly a reason to write a proposal in the state file and keep working the internals.

## Reporting decisions back

When the user wakes, or at the end of a supervised chunk, each lasting decision is **one line** — never a
lecture, never silence:

```text
<what was decided> because <the two criteria that decided it>; cost: <what it gives up>;
reversal: <the one boundary to touch>
```

> Aggregation happens at write time, into a per-day totals table, because the dashboard reads on every request
> and the source rows are append-only; cost: writes now touch two tables and a backfill ran once; reversal: the
> `recompute_range()` adapter, ~1 file. Uncertain: assumed rows are never edited — if they are, this becomes a
> read-time job.

Three parts plus the uncertainty. If a line cannot be written this way, the decision was either too small to
record or not understood well enough to have made.

## Deciding on behalf of a sleeping user — the extra cautions

- **The visible surface is where mistakes become expensive.** A wrong internal choice is fixable quietly; a
  changed user-visible behavior is discovered by the user in front of the product. Under autonomy, keep the
  design contract *tighter*, not looser ([`00`](00-the-authority-line.md)).
- **Prefer the reversible option between two goods.** Reversibility is worth more when nobody is there to
  re-decide; say so in the record and note the seam you kept.
- **Never adopt a dependency, a service, or an operational obligation silently.** Those are costs the user
  carries after they wake. Add a dependency only when the requirement genuinely needs it, and put it in the
  summary as a line.
- **Do not confuse "the user gave freedom" with "the user gave blank check".** Freedom over implementation is
  the delegation; the vision they described stays the constraint. If a decision would make the result look or
  behave different from what they asked for, that is a proposal in the state file, not a choice.
