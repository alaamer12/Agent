# Interview guide - ask only what the repository cannot answer

`AGENTS.md` records **decisions**. A decision is a question whose answer changes a rule in the file and cannot
be looked up. Everything else is reconnaissance, and reconnaissance is not the user's job.

## The three-question filter

Keep a question only if all three hold:

1. **The answer changes a rule.** "What's the project name?" changes nothing in the file.
2. **The repository does not already say it.** If `bun.lockb` exists, the package manager is Bun; asking
   wastes the user's attention and signals I did not look.
3. **The alternative is a guess I would have to enforce.** If I can leave it `pending` without breaking the
   agent's other duties, asking may still not be worth it - but inventing never is.

## The universal "research the domain before asking" rule

A static question list always misses the nuances of how an engineering domain works in practice. Therefore,
**for every section of `AGENTS.md` and every topic in Section 3 (`How To`)**, the agent has a standing duty
**before** formulating its interview questions:

1. **Research & enumerate the professional properties of the topic:** What are all the structural properties,
   professional patterns, edge cases, and failure modes of doing that topic at a high standard in this project's
   stack? (Inspect the repo, manifests, and framework/tool docs—e.g. Turbo, Nx, Changesets, Expo, Prisma,
   Unity VCS—so your questions reflect real domain mastery).
2. **Contrast viable architectural models instead of asking blank questions:** Never ask a bare *"How do you
   want to handle X?"* Surface the concrete models and their trade-offs in this repo so the user's horizons are
   expanded and they can pick or combine the exact properties they need.
3. **Probe edge cases, rollback/fallback, and automation boundaries:** Under every topic, think past the happy
   path: *what happens when this fails, needs a rollback/fallback, crosses multiple packages, or is touched by a
   subagent?*

## The hidden-dimensions probe

Every concern the interview settles gets this probe **before its round closes** - most dimensions are invisible
until asked about, and a rulebook that misses one silently enforces the wrong story later. For each settled
concern, ask: *along what axis could this exist in more than one version, with different rules per version?*

Commonly hidden dimensions (examples, not a menu - propose only what the repo could plausibly have):

| dimension | what it changes in the rulebook |
|---|---|
| **Install/run scope** - per-user vs per-machine (system) editions of the same app | version and upgrade authority (who may write Program Files vs `%LOCALAPPDATA%`), uninstall rules, autostart/service rights, the promotion doc's edit permissions |
| **Database migration lineage** - schema versions travel independently of the app version | which engines, forward-only or rollback-capable, who stamps migrations, which how-to doc (`rules/migrations.md`) owns the sequence |
| **Release channels** - stable/beta/canary | per-channel rule differences and the REACH that detects the channel (section 2) |
| **Target platform** - web/desktop/mobile, OS variants | platform-conditional commands, per-platform review passes |
| **Deployment mode** - cloud vs self-hosted; tenancy/region | config strategy, feature exclusions, privacy section reach |
| **Audience split of identifiers** - public version vs internal build number | already asked in Q24's dual-versioning clause; the probe makes sure it is not skipped |
| **Online/offline or sync mode** | conflict-resolution topic, verification rules |

Probe discipline - the balance this exists to keep:

- **Ask once, with evidence or an example, per concern** - "your installer writes to a per-user folder; do you
  also ship a machine-wide edition?" is a probe; "does your CLI have a submarine mode?" is invention.
