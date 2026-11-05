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

## Rounds - the interview is delivered in waves, not one wall

Each round settles one small group of sections (2-5 questions). Present a round, collect its answers,
restate the decisions in a 3-6 line list, and only then open the next round. Rounds the repository already
answers are skipped with one line saying so.

| Round | Sections | Question numbers from the bank |
|---|---|---|
| **1 - What this project is, right now** | 1, 2, 3, 16 | 1, 2, 3, 4, 22, 28 |
| **2 - The toolchain as it actually is** | 5, 6, 7 | 7, 8, 9, 11 |
| **3 - What the project already has** | 2, 4, 12, 18, 22 | 5, 6, 19, 24, 27 |
| **4 - Agents working in this project** | 3, 8, 17, 20 | 10, 12, 13, 14, 15, 23, 25 |
| **5 - Trust and boundaries** | 9, 10, 11, 14, 15, 21 | 16, 17, 18, 20, 21, 26 |

Maintenance (15) and Facts (21) are not rounds: the first is the fixed duty, the second fixed text whose bullets only accumulate - neither needs an interview question, though the audit seeds Facts from evidence it already proved. Ask only for an owner or review cadence if the user
has an opinion. If the user stops early, the remaining rounds become numbered pending items - never defaults.

## Must ask - the decision bank

Ask only for the sections the repo left unresolved. Each row shows the rule it produces; the round table
above says which rows travel together.

