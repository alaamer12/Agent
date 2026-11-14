---
name: yo-engineer
description: Produces a professional structure.md — a project's folder tree paired with an Authority Table mapping every shared decision to one owner — built only from documented evidence about the project. Refuses to draft structure until the project's purpose, scope, expected output, and load-bearing domain decisions are established in docs or stated plainly by the user, and instead guides the user through the specific questions needed to establish them. Use whenever the user invokes /yo-engineer, asks to structure, architect, or organize a codebase or repository, asks for a project tree or folder layout, or asks how a project's shared decisions (constants, rules, query logic) should be organized across an app or across multiple clients. Also use when a project has drifted (the same rule or constant defined in more than one place) and needs its structure re-grounded around single-ownership.
---

# Yo-Engineer

Produces `structure.md`: a folder tree where every non-trivial piece traces to a reason in the project's own evidence, paired with an Authority Table so every shared decision has exactly one owner. This skill's only deliverable is `structure.md` (or a matching component-scoped variant) — it does not produce other project docs, though it may ask the user to write some first.

Read `references/principles.md` and `references/decision-spectra.md` in full before drafting anything. `principles.md` is the doctrine this whole workflow enforces — the stereotypes to catch yourself running, the counter-moves, and the exact self-audit checklist step 4 below uses. `decision-spectra.md` is the universal set of structural trade-offs (repo boundary, deployable boundary, shared-ground threshold, isolation cost, naming) that every agenda maps onto its own ecosystem's idiom — read it before any agenda, since an agenda only tells you how a spectrum gets expressed in one language, never why the spectrum itself matters. Do not skip either because the workflow below looks self-explanatory; the workflow is a shell around this doctrine, not a replacement for it.

## Workflow

### Step 1 — Evidence audit

Read `references/evidence-bar.md` for the full method. In short: check the project's docs (and whatever the filesystem/repo offers, if available) for evidence covering what the project is, its scope boundary, its expected final output, and the load-bearing domain decisions specific to it. Classify each as decided-with-evidence / assumed / unasked.

Do this classification visibly to yourself before moving to step 2 — don't let a plausible-sounding assumption quietly stand in for evidence.

### Step 2 — Refuse and guide, or proceed

**If a load-bearing category is unasked:** stop. Do not draft. Follow `references/evidence-bar.md`'s guidance on what to hand back — name the specific gap, give the actual question set (short, answerable in a few lines), and say what doc it becomes if the project doesn't already have a home for it. This is a redirect, not a dead end — frame it that way.

**If items are merely assumed:** surface each assumption plainly to the user as a stated assumption before drafting, and give them a chance to correct it in the same message where you'd otherwise start drafting. Don't bury assumptions inside the draft and hope they're right.

**If evidence conflicts** (two docs disagree, or the user says something that contradicts a doc): stop and ask one targeted question naming the conflict. Do not average, silently prefer one source, or pick whichever produces a cleaner tree.

Only proceed to step 3 once every load-bearing category is decided-with-evidence, or explicitly assumed-and-confirmed.

### Step 3 — Match an agenda, then pressure-test it

Check `references/agendas/index.md` for a `<language>/<framework-or-plain>/` folder matching the project. Agendas nest by language first, then framework (or `plain/` when there's no UI framework — a backend, worker fleet, or CLI) — a typing tool layered on a language (TypeScript on JavaScript) is not its own branch; it's a note inside the language's folder.

If a matching folder exists, read its `index.md` for how this ecosystem's idiom expresses each spectrum from `references/decision-spectra.md`, then check `examples/` for a case whose specific spectrum matches what this project needs decided. An example isn't decoration — it's the argued case for why a spectrum resolved one way *in a specific situation*, including what the traditional default would have produced and why the evidence pointed elsewhere. Reading only `index.md` and skipping the relevant example means working from the abstract spectrum without the case that stress-tested it. An agenda entry — idiom note or example — is a hypothesis to test against this project's evidence, never a template to copy.

If no folder matches the stack exactly, `references/decision-spectra.md` still applies in full — it isn't language-scoped. Additionally, check other agenda folders' examples for a case whose shape transfers even though the ecosystem doesn't match, weight it as a weaker, borrowed hypothesis, say plainly that no dedicated agenda backs this stack, and ask whether to proceed on that basis or wait for one to be written.

Draft the tree and the Authority Table using `assets/structure-template.md` as the skeleton. Every folder that isn't self-evident from its name gets an inline comment naming what decision it owns or what role it plays — not just what type of file lives there. Every shared decision (constant, rule, query semantic, validation) gets a row in the Authority Table: decision, single ground, consumers, protecting test. Anything genuinely undecided becomes a Named Absence, not a guess — see `principles.md`.

### Step 4 — Self-audit before presenting

Run the full self-audit gate from `references/principles.md` against the draft: professional-shape check, elevation check, staleness check, symmetrization check, eloquence check, named-absence check. Fix anything that fails a check — don't present with a caveat instead of a fix. This step is not optional and not skippable because the draft "looks right" — looking right from inside the frame that produced it is exactly what the checklist exists to catch.

### Step 5 — Present

Show the draft along with:
- Which assumptions (if any) were surfaced in step 2 and how they were resolved
- Which agenda patterns were applied, and which were deliberately *not* applied because their override conditions matched this project (this is worth stating explicitly — it's the evidence that the agenda was pressure-tested, not copied)
- Any Named Absences and their revisit triggers

Treat any correction the user gives after this as probable premise-replacement, not a one-line patch — per `principles.md`, ask what else might be resting on the premise that just changed before just fixing the one thing named.

## When this skill should NOT produce a full structure.md

If the user's request is narrow — "where should this one new file go," "does this one constant belong in a shared package" — answer that narrowly using the same reasoning (single-ground, override-conditions-checked agenda patterns) rather than triggering the full evidence-audit-and-refusal workflow. The refusal mechanic in step 2 is for drafting or re-drafting a project's structure wholesale, not a gate on every small structural question.

## Reference files

- `references/principles.md` — the doctrine: stereotypes, counter-moves, the self-audit gate, named absences. Read in full before step 3.
- `references/decision-spectra.md` — the universal structural trade-offs every agenda maps onto its own ecosystem. Read in full before step 3.
- `references/evidence-bar.md` — the refusal mechanic: evidence categories, classification method, what to hand back on refusal, handling conflicts.
- `references/agendas/index.md` — thin directory of language/framework agenda folders.
- `references/agendas/javascript/plain/index.md` — how JS/TS idiom expresses each spectrum for backends, worker fleets, CLIs (no UI framework).
- `references/agendas/javascript/plain/examples/*.md` — argued, redacted, single-point worked cases for that agenda.
- `assets/structure-template.md` — the output skeleton.
