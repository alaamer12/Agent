# /mine — case-mining: collect the concrete situations, make each one usable

This file covers the third way to interrogate a topic. `workflow.md` and
`search-and-mining-technique.md` describe **read-mining** — reach a source,
census it, chase its *why*, write a checkpoint — which answers "what does this
class of thing look like, and why." `run-mining.md` describes **run-mining** —
put each candidate through an identical trial — which answers "which of these
is best, prove it." A third class of task wants neither a description nor a
ranking; it wants **the enumerable list of concrete situations, each with how
you actually handle it**:

- *"Mine 50 cases on how to debug hard-scenario debugging."* — attach to a
  running process, a failure that surfaces only after 100 hours, a `.dmp` /
  core dump, a Heisenbug that dies under the debugger, a distributed trace that
  vanishes at the service boundary, a stack that only breaks under load.
- *"Every way this API fails, and what to do about each."*
- *"The hard migration cases for moving this system off the old schema."*
- *"Collect the incident cases for this class of outage into a triage playbook."*

For these the unit of work is not a *source* and not a *candidate to rank* — it
is a **case**: one distinct, self-contained situation plus the handling that
belongs to it. This is **case-mining**: enumerate the real space of situations a
topic can present, obtain the handling for each (from sources that attest it, or
by reasoning the space where no source bothers to write it down), keep them
genuinely distinct and genuinely hard, and end with a **catalog** a person can
pick a case out of and act on. `/mine` does all three methods; which one a task
wants is settled in Phase 1 (see `workflow.md` → "Settle the mining method and
the candidate provenance first").

The examples here are debugging because that is the task that surfaced this
mode — but nothing below is about debugging. It applies to whatever has a space
of concrete cases to enumerate: failure modes, edge situations, support-triage
scenarios, security-hardening cases, migration paths, data-quality breaks,
browser/platform quirks, protocol error conditions, CTF categories. Wherever the
deliverable is "show me the distinct situations and how to handle each," not
"explain the field" (read) and not "pick a winner" (run), this is the mode.

## Case-mining is not a separate skill — it reuses the whole spine

Everything structural in `/mine` still applies, with each piece given a
case-mode reading. Do not fork a parallel process; map onto the existing one:

| Read-mining piece | What it becomes when you mine cases |
|---|---|
| The candidate list (Phase 1) | The **case list** — and the count is a *coverage target*, not a number to hit by padding (see "Coverage is the whole game") |
| What a source is | A source is **evidence for cases**, not a candidate itself: one postmortem may yield four cases, and one hard case may be assembled from three writeups. The mapping source↔case is many-to-many, and that is the whole difference from read- and run-mining. |
| The ground census (Phase 2) | The **coverage map**: how many cases, spread over which scenario families, what share attested vs derived, which families look thin, what got deduped away. This is the case-run's quantitative spine, exactly as the file count is a read source's. |
| The source ledger (Phase 2) | The **evidence per case**: an attested case carries the source URL(s) that document it (commit/thread/postmortem-pinned); a derived case carries the *derivation* (which axes it falls out of, and why it must be possible). An evidenced case is a fact; an unevidenced one is a guess wearing the catalog's clothes. |
| The what→why→cost chase | The **situation→recognition→handling→cost chase**: what the case looks like from the inside, how you *know* you are in it, the diagnosis/handling path that actually works, and what that handling costs or breaks (the tool that needs symbols, the attach that stalls the process, the technique that only works if you reproduced it locally). |
| The checkpoint file | A **case card** — one per case, same durable-notes purpose and same self-sufficiency test: could a reader who has never seen the topic act on just this card? |
| The distillation (Phase 4) | The **case catalog** — see "What case-mining ends in" below. |
| Solo / subagents | Unchanged; fanning out is *more* natural here — one subagent per scenario family, each returning its family's cards, is the within-fan-out shape this skill already supports. |

The budget discipline is unchanged in spirit but shifts where it bites: the
expensive unit is no longer "reading one more file" or "building one more
candidate" but "attesting and de-duplicating one more *case*" — reaching the
sources that document a situation well enough to state its handling truthfully.

## Where cases come from: attested vs derived

Read-mining always *finds* sources; run-mining splits found vs authored. Cases
split along the same fault, but the two halves mean something specific here:

- **Attested cases** are documented somewhere real — a postmortem, a bug
  tracker, a Stack Overflow thread, a war-story blog, a vendor's troubleshooting
  guide, a book's case study, an RFC's error conditions. Discovery is the normal
  Phase 1 candidate search *across those ecosystems* (`source-ecosystems.md`:
  postmortems/org writing, discussion corpora, documentation sets' troubleshooting
  pages, bug trackers, research on the failure taxonomy). You reach the source,
  read it for *the situation and the handling*, and lift the case with its
  evidence. This is read-mining serving as the raw material for cases — case- and
  read-mining compose the way run- and read-mining do.
- **Derived cases** are ones you reason out of the *scenario space* when no
  source bothers to write them down — "a failure that only appears after 100
  hours" is real whether or not someone blogged it. You derive a case by walking
  the axes (below) and asking what combinations *must* be possible; you then
  label it `derived`, and it is weaker than an attested case precisely because
  nothing external vouches for it. Derivation is legitimate; passing a derived
  case off as attested is the case-sized version of the invented ledger.

A healthy case-mine is **mostly attested, with a derived minority** to fill the
holes the field leaves unwritten — and the coverage map says which is which, so
the reader can weigh the catalog accordingly. A catalog that is *all* derived is
a list of plausible-sounding guesses; a catalog that is *only* what one blog
happened to cover is missing the hard cases nobody found clever enough to write
up. Seed the derived space *from* attested cases (the writeups teach you the
axes), then enumerate.

## Coverage without duplication is the whole game

A case-mine earns trust exactly as far as its list is a *map of the real space*
and not the first N things that came to mind. Padding to "50" with fifty ways to
say "check the logs" is the failure this mode exists to avoid, and it is the
direct analogue of run-mining's fairness rule — do this part wrong and the
number on the deliverable is theatre. The parts:

1. **Enumerate the space before you fill it.** Fix the *scenario axes* the topic
   actually turns on, then generate cases across them — do not free-associate
   until a count appears. For hard debugging the axes are things like: *phase*
   (repro → localize → inspect → confirm → fix), *environment* (dev vs prod,
   attached vs offline, single vs distributed, under load vs idle), *artifact*
   (live process, core/`.dmp`, log stream, trace, reproduced VM), *time/trigger
   shape* (deterministic, intermittent, after-N-hours, race, clock/calendar),
   *observability* (visible in metrics, only in a heap, only in the wire). Every
   case sits at a point in this grid; the coverage map is the grid with its
   occupied cells. Set the axes from the sources you read, not from a generic
   checklist — a schema-migration topic's axes are nothing like a debugger's, and
   forcing the wrong grid is the same trap as the wrong fixture set in run-mining.
2. **Distinctness = different handling, not different wording.** Two situations
   that resolve to the *same* recognition and the *same* remedy are **one case**
   wearing two names ("deadlock" vs "thread pool exhaustion" may be one handling,
   or may be two — you find out by writing what each actually prescribes, and
   merging them if the prescriptions are identical). Dedup the space *on the
   handling*, after collection and before deepening each card — exactly like
   `workflow.md` → "Dedup after collection," with the judgment on the remedy
   rather than the pixels. This is where a padded 50 collapses to an honest 31;
   that collapse is a finding, not a failure.
3. **Hardness is the target.** A "hard-scenario" case earns its card because it
   defeats the obvious approach. Rank the candidates toward cases that break
   naive handling (the Heisenbug that disappears under the debugger; the failure
   that needs production load to reproduce; the `.dmp` with no symbols and no
   source), not the ones every beginner article lists. An all-easy set has the
   same problem as an all-easy fixture set in run-mining: it ranks nothing and
   teaches nothing, because every tool "passes" it.
4. **Each case stands alone.** A reader who pulls *one* card must be able to act
   with it — recognize the situation, follow a handling path, know the trap and
   the cost — without reading the other N-1 or holding the whole run in their
   head. This is the checkpoint self-sufficiency test, applied to the case. A card
   that says "same as #3 but under load" is not a card.
5. **A handling is a claim until sourced.** The remedy itself must be evidenced,
   not recalled: attested cases cite where the handling is documented (and if
   two sources prescribe different remedies for the same situation, that
   disagreement is *the finding* — record both and say which the source-ecosystem
   rules weight higher). Where you had to reason the handling out and no source
   confirms it, label it `inferred`, the same `stated`/`inferred` floor every
   checkpoint carries. For a case whose handling is *tool-specific and checkable*,
   you may run a **seeded run-mine** on just that remedy (does this debugger
   actually attach to a running process this way) — case- and run-mining compose,
   and the `witness/` folder holds the proof.

## Census and ledger when you mine cases

Same duty as read-mining — bound the claims and make them re-checkable —
different fields. Capture while you work, never reconstruct from memory at
write-up (the invention failure mode is identical: a tidy "50 cases" list whose
evidence lines were never actually touched).

- **Coverage map** (the census): the axes you settled on, the case count, the
  families and how many cases sit in each (and which families are thin — a
  family with one case is a coverage gap you should say so about, not hide), the
  attested/derived split, the dedup removals and what merged into what, and the
  hardness distribution (how many are genuinely hard vs table stakes). "31 cases,
  22 attested across 9 sources, 9 derived, the 'offline artifact' family has one
  case and looks thin" is the honest spine a reader weighs the catalog against.
- **Evidence per case** (the source ledger, reused): for an attested case, the
  URL(s) that document the situation and the handling, pinned the way each
  ecosystem pins (postmortem URL + date + wayback; issue/answer permalink with
  the comment anchor; book + page range within the noise map). For a derived
  case, the derivation line — which cells of the grid produced it and the reason
  it must be reachable. Scrub secrets and signed-URL query strings exactly as the
  read ledger requires; internal incident links carry credentials too.
- **The three markers, and the two axes they sit on** — because they are easy to
  confuse and each card must carry one of each pair. **Provenance** answers where
  the *case* came from: `attested` (a source documents this situation) or
  `derived` (the scenario grid produced it; no source attests it). **Confidence**
  answers where the *handling* came from: `stated` (the source prescribes the
  remedy) or `inferred` (the source shows the symptom, the handling is your
  reasoning). They cross-cut freely: an attested case with an inferred handling
  ("the postmortem proves this failure exists; nobody documented the fix") is a
  different and very common animal than a derived case whose remedy was also
  reasoned out — a card's evidence line names both, and the catalog's honesty
  lives in that distinction.

## Budget of a case run

Case-mining sits between read and run on cost: cheaper than building N
candidates, dearer than skimming N sources, because each case's price is "reach
the source(s) that attest it, and get the handling right enough to state it."
Before committing, sanity-check what N honest, distinct cases costs against the
budget — a count is *not* negotiable downward by padding, so if "50 cases in an
hour" can only yield 18 hard, attested ones, say so plainly rather than shipping
50 shallow cards (this is `workflow.md`'s "the estimate plans the list, it does
not cap a unit" rule, aimed at the opposite failure — the list being *too big* to
mine honestly). Fan out by scenario family when subagents fit; each family brief
carries the shared axis set (so families tile the space instead of colliding),
the coverage-map shape the parent will stitch, and the distinctness-by-handling
rule so two families don't emit the same remedy under two names.

## What case-mining ends in

A case-mine's deliverable is a **catalog**, and — like run-mining's score table
— it is the second place `/mine` deliberately imposes structure, because here the
browsable, independently-usable card *is* the deliverable, in the same way the
comparison is the point of a bake-off. The catalog is:

- **The coverage lead** — a short free-form front that states the axes you mapped
  the space onto, the honest count and its attested/derived split, which families
  are dense and which are thin, and what the dedup pass collapsed. This is where
  the reader learns how much to trust the list before reading a single card.
- **The cases**, as compact cards, each carrying the same fields (the one fixed
  shape, and deliberately so):
  **Situation** → **How you recognize it** → **Handling path** →
  **Tools/techniques** → **Pitfalls & cost** → **Lesson** →
  **Evidence** (`attested@<source>` / `derived` / `inferred`, with the link or
  derivation). The order is the reader's act sequence — spot it, then do it —
  not a form to fill.
- **A stated-vs-inferred label carried on every card**, exactly as read-mining
  carries it, so a handling the sources assert and a handling you reasoned out
  are never confused for each other at a glance.

Around the cards, the *prose* stays free-form as any distillation does — the
lead, the cross-case observations ("these four are secretly one handling under
load"), the honest uncertainty, are written as understanding, not filled into
boxes. Only the per-card fields are fixed, and only for the same reason run-mining
yields its rule to the score table: browse-and-act requires each entry to have a
predictable shape. The `workflow.md` → Phase 4 rules otherwise hold verbatim.

Keep the coverage map and the source→case mapping in the run directory
(`distillation/`), and the raw writeups you lifted cases from in `sources/` — so a
reader can check a card against its attested source, or re-derive the space,
after the run's context is gone. The catalog is a first-class output; the
mapping that made it honest is its proof, and lives in `witness/`.