| # | Question | Feeds | If unanswered |
|---|---|---|---|
| 1 | Which version is active now, and which must be ignored? | 2 | the file cannot fence scope; highest-cost omission |
| 2 | Which channels exist; do any rules differ per channel? How does the agent detect the channel? | 2, 3 | leave channel out of the table and say so |
| 3 | Where does new work land, and what may never be committed directly? Who approves promotion? | 3 | record the observed branch pattern as *inferred, unconfirmed* |
| 4 | Version format and increment duty; who may change the base version? | 3 - version.md (procedures route via 3) | pointer to the file holding it, no invented format |
| 5 | Is there a units index? Where? Reuse-or-extend duty? Who updates it when a subagent adds a unit? | 2 - the units duties ride section 2's registry row | `pending - no units reference yet` |
| 6 | Where do design/prototype references live, and which are in scope? | 4 | omit section 4 with one line saying the project has none |
| 7 | Which shell must be avoided and why; chaining allowed? Scratch script location and cleanup duty? | 5 | ask; this is environment-specific knowledge only the user has |
| 8 | One package manager, confirmed? | 6 | use the inferred one, marked *inferred from lockfile* |
| 9 | Environment strategy: type-safe schema? build-time generation from a central file? runtime secret store? paths and commands | 6 | `pending` + the prohibition that is always safe: do not edit `.env` directly |
| 10 | Debugging: inspect data permitted? modify permitted, in which environment? how to verify visual/GUI behavior? | 3 - the debugging how-to doc | permit read-only inspection locally, require a question for anything mutating |
| 11 | What must happen before the first edit in a session? | 8 | derive from sections 2, 4, 6 as a startup checklist |
| 12 | Subagent naming scheme; report location and filename pattern; is reusing a role name allowed to overwrite? | 8 | propose a default and mark it *proposed* |
| 13 | What may a subagent decide alone vs return undecided? | 8 | default: reversible local edits in scope = decide; anything crossing files/branches/destructive = return undecided |
| 14 | Fan-out: max depths and max total workers; what happens when a leaf fails | 8 | cap at 2 depths and report the cap as a default |
| 15 | Any mandatory-skill rule for this project? | 1, 8 | omit; do not invent an obligation to use skills the project may not have |
| 16 | What stays private from version control and other agents' sight - skill folders, plans, run records? What do those tools output (the cascade - hidden tool means hidden outputs)? Which binaries are hidden, and where does their install note live instead? If any of that was already tracked, may it be cleared from the cache after asking? | 9 | state "no privacy restrictions recorded"; never guess what the user wants hidden |
| 17 | Is anything ever installed globally on purpose - a shared CLI, a system package? Everything else stays project-local (dependencies, toolchains, interpreters, environments) | 10 | default: local-first, no exceptions |
| 18 | Which environment actions need permission - external binary installs, external processes (emulators, daemons), existing-database writes, credentials, machine config? Ask per session (safe default) or fixed per action? | 11 | default: ask per session; when a limit blocks work, say what cannot be done and ask |
| 19 | Which project skills does the team rely on, and what must an agent read or do before using each (required document, scratch rule, format)? One row per skill | 12 | omit; skills add their own rows when adopted |
| 20 | Which VCS does this project use ([Git], [Unity VCS/Plastic], [Perforce], [Mercurial], [SVN]) - concepts are for the interview; once answered, the written section takes the tool's name as its heading (## Git) and speaks its vocabulary directly, no neutral ceremony. Version control: which operations may an agent do freely (read-only? commits?), which need asking (push, PR, shared-branch merge), which are never without explicit order (rebase/amend of pushed work, `reset --hard`, `clean`, force-push)? Is parking unfinished work allowed (git stash / [shelve] / equivalent) - and with which message pattern so entries are identifiable in a shared worktree, or what replaces it? Whose name do agent-made commits carry - human sole author, a `Co-authored-by:` trailer (exact name and address), or an agent identity? (`commit` and `branch` ask the authorship question only because this answer is missing.) | 14 | default: read-only + local commits allowed, push asks, rewrites/clean/reset never; stash forbidden (use worktrees or WIP commits); keep configured identity, no trailer - all marked *default, unconfirmed* |
| 21 | How do you want to be asked? **Exact** - I present named implementation specifics and you choose ("which channel cipher: X, Y, Z"), you own internals. **Broad** - I ask intent ("do you want E2EE?"), you answer, and I choose the internals best for the project. **Both by weight** - intent stays Broad, and you name the few decisions you want Exact (which get written here). Then the fixed duty regardless of mode: weight-bearing questions (irreversible, costly, security, cross-module) are ALWAYS asked while you are in the loop, trivia is never asked; consequential options route through `caution`; before any anonymous run, your critical questions get answered first. Where do lasting decisions get written? Default: one file per decision in `<docs>/decisions/` with Date + Commit + App-Version anchors (never a combined decisions.md), the run ledger beside them at `states.md` - the ask-or-decide call itself recorded too. | 15 | default: Broad by weight with the always-ask mandate, the pre-anonymous rule and the one-file-per-decision convention; stated as *default, unconfirmed* |
| 22 | Where is the docs root? (MUST-ASK when the folder is missing or undeclared - there is no project without docs; the path is declared in section 2 and every pointer hangs from it, including `<docs>/decisions/`.) And: what does this project treat as **golden rules** - the list that never bends whatever the task or deadline? Each rule must be phrased so a violation is recognizable while writing it ("No hardcoding - runtime-changeable values always live in the project's data source, never in source; where exactly - [tables], [config], [flags], [CMS] - is the project's own choice"). | 2, 15 | never invent the docs path and never skip the declaration; golden rules default: none recorded, said so |
| 25 | Task rituals - what should happen on EVERY piece of work unless the user says otherwise? Before: what to read/confirm first? While: standing checks (e.g. "before writing new code, search for an existing implementation")? After: gates to run (e.g. type-check [tsc --noEmit] or the stack's equivalent, lint, self-review against the golden rules)? Remember: the user's current prompt overrides the ritual for one task; a standing wish edits this section. Empty phase is fine - "none recorded". | 20 | default: no rituals beyond sections 2 and 9; stated as *default, unconfirmed* |
| 24 | Version policy, in full: which pattern - [SemVer - semver.org], [CalVer - calver.org], [SDK-style major-per-release], [base + dev tag] are illustrative, the project may mix or own its scheme; **cite the chosen spec, never restate or invent its rules**; what bumps which component (every fix? milestones? release cuts only) - a WRITTEN rule, because letting the agent guess the bump kind probabilistically is the failure this question replaces; who may bump ([explicit request] / [agent by rule] / [agent asks]); one version or two audiences (public vs internal/build code) and the mapping; every declaration site where the number is written (project file, platform manifests, About UI reads runtime - never hardcoded); what travels with a bump - each attachment gets its own subsection under section 3 (### Changelog with its format decision, e.g. Keep a Changelog; ### Release notes; ### Public docs; ### Tags) defining how that document is written. | 18 | default: no bump without explicit user request; pattern + sites marked pending from the manifests' own evidence |
| 28 | What should EVERY agent in this project always do, in how it behaves and reports? The standing behavioral directives - offer the known shapes as examples, the user picks or invents: [declaration line] ("the last line of every response names the skills used"), [skill-usage floor] ("every user message gets at least one attempted skill before answering"), [mandatory pre-workflow] ("run /grill-me on the plan before any implementation"), or none ("no standing directives"). These bind subagents too - whatever is chosen travels into the 10.4 block's SKILLS clause. | 1 | record "none recorded yet" - never silence, never a default the user never chose |
| 26 | How should the agent talk - and write? The register: [concise] (answer first, reasoning on request), [explanatory] (trade-offs shown while deciding), [verbose] (teaching walkthroughs), [ponytail] (the lazy-senior-dev minimum: the shortest statement that still proves the point, no ceremony) - illustrative modes, mix or name your own. How do YOU talk (vocabulary, directness, terseness)? The agent answers at the user's level and frames questions in their words. Confirm the reflection rule: the same voice governs every document the agent writes (reports, decision records, changelog and release prose) - one voice spoken and written. | 21 | default: concise, matching the user's observed register, written docs included; stated as *default, unconfirmed* |
| 27 | Which writable meanings live in MORE THAN ONE place? The same feature as [two SDKs in two languages], a [doc pair] that must keep telling one story, [config mirrors], the version declaration sites (this feeds 20's pointer: when the number has more than one home, it is a sync block, not a Version-section list). For each: name the block and every home - exact location + line anchor + what that home must carry; the sync is in MEANING, not letters (homes phrase per idiom), and an edit to one side's meaning lands on every row in the same change. | 22, pointer from 18 | record "none found" only after the audit looked; a discovered duplicate with no block is a finding, not a note |
| 23 | What named review routines does the project run? Every review starts with the same first pass - hunt violations of this rulebook (golden rules first) in code AND docs; below it, each task: name, what to read, what counts as a violation. Offer the common two as seeds, not quotas: Docs (stale passages, unlinked docs nothing points to, docs over 500 lines split into a folder of the same name with index.md) and [DB] (learn all tables, hunt hardcoded/mocked data - only where a database exists; otherwise the project's own truth-store task or none). | 17 | record only the always-first pass; named tasks stay pending |


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
