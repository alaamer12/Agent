# Viber Memory — The Project's Conversational Ledger

> The project's conversational ledger under `.viber/`: `memory.md`, `settled.md`, `learnt.md` — formats, triggers, recording discipline. Fed by `grill-me` / `close-topics` / `agents-md`; read by the Router (`router.md`).

## 1. Overview

Viber Memory is a **project-scoped persistence layer** for the knowledge a project produces while it is being
discussed and built: the questions still open, the questions already answered, and the facts learned about the
user and the project along the way.

It exists because a conversation is not a database. A question deferred today, a decision the user made in
passing, a pain the user mentioned once — each evaporates when the session ends unless it is written down. The
next session then re-asks the settled question, re-litigates the settled decision, and re-learns the settled
fact. Memory is the ledger that stops that waste.

It is **not a lifecycle phase** and **not a Skill that runs on its own**. It is a ledger that every Skill and
every session reads and writes, in the same way the Router is a layer every step consults. `init` creates the
files; the Router reads them; `grill-me`, `close-topics`, `agents-md`, `thaw`, and `adapt` feed them.

### Core Principle

**Capture the question, the answer, and the lesson — at the moment they exist, not at the end.**

A deferred question is recorded the moment it is deferred. An answer is recorded the moment it is given,
whether the user stated it explicitly or implied it. A fact is recorded the moment it is learned. Nothing waits
for a "summary step" that may never come.

### What Memory is for

| File | Holds | The failure it prevents |
|---|---|---|
| `memory.md` | Questions that are open or deferred — what is asked, what it means, what blocks it now | A deferred question is forgotten and never resurfaces when its blocker clears |
| `settled.md` | Questions already answered — the question, the answer, and the reason (explicit or implicit) | A settled decision is re-asked or re-litigated next session |
| `learnt.md` | Facts learned about the user and the project — experience, preferences, pain, constraints | The agent re-learns what the user already told it, or ignores a stated constraint |

---

## 2. Where Memory Lives

All of a project's Viber state lives in the **project's own `.viber` directory** — `<project-root>/.viber/`.
This is deliberate: keeping the registry and the memory inside the project makes them visible and transparent
to the user, instead of hidden in a user-home folder. Nothing Viber writes lives outside the project.

| File | Holds |
|---|---|
| `<project-root>/.viber/registry.md` | The Skill registry written by `init` — a per-project snapshot of the user's deck (Viber Skills + registered/extension Skills) |
| `<project-root>/.viber/memory.md` | This project's open and deferred questions |
| `<project-root>/.viber/settled.md` | This project's answered questions, with reasons |
| `<project-root>/.viber/learnt.md` | Facts learned about the user and the project |

The deck's *membership* is still decided by registration — a Skill registered with the user's agent belongs to
the user's deck (`lifecycle.md` section 8) — but the registry that indexes it is materialized **per project**,
so each project carries its own transparent copy. A project's memory never travels to another project.

`init` creates the registry and the three memory files with their empty templates on first run. A later `init`
refreshes the registry but **never erases memory** — memory is append-and-move, not reset. The project `.viber`
directory also holds the Router's project-level progress state (`router.md` section 8). These files are part of
Viber's supervision umbrella: when supervision is active they are among the artifacts Viber owns (see
`supervision.md`).

---

## 3. The Three Files

Each file is Markdown, starts with a one-line purpose, and carries one table. Rows are added as knowledge
arrives; a row moves between files when its state changes (section 5). Dates are `YYYY-MM-DD`.

### 3.1. `memory.md` — Open and Deferred Questions

**Purpose:** every question the project cannot answer yet, with enough context that a future session can pick
it up without re-deriving it. This is the home of `agents-md`'s `pending — not assumed` items and
`close-topics`' open topics.

**Template:**

```markdown
# Viber Memory — Open Questions

Questions this project has not answered yet. When one is answered, move it to settled.md.

| # | Question | Description / clarification | What blocks it now | Raised | Status |
|---|---|---|---|---|---|
| Q1 | <the question, in one line> | <what it means and why it matters> | <the dependency, missing input, or phase gate> | <YYYY-MM-DD> | open / deferred |
```

**Field rules:**

- **Question** — the actual question, not a topic label. "Which hook language runs the scoring formulas?" not
  "hooks".
- **Description / clarification** — what the question is really asking and why it matters here, so a reader who
  was not in the session understands it.
