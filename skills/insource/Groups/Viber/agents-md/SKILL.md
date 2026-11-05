---
name: agents-md
description: 'Creates/audits AGENTS.md - agent rulebook: obligations+references not docs; one owner per fact (brief+pointer). 19 sections: instructions; context fence value+REACH+docs-root MUST-ASK; how-to router (also owns exec/env/version policy); startup; delegation; privacy - cascade/gitignore; resourceful - local-first; authority - ask-per-session, honest-if-blocked; version control - VCS tiers, parked-work, identity; ambiguity - Exact/Broad, weighty MANDATORY, 1-file records; golden rules - never-bend, violation-shaped; review - rulebook-violations lead, then named tasks; skills - per-skill rows; facts - corrections beat memory; before-between-after - per-phase rituals (read/dedup/type-check), current prompt overrides; voice - a register per surface (user, public, internal writing), user''s own; sync blocks - multi-home meanings, a per-block table (site+line), meaning not letters, same-change duty; sections never deleted; maintenance - same-change+date. Writes ONLY AGENTS.md.'
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
| References, not duplication | every detail is a path the agent opens, never a summary that will drift - **and one owner per fact across sections**: a section that touches another section's or a doc's subject writes a brief plus a pointer ("see section 3", "Read: `<docs>/file.md`"), never a restatement - two copies agree today and disagree after the first edit |
| Explicit active context | version, channel, and any other dimension are named **with their reach** - what the value governs and how the agent recognizes it (a docs split, a code tree, a build flag) - never as bare labels, with what to **ignore** stated too |
| **Identity, not heading shape** | a section is recognized by its canonical title and order; heading depth, numbering, and subsection styling belong to the writer and the harness - the shape is flexible, the identity and full content never get erased |
| User-decided | no branching strategy, package manager, secret mechanism, or debug permission invented |
| Bounded | ~500 lines total, **~50 lines per section**; `scripts/agents_lint.py` flags both kinds of creep |
| Honest gaps | anything unanswered is written as `pending - not assumed`, never filled with plausible filler |
| **All sections exist, emptiness is a state** | the created file carries every section; one with no content yet keeps its guide paragraph + "none recorded yet" - the guide is what teaches later agents what belongs there; deleting a section for being empty deletes the knowledge of what fills it |
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

