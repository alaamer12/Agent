---
name: stateful
description: Derive every state a user-visible screen can enter, then implement the approved ones — pending, empty, stale, partial; provider down, degraded, throttled, maintenance; no connection at launch; extreme latency; expired session; refused entitlement; unknown values; device suspended, killed, storage-full; races; integrity and breach conditions. Platform-neutral: web, mobile, desktop, terminal, kiosk, embedded, any stack, and prototypes. Never a fixed checklist: states derive from the screen's own dependencies through nine condition axes, each candidate passes four evidence gates and a severity triage, and unknown input gets a designed rendering rather than the happy path. Use for "handle all the states", "what states can this screen have", "make it state-complete", "audit for missing states", "this breaks when the network is slow or gone", "it hangs or shows nothing when the server is down", "handle offline, errors and edge cases", "/stateful <file|screen|app>" — on any of those platforms — or when a happy path exists but its failure behavior doesn't. Not for polishing existing states (visual-enhancer), from-scratch screens, or headless state machines.
---

# Stateful

A screen is finished when **every condition it can be found in has a distinct, honest, recoverable
rendering** — not when its happy path works.

## Step 0 — Adopt the persona (`references/persona.md`)

> **A screen's default behavior is to lie confidently.** Code that runs happily on a good day renders
> *something* for every input. The absence of a crash is not the absence of a state.

Then rotate five stances over it — reliability engineer, paranoid security reviewer, first-run novice,
adversary, and the person with one hand, no colour, three seconds of patience. Each finds states the
others cannot. The file's think-hard procedure **is** the work.

The same file carries the *scale* method (reason in the axis grid with a running ledger, collapse out loud,
budget the passes, state the unbuilt ceiling in units), the **anti-generic test** — four questions answered
before a matrix exists, which is what stops the output being the usual pending/empty/error list — and the
confidence labels **verified / inferred / assumed**; an assumed row is never implemented unchecked.

## Gate 0 — Classify the target

| Input | Mode | What "implement" means |
|---|---|---|
| Static prototype / mockup | **prototype** | Render each state + make each forceable (query param, launch arg, dev menu). Content faked, and labelled as faked. |
| Real application source | **source** | Wire to real signals. **Never fabricate data to make a state render prettily.** |
| A whole product surface | **sweep** | Step 6 — cross-cutting states handled once, for every screen, no exceptions. |

Record the **platform posture** (`inventory.md` head — fat-client, offline-first, thin-over-link,
local-only, device-paired, headless-plus-surface): it decides which axes are live.

## Step 1 — Extract the eight facts (`references/inventory.md`)

Read the screen **and everything it reaches through**: data layer, services, shell, entry guards,
local store. A screen inherits every state its providers can produce, and the provider is where the
truth lives. Facts: **reads · writes · failure paths · gates · entity lifecycle · composition ·
emptiness multiplicities · host-device dependencies.** Fill the recording block; every row cites it.

## Step 2 — Walk the axes, then name what you find

`references/derivation-axes.md` is the method: nine independent condition axes (**data · provider ·
transport · viewer · entity · action · host · trust · time-and-order**) walked *singly* — every
single-cause state, and bounded — then along their *edges*: in-flight interruption, late truth, recovery
asymmetry, compounding failure. `references/state-taxonomy.md` names where you land (~110 states, ten
families, each with evidence and required recovery) and classifies provider failure **semantically**,
mapped from whatever carrier the project has — status codes, error enums, errno, exit codes, driver
results. **Never bind a state to a wire format.** `references/hostile-and-unknown-conditions.md` owns the
trust axis; its **fail-closed law is not optional**.

## Step 3 — Four gates every candidate must pass

1. **Evidence** — the `file:line` of the call, branch, gate, field or collection producing it. None → drop.
2. **Reachability** — a real viewer lands here without doing something absurd. Rare-but-real → keep, low priority.
3. **Distinctness** — needs a different message *or* recovery than a listed state; otherwise merge and name the causes.
4. **Consequence** — unhandled, the viewer sees something wrong: blank frame, stuck activity marker, silent failure, false success, dead end, someone else's data.

**Then score the survivors** — `sev = reach × consequence ÷ recoverability`, bucketed S1–S4 (scale in the
matrix template) — so a forty-row ledger sorts itself instead of being argued from. Report the score; a row
the user cares about more than the formula says gets upgraded in plain sight, and recorded as their call.

## Step 4 — Present the matrix and consult (blocking)