- **A dimension with no trace stays out of the file**, recorded as one honest line ("no per-system edition -
  confirmed absent") when it was plausible enough to ask, and unmentioned when it was not.
- **Overlooking and overengineering both fail the same way** - the first discovers itself in a broken session,
  the second is paid for in every session. Dig to "confirmed absent", stop there.

## Inferable from the repo - look these up, do not ask

| Fact | Evidence |
|---|---|
| Package manager | `bun.lockb` / `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`; `packageManager` field in `package.json` |
| Active branch and the branch actually being committed to | `git branch --show-current`, `git log --oneline -20 --all`, merge patterns in history |
| Version format and base | `.csproj` `ApplicationVersion`/`InformationalVersion`, `package.json` version, `Cargo.toml`, `gradle.properties`, changelog headers |
| Commit message convention | 3-40 real subjects; presence of type prefixes correlates with commitlint config |
| Tooling enforcement | `.commitlintrc*`, `.husky/`, `.pre-commit-config.yaml`, `.editorconfig`, lint configs, CI workflow files |
| Docs tree and version dirs | `find` for `docs/`, `.repertoire/`, `steering`, `v1/`, `v2/`, `design/`, `prototype/`, `scratch/` |
| Skill/command roots | `.cursor/skills`, `.claude/skills`, `.qoder/skills`, `skills/`, `.cursor/commands` |
| Env plumbing | `config.env`, `.env.example`, `*.schema.ts` env files, `1password`/`op` references in scripts or CI |
| Test and build commands | CI workflow steps (the safest source), `package.json` scripts, `Makefile`, build docs |
| Data store | connection config keys, migrations folder, ORM config |

If two sources conflict (lockfiles for two managers, CI on three), **that** is a question - with the conflict
named: "There is both `bun.lockb` and `package-lock.json`; history shows both used. Which is authoritative -
the other gets deleted or ignored?"

## Pre-round discovery summary & slate confirmation

Before firing Round 1, do not march blindly through preset questions. Present a compact discovery summary from
Step 1 reconnaissance:

- **Already answered by the repo (Skipped):** package manager, VCS, detected branches, existing docs root, etc.
- **Standard sections needing decisions:** which of the 19 sections have unresolved choices.
- **Repo-specific anomalies/gaps spotted:** conflicts or unique traits found in the repo (e.g., multiple
  lockfiles, monorepo packages with mixed versions, concurrent agent markers, custom codegen steps) that need a
  decision.
- **The Section 3 (`How To`) topic slate (see below):** which of the 5 common topics apply, plus any **6th, 7th,
  or Nth project-specific topics** discovered from the codebase, asking the user which to keep, drop, or add before
  interviewing on them.

## Dedicated mechanism for Section 3 (`How To`) - the dynamic N-topic router

Every other section in `AGENTS.md` has a fixed single subject (Section 7 is always Privacy, Section 12 is always
VCS, Section 18 is always Voice). **Section 3 (`How To`) is the only open-ended, polymorphic section in the
rulebook:**

- It routes **task classes -> procedural & policy docs** (or holds them inline).
- The 5 topics mentioned in `SKILL.md` (`development`, `debugging`, `execution`, `environment`, `version`) are
  **common starting candidates, NOT a fixed 5-item quota**.
- Depending on the project, Section 3 might need **3 topics, 5 topics, 6 topics, or 10 topics**.

### Step A: The `How To` topic-slate gate (discover, propose, and ask before interviewing)

1. **Evaluate the 5 common topics against the repo:** Check which of `[development, debugging, execution,
   environment, version]` actually apply here.
2. **Think critically about a 6th, 7th, or Nth missing topic:** Based on the repo's stack and domain, ask
   yourself: *"What recurring engineering procedure or policy in this specific project will an agent get wrong if
   it isn't a `How To` topic?"*
   - *Examples of 6th+ topics:* Database migrations & rollback policy, Codegen / protobuf / OpenAPI sync,
     Multi-package / SDK lockstep parity, Asset / shader pipeline, Offline sync / conflict resolution,
     Localization / RTL rules, Release publishing & signing.
3. **Ask the user to confirm the `How To` slate first:**
   > *"For Section 3 (`How To`), here are the baseline topics `[e.g., 1. Development, 2. Debugging, 3. Execution, 4. Environment, 5. Version]`, plus `[6. <Repo-Specific Topic>, ...]` that your project seems to need.*
   > *1. Do you want to keep these topics, drop any of them, or add another topic?*
   > *2. Should their rules live as separate routed files (e.g. `rules/<topic>.md`) or inline inside `AGENTS.md`?"*

### Step B: Deep-dive research & question generation for each confirmed `How To` topic

Once the user confirms the exact list of `N` topics for Section 3, research the professional anatomy of each
confirmed topic and probe its specific angles:

- **If `Version / Releases` is in the slate (feeds Q4 & Q24):**
  - *Research mandate:* Inspect all manifests/packages in the repo and consider monorepo lockstep vs.
    independent versioning, prerelease channels, hotfix backports, automated changelogs, and store/binary build
    numbers.
  - *Multi-package / SDK topology:* If the repo has multiple packages/modules/plugins, how do their versions
    relate? **Unified / Lockstep SDK** (e.g., Expo style where `SDK 58` means `expo-ui@58.x`,
    `expo-camera@58.x` all align and release together) vs. **Independent per-package** (each package bumps only
    when its own code changes) vs. **Core lockstep + independent satellites** (with a compatibility matrix)?
  - *Fallback / hotfix / deprecation policy:* How are hotfixes patched onto older releases, how are breaking
    changes deprecated before removal, and how is a bad release rolled back?
- **If `Development / Branch Flow` is in the slate (feeds Q3):**
  - *Research mandate:* Inspect `git branch -a`, `git log --graph`, and CI workflows to map trunk-based,
    GitFlow, or release-train models.
  - *Operational meaning & rollback:* What each branch (`main`, `canary`, `develop`, `release/*`) actually
    governs (directory tree, build flags, CI pipeline, deployment environment), merge strategy (squash vs. merge
    commit vs. rebase), and how a broken merge on a shared track is reverted or hotfixed.
- **If `Debugging & Verification` is in the slate (feeds Q10 & [`04`](04-execution-env-debug.md)):**
  - *Research mandate:* Inspect the project's layers (UI, API, DB, workers, native bridge) and observability
    tools.
  - *Single playbook vs. folder split:* Should debugging stay one file (`rules/debugging.md`) or split by layer
    (`rules/debugging/ui.md`, `rules/debugging/db.md`, `rules/debugging/workers.md`)? Plus deterministic repro
    methods, read vs. mutate safety per environment, visual proof, and scratch cleanup.
- **If `Execution & Tooling` or `Environment & Configuration` is in the slate (feeds Q7–9 & [`04`](04-execution-env-debug.md)):**
  - *Research mandate:* Inspect task runners (`turbo`, `nx`, `make`), shell pitfalls, daemon management, and how
    config flows from secret stores/templates into build-time and boot-time validation schemas.
- **For ANY 6th, 7th, or custom topic confirmed by the user (`<custom-topic>.md`):**
  - *Research mandate:* First research what a production-grade standard for `<custom-topic>` requires in this
    tech stack (its core properties, invariants, failure modes, and fallback mechanisms), then generate **3 to 5
    deep questions** across four axes:
    1. **Architecture & Topology:** How is `<custom-topic>` structured across the repo (single source of truth,
       module boundaries, lockstep vs. independent parts)?
    2. **Standard Procedure & Fallback/Safety:** What is the exact sequence to make a change, and how are
       rollbacks, migrations, or fallbacks handled safely?
    3. **Hard Prohibitions & Authority:** What must an agent *never* edit or run by hand, and which actions
       require user approval?
    4. **Verification & Sync Ripple:** What automated check proves `<custom-topic>` is healthy, and which other
       files/docs/sync-blocks must update in the same commit?

## Rounds - the interview is delivered in waves, not one wall

Each round settles one small group of sections (2-5 questions). Present a round, collect its answers,
restate the decisions in a 3-6 line list, and only then open the next round. Rounds the repository already
answers are skipped with one line saying so.

| Round | Sections | Question numbers from the bank |
|---|---|---|
| **1 - What this project is, right now** | 1, 2, 3, 14 | Slate confirmation, 1, 2, 3, 4, 22, 28 |
| **2 - The toolchain as it actually is** | 3, 5 | 7, 8, 9, 11 (+ confirmed `How To` custom topics) |
| **3 - What the project already has** | 2, 3, 4, 10, 19 | 5, 6, 19, 24, 27 |
| **4 - Agents working in this project** | 3, 6, 15, 17 | 10, 12, 13, 14, 15, 23, 25 |
| **5 - Trust and boundaries** | 7, 8, 9, 12, 13, 18 | 16, 17, 18, 20, 21, 26 |

Maintenance (11) and Facts (16) are not rounds: the first is the fixed duty, the second fixed text whose bullets only accumulate - neither needs an interview question, though the audit seeds Facts from evidence it already proved. Ask only for an owner or review cadence if the user
has an opinion. If the user stops early, the remaining rounds become numbered pending items - never defaults.

## Must ask - the decision bank

Ask only for the sections the repo left unresolved. Each row shows the rule it produces; the round table
above says which rows travel together. Before asking any row, apply the **research-before-asking rule** above so
options are concrete and grounded in the repo's stack.

| # | Question | Feeds | If unanswered |
|---|---|---|---|
| 1 | Which version is active now, and which must be ignored? | 2 | the file cannot fence scope; highest-cost omission |
| 2 | Which channels exist; do any rules differ per channel? How does the agent detect the channel? **Also research & ask:** what other dimensions split code, docs, or build rules in this repo (e.g. target platform `mobile`/`web`/`desktop`, deployment mode `cloud`/`self-hosted`, tenancy/region, online/offline-first)? | 2, 3 | leave unconfirmed dimensions out of the table and say so |
| 3 | Where does new work land, and what may never be committed directly? Who approves promotion, what is the operational meaning of each branch, and how is a bad merge rolled back? | 3 | record the observed branch pattern as *inferred, unconfirmed* |
| 4 | Version format and increment duty; who may change the base version? | 3 - version.md (procedures route via 3) | pointer to the file holding it, no invented format |
| 5 | Is there a units index? Where? Reuse-or-extend duty? Who updates it when a subagent adds a unit? | 2 - the units duties ride section 2's registry row | `pending - no units reference yet` |
| 6 | Where do design/prototype/spec references live, which are in scope, and **what is the fidelity contract** (strict pixel-parity convergence, structural/behavioral parity, or directional inspiration)? | 4 | omit section 4 with one line saying the project has none |
| 7 | Which shell must be avoided and why; chaining allowed? Scratch script location and cleanup duty? | 3 - execution.md | ask; this is environment-specific knowledge only the user has |
| 8 | One package manager, confirmed? | 3 - execution.md | use the inferred one, marked *inferred from lockfile* |
| 9 | Environment strategy: type-safe schema? build-time generation from a central file? runtime secret store? paths and commands | 3 - environment.md | `pending` + the prohibition that is always safe: do not edit `.env` directly |
| 10 | Debugging: single playbook or folder split by layer (`ui.md`, `db.md`)? Inspect data permitted? Modify permitted, in which environment? How to verify visual/GUI behavior? | 3 - the debugging how-to doc | permit read-only inspection locally, require a question for anything mutating |
| 11 | What must happen before the first edit in a session? | 5 | derive from sections 2, 3, 4 as a startup checklist |
| 12 | Subagent naming scheme; report location and filename pattern; is reusing a role name allowed to overwrite? | 6 | propose a default and mark it *proposed* |
| 13 | What may a subagent decide alone vs return undecided, and how are parallel write-isolation boundaries (lockfiles, barrel exports, migrations, codegen) enforced? | 6 | default: reversible local edits in disjoint scope = decide; anything crossing files/branches/destructive = return undecided |
| 14 | Fan-out: max depths and max total workers; what happens when a leaf fails | 6 | cap at 2 depths and report the cap as a default |
| 15 | Any mandatory-skill rule for this project? | 1, 6 | omit; do not invent an obligation to use skills the project may not have |
| 16 | What stays private from version control and other agents' sight - skill folders, plans, run records? What do those tools output (the cascade - hidden tool means hidden outputs)? Which binaries are hidden, and where does their install note live instead? If any of that was already tracked, may it be cleared from the cache after asking? | 7 | state "no privacy restrictions recorded"; never guess what the user wants hidden |
| 17 | Is anything ever installed globally on purpose - a shared CLI, a system package? Everything else stays project-local (dependencies, toolchains, interpreters, environments) | 8 | default: local-first, no exceptions |
| 18 | Which environment actions need permission - external binary installs, external processes (emulators, daemons), existing-database writes, credentials, machine config? Ask per session (safe default) or fixed per action? | 9 | default: ask per session; when a limit blocks work, say what cannot be done and ask |
| 19 | Which project skills does the team rely on, and what must an agent read or do before using each (required document, scratch rule, format)? One row per skill | 10 | omit; skills add their own rows when adopted |
| 20 | Which VCS does this project use ([Git], [Unity VCS/Plastic], [Perforce], [Mercurial], [SVN]) - concepts are for the interview; once answered, the written section takes the tool's name as its heading (## Git) and speaks its vocabulary directly, no neutral ceremony. Version control: which operations may an agent do freely (read-only? commits?), which need asking (push, PR, shared-branch merge), which are never without explicit order (rebase/amend of pushed work, `reset --hard`, `clean`, force-push)? Is parking unfinished work allowed (git stash / [shelve] / equivalent) - and with which message pattern so entries are identifiable in a shared worktree, or what replaces it? Whose name do agent-made commits carry - human sole author, a `Co-authored-by:` trailer (exact name and address), or an agent identity? (`commit` and `branch` ask the authorship question only because this answer is missing.) | 12 | default: read-only + local commits allowed, push asks, rewrites/clean/reset never; stash forbidden (use worktrees or WIP commits); keep configured identity, no trailer - all marked *default, unconfirmed* |
| 21 | How do you want to be asked? **Exact** - I present named implementation specifics and you choose ("which channel cipher: X, Y, Z"), you own internals. **Broad** - I ask intent ("do you want E2EE?"), you answer, and I choose the internals best for the project. **Both by weight** - intent stays Broad, and you name the few decisions you want Exact (which get written here). Then the fixed duty regardless of mode: weight-bearing questions (irreversible, costly, security, cross-module) are ALWAYS asked while you are in the loop, trivia is never asked; consequential options route through `caution`; before any anonymous run, your critical questions get answered first. Where do lasting decisions get written? Default: one file per decision in `<docs>/decisions/` with Date + Commit + App-Version anchors (never a combined decisions.md), the run ledger beside them at `states.md` - the ask-or-decide call itself recorded too. | 13 | default: Broad by weight with the always-ask mandate, the pre-anonymous rule and the one-file-per-decision convention; stated as *default, unconfirmed* |
| 22 | Where is the docs root? (MUST-ASK when the folder is missing or undeclared - there is no project without docs; the path is declared in section 2 and every pointer hangs from it, including `<docs>/decisions/`.) And: what does this project treat as **golden rules** - the list that never bends whatever the task or deadline? **(Inspect existing linters, schemas, boundaries, and git history first to propose 2–4 candidate golden rules with their concrete enforcement mechanisms for the user to approve or edit.)** Each rule must name its mechanism + loud failure. Also: placement of the procedural detail - the skill **recommends one dedicated referenced file per topic**
(`rules/version.md`, `rules/debugging.md`, …) so every session pays only the routing line and reads the file
its task names; the alternative is inline in `AGENTS.md` (guaranteed to reach the agent every message, paid
every turn). The user decides; recommend the referenced split and ask. | 2, 3, 14 | never invent the docs path and never skip the declaration; golden rules default: none recorded, said so; placement: referenced-per-topic **as the recommendation**, stated to the user as theirs to override |
| 23 | What named review routines does the project run? Every review starts with the same first pass - hunt violations of this rulebook (golden rules first) in code AND docs; below it, each task: name, what to read, what counts as a violation. Offer the common two as seeds (`Docs` and `[DB]`), **and research/propose domain-specific review passes that fit this project** (e.g., `API/SDK breaking-change pass`, `UI accessibility/RTL/CLS pass`, `Security/authz boundary pass`, `Concurrency/memory pass`). | 15 | record only the always-first pass; named tasks stay pending |
| 24 | Version policy, in full: **multi-package/SDK topology** (lockstep unified SDK like Expo `SDK 58` across all packages vs. independent per-package vs. core lockstep + satellites); which pattern - [SemVer - semver.org], [CalVer - calver.org], [SDK-style major-per-release], [base + dev tag] are illustrative, the project may mix or own its scheme; **cite the chosen spec, never restate or invent its rules**; what bumps which component (every fix? milestones? release cuts only) - a WRITTEN rule, because letting the agent guess the bump kind probabilistically is the failure this question replaces; who may bump ([explicit request] / [agent by rule] / [agent asks]); one version or two audiences (public vs internal/build code) and the mapping; hotfix/deprecation/rollback rules; every declaration site where the number is written (project file, platform manifests, About UI reads runtime - never hardcoded); what travels with a bump - each attachment gets its own subsection under section 3 (`### Changelog`, `### Release notes`, `### Public docs`, `### Tags`) defining how that document is written. | 3 - version.md | default: no bump without explicit user request; pattern + sites marked pending from the manifests' own evidence |
| 25 | Task rituals - what should happen on EVERY piece of work unless the user says otherwise? Before: what to read/confirm first? While: standing checks (e.g. "before writing new code, search for an existing implementation")? After: gates to run (e.g. type-check [tsc --noEmit] or the stack's equivalent, lint, self-review against the golden rules)? Remember: the user's current prompt overrides the ritual for one task; a standing wish edits this section. Empty phase is fine - "none recorded". | 17 | default: no rituals beyond sections 2 and 5; stated as *default, unconfirmed* |
| 26 | How should the agent talk - and write? The register per surface (replying to the user, public docs, internal engineering docs): [concise], [explanatory], [verbose], [ponytail] - illustrative modes, mix or name your own. How do YOU talk (vocabulary, directness, terseness)? The agent answers at the user's level and frames questions in their words. Confirm the reflection rule: every document and artifact takes the register of its surface row. | 18 | default: concise, matching the user's observed register, written docs included; stated as *default, unconfirmed* |
| 27 | Which writable meanings live in MORE THAN ONE place? **(Proactively scan the repo first for duplicated version numbers across manifests, mirrored configs, or multi-language SDK folders and present them for confirmation.)** The same feature as [two SDKs in two languages], a [doc pair] that must keep telling one story, [config mirrors], the version declaration sites (when the number has more than one home, it is a sync block). For each: name the block and every home - exact location + line anchor + what that home must carry; the sync is in MEANING, not letters, and an edit to one side's meaning lands on every row in the same change. | 19, pointer from 3 | record "none found" only after the audit looked; a discovered duplicate with no block is a finding, not a note |
| 28 | What should EVERY agent in this project always do, in how it behaves and reports? The standing behavioral directives - offer the known shapes as examples, the user picks or invents: [declaration line] ("the last line of every response names the skills used"), [skill-usage floor] ("every user message gets at least one attempted skill before answering"), [mandatory pre-workflow] ("run /grill-me on the plan before any implementation"), or none ("no standing directives"). These bind subagents too - whatever is chosen travels into the 6.4 block's SKILLS clause. | 1 | record "none recorded yet" - never silence, never a default the user never chose |


## How to hand it to `inquire`

**One page per round** - not one page for everything, and not fifteen pings. Inside a round: group by section,
lead with the context the user needs to answer well ("your repo has both lockfiles; here is what each
implies"), order options with the recommendation first and the trade-off visible, and use branching where an
answer opens a follow-up (e.g. env strategy → which provider). Every question must be answerable by someone
who has not read this skill's references.

Then, after each round's answers: **restate the decisions back in a short list and wait for corrections**
before opening the next round. Silent incorporation loses the chance to catch a misread answer, and the file
is going to enforce it every session.

## Recording answers without smuggling assumptions

| Answer quality | How to write it |
|---|---|
| Decided | the rule, imperative, with the reason in a clause |
| Inferred from repo | the rule + `(inferred from <evidence>; correct me if wrong)` |
| Partially decided | write the decided half; list the rest as pending |
| "Do whatever you think" | pick, then mark **proposed**, and include it in the closing report so the user can veto |
| No answer | `pending - not assumed`, numbered |

The distinction between *decided*, *inferred*, and *proposed* is worth keeping in the file: it tells the next
agent how hard to push back, and it makes the next audit pass short - the pending list is the work queue.