- **What blocks it now** — the concrete reason it cannot be answered yet: a missing dependency ("needs the
  architecture output"), a phase gate ("DR — no app exists yet"), a missing input ("waiting on SNDUK API
  docs"), or a user decision ("user has not chosen"). This is the field the Router watches: when the blocker
  clears, the question is ready to surface.
- **Status** — `open` (actively being worked) or `deferred` (parked until its blocker clears).

**Illustrative row** (from a drafting session):

| # | Question | Description / clarification | What blocks it now | Raised | Status |
|---|---|---|---|---|---|
| Q1 | Which language runs the scoring formulas and the sync — JS (goja) or Go? | PocketBase hooks run in goja (ES5-ish, no npm/TS); the code-owned formulas must run server-side. The choice shapes how the shared formula package is written and tested. | Depends on the integrity-logic topic closing in steering-tech | 2026-11-15 | deferred |
| Q2 | What is the environment / secrets strategy? | How config and the encrypted SNDUK token vault are declared, validated, and loaded. | DR — no app exists yet; closes at Implementation | 2026-11-15 | deferred |

### 3.2. `settled.md` — Answered Questions

**Purpose:** every question the project has answered, with the answer and the reason — so the decision is not
re-asked, and the next agent understands *why*, not just *what*.

**Template:**

```markdown
# Viber Memory — Settled

Questions this project has answered. During Draft [DR] these are provisional and revisable (see thaw).

| # | Question | Answer | Reason | Kind | Settled | Provisional |
|---|---|---|---|---|---|---|
| S1 | <the question> | <the answer> | <why — what the user said or implied> | explicit / implicit | <YYYY-MM-DD> | yes (DR) / no |
```

**Field rules:**

- **Reason** — capture the user's justification whether stated **explicitly** ("I want less code and a mature
  BaaS") or **implicit** (they rejected every option that needed a custom backend, implying the less-code
  priority). An implicit reason is recorded as implicit and is lower-confidence — re-confirm it if a later
  decision depends on it.
- **Kind** — `explicit` (the user said it) or `implicit` (inferred from their choices or words). Never present
  an implicit answer as an explicit mandate.
- **Provisional** — during Draft [DR] an answer is the current best, not law (`thaw`; phases in
  `lifecycle.md` 1.2). Mark it `yes (DR)`; it
  tightens to `no` when the project enters In-Progress and the decision is cast into a formal record. A settled
  answer is still revisable while drafting — settled means "answered", not "frozen".

**Illustrative row:**

| # | Question | Answer | Reason | Kind | Settled | Provisional |
|---|---|---|---|---|---|---|
| S1 | Which backend data platform — PocketBase, Appwrite, Supabase, or custom Postgres? | PocketBase, BaaS-centric, no custom backend. | User wants less code and a mature, production-ready BaaS; has used PocketBase heavily and it performed well; single binary, no API→DB hop. Supabase/Appwrite weighed and set aside for now. | explicit | 2026-11-15 | yes (DR) |

### 3.3. `learnt.md` — Learned Facts

**Purpose:** what the agent learned about the user and the project that should shape future decisions —
experience, preferences, pain points, constraints, and the reasons behind choices. This is the project's
working memory of the user, so the agent never re-learns it or ignores it.

**Template:**

```markdown
# Viber Memory — Learnt

Facts learned about the user and the project. Each shapes how future decisions are made.

| # | Fact | Evidence / how learned | Implication | Learnt |
|---|---|---|---|---|
| L1 | <what was learned> | <user said / observed / verified, with the session or source> | <how it should shape decisions> | <YYYY-MM-DD> |
```

**Field rules:**

- **Fact** — a durable truth about the user or project, not a one-off task detail.
- **Evidence / how learned** — where it came from: a user statement, an observation, a verification. A fact
  inferred rather than stated is marked as inferred.
- **Implication** — the operative consequence: what the agent must do or avoid because of this fact. A fact
  with no implication is trivia; record only what changes behavior.

