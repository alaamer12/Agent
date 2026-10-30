---
name: bequeath
description: 'End-of-session asset harvesting: review the whole conversation, propose what is worth keeping, and turn approved work into tested, reusable assets in the project''s bequest/ directory. Finds throwaway scripts, command sequences, debugging procedures, config snippets, queries, repeated workflows, useful patterns and instructive dead ends. Reports candidates first (name, type, original purpose, proposal, future use, direct-vs-generalize) and creates nothing until the user selects; silence is not approval. Generalizes only approved items - configurable inputs, no hardcoded values, temp paths or task assumptions - then tests beyond the original example and states verification honestly (verified automated/manual, partial, unverified). Each asset carries a card (what, when, how, inputs, outputs, assumptions, limitations, verification) beside its tests, with an index for discovery. Never stores secrets, never duplicates an asset, never claims untested reliability. Not session state or new global skills.'
when_to_use: The conversation is ending, or the user says "bequeath", "save what we learned", "keep this for next time", "turn this into something reusable" — and work performed in the session may be worth preserving beyond it.
argument-hint: "[optional scope: e.g. 'just the debugging scripts']"
---

# Bequeath

Work produced in a conversation dies with it: the debugging script that found the bug, the command sequence
that reproduced it, the query that proved the data was wrong. Future agents start from nothing and redo it.
Bequeath turns *selected* pieces of that work into **generalized, tested, reusable assets** under `bequest/`.

The contract, in order: **propose → user selects → generalize → test → store → report.** Nothing is created
before the selection; nothing is claimed as working before it was run.

## Iron rules

1. **Report first, create nothing.** Step 2 is a proposal only. No files, no refactors, no "I'll just clean it
   up while I'm here".
2. **Silence is not approval.** Proceed only on an explicit selection. "Sounds good" to one row approves that
   row. No answer means no assets.
3. **Tested means run.** Every asset you store was executed after generalization, against cases beyond the
   original example, and you can state the result. An untested asset is stored with status `unverified`, and
   that sentence is not optional.
4. **One canonical copy.** If an asset already exists in `bequeath/`, improve it in place; do not fork a
   competitor. Duplicates are how a repository of assets becomes a graveyard.
5. **No secrets, no machine paths.** Tokens, keys, emails, internal hosts and `C:\Users\...`-style paths do not
   belong in an artifact meant for another agent.

## Step 1 — reconstruct the conversation

Read the session from the beginning, not just the final state. You are looking for work that *worked* and would
be redone, and for knowledge that cost something to obtain. Check at least:

| Look at | Typical catch |
|---|---|
| Scratch scripts, `/tmp` files, notebooks | a repro or analysis that took an hour to get right |
| Shell history of the session | multi-step installs, one-liners that encode a discovered fact |
| Debugging trail | how the cause was isolated; the failing-then-passing test |
| Config and environment changes | versions, env vars, flags that made it work |
| API/database work | working request shapes, queries, migrations, backfills |
| Repetition | the same three commands run five times — a candidate automation |
| Patterns and discoveries | undocumented behavior, ordering constraints, gotchas |
| Dead ends | "X cannot work because Y" — an asset in the form of a constraint |

Do not filter for importance yet; the next step judges. A 15-line script that saved a day is worth more than a
200-line helper that was never run.

## Asset forms — all of them are supported

An asset does not have to be executable. Six forms, different storage, different notion of "tested":

| Form | Lives as | The card must contain | "Tested" means |
|---|---|---|---|
| **Script / utility** | card + code + `tests/` | exact command, inputs, exit codes | run it: original case, ≥2 variants, an edge case |
| **Command sequence** | card + a `run.sh` / `run.ps1`, or the steps alone | the ordered commands, preconditions, abort conditions | run it once in a sandbox end to end (or run the verification steps if execution is unsafe) |
| **Procedure** | **card only** — the README is the asset | numbered steps, preconditions, how to confirm each step, rollback | walk it in a throwaway environment; confirm the described end state and one documented failure |
| **Config / template** | card + the file with placeholders | every placeholder, valid values, what breaks if unchanged | apply it to a scratch copy and start the thing; confirm it loads and behaves |
| **Query / data logic** | card + `.sql` / snippet | schema assumptions, privileges, expected shape | run read-only against real or fixture data; compare row count/shape to the expectation |
| **Pattern / constraint** | card + a small check, or the card alone | the rule, one canonical example, the failure it prevents | run the check on a case that should fail and one that should pass |

A procedure with no script is not a lesser asset — it is the right form when the steps require judgment. What
makes it an asset is the card: triggers, preconditions, verification and limitations, not a file extension.

For any form: an asset whose only "test" is that its author read it twice is stored as `unverified`.

## Step 2 — the bequeath report

Present a table, one row per candidate ([`references/00-candidates-and-report.md`](references/00-candidates-and-report.md)):

| # | Name | Type | Original purpose | Bequeath proposal | Future use | Form |
|---|---|---|---|---|---|---|
| 1 | `<name>` | script / procedure / config / query / pattern / doc | <what it did in this session> | <how it becomes reusable> | <when a future agent needs it> | direct / generalize |

Then one line per row: what has to be stripped or parameterized for it to be reusable (paths, project names,
versions, credentials, task assumptions). Mark **direct** only when it is already runnable elsewhere.

If nothing qualifies — the session was one-off reading, or everything was already stored — say so in two
sentences and stop. Do not manufacture candidates to look productive.

