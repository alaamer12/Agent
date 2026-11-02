---
name: agents-md
description: 'Creates or audits AGENTS.md - the agent rulebook: obligations and references, not documentation - ~500 lines total, ~50 per section (overflow moves to referenced docs). Interviews; 16 sections: agent instructions; mandatory context with the active-scope fence; workflow; units (read-before-implement); design; execution + one package manager; env/secrets; debug; startup; delegation duties; privacy - path cascade, .gitignore sync, cache asks; resourceful - local over global (global = named exceptions); authority - ask per session (default) or fixed: external installs/processes, DB writes; when blocked, say honestly and ask; version control - git tiers (allowed / ask / never: rewrites, reset --hard, clean), stash policy + message pattern, commit author identity; skills - one row per skill: when it applies, what to read/do first; maintenance - same-change update; review date. Audits existing files (move-out map, no silent deletion, foreign blocks pass through); writes ONLY AGENTS.md.'
when_to_use: The user asks to create, restructure, or audit AGENTS.md (or an equivalent agent instruction file), to define how the main agent delegates to subagents, or says "agents-md this project". Also /agents-md.
argument-hint: "[project root, defaults to current repo]"

---

# Agentify - write the rulebook, not the encyclopedia

`AGENTS.md` is what an agent is *obliged to do and obliged to read*. It is not a description of the system.
Everything detailed belongs in its own file, referenced by path. If a paragraph explains how something works,
it belongs elsewhere; if it says what the agent must do, it belongs here.

**Agentify gathers; it does not assume, and it does not implement.** It asks the user the decisions, records
them as rules and pointers, and leaves the mechanisms (units generation, config generation, secret retrieval)
to their own skills. The output is exactly one file: `AGENTS.md`.

## Non-negotiable properties of the output

| Property | Test |
|---|---|
| Rules, not documentation | no section explains how the system works |
| References, not duplication | every detail is a path the agent opens, never a summary that will drift |
| Explicit active context | version, channel, and any other dimension are named, with what to **ignore** stated too |
| User-decided | no branching strategy, package manager, secret mechanism, or debug permission invented |
| Bounded | ~500 lines total, **~50 lines per section**; `scripts/agents_lint.py` flags both kinds of creep |
| Honest gaps | anything unanswered is written as `pending - not assumed`, never filled with plausible filler |
| **Current, not merely complete** | section 15 carries the maintenance duty and a `Last reviewed:` date; a rule that changed without updating this file is a wrong instruction that reads like an authoritative one |

The last one is the difference between a rulebook and a rumor: an agent cannot tell an invented default from a
decided one, and it will enforce the invented one.

## Step 1 - Look everything up before asking anything

Establish from the repository, not the user:

```bash
ls -a; test -f AGENTS.md && wc -l AGENTS.md          # existing rulebook
git log --oneline -12; git branch -a | head          # real branching and message style
ls package.json bun.lockb package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null   # package manager, by evidence
git ls-files | grep -iE "env|secret|config\.env|onepassword|1password" | head -20
find . -maxdepth 3 -type d \( -name ".repertoire" -o -name "*steering*" -o -name "docs" \
     -o -name "design" -o -name "prototype*" -o -name "scratch" \) 2>/dev/null
ls -d .cursor/skills .claude/skills .qoder/skills skills 2>/dev/null      # skill roots per harness
find . -maxdepth 3 -iname "UNITS.md" -o -maxdepth 3 -iname "*units*.md" 2>/dev/null
```

**Never ask the user what a file already says.** `inquire`'s own first rule is the same; the interview is for
decisions, not for facts I can read.

## Step 2 - Audit an existing `AGENTS.md` (if present), then propose a map

Classify every existing rule into the sixteen sections and show the user the map **before** writing anything
([`03`](references/03-audit-and-merge.md)):

```text
existing content                       | -> section | action
---------------------------------------+------------+---------------------
"Prefer CMD over PowerShell"           | 6          | keep, add reason
"pool of agents x->2x->4x" notation    | 10         | keep, add depth budget
3 paragraphs describing the sync engine| (none)     | MOVE OUT -> docs/... + pointer
"ask before deleting"                  | 1          | keep
```

- Nothing is dropped silently; a removed rule is a decision the user makes, not a formatting choice.
- A block delimited by another tool's markers (for example `theskills` pins, between two HTML comment markers)
  is copied through **verbatim** and mentioned in the report - agents-md does not own that region.

## Step 3 - Ask the remaining decisions with `inquire`, in rounds

**The interview is the backbone, not a formality:** this file sets the path every future agent and subagent
follows, so every answer here becomes a standing instruction downstream - which is exactly why an unanswered
question is recorded as pending instead of guessed.

**Deliver it in rounds, not as one wall of questions.** Each round settles one small group of sections
(2-5 questions), and the user sees the next round only after the previous one is answered and confirmed:

