# Agent Skills Catalog

This repository contains a comprehensive collection of modular Agent Skills. Each skill provides specialized domain instructions, operational workflows, patterns, and best practices for agents.

Total skills available: **44**

## Quick Index

- [backend-db-debugging](./backend-db-debugging/SKILL.md) — Universal workflows, patterns, and templates for debugging backend services, databases, schema drift, migrations, enviro...
- [dig-binary](./dig-binary/SKILL.md) — Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracin...
- [blockiya](./blockiya/SKILL.md) — Enforce and apply the Blockiya architectural pattern for UI construction across component frameworks. Use when designing...
- [check-violations](./check-violations/SKILL.md) — Universal, language-agnostic agent skill to audit codebases, architectures, contracts, and visual/data invariants for ru...
- [chekr](./chekr/SKILL.md) — >- Run and remediate SNDUK Chekr architectural checks (@chekr/cli v0.3.2). Use when fixing check-violations, writing cus...
- [code](./code/SKILL.md) — Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates...
- [contribute-agents](./contribute-agents/SKILL.md) — Coordinate multiple AI subagents that collaboratively work on a task, critique each other's reasoning, and converge on a...
- [cross-platform-refactor](./cross-platform-refactor/SKILL.md) — Framework for auditing and refactoring ANY multi-platform codebase (mobile/desktop/web, any language/framework — MAUI, R...
- [design-mockup](./design-mockup/SKILL.md) — Build static HTML/CSS mockups of app/website screens as standalone, frameless files sized for a viewport (desktop/tablet...
- [display-to-user](./display-to-user/SKILL.md) — Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "l...
- [docs-refactor](./docs-refactor/SKILL.md) — Reorganize a messy set of Markdown/text documentation into a clean, one-concern-per-file structure with a per-directory ...
- [document-db-attach-chain](./document-db-attach-chain/SKILL.md) — Batched, immutable, order-guarded cross-collection reads for document databases (RxDB, PouchDB, Dexie/IndexedDB, MongoDB...
- [explain](./explain/SKILL.md) — Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-...
- [gitter](./gitter/SKILL.md) — Structures git workflow practices. Use when making any code change, committing, branching, resolving conflicts, splittin...
- [how-to-do](./how-to-do/SKILL.md) — Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are do...
- [idk](./idk/SKILL.md) — Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't ...
- [investigate](./investigate/SKILL.md) — Investigate local files, codebases, datasets, and external Agent Skills. Use for high-precision searches across heterogeneous formats, diagnosing unfamiliar architectures, inspecting...
- [like-a-pro](./like-a-pro/SKILL.md) — Root meta-skill orchestrator that reproduces production-grade engineering standards and conventions across applications....
- [mine](./mine/SKILL.md) — Runs a deep, budgeted, multi-source research dig to understand not just what a class of thing looks like, but WHY — the ...
- [no-framework](./no-framework/SKILL.md) — > Build Single Page Applications using NoF (No Frameworks) — a lightweight architecture defaulting to VanJS (~1KB, fine-...
- [audit-deps](./audit-deps/SKILL.md) — Audit and cleanup of project dependencies in a monorepo. Use when identifying unused libraries, removing redundancy, or ...
- [persona](./persona/SKILL.md) — > Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full beha...
- [planner](./planner/SKILL.md) — Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifi...
- [polyglot](./polyglot/SKILL.md) — Teaches AI agents how to design and author universal, general, and language-agnostic agent skills, and how to write bala...
- [pvc-fy](./pvc-fy/SKILL.md) — Apply PVC (Page-View-Component) role-based UI construction architecture for web apps across any component framework. Use...
- [scrape](./scrape/SKILL.md) — Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all...
- [scraper-optimizer](./scraper-optimizer/SKILL.md) — Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory...
- [search-deeply](./search-deeply/SKILL.md) — Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems ...
- [senior-refactor](./senior-refactor/SKILL.md) — Universal multi-platform refactoring skill to decouple codebases across TypeScript/React Native, Go, Rust, Flutter, and ...
- [subagent](./subagent/SKILL.md) — Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized...
- [summarize](./summarize/SKILL.md) — Use this skill whenever the user wants to shorten content without losing its meaning — summarize, condense, distill, rec...
- [take-a-breath](./take-a-breath/SKILL.md) — Force a deliberate pause before implementing. Stop the urge to code from scratch, calm the overwhelmed engineering impul...
- [technical-comparisons](./technical-comparisons/SKILL.md) — Write professional, well-reasoned comparisons between two or more technologies, tools, libraries, frameworks, products, ...
- [tray-inspection](./tray-inspection/SKILL.md) — Comprehensive workflow and Win32 inspection procedures for Windows system tray items, including listing active tray icon...
- [treasure-findings](./treasure-findings/SKILL.md) — Orchestrates blind multi-agent orthogonal discovery where N subagents (N >= 2) explore any task, codebase, research topi...
- [type-up](./type-up/SKILL.md) — >- Converts plain primitive types (string, number, boolean, etc.) into a professional typing system with semantic aliase...
- [unit-agent](./unit-agent/SKILL.md) — Command-line Junie interface for running code tasks. Use this skill to orchestrate Junie subtasks via CLI, especially wh...
- [up-agents](./up-agents/SKILL.md) — >- Launch staggered parallel worker subagents plus a delayed reviewer agent. Use when the user says up-agents, up agents...
- [using-agent-skills](./using-agent-skills/SKILL.md) — Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the ...
- [visual-enhancer](./visual-enhancer/SKILL.md) — Audits any code that produces a visual/rendered output — web components (HTML/React/Vue/Svelte/CSS), design mockups, Sto...
- [visual-parity-testing](./visual-parity-testing/SKILL.md) — Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually ren...
- [viz-planning](./viz-planning/SKILL.md) — Use this skill when planning, designing, or architecting a data visualization system, dashboard, chart component, report...
- [yo-nerdy](./yo-nerdy/SKILL.md) — > Use whenever a user wants to deeply study, dissect, reverse-engineer, or fully specify every detail of ONE specific pa...

---

## Skills Details

### 1. [backend-db-debugging](./backend-db-debugging/SKILL.md)

- **Directory:** `backend-db-debugging`
- **Title:** Universal Backend & Database Debugging
- **Description:** Universal workflows, patterns, and templates for debugging backend services, databases, schema drift, migrations, environment loading, and module/package path resolution in ephemeral scratch environments.

**Overview & Usage:**
A project-agnostic, production-grade guide for inspecting database schemas, validating backend service layers, resolving workspace/monorepo module paths, dynamically discovering environment variables, and verifying database migrations safely in ephemeral scratch environments.

---

### 2. [dig-binary](./dig-binary/SKILL.md)

- **Directory:** `dig-binary`
- **Title:** Universal Software Reverse Engineering & Black-Box Inspection
- **Description:** Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracing, network protocols, native binaries (PE, ELF, Mach-O), bytecode (JVM, Dalvik, Python, .NET), archives (ZIP, JAR, APK, TAR, ASAR), and local data stores. Use when source code is missing, obfuscated, or partial and internal models, APIs, hidden behaviors, or error causes must be uncovered.

**Overview & Usage:**
A comprehensive methodology and toolkit for reverse engineering modern software systems when source code is absent, incomplete, or obfuscated. It covers static artifact dissection (web bundles, native binaries, bytecode, archives), dynamic runtime tracing (process arguments, environment variables, I/O monitoring), network protocol reconstruction (REST, GraphQL, Protobuf/gRPC, WebSockets), and data storage analysis (SQLite, LevelDB, serialization models).

---

### 3. [blockiya](./blockiya/SKILL.md)

- **Directory:** `blockiya`
- **Title:** Blockiya Pattern Skill (Polyglot)
- **Description:** Enforce and apply the Blockiya architectural pattern for UI construction across component frameworks. Use when designing, reviewing, refactoring, or implementing orchestrators, features, pages, views, or project structure that must follow Blockiya rules — zero visual concerns in orchestrators, derive-before-pass, intents-only-upward, stereotypes, adapters, Strict utilities, growth signals, UML notation, or recommended feature-slice layout. Works for React, Vue, Svelte, Solid, and similar. Triggers include blockiya, Blockiya pattern, orchestrator block, strict blockiya, blockiya-core, derive before pass, fire intents and stop, zero styling blockiya, Atomic stereotype, Compound stereotype, behavioral primitive, adapter wrapper, UML notation, Vue Blockiya, framework-agnostic Blockiya.

**Overview & Usage:**
Apply the Blockiya architectural pattern rigorously across component frameworks (React, Vue Composition API, Svelte, Solid, Angular signals, etc.).

---

### 4. [check-violations](./check-violations/SKILL.md)

- **Directory:** `check-violations`
- **Title:** check-violations — Universal Invariant & Architectural Violation Auditing
- **Description:** Universal, language-agnostic agent skill to audit codebases, architectures, contracts, and visual/data invariants for rule violations using fast scriptable checkers (regex, lightweight rules, scriptable Python/JS/C#), reserving AST only when strictly necessary.

**Overview & Usage:**
Systematically audit, detect, and remediate violations of architectural invariants, coding contracts, visual fidelities, and data schemas across any technology stack. This skill abstracts inspection mechanisms—whether static analysis, runtime verification, or visual/structural diffing—into a universal, language-agnostic workflow.

---

### 5. [chekr](./chekr/SKILL.md)

- **Directory:** `chekr`
- **Title:** Chekr — SNDUK architectural checks
- **Description:** >- Run and remediate SNDUK Chekr architectural checks (@chekr/cli v0.3.2). Use when fixing check-violations, writing custom .chekr/checks, using @chekr-ignore blocks, pruning cache, auditing violations.json, or parallel per-package remediation.

**Overview & Usage:**
Custom static analysis for this monorepo. Rules live in `.chekr/checks/`; config in `chekr.config.js`. CLI: **@chekr/cli v0.3.2**.

---

### 6. [code](./code/SKILL.md)

- **Directory:** `code`
- **Title:** Code — brief, toolchain, docs-grounded, then write
- **Description:** Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates, in order: (1) a coding brief naming the app/module being coded and which stack-agnostic concerns it touches (interfaces, styling, a11y, navigation, forms, persistence, platform, concurrency, errors, build); (2) root inspection to detect the real toolchain (lockfile decides - bun.lock->bun, package-lock.json->npm, Cargo.lock->cargo, go.mod->go, uv/poetry.lock->python; binding project rules outrank inference); (3) targeted grounding of ONLY the touched concerns in CURRENT official docs for each ecosystem, via the `scrape` skill when available (cache + grep over re-fetching; WebFetch fallback), with trade-off questions to the user instead of silent picks. Use before scaffolding/editing source in any stack (TypeScript frameworks, Rust, Python, Go, ...) - it exists to stop coding from model memory that went stale. Chain with project standards skills when present.

**Overview & Usage:**
Never let a code edit start from memory. Every ecosystem drifts - Rust editions and trait APIs churn, Python frameworks deprecate whole patterns, JS component APIs get renamed between majors, Go stdlib gains context-aware variants - so a confident-looking API from training time is a latent bug. Three gates precede the first edit to source. The invariant: **grounding beats guessing, in any language.**

---

### 7. [contribute-agents](./contribute-agents/SKILL.md)

- **Directory:** `contribute-agents`
- **Title:** Contribute Agents
- **Description:** Coordinate multiple AI subagents that collaboratively work on a task, critique each other's reasoning, and converge on a documented conclusion. Use when the user wants two or more agents to discuss, debate, review, or jointly solve a problem (e.g. "have two agents argue about X", "run a panel of reviewers on this design", "make agents challenge each other's evidence") and wants a supervised discussion with an explicit termination condition and a final report.

**Overview & Usage:**
Orchestrate a supervised, multi-agent collaboration: several subagents work on the same task from different personas, communicate through a shared workspace, critically review each other instead of agreeing by default, and stop only when an explicit termination condition is met. You (the calling agent) act as the **Observer/Orchestrator** — you set up the collaboration, delegate the subagents, monitor them, and produce the final report. You never inject your own reasoning into their discussion.

---

### 8. [cross-platform-refactor](./cross-platform-refactor/SKILL.md)

- **Directory:** `cross-platform-refactor`
- **Title:** Cross-Platform Refactor
- **Description:** Framework for auditing and refactoring ANY multi-platform codebase (mobile/desktop/web, any language/framework — MAUI, React Native, Flutter, Kotlin Multiplatform, Swift, Electron, etc.) into one that is both fully cross-platform (no shared file secretly depends on one platform) and fully abstracted (no duplicated UI/interaction logic). Use when porting an app to new platforms, auditing for platform-leaking code, eliminating scattered 'if platform == X' conditionals, standardizing platform value/capability resolution, splitting desktop-vs-mobile UI layouts wrongly sharing one tree, or turning duplicated UI behavior into reusable components. Trigger even without the words 'cross-platform'/'abstraction' — e.g. 'make this work on mobile too', 'this only works on Windows', 'get rid of all the platform ifs', 'the mobile version looks wrong', 'why do we have three different confirm dialogs'.

**Overview & Usage:**
A framework for taking any multi-platform codebase from "leaky and duplicated" to "cleanly separated and reusable" — without a behavior rewrite, and without being tied to any single language or UI framework.

---

### 9. [design-mockup](./design-mockup/SKILL.md)

- **Directory:** `design-mockup`
- **Title:** Design Mockup
- **Description:** Build static HTML/CSS mockups of app/website screens as standalone, frameless files sized for a viewport (desktop/tablet/mobile). Use for "mockup", "wireframe", or seeing what a screen "would look like" as static HTML. Every interactive element (sheets, drawers, modals, dropdowns, tabs, toggles, accordions, steppers, toasts) must be drivable via URL query params so a state can be linked/screenshotted without clicking through. Also covers an opt-in command — auditing an already-built HTML file for dead controls (kebab/ellipsis menus, chevrons, bells) that look clickable but do nothing, wiring each to the expected feedback (dropdown, toast, panel, inline toggle). Trigger that for "this does nothing when clicked", "add feedback to interactive elements", "make this feel real", "audit for dead clicks", "wire up the kebab menu", or "opt in" feedback. Not for real interactive apps or React components (use frontend-design).

**Overview & Usage:**
A static HTML mockup of a UI — a screen, a short flow, or one component in context. It looks real and can be screenshotted in any state, but has no backend and no real logic: every dynamic-looking bit of state is faked with placeholder content or exposed as a URL query parameter.

---

### 10. [display-to-user](./display-to-user/SKILL.md)

- **Directory:** `display-to-user`
- **Description:** Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "let me see", or "give me a link to see" what you've done to their project — the current state of files, or just the changes so far. Also trigger this if the user asks for a way to visually browse the project tree, preview a README or HTML file you produced, or share a live view of the repo with someone else. This spins up a local web viewer (file tree + git status + file preview) and tunnels it with ngrok so the user gets a real clickable URL back, rather than you pasting file contents into chat.

**Overview & Usage:**
Give the user (or someone they forward the link to) a live, browsable view of the project you're working in: a file tree, git change highlighting, and rendered previews of Markdown/HTML files — reachable from a public URL via ngrok, since you're running remotely and the user can't just open `localhost` themselves.

---

### 11. [docs-refactor](./docs-refactor/SKILL.md)

- **Directory:** `docs-refactor`
- **Title:** Docs Refactor
- **Description:** Reorganize a messy set of Markdown/text documentation into a clean, one-concern-per-file structure with a per-directory README acting as a local map. Use this when the user explicitly asks to refactor, reorganize, restructure, clean up, or de-duplicate a documentation set — phrases like "refactor these docs," "these files are a mess, can you reorganize them," "split this doc up," "our docs keep repeating the same stuff," or "give this folder a proper structure." Do not trigger on requests to just edit or fix content in a single existing file, or to write a brand-new doc from scratch — this skill is specifically for restructuring an existing multi-file (or single bloated-file) documentation set.

**Overview & Usage:**
A skill for taking documentation that has grown organically — usually AI-generated, usually across many sessions — and turning it into a set of files that each own exactly one concern, with a README at every directory level acting as a mini-map for whoever (human or AI) lands there next.

---

### 12. [document-db-attach-chain](./document-db-attach-chain/SKILL.md)

- **Directory:** `document-db-attach-chain`
- **Title:** Document DB Attach Chain
- **Description:** Batched, immutable, order-guarded cross-collection reads for document databases (RxDB, PouchDB, Dexie/IndexedDB, MongoDB) via an engine-agnostic attachOne/attachMany/attachGroup chain (attachTo(...).one().many().group()) built on a small per-engine FetchAdapter. Use whenever writing query code that combines documents from two or more collections/tables on RxDB, PouchDB, Dexie, or MongoDB — e.g. attaching a post's author, a user's related records, or "posts with comments and comment authors" style reads. Also use when asked for a "join" helper, an "ODM-style" or "Drizzle-like" relation utility for these engines, or when attachOne/attachMany/attachGroup/attachTo are named directly. On MongoDB, check "Choosing a strategy" first — this pattern is the fallback there, not the default (prefer $lookup). Do NOT use for one schema-declared relationship read repeatedly on an engine with native population (e.g. RxDB's .populate()) — see "When NOT to use this.

**Overview & Usage:**
No document database engine has a universal answer to cross-collection reads: some (RxDB, PouchDB, Dexie) have no server-side query planner spanning collections at all, so "join" only ever means "fetch, then fetch again, then merge in application code." Others (MongoDB) have a real native join (`$lookup`). This skill teaches one engine-agnostic pattern — batched, immutable, order-guarded — for the engines that need it, and is explicit about when an engine has something better.

---

### 13. [explain](./explain/SKILL.md)

- **Directory:** `explain`
- **Title:** Explain
- **Description:** Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-day (a security flaw nobody has fixed yet)". Use this whenever the user asks you to explain, simplify, clarify, break down, or "explain like I'm new to this", or says a previous answer was too technical, confusing, full of jargon, or hard to follow. Also use it proactively whenever your own answer is about to use a specialized or industry-specific term (security, finance, medicine, law, engineering, programming, etc.) and the user hasn't signaled expert familiarity with that field.

**Overview & Usage:**
The gap between an expert explanation and a clear one is almost never about the ideas — it's about the words. A correct, complete answer can still fail the reader if it's built out of terms they have to stop and look up. This skill's job is to close that gap: say the true thing, but say it so a smart, motivated person with no background in the topic can follow it on the first read.

---

### 14. [gitter](./gitter/SKILL.md)

- **Directory:** `gitter`
- **Title:** Gitter
- **Description:** Structures git workflow practices. Use when making any code change, committing, branching, resolving conflicts, splitting uncommitted work into atomic commits, opening or reviewing a PR, pushing, organizing parallel streams, cutting a release, choosing a semantic version bump, tagging, or writing a changelog.

**Overview & Usage:**
Git is the safety net. Treat commits as save points, branches as sandboxes, and history as documentation. With agents generating code at high speed, disciplined version control keeps changes manageable, reviewable, and reversible.

---

### 15. [how-to-do](./how-to-do/SKILL.md)

- **Directory:** `how-to-do`
- **Description:** Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are done the same correct way every time across sessions, agents, and models — instead of silently missing a step. ALWAYS check for a .htd/ folder at the repo root before starting ANY coding task, even if not mentioned, and consult it if present. Trigger this — don't wait to be asked — whenever the user says "add", "create", "change", "update", "refactor", "migrate", "wire up", or "integrate" something in a real codebase, including simple-sounding tasks like "add a table" (exactly what this exists for — never skip as too simple). Also trigger on any mention of "how-to-do", ".htd", or standardizing a workflow. After any nontrivial multi-file change in a repo with (or needing) .htd/, use this proactively to record a new procedure, patch an existing one, or confirm no update is needed — skipping this defeats the skill's purpose.

**Overview & Usage:**
A persistent record, local to each repo, of *how* to correctly perform recurring classes of change — so the procedure survives across sessions, across different agents, and across different models, instead of being re-derived (and silently getting a step wrong) every time.

---

### 16. [idk](./idk/SKILL.md)

- **Directory:** `idk`
- **Description:** Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't know", "not sure what I need", "I don't know how to explain it", "I can't put it into words", or similar explicit expressions of uncertainty about their own intent. This is NOT a general clarifying-questions skill — it only triggers on that explicit signal, not on every vague or underspecified request. Once triggered, it guides the user from a fuzzy feeling toward a clear, named intent through a calm, jargon-free conversation, optionally looking around the project's code and docs for clues, and ends with a plain-language review that maps what the user said onto the standard technical term for it.

**Overview & Usage:**
The user knows *something* is off, or wants *something* to change, or has a feeling about the project — but they can't articulate it in technical terms, or they're not sure what they actually want yet. They say "idk" not because they're lazy, but because turning a vague feeling into a concrete, actionable request is genuinely hard, especially across a language or expertise gap. Forcing them to pick from a menu of technical options right away just adds friction on top of the uncertainty.

---

### 17. [investigate](./investigate/SKILL.md)

- **Directory:** `investigate`
- **Title:** Investigation & Search
- **Description:** Investigate local files, codebases, datasets, and external Agent Skills. Use for high-precision searches across heterogeneous formats, diagnosing unfamiliar architectures, inspecting or comparing Skills from SkillsMP, GitHub, and other public sources, temporarily using or remixing external Skills, and synthesizing evidence into structured reports. Does not install external Skills unless explicitly requested.

**Overview & Usage:**
A comprehensive methodology and executable toolkit for investigating complex local filesystems, datasets, and diverse data formats, as well as inspecting, comparing, temporarily using, and remixing public Agent Skills. It emphasizes robust evidence gathering, high-throughput search, source integrity, progressive disclosure, and safe handling of untrusted external content.

---

### 19. [like-a-pro](./like-a-pro/SKILL.md)

- **Directory:** `like-a-pro`
- **Title:** Like-a-Pro Meta-Skill
- **Description:** Root meta-skill orchestrator that reproduces production-grade engineering standards and conventions across applications. Guides the complete lifecycle from Idea -> Details-Up -> App Boundary Confirmation -> Child Skills (language-conventional, sql-conventional, errors-handling, ui-rules, system-creator).

**Overview & Usage:**
The **like-a-pro** meta-skill is a modular orchestration engine designed to reproduce production-grade technical standards, schemas, error architectures, and system documentation across any software project. It bridges the journey from initial idea to robust, consistent implementation standards across 3 canonical phases.

---

### 20. [mine](./mine/SKILL.md)

- **Directory:** `mine`
- **Title:** /mine
- **Description:** Runs a deep, budgeted, multi-source research dig to understand not just what a class of thing looks like, but WHY — the decisions, tradeoffs, and constraints behind it, both explicit (stated) and implicit (only inferable). Task-based: sources and technique adapt to what's asked — real GitHub codebases for "top enterprise projects," visual/design references (screens, dashboards, UI patterns) for "50 dashboard designs," or other source types the task points at. Ends by writing one free-form distilled document of everything learned — never a templated report or per-source recap. Trigger this whenever the user says "/mine", asks to "mine" a topic, or asks for a deep dive, deep research, or comprehensive understanding across multiple top/best real-world examples — especially with a budget like "top 20," "for an hour," or "as deep as you can go." Always propose a verified source plan and get explicit user approval before mining starts — never start digging without an approved plan first.

**Overview & Usage:**
> Given a topic, plan a set of real, distinct sources (codebases, design > references, or whatever the task points at); dig into each to > understand not just what's there but *why*; end with one distilled > document of everything learned.

---

### 21. [no-framework](./no-framework/SKILL.md)

- **Directory:** `no-framework`
- **Title:** NoF: No Frameworks Architecture
- **Description:** > Build Single Page Applications using NoF (No Frameworks) — a lightweight architecture defaulting to VanJS (~1KB, fine-grained reactive UI) and Navigo (~4KB, client-side routing), no React/Vue/Angular. Use this whenever building or scaffolding a small-to-medium SPA that should stay framework-free. Requires verifying current library versions and API compatibility (VanJS, Navigo, and any other library used) before writing code, since pinned versions in this skill's own examples can go stale. Any library that works as plain vanilla JS without a framework runtime is fair game within this architecture, not just VanJS/Navigo — including CSS tooling like Less/Sass when a project's needs justify it. Covers project scaffolding, state/derive patterns, routing, component architecture, rendering conventions, debugging/profiling, and shipping to production (no-bundler and Vite build paths). Not the right fit for very large multi-page enterprise apps, large teams, or apps needing complex animation libraries — see the "when to use" section for the actual line.

**Overview & Usage:**
Simplicity over complexity, performance by default, full control over the codebase. If something can be done with less code while staying just as clear, do it that way — don't reach for abstraction NoF doesn't need.

---

### 22. [audit-deps](./audit-deps/SKILL.md)

- **Directory:** `audit-deps`
- **Title:** Package Audit and Cleanup
- **Description:** Audit and cleanup of project dependencies in a monorepo. Use when identifying unused libraries, removing redundancy, or optimizing package sizes across workspaces.

**Overview & Usage:**
In a large monorepo, dependencies can quickly become redundant, outdated, or unused. This skill provides a systematic workflow for auditing `package.json` files across all workspaces (apps and packages), identifying "ghost" dependencies, and safely removing them without breaking the build or runtime.

---

### 23. [persona](./persona/SKILL.md)

- **Directory:** `persona`
- **Title:** Persona & Context Construction
- **Description:** > Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full behavioral specification of how the agent thinks, investigates, judges quality, and communicates. Use this whenever building, prompting, or orchestrating a subagent (security reviewer, database engineer, testing engineer, frontend engineer, DevOps/SRE, technical writer, code reviewer, or any other domain specialist) and a generic "you are a senior X" persona would be too shallow. Especially relevant for multi-agent orchestration systems (e.g. contribute-agents) that need distinct professional perspectives per role, and for any task asking to "give this agent a persona," "make this agent think like a senior X," or "construct context for a subagent." The method is role-agnostic — it applies identically whether the role is testing, security, database, frontend, or something else entirely.

**Overview & Usage:**
Build a persona that makes a subagent **reason and behave like an experienced practitioner**, not one that makes it *announce* expertise. The test at every step is: would this text change what the agent notices, how it investigates, and what it accepts as evidence — or is it decorative?

---

### 24. [planner](./planner/SKILL.md)

- **Directory:** `planner`
- **Title:** Planner
- **Description:** Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifies vague or slang-heavy language if needed, then generates structured hypotheses that surface explicit requirements plus professional reading-between-the-lines concerns, gathers local and web context, iterates with the user until hypotheses are approved, and finally produces a solid plan. Use in planning-mode or quest-mode, or whenever the user asks for a plan, architecture outline, implementation roadmap, or disciplined decomposition of a complex task. Triggers include planner, planning mode, quest mode, make a plan, rigorous plan, hypothesis-driven planning.

**Overview & Usage:**
Enforce a disciplined, hypothesis-driven, **universal** planning process. The skill is language-agnostic and technology-neutral (polyglot principles). It adapts to the current project and forces thorough coverage of both stated requirements and the professional concerns a senior engineer would notice between the lines.

---

### 25. [polyglot](./polyglot/SKILL.md)

- **Directory:** `polyglot`
- **Title:** Polyglot: Universal & Language-Agnostic Skill Design
- **Description:** Teaches AI agents how to design and author universal, general, and language-agnostic agent skills, and how to write balanced, representative polyglot code examples. Use when creating or refactoring agent skills, coding standards, templates, or architectural specifications.

**Overview & Usage:**
`polyglot` provides principles, workflows, and conventions to ensure that newly authored agent skills and architectural specifications never trap users into a single language, framework, database engine, or prescriptive convention.

---

### 26. [pvc-fy](./pvc-fy/SKILL.md)

- **Directory:** `pvc-fy`
- **Title:** PVC Architecture — Page, View, Component
- **Description:** Apply PVC (Page-View-Component) role-based UI construction architecture for web apps across any component framework. Use when designing, reviewing, refactoring, or scaffolding UI structure, pages, views, components, decorations, aligners, or UI elements. Works for React, Vue, Svelte, Solid, Angular, and similar. Triggers include PVC, Page View Component architecture, role-based UI, semantic UI composition, View vs Component distinction, project structure for UI, UI hierarchy rules, architectural classification of components, Vue PVC, React PVC, framework-agnostic UI architecture.

**Overview & Usage:**
Role-based UI construction model. Pages compose Views. Views compose purposeful Components + supporting Decorations/Aligners + nested Views. UI Elements are the primitive building blocks. Classification is by architectural role, not by framework component implementation.

---

### 27. [scrape](./scrape/SKILL.md)

- **Directory:** `scrape`
- **Title:** Scrape — full framework docs, locally
- **Description:** Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all guide pages + every API component page; capacitor/react/vue planned) plus `--auto` URL discovery for any Docusaurus-style docs site and explicit `--url` scraping, with a `--verify` mode that proves every page is reachable and server-rendered. Use whenever the agent needs authoritative external docs - e.g. Ionic component props/events/methods/CSS custom properties before building mobile UI, API reference lookups, or confirming doc URLs exist - instead of guessing from memory or fetching pages one by one.

**Overview & Usage:**
One script, `scripts/scrape.py` (Python 3, `requests` + `beautifulsoup4` only), that downloads complete documentation sets as Markdown and guarantees nothing silently: every failure mode (404, JS-rendered page, thin content) is reported.

---

### 28. [scraper-optimizer](./scraper-optimizer/SKILL.md)

- **Directory:** `scraper-optimizer`
- **Title:** Scraper Optimizer
- **Description:** Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory-bounded web scrapers and data ingestion pipelines across Python, Go, Node.js, Rust, C#, and Java.

**Overview & Usage:**
Design, profile, and optimize high-throughput web scrapers and stream pipelines that maintain a flat $O(\text{concurrency})$ memory footprint regardless of dataset volume ($O(N)$), preventing container OOM kills (Railway, Kubernetes, Fly.io).

---

### 29. [search-deeply](./search-deeply/SKILL.md)

- **Directory:** `search-deeply`
- **Title:** Search Deeply
- **Description:** Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems problems. Use when the user requests very deep research, production-grade architecture analysis, lifecycle design, formal state machines, ownership models, race-condition handling, resource pools, platform constraints, failure-mode analysis, anti-patterns, or any study that must go far beyond shallow answers. Triggers include deep research, architecture study, implementation-oriented, formal state machine, ownership analysis, failure modes, anti-patterns, decision matrix.

**Overview & Usage:**
Conduct rigorous, multi-pass technical research that yields a single recommended, implementable architecture rather than a catalog of options. Separate documented facts from patterns and recommendations. Prefer primary sources. Always produce formal state machines, clear ownership models, race-condition defenses, failure-mode tables, anti-pattern analysis, a decision matrix, and a progressive practice exercise.

---

### 30. [senior-refactor](./senior-refactor/SKILL.md)

- **Directory:** `senior-refactor`
- **Title:** Senior Refactor: Zero-Coupling & Universal Multi-Platform Architecture
- **Description:** Universal multi-platform refactoring skill to decouple codebases across TypeScript/React Native, Go, Rust, Flutter, and C#/.NET. Eliminates inline preprocessor directives (#if PLATFORM) and runtime OS switch sprawl, establishes 3-tier unit hierarchies (UNITS.md), and swaps view layouts across desktop and mobile. MUST BE USED whenever refactoring client code for cross-platform readiness, resolving platform coupling, splitting partial classes or build tags by OS family, or converting ad-hoc components into base/specialization units. Examples: "refactor this to be platform independent", "eliminate #if WINDOWS", "split into platform files", "extract base and specialization unit", "implement view barrel layout swapping".

**Overview & Usage:**
A comprehensive, language-agnostic skill for transforming tightly-coupled, platform-locked client codebases into clean, decoupled, multi-platform architectures without breaking existing functionality.

---

### 31. [subagent](./subagent/SKILL.md)

- **Directory:** `subagent`
- **Title:** Professional Subagent
- **Description:** Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structured brief with hierarchical Context, precise Goal, How, Autonomy Bounds, and Output Contract so the sub-agent stays focused, never decides, and returns full raw results instead of summaries. Also covers pre-delegation environment consistency checks (to prevent sub-agent drift), requirements for exhaustive slightest-detail reporting back to the main agent, and detecting/mitigating race conditions between concurrently running sub-agents (e.g. shared scripts or files). Triggers include sub-agent, subagent, delegate, spawn worker, professional brief, task handoff, isolated prompt, parallel agents, concurrent agents.

**Overview & Usage:**
Generate a complete, self-contained brief that a main agent can hand to a sub-agent. The brief enforces isolation, clear boundaries, full evidence return, and zero decision-making authority.

---

### 32. [summarize](./summarize/SKILL.md)

- **Directory:** `summarize`
- **Title:** Document Summarization
- **Description:** Use this skill whenever the user wants to shorten content without losing its meaning — summarize, condense, distill, recap, abridge, or extract key points from an article, report, transcript, thread, email chain, conversation, or document, including TL;DR, executive summary, abstract, digest, or brief requests. Trigger even on a bare \"summarize this\" with no further instruction, and when the user wants the shortest/most extreme version. Also trigger for conversation/Q&A summarization with role-specific instructions (\"keep my questions, summarize the agent's answers\") and for requests specifying a custom output structure (\"put questions on top under headers, answers below\") — this skill decides whether the request preserves the source's shape or needs a new one. Not for line-level copyediting/proofreading at the same length — see process-business-writing.

**Overview & Usage:**
Reduce a longer source into a shorter one **without losing the meaning the reader needs to walk away with.** This is not word-deletion — it is re-deriving the point from a position of having understood the whole, then rendering it in as few words as the requested mode allows.

---

### 33. [take-a-breath](./take-a-breath/SKILL.md)

- **Directory:** `take-a-breath`
- **Title:** Take a Breath
- **Description:** Force a deliberate pause before implementing. Stop the urge to code from scratch, calm the overwhelmed engineering impulse, and apply sober judgment about whether a mature, production-proven solution already exists. Use when the agent is about to write custom code for a common problem, when the user says take a breath, pause and evaluate, don't reinvent, prefer existing solutions, or when the task feels like it might already have a solid library, framework, platform feature, or established pattern. Triggers include take-a-breath, take a breath, pause and think, don't reinvent the wheel, prefer proven solutions, evaluate existing options.

**Overview & Usage:**
You are the stressed engineer who is about to write a lot of code because the problem feels urgent and solvable. Stop. Breathe. Look around.

---

### 34. [technical-comparisons](./technical-comparisons/SKILL.md)

- **Directory:** `technical-comparisons`
- **Title:** Technical Comparisons
- **Description:** Write professional, well-reasoned comparisons between two or more technologies, tools, libraries, frameworks, products, or services of any kind (programming/frontend tooling, databases, note-taking apps, cloud providers, hardware, SaaS products, etc.). Use this skill any time the user asks to compare, evaluate trade-offs between, or choose between named options — even if they just say "which is better" or "help me decide between X and Y." Enforces real differentiators only (not just what each side's own marketing highlights), "why it matters" reasoning for every claim, current/verified information via search, careful grading of benchmark/performance claims, and a neutral, use-case-driven recommendation instead of a false absolute winner.

**Overview & Usage:**
A skill for writing comparisons that engineers actually trust — the kind that gets referenced, not the kind that gets skimmed and closed. The core failure mode this skill exists to prevent: listing a feature as an "advantage" of A when B can achieve the same outcome a different way, and listing features without ever saying why they matter to the reader.

---

### 35. [tray-inspection](./tray-inspection/SKILL.md)

- **Directory:** `tray-inspection`
- **Title:** Windows System Tray Inspection and Diagnostics
- **Description:** Comprehensive workflow and Win32 inspection procedures for Windows system tray items, including listing active tray icons, reading explorer toolbar memory, extracting native HICON bitmaps/PNGs, capturing high-DPI tray snips, and diagnosing tray state or badging issues.

**Overview & Usage:**
Windows system tray icons are managed by Windows Explorer across two distinct toolbar controls (`Shell_TrayWnd` for visible taskbar items and `NotifyIconOverflowWindow` for overflow flyout items). Inspecting, listing, or extracting icons from these areas requires cross-process Win32 memory scanning, toolbar message interception (`TB_BUTTONCOUNT`, `TB_GETBUTTON`), or GDI screen capture.

---

### 36. [treasure-findings](./treasure-findings/SKILL.md)

- **Directory:** `treasure-findings`
- **Title:** treasure-findings — Blind Orthogonal Multi-Agent Discovery & Synthesis
- **Description:** Orchestrates blind multi-agent orthogonal discovery where N subagents (N >= 2) explore any task, codebase, research topic, or problem domain via distinct cognitive perspectives, methodologies, and advanced prompt engineering disciplines with zero peer knowledge, followed by master synthesis into an authoritative findings report.

**Overview & Usage:**
Maximize analytical yield, error detection, and strategic discovery by dispatching **N isolated subagents (N &ge; 2)** engineered with **mutually orthogonal cognitive lenses, distinct prompt engineering disciplines, and independent investigative methodologies**. Subagents operate in total isolation with zero knowledge of their peers, eliminating cognitive anchoring, shared bias, and collective blind spots. Upon completion, the master orchestrator cross-examines, triangulates, and fuses all discoveries into a single authoritative master findings document.

---

### 37. [type-up](./type-up/SKILL.md)

- **Directory:** `type-up`
- **Description:** >- Converts plain primitive types (string, number, boolean, etc.) into a professional typing system with semantic aliases, documentation, runtime validation, and tests. Use when the user asks for better types, semantic types, branded/NewType types, config typing, API contracts, PathLike-style aliases, schema validation, or professional typing for public surfaces.

**Overview & Usage:**
Turn **basic primitive fields** into a **documented, validated type system** that helps editors, authors, runtime safety, and CI — while remaining practical for consumers.

---

### 38. [unit-agent](./unit-agent/SKILL.md)

- **Directory:** `unit-agent`
- **Title:** Unit Agent (Junie CLI)
- **Description:** Command-line Junie interface for running code tasks. Use this skill to orchestrate Junie subtasks via CLI, especially when you need specific configurations like --plan, --brave, or custom project locations.

**Overview & Usage:**
Command-line Junie interface for running code tasks autonomously or interactively. Use this skill when you need to delegate a scoped task to Junie itself as a tool, or when the user describes a task that fits the "Junie as a CLI" pattern.

---

### 39. [up-agents](./up-agents/SKILL.md)

- **Directory:** `up-agents`
- **Title:** up-agents — Staggered Worker Pool + Reviewer
- **Description:** >- Launch staggered parallel worker subagents plus a delayed reviewer agent. Use when the user says up-agents, up agents, up-agents N + 1, spawn workers, worker pool with reviewer, or wants parallel implementation with a final QA pass.

**Overview & Usage:**
Orchestrate **N parallel worker subagents** with **staggered start delays**, then **1 reviewer subagent** that wakes last to build, test, and review.

---

### 40. [using-agent-skills](./using-agent-skills/SKILL.md)

- **Directory:** `using-agent-skills`
- **Title:** Using Agent Skills
- **Description:** Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.

**Overview & Usage:**
This repo keeps its skills in **`.cursor/skills/`**. Each skill is a directory with a `SKILL.md` (and optional `reference.md`, `references/`, `POWER.md`).

---

### 41. [visual-enhancer](./visual-enhancer/SKILL.md)

- **Directory:** `visual-enhancer`
- **Title:** Visual Enhancer
- **Description:** Audits any code that produces a visual/rendered output — web components (HTML/React/Vue/Svelte/CSS), design mockups, Storybook stories, CLI/TUI output (ink, blessed, yoga-layout, raw console output), or native UI layout code — and reports concrete, substantive visual/UX enhancements. Use this skill whenever the user invokes "/visual-enhance", asks to "enhance the visual", "improve the UI/UX", "review the design", "make this look better", "check for visual issues", or points at a screen/page/component/mockup/CLI output and asks what could look better — even if they don't use the words "visual enhancer" explicitly. Triggers on both general requests ("/visual-enhance" or "check the whole project") and targeted requests naming a specific file, component, folder, or page. Do NOT use for functional bug fixes, accessibility-only audits, or requests to build a new UI from scratch — this skill is for enhancing what already visually exists in code.

**Overview & Usage:**
Audits existing rendered/visual code and produces a written report of **substantive** visual/UX enhancements — never a redesign, never a list of cosmetic nitpicks. Output only, no code is modified by this skill; the user applies suggested fixes themselves.

---

### 42. [visual-parity-testing](./visual-parity-testing/SKILL.md)

- **Directory:** `visual-parity-testing`
- **Title:** Visual Parity Testing & Autonomous Convergence
- **Description:** Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually renders on a real device/emulator, for any UI framework. Covers the full pipeline (mockup + on-device capture, frame/chrome-noise normalization, similarity scoring, regional diagnosis) and an autonomous convergence loop that iterates capture→compare→diagnose→fix→rebuild without pausing for check-ins until threshold is met. Also covers: inventorying ItC (interact-to-change) components like dropdowns/drawers/modals and forcing their states via query params; dummy/placeholder mockup data needing fixtures so content mismatches don't masquerade as layout bugs; transition/animation ('smoothing') parity beyond static screenshots; and navigating past obstacle screens (splash/onboarding/permissions) without getting stuck. Use when the user wants pixel/visual parity with a design, an automated visual regression pipeline, or an agent that autonomously iterates toward a similarity score.

**Overview & Usage:**
A framework for measuring — and then autonomously closing — the gap between a design reference and what a real device actually renders. This is not a one-shot "take a screenshot and diff it" tool; it's built around a **loop an agent runs to convergence on its own**, the same way a human would iterate, but without needing to be prompted after every attempt.

---

### 43. [viz-planning](./viz-planning/SKILL.md)

- **Directory:** `viz-planning`
- **Title:** Viz Planning
- **Description:** Use this skill when planning, designing, or architecting a data visualization system, dashboard, chart component, reporting tool, or analytics app — anything built once and used repeatedly, or involving real complexity (unstable schemas, growing/streaming datasets, multiple sources, many categories, outliers, filtering or persisted state). Walks through data source stability, schema evolution, volume, semantics, chart selection, grouping/aggregation/outlier handling, filtering and state architecture, layout, and configuration precedence BEFORE any chart gets built, so the wrong visualization or a fragile pipeline doesn't get picked by default. Trigger even when the user just says "help me build a dashboard for X" or "I need to visualize this data" without naming any of these specifics — the point is surfacing considerations they haven't thought of yet. Do NOT use for one-off requests like "chart this CSV" or "plot Q3 revenue" against already-clean, already-understood data — just chart it directly.

**Overview & Usage:**
Picking a chart type is the last decision in data visualization, not the first. Before that: where the data comes from and how stable it is, what it means, how much of it there is, what question it's answering, what deserves focus, what should be grouped or hidden versus always discoverable, how state and configuration persist, and what happens when the data doesn't match expectations. Skipping these produces dashboards that break on the first schema change, pie charts with 40 unreadable slices, or filters that vanish on refresh.

---

### 44. [yo-nerdy](./yo-nerdy/SKILL.md)

- **Directory:** `yo-nerdy`
- **Description:** > Use whenever a user wants to deeply study, dissect, reverse-engineer, or fully specify every detail of ONE specific part, feature, flow, or subsystem of a larger system — e.g. a payment checkout flow, an auth/session flow, a search bar, a notification pipeline, a caching layer, an image-annotation/labeling scheme, a rate limiter. Produces an exhaustive breakdown of every micro-decision (triggering rules, edge cases, scoring/ranking logic, label/category granularity, i18n, caching tradeoffs, failure modes), grounded in whichever field actually governs the component (Information Retrieval, Distributed Systems, Security, Computer Vision, Control Theory, etc.), and actively asks the user how they want key tradeoffs resolved (throughput vs. precision, coarse vs. fine-grained categories) instead of guessing. Trigger even without "deep dive" or "spec" — "how exactly should X work" is a strong signal. Must REFUSE and ask for one bounded component when asked to analyze an entire system or several components at once.

**Overview & Usage:**
This skill produces the kind of document a senior engineer wishes existed before anyone started building a feature: every implicit micro-decision made explicit, every edge case named, every "what happens if..." answered or explicitly flagged for a human to decide — grounded in the real discipline that governs the problem, checked against how actual production systems handle it, and built around the *user's* preferences on the handful of decisions that are genuinely a matter of taste rather than engineering fact.

---