## Step 3 — selection

Ask which candidates to proceed with. Accept per-row decisions, merges ("combine 2 and 4"), and partial
scope. Re-read the approved set back before generalizing, so a misread row does not become a wasted asset.

## Step 4 — generalize

For each approved item, preserve the behavior and remove the coupling to this conversation
([`references/01-generalization.md`](references/01-generalization.md)):

- **Inputs become parameters** with sane defaults; no hardcoded project names, paths, versions or IDs.
- **Outputs become explicit** — a file, stdout, a JSON schema — not "whatever the session needed".
- **Assumptions become documented** — version ranges, OS, data shape, required tools.
- **The simplest form wins.** A 30-line script with `--help` beats a plugin framework. Do not generalize into
  a product.
- **Keep the failing case** when the original work encoded a negative result: "this approach fails under X" is
  valuable as a check or a documented constraint.

## Step 5 — test

Define correct behavior, then test it ([`references/02-testing-and-verification.md`](references/02-testing-and-verification.md)):

1. The original case — the asset still does what the session needed.
2. At least two cases beyond it — different input, different path, empty/malformed input, missing dependency.
3. The failure mode — the expected error is clear and non-destructive.
4. Re-run after every fix, and record the actual output, not the intention.

State one of four statuses, and nothing stronger: **verified (automated)**, **verified (manual)**,
**partially verified** (say which cases are missing), **unverified** (say why — no environment, no data, or
untested by the user's request). A script that only works on the original example is not generalized; it is
an example.

## Step 6 — store in `bequest/`

Follow the layout in [`references/03-bequest-layout.md`](references/03-bequest-layout.md). If `bequest/` does not
exist, run:

```bash
python scripts/bequest_check.py --scaffold <project-root>     # creates bequest/ + INDEX.md, touches nothing else
```

```text
bequest/
├── INDEX.md                     one row per asset: name, type, verify status, path
└── <asset-slug>/
    ├── README.md                the asset card (template: assets/templates/asset-card.md)
    ├── <script-or-files>
    └── tests/                   automated tests when the asset is code
```

Every asset card carries: what it does · when to use it · how to use it (exact command) · inputs and
dependencies · expected outputs · assumptions and limitations · verification status and test instructions.
Scripts and their documentation and tests stay together.

## Step 7 — verify the stored version

Not the working copy — the stored one:

```bash
python scripts/bequest_check.py --check <project-root>
```

It checks that every asset has a card with the required sections, the status word is one of the four, links
resolve, indexed rows match directories, and flags hardcoded absolute/temp paths, secret-shaped strings and
byte-identical duplicates. Then re-run the asset's own tests from inside `bequest/`, and confirm the card's
commands match the files as stored.

## Step 8 — the final bequeath report

1. **Selected:** which candidates the user approved (and which they declined — one line).
2. **Generalizations:** for each, the original artifact → what changed (parameters added, coupling removed).
3. **Stored locations:** exact paths.
4. **Testing:** what was run, with which inputs, and the result — copied from the real output.
5. **Remaining limitations:** cases not covered, environments not available, anything stored as `unverified`.
6. **Future usage:** how a later agent discovers it (`bequest/INDEX.md`, the card's "When to use").

Distinguish completed from incomplete work explicitly. "Stored but unverified because no Python 3.8 here" is a
good report; "all assets fully tested" after one happy-path run is not.

## Boundaries

| Not this | Use instead |
|---|---|
| Saving where the current session stands so it can resume later | `flush`, `iwts` (session state, not reusable assets) |
| Creating a new *global* agent skill from a project capability | `adapt` (this skill stores project-local assets under `bequest/`) |
| Writing a narrative document of what happened | `document` — bequeath produces runnable assets plus a card, not a story |
| Publishing or sharing the assets outside the project | out of scope; nothing leaves the repo without an explicit request |

## The pair

These two skills are halves of one loop and are meant to live together:

```text
end of session            start of next task
bequeath  ---------->  bequest/  ---------->  heir
(propose, select,          INDEX.md +            (match, evaluate, verify,
 generalize, test,         cards + tests         reuse/adapt, cite)
 store)
```

[`heir`](../heir/SKILL.md) opens `bequest/INDEX.md` at the start of a task, evaluates a matching asset against
that task, runs its tests before trusting it, and improves it in place. It never writes assets — the selection
gate and the test-before-claim rules are bequeath's, and they must exist in exactly one place.

## References and assets

| Path | Owns |
|---|---|
| [`references/00-candidates-and-report.md`](references/00-candidates-and-report.md) | what qualifies, how to judge it, the report format, good and bad candidates |
| [`references/01-generalization.md`](references/01-generalization.md) | removing task coupling, parameter design, before/after transformations, the overengineering guard |
| [`references/02-testing-and-verification.md`](references/02-testing-and-verification.md) | defining correct behavior, the case matrix, status ladder, honest reporting |
| [`references/03-bequest-layout.md`](references/03-bequest-layout.md) | directory conventions, the asset card fields, index, update-vs-duplicate, git hygiene |
| [`assets/templates/asset-card.md`](assets/templates/asset-card.md) | the per-asset README, ready to copy |
| [`assets/templates/bequest-index.md`](assets/templates/bequest-index.md) | the index skeleton |
| `scripts/bequest_check.py` | scaffold + validator (card sections, status word, links, index coverage, path/secret/duplicate scan); self-test with no arguments |