Classify every existing rule into the nineteen sections and show the user the map **before** writing anything
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
| **1 - What this project is, right now** | 1, 2, 3, 14 | the user's standing behavioral directives for every agent (declaration lines, skill-usage floors, mandatory pre-workflows - §1); active version/channels and what is excluded; where work lands; versioning and promotion; **the docs root (must-ask when missing - there is no project without docs)**; the golden rules that never bend |
| **2 - The toolchain as it actually is** | 3, 5 | shell/chaining pitfalls, the one package manager, environment/secrets strategy (all three as routed how-to docs), startup steps |
| **3 - What the project already has** | 2, 4, 10, 19 | the units index and its duties; design/prototype locations and scope; per-skill usage notes; the version policy (pattern, bump rule + who, sites, dual-versioning, attachments); which writable meanings have more than one home and must be tabled as sync blocks |
| **4 - Agents working in this project** | 3, 6, 15 | debug permissions; delegation naming, reports, fan-out, what a subagent may decide alone; the named review tasks (rulebook-violation pass always leads) |
| **5 - Trust and boundaries** | 7, 8, 9, 12, 13, 18 | privacy paths and the cache question; local-vs-global install exceptions; authority settings; version-control authority for whichever VCS the project uses (git, Unity VCS, Perforce...) - inspect/check-in tiers, outward-ask, never-without-order, parked-work (stash/[shelve]) policy, change identity; how the user wants to be asked (Exact / Broad / both) + where decisions get recorded; the voice the agent talks and writes in (register + the user's own) |

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
- **Maintenance (section 11) is not a round.** It is the fixed duty; only its owner and review cadence are
  worth one line if the user has an opinion.

The question bank per round: [`02`](references/02-interview-guide.md). State the full decision list back before
drafting ([`05`](references/05-delegation-and-subagents.md) for section 6 specifics).

## Step 4 - Draft from the template

Start from [`assets/templates/AGENTS-template.md`](assets/templates/AGENTS-template.md) and fill it. The nineteen
sections, in this order:

| # | Section | Must contain | Must not contain |
|---|---|---|---|
| 1 | Agent Instructions | stable behavioral rules and restrictions - **plus the user's standing behavioral directives: how every agent must BEHAVE and be FOLLOWED - [declaration lines] (e.g. the last line of each output names the skills used), [skill-usage floors] (e.g. try at least one applicable skill per response), [mandatory pre-workflows] (e.g. run grill-me before any implementation) - shapes are examples, the directives are the user's choice, and these bind subagents through the block's SKILLS clause too**; the file's H1 names the rulebook ("<project> - Agent Rulebook"), never a section's own title | version- or channel-dependent rules; silently skipping the question - an empty section says "none recorded yet", never stays blank by forgetting to ask |
| 2 | Mandatory Context | routing table of files to read - REGISTERED docs live only here (how-to docs, the units index, commitments...); **registered indexes can carry their duties on the row** (units: read-before-implement, reuse over duplicate, entry in the same task - a standalone Units section is just one path plus three duties, which is what section 2 already is) - **each dimension names its REACH: what the value governs and how to recognize it** (a docs-tree split like docs/[main] vs docs/[canary], the code tree, a [build flag], a naming pattern, which rules apply); **excluded** scope; "indexes are routers, follow the links" | summaries of what those files say; label-only dimensions (a bare value with no reach - the shallow fence that misdirects every later read) |
| 3 | How To | **the procedural router, also holding policy-shaped rules**: task class -> registered how-to doc; WHICH classes and file names exist is the project's own (found in its repo, asked when absent). What each routed kind typically owns - [a development doc]: branch model + operational meanings + promotion; [a debugging doc]: reproduce/escalate/verify/clean; [a commands doc]: shell rule WITH the failure it prevents + the one package manager; [a configuration doc]: strategy + the .env prohibition and its route; [a release/version doc]: scheme as SHAPE with its spec cited (never a live value), WRITTEN bump rule + who per component, dual-track meanings, declaration-site sync (a multi-home number = a sync block, section 19), attachment blocks as subsections - illustrative pairings, not required names or a required set. A grown kind splits into a folder ([debugging/db.md], [version/main.md]). ROUTED docs own procedures AND their policy; AGENTS.md keeps the routing line + the read-before-act and write-back duties; the docs are REGISTERED in section 2's table (one owner per path - the router names docs, never repeats paths); duties: read the routed doc before working the task class, a discovered step updates that doc in the same change (section 11 routes); token efficiency is the point - the agent opens only the file the task needs; there is no standalone Version section - a project's version policy, if it has one, belongs to its routed doc; the routing line is all AGENTS.md keeps | path re-registration duplicating section 2, procedure or policy bodies in the rulebook, bare branch labels wherever the doc lives, forgetting the router line AND the registry row when a how-to doc is added |
| 4 | Design & Prototypes | locations, which are in active scope, how to tell current spec from future spec | design rationale prose |
| 5 | Agent Execution & Startup | what must be read/run/confirmed before the first change of a session | setup guide duplication |
| 6 | Agents | delegation duties both ways, per-task doc list rule, the embedded pasteable block, report artifact; **the full rulebook binds a subagent like the main agent - scope narrows actions (no commits/VCS work unless ordered), never obligations; no context leaks into its artifacts; **the block is a template, not a snapshot - volatile facts (version, channel, docs list) are <FILL> slots the parent fills at paste time, stable policy stays fixed text** | burned volatile values (a version number frozen in the block), a second rulebook beside the first |
| 7 | Privacy | **the project's visibility policy**: private paths (skills, plans, binaries) · the **cascade** (hidden tool ⇒ its outputs are hidden too) · hidden **binaries carry an install note elsewhere**, not the file · the **`.gitignore` sync duty** · when a declared-private path is missing from `.gitignore` or was tracked before the rule, **ask the user before clearing the cache** - never delete silently | secrets themselves (section 3), a file-by-file inventory of what exists |
| 8 | Resourceful | **project-local first**: dependencies, toolchains, interpreters, environments stay in the project (the local env, not a global one, in every language); global installs are named exceptions with a reason, never a convenience default; project binaries run through the project's own tooling so the pinned version is the version used | a per-language install tutorial (the rule is language-neutral), the package manager choice (section 3) |
| 9 | Authority | **what agents may do in this environment**: which actions are ask-per-session (the safe default) or fixed (granted, with reason) - external binary installs, external processes, existing-database writes, credentials, machine-level config; project-local installs stay in section 8; when a limit blocks the requested work, the agent says honestly what it cannot do and asks, never improvising or skipping | a per-command permission catalogue, or global installs themselves (section 8) |
| 10 | Skills | **per-skill instructions**: one row per independent skill the project relies on - when it applies, and what to read/do first (the skill owns and updates its row; agents-md keeps the table) | the skill's full manual, or notes for skills the project does not use |
| 11 | Rulebook Maintenance | **the duty to keep this file current**: every decision that changes a project rule updates the file in the same change; the decision→section map (new channel, new doc, rename, moved pointer, **privacy change ⇒ same-change `.gitignore` line**, version-control change ⇒ regenerate the block's VCS clause); a `Last reviewed: YYYY-MM-DD` line | a changelog, or technical detail that belongs in a doc |
| 12 | Version Control | **authority over the project's version control** - neutrality is for the interview, the written file commits: when the project uses Git the heading IS "Git" and lines speak it natively, with no "the VCS in use" ceremony: the tiers (allowed: inspect + local commits per the development how-to doc (section 3's router) / ask-first: push, PRs, shared-branch merges / never-without-order: history rewrites, `reset --hard`, `clean`, force-push, `--no-verify`); the **parked-work policy** (stash/[shelve] allowed or not, and the naming pattern that makes entries identifiable in a shared worktree); the **change identity** (human sole author vs `Co-authored-by` disclosure - the exact name decided once, here; this is the answer `commit` and `branch` look for before asking) | tutorial-style git commands (the development how-to doc, routed by section 3, owns the branch model), non-git permissions (section 9), the full commit-message convention (a doc or the `commit` skill's INIT output) |
| 13 | Ambiguity | **how the agent asks**: the chosen question mode - **Exact** (user answers named implementation specifics, "which cipher: X/Y/Z", never just "want encryption?") or **Broad** (user answers intent, "do you want E2EE?"; internals are the agent's to choose best-for-project) - or **both by weight** with the user's Exact list written down; the **[MANDATORY] always-ask rule** - weight-bearing decisions (irreversible, costly, security, cross-module, product behavior) are asked, never silently assumed, while the user is in the loop - and its twin: trivia ("X-file inside Y-folder?") is decided, never asked; consequential options routed through `caution`; **before going anonymous** - any mode that takes the user out of the loop, never named by one skill - every critical question is asked first, leftovers written as explicit assumptions. Also owns **decision records** (anonymous/autonomous modes are thin operating modes; this section is the convention): **one file per decision** at `<docs>/decisions/<slug>.md`, never a combined `decisions.md` that explodes with project age; each record anchored **Date + Commit hash + App-Version** (version stated when it changed between decisions); content order question→context→options→choice→consequences→reversal; **the ask-or-decide call itself is a recorded decision** (what was assumed instead of asked, especially under anonymity); the anonymous ledger lives at `<docs>/decisions/states.md` | a per-command question catalogue, the authority settings themselves (section 9), the subagent no-ask rule (section 6) |
| 14 | Golden Rules | the **never-bend list**, one rule per line, each NAMING ITS MECHANISM - the one sanctioned path plus the loud failure guarding it ([typed settings schema + fail-fast at boot], [single accessor], [removed raw entry point], [CI import gate]); "don't hardcode env vars" rests on vigilance, "every env key is declared in the typed schema and startup fails without it" is unbreakable by construction - the second form or nothing goes here; keep it short - a golden rule that competes for memory is one too many; the subagent block carries a GOLDEN clause | wishes without a violation shape, the long conventions doc (that is a referenced rulebook), anything situational (situations are sections 2/13) |
| 16 | Facts | **corrections to agents' training memory**: the section's paragraph is FIXED TEXT (reproduce verbatim) - verified facts contradict what training/prior knowledge would assume, they WIN over memory, a suspect fact is re-verified and re-dated, never argued from memory; the recording duty: verification contradicts a prior belief during any task -> append the dated bullet (believed / actual / proven) in the same change. Bullets ACCUMULATE over the project's life - the section starts near-empty and grows; the subagent block carries a FACTS clause | general knowledge, opinions, anything unverified, deleting stale bullets from memory instead of re-verifying in place |
| 17 | Before-Between-After | the **always-on task rituals** in three phases - BEFORE a task (what to read/confirm first), BETWEEN/while working (e.g. search for an existing implementation before writing a new one - collapse duplication mid-task, not later), AFTER finishing (e.g. run the type-check gate [tsc --noEmit] / the project's equivalent, lint, self-review the diff against section 14). The user's CURRENT prompt overrides the rituals for that task ("run the type-check first this time" wins once); a standing wish to change a ritual edits THIS section. Guide paragraph fixed; bullets grow for the life of the project - an empty phase keeps its header | one-off instructions for a single task, the session-start ritual (that is section 5; this is every task), restating sections 2/4/9's read duties ("read the mandatory docs first" is section 2 twice - rituals are additive only) |
| 15 | Review | **when a review runs - a named review task or the diff self-review - its first pass is finding violations of this rulebook - golden rules first - in code AND docs; it is the definition of a review here, not an always-on job between unrelated tasks**; beneath it the project's named review tasks, each as "name - what to read - what counts as a violation" (e.g. Docs: stale passages, unlinked docs nothing points to, docs over 500 lines become a folder named after the doc with index.md; [DB]: learn all tables, hunt hardcoded/mocked data - seeds, not a quota, only where such a store exists) | generic "review for bugs" prose, per-task checklists that belong in docs; phrasing the violation pass as a duty that fires outside review work |
| 18 | Voice | **the register the agent speaks and writes in**: the chosen mode - [concise] (answer first, reasoning on request) / [explanatory] (trade-offs shown) / [verbose] (teaching walkthroughs) / [ponytail] (the lazy-senior-dev minimum: the shortest statement that still proves the point) - the modes are illustrative, the CHOICE is mandatory; **a register PER SURFACE** - replying to the user / [public documents] (README, release notes, help) / [internal documents] (decision records, reports, how-to docs) may each carry its own voice; one register everywhere is a valid CHOICE, never a silence-default; **the user's own register recorded** (their vocabulary, directness, terseness set the level; the agent answers at it, never lectures past it); **written reflection**: no surface speaks off-script - every document and artifact the agent writes takes the register of its surface row; the subagent block carries a VOICE clause | a transcript of past phrasings, per-audience tone rules that fight the single register, a persona the user never chose, silence-by-default ("whatever sounds right") |
| 19 | Sync Blocks | **writable meanings with more than one home**: the same feature shipped as [two SDKs in two languages], a doc pair that must tell one story, a [config mirror], the version declaration sites section 3 points here for - THE LAW: blocks sync in **MEANING, not letters** (each home may phrase per its idiom; drift of what they MEAN is the defect); **one table per block**, rows exact: `location | line anchor | what this home carries`; **the tables are born in their own file** - <docs>/sync-blocks.md, one named section per block (they explode line by line as the project grows); AGENTS.md keeps the law, the duty, the format, and the `Read:` pointer; the **same-change duty**: an edit that changes one side's meaning updates every row of that block now (section 11 routes it; a moved anchor gets re-anchored); finding an unlisted duplicated meaning during audit is a finding, not a note; the subagent block carries a SYNC clause | demanding verbatim copies (the homes correctly differ in words), one merged table mixing blocks, locations without anchors (an unsyncable "sync"), growing block tables inside AGENTS.md by default, treating this as documentation-about-code rather than a binding list |

Rules that govern section 6's block: the block is a **projection of sections 1-5, 7-9, 12, 14, 16, 18, 19**, not a second
rulebook.
Generate it from the decisions already recorded, keep each clause traceable to its section, and state in the
file that editing the rulebook means regenerating the block ([`05`](references/05-delegation-and-subagents.md)).

**The 50-line section budget.** Every section is a list of obligations plus pointers - if a section runs past
about 50 lines, it has become a document. Lift its detail out into a doc under the project's own docs location,
keep 2-4 obligation lines plus a `Read: <path>` pointer, and say in the report which section split and where the
content went. The agent then carries the rulebook cheaply and opens the doc only when the task needs it. The
split is a move, not a delete: the destination doc must exist or be listed as to-create (the `document` skill
writes it; agents-md only owns the AGENTS.md side of the swap). Applies while drafting and while auditing;
`agents_lint.py` flags every section over the budget. **Section 24 is the standing exception to "start
inline": its tables are the fastest-growing body in the rulebook, so by default they are born in
`<docs>/sync-blocks.md` from the first block.**
**This is where growth actually happens, so the budget names it:** routine sections swell quietly - §19 Review
gains a third task, a fourth, a checklist per task; §17 Ambiguity gains format detail; §13 Authority gains
per-tool lines. The moment a section is outgrown, its **body moves to a doc under `<docs>` and AGENTS.md keeps
the obligation plus the pointer** - Review's always-first rule stays (one line), the task definitions move to
`<docs>/review.md` with `Read: <docs>/review.md` before the task list runs; Ambiguity's record format moves to
`<docs>/decision-conventions.md` the same way. A section that stayed small is the only section nobody had to
decide this about; when in doubt, split early - a pointer is cheap, a bloated rulebook is paid on every
session.

## Step 5 - Verify, then write the one file

```bash
python scripts/agents_lint.py AGENTS.md            # sections, line budgets, dead links, scope fence, block sync
python scripts/agents_lint.py AGENTS.md --strict    # also flags vague mandates and undocumented pending items
```

The linter checks mechanically: all nineteen headings present and ordered; total lines; every relative link
resolves on disk; the active-scope line names both what is in scope and what is excluded, and every
context dimension carries its reach (what it governs / how to recognize it), not a bare label; the Privacy section
carries both of its duties (the `.gitignore` sync and the ask-before-clearing-the-cache rule); the Resourceful
section states the local-over-global rule; the Version Control section names the VCS, its authority tiers, a parked-work policy,
and a change-identity rule; the Voice section names the chosen register, the user''s own, and binds it to written artifacts; every sync block carries its own table (locations + line anchors, the meaning law, the same-change duty); the Version section declares pattern, bump rule + who, the sync sites, and attachments; the Facts section carries its fixed trust-over-memory paragraph and the recording duty; the before-between-after section names all three phases and the user-override rule; the Ambiguity section names the Exact/Broad question modes, the mandatory-ask rule, the pre-anonymous rule, and the one-file-per-decision record convention with Date/Commit/App-Version anchors; the Golden Rules section states nothing casual, the Review section puts rulebook-violation hunting first, and section 1 answers the behavioral-contract question (a standing directive or an honest 'none recorded yet' - never blank-by-forgotten); every block clause
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
- **Verification that contradicts a prior belief becomes a Facts bullet in the same change** - the
  section that starts nearly empty is the one that grows for the whole life of the file; letting the
  next agent re-learn "library X DOES support Vue" the expensive way is the defect this prevents.
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
- **No invented defaults.** Unanswered means recorded as pending. The tempting failure is filling section 3
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
| [`00-what-agents-md-is.md`](references/00-what-agents-md-is.md) | The rulebook/docs boundary, the nineteen sections with worked good-vs-bad pairs, line-budget discipline | Always, before drafting |
| [`01-conditional-context.md`](references/01-conditional-context.md) | Version and channel as independent dimensions, the active/excluded scope fence, other conditional contexts, the routing table format, dead-link handling | Section 2, 5 |
| [`02-interview-guide.md`](references/02-interview-guide.md) | The five interview rounds and which questions travel together, the question bank, what is look-up-able vs must-ask, how to hand each round to `inquire`, how to record a "pending" answer | Step 3 |
| [`03-audit-and-merge.md`](references/03-audit-and-merge.md) | Classifying an existing file, the map table, move-out decisions, foreign managed blocks, conflict rules | Step 2 |
| [`04-execution-env-debug.md`](references/04-execution-env-debug.md) | Command chaining and Windows shell pitfalls, package-manager evidence, the three environment strategies and how to combine them, debugging permissions - the last two feed the how-to docs §3 routes to | Sections 6, 7 and the how-to debugging doc |
| [`05-delegation-and-subagents.md`](references/05-delegation-and-subagents.md) | Main-agent duties, subagent duties, per-task doc lists, generating the pasteable block from the rulebook, report files, fan-out grammar with budgets, write-conflict rules | Section 10 |
| [`06-anti-patterns.md`](references/06-anti-patterns.md) | Encyclopedia drift, invented defaults, stale context, block rule, duplicated mandates, dead links, vague rules | Reviewing any draft |
| [`07-harness-and-portability.md`](references/07-harness-and-portability.md) | Which instruction files agents read, project vs user scope, skill/command roots, the `AGENTS.local.md` split for machine-specific rules | Step 1 and section choice |
| [`08-keeping-the-rulebook-current.md`](references/08-keeping-the-rulebook-current.md) | The maintenance duty: which decisions must update the file the same day, the decision-to-section map, rename and pointer hygiene, drift symptoms, subagent reporting | Writing section 11, and every session that changes a rule |
| [`09-privacy-and-visibility.md`](references/09-privacy-and-visibility.md) | The Privacy section: what to declare private, the producer→output cascade, hidden binaries with a documented install need, `.gitignore` sync and the ask-before-clearing-the-cache rule, audit and subagent-block behavior | Writing section 7, and any session that changes a privacy rule |

## Script and asset

- `scripts/agents_lint.py` - validates an `AGENTS.md`: nineteen sections in order, the total line budget and the
  50-line per-section budget, every relative path
  resolves, no absolute or foreign-project paths, active scope names what is included **and excluded**, the
  Privacy section carries both duties (`.gitignore` sync + ask-before-cache-clear), the Resourceful section
  states local-over-global, the Version Control section names its four duties (the tool - by heading or
  first line, authority tiers, parked-work policy, change identity), the Voice section carries its three duties (register, user''s own, written reflection), the Sync Blocks section carries per-block tables with the meaning law and the same-change duty, the subagent block traces clause-by-clause to sections, the maintenance section carries the update duty and a
  `Last reviewed:` date that is neither missing, malformed, future, nor older than 90 days, and `pending` items
  counted. `--strict` adds vague-mandate and doc-dump heuristics. Exit 0 clean, 1 findings, 2 usage error;
  self-test with no argument (twenty-nine fixtures). Windows: `python`, not `python3`.
- `assets/templates/AGENTS-template.md` - the nineteen-section skeleton with placeholders, the scope fence, the
  embedded subagent block, and the maintenance duty with its decision-to-section map. Start every file from it
  rather than free-handing. **Every section exists in the created file - never delete one for having no content yet; an unpopulated section keeps its guide paragraph plus "none recorded yet", because the guide is what teaches later agents what belongs there.**
