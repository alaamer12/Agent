---
name: ladder
description: 'Find, design and harden ladders: ordered decision structures where rungs (a condition paired with an outcome) are evaluated in one order until something wins. Built for asks such as whether the code already has tiers, layers or fallbacks between its parts, whether errors escalate instead of being swallowed, and whether a guarantee is actually guaranteed: it audits the code for the precedence chains already in it, reports findings with file:line evidence, presents the fitting shapes with trade-offs and asks which to take, then records the decision in the project''s own doc format and implements to it. Names the twelve shapes and four semantics (first-match, all-strictest, all-permissive, exactly-one) and the defects it detects (shadows, unreachable rungs, missing terminal rung, severity inversion, swallowed failures). Writes them without nested conditionals: pure decide over data, effects at the boundary, in the repo''s own paradigm.'
when_to_use: The user asks whether tiers/ladders/layers or fallbacks exist in the code, wants code made more robust or a guarantee guaranteed, wants errors or information escalated instead of swallowed, asks to design classification/routing/authorization/escalation/state-resolution logic, wants an if-else chain replaced, or asks why one rule never fires.
---

# Ladder — ordered decision structures

A ladder is **two rails and many rungs**: facts go in, one answer comes out, and the rungs between them
are conditions paired with outcomes, evaluated in one defined order until something wins. It is the most
re-invented structure in software, and it is nearly always wrong in one of four ways: the winner is
decided by *position* while everyone believes it is decided by *meaning*; there is no terminal rung, so
unknown input takes the happy path; a broad rung shadows a specific one and nobody notices; or the same
question is answered by three different ladders in three layers.

Most invocations of this skill are therefore **audits, not greenfield designs**: "do we have tiers
here?", "can we make this more robust with fallback?", "we're swallowing errors", "how do we make this
guarantee unbreakable?" The workflow is audit → report → ask → record → implement → verify, and the
middle three steps are the point — the user picks the strategy after seeing the trade-offs.

## Step 0 - Confirm which "ladder" is meant

Five things share the word; only one is this skill's default.

| They said | They mean | Go to |
|---|---|---|
| "tiers / layers / fallback / escalate / guarantee / this rule never fires" | a **decision ladder in our code** | Step 1, `20` |
| "this if-else chain is unreadable" | **replace a ladder** | `02`, `08`, `22` |
| "what level is this bug at / how did we conclude that" | **thinking ladders** | `18` |
| "PLC, rungs, IEC 61131-3" | **ladder logic** | `17` |
| "staircase layout" | **stepped UI** | `17` |

## Step 1 - Audit the code before proposing anything

`20` has the search patterns and the per-finding table. The short version: locate every place where more
than one candidate answer exists and something picks one — config and middleware ordering, registry and
resolver chains, `switch`/map dispatch, loops that `break`, and every `catch`/`?? `/`except: pass` that
quietly chooses the happy path. Read what the greps find; a match is a candidate, a `file:line` is
evidence.

Do this in the same pass: read the project's conventions (instruction files, docs layout, lint and
formatter config, neighbouring code) so the options you offer are expressible in the house style, and
state the **guarantee** in one sentence with no `if` in it — the audit is measured against that sentence,
not against taste.

## Step 2 - Report the findings, then ask (blocking)

Report first, per site: the shape today, where its order comes from, whether it has a terminal rung, the
defect, and what a wrong pick costs here. Then present the two or three shapes that genuinely fit —
`16` narrows them, `21` gives the option table — each with what it fixes, the cost now, the cost later,
reversibility, and the risk if the choice is wrong. Recommend one in a line. Then ask, and **wait**.

Two rules here. Do not code between the report and the answer; and if the user delegates ("you pick"),
pick, say which axis you weighted, and write it down as their delegation. A ladder chosen silently is a
policy nobody agreed to, which is exactly the class of bug under audit.

## Step 3 - Write the decision down, in the project's own format

`21` owns this. Find where the repo already records such calls — `docs/adr/NNNN-*.md`, a
`conventions/` or `decisions/` folder, steering files, a rules doc, `AGENTS.md` — and match that format:
heading order, voice, front matter, numbering scheme. If the project records nothing like this anywhere,
create one file beside the code and say out loud that you started the pattern. The record is short: the
guarantee, the chosen semantics (mode, ordering key, terminal rung, who overrides whom), the rejected
options with reasons, the consequences, and how it is verified.

## Step 4 - Implement it

The four properties the record must pin down are also the four that pick the code:

