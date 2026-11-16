---
name: agents-md
version: 1.1.1
author: Amr
specialized: none
description: 'Creates/audits AGENTS.md - agent rulebook: obligations+references not docs, rules/ per-topic referenced is the recommendation, inline stays valid; one owner per fact (brief+pointer). 19 sections: instructions; context fence value+REACH+docs-root MUST-ASK; how-to router (also owns exec/env/version policy); startup; delegation; privacy - cascade/gitignore; resourceful - local-first; authority - ask-per-session; version control - VCS tiers, parked-work, identity; ambiguity - Exact/Broad, weighty MANDATORY, 1-file records; golden rules - never-bend, violation-shaped; review - rulebook-violations lead, then named tasks; skills - per-skill rows; facts - corrections beat memory; before-between-after - per-phase rituals (read/dedup/type-check), current prompt overrides; voice - a register per surface user''s own; sync blocks - multi-home meanings, a per-block table (site+line), meaning not letters, same-change duty; sections never deleted; maintenance - same-change+date. Writes ONLY AGENTS.md.'
when_to_use: The user asks to create, restructure, or audit AGENTS.md (or an equivalent agent instruction file), to define how the main agent delegates to subagents, or says "agents-md this project". Also /agents-md.
argument-hint: "[project root, defaults to current repo]"









---

# Agentify - write the rulebook, not the encyclopedia

`AGENTS.md` is what an agent is *obliged to do and obliged to read*. It is not a description of the system.
Detail usually belongs in its own file, referenced by path - conventionally under a `rules/` folder - but the
user may keep it inline in `AGENTS.md` instead (see "Where the rules live" below). If a paragraph explains how
something works, it belongs elsewhere; if it says what the agent must do, it belongs here.

**Agentify gathers; it does not assume, and it does not implement.** It asks the user the decisions, records
them as rules and pointers, and leaves the mechanisms (units generation, config generation, secret retrieval)
to their own skills. agents-md writes exactly one file, `AGENTS.md`; routed how-to docs it recommends are
written by their owner (the `document` skill, or the user), never stubbed here.

## Non-negotiable properties of the output

| Property | Test |
|---|---|
| Rules, not documentation | no section explains how the system works |
| References, not duplication | every detail has exactly one owner - a path the agent opens when the user chose referenced docs, or this file when the user chose inline - never a summary that will drift; **and one owner per fact across sections**: a section that touches another section's or a doc's subject writes a brief plus a pointer ("see section 3", "Read: `<docs>/file.md`"), never a restatement - two copies agree today and disagree after the first edit |
| Explicit active context | version, channel, and any other dimension are named **with their reach** - what the value governs and how the agent recognizes it (a docs split, a code tree, a build flag) - never as bare labels, with what to **ignore** stated too |
| **Identity, not heading shape** | a section is recognized by its canonical title and order; heading depth, numbering, and subsection styling belong to the writer and the harness - the shape is flexible, the identity and full content never get erased |
| User-decided | no branching strategy, package manager, secret mechanism, or debug permission invented |
| Honest gaps | anything unanswered is written as `pending - not assumed`, never filled with plausible filler |
| **All sections exist, emptiness is a state** | the created file carries every section; one with no content yet keeps its guide paragraph + "none recorded yet" - the guide is what teaches later agents what belongs there; deleting a section for being empty deletes the knowledge of what fills it |
| **Current, not merely complete** | section 11 carries the maintenance duty and a `Last reviewed:` date; a rule that changed without updating this file is a wrong instruction that reads like an authoritative one |

The last one is the difference between a rulebook and a rumor: an agent cannot tell an invented default from a
decided one, and it will enforce the invented one.

## Where the rules live: inline, or `rules/` by convention

Inline vs referenced, the `rules/` convention, the recommended one-file-per-topic shape, the advisory ~500/~50
heuristics, and what moves out as a section grows: [`00-what-agents-md-is.md`](references/00-what-agents-md-is.md).
Placement is the user's choice; size is guidance, never a finding.

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

Classify every existing rule into the nineteen sections and show the user the map **before** writing anything.
The map table - with a compact example - the move-out options, the conflict rules and the foreign managed
blocks: [`03-audit-and-merge.md`](references/03-audit-and-merge.md).

- Nothing is dropped silently; a removed rule is a decision the user makes, not a formatting choice.
- A block delimited by another tool's markers (for example `theskills` pins, between two HTML comment markers)
  is copied through **verbatim** and mentioned in the report - agents-md does not own that region.

