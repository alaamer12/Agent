---
name: agents-md
description: 'Creates or audits a project''s AGENTS.md - the rulebook an agent follows every session: obligations and references, not documentation, ~500 lines max. Interviews via inquire and records decisions in eleven sections: agent instructions; mandatory context with an active-scope fence naming the version/channel in force and what to ignore; development workflow; units index with read-before-implement duty; design locations per context; execution rules and one package manager; environment/secrets strategy; debugging permissions; startup; the main-agent/subagent delegation contract - role naming, complete briefs (subagents cannot ask), per-task doc lists, autonomy bounds, preferences block, report files; and the maintenance duty - rule changes (a new channel, a new or renamed doc) update the file in the same change, with a checked review date. Audits an existing file (keep/move-out/drop map, no silent deletion, other tools'' managed blocks preserved) and writes ONLY AGENTS.md - dead paths reported, gaps pending.'
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
| Bounded | ~500 lines maximum; `scripts/agents_lint.py` flags creep |
| Honest gaps | anything unanswered is written as `pending - not assumed`, never filled with plausible filler |
| **Current, not merely complete** | section 11 carries the maintenance duty and a `Last reviewed:` date; a rule that changed without updating this file is a wrong instruction that reads like an authoritative one |

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

Classify every existing rule into the eleven sections and show the user the map **before** writing anything
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

## Step 3 - Ask the remaining decisions with `inquire`

Build one question page from the sections the repository could not answer ([`02`](references/02-interview-guide.md)
holds the question bank). Each question must (a) change a rule in the file, (b) be unguessable from the repo,
(c) carry its trade-off. Typical set:

1. Which version is active, and which are explicitly out of scope? Which directories map to each?
2. Which channels exist, and does any rule or document differ per channel?
3. Branching model and what may be committed where; how versions increment; who approves a promotion.
4. Is there a units reference, where it lives, and what the read/reuse/update duty is.
5. Where the design/prototype references live and how they are scoped to version/channel.
6. Command-execution restrictions (chaining, pipes, which shell hangs) and the package manager.
7. Environment strategy: type-safe validation? build-time generation from a central file? runtime secret
   store? which combination, and the paths involved.
8. Debugging: is DB inspection allowed, is modifying data allowed, how to verify GUI/visual behavior, and the
   scratch/ cleanup duty.
9. Startup: what the agent must do before its first edit.
10. Delegation: naming scheme, report location and format, fan-out depth/worker caps, what a subagent may
    decide alone.

State the decisions back in one short list before drafting ([`05`](references/05-delegation-and-subagents.md) for
section 10 specifics).

## Step 4 - Draft from the template

Start from [`assets/templates/AGENTS-template.md`](assets/templates/AGENTS-template.md) and fill it. The ten
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
| 11 | Rulebook Maintenance | **the duty to keep this file current**: every decision that changes a project rule updates the file in the same change; the decision→section map (new channel, new doc, rename, moved pointer); a `Last reviewed: YYYY-MM-DD` line | a changelog, or technical detail that belongs in a doc |

Rules that govern section 10's block: the block is a **projection of sections 1-9**, not a second rulebook.
Generate it from the decisions already recorded, keep each clause traceable to its section, and state in the
file that editing the rulebook means regenerating the block ([`05`](references/05-delegation-and-subagents.md)).

## Step 5 - Verify, then write the one file

```bash
python scripts/agents_lint.py AGENTS.md            # sections, line budget, dead links, scope fence, block sync
python scripts/agents_lint.py AGENTS.md --strict    # also flags vague mandates and undocumented pending items
```

The linter checks mechanically: all eleven headings present and ordered; total lines; every relative link
resolves on disk; the active-scope line names both what is in scope and what is excluded; every block clause
maps to a section; the maintenance section carries the update duty and a review date that is not
stale; and no absolute paths or foreign-project paths. Fix what it reports; do not edit the check
to make the output pass.

Then write `AGENTS.md` and report:

- the section map of anything that was already there, and what moved out (with where it went);
- **dead or missing references** - paths the rulebook points at that do not exist. agents-md reports them and
  recommends who should create them; it does not create directories or stub files itself;
- items left `pending - not assumed`, as a numbered list the user can answer later;
- the line count and what to cut first if it grows.

## Step 6 - Keep it current, every session

The file is only worth what it is worth today. Section 11 is the duty, and the duty applies to agents-md itself:

- **A decision that changes a project rule updates `AGENTS.md` in the same change.** A new channel (`stable`
  gains `canary`), a version that stops being future and becomes current, a new mandatory document, a document
  renamed or moved, a permission that changed during debugging, a new delegation limit — each one is a section
  edit, not a note to self. See
  [`08-keeping-the-rulebook-current.md`](references/08-keeping-the-rulebook-current.md) for the decision→section
  map.
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
- **Do not document the harness's internals** as if they were stable (which instruction files it reads, marker
  formats, precedence). Record what the user's project does; hedge the rest ([`07`](references/07-harness-and-portability.md)).
- **Size is a feature.** If the content wants 900 lines, the file is holding documentation: propose the split,
  get the user's agreement on where it goes, leave pointers.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-what-agents-md-is.md`](references/00-what-agents-md-is.md) | The rulebook/docs boundary, the eleven sections with worked good-vs-bad pairs, line-budget discipline | Always, before drafting |
| [`01-conditional-context.md`](references/01-conditional-context.md) | Version and channel as independent dimensions, the active/excluded scope fence, other conditional contexts, the routing table format, dead-link handling | Section 2, 5 |
| [`02-interview-guide.md`](references/02-interview-guide.md) | The question bank per section, what is look-up-able vs must-ask, how to hand it to `inquire`, how to record a "pending" answer | Step 3 |
| [`03-audit-and-merge.md`](references/03-audit-and-merge.md) | Classifying an existing file, the map table, move-out decisions, foreign managed blocks, conflict rules | Step 2 |
| [`04-execution-env-debug.md`](references/04-execution-env-debug.md) | Command chaining and Windows shell pitfalls, package-manager evidence, the three environment strategies and how to combine them, debugging permissions | Sections 6-8 |
| [`05-delegation-and-subagents.md`](references/05-delegation-and-subagents.md) | Main-agent duties, subagent duties, per-task doc lists, generating the pasteable block from the rulebook, report files, fan-out grammar with budgets, write-conflict rules | Section 10 |
| [`06-anti-patterns.md`](references/06-anti-patterns.md) | Encyclopedia drift, invented defaults, stale context, block rule, duplicated mandates, dead links, vague rules | Reviewing any draft |
| [`07-harness-and-portability.md`](references/07-harness-and-portability.md) | Which instruction files agents read, project vs user scope, skill/command roots, the `AGENTS.local.md` split for machine-specific rules | Step 1 and section choice |
| [`08-keeping-the-rulebook-current.md`](references/08-keeping-the-rulebook-current.md) | The maintenance duty: which decisions must update the file the same day, the decision-to-section map, rename and pointer hygiene, drift symptoms, subagent reporting | Writing section 11, and every session that changes a rule |

## Script and asset

- `scripts/agents_lint.py` - validates an `AGENTS.md`: eleven sections in order, line budget, every relative path
  resolves, no absolute or foreign-project paths, active scope names what is included **and excluded**, the
  subagent block traces clause-by-clause to sections, the maintenance section carries the update duty and a
  `Last reviewed:` date that is neither missing, malformed, future, nor older than 90 days, and `pending` items
  counted. `--strict` adds vague-mandate and doc-dump heuristics. Exit 0 clean, 1 findings, 2 usage error;
  self-test with no argument (fifteen fixtures). Windows: `python`, not `python3`.
- `assets/templates/AGENTS-template.md` - the eleven-section skeleton with placeholders, the scope fence, the
  embedded subagent block, and the maintenance duty with its decision-to-section map. Start every file from it
  rather than free-handing, then delete inapplicable sections rather than leaving them empty.