1. **Who owns the order** — author position or priority (`02`, `07`), engine tiers (`13`), or tiers of
   priorities inside scopes (`03`). Say which direction wins; systems ship both.
2. **Matching mode** — first-match, all-strictest, all-permissive, exactly-one, collect (`14`), written
   as a function, not a comment.
3. **Override direction** — nearest scope, strictest verdict, most specific, nobody (`03`, `13`). Where
   tiers and scopes coexist, the loop order is the policy (`13`).
4. **Terminal rung** — its name, its value, and whether arriving there is normal traffic or an error
   (`08`, `15`).

Then write it so the shape survives review (`22`): pure `decide` over data, effects in one interpreter at
the boundary, no nesting where a table or a match does the job, predicates side-effect-free, unknown
inputs producing a value instead of a crash or a pass. Respect the repo's paradigm rather than importing
a new one — a codebase of classes takes a strategy table, a codebase of functions takes a fold; the
ladder's properties are the requirement, the syntax is the project's. If the project's rules forbid the
idiom you'd choose, implement the allowed form, keep the properties by other means, and note the
constraint in the record.

## Step 5 - Verify, then say what changed

`scripts/ladder_audit.py` runs the mechanical checks; `15` covers the tests it cannot replace. Run the
audit as part of the change, not afterwards:

```bash
python scripts/ladder_audit.py              # self-test: 8 fixtures, every defect class must be caught
python scripts/ladder_audit.py rules.yaml   # audit a rule set (YAML subset or JSON)
```

On Windows use `python`; `python3` is usually a Store stub. Findings, in the order they bite:
**terminal** (no always-answering rung) · **shadow** (an earlier rung provably covers a later one) ·
**severity-inversion** (a permissive rung before a strict one that can co-hold — the flat-list deny bug)
· **unreachable** (no synthesized input reaches the rung) · **order-mode** (the declared mode still
depends on list position) · **impure** / **schema** (a condition reads the clock or the network;
duplicate ids, unknown fields or operators). Exit 1 on any finding.

Then report: the guarantee, the invariant that now holds *structurally* rather than by ordering, the
before/after evidence (`file:line` of each replaced site), what the audit proved, what a future author
must not do to keep it true, and where the decision record lives.

## References — update this table in the same change that adds, removes or renumbers any file