## Step 3 - Ask the remaining decisions with `inquire`, in rounds

**The interview is the backbone, not a formality:** this file sets the path every future agent and subagent
follows, so every answer here becomes a standing instruction downstream - which is exactly why an unanswered
question is recorded as pending instead of guessed.

**Before Round 1 - research the domain, then confirm the slate** ([`02`](references/02-interview-guide.md)):
never ask a blank question; present the models this repo's stack actually supports, and settle the Section 3
(`How To`) topic list - the 5 common topics plus any 6th, 7th or Nth the repo suggests - before the questions.

**Deliver it in rounds, not as one wall of questions** - five rounds, each settling one small group of sections
(2-5 questions): what this project is, right now · the toolchain as it actually is · what the project already
has · agents working in this project · trust and boundaries. Skip a round the repository already answers; close
each settled concern with the hidden-dimensions probe (dig to "confirmed absent", then stop); restate the
decisions in 3-6 lines and wait for corrections; stopping early leaves numbered pending items, never defaults.
The round-to-question map, the research-before-asking rule, the probe, the decision bank with what each row
feeds and what to write when it stays unanswered, and how to hand a round to `inquire`:
[`02-interview-guide.md`](references/02-interview-guide.md). State the full decision list back before drafting
([`05`](references/05-delegation-and-subagents.md) for section 6 specifics).

## Step 4 - Draft from the template

Start from [`assets/templates/AGENTS-template.md`](assets/templates/AGENTS-template.md) and fill it. The nineteen
sections, in this order:

1 Agent Instructions · 2 Mandatory Context · 3 How To · 4 Design & Prototypes · 5 Agent Execution & Startup ·
6 Agents · 7 Privacy · 8 Resourceful · 9 Authority · 10 Skills · 11 Rulebook Maintenance · 12 Version Control ·
13 Ambiguity · 14 Golden Rules · 15 Review · 16 Facts · 17 Before-Between-After · 18 Voice · 19 Sync Blocks -
what each must contain and what must never land in it:
[`10-the-nineteen-sections.md`](references/10-the-nineteen-sections.md).

Rules that govern section 6's block: the block is a **projection of sections 1-5, 7-9, 12, 14, 16, 18, 19**, not a second
rulebook.
Generate it from the decisions already recorded, keep each clause traceable to its section, and state in the
file that editing the rulebook means regenerating the block ([`05`](references/05-delegation-and-subagents.md)).

## Step 5 - Verify, then write the one file

Read the draft back against the sixteen-point checklist - sections, links, scope, privacy, resourceful, version
control, voice, sync blocks, version policy, facts, rituals, ambiguity, golden rules and review, section 1, the
subagent block, maintenance - and fix what it finds rather than loosening it to make the draft pass:
[`11-verify-before-writing.md`](references/11-verify-before-writing.md). Verify by hand; there is no lint script.

Then write `AGENTS.md` and report:

- the section map of anything that was already there, and what moved out (with where it went);
- **dead or missing references** - paths the rulebook points at that do not exist. agents-md reports them and
  recommends who should create them; it does not create directories or stub files itself;
- items left `pending - not assumed`, as a numbered list the user can answer later;
- the total and longest-section line counts as advisory guidance, and - only if the user chose the referenced
  style - which section to extract first.

## Step 6 - Keep it current, every session

The file is only worth what it is worth today, and the maintenance duty applies to agents-md itself:

- **A decision that changes a project rule updates `AGENTS.md` in the same change** - a new channel, a version
  that becomes current, a new mandatory document, a rename, a permission gained while debugging, a new
  delegation limit: each is a section edit, not a note to self. A **privacy-rule change is two changes in one**:
  the `.gitignore` line lands in the same edit, and an already-tracked path is cleared from the cache only
  after asking the user - never silently. The decision-to-section map, the per-session habit and the drift
  symptoms: [`08`](references/08-keeping-the-rulebook-current.md),
  [`09`](references/09-privacy-and-visibility.md).
- **A pointer that no longer resolves is a defect, fixed immediately**; **rules retire** (a rulebook that
  accumulates obsolete rules is worse than an empty one); a verification that contradicts a prior belief
  becomes a **Facts** bullet in the same change.
- **Subagents report drift, they do not edit it**; the parent reconciles.

## Boundaries

