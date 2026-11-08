# Draft: Non-Redundant Additions to `agents-md` (What Is Actually Missing from `02-interview-guide.md`)

> **Audit against existing `references/00`–`09`:**
> Upon reviewing every reference file in `agents-md`, **`02-interview-guide.md` already has a 28-question bank covering Sections 1–19**, plus `01` (context), `04` (execution/env/debug), `05` (delegation), and `09` (privacy).
> Therefore, repeating what Sections 1–19 ask is **100% duplicate** of `02-interview-guide.md`.
>
> Below is **ONLY what is genuinely new and missing** from `agents-md` right now, structured into three focused parts:
> 1. **The Universal Research-Before-Asking Rule (For Every Section & Every Topic):** Before asking about *any* section or *any* file, the agent must research and map the professional dimensions, properties, and industry patterns of that topic in the context of the project's stack so its questions are deep, eye-opening, and tailored—never shallow or generic.
> 2. **General `AGENTS.md` Discovery Gaps:** How the agent discovers *unlisted* dimensions and deep edge-cases across the whole rulebook without relying only on the static 28 rows.
> 3. **The Dedicated `Section 3: How To` Dynamic Slate & Deep-Dive Engine (Lines 65–145):** Why `How To` is unique, how the agent proposes the N-topic slate (whether 3, 5, 6, or 8 topics—never hardcoded to 5) and asks the user before interviewing, and how it researches and generates deep questions for each chosen topic.

---

## Part 1: The Universal "Research the Domain Before Asking" Rule (Applies Everywhere)

A static question list always misses the nuances of how a real engineering domain works in practice. Therefore, **under every section of `AGENTS.md` and under every topic in `How To`**, the agent has a standing obligation **before** formulating its interview questions:

### The Pre-Question Domain Research Step
Whenever the agent prepares to ask about **any topic `<X>`** (whether `<X>` is versioning, branch promotion, debugging, database migrations, subagent delegation, privacy, review routines, or a custom domain topic):
1. **Research & Enumerate the Professional Properties of `<X>`:**
   - What are all the structural properties, professional patterns, edge cases, and failure modes of doing `<X>` at a high engineering standard in this stack?
   - *(Use repo inspection, framework docs, or quick web/doc research if the stack uses a specific tool like Turbo, Nx, Changesets, Expo, Prisma, Unity VCS, etc.).*
2. **Contrast the Viable Models (So the User Sees Real Options, Not Blank Questions):**
   - Never ask a bare *"How do you want to do `<X>`?"*
   - Instead, surface the real architectural models for `<X>` (with their trade-offs in this repo) so the user's horizons are expanded and they can pick or combine the exact properties they want.
3. **Probe Edge Cases, Rollback/Fallback, and Automation Boundaries:**
   - For every topic `<X>`, think beyond the happy path: *What happens when `<X>` fails, needs a rollback/fallback, crosses multiple modules, or is touched by a subagent?*

---

## Part 2: What Is Missing for `AGENTS.md` as a Whole (General Rulebook Discovery)

Currently, `02-interview-guide.md` gives 28 fixed questions, and `SKILL.md` Step 1 checks a fixed list of bash commands. What is missing is **how the agent discovers project-specific questions that aren't in the static bank**:

### 1. The Pre-Round Slate Confirmation (For the Whole `AGENTS.md` Interview)
Before starting the 5 interview rounds in `02-interview-guide.md`, the agent should not blindly fire preset questions. After Step 1 reconnaissance, it presents a **1-screen Discovery Summary**:
- **Already answered by the repo (Skipped):** e.g., package manager, VCS, existing docs root, detected branches.
- **Standard sections needing decisions:** Which of the 19 sections have unresolved choices.
- **Repo-specific anomalies/gaps spotted:** Conflicts or unique traits found in the repo (e.g., multiple lockfiles, monorepo packages with mixed versions, concurrent agent markers, custom codegen steps) that need a decision.
- **Ask the user upfront:** *"Here are the core areas I need to ask about based on your repo, plus [X] project-specific areas I spotted. Do you want to cover all of them, skip any, or add a specific concern before Round 1?"*

### 2. Deepening Specific Sections Where `02-interview-guide.md` Is Currently Thin
*(Applying the Research-Before-Asking rule to the sections that need broader horizons)*

- **Section 2 (Mandatory Context) — Researching All Context Dimensions:**
  - *Research prompt for the agent:* Inspect the repo to see every axis along which code, config, or docs split—not just `Version` and `Channel`, but **Target Platform** (`mobile`/`web`/`desktop`), **Deployment Mode** (`cloud`/`self-hosted`), **Tenancy/Region**, or **Online/Offline-first**—and ask which dimensions exist and how each is recognized on disk.