| File | Owns | Read when |
|---|---|---|
| [`references/00-anatomy-and-semantics.md`](references/00-anatomy-and-semantics.md) | Vocabulary, the seven slots of any ladder, the semantics table with its standard names, invariants, anti-patterns, the terminal rung in five stacks | Step 1, always |
| [`references/01-if-chain.md`](references/01-if-chain.md) | The chain: order coupling, the missing final `else`, when to stop using it; TS/Go/Rust/Elixir/SQL forms | Auditing or keeping a small chain |
| [`references/02-rules-table.md`](references/02-rules-table.md) | Rung-as-record table: ids, import-time totality, Python/Go/Java/Rust/SQL/YAML forms, why a map is the wrong tool | Order must be reviewable |
| [`references/03-scope-chain.md`](references/03-scope-chain.md) | Ladder of ladders: who may override whom, nearest- vs last-wins, hop-bounded chaining, six shipped cascades | User/team/global or folder rules |
| [`references/04-guard-clauses.md`](references/04-guard-clauses.md) | The vertical ladder: cost-ordered guards, mutating guards, first-match vs all-matches validation | Preconditions before work; handlers |
| [`references/05-match-tree.md`](references/05-match-tree.md) | Shared-prefix trees and tries: specificity by structure, exact-before-wildcard, the dead-child detector | Long rule sets, routing, prefixes |
| [`references/06-decision-table-in-config.md`](references/06-decision-table-in-config.md) | Rules as data: bounded grammars (CEL/JSONLogic/Cedar/Rego vs SpEL), load-time validation, grammar size as a safety property | Non-developers edit the ladder |
| [`references/07-priority-numbers.md`](references/07-priority-numbers.md) | Priority/salience: sort-direction conventions, tie-break stability, the shuffle test, gaps | Rules arrive from many owners |
| [`references/08-state-dispatch-matrix.md`](references/08-state-dispatch-matrix.md) | Closed-set dispatch in seven stacks; unknown renders as unknown; zero-value ingress; totality tests | The discriminator is an enum |
| [`references/09-pattern-matching-and-switching.md`](references/09-pattern-matching-and-switching.md) | What each language's matcher guarantees and never guarantees: exhaustiveness, unreachable arms, guards, fallthrough | Choosing between chain, matrix, matcher |
| [`references/10-chain-of-responsibility.md`](references/10-chain-of-responsibility.md) | Rungs as objects: composition order as the reviewed artifact, decline vs raise, cycles, DI order accidents | Rungs have heavy, separate owners |
| [`references/11-attempt-and-escalation-ladders.md`](references/11-attempt-and-escalation-ladders.md) | Ordered attempts with cost, timeout, error class, budget; where `??`/`or_else` stop being enough; retry storms, silent downgrades | Fallbacks, failover, "escalate, don't swallow" |
| [`references/12-state-guards-and-no-code-builders.md`](references/12-state-guards-and-no-code-builders.md) | Statechart guard order (first true transition wins), broad-guard shadowing, impure guards; what a visual builder must ship | State machines; workflow/agent builders |
| [`references/13-fixed-tiers.md`](references/13-fixed-tiers.md) | Engine-owned verdict order: tiers vs a flat list, tiers x scopes loop order, closed tier types, the conflict test pair | Prohibitions must not be overridable |
| [`references/14-semantics-and-combining.md`](references/14-semantics-and-combining.md) | First / all-strictest / all-permissive / exactly-one / collect / last-wins, the divergence table, chaining and its bound | Step 4's mode choice; two rules disagree |
| [`references/15-testing-shadows-and-audit.md`](references/15-testing-shadows-and-audit.md) | Totality, reachability, determinism, order-independence; the probe, golden matrices, mutation checks, audit fields, ten review questions | Step 5, and reviewing someone else's ladder |
| [`references/16-selection-guide.md`](references/16-selection-guide.md) | Need-to-shape and situation-to-mode tables, the resolving questions, migration paths, anti-selections | Step 2, to narrow the options |
| [`references/17-ladder-logic-and-stepped-layouts.md`](references/17-ladder-logic-and-stepped-layouts.md) | IEC 61131-3 ladder logic (scan, image tables, duplicate coils, interlocks) and stepped UI layouts | "Ladder" means PLC or layout |
| [`references/18-abstraction-and-inference.md`](references/18-abstraction-and-inference.md) | Ladder of abstraction, ladder of inference, laddering interviews: the rung a problem is solved at, what a condition rests on | Requirement framing; "this keeps happening" |
| [`references/19-sources.md`](references/19-sources.md) | Where each convention claim came from (DMN hit policies, XACML, Cedar, Drools/CLIPS, CSS, EditorConfig, Bifrost, statecharts, IEC 61131-3) | Citing or double-checking a convention |
| [`references/20-finding-ladders-in-a-codebase.md`](references/20-finding-ladders-in-a-codebase.md) | **Step 1.** Audit modes by phrasing, where ladders hide, search patterns, the per-finding report table, reading the guarantee | Step 1, every invocation |
| [`references/21-reporting-asking-and-the-decision-record.md`](references/21-reporting-asking-and-the-decision-record.md) | **Steps 2-3.** Findings report shape, the options-with-trade-offs table and the ask, where and how to record the decision in the project's own format | Step 2 and Step 3 |
| [`references/22-expressing-a-ladder-as-code.md`](references/22-expressing-a-ladder-as-code.md) | **Step 4.** Pure decide / interpret split, idiom by shape, clean-code rules, matching the repo's paradigm, what to do when the repo forbids the idiom | Step 4, and reviewing the diff |

## Script

- `scripts/ladder_audit.py` — mechanical checks on a rule list: missing terminal rung, shadows (equality,
  `in` subsets, prefix containment, range inclusion), severity inversion, unreachable rungs probed from
  the rules' own conditions, order-dependence that contradicts the declared mode, impure predicates, and
  schema drift (duplicate ids, unknown fields or operators). Reads YAML-subset or JSON; with no argument
  it self-tests over eight fixtures and must catch every injected defect. Exit 1 on any finding.
- `references/` carries no runnable files on purpose: every sketch inside a reference is a language
  excerpt, not a program, so the skill stays stack-agnostic.

## Related skills

- **`error-handling`** — when the audit's finding is swallowed failures, that skill decides the contract,
  payload and organization; this one decides the order the rungs are tried in. Escalation ladders (`11`)
  and tiers (`13`) are the shared surface.
- **`stateful`** — states a screen can be found in; its precedence ladder and this skill's mode table are
  the same decision made about UI rather than about domain rules.
- **`sql-handling`**, **`language-handling`**, **`ui-handling`** — the repo's own conventions, which
  outrank any idiom suggested here (`22`).
