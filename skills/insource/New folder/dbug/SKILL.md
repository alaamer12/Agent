---
name: dbug
description: The debugging meta-skill. Investigate, debug, fix, and verify any problem in a codebase as a disciplined process — never "change code until the error disappears". ALWAYS use this when something is broken, wrong, failing, unexpected, regressed, or hard to reproduce — mentions of bug, error, exception, crash, 500, timeout, wrong/missing/duplicate data, "stopped working", "worked before", "works on my machine", flaky, regression, schema mismatch, or a pasted stack trace, even if the user never says "debug". Routes to specialised inner skills (investigation, regression-testing, instrumentation, backend, database, frontend, production) and enforces the core stances: root-cause fixes over symptom patches, minimal-but-complete fixes, make-the-bug-structurally-impossible, "every bug is a chance to test", controlled .debugging/ artifacts, and feeding solved problems back into how-to-do.
---

# dbug — debugging meta-skill

A big skill made of specialised inner skills, each with its own `SKILL.md`.
This file is the **router**: it states the non-negotiable stances, the one
workflow every bug follows, and where to send the investigation next. The
teaching lives in the inner skills — load only the ones the current bug
needs, and follow cross-references between them freely (they are written to
link to each other).

## What this is / what it is not

**Is:** the process — understand → classify → gather evidence → find the
cause → reproduce as a test → fix root cause and every layer → verify →
keep artifacts under control → capture the knowledge.

**Is not:**
- a domain tutorial library — inner skills give playbooks, not encyclopedias;
- a test-style guide — it says *when* a bug becomes a test, `regression-testing/` says how;
- a substitute for the **how-to-do** skill — permanent procedures go there; `.debugging/bugs/` records incidents;
- permission to build expensive infrastructure (Playwright, e2e harnesses, new services) — ask the user first (see "Ask the user").

## The six core stances

1. **Understand before solving.** Classify the problem type first (see
   `investigation/`). Immediate-evidence problems (schema vs DB mismatch with
   both artifacts in hand) start investigating at once; vague problems
   ("half the system broke") require user questions *before* digging.
2. **No fix without root cause.** A patch that makes the symptom disappear
   while the defect remains is not a fix. Fix the **source of truth**, not
   only the broken instance (a live DB repaired by hand while the schema file
   still holds the bug will re-break on the next recreate/deploy).
3. **Minimal ≠ incomplete.** Scope the fix to what is necessary, then make it
   complete *across every layer the invalid data/state passes through* —
   make the bug structurally impossible, not merely caught once.
4. **Every bug is a chance to test.** When the bug is reasonably testable:
   reproduce the *actual* failure as a test, watch it fail, fix, watch it
   pass, keep it as regression protection. Never invent hypothetical
   bug-shaped scenarios to skip this.
5. **Controlled observation only.** Debug output goes through a gated,
   scoped facility (dev-only, per-service/module), never scattered
   `console.log`s; ad-hoc scripts live in `.debugging/tmp/` with a lifecycle
   (promote → `instruments/`, or delete) — all per `instrumentation/`.
6. **Escalate honestly.** If a permission, credential, or platform UI blocks
   a step (e.g. read-only DB role where a write is needed), say so with the
   5-point protocol (what/why/where/do-what/report-what — in
   `investigation/`) instead of pretending to do it, then continue after the
   user acts.

## The workflow

```
Understand & classify ──► ask user if context is missing ──► gather evidence
   (investigation/)          (history questions below)         ↓
                 Git forensics when "worked before" is in play
                                  ↓
              form & test hypotheses until root cause is proven  ◄── temp
                                  ↓                       scripts/instrumentation
        design minimal-but-complete fix (every layer, source of truth)
                                  ↓
   reproduce as failing test ──► apply fix ──► test passes ──► verify
          (regression-testing/)                    ↓
        escalate to user when env/permission requires it
                                  ↓
     promote useful script → instruments/ · record bug → bugs/ · clean tmp/
                                  ↓
              capture the class-of-problem procedure via how-to-do
```

Not every bug touches every step — a self-evident one-line defect still
gets a test when testable; an untestable UI glitch skips to manual
verification. Skipped steps must be a *decision*, not an oversight.

## Routing

### By phase (load as the investigation moves)

| Where you are | Go to |
|---|---|
| Classifying, question lists, evidence gathering, hypotheses, root-cause design, escalation protocol, problem-class playbooks | [`investigation/SKILL.md`](investigation/SKILL.md) |
| Turning the confirmed failure into a failing test, choosing the test layer, cost gates before e2e | [`regression-testing/SKILL.md`](regression-testing/SKILL.md) |
| Adding debug logging, writing scratch verify scripts, `.debugging/` lifecycle, bug records, promoting instruments | [`instrumentation/SKILL.md`](instrumentation/SKILL.md) |
| Bug solved, non-trivial multi-step procedure discovered | **how-to-do** skill (sibling — its `.htd/` system; dbug never writes procedures itself) |

### By domain symptom

| Symptom shape | Go to |
|---|---|
| API/route/service wrong, handlers, queues/workers, DI, env loading, module resolution, "is it the request, our logic, or a dependency?" | [`backend/SKILL.md`](backend/SKILL.md) |
| Schema drift vs live DB, migrations, constraints/RLS, ORM-generated SQL, wrong/missing/duplicate rows, locks/isolation | [`database/SKILL.md`](database/SKILL.md) |
| UI wrong/empty/stale, browser console errors, network tab surprises, client state vs render | [`frontend/SKILL.md`](frontend/SKILL.md) |
| Can't reproduce, prod-only, intermittent, only-under-load, only-one-customer, race/deadlock, memory growth, heisenbug | [`production/SKILL.md`](production/SKILL.md) |

Domain inner skills cross-reference each other (frontend bugs frequently
start at the network boundary → backend/database; backend query surprises →
database). Everything, always, runs through `investigation/` for the
process itself.

## Ask the user — the only four gates

1. **Before investigating a vague/blast-radius problem:** was it working
   before? in Git? ~how many commits / which branch ago? what changed just
   before it broke? (only questions that change the investigation path)
2. **Before intensive verification/testing:** e2e suites, Playwright-class
   setup, staging reseeds — propose cost, get a yes.
3. **Before promoting a temp script to a permanent instrument:** offer it,
   let the user decide keep-vs-delete when value is borderline.
4. **When blocked by permissions/external UI:** the 5-point escalation
   protocol in `investigation/`, then resume and verify the user's action.

## The artifact shape (rules live in `instrumentation/`)

```
.debugging/            (target repo root — created on first real need)
├── bugs/          · significant investigation records
├── instruments/   · promoted, generalized reusable tools
└── tmp/           · this session's scratch scripts — deleted or promoted
tests/             · regression tests born from real bugs (project's layout)
.htd/              · generalized procedures (owned by how-to-do)
```

The point of distinguishing all five: debugging gets repeatable rigour
without one-off scripts and incident notes calcifying into permanent
project complexity.