**Never implement before this is answered.** Format: `assets/templates/matrix-template.md`, in chat — axes
walked, ceiling, rejected list, anti-generic answers. Verdicts: `add` · `upgrade` · `keep` (say what you
checked) · `n/a` (structural reason) · `policy` (the risk owner decides) · `defer`. Then ask once: rows to
cut/add · depth budget · permission to move cross-cutting rows to the shared layer · **which contested
precedence positions the product wants** · the screen's irreversible actions.

**Depth ladder D0–D3** (one honest line → +one working recovery control → project components and correct
progress → forceable and actually rendered) is defined in `implementation.md`. **Floors, per row, never
globally:** D1 for anything blocking the screen's purpose, D2 for any state a viewer will see, D3 for the
3–5 likeliest, D0 for rare informational ones; S1 rows and the hostile file's §1–§4 never drop below D1.

## Step 5 — Implement

**Conventions hook first:** read the project's instruction files, structure and design-system docs,
navigation and transport layers, shared shell — which layer owns shared handling, where reusable state UI
lives, what the platform's announcement and focus mechanisms are, whether a new block must update a registry
in the same change. **Whatever the project declares outranks this skill**: its component tiers, any
units/registry/catalog doc that must change in the same commit, its failure-copy voice and disclosure rule.
A repo whose conventions you did not look for is not a repo without them.

Then: **one resolver, one value, one order**, with a named `Unexpected` variant so unclassified input can
never fall through to the happy path (`precedence-resolution.md`; idioms in
`examples/polyglot-walkthrough.md`) → render each approved state at depth, one primary action each → wire
real signals, simulating only the *trigger*, never the data → fail closed, and disclose a correlation id
rather than the internal topology.

## Step 6 — Sweep mode

`references/project-sweep.md`. Its rule, worth stating here: enumerate from the navigation *declaration*
rather than a file scan, cluster by frequency **and** shared mechanism, then give each cross-cutting state
**one owner layer, applied to every screen without exception or opt-out** — shared-first, then wire screens
and delete their duplicated handling in the same step.

## Step 7 — Verify, then report

**Force every implemented state and look at it** (how, per platform: `implementation.md` §Forcing). The
placeholder reserves the space content takes; no jump on clear; a non-touch path reaches the recovery control;
**an unknown input renders as unknown**; no state strands the viewer (full list in that file). Then report
axes walked, candidates killed, what was added/upgraded/kept/unhandled and why, and where the resolver lives.

## References — update this table in the same change that adds, removes or renames any file

| File | Owns | Read when |
|---|---|---|
| [`references/persona.md`](references/persona.md) | Stance, five stances, think-hard procedure, reasoning at scale, anti-generic test, confidence labels, obligations, what "done" means | Step 0, always |
| [`references/inventory.md`](references/inventory.md) | Platform postures, the eight facts with per-platform signals, recording block | Step 1 |
| [`references/derivation-axes.md`](references/derivation-axes.md) | The nine axes, single-axis and edge passes, collapse rules, budget slices | Step 2 — the method |
| [`references/state-taxonomy.md`](references/state-taxonomy.md) | Outcome classes vs carriers, ~110 states with evidence + recovery, cross-axis confusions, legal merges | Step 2 — the vocabulary |
| [`references/hostile-and-unknown-conditions.md`](references/hostile-and-unknown-conditions.md) | Fail-closed law, unknown values, integrity, exposure/breach, hostile content, tampered clients, crash-adjacent | Step 2, Step 5 |
| [`assets/templates/matrix-template.md`](assets/templates/matrix-template.md) | Consult-table format, severity column, table rules, which questions to ask | Step 4 |
| [`references/precedence-resolution.md`](references/precedence-resolution.md) | Boolean soup, the one-value shape, the precedence ladder and contested positions, resolver location | Step 5 |
| [`references/implementation.md`](references/implementation.md) | Depth detail, copy formula, progress per platform, retry semantics, operability, forcing table, 17 anti-patterns | Step 5, Step 7 |
| [`references/project-sweep.md`](references/project-sweep.md) | Sweep: enumerate, cluster, one-owner-no-exceptions, shared-first, dedup | Step 6 |
| [`examples/polyglot-walkthrough.md`](examples/polyglot-walkthrough.md) | The condition value in TS/C#/Go/Rust/Python/Elixir and where each stack enforces exhaustiveness, the same rows across web/mobile/desktop/TUI/embedded | Non-web target, or when a stack idiom is needed |