| Round | Sections it settles | The decisions inside it |
|---|---|---|
| **1 - What this project is, right now** | 2 (+3) | active version/channels and what is excluded; where work lands; versioning and promotion |
| **2 - The toolchain as it actually is** | 6, 7, 9 | shell/chaining pitfalls, the one package manager, environment/secrets strategy, startup steps |
| **3 - What the project already has** | 4, 5, 14 | the units index and its duties; design/prototype locations and scope; per-skill usage notes (when a skill applies, what to read/do first) |
| **4 - Agents working in this project** | 8, 10 | debug permissions; delegation naming, reports, fan-out, what a subagent may decide alone |
| **5 - Trust and boundaries** | 11, 12, 13, 16 | privacy paths and the cache question; local-vs-global install exceptions; authority settings; git permissions (what is allowed / needs asking / never), stash policy, commit authorship |

Round rules:

- **Skip what the repo answers.** Any round whose answers are already visible in the repository is skipped
  with one line saying so - the interview asks decisions, not facts.
- **One round at a time.** Present the round's questions, collect the answers, then **restate the decisions
  in a 3-6 line list** and wait for corrections before opening the next round. The restatement is where a
  misheard answer gets caught cheaply.
- **Each question must** (a) change a rule in the file, (b) be unguessable from the repository, (c) carry its
  trade-off. A question that fails any of the three is cut, not softened.
- **Stopping early is allowed.** If the user wants to stop, the remaining rounds become numbered pending
  items - never filled with defaults.
- **Maintenance (section 15) is not a round.** It is the fixed duty; only its owner and review cadence are
  worth one line if the user has an opinion.

The question bank per round: [`02`](references/02-interview-guide.md). State the full decision list back before
drafting ([`05`](references/05-delegation-and-subagents.md) for section 10 specifics).

## Step 4 - Draft from the template

Start from [`assets/templates/AGENTS-template.md`](assets/templates/AGENTS-template.md) and fill it. The sixteen
sections, in this order:

| # | Section | Must contain | Must not contain |
|---|---|---|---|
| 1 | Agent Instructions | stable behavioral rules and restrictions | version- or channel-dependent rules |
| 2 | Mandatory Context | routing table of files to read; **active** version/channel/other; **excluded** scope; "indexes are routers, follow the links" | summaries of what those files say |
| 3 | Development Workflow | branch model, where work lands, versioning format and increment duty, promotion and change management | tutorial-style git instructions |
| 4 | Units Reference | path, read-before-implement duty, reuse-over-duplicate rule, who updates it (same task, not follow-up) | the list of units itself |
| 5 | Design & Prototypes | locations, which are in active scope, how to tell current spec from future spec | design rationale prose |
| 6 | Execution & Tool Usage | shell/chaining restrictions with the failure they prevent, one package manager, scratch-script-then-delete | a command catalogue |
| 7 | Environment & Secrets | the chosen strategy, the paths/schemas involved, the prohibition on editing `.env` ad hoc | the whole config system's documentation |
| 8 | Debugging | reproduction order, what inspection/modification is permitted, verification method, cleanup | generic debugging advice |
| 9 | Agent Execution & Startup | what must be read/run/confirmed before the first change of a session | setup guide duplication |
| 10 | Main Agent & Subagents | delegation duties both ways, per-task doc list rule, the embedded pasteable block, report artifact | project architecture detail |
| 11 | Privacy | **the project's visibility policy**: private paths (skills, plans, binaries) · the **cascade** (hidden tool ⇒ its outputs are hidden too) · hidden **binaries carry an install note elsewhere**, not the file · the **`.gitignore` sync duty** · when a declared-private path is missing from `.gitignore` or was tracked before the rule, **ask the user before clearing the cache** - never delete silently | secrets themselves (section 7), a file-by-file inventory of what exists |
| 12 | Resourceful | **project-local first**: dependencies, toolchains, interpreters, environments stay in the project (the local env, not a global one, in every language); global installs are named exceptions with a reason, never a convenience default; project binaries run through the project's own tooling so the pinned version is the version used | a per-language install tutorial (the rule is language-neutral), the package manager choice (section 6) |
| 13 | Authority | **what agents may do in this environment**: which actions are ask-per-session (the safe default) or fixed (granted, with reason) - external binary installs, external processes, existing-database writes, credentials, machine-level config; project-local installs stay in section 12; when a limit blocks the requested work, the agent says honestly what it cannot do and asks, never improvising or skipping | a per-command permission catalogue, or global installs themselves (section 12) |
| 14 | Skills | **per-skill instructions**: one row per independent skill the project relies on - when it applies, and what to read/do first (the skill owns and updates its row; agents-md keeps the table) | the skill's full manual, or notes for skills the project does not use |
| 15 | Rulebook Maintenance | **the duty to keep this file current**: every decision that changes a project rule updates the file in the same change; the decision→section map (new channel, new doc, rename, moved pointer, **privacy change ⇒ same-change `.gitignore` line**, git-rule change ⇒ regenerate the block's GIT clause); a `Last reviewed: YYYY-MM-DD` line | a changelog, or technical detail that belongs in a doc |
| 16 | Version Control | **what the agent may do with git**: the tiers (allowed: read-only + commits per section 3 / ask-first: push, PRs, shared-branch merges / never-without-order: history rewrites, `reset --hard`, `clean`, force-push, `--no-verify`); the **stash policy** (allowed or not, and the message pattern that makes entries identifiable in a shared worktree); the **commit author identity** (human sole author vs `Co-authored-by` disclosure - the exact name decided once, here; this is the answer `commit` and `branch` look for before asking) | tutorial-style git commands (section 3 owns the branch model), non-git permissions (section 13), the full commit-message convention (a doc or the `commit` skill's INIT output) |

Rules that govern section 10's block: the block is a **projection of sections 1-9, 11-13, 16**, not a second
rulebook.
Generate it from the decisions already recorded, keep each clause traceable to its section, and state in the
file that editing the rulebook means regenerating the block ([`05`](references/05-delegation-and-subagents.md)).

**The 50-line section budget.** Every section is a list of obligations plus pointers - if a section runs past
about 50 lines, it has become a document. Lift its detail out into a doc under the project's own docs location,
keep 2-4 obligation lines plus a `Read: <path>` pointer, and say in the report which section split and where the
content went. The agent then carries the rulebook cheaply and opens the doc only when the task needs it. The
split is a move, not a delete: the destination doc must exist or be listed as to-create (the `document` skill
writes it; agents-md only owns the AGENTS.md side of the swap). Applies while drafting and while auditing;
`agents_lint.py` flags every section over the budget.

## Step 5 - Verify, then write the one file

```bash
python scripts/agents_lint.py AGENTS.md            # sections, line budgets, dead links, scope fence, block sync
python scripts/agents_lint.py AGENTS.md --strict    # also flags vague mandates and undocumented pending items
```

The linter checks mechanically: all sixteen headings present and ordered; total lines; every relative link
resolves on disk; the active-scope line names both what is in scope and what is excluded; the Privacy section
carries both of its duties (the `.gitignore` sync and the ask-before-clearing-the-cache rule); the Resourceful
section states the local-over-global rule; the Version Control section names permission tiers, a stash policy,
and a commit-author rule; every block clause
maps to a section; the maintenance section carries the update duty and a review date that is not
stale; and no absolute paths or foreign-project paths. Fix what it reports; do not edit the check
to make the output pass.

Then write `AGENTS.md` and report:

- the section map of anything that was already there, and what moved out (with where it went);
- **dead or missing references** - paths the rulebook points at that do not exist. agents-md reports them and
  recommends who should create them; it does not create directories or stub files itself;
- items left `pending - not assumed`, as a numbered list the user can answer later;
- the total and longest-section line counts, and which section to extract first if it grows.

## Step 6 - Keep it current, every session

The file is only worth what it is worth today. Section 15 is the duty, and the duty applies to agents-md itself:

- **A decision that changes a project rule updates `AGENTS.md` in the same change.** A new channel (`stable`
  gains `canary`), a version that stops being future and becomes current, a new mandatory document, a document
  renamed or moved, a permission that changed during debugging, a new delegation limit — each one is a section
  edit, not a note to self. See
  [`08-keeping-the-rulebook-current.md`](references/08-keeping-the-rulebook-current.md) for the decision→section
  map.
- **A privacy-rule change is two changes in one.** A newly private path must land in `.gitignore` in the same
  edit; a path that was *already tracked* before being declared private is not hidden by `.gitignore` - the
  cache-clearing step (`git rm --cached <path>`, removing local generated copies of hidden outputs) is
  **proposed to the user and asked for, never done silently**. See
  [`09-privacy-and-visibility.md`](references/09-privacy-and-visibility.md).
- **A pointer that no longer resolves is a defect, fixed immediately.** Renaming a file without fixing the row
  that cited it teaches every later session to ignore the file.
- **Rules retire.** Delete what no longer holds; a rulebook that accumulates obsolete rules is worse than an
  empty one, because the agent cannot tell which half still applies.
- **Refresh the review date** when you have verified the two highest-risk lines — the active-scope fence and
  the branch/version policy — not merely when you touch the file.
- **Subagents report drift, they do not edit it.** A subagent that finds the rulebook stale returns it as a
  finding in its report; the parent reconciles.

## Boundaries

- **One output file.** `AGENTS.md` in the project root (or the harness's equivalent if the user names it).
  No new directories, no stub docs, no generated units file, no separate block file - those are other skills'
  jobs, and creating them here would pretend a decision was made.
- **No invented defaults.** Unanswered means recorded as pending. The tempting failure is filling section 7
  with a generic env story because the repo has no config layer yet; that is a fabrication the agent will
  enforce.
- **No silent deletion** during merge, and another tool's managed block passes through untouched.
- **The `# Glossary` section is `glossary`'s content.** agents-md may add the section as an obligation +
  pointer when writing the rulebook and keeps it through audits, but never edits term entries itself, and
  never treats an outgrown glossary as its own move-out decision - that skill owns when the list becomes a
  `GLOSSARY.md`.
- **COMMITMENTS.md is `commitments-md`'s content.** agents-md adds the routing row and the reading duty for
  it (section 2), keeps a small commitment set as a section when the user chose that placement, and never
  invents or ranks priorities itself - a priority is a decision, not a formatting choice.
- **Do not document the harness's internals** as if they were stable (which instruction files it reads, marker
  formats, precedence). Record what the user's project does; hedge the rest ([`07`](references/07-harness-and-portability.md)).
- **Size is a feature.** Two budgets: ~500 lines in total, ~50 per section. If the content wants 900 lines, the
  file is holding documentation: propose the split, get the user's agreement on where it goes, leave pointers.
  A single section past ~50 lines gets the same treatment even when the whole file is short - it becomes a doc
  and a `Read:` pointer.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-what-agents-md-is.md`](references/00-what-agents-md-is.md) | The rulebook/docs boundary, the sixteen sections with worked good-vs-bad pairs, line-budget discipline | Always, before drafting |
| [`01-conditional-context.md`](references/01-conditional-context.md) | Version and channel as independent dimensions, the active/excluded scope fence, other conditional contexts, the routing table format, dead-link handling | Section 2, 5 |
| [`02-interview-guide.md`](references/02-interview-guide.md) | The five interview rounds and which questions travel together, the question bank, what is look-up-able vs must-ask, how to hand each round to `inquire`, how to record a "pending" answer | Step 3 |
| [`03-audit-and-merge.md`](references/03-audit-and-merge.md) | Classifying an existing file, the map table, move-out decisions, foreign managed blocks, conflict rules | Step 2 |
| [`04-execution-env-debug.md`](references/04-execution-env-debug.md) | Command chaining and Windows shell pitfalls, package-manager evidence, the three environment strategies and how to combine them, debugging permissions | Sections 6-8 |
| [`05-delegation-and-subagents.md`](references/05-delegation-and-subagents.md) | Main-agent duties, subagent duties, per-task doc lists, generating the pasteable block from the rulebook, report files, fan-out grammar with budgets, write-conflict rules | Section 10 |
| [`06-anti-patterns.md`](references/06-anti-patterns.md) | Encyclopedia drift, invented defaults, stale context, block rule, duplicated mandates, dead links, vague rules | Reviewing any draft |
| [`07-harness-and-portability.md`](references/07-harness-and-portability.md) | Which instruction files agents read, project vs user scope, skill/command roots, the `AGENTS.local.md` split for machine-specific rules | Step 1 and section choice |
| [`08-keeping-the-rulebook-current.md`](references/08-keeping-the-rulebook-current.md) | The maintenance duty: which decisions must update the file the same day, the decision-to-section map, rename and pointer hygiene, drift symptoms, subagent reporting | Writing section 15, and every session that changes a rule |
| [`09-privacy-and-visibility.md`](references/09-privacy-and-visibility.md) | The Privacy section: what to declare private, the producer→output cascade, hidden binaries with a documented install need, `.gitignore` sync and the ask-before-clearing-the-cache rule, audit and subagent-block behavior | Writing section 11, and any session that changes a privacy rule |

## Script and asset

- `scripts/agents_lint.py` - validates an `AGENTS.md`: sixteen sections in order, the total line budget and the
  50-line per-section budget, every relative path
  resolves, no absolute or foreign-project paths, active scope names what is included **and excluded**, the
  Privacy section carries both duties (`.gitignore` sync + ask-before-cache-clear), the Resourceful section
  states local-over-global, the Version Control section names its three duties (git permission tiers, stash
  policy, commit authorship), the subagent block traces clause-by-clause to sections, the maintenance section carries the update duty and a
  `Last reviewed:` date that is neither missing, malformed, future, nor older than 90 days, and `pending` items
  counted. `--strict` adds vague-mandate and doc-dump heuristics. Exit 0 clean, 1 findings, 2 usage error;
  self-test with no argument (twenty fixtures). Windows: `python`, not `python3`.
- `assets/templates/AGENTS-template.md` - the sixteen-section skeleton with placeholders, the scope fence, the
  embedded subagent block, and the maintenance duty with its decision-to-section map. Start every file from it
  rather than free-handing, then delete inapplicable sections rather than leaving them empty.