- **One output file.** `AGENTS.md` in the project root (or the harness's equivalent if the user names it).
  No new directories, no stub docs, no generated units file, no separate block file - those are other skills'
  jobs, and creating them here would pretend a decision was made.
- **No invented defaults.** Unanswered means recorded as pending. The tempting failure is filling section 3
  with a generic env story because the repo has no config layer yet; that is a fabrication the agent will
  enforce.
- **No silent deletion** during merge, and another tool's managed block passes through untouched.
- **The `# Glossary` section is `glossary-md`'s content.** agents-md may add the section as an obligation +
  pointer when writing the rulebook and keeps it through audits, but never edits term entries itself, and
  never treats an outgrown glossary as its own move-out decision - that skill owns when the list becomes a
  `GLOSSARY.md`.
- **COMMITMENTS.md is `commitments-md`'s content.** agents-md adds the routing row and the reading duty for
  it (section 2), keeps a small commitment set as a section when the user chose that placement, and never
  invents or ranks priorities itself - a priority is a decision, not a formatting choice.
- **Do not document the harness's internals** as if they were stable (which instruction files it reads, marker
  formats, precedence). Record what the user's project does; hedge the rest ([`07`](references/07-harness-and-portability.md)).

## References

| File | Owns | Read when |
|---|---|---|
| [`00-what-agents-md-is.md`](references/00-what-agents-md-is.md) | The rulebook/docs boundary, the nineteen sections with worked good-vs-bad pairs, placement (`rules/` convention, inline vs referenced) and advisory size guidance | Always, before drafting |
| [`01-conditional-context.md`](references/01-conditional-context.md) | Version and channel as independent dimensions, the active/excluded scope fence, other conditional contexts, the routing table format, dead-link handling | Section 2, 5 |
| [`02-interview-guide.md`](references/02-interview-guide.md) | The five interview rounds and which questions travel together, the question bank, what is look-up-able vs must-ask, how to hand each round to `inquire`, how to record a "pending" answer | Step 3 |
| [`03-audit-and-merge.md`](references/03-audit-and-merge.md) | Classifying an existing file, the map table, move-out decisions, foreign managed blocks, conflict rules | Step 2 |
| [`04-execution-env-debug.md`](references/04-execution-env-debug.md) | Command chaining and Windows shell pitfalls, package-manager evidence, the three environment strategies and how to combine them, debugging permissions and the registered-instruments block - the last two feed the how-to docs §3 routes to | Sections 6, 7 and the how-to debugging doc |
| [`05-delegation-and-subagents.md`](references/05-delegation-and-subagents.md) | Main-agent duties, subagent duties, per-task doc lists, generating the pasteable block from the rulebook, report files, fan-out grammar with budgets, write-conflict rules | Section 10 |
| [`06-anti-patterns.md`](references/06-anti-patterns.md) | Encyclopedia drift, invented defaults, stale context, block rule, duplicated mandates, dead links, vague rules | Reviewing any draft |
| [`07-harness-and-portability.md`](references/07-harness-and-portability.md) | Which instruction files agents read, project vs user scope, skill/command roots, the `AGENTS.local.md` split for machine-specific rules | Step 1 and section choice |
| [`08-keeping-the-rulebook-current.md`](references/08-keeping-the-rulebook-current.md) | The maintenance duty: which decisions must update the file the same day, the decision-to-section map, rename and pointer hygiene, drift symptoms, subagent reporting | Writing section 11, and every session that changes a rule |
| [`09-privacy-and-visibility.md`](references/09-privacy-and-visibility.md) | The Privacy section: what to declare private, the producer→output cascade, hidden binaries with a documented install need, `.gitignore` sync and the ask-before-clearing-the-cache rule, audit and subagent-block behavior | Writing section 7, and any session that changes a privacy rule |
| [`10-the-nineteen-sections.md`](references/10-the-nineteen-sections.md) | The nineteen sections in their order, each with what it must contain and what must never land in it | Step 4, drafting the file |
| [`11-verify-before-writing.md`](references/11-verify-before-writing.md) | The sixteen-point checklist the draft is read back against, by hand, before `AGENTS.md` is written | Step 5, before writing |

## Asset

- `assets/templates/AGENTS-template.md` - the nineteen-section skeleton with placeholders, the scope fence, the
  embedded subagent block, and the maintenance duty with its decision-to-section map. Start every file from it
  rather than free-handing. **Every section exists in the created file - never delete one for having no content yet; an unpopulated section keeps its guide paragraph plus "none recorded yet", because the guide is what teaches later agents what belongs there.**
