# <!-- project name --> - Agent Rulebook

<!-- The H1 names the FILE (the project's rulebook). It is never the bare name of a
     section - "# Agent Instructions" above "## 1. Agent Instructions" reads as two sections
     with the same claim and no owner. -->

Instructions for AI agents working in this repository. Follow them on every task, including work delegated to
subagents. This file is a rulebook: it states what you must do and what you must read. It does not describe
the system - the files it points to do that.

<!-- agents-md:sections 1-19. No section is ever deleted for being empty - empty = guide paragraph + "none recorded yet". -->
<!-- WRITER SHAPE LAW: a section's identity is its canonical title, its order, and its content - NEVER
     the heading depth or a numbering scheme. Sections and subsections may be written in whatever
     shape fits the harness and the project (##, ###, plain bullets, bold lead-ins; "### 3.1" in this
     template is one writer's shape, not a mandate - a sub-part explained under a bold line is just
     as findable). What is never flexible: all sections exist, in order, with their duties.
     Flexibility is about the ink, never about erasing identity or content. -->
<!-- SIZE + PLACEMENT (convention, not a rule): ~500 lines for the file and ~50 per section are
     advisory heuristics for the referenced style. Routed how-to docs conventionally live under a
     "rules/" folder beside AGENTS.md (rules/development.md, rules/debugging/ui.md), or under the
     project's docs root. The user may instead keep the procedure/policy inline here - that is a
     valid choice, and length alone is not a violation. Inline rules are guaranteed to reach the
     agent every message; referenced docs cost less context but risk being skipped or forgotten.
     Ask which the user prefers. -->

---

<!-- EVERY SECTION EXISTS WHEN THIS FILE IS CREATED. The difference between sections is whether
     they carry information yet, not whether they are present: an unpopulated section keeps its
     guide paragraph plus the line "none recorded yet" - it is NEVER deleted, because the guide
     paragraph is what teaches a later agent what belongs there and when to fill it. Emptiness is
     a state that ends; a deleted section is knowledge lost forever.
     ONE OWNER PER FACT: a section must not restate data another section or a doc owns. If
     section X relates to section Y's subject, X gives at most a brief line plus a pointer -
     "see section Y" / "Read: <docs>/file.md" - and Y holds the rule. Cross-section duplication
     is the drift the maintenance duty cannot catch: two places agree today and disagree after the
     first edit. Before writing any line here ask: which section or doc OWNS this fact? -->

## 1. Agent Instructions

Stable behavioral rules, independent of version, channel, or phase.

<!-- If the user keeps a global preferences file (the `personalize` skill owns it and the precedence
     ladder): this rulebook INHERITS those preferences; any override this project needs is written
     here as an explicit line with its reason, never as a silent contradiction. -->
<!-- THE BEHAVIORAL CONTRACT: ask the user how every agent must behave and be followed, and write
     the answer here. The common shapes are EXAMPLES, not a menu - the directives are the user's
     choice, and they bind subagents too (the 6.4 block's SKILLS clause carries them):
     [declaration line] - e.g. the last line of every response names the skills used;
     [skill-usage floor] - e.g. attempt at least one applicable skill before answering any message;
     [mandatory pre-workflow] - e.g. run the grill-me skill on a plan before any implementation.
     A user who chose none gets "none recorded yet" - blank-by-forgetting is this section's only
     unforgivable state. -->
- <!-- e.g. Do not contradict the steering docs without verifying the codebase first. -->
- <!-- e.g. Ask before deleting files or rewriting history; a rebuild or a revert is cheaper than a lost artifact. -->
- <!-- e.g. Report which skill(s) you used for the task, so the claim is checkable. -->

---

## 2. Mandatory Context

**Read these at the start of every conversation, regardless of the task, and keep them in mind for every
decision.** Each index file is a router, not the answer - follow its links to the specific document that
answers your question instead of assuming the index was enough.

**Docs root:** `<docs>` = <!-- e.g. docs/ or Docs/ or src/../documentation/ -->. There is no project
without docs - they are the source of truth, and every pointer in this file hangs from this one path.
If the folder does not exist or is not declared, the agent ASKS (must-ask, never assume, never silently
create a rival location).

### 2.1 Active context

<!-- A DIMENSION IS A FENCE ACROSS SURFACES, NOT A LABEL. A version or channel can split the docs
     tree (docs/[main] vs docs/[canary]), the code tree, the build ([build flag]/naming suffix),
     and which rules apply - the Recognized-by cell states where THIS project's value actually
     shows, so a later agent can tell which file belongs to which context instead of guessing from
     one word. A dimension that genuinely reaches nothing says so ("docs split only"); what is
     banned is the empty label. Long reach goes to subsections or a referenced doc, same discipline
     as the development how-to doc's branch meanings. -->

| Dimension | Active | Recognized by - what the value governs | Out of scope - do not read or apply |
|---|---|---|---|
| Version | <!-- e.g. V1 --> | <!-- where it shows: the code tree it lives in, a docs split, a [build flag], a file-naming pattern --> | <!-- e.g. v2/ - future features only --> |
| Channel | <!-- e.g. canary --> | <!-- what flips when the channel changes: rules, docs, artifacts, deployment --> | <!-- e.g. stable-only rules where they differ --> |
| <!-- other: MVP / post-MVP, tenant, platform --> | <!-- active value --> | <!-- its reach --> | <!-- excluded value(s) --> |

Never mix documentation, requirements, or rules across dimensions. If a file belongs to an excluded context,
treat it as absent.

### 2.2 Files to read

| File | Purpose |
|---|---|
| <!-- path --> | <!-- one line: what decision this file governs --> |
| <!-- [docs/how-to/development.md] and [docs/how-to/debugging.md] --> | <!-- how-to docs are registered HERE, the section 3 router names them - one owner per path --> |
| <!-- [COMMITMENTS.md](COMMITMENTS.md) --> | <!-- declared priorities and trade-offs - read before choosing an approach that trades dimensions; owned by commitments-md --> |
| <!-- [docs/UNITS.md](docs/UNITS.md) --> | <!-- reusable-unit index - READ before implementing, reuse over duplicate, a new unit's entry lands in the same task; generated by the units owner, never hand-edited alongside unrelated work - the units duties ride this registry row --> |
| <!-- [docs/how-to/development.md], [debugging.md], [execution.md], [environment.md], [version.md] --> | <!-- register EVERY how-to doc here - the section 3 router names them; paths live only here --> |
| <!-- path --> | <!-- ... --> |

Shared/base context reads apply in every active context:

| File | Purpose |
|---|---|
| <!-- path --> | <!-- ... --> |

---

## 3. How To

<!-- PROCEDURES USUALLY LIVE IN HOW-TO DOCS, ROUTED BY TASK CLASS - BUT INLINE IS VALID. This is
     where Development Workflow and Debugging used to sit: the branch model, promotion mechanics, and
     the debug playbook are PROCEDURES, and by convention they live in docs the agent opens per task
     (conventionally under rules/: rules/development.md, rules/debugging/ui.md), not in chapters
     bound to the rulebook every session. The user may instead keep a procedure/policy inline in
     this section - then there is no Read pointer and no routed doc to update. Ask which they
     prefer: inline is guaranteed to reach the agent every message (never forgotten) but is paid
     every turn; referenced docs cost less context but the agent may skip the read or forget a rule
     it did not load. Two duties bind the router when referenced: (1) every how-to doc is REGISTERED
     once in the section 2 table - paths have one owner; this section maps task class to doc NAME,
     never repeats a path; (2) a topic that grows past one file becomes a folder
     (rules/debugging.md -> rules/debugging/ui.md + rules/debugging/backend.md) - split early,
     routing gains a line, the rulebook stays thin. The operational-meaning discipline travels INTO
     the development doc: a bare branch label without its mechanics (folder, naming pattern,
     [build flag], what ships) is still a mystery wherever it is written. -->

| Task class | Read first (each doc registered in section 2) |
|---|---|
| <!-- Development: branch flow, promotion, CI effects --> | <!-- rules/development.md --> |
| <!-- Debugging: reproduce, escalate, verify, clean up --> | <!-- rules/debugging.md --> |
| <!-- <a deeper layer of one procedure> --> | <!-- rules/debugging/<layer>.md - the folder split --> |
| <!-- Running commands, shell, package manager --> | <!-- rules/execution.md --> |
| <!-- Environment, configuration, secrets --> | <!-- rules/environment.md --> |
| <!-- Version naming, bumps, releases --> | <!-- rules/version.md - a per-track topic can be a folder: rules/version/[main].md, rules/version/[canary].md --> |

- **Routed docs own POLICY, not only steps** (the names below are illustrative pairings - which classes a project routes and what its docs are called is the project's own) - a [version doc] may carry the scheme (shape + cited spec,
  never a live value in AGENTS.md), the WRITTEN bump rule + who may bump per component, declaration-site
  sync (a multi-home number = a section 19 sync block), dual-track meanings per track, and its
  attachment blocks (changelog, release notes, public docs, tags) as subsections; [execution.md]
  carries the shell rule WITH the failure it prevents + the one package manager; [environment.md]
  carries the chosen strategy + the .env prohibition and its permitted route.
- **Read-before-act:** before working a task class, open its routed doc.
- **Write-back:** a discovered step updates that doc in the same change (section 11 routes); a
  how-to doc missing from section 2's registry is a defect, and a procedure that outgrew the doc
  becomes the next doc - never the next paragraph here.

---

## 4. Design, Prototypes, and Visual References

| Location | Scope | Use for |
|---|---|---|
| <!-- path --> | <!-- active context --> | <!-- current spec for what is shipping --> |
| <!-- path --> | <!-- excluded / future --> | <!-- future-scope work only --> |

Before treating a mockup or prototype as current, confirm it belongs to the active context. Do not mix
future-scope visuals into in-scope work, and do not assume every file in a design directory is relevant.

---

## 5. Agent Execution and Startup

Before the first change in a session:

1. <!-- read the mandatory context in section 2 -->
2. <!-- confirm the active version/channel, and how to detect it (branch, config, flag) -->
3. <!-- the minimum verification command that proves the toolchain works, or state that it was skipped -->
4. <!-- units check for implementation tasks (section 2's units duties) -->

Then, during work: <!-- reporting duties, checkpoints, when to stop and ask -->

---

## 6. Agents

### 6.1 The premise that shapes every rule below

A subagent cannot see this conversation and cannot ask follow-up questions. Anything not in its prompt is
unavailable to it. Assume the omission will be filled by a guess.

### 6.2 Main agent responsibilities

1. **Name by responsibility.** Assign each subagent a name that says what it does
   (<!-- e.g. pipeline-diff-reviewer -->); the name is used for the handle, the report file, and status
   reporting. Never a generic label.
2. **Give complete context up front.** Goal, exact files and paths already identified, decisions already made
   (naming, chosen approach, rejected options), and the precise output expected. Do not delegate the framing.
3. **List the documents it must read.** Name the specific files for that task, in the prompt, on top of the
   baseline block below. A subagent reading only the general list will miss the constraint that mattered.
4. **Propagate the duties.** Units check (section 2's registry duty), execution and shell rules (section 3), environment rules
   (section 3), and the report obligation.
5. **Bound the work.** State what the subagent may decide alone, what it must return undecided, and what it
   must not touch (files, branches, shared state). When several subagents can write, assign disjoint paths or
   sequence them.
6. **Merge, do not re-do.** When fanning out, the orchestrator splits scoped subtasks and integrates results;
   it does not perform every leaf's work itself.
7. **Collect the reports.** Confirm each finished subagent wrote its report; reconcile contradictions between
   reports before acting on them.

### 6.3 Subagent duties

- **The FULL rulebook binds a subagent like the main agent.** The block is a projection for
  the prompt, not a lesser code: obey every section - golden rules, privacy, VCS authority included.
  Scope narrows ACTIONS (a scoped task does not commit, push, bump, or do version-control work
  unless ordered), never OBLIGATIONS - and it never leaks context: private paths and other tasks'
  material stay out of every artifact written.

- Read the mandatory documents listed in your prompt in full, and follow them exactly.
- Perform only the scoped task; return anything outside it as a finding, not as a change.
- Do not create parallel components where an existing unit covers the need (section 2's units duties).
- Obey the shell, package-manager, and environment rules (sections 3-7); do not edit `.env` or rewrite history.
- Write your report (10.5) and return its summary alongside the deliverable.
- If the task is impossible as briefed, say so with the evidence rather than substituting a different goal.

### 6.4 Baseline block - paste at the top of every subagent prompt

> Generated from sections 1-5, 7-9, 12, 14, 16, 18, 19. **When the rulebook changes, regenerate this block.** It is a projection, not a
> second source of truth.

```text
=== MANDATORY AGENT PREFERENCES (read and follow) ===
The whole rulebook binds you exactly as it binds the main agent; your task scope limits the
ACTIONS you take (not which rules apply) - you do not commit, tag, bump versions or touch VCS
state unless ordered, but you violate none of them either; and you leak nothing: section 7's
privacy rules apply to every artifact you write, and context from outside your task stays out of
your report.

1. CONTEXT - <FILL active version> ; <FILL active channel> ; ignore <FILL excluded paths> - the parent
   substitutes these from section 2.1 AT PASTE TIME; volatile facts are slots, never burned values
   Read in full before deciding anything: <!-- paths, from section 2 -->
   Indexes are routers: follow the links to the doc that answers your question.
2. TASK-SPECIFIC DOCS - the master lists these below; read them and adhere exactly.
3. SKILLS - <!-- section 1's standing directives for subagents: the declaration line (last line names the skills used), the skill-usage floor (attempt an applicable skill per response), any mandatory pre-workflow; "not required" only if the user chose none -->
4. SHELL - <!-- section 3, compressed: which shell, chaining, scratch scripts and cleanup -->
5. TOOLING - <!-- section 3: the one package manager -->
6. ENV - <!-- section 3: the route to change env values, and the .env prohibition -->
7. DEBUG - <!-- the debugging how-to doc routed by section 3: permitted inspection/modification, escalation order, cleanup -->
8. UNITS - read <!-- units file --> before implementing; reuse/extend, and add an entry for any new unit
9. REPORT - write <!-- default: .subagents/<name>.md --> when finished: goal, actions, files touched, decisions,
   verification. This is in addition to your returned result.
10. PRIVACY - <!-- section 7, compressed: private paths + the rule that outputs of hidden tools stay
   private; write only into those, never commit them -->
11. RESOURCEFUL - <!-- section 8, compressed: project-local deps/toolchains/envs; no global installs
   without asking -->
12. AUTHORITY - <!-- section 9, compressed: ask before system installs, external processes, existing-DB
   writes; if blocked, say what you cannot do and ask -->
13. VCS - <!-- section 12, compressed: the tool by name, allowed/never tiers, parked-work pattern, change identity -->
14. GOLDEN - <!-- section 14, compressed: the rules that never bend, one clause line each -->
15. FACTS - <!-- section 16, copied or pointed: verified facts WIN OVER your training memory -->
16. VOICE - <!-- section 18, compressed: the register the agent speaks AND writes in; reports inherit it -->
17. SYNC - <!-- section 19, compressed: if your edit touches a block's meaning, update every linked location in the same change -->

TASK-SPECIFIC DOCS: <!-- master fills this -->
SCOPE: <!-- what you may change; what you must not -->
OUTPUT CONTRACT: <!-- the exact deliverable, in the exact form -->

=== END PREFERENCES - the task follows below ===
```

### 6.5 Reports

<!-- Default location: `.subagents/<name>.md` - hidden from view, listed in
     `.gitignore` (section 7's sync duty), never committed: reports are the working record,
     not repo content. A project may declare its own location; the default applies when it
     has not. -->

Each subagent writes <!-- e.g. .repertoire/agents/<name>.md --> containing: what it was asked to do, what it
did, files touched, decisions made and why, verification performed and its result, and anything left
undecided. <!-- If the same role can run twice: <name>-<yyyymmdd-HHmm>.md, or the rule that overwriting is fine. -->
Reports are the durable record; the returned text is not.

### 6.6 Fan-out notation, when the project uses it

`x->N1x->N2x->...` - `x` is the orchestrator; each number is the agent count at that depth; branching factor
is `count[n+1] / count[n]`. Execute: parse, split into one scoped subtask per leaf, launch depth 1 in parallel,
have each mid-depth agent spawn its children and merge before returning, root merges everything into one
response. Limits: max <!-- N --> depths and max <!-- N --> total workers; if a leaf fails, report the failure
in the merged result instead of silently re-doing its scope.

---

## 7. Privacy

**What stays hidden - and what hiding it hides along with it.** This section is the project's visibility
policy for agents: paths that must not be committed or quoted in artifacts that leave the repo, and the
duties that keep the declaration real.

- Private paths: <!-- e.g. the agent-skills folder, working-plan directories, `tools/pocketbase.exe` -->
- **Cascade:** hiding a producer hides its outputs. If the agent skills are private, the folders those
  skills write are private too - delegated/anonymous run records, generated reports, caches.
- **Hidden binaries:** the file stays out; the *need* stays in - record where to obtain/install it in
  <!-- setup doc path -->, not the binary itself.
- **Sync duty:** every private path must also appear in `.gitignore`. When this section is updated and a
  path is missing there - or was tracked before being declared private - **ask the user before clearing
  the cache** (`git rm --cached`, deleting local generated copies); an ignore rule hides the future, not
  the past. Never delete silently.
- <!-- If nothing is private, state it: "No privacy restrictions recorded; everything here is shareable as-is." -->

---

## 8. Resourceful

**Project-local first.** Anything that can be installed, pinned, or run per-project is: dependencies,
toolchains, interpreters, CLIs, environments. Global installs are exceptions, named here with their reason -
never a convenience default.

- Local environments are the rule, e.g. `[.venv]` for Python, a project install for JS tooling (never a
  global `-g` install for a project need), a per-project `[Cargo]`/`[Composer]`/`[Maven]` local store, a
  project-local toolchain for the JVM - the same idea in every language.
- Run project binaries through the project's own tooling (the venv, `node_modules/.bin`, the package
  manager's exec), so the version used is the version the project pinned.
- Global installs allowed as exceptions: <!-- e.g. none, or: the company CLI the team shares; why, and who needs it -->

---

## 9. Authority

**What agents may do in this environment, and what they must ask about first.** Every action below has one
of two settings: **ask per session** (the safe default) or **fixed** (pre-granted - record the grant here,
with its reason).

| Action | Setting |
|---|---|
| Install a binary or package outside the project (system-wide; a standalone tool such as <!-- e.g. pocketbase -->) | <!-- ask per session / fixed --> |
| Run external processes (emulators, service daemons, third-party CLIs) | <!-- ask per session / fixed --> |
| Write to an existing database outside scratch/local data | <!-- ask per session / fixed --> |
| Read or write credentials and secret stores | <!-- ask per session / fixed --> |
| Change machine-level configuration (shell profiles, global config, system services) | <!-- ask per session / fixed --> |

- Installing an external tool is not inherently forbidden: a project may genuinely need something it does
  not have (a missing binary, a package the platform lacks) - that install happens under this section's
  setting, not as a silent act and not as an automatic refusal.
- Project-local installs belong to section 8 (Resourceful): this project's dependencies, toolchains and
  environments install locally without asking, because they touch nothing outside the project.
- **When an authority limit blocks the requested work, say so and ask** - never improvise around it and
  never silently skip the blocked part. The `/honest` shape, in plain words: "Under the current authority I
  may not be able to do X, Y, Z. Shall I continue as is, or do you grant me authority for it?"

---

## 10. Skills

**Per-skill instructions, owned by the skills.** Each independent skill that matters to this project
records one row here: when it applies, and what an agent must read or do before using it - the
condition and the pointer, not the skill's whole manual.

| Skill | Use it when | Read or do first |
|---|---|---|
| <!-- plan --> | <!-- work spans more than one session --> | <!-- docs/plans/README.md - the plan format this repo follows --> |
| <!-- commit --> | <!-- before any commit --> | <!-- the message map in docs/commit-craft.md --> |

- A skill adds its row here when the project adopts it; the row is updated when the skill's usage in
  this project changes. Keep rows to one line.

---

## 11. Rulebook Maintenance

**This file is current or it is wrong.** Every session that changes a project rule updates this file in the
same change — not in a follow-up, not next sprint.

**This section is not a changelog.** The product's release history belongs to section 3 and the CHANGELOG;
this table is an *update-routing map*: when a decision changes, which section must be edited in the same
commit. Every section carries a trigger row here, because a section no decision routes to is the section that
silently rots.

- **Last reviewed:** <!-- YYYY-MM-DD -->

### What must be written here, the moment it is decided

| The decision | Section to update |
|---|---|
| A new channel, version, or other conditional context is introduced (e.g. the project adds `canary` alongside `stable`) | 2 — add the dimension, its active value, and what is now excluded |
| A new mandatory document is created | 2 (or 4/5 as appropriate) — add its row and one-line purpose |
| A document is renamed, moved, merged, or split | the row that pointed at it — fix the path in the same change that moved the file |
| A document becomes obsolete or moves out of active scope | remove or fence it; do not leave a pointer that reads as current |
| A procedure changes (branch flow, promotion, debug method) | 3 - the how-to doc itself, same change; a new task class adds a routing line AND a section 2 registration |
| A version-control rule changes (the VCS named, a tier, parked-work policy, change identity) | 12 — the tier line, **and regenerate the block's VCS clause in 6.4** |
| The user changed how they want to be asked (Exact/Broad/both, the named Exact list) | 13 — the mode, its named Exact decisions, and the pre-anonymous rule |
| A golden rule is added, retired, or reworded | 14 — **and regenerate the block's GOLDEN clause**; a golden-rule change is the loudest change in the repo |
| A named review task changes (new routine, docs budgets, table list) | 15 |
| A version policy changes (scheme, bump rule or who, a site, an attachment) | 3 - version.md, same change |
| Verification contradicted a training/prior belief (a library DOES support the thing, an API is NOT deprecated) | 16 - append the dated fact bullet in the same change; the paragraph itself is fixed text |
| A finished task revealed a step that should have been mandatory (or one proved noise) | 17 - add/remove the ritual bullet for its phase; the guide paragraph stays fixed |
| The user changed how the agent should talk or write (the chosen register, the user's own voice, the written reflection) | 18 - the mode line **and regenerate the block's VOICE clause** |
| A synced block's meaning changed (one side edited), or a new multi-home content was discovered | 19 - that block's whole table in the same change: every linked location updated, moved anchors re-anchored; if it is the version number's homes, section 3's pointer stays |
| The user changes how they want to be asked (Exact/Broad/both, the critical-question list) | 13 — the mode, its named Exact decisions, and the pre-anonymous rule |
| A new reusable component area appears, or the units index moves | 4 |
| A path becomes private (or stops being) | 7 — the entry **and the `.gitignore` line in the same change**; if the path was already tracked, ask the user before clearing the cache |
| A design/prototype directory is added, or scope changes between current and future | 4 |
| A shell, tooling, or package-manager restriction changes | 3 - execution.md |
| A dependency/local-environment rule changes, or a global install becomes an allowed exception | 8 — the exception and the local-first rule stay in one place |
| An authority setting changes (ask-per-session vs fixed), or a grant is given/revoked | 9 — the setting, its reason, and its scope in the same change |
| A skill gains a project-specific usage note (read X first, run it this way), or stops needing one | 10 — one row, condition + pointer |
| The environment or secrets strategy changes (new schema layer, provider, generation step) | 3 - environment.md |
| Debug permissions or steps change (new environment, new inspection tool) | 3 - the debugging how-to doc |
| A startup step is added or removed | 5 |
| Delegation rules change (naming, reports, autonomy, fan-out limits) | 6 — **and regenerate the block in 6.4** |
| A stable behavioral rule is added, retired, or reworded | 1 |
| The owner or review cadence of this duty changes | 11 |

### What does not belong here

Technical detail belongs in the documents this file points at. A rule change is "the envelope around the
agent": *what must be read, what may be done, by whom, in which scope*. If the sentence explains how something
works, it goes into a doc and this file gains a row.

### The drift this prevents

A rulebook that stops being updated is worse than none, because agents trust it. `stable`-only rules after
`canary` shipped, a pointer to a file renamed three months ago, a "current version is V1" line while V2 is in
development — each one is a wrong instruction that reads like an authoritative one.

Re-read the trigger map after editing: every section still has a row, and every row still names a section that
exists.

## 12. <!-- Version Control / Git / Unity VCS / Perforce: the interview is neutral, the FILE is
     not. Once the project's VCS is known, the heading IS the tool's name ("## 15. Git") and every
     line speaks its vocabulary; never spend text declaring "the VCS in use is X". -->

<!-- The version-control half of authority: what the agent may DO against this project's VCS, and
     under whose name. Concepts below are the interview's shape; the written section commits to the
     real tool - [Git] lines read differently from [Perforce] ones, where every submit is outward
     and "local commit" does not exist. The `commit` and `branch` skills detect conventions and ask
     the authorship question precisely because this section should answer it; keep it in sync with
     branch model in the development how-to doc (routed by section 3). -->

- **Allowed:** inspecting history and state always (<!-- [git status/log/diff/show] -->);
  <!-- and: local check-ins (commits/changesets) on which branches, following the development how-to doc (section 3) -->
- **Ask first:** anything outward-facing - publishing (push/submit), pull requests, merging into
  shared branches, deleting branches, release tags <!-- list what counts outward in this VCS: in
  Perforce every submit is outward; in Plastic, push to the central repo -->
- **Never without explicit user order:** history rewrites (rebase/amend/filter of published work,
  changeset reparenting), destructive restores (`reset --hard`, revert-of-others, undo to version),
  workspace purges (`clean`/wipe of unpublished work), and never bypass verification hooks to
  force a check-in - fix the cause instead.
- **Suspend-work policy** (temporary parking of unfinished changes): <!-- allowed / forbidden. If
  allowed, the naming pattern so entries are identifiable in a shared workspace - [git stash push
  -u -m "agent/<task-slug>"], [Plastic/Unity VCS shelve], [p4 revert-after-copy]; apply/restore the
  exact named entry, never a blind pop/undrop, and drop only entries this agent created. If
  forbidden, say what replaces it (a WIP check-in on a scratch branch, a separate workspace). -->
- **Change identity:** check-ins keep <!-- the repository's configured human identity / an agent
  identity -->; agent involvement is <!-- disclosed with a `Co-authored-by:` trailer naming the
  tool - state the exact name and address / invisible by choice -->. Never edit VCS config to
  change authorship; the `commit`/`branch` skills defer to this line.

## 13. Ambiguity

<!-- The standing policy for two things the anonymous modes leave behind: WHAT TYPES of questions
     the user wants and WHEN to ask them, and HOW what was decided - including the ask-or-decide
     call itself - is recorded. Whatever the project's anonymous/autonomous modes are, they are thin
     operating modes; this section owns the record convention.
     WRITE POLICY, NOT TRANSCRIPTS: this section states the kind of question and the trigger; it
     never contains the questions asked, quoted user intent, or example wording - a stored sample
     question is one more fact with two owners, and it will be quoted back as if it were the rule. -->

- **Question mode:** <!-- choose one and write it here:
  - Exact - the user answers specifics: present named implementation options ("which channel
    cipher: X, Y, Z"), never just intent ("want encryption?") - the user owns the internals;
  - Broad - the user answers intent ("do you want E2E encryption?"); mechanisms, libraries and
    internal details belong to the agent, chosen best for this project's case;
  - Both (by weight) - intent questions stay Broad; the decisions the user names as theirs are
    asked Exact, and that list is written here, not remembered. -->
- **[MANDATORY] Ask when the question carries weight:** irreversible, costly, security- or
  compliance-shaped, cross-module, or product-behavior-changing decisions are ASKED - never
  silently assumed - while the agent is in the loop. The opposite failure is equally banned:
  weightless questions (placement, naming, routine internals) are decided, never asked. An agent
  that asks about everything is as broken as one that asks about nothing.
- **Consequential asks:** route questions whose options carry danger (data exposure, irreversible
  operations, unbounded cost) through the `caution` skill so the user sees the card before the
  answer. <!-- adjust or name the project's own equivalent -->
- **Before going anonymous:** ANY mode that takes the user out of the loop (delegated runs,
  autonomous hand-offs - the condition is "the user is no longer watching", never one skill's name;
  if the project names its own such mode, write that name here) requires the critical open
  questions to be asked and settled FIRST; what
  cannot be settled before leaving is written down as an explicit assumption with its cost, never
  silently filled. Anonymous mode then switches the agent to self-decide (see section 9).
- **Decision records - the project's recording convention (this section owns it):**
  - **One file per decision**, `<docs>/decisions/<slug>.md` - `<docs>` is wherever this project's
    documentation lives (here: <!-- e.g. docs/ -->); a single combined `decisions.md` is forbidden
    as a destination: it explodes with project age. An established ADR numbering/tone wins if one
    exists.
  - **Header anchors on every record:** `Date` + `Commit` (hash at the time of the decision) +
    `App-Version` (recorded even when unchanged; stated as a change when it differs from the
    previous decision) + `Status` (settled / accepted-risk / open / superseded).
  - **Content order** (the shape a decision record teaches): the question the work asked, context, real options and
    why losers lost, choice, consequences, reversal boundary. An answer without a question is not
    a record.
  - **The ask-or-decide call is itself a decision:** choosing NOT to ask (weight judged low, or the
    user was asleep), and what was assumed instead of asked, gets the same one-file record -
    especially before/while anonymous runs.
  - The anonymous ledger lives beside the records: `<docs>/decisions/states.md` (status, remaining,
    decisions as links, uncertainties, parked findings) - resume reads it, handover writes it.

## 14. Golden Rules

<!-- The shortest section in the rulebook, and the heaviest: what never bends, whatever the task,
     deadline, or context. A golden rule NAMES ITS MECHANISM: the one sanctioned path plus the loud
     failure guarding it - typed schema + fail-fast, a single accessor, a removed raw entry point, a
     CI import gate. "Don't hardcode env vars" is a wish resting on vigilance; "every env key is
     declared in the typed schema and the app fails to start without it" is a golden rule: the safe
     path is the only path and the unsafe one is structurally impossible or instantly loud.
     Shape per rule: [the one sanctioned mechanism] + [what fails when anyone leaves it].
     "Do not X" without a mechanism is not a golden rule - it belongs nowhere in this section.
     The Review section hunts violations of these first. -->

- **<!-- Example shape (replace with the project's real mechanisms):** runtime-changeable values are
  read ONLY through [the typed settings accessor], which [fails fast at startup on unknown/missing
  keys] - source literals have no reader, so the wrong value is a boot failure, not a silent drift. -->**
- <!-- one absolute rule per line; keep the list under a screenful - a golden rule that competes
     for memory is a golden rule too many -->

## 15. Review

**Whenever a review runs - a named review task, or the self-review of your own diff - its first
pass is always:** hunt violations of this rulebook - the golden rules above all, then every other
section - in the **code AND the docs**. That is the definition of a review here, not an always-on
job between unrelated tasks (ordinary work runs section 17's After gate). A bug hunt that did not
read AGENTS.md first is reviewing against the wrong standard; a clean rulebook scan that finds
nothing while bugs exist means the scan was shallow, not that the code is pure.

Beneath that pass, this project's named review tasks <!-- each: name - what to read - what counts
as a violation. GROWTH RULE: this section is where routine work accretes - the moment it passes ~50
lines, keep the always-first rule plus a one-line index of tasks here, and move the full task
definitions to `<docs>/review.md` with `Read: <docs>/review.md` stated before any task runs. The same
rule holds for any section that swells (Ambiguity's record formats -> a conventions doc; Authority's
per-tool lines -> a doc); AGENTS.md carries obligations and pointers, docs carry the body. -->

- **Docs:** read all docs content end to end; find stale/outdated passages; find **unlinked
  docs** - nothing in any routing or chain points to them, so a reader can never arrive; any single
  doc over **500 lines** becomes a folder named after the doc, split into one-concern-per-file
  pages inside it, with an `index.md` as its local map.
- **[DB]:** learn every table; hunt hardcoded/mocked data against section 14 - every literal the
  tables could answer. <!-- [DB] is illustrative: no database, no DB task - pick the project's own
  truth-store equivalent or leave it out. Seed tasks are seeds, not a quota. -->
- <!-- e.g. **API:** learn all routes and their request/response shapes; hunt handlers that bypass
     the validation layer; ... -->

## 16. Facts

<!-- FIXED PARAGRAPH - reproduce it verbatim in generated files; only the bullets below it grow.
     This section exists because agents carry training-era knowledge that can be simply wrong for
     this project's tools and time: "library X does not support Vue", "API Y is deprecated",
     "platform Z cannot do this" - stated confidently and contradicted by a two-minute check. The
     bullets are those corrections: paid for by verification, dated, and they win over memory. -->

The bullets below are **verified facts that contradict what an agent's training or prior knowledge
would assume**. The rules are fixed:

- **These facts win over memory.** If a bullet says X and you remember not-X, follow the bullet -
  your memory is older, and it was wrong here before.
- **A suspect fact gets re-verified, never argued from memory.** Check the current source; if
  reality moved, update the bullet's date and note what changed - and if the update was a decision,
  write the decision record too (section 13).
- **Recording duty, for the whole life of the project:** the moment verification during any task
  shows a training/prior belief wrong for this project, append a dated bullet in the same change -
  believed / actual / how it was proven. Do not let the next agent re-learn it the expensive way.
- **Bullet format:** `- **<subject>** - <the truth here>. Prior belief: <what memory said>.
  Verified <YYYY-MM-DD> by <method / source / doc>.`
- Facts describe **this project's verified reality**, current as of their date; general knowledge
  belongs in no file, and stale facts are corrected in place, with the date moved - not deleted
  from memory.

<!-- seed bullets from anything the audit already proved; they accumulate for the life of the project -->
- <!-- example bullet once verified: **LibraryX supports Vue** - the wrapper package ships official
  Vue bindings. Prior belief: React-only. Verified 2026-11-01 by docs link + install test. -->

## 17. Before-Between-After

<!-- Guide paragraph is fixed; the bullets grow as the project learns what must always happen.
     These are the rituals the user can EXPECT on every piece of work without ever asking - and
     the user's CURRENT prompt overrides them for that task whenever it says otherwise (e.g.
     "run the type-check first this time" wins for that task; the ritual stands for the next).
     ADDITIVE ONLY: a ritual must add something no other section owns. "Read the mandatory docs
     before starting" is section 2 restated - it does not belong here. A phase with nothing unique
     says "none unique - owned by section N" and stays empty.
     Update trigger: any time a finished task reveals a step that should have been mandatory. -->

- **Override rule:** these rituals apply unless the user's current prompt says otherwise; a
  standing wish to change one is edited HERE (section 11 duty), not remembered informally.
- **Before a task:** <!-- usually NONE UNIQUE - reading/scope confirmation are sections 2 and 9's
  duties; record a BEFORE ritual only for what they do not cover (a task-type-specific precondition,
  e.g. a migration must start from a fresh local db copy). -->
- **While working:** <!-- e.g. before writing new code, search for an existing implementation -
  duplicated logic found mid-task is collapsed here, not later -->
- **After finishing:** <!-- e.g. run the project's type-check gate [tsc --noEmit] / [its
  equivalent in any stack] and lint; self-review the diff against section 14; note anything a
  later task must do differently in the report -->
- <!-- none recorded yet in a phase is legal - the phase header stays, the bullets wait -->

## 18. Voice

<!-- HOW THE AGENT TALKS, WHOSE REGISTER IT MATCHES, AND HOW VOICE SPLITS ACROSS SURFACES.
     The agent MAY carry several voices: one for replying to the user, another for PUBLIC documents
     (README, release notes, help), another for INTERNAL writing (decision records, reports, how-to
     docs) - a single voice everywhere is a valid choice, but it must be CHOSEN, not defaulted by
     silence. The modes below are illustrative, not a closed menu; what binds is that every choice
     is WRITTEN, known before the first answer, and honored in documents. -->

- **Registers per surface** (delete rows the project does not have; one register for all
  surfaces is fine when stated as the choice):

| Surface | Register |
|---|---|
| <!-- replying to the user --> | <!-- [concise] - answer first, reasoning on request --> |
| <!-- public documents (README, release notes, help) --> | <!-- [explanatory] - trade-offs shown, reader-first --> |
| <!-- internal documents (decision records, reports, how-to docs) --> | <!-- [ponytail] - the lazy-senior-dev minimum: shortest statement that still proves the point --> |
- **The user's register:** <!-- how the USER talks - vocabulary, directness, terseness - recorded
  once here; the agent answers at the user's level, frames questions in their words, and never
  lectures past them -->
- **Written reflection:** no surface speaks off-script - every document and artifact the agent
  writes takes the register of its surface row; nothing falls back to an ungoverned default voice.
- <!-- none recorded yet: until the user chooses, the agent keeps a neutral default and asks in the
  first conversation that produces prose -->

## 19. Sync Blocks

<!-- The writable meanings that live in MORE THAN ONE place: the same feature shipped as two SDKs
     for two languages, a document pair that must keep telling one story, config mirrors, the
     version declaration sites section 3 points here for. THE LAW: blocks sync in MEANING, not in
     letters - each home may phrase per its idiom (the [Python docstring] and the [TS type] state
     one rule in different correct words); what must never drift is what they MEAN. An unlisted
     second home is an unsynced one: finding duplicated meaning is this section's audit duty.
     THE TABLES GROW FIRST: one more block is one more table, so the tables live in their own
     file by DEFAULT - <docs>/sync-blocks.md, one named section per block, its own table inside.
     AGENTS.md keeps the law, the duty, the format, and the pointer; an inline table is legal only
     while the project has one small block. -->

- **Duty:** an edit that changes one side's meaning updates every row of that block **in the same
  change** (section 11 routes it); a moved anchor gets re-anchored in that same change -
  a line number that no longer lands is a dead pointer.
- **Format:** one table per block, rows exact: `location | line anchor | what this home carries`.
- **Location of the tables:** Read: <!-- <docs>/sync-blocks.md - create it at the first block;
  until then this line says "no blocks recorded" -->