- **Section 4 (Design & Prototypes) — Researching Spec Formats & Fidelity Contracts:**
  - *Research prompt for the agent:* Check what design/spec artifacts exist (HTML prototypes, Figma, Storybook, OpenAPI) and ask about the **professional fidelity level**: strict pixel-parity convergence, structural/behavioral parity, or directional inspiration—plus how responsive/state variants (`?loading`, `?error`) are represented.
- **Section 6 (Agents / Delegation) — Researching Concurrency & State Isolation:**
  - *Research prompt for the agent:* Analyze where parallel subagents would collide in this repo (shared lockfiles, barrel `index.ts` exports, migration folders, codegen outputs) and ask how write-isolation, worktree/branch slicing, and failed-worker recovery should work professionally.
- **Section 12 (Version Control) — Researching the VCS's Professional Workflow:**
  - *Research prompt for the agent:* Research the exact VCS in use (Git worktrees, stacked PRs, commit-hook tooling, or Perforce/Plastic streams/shelves) to ask informed questions about commit atomicity, parked-work safety, and branch protection.
- **Section 14 (Golden Rules) — Proposing Structural Mechanisms from Repo Evidence:**
  - *Research prompt for the agent:* Instead of asking *"What are your golden rules?"* into a vacuum, inspect existing linters, schemas, architectural boundaries, and recurring git-log bug fixes, then **research and propose 2–4 high-leverage Golden Rules with concrete enforcement mechanisms** (compile-time, boot-time fail-fast, or CI gate) for the user to choose from.
- **Section 15 (Review) — Researching Domain-Specific Audit Passes:**
  - *Research prompt for the agent:* Beyond `Docs` and `DB`, research what high-value audit passes fit this project's domain (e.g., `API/SDK breaking-change audit`, `UI accessibility/RTL/CLS audit`, `Security/authz boundary audit`, `Concurrency/memory leak audit`) and propose them as optional named review tasks.
- **Section 19 (Sync Blocks) — Proactive Multi-Home Discovery:**
  - *Research prompt for the agent:* Actively scan the repo for duplicated truths (version numbers across manifests, mirrored configs, multi-language SDK implementations, client/server shared types without codegen) and present the discovered list to the user to confirm as Sync Blocks.

---

## Part 3: Dedicated Mechanism for `Section 3: How To` (The Dynamic N-Topic Router)

### Why `Section 3 (How To)` Is Unique in `AGENTS.md`
Every other section in `AGENTS.md` has a fixed single subject (Section 7 is always Privacy, Section 12 is always VCS, Section 18 is always Voice).
**Section 3 (`How To`) is the only open-ended, polymorphic section in the rulebook:**
- It routes **task classes -> procedural & policy docs** (or holds them inline).
- The 5 topics currently mentioned in `SKILL.md` (`development`, `debugging`, `execution`, `environment`, `version`) are **common starting candidates, NOT a fixed 5-item limit**.
- Depending on the project, Section 3 might hold **3 topics, 5 topics, 6 topics, or 10 topics**.

### Step A: The `How To` Topic-Slate Gate (Discover, Propose, and Ask Before Interviewing)
Before asking detailed procedural questions for Section 3, the agent must run this gate:

1. **Evaluate the 5 common topics against the repo:** Check which of `[development, debugging, execution, environment, version]` actually apply.
2. **Research & think critically about a 6th, 7th, or Nth missing topic:** Based on the repo's stack and domain, ask: *"What recurring engineering procedure or policy in this specific project will an agent get wrong if it isn't a `How To` topic?"*
   - *Examples of 6th+ topics:* Database migrations & rollback policy, Codegen / protobuf / OpenAPI sync, Multi-package / SDK lockstep parity, Asset / shader pipeline, Offline sync / conflict resolution, Localization / RTL rules, Release publishing & signing.
3. **Ask the user to confirm the `How To` slate first:**
   > *"For Section 3 (`How To`), here are the core topics `[e.g., 1. Development, 2. Debugging, 3. Execution, 4. Environment, 5. Version]`, plus `[6. <Repo-Specific Topic>, ...]` that your project seems to need.*
   > *1. Do you want to keep these topics, drop any of them, or add another topic?*
   > *2. Should their rules live as separate files (e.g. `rules/<topic>.md`) or inline inside `AGENTS.md`?"*

### Step B: Deep-Dive Question Generator & Research Prompt for Each Confirmed `How To` Topic
Once the user confirms the exact list of `N` topics for Section 3, the agent **researches the professional anatomy of each confirmed topic** and asks deep, structured questions:

#### 1. If `Version / Releases` is in the slate:
- **Agent Research Mandate:** Before asking, inspect all manifests/packages in the repo and consider the full spectrum of professional release engineering (monorepo lockstep vs. independent versioning, prerelease channels, hotfix backports, automated changelogs, binary/store build numbers).
- **Key Angles to Probe (Beyond `02` Q24):**
  - **Multi-Package / SDK Topology:** Lockstep/Unified SDK (e.g., Expo style where `SDK 58` means `expo-ui@58.x`, `expo-camera@58.x` all release and align together) vs. Independent per-package evolution vs. Core lockstep + independent satellites (with peer-dependency compatibility rules).
  - **Fallback / Hotfix / Deprecation Policy:** How are hotfixes patched onto older releases, how are breaking changes deprecated before removal, and how is a bad release rolled back?
  - *(Plus Q24's spec citation, deterministic bump rules & authority, dual-track public vs. internal build numbers, declaration sites -> Section 19 sync block, and release attachments).*

#### 2. If `Development / Branch Flow` is in the slate:
- **Agent Research Mandate:** Inspect `git branch -a`, `git log --graph`, and CI workflows (`.github/workflows`, etc.), and think through professional trunk-based, GitFlow, or release-train models.
- **Key Angles to Probe (Beyond `02` Q3):**
  - **Operational Meaning per Branch:** What each branch (`main`, `canary`, `develop`, `release/*`) actually governs (directory tree, build flags, CI pipeline, deployment environment).
  - **Landing, Promotion & Rollback Mechanics:** Branch naming (`agent/<slug>`), protected branches, merge strategy (squash vs. merge commit vs. rebase), promotion gates, and how a broken merge on a shared track is reverted or hotfixed.

#### 3. If `Debugging & Verification` is in the slate:
- **Agent Research Mandate:** Inspect the project's layers (UI, API, DB, background workers, native bridge) and test/observability tools to understand how a senior engineer diagnoses bugs in this exact stack without leaving dirty state.
- **Key Angles to Probe (Beyond `02` Q10 & `04`):**
  - **Single Playbook vs. Layer Folder Split:** Should debugging stay one file (`rules/debugging.md`) or split by layer (`rules/debugging/ui.md`, `rules/debugging/db.md`, `rules/debugging/workers.md`)?
  - **Observability, Reproduction & State Safety:** How to capture deterministic repros (learning tests, fixtures, state snapshots), read vs. mutate boundaries per environment, visual/device verification proof, and mandatory scratch cleanup.

#### 4. If `Execution & Tooling` is in the slate:
- **Agent Research Mandate:** Inspect scripts, task runners (`turbo`, `nx`, `make`, `just`), OS/shell quirks, and long-running daemon/watcher commands to identify every way an automated agent can hang, corrupt lockfiles, or burn time.
- **Key Angles to Probe:** Shell pitfalls and the exact failures they prevent, non-interactive flags, background process/port management, single package-manager enforcement, and fast targeted verification vs. heavy full-suite builds.

#### 5. If `Environment & Configuration` is in the slate:
- **Agent Research Mandate:** Inspect how configuration flows from secret stores / templates into build-time and runtime across local, test, staging, and prod environments.
- **Key Angles to Probe:** Typed boot-time validation schema (fail-fast, zero hardcoded fallbacks), build-time generation, secret-provider integration (`1Password`, `Doppler`, `Vault`), safe local overrides, and the exact multi-step route to register a new variable without touching `.env` directly.

#### 6. For ANY 6th, 7th, or Custom Topic Confirmed by the User (`<custom-topic>.md`):
- **Agent Research Mandate:** Whenever a custom topic is added to `How To` (e.g., `migrations`, `sdk-parity`, `codegen`, `offline-sync`, `shaders`, `billing-ledger`), the agent must **first research what a production-grade standard for `<custom-topic>` requires in this tech stack**—identifying its core properties, invariants, failure modes, and safety mechanisms—and then generate **3 to 5 deep questions** across these 4 axes:
  1. **Architecture & Topology:** How is `<custom-topic>` structured across the repo (single source of truth, module boundaries, lockstep vs. independent parts)?
  2. **Standard Procedure & Safety/Fallback:** What is the exact professional sequence to make a change, and how are rollbacks, migrations, or fallbacks handled safely?
  3. **Hard Prohibitions & Authority:** What must an agent *never* edit or run by hand, and which actions require user approval?
  4. **Verification & Sync Ripple:** What automated check proves `<custom-topic>` is healthy, and which other files/docs/sync-blocks must update in the same commit?

---

## Fix Note Spotted During Dedup Audit
While checking `02-interview-guide.md` against `SKILL.md`:
- `SKILL.md` uses **19 sections** (Sections 1–19).
- `02-interview-guide.md` (lines 41–49 and column `Feeds` in lines 59–86) and `03-audit-and-merge.md` (line 10) still reference old section numbers (**up to 22 / 23**, e.g. feeding sections `18, 20, 21, 22`).
- When we merge this draft into `agents-md`, we should also align those section numbers in `02` and `03` to match the canonical 1–19 numbering in `SKILL.md`!