**Illustrative row** (the user's own example):

| # | Fact | Evidence / how learned | Implication | Learnt |
|---|---|---|---|---|
| L1 | The user has used Supabase (Cloud) for years and PocketBase a lot; had real pain with PocketBase schema migration and ID auto-generation (poorly documented), yet chose PocketBase for this project because it weights higher on their goals. | User statement during the data-platform discussion. | Do not re-litigate the PocketBase choice. Treat schema-migration and ID-generation as a known pain: a deliberate migration + ID strategy is a required open question, not an afterthought. | 2026-11-15 |

---

## 4. How Memory Connects

Memory is fed by the Skills that already produce questions, answers, and lessons, and read by the layer that
guides the workflow.

| Source / reader | Relationship to Memory |
|---|---|
| `grill-me` | A question it raises that cannot be answered now → `memory.md`. An answer it reaches → `settled.md`. |
| `close-topics` | An open topic → `memory.md`. A closed topic → `settled.md` (with the reason). The agenda of deferred topics is `memory.md`. |
| `agents-md` | Its `pending — not assumed` items are recorded in `memory.md` so they survive the session and resurface when unblocked. |
| `thaw` | A settled answer is provisional while drafting; `settled.md` carries the `Provisional` flag. A re-validated answer updates the row, it does not silently overwrite the reason. |
| `adapt` | A recurring need or repeated correction is a learned fact → `learnt.md`; the adaptation itself is recorded in `AGENTS.md` (adapt owns that). |
| **Router** | Reads `memory.md` for "outstanding decisions or blockers" (`router.md` 2.2) and surfaces a deferred question when its blocker clears. Reads `settled.md` to avoid re-suggesting a settled decision. |
| `init` | Creates the registry and the three memory files on first run; reads them to report where the project stands; never erases memory on refresh. |
| `supervision` | Memory already lives under `.viber` — it is part of the umbrella; when supervision is active the memory files are among the artifacts Viber owns (see `supervision.md`). |
| **Session start** | The agent reads all three before deciding anything, so it neither re-asks settled questions nor ignores learned constraints. |

### Memory is not the spec, and not the rulebook

| Artifact | Owns | Memory's relation |
|---|---|---|
| `docs/steering/` | The project's specification (perception + tech) | A settled decision that becomes part of the spec is written there; `settled.md` keeps the question→answer→reason provenance and points to it. |
| `AGENTS.md` | The agent rulebook (obligations, pointers) | A settled decision that becomes a rule is written there; `settled.md` records why. |
| `.viber/*.md` | The conversational ledger | The questions, answers, and lessons themselves — including the ones not yet promoted to a spec or rule. |

**One fact, one home.** Memory records the *provenance* (what was asked, answered, learned, and why); the spec
and rulebook own the *operative* fact. Memory points to where a settled decision landed; it does not duplicate
the spec's body.

---

## 5. Recording Discipline

- **Write at the moment.** A deferred question goes to `memory.md` when it is deferred, not at session end. An
  answer goes to `settled.md` when given. A fact goes to `learnt.md` when learned.
- **Move on answer.** When a `memory.md` question is answered, add the row to `settled.md` and remove it from
  `memory.md` (or mark it `answered → S<n>`). A question never lives in both files as open.
- **Explicit vs implicit.** Record the reason whether the user stated it or implied it; mark implicit reasons
  as implicit and lower-confidence. Never inflate an implicit answer into an explicit mandate.
- **Provisional while drafting.** During DR, settled answers are revisable (`thaw`). Re-validation updates the
  row and preserves the original reason; it does not erase history.
- **No invented answers.** An unanswered question stays in `memory.md`. It is never silently filled with a
  plausible default — that is the `agents-md` "honest gaps" rule applied to memory.
- **Read before deciding.** At session start, read all three files. Do not re-ask a settled question, do not
  re-litigate a settled decision, do not ignore a learned constraint.
- **Surface when unblocked.** The Router watches `memory.md`'s "what blocks it now"; when the blocker clears,
  it surfaces the question rather than letting it stay parked forever.

---

## 6. Rules

- **Project-scoped.** All Viber state — registry and memory — lives in `<project-root>/.viber/`; a project's
  memory never travels to another project.
- **No secrets.** Nothing private — credentials, tokens, personal data — is written into memory. A learned fact
  about a credential records *that it exists and where it is declared*, never its value.
- **Append-and-move, never reset.** `init` refresh never erases memory. Rows move between files as state
  changes; history is preserved, not overwritten.
- **One fact, one home.** Memory keeps provenance and points to the owning spec/rule; it does not restate the
  spec body.
- **Honest gaps.** Unanswered stays open; implicit stays marked implicit; provisional stays marked provisional.
- **Durable user facts may be promoted.** A learned fact that is true of the user across projects (a standing
  preference, a toolchain choice) may also be promoted to the user's global memory or `personalize`; the
  project `learnt.md` remains this project's record of it.

---

## 7. Boundaries

### Memory SHOULD

- Record every deferred question with its description and its blocker.
- Record every answered question with its answer and reason, explicit or implicit.
- Record every durable learned fact with its evidence and implication.
- Be read at session start and consulted before re-asking or re-deciding.
- Surface deferred questions when their blocker clears.
- Keep provenance and point to where a settled decision landed.

### Memory SHOULD NOT

- Become a second specification — the spec lives in `docs/steering/`, the rulebook in `AGENTS.md`.
- Hold secrets or personal data values.
- Silently fill an unanswered question with a default.
- Present an implicit answer as an explicit user mandate.
- Freeze a provisional answer during Draft — settled is not frozen (`thaw`).
- Duplicate the body of a spec or rule it points to.
- Erase history on refresh or re-validation.
- Replace the responsibilities of `grill-me`, `close-topics`, `thaw`, or `adapt` — it records what they produce.

---

## 8. Flow

The memory pipeline is diagrammed in [`diagrams/memory-flow.mmd`](../diagrams/memory-flow.mmd): knowledge arriving from Skills and sessions feeds the three files, and the Router surfaces a deferred question when its blocker clears.

---

## 9. Open Items

1. **Promotion path.** The exact rule for promoting a durable user-level fact from project `learnt.md` to the
   user's global memory / `personalize` — when it is automatic, when it asks.
2. **Topic linkage.** Whether `memory.md` rows should link to a `close-topics` topic id or a steering doc path,
   so a deferred question can be traced to the spec area it belongs to.
3. **Skill wrapper.** Whether Memory stays a passive ledger (this document) or also gains a small shared Skill
   that records and surfaces rows on demand. The ledger works without a Skill; a wrapper is optional.