# Agent Skills Catalog

This repository contains a comprehensive collection of modular Agent Skills. Each skill provides specialized domain instructions, operational workflows, patterns, and best practices for agents.

Total active skills: **125** — 28 standalone at the repository root and the rest organized under 16 topic groups. 26 archived skills are listed at the end.

## Skill types

This catalog uses three composition types. **A skill's entrypoint is its own `SKILL.md`; a folder name or its depth in the repository does not make it a skill.** Type describes what a skill contains, not where it is stored or which slash command an agent exposes.

| Type | Root entrypoint | Functional children | Independent skill boundaries |
|---|---|---|---|
| **Meta-Skill** | `<meta-skill>/SKILL.md` | Sub-skills, each with its own `SKILL.md` | The parent and each sub-skill have separate entrypoints |
| **Battery-Skill** | `<battery-skill>/SKILL.md` | Internal modes/modules without their own `SKILL.md` | Only the battery is an independent skill |
| **Skill** | `<skill>/SKILL.md` | Supporting material, not a collection of sub-skills or internal methods | Only the skill itself |

### Meta-Skill: compose independent sub-skills

The parent routes work to sub-skills. Each functional child carries its own skill instructions and metadata, so it can be identified and used as a skill in its own right. Its own composition can again be a Skill, Battery-Skill, or Meta-Skill. Separate slash-command exposure depends on the host agent; it is not the classification test.

```text
meta-skill/
  SKILL.md
  first/
    SKILL.md
    references/
  second/
    SKILL.md
    scripts/
```

Example: [`animation`](./animation/SKILL.md) contains the `ascii`, `life`, and `svg` sub-skills. Inventory and lint include each actual child entrypoint, with its nearest owning skill recorded as its parent.

### Battery-Skill: one skill, several internal methods

The root owns the shared rules and dispatches to internal methods. Those methods are parts of the battery, not separately installable skills: a `method.md`, `README.md`, or other internal guide does not substitute for a child `SKILL.md`.

```text
battery-skill/
  SKILL.md
  first-mode/
    method.md
    references/
  second-mode/
    method.md
    assets/
```

Example: [`design`](./design/SKILL.md) contains `design-md`, `playfile`, `prototype`, and `calibrate`; [`pages`](./Groups/Design/pages/SKILL.md) contains `main`, `secondary`, and `complementary`. Their internal methods do not receive independent catalog rows, versions, or installation records. Change tracking belongs to the containing skill.

### Skill: one method with supporting material

A normal skill can have many files and folders. References, examples, scripts, assets, and templates support its method; their presence alone does not make it a battery. Several commands or a routing table alone also do not establish separate module boundaries.

```text
skill/
  SKILL.md
  references/
  examples/
  scripts/
  assets/
```

Example: [`techstack`](./techstack/SKILL.md) uses references, examples, and templates without making those directories independent skills or internal modes.

### Groups, support folders, and mixed structures

- **Groups are organization, not a fourth skill type.** `Groups/Design/` has no entrypoint of its own. Moving a skill into a group does not change its type or make it a sub-skill.
- **Support names are contextual.** `references/method.md` is not automatically a battery mode. Conversely, [`assets`](./Groups/Design/assets/SKILL.md) and [`resources`](./Groups/Design/resources/SKILL.md) are real skills because those directories have their own entrypoints.
- **Structure is evidence, not semantic proof.** The manager infers composition from actual entrypoints and Markdown-backed module directories outside conventional support folders. An unusually named reference collection can resemble a module; inspect the reported child/module paths rather than treating a label as proof that the content is independently usable.
- **Mixed composition needs an explicit correction.** A parent with both independent sub-skills and internal module branches does not cleanly satisfy either composite form. The manager preserves the real sub-skill entrypoints, reports the parent as Meta-Skill, and emits a composition warning. It does not add or delete `SKILL.md` files automatically.
- **Links are installation details, not types.** A symlink, junction, or hard copy can contain any of the three types. A broken link or a database record alone does not prove a live skill exists.

### Inspecting the types

```bash
python manager.py report --sort type
python manager.py report animation design pages techstack --json
python manager.py find design prototype
python manager.py lint --strict --verbose
python -m unittest test_manager_structure
```

`report` includes nested independent skills, type, parent, and composition evidence (`children`, `modules`, and `issues` in JSON). Internal modules are not independent report rows. Per-skill file counts include descendants, while the summary counts unique files to avoid counting a meta-child's files twice. `find` uses the same classification across the registry, agent folders, and recorded `--into` installations. `lint` checks actual skill entrypoints and flags mixed structures; `--strict` makes findings fail the command.

## Quick Index

### Agent

- [amongus](./Groups/Agent/amongus/SKILL.md) — Tiny awareness skill: the project has another agent working in it besides you. Edits you did not make, files that changed since you last read them, a hunks that…
- [bequeath](./Groups/Agent/Bequest/bequeath/SKILL.md) — End-of-session asset harvesting: review the whole conversation, propose what is worth keeping, and turn approved work into tested, reusable assets in the projec…
- [context](./Groups/Agent/Session/context/SKILL.md) — Project-context reconstruction — build a reliable mental model of a project from all available artifacts (docs, source, config, git history with a 5-commit defa…
- [flush](./Groups/Agent/Session/flush/SKILL.md) — Agent continuity capture, manual — persist working state before session end, environment change, loss, milestone, handoff, or when the conversation grew too lar…
- [heir](./Groups/Agent/Bequest/heir/SKILL.md) — Acknowledge the legacy of previous agents before rebuilding anything. At the start of a task, if the project has a `bequest/` directory, open its INDEX, decide…
- [how-to-do](./Groups/Agent/how-to-do/SKILL.md) — Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are done the same correct way every time acros…
- [mistakes](./Groups/Agent/mistakes/SKILL.md) — A personal, growing log of mistakes already made or observed, with where each one shows up and how to fix it. Use when the user says mistakes, check my mistakes…
- [persona](./Groups/Agent/persona/SKILL.md) — Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full behavioral specification of how the agent thin…
- [recall](./Groups/Agent/recall/SKILL.md) — Recall, in two modes, on one rule: report only what you can actually find. Mode A answers "do you remember when I said X?", "did I mention Y?", or /recall <topi…
- [subagent](./Groups/Agent/subagent/SKILL.md) — Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structu…

### Audit

- [anti-slop](./Groups/Audit/anti-slop/SKILL.md) — Review UI and product-design quality for a page, selected routes, an application, or a repository. Use when asked to find, explain, prioritize, or guide correct…
- [antipattern](./Groups/Audit/antipattern/SKILL.md) — Investigates a software project, researches the engineering anti-patterns that matter for its stack, gathers evidence from code, architecture, business rules an…
- [crosscheck](./Groups/Audit/crosscheck/SKILL.md) — Cross-check a task, codebase, or research question by blind orthogonal discovery: dispatch N isolated subagents (N >= 2), each engineered with a distinct cognit…
- [exmaine](./Groups/Audit/exmaine/SKILL.md) — Examine a project from the inside out, starting at AGENTS.md: follow every doc path it declares (design docs, units, glossary, commitments, decisions, skill sou…
- [impurities](./Groups/Audit/impurities/SKILL.md) — Project-wide defect discovery and remediation through self-designed iterations — never a fixed checklist. Assess the actual project (runtime, resources, depende…
- [ladder](./Groups/Audit/ladder/SKILL.md) — Find, design and harden ladders: ordered decision structures where rungs (a condition paired with an outcome) are evaluated in one order until something wins. B…
- [packages](./Groups/Audit/packages/SKILL.md) — One run, two jobs over a project's dependencies, any ecosystem (JS/TS, Python, Go, Rust, JVM, .NET…) and any project shape. Job 1 — redundancy audit: classifies…
- [please-verify](./Groups/Audit/please-verify/SKILL.md) — Broad verification of a project or delivered body of work - not just the last step - answering one question: is the work actually complete and sufficiently veri…
- [pvc](./Groups/Audit/pvc/SKILL.md) — Role-based UI construction (Page → View → Component, plus Decoration, Aligner, UI Element, Rendition) — framework-agnostic architecture for building or auditing…
- [scraper-optimizer](./Groups/Audit/scraper-optimizer/SKILL.md) — Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory-bounded web scrapers and data ingestion…
- [seo](./Groups/Audit/seo/SKILL.md) — Universal 100-point on-page SEO playbook for ANY web stack (Next.js, SvelteKit, Nuxt, Blazor, ASP.NET, Rails, Laravel, Django, Dioxus, Leptos, Astro, Hugo, stat…
- [states](./Groups/Audit/states/SKILL.md) — Classify any fact an app consults as a State or a Condition, decide who owns it, and settle whether a consumer may read it or must create it. Use when deciding…
- [treat](./Groups/Audit/treat/SKILL.md) — Evaluate how adopted tools and libraries want to be used and recommend structure or adaptations that respect their model - concepts, patterns, constraints. Revi…

### Code

- [code-review](./Groups/Code/code-review/SKILL.md) — Review the changes since a fixed point (commit, branch, tag, merge-base) on two separated axes run as parallel subagents and aggregated side by side, never cros…
- [dbug](./Groups/Code/dbug/SKILL.md) — Debug any problem in any codebase, any language — bug, error, exception, crash, 500, timeout, wrong/missing/duplicate data, regression, "worked before", "works…
- [fix](./Groups/Code/fix/SKILL.md) — After root-cause diagnosis with dbug, resolve the problem and improve the relevant implementation so the same or similar problems become easier to identify, und…
- [gh](./Groups/Code/gh/SKILL.md) — All GitHub CLI/Actions work in one router: fix failing CI/PR checks (gh pr checks, gh run view --log-failed, bundled inspect_pr_checks.py; classify workflow-fil…
- [implement](./Groups/Code/implement/SKILL.md) — Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates, in order: (1) a coding brief naming th…
- [planner](./Groups/Code/planner/SKILL.md) — Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifies vague or slang-heavy language if need…
- [refactor](./Groups/Code/refactor/SKILL.md) — Surgical code refactoring that improves structure and maintainability without changing behavior. Use when the user says refactor this, clean up this code, fix c…
- [test](./Groups/Code/test/SKILL.md) — General testing principles and ethics for any test the agent writes or reviews — unit, integration, contract, e2e, property, invariant, regression, or pipeline.…
- [update](./Groups/Code/update/SKILL.md) — Change something everywhere it lives, leaving no stale copy behind. Use for ANY change request: reword copy or docs; rename a term, identifier, file, route, or…

### Crawl

- [capture](./Groups/Crawl/capture/SKILL.md) — Capture visuals, files, data, or design from designs, sites, pages, and apps, invoked as `/capture designs|screenshots|siteshots|page|website|dom|design|images`…
- [educate](./Groups/Crawl/Scraping/educate/SKILL.md) — Turns documentation retrieved by the Scrape skill into a pruned, project-relevant, indexed, version-aware knowledge base so the agent never has to re-read or re…
- [fahlwy](./Groups/Crawl/fahlwy/SKILL.md) — Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts, PDF books, brand lo…
- [scrape](./Groups/Crawl/Scraping/scrape/SKILL.md) — Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all guide pages + every API component page;…

### Decision

- [contract](./Groups/Decision/contract/SKILL.md) — Documents who owns what across architectural layers as tiny, precise contract files in <docs>/contract/: one responsibility per file, ownership either OoU (exac…
- [decide](./Groups/Decision/decide/SKILL.md) — Helps the user choose between candidates (software in any language or platform, databases, tools, cloud services, products, approaches) by researching them fair…
- [dtb](./Groups/Decision/dtb/SKILL.md) — Do the Best: decide HOW the work is done while the user keeps owning WHAT is to be built. Use when the user hands over a goal, prototype or reference without ev…
- [iwts](./Groups/Decision/iwts/SKILL.md) — Autonomous ownership mode — "I Want to Sleep". Invoke when the user says iwts, "I want to sleep", "take over", "finish it while I'm away", or delegates the proj…
- [thebest](./Groups/Decision/thebest/SKILL.md) — Evidence-based option choice for THIS project: gather proof, hand the user a verdict - "this is likely best for us, based on these tests and research" - and sto…

### Design

- [assets](./Groups/Design/assets/SKILL.md) — Pipeline contract for a project's imagery: plan the bill of materials, generate the masters, conform them into delivery files. Routes the three steps to the ski…
- [bleed](./Groups/Design/bleed/SKILL.md) — Convert a web UI between layout registers - full-bleed page, framed cards, or hybrid - and fix the "document inside an app" smell where a page wraps itself in a…
- [collection](./Groups/Design/collection/SKILL.md) — Method for a project's generated imagery: dissect a reference or page set into a bill of materials (BOM), fix the style canon once, write the prompts, plan gene…
- [denoise](./Groups/Design/denoise/SKILL.md) — Transforms crowded, noisy, visually overwhelming UIs into calm, readable, professional interfaces that are easier to use, not just nicer to look at, at one of t…
- [diverge](./Groups/Design/diverge/SKILL.md) — Previews genuinely different design directions for an existing UI before committing a whole project or batch of pages to one of them. Two commands: /diverge tas…
- [pages](./Groups/Design/pages/SKILL.md) — A product's complete page universe: one skill, three modes, ONE artifact. /pages main plans the core-screen inventory, pruning a 492-row 30-discipline candidate…
- [parity](./Groups/Design/parity/SKILL.md) — Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually renders on a real device/emulator, for any…
- [resources](./Groups/Design/resources/SKILL.md) — Resource files for any platform: images, icons, fonts, audio, video, documents, color values - the files, not the systems that serve them. Fourteen tools: recol…
- [scss](./Groups/Design/Style/scss/SKILL.md) — SCSS/Sassy CSS best practices and coding guidelines for maintainable, scalable stylesheets
- [stateful](./Groups/Design/stateful/SKILL.md) — Derive every state a user-visible screen can enter, then implement the approved ones — pending, empty, stale, partial; provider down, degraded, throttled, maint…
- [styleup](./Groups/Design/Style/styleup/SKILL.md) — Turns an existing project's styling into a maintainable, professional system on any stack: inventories every hardcoded or duplicated style, works inside the sty…
- [styling](./Groups/Design/Style/styling/SKILL.md) — Platform-neutral rules for writing NEW styling on any stack (HTML/Web, Blazor, MAUI, Qt): per-module stylesheets, no monolith; role-named tokens as single sourc…

### Favor

- [design-taste-frontend](./Groups/Favor/design-taste-frontend/SKILL.md) — tasteskill 2.5.1, the anti-slop frontend skill. Builds professional company websites at the level of figma.com and x.ai: plain copy in a voice of its own, one s…
- [taste](./Groups/Favor/taste/SKILL.md) — Smart design router skill that clarifies user intent to route to either ui-taste (apps/dashboards/iOS) or design-taste-frontend (landing pages/showcases).
- [ui-taste](./Groups/Favor/ui-taste/SKILL.md) — Give your coding agent better UI taste. Build and polish web and iOS interfaces with Uizze's anti-ui-slop playbooks and optional real-product references. Use fo…

### Files

- [document](./Groups/Files/document/SKILL.md) — Markdown documents: five jobs, the default entry whenever a task produces, restructures, shortens or rewords a document - self-invoked, not only when /document…
- [pdf](./Groups/Files/pdf/SKILL.md) — Use this skill whenever the user wants to do anything with PDF files, in either of its two modes. READ mode: extract text from a PDF into .txt with scripts/pdf_…
- [postmortem](./Groups/Files/postmortem/SKILL.md) — Blameless, self-contained incident documents: postmortem, incident report, RCA, bug write-up, "what went wrong". Modes: file (default) or folder. FILE: one Mark…
- [summarize](./Groups/Files/summarize/SKILL.md) — Use this skill whenever the user wants to shorten content without losing its meaning — summarize, condense, distill, recap, abridge, or extract key points from…

### Generalize

- [polyglot](./Groups/Generalize/polyglot/SKILL.md) — Teaches AI agents how to design and author universal, general, and language-agnostic agent skills, and how to write balanced, representative polyglot code examp…
- [revoke](./Groups/Generalize/revoke/SKILL.md) — Sanitise an artifact by revoking what ties it to a specific project, person, customer or deployment: the substance survives, the identity does not. Use when a r…

### Git

- [branch](./Groups/Git/branch/SKILL.md) — Plans, names, and safely runs Git branches, including repositories several agents share. Three situations differ: alone; beside other agent processes (a second…
- [commit](./Groups/Git/commit/SKILL.md) — Professional git commits, in two modes. GUIDE (default, writes nothing): detect the repo's incumbent convention from its history, split work into atomic units,…
- [diffs](./Groups/Git/diffs/SKILL.md) — Read git diffs like evidence, not text: triage huge diffs and search diff history. Establishes the right baseline (A..B vs A...B, worktree/staged/HEAD, merge ba…

### Prospecting

- [mine](./Groups/Prospecting/mine/SKILL.md) — Runs a deep, budgeted, multi-source dig to understand not just what a class of thing looks like but WHY - and, when asked to decide, runs the options through a…
- [smelt](./Groups/Prospecting/smelt/SKILL.md) — Turns a completed mine run — or any research corpus of checkpoints, distillations, plans, and witness notes — into a durable, evidence-linked knowledge base ano…

### Search

- [dig-binary](./Groups/Search/dig-binary/SKILL.md) — Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracing, network protocols, native binaries (P…
- [investigate](./Groups/Search/investigate/SKILL.md) — Investigate local files, codebases, datasets, and external Agent Skills. Use for high-precision searches across heterogeneous formats, diagnosing unfamiliar arc…
- [search-deeply](./Groups/Search/search-deeply/SKILL.md) — Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems problems. Use when the user requests ver…

### Special

- [display-to-user](./Groups/Special/display-to-user/SKILL.md) — Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "let me see", or "give me a link to see" w…
- [tray-inspection](./Groups/Special/tray-inspection/SKILL.md) — Comprehensive workflow and Win32 inspection procedures for Windows system tray items, including listing active tray icons, reading explorer toolbar memory, extr…
- [viz-planning](./Groups/Special/viz-planning/SKILL.md) — Use this skill when planning, designing, or architecting a data visualization system, dashboard, chart component, reporting tool, or analytics app — anything bu…

### Talk

- [chat](./Groups/Talk/chat/SKILL.md) — Relaxed conversation mode the user starts and ends. The user wants to talk something through, not get work done: the agent listens, answers in short plain sente…
- [explain](./Groups/Talk/explain/SKILL.md) — Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-day (a security flaw nobody has fixed ye…
- [grill-me](./Groups/Talk/grill-me/SKILL.md) — Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
- [honest](./Groups/Talk/honest/SKILL.md) — Answers honestly instead of agreeably, and says what it understood before it judges anything. Use when the user asks 'can this really work', 'will this work', '…
- [idk](./Groups/Talk/idk/SKILL.md) — Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't know", "not sure what I need", "I don't…
- [inquire](./Groups/Talk/inquire/SKILL.md) — Build a rich, interactive question page (HTML) when the agent must get several important decisions from the user before or during work. Use it when there are 2…
- [judge](./Groups/Talk/judge/SKILL.md) — Acts as a fair, unbiased judge comparing two or more candidates (libraries, frameworks, tools, architectural approaches, vendors, design options, or any compara…
- [tldr](./Groups/Talk/tldr/SKILL.md) — Answer in the shortest honest form instead of the usual full explanation — a word, a phrase, or one short sentence, with no preamble, hedging, or recap of what…
- [walkthrough](./Groups/Talk/walkthrough/SKILL.md) — Slow, step-by-step mode for working through a big or confusing problem (a project, a decision, a messy situation) at a steady, unhurried pace instead of jumping…

### Viber

- [adapt](./Groups/Viber/adapt/SKILL.md) — Grows a project's own Viber version. Viber has fixed foundations, but no two projects walk the same path. When the journey needs a capability nothing covers, ad…
- [agents-md](./Groups/Viber/agents-md/SKILL.md) — Creates/audits AGENTS.md - agent rulebook: obligations+references not docs, rules/ per-topic referenced is the recommendation, inline stays valid; one owner per…
- [architecture](./Groups/Viber/architecture/SKILL.md) — Orchestrates and drafts an application's complete technical architecture documentation suite across its core pillars (language conventions, error handling, visu…
  - [accessibility](./Groups/Viber/architecture/accessibility/SKILL.md) — Orchestrates and authors an application's Accessibility Architecture specification into <docs>/architecture/accessibility-architecture.md. Moves beyond complian…
  - [display](./Groups/Viber/architecture/display/SKILL.md) — Orchestrates and authors an application's Display Architecture specification into <docs>/architecture/display-architecture.md — how values and text are EXPRESSE…
  - [plugin](./Groups/Viber/architecture/plugin/SKILL.md) — Authors an application's plugin and settings architecture as one extensibility system. Settings and plugins are the same family: a closed host exposes a small e…
- [commitments-md](./Groups/Viber/commitments-md/SKILL.md) — Creates and maintains COMMITMENTS.md - the project's declared goals, priorities and trade-offs - or a small Commitments section in AGENTS.md when tiny. Premise:…
- [glossary-md](./Groups/Viber/glossary-md/SKILL.md) — Maintains one unambiguous project vocabulary in alphabetical letter blocks. Golden rule for what earns a block: the word as used here carries more than the dict…
- [idea-md](./Groups/Viber/idea-md/SKILL.md) — Turns a raw project prompt - any language, any mess - into IDEA.md: the project's complete idea document, readable by anyone, technical or not. First the idea's…
- [readme-md](./Groups/Viber/readme-md/SKILL.md) — Create, review, and update professional README files grounded in the actual project, never in assumptions or nonexistent features. Use when asked to write, fix,…
- [steering](./Groups/Viber/steering/SKILL.md) — Interactive documentation architecture and steering taxonomy skill. Transforms project requirements or legacy documentation into the Two-Tier Steering Taxonomy…
- [system-md](./Groups/Viber/system-md/SKILL.md) — Produces and maintains SYSTEM-COMPONENTS.md for a confirmed application: an architectural inventory of the functional building blocks - subsystems, services, en…
- [units-md](./Groups/Viber/units-md/SKILL.md) — Generates, refreshes, and audits a project's UNITS.md - the index of reusable units an agent reads before implementing, so it extends what exists instead of bui…

### Video

- [create-video](./Groups/Video/create-video/SKILL.md) — Turn a vague video request into locked, numeric direction, then lay out, verify and deliver a professional video project. Loads after the hyperframes entry poin…
- [watch-video](./Groups/Video/watch-video/SKILL.md) — Watch a video by reconstructing it from frames plus a timestamped transcript, measure how objects move through it, and write structured markdown notes. Download…

### Standalone (repository root)

- [animation](./animation/SKILL.md) — Animation meta-skill — a router, nothing more. Routes any motion request to the sub-skill that holds the functionality: `life` (UI motion — micro, component, tr…
  - [ascii](./animation/ascii/SKILL.md) — Build ASCII and character-based animations for web, terminal, or CLI. Use when the user asks for an ASCII animation, terminal intro or loader, image or video to…
  - [life](./animation/life/SKILL.md) — Designs, builds, reviews, and prototypes UI animation through three commands - micro, component, transition (one element, one visual unit, one state-to-state mo…
  - [svg](./animation/svg/SKILL.md) — Animate a static, flat SVG logo or icon (solid-fill <path> elements) with one of twenty-five animation styles: chrome-liquid, draw-fill, loading-loop, elastic-e…
- [avatar](./avatar/SKILL.md) — Creates avatars without defaulting to one style. An avatar is a stand-in for an absent entity, so the skill first reads the request on four axes - medium, sourc…
- [benchmark](./benchmark/SKILL.md) — Benchmark candidates on task-derived dimensions, in normal or ultra mode. Think first: which decision is being made (faster, more accurate, less memory) and how…
- [caution](./caution/SKILL.md) — Informed-consent gate on the user's answers: screen every reply (chat, AskUserQuestion, command flags, hook or server input) for a decision whose cost the answe…
- [close-topics](./close-topics/SKILL.md) — Guided, conversational, topic-by-topic technical specification: close one design area before opening the next. Use when a project has undecided architecture (sc…
- [compare](./compare/SKILL.md) — Write professional, well-reasoned comparisons between two or more subjects of any kind — technologies, files, projects, code modules, books, documents, biologic…
- [design](./design/SKILL.md) — Design work, one skill, four modes: design-md (author the project's canonical DESIGN.md: machine-readable tokens + human rationale, Google Labs design.md conve…
- [dont-stop](./dont-stop/SKILL.md) — Forces the agent to keep working autonomously until the ENTIRE goal is truly finished, across all phases, with no mid-way stops, no "phase 1 done, ready for pha…
- [generate](./generate/SKILL.md) — Universal image AND video generation via RESTful providers (xAI, OpenAI, Gemini, KovAPI/NezhaGate) through registry data.csv: vendors and media types are data r…
- [learning-test](./learning-test/SKILL.md) — Write and run a "learning test" (term coined by Jim Newkirk, popularized by Robert C. Martin/Uncle Bob in Clean Code ch.8 "Boundaries") to empirically discover…
- [no-framework](./no-framework/SKILL.md) — Build Single Page Applications using NoF (No Frameworks) — Navigo (~4KB routing) plus a choice of small UI libraries (Preact by default, or VanJS / Nano JSX via…
- [parallelize](./parallelize/SKILL.md) — Plan and run parallel work: the main agent decides in chat how to fan out a large or newly approved job, keeps the most sensitive work for itself, and hands bou…
- [personalize](./personalize/SKILL.md) — Updates the user's GLOBAL agent instruction file (the personal AGENTS.md every project loads) so settled questions never get re-asked - an agent asking "which p…
- [pick](./pick/SKILL.md) — Pick the right PRODUCTION library for a development task instead of hand-rolling it - answers lookup questions from data.csv, a verified catalog across UI piece…
- [reveal](./reveal/SKILL.md) — Competitive-intelligence investigation into how unique a project idea actually is: how much already exists, who built it, how well it works, and what genuinely…
- [seam](./seam/SKILL.md) — Place and enforce the one file that knows the third party - the framework, the vendor SDK, the platform driver - so every layer above it speaks the project's ow…
- [sly](./sly/SKILL.md) — Resourceful route-finding when the obvious path is blocked: capture the value, not the access. INVOKED ONLY WHEN THE USER ASKS - '/sly', 'be /sly and find a sol…
- [spike](./spike/SKILL.md) — Turn "will this break it?" into numbers. A measurement, not a decision - pick the smallest renderable unit that carries a claim, derive its state list from code…
- [take-a-breath](./take-a-breath/SKILL.md) — Force a deliberate pause before implementing. Stop the urge to code from scratch, calm the overwhelmed engineering impulse, and apply sober judgment about wheth…
- [techstack](./techstack/SKILL.md) — Recommend a technology/framework/library/tech stack (mobile, web, backend, desktop, infra) in any language or platform via rigorous, current, requirements-drive…
- [theskills](./theskills/SKILL.md) — Pin skills as fixed, auto-apply behavior and persist that into the agent's memory context, so future sessions run them without being asked. Run at the start of…
- [tier-up](./tier-up/SKILL.md) — Installs and runs the three-tier type architecture in a project: the raw type is named in exactly one file per primitive family, every domain meaning becomes a…
- [type-up](./type-up/SKILL.md) — Enhances a codebase's type system so bugs surface at check time instead of runtime, in any language: brands for raw types, creation points, and boundary checks…

## Skill Details

### Agent

#### `amongus`

- **Path:** [`Groups/Agent/amongus/SKILL.md`](./Groups/Agent/amongus/SKILL.md)
- **Description:** Tiny awareness skill: the project has another agent working in it besides you. Edits you did not make, files that changed since you last read them, a hunks that vanished - that is the teammate, not corruption. On trigger, acknowledge with exactly one line - COPY That! - then keep working with zero further commentary. Includes numbered-identity generosity: whenever agents work anonymously by any means (shared devXX-style labels), whoever took a number first keeps it - yield generously to the next free number (dev72 taken means you become dev73), never contest, split or rewrite theirs. Never panic, never revert, never "restore" or overwrite work you did not touch: re-read the file for current state, keep your changes additive, and on a collision over the same file, wait until the other agent is done with it or move to another file and return afterwards. Use when confused changes appear in the working tree, when two agents share a repo, or when the user says amongus / another agent is editing this project.

---

#### `bequeath`

- **Path:** [`Groups/Agent/Bequest/bequeath/SKILL.md`](./Groups/Agent/Bequest/bequeath/SKILL.md)
- **Description:** End-of-session asset harvesting: review the whole conversation, propose what is worth keeping, and turn approved work into tested, reusable assets in the project's bequest/ directory. Finds throwaway scripts, command sequences, debugging procedures, config snippets, queries, repeated workflows, useful patterns and instructive dead ends. Reports candidates first (name, type, original purpose, proposal, future use, direct-vs-generalize) and creates nothing until the user selects; silence is not approval. Generalizes only approved items - configurable inputs, no hardcoded values, temp paths or task assumptions - then tests beyond the original example and states verification honestly (verified automated/manual, partial, unverified). Each asset carries a card (what, when, how, inputs, outputs, assumptions, limitations, verification) beside its tests, with an index for discovery. Never stores secrets, never duplicates an asset, never claims untested reliability. Not session state or new global skills.
- **Use-case:** The conversation is ending, or the user says "bequeath", "save what we learned", "keep this for next time", "turn this into something reusable" — and work performed in the session may be worth preserving beyond it.
- **Usage:** `/bequeath [optional scope: e.g. 'just the debugging scripts']`

---

#### `context`

- **Path:** [`Groups/Agent/Session/context/SKILL.md`](./Groups/Agent/Session/context/SKILL.md)
- **Description:** Project-context reconstruction — build a reliable mental model of a project from all available artifacts (docs, source, config, git history with a 5-commit default, Flush notes, images, prototypes, design artifacts) before any work. Two modes: light (default) inspects and reads only, never running tests, builds, installs, or scripts; utter allows active verification when inspection alone cannot answer. Neither mode modifies the project for context. Treats docs as unverified, cross-checking claims against code; conflicts resolve by priority (current state > source/config > docs > recent git > flush notes > history), and fact, intention, decision, assumption, unknown stay distinct — assumptions never silently become facts. Completes when the agent could work without blindly rediscovering fundamentals. Reads companion Flush files (incl. the SESSIONS.md journal), works without them. Use at session start, before nontrivial tasks, after compaction. Triggers: load context, understand the project, get oriented.

---

#### `flush`

- **Path:** [`Groups/Agent/Session/flush/SKILL.md`](./Groups/Agent/Session/flush/SKILL.md)
- **Description:** Agent continuity capture, manual — persist working state before session end, environment change, loss, milestone, handoff, or when the conversation grew too large: CONTEXT.md (how we got here — decisions, reversals, what worked/failed, open questions), PLAN.md (the ACTUAL plan, not the original), SNAPSHOT.md (facts verified against the project, not memory), STATUS.md (assessment) — one job per note; compression, never transcript or continuation. Each flush carries an agent-chosen kebab-case session name with a sequence number in every note header and appends one entry to the append-only SESSIONS.md journal, so later sessions see each session's record; past entries are never rewritten and git owns old note content — no hand-rolled archives. Uncertainty stays Unknown, partial work is never written as done, stale notes are replaced not accumulated, cross-note consistency checked before completion. The companion context skill reads these back. Triggers: flush, save/persist state, hand off the project.

---

#### `heir`

- **Path:** [`Groups/Agent/Bequest/heir/SKILL.md`](./Groups/Agent/Bequest/heir/SKILL.md)
- **Description:** Acknowledge the legacy of previous agents before rebuilding anything. At the start of a task, if the project has a `bequest/` directory, open its INDEX, decide whether any inherited asset fits THIS task, verify it before trusting it, then reuse, adapt or extend it in place. Use when starting work in a project that may already contain scripts, procedures, configs or patterns left by earlier sessions, or when the user says "we did this before", "reuse what exists", "check what is already there". Inherited assets are evaluated, not assumed: inputs, assumptions, dependencies and verification status are read from the asset card, and its tests are run before it is trusted — a partially verified asset is a lead, not a fact. Improvements update the asset and its card rather than forking a copy. heir never creates bequest assets itself; when the session produces reusable work it hands off to `bequeath` so the next agent inherits it too.
- **Use-case:** At the beginning of a task in a project that has a `bequest/` directory, or whenever prior work might already solve part of the current problem.
- **Usage:** `/heir [what the current task is about, for matching against bequest/INDEX.md]`

---

#### `how-to-do`

- **Path:** [`Groups/Agent/how-to-do/SKILL.md`](./Groups/Agent/how-to-do/SKILL.md)
- **Description:** Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are done the same correct way every time across sessions, agents, and models — instead of silently missing a step. ALWAYS check for a .htd/ folder at the repo root before starting ANY coding task, even if not mentioned, and consult it if present. Trigger this — don't wait to be asked — whenever the user says "add", "create", "change", "update", "refactor", "migrate", "wire up", or "integrate" something in a real codebase, including simple-sounding tasks like "add a table" (exactly what this exists for — never skip as too simple). Also trigger on any mention of "how-to-do", ".htd", or standardizing a workflow. After any nontrivial multi-file change in a repo with (or needing) .htd/, use this proactively to record a new procedure, patch an existing one, or confirm no update is needed — skipping this defeats the skill's purpose.

---

#### `mistakes`

- **Path:** [`Groups/Agent/mistakes/SKILL.md`](./Groups/Agent/mistakes/SKILL.md)
- **Description:** A personal, growing log of mistakes already made or observed, with where each one shows up and how to fix it. Use when the user says mistakes, check my mistakes, audit for mistakes, avoid this, remember this mistake, log a mistake, add to my mistakes, lessons learned, I told you before, we already fixed this, or before data modeling, API design, migrations, auth, state management, UI, tests, or configuration. Invoked as /mistakes it audits the project against the active log, reports confirmed findings with file and line evidence, fixes the safe ones (docs, comments, README, tests) and proposes the risky ones (schema, migrations, API contracts, auth, secrets) for approval instead of editing them. It also loads only the rows that match the current task, applies their fixes before the work, runs their checks after it, and appends a new row only when the user asks. Not a style guide, not a generic best-practice list, and never a silent override of the project own documented decisions.

---

#### `persona`

- **Path:** [`Groups/Agent/persona/SKILL.md`](./Groups/Agent/persona/SKILL.md)
- **Description:** Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full behavioral specification of how the agent thinks, investigates, judges quality, and communicates. Use this whenever building, prompting, or orchestrating a subagent (security reviewer, database engineer, testing engineer, frontend engineer, DevOps/SRE, technical writer, code reviewer, or any other domain specialist) and a generic "you are a senior X" persona would be too shallow. Especially relevant for multi-agent orchestration systems (e.g. contribute-agents) that need distinct professional perspectives per role, and for any task asking to "give this agent a persona," "make this agent think like a senior X," or "construct context for a subagent." The method is role-agnostic — it applies identically whether the role is testing, security, database, frontend, or something else entirely.

---

#### `recall`

- **Path:** [`Groups/Agent/recall/SKILL.md`](./Groups/Agent/recall/SKILL.md)
- **Description:** Recall, in two modes, on one rule: report only what you can actually find. Mode A answers "do you remember when I said X?", "did I mention Y?", or /recall <topic> from what is really present - live context, plus past-chat or memory tools when present: open with Yes, No, or Partly, quote the user's own words verbatim on a Yes, 1-5 lines, never an invented memory. Mode B recovers a conversation that compaction, a lost session, or a new terminal made unavailable: prefer the harness's own history mechanism over file hunting, locate the session by id, title, date, or distinctive content, inspect the real storage format before parsing, and recover at the requested depth - full fidelity (tool calls, outputs, errors, order) or the discussion - chunking long transcripts on record boundaries. The objective is the ORIGINAL conversation, not a summary or reconstruction; inaccessible sources are stated as limits, not guessed. Escalates A to B when the answer is missing from context but plausibly in an earlier session.
- **Use-case:** The user asks whether you remember, recall, or were told something earlier ("do you remember when I said…", "did I mention…", "what did I tell you about…"), or invokes /recall; or context was compacted or the session was lost and the current task depends on earlier decisions, instructions, tool results, errors, or research no longer visible.
- **Usage:** `/recall [what you asked earlier, or the session to recover]`

---

#### `subagent`

- **Path:** [`Groups/Agent/subagent/SKILL.md`](./Groups/Agent/subagent/SKILL.md)
- **Description:** Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structured brief with hierarchical Context, precise Goal, How, Autonomy Bounds, and Output Contract so the sub-agent stays focused, never decides, and returns full raw results instead of summaries. Also covers pre-delegation environment consistency checks (to prevent sub-agent drift), requirements for exhaustive slightest-detail reporting back to the main agent, detecting/mitigating race conditions between concurrently running sub-agents (e.g. shared scripts or files), and the default dispatch mode — sub-agents always run in the background unless the user explicitly asks for foreground. Triggers include sub-agent, subagent, delegate, spawn worker, professional brief, task handoff, isolated prompt, parallel agents, concurrent agents, background agents. It also carries the rulebook in the brief and clears the subagent's authority questions with the user first.

---

### Audit

#### `anti-slop`

- **Path:** [`Groups/Audit/anti-slop/SKILL.md`](./Groups/Audit/anti-slop/SKILL.md)
- **Description:** Review UI and product-design quality for a page, selected routes, an application, or a repository. Use when asked to find, explain, prioritize, or guide correction of design anti-patterns using visual/contextual evidence, source inspection, or both. Routes through a 67-pattern catalog and keeps findings evidence-based; it does not infer AI authorship or treat style matches as violations.

---

#### `antipattern`

- **Path:** [`Groups/Audit/antipattern/SKILL.md`](./Groups/Audit/antipattern/SKILL.md)
- **Description:** Investigates a software project, researches the engineering anti-patterns that matter for its stack, gathers evidence from code, architecture, business rules and dependencies, and documents which anti-patterns agents must avoid (usually as ANTIPATTERN.md). Use whenever the user asks about anti-patterns, code smells, AI slop, "what should we avoid in this codebase", wants project rules against bad patterns, wants an anti-pattern audit or report, or asks to create or update ANTIPATTERN.md, even if they never say "anti-pattern". Findings are rated for impact and confidence separately, kept to what project evidence supports, and a clean audit is a valid result. Identifies, investigates, recommends and documents only. Do NOT use to fix, refactor or enforce rules, for general code review, or to change application behavior.
- **Use-case:** The user asks what anti-patterns, code smells, or bad practices to avoid in a project; requests an anti-pattern audit, report, or rules document; mentions AI slop in a codebase; or asks to create or update ANTIPATTERN.md.
- **Usage:** `/antipattern [a pattern, an area, or 'audit this repo']`

---

#### `crosscheck`

- **Path:** [`Groups/Audit/crosscheck/SKILL.md`](./Groups/Audit/crosscheck/SKILL.md)
- **Description:** Cross-check a task, codebase, or research question by blind orthogonal discovery: dispatch N isolated subagents (N >= 2), each engineered with a distinct cognitive lens - empirical/pattern-scanning, structural/behavioral, adversarial, product-pragmatist - none of them seeing the others' findings, hypotheses, or methods, then synthesize the reports into one reconciled document. Every finding is labelled by how it was found: consensus (corroborated by independent lenses), solitary (visible to only one lens), conflict (scouts disagree, tie broken by direct inspection), or dismissed (candidate proven a false positive). Use for "crosscheck this", multi-agent discovery, exhaustive audits where anchoring and shared blind spots are the risk, layer-violation or invariant sweeps, and when the orthogonal-scout agents are dispatched. Phase 0 pauses to disambiguate scope with the user first. Writes .repertoire/findings/<topic>-findings.md; scout reports stay in .repertoire/agents/ unless --cleanup.
- **Use-case:** The user asks for a crosscheck, a blind multi-agent audit, orthogonal discovery, "have several agents look at this independently", or an exhaustive findings report where one agent's framing could hide a whole class of issues; also before a large refactor or review that needs both recall and precision.
- **Usage:** `/crosscheck [N] [task] [--lenses "a,b,c"] [--cleanup|--keep-artifacts]`

---

#### `exmaine`

- **Path:** [`Groups/Audit/exmaine/SKILL.md`](./Groups/Audit/exmaine/SKILL.md)
- **Description:** Examine a project from the inside out, starting at AGENTS.md: follow every doc path it declares (design docs, units, glossary, commitments, decisions, skill sources), read them, sweep the code against what the docs claim, and deliver a complete overview that orients an agent fully around the project. Strictly static and read-only: never runs install, test, build or serve commands - files are only read; anything unprovable by reading is reported as an unverifiable runtime claim, never assumed. /exmaine full runs the complete examination: every area checked against its stated intent, broken pointers and orphan code recorded in a gap ledger, ending with the full project overview. Use when asked to exmaine/examine/inspect the project, to get oriented in an unfamiliar repo, 'read the docs and check the code', or before a large task needing whole-project understanding. Not a verdict run ('is this complete and verified?' = please-verify), not refactoring proposals, not runtime debugging.

---

#### `impurities`

- **Path:** [`Groups/Audit/impurities/SKILL.md`](./Groups/Audit/impurities/SKILL.md)
- **Description:** Project-wide defect discovery and remediation through self-designed iterations — never a fixed checklist. Assess the actual project (runtime, resources, dependencies, assets, build, CI, config, platforms), then design and run as many focused investigate-and-remediate iterations as its specific risks warrant: investigate, document findings with evidence, root-cause, fix preserving intended behavior, verify, commit traceably on an isolated branch. Core discipline — absence of an obvious reference is evidence to investigate, not proof of unused: build tooling, plugins, reflection, codegen, and CI consume what imports never show. Findings classified confirmed/suspected/optimization/unresolved, never beyond their evidence; the plan adapts mid-work; sub-agents take independent scopes, the parent owns integration. Completes on responsible coverage, not "defect-free". Use for hidden defects, waste, unsafe patterns, deep tech-debt sweeps. Triggers: impurities, defect hunt, find what's wrong, deep cleanup.

---

#### `ladder`

- **Path:** [`Groups/Audit/ladder/SKILL.md`](./Groups/Audit/ladder/SKILL.md)
- **Description:** Find, design and harden ladders: ordered decision structures where rungs (a condition paired with an outcome) are evaluated in one order until something wins. Built for asks such as whether the code already has tiers, layers or fallbacks between its parts, whether errors escalate instead of being swallowed, and whether a guarantee is actually guaranteed: it audits the code for the precedence chains already in it, reports findings with file:line evidence, presents the fitting shapes with trade-offs and asks which to take, then records the decision in the project's own doc format and implements to it. Names the twelve shapes and four semantics (first-match, all-strictest, all-permissive, exactly-one) and the defects it detects (shadows, unreachable rungs, missing terminal rung, severity inversion, swallowed failures). Writes them without nested conditionals: pure decide over data, effects at the boundary, in the repo's own paradigm.
- **Use-case:** The user asks whether tiers/ladders/layers or fallbacks exist in the code, wants code made more robust or a guarantee guaranteed, wants errors or information escalated instead of swallowed, asks to design classification/routing/authorization/escalation/state-resolution logic, wants an if-else chain replaced, or asks why one rule never fires.

---

#### `packages`

- **Path:** [`Groups/Audit/packages/SKILL.md`](./Groups/Audit/packages/SKILL.md)
- **Description:** One run, two jobs over a project's dependencies, any ecosystem (JS/TS, Python, Go, Rust, JVM, .NET…) and any project shape. Job 1 — redundancy audit: classifies each dependency as explicit (imported) or implicit (needed without any import: toolchain binaries, native/link-time stubs, config plugins, entry-point-discovered packages, blank imports, peer deps, codegen, type-only), flagging for removal only what is neither. Job 2 — freshness: updates via the ecosystem's first-class tooling when it exists (go mod tidy, bun update --latest, cargo upgrade, uv, dotnet-outdated…), else resolves latest via context7 or registry/web search — never memory; always a before/after report for approval, majors checked against migration guides and real project usage first. Both jobs close with a mandatory verification gate — resolve, typecheck/compile, build, tests, runtime — with commands discovered from the project's scripts and CI, never invented. Use to audit, dedupe, clean up, update, or modernize dependencies in any stack.

---

#### `please-verify`

- **Path:** [`Groups/Audit/please-verify/SKILL.md`](./Groups/Audit/please-verify/SKILL.md)
- **Description:** Broad verification of a project or delivered body of work - not just the last step - answering one question: is the work actually complete and sufficiently verified? Starts from the user's ask (conversation, IDEA.md, plan, AGENTS.md), never from the agent's own summary, and sweeps requirements, completeness, bugs, rule violations, consistency, missing work, proof of work, integration and project-level correctness. The evidence ladder is the rule: files existing is not proof, 'it should work' is not proof - a build log, a test run with output, a launched app with observed behavior are proof; unproven is UNVERIFIED, never PASS. Catches the classic failure: files delivered and called 'done' without ever building or running them. Read-only: runs builds, tests and the app for evidence, then reports COMPLETE & VERIFIED / INCOMPLETE / UNVERIFIED / BROKEN with an evidence table, blockers and ordered next actions - it does not fix. Triggers: 'please verify', 'is this actually done', 'did we finish', 'prove it works'.
- **Use-case:** The user asks whether work is really complete, wants a broad project-level verification or a proof-of-work check, or a delivery claims to be finished and the claim needs testing against the original expectations. Also /please-verify.
- **Usage:** `/please-verify [the project path, or the scope to verify]`

---

#### `pvc`

- **Path:** [`Groups/Audit/pvc/SKILL.md`](./Groups/Audit/pvc/SKILL.md)
- **Description:** Role-based UI construction (Page → View → Component, plus Decoration, Aligner, UI Element, Rendition) — framework-agnostic architecture for building or auditing UI code in React, Vue, Solid, Svelte, Blazor, Dioxus or any component system. Use when designing a screen or feature folder, deciding what a piece of UI actually is, separating loading/error/offline handling, placing a shared Component, naming a unit, or when a codebase has become "everything is a component". Also use for `scripts/check_pvc.py` audits and `scripts/scaffold_feature.py` skeletons. Classifying a fact as a State or a Condition, and deciding who owns it, is the companion /states skill — invoke both for screen design; this skill needs only whether a unit reads a fact source.
- **Usage:** `/pvc <feature or screen being designed, or a path to audit>`

---

#### `scraper-optimizer`

- **Path:** [`Groups/Audit/scraper-optimizer/SKILL.md`](./Groups/Audit/scraper-optimizer/SKILL.md)
- **Description:** Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory-bounded web scrapers and data ingestion pipelines across Python, Go, Node.js, Rust, C#, and Java.

---

#### `seo`

- **Path:** [`Groups/Audit/seo/SKILL.md`](./Groups/Audit/seo/SKILL.md)
- **Description:** Universal 100-point on-page SEO playbook for ANY web stack (Next.js, SvelteKit, Nuxt, Blazor, ASP.NET, Rails, Laravel, Django, Dioxus, Leptos, Astro, Hugo, static HTML - SSR, SSG or client-rendered). Use when the user wants to build, audit, or auto-fix pages so the raw first HTML packet scores 100/100 on Wincher-style on-page criteria (title/headings/body/meta/media/code/url), or makes any SEO complaint ("SEO audit", "my SEO is bad", "traffic dropped", "not ranking", "thin pages", "meta tags review"). Commands: /seo [target] = analyze then fix everything without asking, /seo analyze [target] = report only. Target may be a single page ("login page"), a section family ("funds page" = ALL funds-related routes: list, detail, tabs, categories, compare), or omitted (= whole codebase).
- **Use-case:** Auditing or fixing on-page SEO for any framework so pages reach a 100/100 first-packet score.
- **Usage:** `/seo [analyze] [page | section | url]`

---

#### `states`

- **Path:** [`Groups/Audit/states/SKILL.md`](./Groups/Audit/states/SKILL.md)
- **Description:** Classify any fact an app consults as a State or a Condition, decide who owns it, and settle whether a consumer may read it or must create it. Use when deciding loading vs offline, error vs permission-denied, empty vs feature-flag-off, or any "is this my own request or something external" question; when placing a fact source (hook, composable, signal, resource, store, injected service); when a background job, sync worker, or subscription needs an ownership decision; or when a fact is duplicated across consumers. Fact sources return data and never render — the UI roles that consume them belong to the /pvc skill.
- **Usage:** `/states <the flag, loading value, subscription, or request being classified>`

---

#### `treat`

- **Path:** [`Groups/Audit/treat/SKILL.md`](./Groups/Audit/treat/SKILL.md)
- **Description:** Evaluate how adopted tools and libraries want to be used and recommend structure or adaptations that respect their model - concepts, patterns, constraints. Reviews a named tool, or discovers model-heavy candidates from the dependency manifests when none is named. Version-aware: the model comes from docs for the installed version, and previous-major idioms are findings. Produces a diagnostic report (in chat by default, as TREAT.md on request) and never edits code. Use when adopting a library or checking whether a project forces a tool into an unnatural shape (Zod, Effect, io-ts). Triggers include treat, respect the tool, tool-aware structure, library model, adapt project to library, zod v3 vs v4, library migration, are we using this library correctly.

---

### Code

#### `code-review`

- **Path:** [`Groups/Code/code-review/SKILL.md`](./Groups/Code/code-review/SKILL.md)
- **Description:** Review the changes since a fixed point (commit, branch, tag, merge-base) on two separated axes run as parallel subagents and aggregated side by side, never cross-reranked: Standards (does the diff follow the repo's documented rules plus a Fowler code-smell baseline that the repo always overrides, skipping what tooling enforces?) and Spec & Quality (is the spec faithfully implemented, judged on correctness, readability, architecture, security, performance?). Carries the Google gate: approve when it definitely improves code health, not perfection; severity labels (Critical/Required/Nit/Optional/FYI); tests reviewed first; change sizing ~100/300/1000 lines; named structural remedies instead of "this is complex"; dependency discipline; dead-code ask-before-delete; no-LGTM honesty rules; never accept "fix it later". Use before merging, evaluating agent-written code, or when asked "is this ready". Not for fixing bugs a review finds (dbug, fix), commit messages (commit), or full-repo security scans (security-scan).
- **Use-case:** The user says review / is-this-ready / look at my diff, before any merge or PR, after a feature lands or an agent produced code, or after a bug fix when the regression test needs reviewing too.
- **Usage:** `/code-review [fixed point: commit | branch | tag | 'main']`

---

#### `dbug`

- **Path:** [`Groups/Code/dbug/SKILL.md`](./Groups/Code/dbug/SKILL.md)
- **Description:** Debug any problem in any codebase, any language — bug, error, exception, crash, 500, timeout, wrong/missing/duplicate data, regression, "worked before", "works on my machine", flaky, prod-only, or a pasted stack trace — even if the user never says "debug". One loop everywhere: see the problem → understand it → form a falsifiable hypothesis → run the cheapest experiment that can refute it → narrow → repeat; negative results delete search-space, so narrowing IS getting closer. Opens the mind with duck debugging: say the full traceback out loud, hop by hop (what enters, what must leave, what actually left) — it exposes the problem before any tooling runs. Stances: root cause not symptom, fix the source of truth, minimal-but-complete across every layer, every bug is a chance to test, controlled observation, honest escalation. Domain playbooks (backend, database, frontend, production), investigation engine, escalation ladder, git forensics, instrumentation, regression-testing load on demand from references/.
- **Use-case:** Something is broken, wrong, failing, unexpected, regressed, or hard to reproduce — the moment you feel the urge to "just change code until the error disappears" is the moment to load this skill.
- **Usage:** `/dbug [problem description | pasted error/traceback]`

---

#### `fix`

- **Path:** [`Groups/Code/fix/SKILL.md`](./Groups/Code/fix/SKILL.md)
- **Description:** After root-cause diagnosis with dbug, resolve the problem and improve the relevant implementation so the same or similar problems become easier to identify, understand, or prevent in the future. Use together with dbug whenever a problem has been understood and a fix is being applied. Covers immediate fix, local-context generalization, consequences, explicit and implicit references, and consistency. Not a standalone debugger.

---

#### `gh`

- **Path:** [`Groups/Code/gh/SKILL.md`](./Groups/Code/gh/SKILL.md)
- **Description:** All GitHub CLI/Actions work in one router: fix failing CI/PR checks (gh pr checks, gh run view --log-failed, bundled inspect_pr_checks.py; classify workflow-file vs job vs flaky vs infra vs external), auth and tokens (gh auth scopes, GITHUB_TOKEN permissions, 401/403 causes, never paste a token into chat), author or edit .github/workflows YAML (valid YAML is not a valid workflow: the space-hash comment trap, quoting expression scalars, actionlint gate), keep workflows thin (wiring not logic - move run: bodies into checked-in script files, conditions stay declarative, scripts return exit codes and one-line feedback; embedding programs in YAML breaks block-scalar indentation and mixes shell with language errors), and harden (SHA-pinned actions, least-privilege permissions, script-injection defense via env mapping, fork-PR rules, OIDC, concurrency, timeouts). Also gh run rerun, workflow dispatch, artifact/release inspection. Not for GitLab CI, Azure Pipelines, Jenkins, or application YAML unrelated to Actions.
- **Use-case:** Anything with gh, GitHub Actions, workflows, CI, or PR checks in it: the user says "fix CI", "the workflow failed", "write a workflow", pastes a run URL, a run says "This run likely failed because of a workflow file issue", a gh command answers 401/403, or a run: block you are writing grows past a couple of lines.
- **Usage:** `/gh [pr number | run URL | workflow file | task description]`

---

#### `implement`

- **Path:** [`Groups/Code/implement/SKILL.md`](./Groups/Code/implement/SKILL.md)
- **Description:** Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates, in order: (1) a coding brief naming the app/module being coded and which stack-agnostic concerns it touches (interfaces, styling, a11y, navigation, forms, persistence, platform, concurrency, errors, build); (2) root inspection to detect the real toolchain (lockfile decides - bun.lock->bun, package-lock.json->npm, Cargo.lock->cargo, go.mod->go, uv/poetry.lock->python; binding project rules outrank inference); (3) targeted grounding of ONLY the touched concerns in CURRENT official docs for each ecosystem, via the `scrape` skill when available (cache + grep over re-fetching; WebFetch fallback), with trade-off questions to the user instead of silent picks. Use before scaffolding/editing source in any stack (TypeScript frameworks, Rust, Python, Go, ...) - it exists to stop coding from model memory that went stale. Chain with project standards skills when present.

---

#### `planner`

- **Path:** [`Groups/Code/planner/SKILL.md`](./Groups/Code/planner/SKILL.md)
- **Description:** Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifies vague or slang-heavy language if needed, then generates structured hypotheses that surface explicit requirements plus professional reading-between-the-lines concerns, gathers local and web context, iterates with the user until hypotheses are approved, and finally produces a solid plan. Use in planning-mode or quest-mode, or whenever the user asks for a plan, architecture outline, implementation roadmap, or disciplined decomposition of a complex task. Triggers include planner, planning mode, quest mode, make a plan, rigorous plan, hypothesis-driven planning.

---

#### `refactor`

- **Path:** [`Groups/Code/refactor/SKILL.md`](./Groups/Code/refactor/SKILL.md)
- **Description:** Surgical code refactoring that improves structure and maintainability without changing behavior. Use when the user says refactor this, clean up this code, fix code smells, extract method, replace conditional, move method, introduce parameter object, eliminate duplication, break down god class/function, improve type safety, or prepare code for a new feature by restructuring. Also trigger for technical debt, smell-driven cleanup, safe transformation sequences, and characterization tests before change. Covers smell catalog, composing methods, moving features, organizing data, simplifying conditionals, and the green-to-green workflow. Not for big-bang rewrites or feature work mixed with structure changes.

---

#### `test`

- **Path:** [`Groups/Code/test/SKILL.md`](./Groups/Code/test/SKILL.md)
- **Description:** General testing principles and ethics for any test the agent writes or reviews — unit, integration, contract, e2e, property, invariant, regression, or pipeline. Use whenever writing, refactoring, reviewing, or deciding what tests a change needs. Covers one-reason-to-fail, test vs verifier distinction, test data as contracts, selective execution, minimal mocking with feature-flag style seams, and discrimination. Do not use for project-specific tooling or mandated workflows.

---

#### `update`

- **Path:** [`Groups/Code/update/SKILL.md`](./Groups/Code/update/SKILL.md)
- **Description:** Change something everywhere it lives, leaving no stale copy behind. Use for ANY change request: reword copy or docs; rename a term, identifier, file, route, or brand; change a value (price, limit, version, color, date), a behavior, or a rule; alter an interface or schema; swap a dependency; move a path; upgrade, deprecate, or restyle. Trigger on update, change, rename, replace, reword, rebrand, bump, correct, migrate, "switch X to Y", "we no longer do X", "it says X but should say Y", "make the docs match", even when only one file, line, or string is named. Pins the claim, finds its source of truth, sweeps by exact text, naming variants, i18n/locale files in every language, tests, docs, config, SEO/a11y text, and by meaning; classifies hits, asks how far to go instead of deciding scope alone, applies, and proves nothing stale remains. Builds a dry-run batch script for wide mechanical edits. Not for new features; for a true defect, find the root cause first.

---

### Crawl

#### `capture`

- **Path:** [`Groups/Crawl/capture/SKILL.md`](./Groups/Crawl/capture/SKILL.md)
- **Description:** Capture visuals, files, data, or design from designs, sites, pages, and apps, invoked as `/capture designs|screenshots|siteshots|page|website|dom|design|images`. `designs` batch-screenshots HTML mockups; `screenshots` images URLs/HTML files; `siteshots` discovers a site's routes (sitemap, robots, crawl) and screenshots each as a scroll series; `page` images a running Windows app window; `website` mirrors a site for offline use and verifies it; `dom` saves fully rendered, fully expanded HTML for scraping; `design` dumps a site's HTML/CSS via curl (html.dump, css.dump) and extracts design tokens (colors, typography, spacing) or HTML/CSS patterns to clone; `images` downloads a page's images at highest original resolution with scroll triggering, filters, deduplication and a JSON decision report. Use whenever the user types /capture, or asks to screenshot, mirror, download, scrape, get a page's DOM, pull a page's images, or extract a site's colors, fonts, design system, or HTML structure to clone or reference.
- **Use-case:** The user types /capture, or asks to screenshot a page, a whole site's routes, or a running app window, mirror or download a site offline, get a page's rendered HTML for scraping, download a page's images at full resolution, extract a site's design tokens or HTML patterns, or compare any of those against the project's own designs.
- **Usage:** `/capture [designs|screenshots|siteshots|page|website|dom|design tokens|design patterns|images] [url or options]`

---

#### `educate`

- **Path:** [`Groups/Crawl/Scraping/educate/SKILL.md`](./Groups/Crawl/Scraping/educate/SKILL.md)
- **Description:** Turns documentation retrieved by the Scrape skill into a pruned, project-relevant, indexed, version-aware knowledge base so the agent never has to re-read or re-search the full raw docs again. Use whenever the user asks to "learn"/"study" a library or framework's docs, wants deep or repeated work with a specific dependency's documentation, asks to build or refresh a local docs index/cache, or whenever you notice you're about to re-scrape or re-read the same third-party documentation you've already fetched. Requires the Scrape skill's output as input — if that documentation hasn't been retrieved yet, run or request Scrape first. Covers pruning raw docs, detecting the project's real dependency version from whatever manifest format its ecosystem actually uses (Node, Python, Rust, Go, Ruby, PHP, JVM, or others — a template, not a fixed list), monorepos with conflicting versions, building a searchable index, and version-aware cache reuse.

---

#### `fahlwy`

- **Path:** [`Groups/Crawl/fahlwy/SKILL.md`](./Groups/Crawl/fahlwy/SKILL.md)
- **Description:** Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts, PDF books, brand logos) by fetching real bytes and validating magic signatures - never stopping at a guessed URL. Keeps its catalog as queryable CSV (data.csv: category, provider, family, url_form, kind, status, last_proven, access, rights, coverage, notes) plus an append-only growth ledger (log.csv), read and written through scripts/catalog.py. Use whenever asked to "find N sources", build an asset/placeholder source list, wire mockup media, or hunt down reliable hotlink/direct-download endpoints, then keep going until every slot is verified.
- **Use-case:** The user wants a countable list of working external asset URLs (images/avatars/video/audio/icons/fonts/PDF books/brand logos), asks to "find a way" to source media for a mockup/demo, wants verified placeholder/stock endpoints, or asks what the catalog already knows (`catalog.py list/search/stale`).

---

#### `scrape`

- **Path:** [`Groups/Crawl/Scraping/scrape/SKILL.md`](./Groups/Crawl/Scraping/scrape/SKILL.md)
- **Description:** Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all guide pages + every API component page; capacitor/react/vue planned) plus `--auto` URL discovery for any Docusaurus-style docs site and explicit `--url` scraping, with a `--verify` mode that proves every page is reachable and server-rendered. Use whenever the agent needs authoritative external docs - e.g. Ionic component props/events/methods/CSS custom properties before building mobile UI, API reference lookups, or confirming doc URLs exist - instead of guessing from memory or fetching pages one by one.

---

### Decision

#### `contract`

- **Path:** [`Groups/Decision/contract/SKILL.md`](./Groups/Decision/contract/SKILL.md)
- **Description:** Documents who owns what across architectural layers as tiny, precise contract files in <docs>/contract/: one responsibility per file, ownership either OoU (exactly one layer owns it) or AoU (all defined layers share it — never dual), with the reason and trade-offs recorded as a durable micro-decision. Use when the user asks where a responsibility belongs ("where should filtering/validation/retries/caching happen", "who owns X", "should the frontend or backend do this"), asks to write, update, list, or check a contract, runs /contract, or when implementing would silently scatter the same logic across layers; also when a scenario needs an explicit exception to an existing rule (hot-path vs default). Layers default to Database(0), Backend(1), Frontend(2), extensible per project; "application-side" always means Backend or Frontend, not Backend alone. Not for full architecture documentation (architecture), goals and priorities (commitments-md), vocabulary (glossary-md), or general prose documents (document).
- **Use-case:** A cross-layer responsibility is being decided (filtering, retry, validation, authorization, caching, formatting), a decision contradicts or extends an existing contract, or the user types /contract.
- **Usage:** `/contract [list|new <responsibility>|update <file>|check]`

---

#### `decide`

- **Path:** [`Groups/Decision/decide/SKILL.md`](./Groups/Decision/decide/SKILL.md)
- **Description:** Helps the user choose between candidates (software in any language or platform, databases, tools, cloud services, products, approaches) by researching them fairly and delivering one rich HTML decision page. The Compare tab has a dated freshness section, per-dimension winners (ties allowed), charts, tables, ratings, sources and a goal-based verdict. The Showcase tab shows real examples (code, images, audio, video, documents, specs or sample output, whichever fits) with candidate tabs. The page exports to PDF. Use this whenever the user wants to decide, choose, pick, evaluate, or compare options, asks "which is best", "X or Y?", "should I use...", "help me pick a...", or mentions /decide, even if they do not ask for a page or report.

---

#### `dtb`

- **Path:** [`Groups/Decision/dtb/SKILL.md`](./Groups/Decision/dtb/SKILL.md)
- **Description:** Do the Best: decide HOW the work is done while the user keeps owning WHAT is to be built. Use when the user hands over a goal, prototype or reference without every technical detail, says "make it good" / "you decide how", or when an autonomous run needs a decision method. The user's vision is a constraint: improve its execution, never replace its direction - redesign only on explicit request. Looks past the visible requirement to the systems behind it (a "search feature" may imply indexing, filtering, ranking, empty states), judges alternatives, edge cases and trade-offs, and picks the strongest appropriate solution - not the first that works, not the most complex. Records lasting decisions as question -> options -> choice -> consequences -> reversal, one file per decision in docs/decisions/ anchored Date+Commit+Version; the ask-or-decide call is recorded too. Interrupts only about vision, requirements, irreversible or costly calls - never to choose details already delegated. Pairs with iwts; runs alone.
- **Use-case:** The user delegates implementation judgment ("you decide how", "make it the best version", "I only care about the result"), hands over a design/prototype to be built properly, or asks the agent to take ownership of engineering decisions — including during an iwts run.
- **Usage:** `/dtb [the goal or artifact whose implementation is being decided]`

---

#### `iwts`

- **Path:** [`Groups/Decision/iwts/SKILL.md`](./Groups/Decision/iwts/SKILL.md)
- **Description:** Autonomous ownership mode — "I Want to Sleep". Invoke when the user says iwts, "I want to sleep", "take over", "finish it while I'm away", or delegates the project and leaves: act as the senior engineer temporarily responsible - decide, implement, fix, validate, keep moving to completion without the user. Thin operating mode: records follow the project's AGENTS.md Ambiguity convention (default: one file per decision in docs/decisions/, anchored Date+Commit+Version; ask-decisions too). Make the best reasonable decision instead of asking; prefer reversible choices with clean boundaries; hunt root causes before stopping; measure progress by completion, not activity; never invent work. Exactly two stops: the work is genuinely complete, or a decision truly belongs to the user (irreversible, external commitment, real cost, missing credentials, ambiguity that materially changes the outcome). Keep the run ledger at docs/decisions/states.md for interrupted-session resume. Not for one-off tasks with the user present.

---

#### `thebest`

- **Path:** [`Groups/Decision/thebest/SKILL.md`](./Groups/Decision/thebest/SKILL.md)
- **Description:** Evidence-based option choice for THIS project: gather proof, hand the user a verdict - "this is likely best for us, based on these tests and research" - and stop; the USER decides (dtb is the reverse). Frame hard constraints first (stack, platform, license, AGENTS.md) and eliminate violating options visibly, before testing. List ALL viable ways (user candidates, ecosystem standards, codebase precedents, lesser-known families), never a remembered shortlist. Map each criterion to its evidence: numbers -> /benchmark (real data, isolated environments), actual library behavior -> /learning-test, facts -> research (context7 if installed, else version-matched docs), fit -> argued; many decisions are pure research - a forced benchmark is fake rigor. Verdict carries confidence, runner-up with its flip condition, untested items. Use for "which approach/library for X", design forks, A-vs-B. Not fresh-stack picks (techstack), the measurement engine (benchmark), or an HTML decision page (decide).
- **Use-case:** The user asks which method/library/approach to use for something, presents candidates to choose between, or a design fork needs an evidence-based verdict; also /thebest.
- **Usage:** `/thebest [the decision, known options, and project constraints if already stated]`

---

### Design

#### `assets`

- **Path:** [`Groups/Design/assets/SKILL.md`](./Groups/Design/assets/SKILL.md)
- **Description:** Pipeline contract for a project's imagery: plan the bill of materials, generate the masters, conform them into delivery files. Routes the three steps to the skills that execute them - collection dissects a page or reference into BOM.md, bom/<page>.md and bom/style.md and writes the prompts; the generate skill produces masters; resources probes a sheet, splits it and fits each slot to its delivery spec with a verification report. Fixes the order and the shared key: one slot id across BOM row, prompt, raw render and delivered file, so nothing is re-derived by hand. Pages marked no-images skip the pipeline. Use when asked what images a page needs, to plan or run an image program end to end, to turn a generated sheet into project assets, or to decide which skill handles a step. Triggers: assets, image pipeline, BOM, image plan, generated sheet, conform, split a sheet. Not for one prompt (generate), pure file work (resources), or writing illustration prompts and style canon (collection).
- **Use-case:** The user asks what images a page needs, wants a project's imagery planned, generated and delivered end to end, needs a generated sheet turned into project asset files, or asks which skill owns a step. Also /assets.
- **Usage:** `/assets [the page, image plan, sheet or pipeline step]`

---

#### `bleed`

- **Path:** [`Groups/Design/bleed/SKILL.md`](./Groups/Design/bleed/SKILL.md)
- **Description:** Convert a web UI between layout registers - full-bleed page, framed cards, or hybrid - and fix the "document inside an app" smell where a page wraps itself in a max-width card. Use when a page or mockup "looks like sections inside a page", when asked to make content take the full page or full width, remove the outer box or card around everything, match the layout grammar of sibling files, stop nesting cards, or conversely to contain a page into cards; also when reviewing a screenshot that shows a narrow centered column with dead margins.
- **Usage:** `/bleed [page|framed|hybrid] <file>`

---

#### `collection`

- **Path:** [`Groups/Design/collection/SKILL.md`](./Groups/Design/collection/SKILL.md)
- **Description:** Method for a project's generated imagery: dissect a reference or page set into a bill of materials (BOM), fix the style canon once, write the prompts, plan generation economically. Per page, every visual is classified (generated / reused / stock / icon) with slot id, role, master and a delivery spec (size, aspect, format, quality, DPR); pages needing no images are marked no-images in BOM.md. Style DNA, character canon, hard rules (no text, no logos) and soft rules live in one file, copied verbatim into every prompt; prompts use fixed sections and chain from a style anchor. Economy: one sheet cut into N slots versus N renders - compare required master (delivery px x max DPR) against cell size. Regenerate only what is missing. Use for an image collection, illustrations for app screens, a consistent set of generated art, 'make images for onboarding', planning a page's images, or normalising a generated sheet. Not for one prompt (generate), stock photos (fahlwy), file work (resources).

---

#### `denoise`

- **Path:** [`Groups/Design/denoise/SKILL.md`](./Groups/Design/denoise/SKILL.md)
- **Description:** Transforms crowded, noisy, visually overwhelming UIs into calm, readable, professional interfaces that are easier to use, not just nicer to look at, at one of three intensities: lite (type/spacing in place), medium (redistributes content, designs forms and states), ultra (full re-theme, re-structure, re-derived information architecture and interaction layer). Use when someone shares an existing UI — HTML/CSS, React, Vue, a screenshot, a mockup, an admin panel, a dashboard — and asks to make it cleaner, more readable, less cluttered or noisy, more professional, easier on the eyes, or denoise/calm; or names a lite/medium/ultra pass. Also handles whole-codebase work: rolling a pass across many pages with a generated map and an audited ledger, verifying nothing broke against a real pre-redesign build, and grading which mode was actually delivered so an Ultra request is never quietly answered with a re-skin. For variations before a rollout, use diverge. Refactor/redesign only, not from-scratch. Framework-agnostic.

---

#### `diverge`

- **Path:** [`Groups/Design/diverge/SKILL.md`](./Groups/Design/diverge/SKILL.md)
- **Description:** Previews genuinely different design directions for an existing UI before committing a whole project or batch of pages to one of them. Two commands: /diverge taste [n] builds n complete, genuinely different directions and delivers them side by side in a picker page whose "Use this one" button copies a ready-to-paste prompt; /diverge snippet proves one direction on a single representative file with mockup data, never touching source, in a like/dislike loop. Use when someone wants to see real options before a redesign rollout, asks for variations, directions, tastes, or design options side by side, says "show me a few different takes before we commit", names /diverge taste or /diverge snippet, or wants a fast go/no-go proof of a redesign feel on one file. Directions must differ on structural judgment calls, not paint. Not for applying one decided redesign pass (denoise or any redesign skill does that), and not from-scratch design.
- **Use-case:** The person is about to commit a project or many pages to one redesign direction and wants real options first, asks for variations/directions/tastes side by side, or wants a one-file mockup proof before rollout.
- **Usage:** `/diverge [taste [n]|snippet] <file-or-project>`

---

#### `pages`

- **Path:** [`Groups/Design/pages/SKILL.md`](./Groups/Design/pages/SKILL.md)
- **Description:** A product's complete page universe: one skill, three modes, ONE artifact. /pages main plans the core-screen inventory, pruning a 492-row 30-discipline candidate catalog against project evidence, splitting mixed concerns and recording redirects and exclusions with reasons. /pages secondary writes the trust documents (ToS, Privacy, Cookies, Contact, Status, DPA, delete-account; one reference per type, scale- and phase-gated - launch set now, the rest on triggers - one canon per document, never invented legal facts). /pages complementary designs the conditional screens that fire only on a trigger, the app running normally without them (onboarding, transaction outcomes, HTTP errors, session gates, maintenance, access gates, token handoffs, callback relays). Every page registers in PAGES.md by kind; nothing a product lacks gets invented. Triggers: plan my pages, legal pages, onboarding flow, error page, callback URL. Not for designing/building screens (prototype, impeccable) or implementation order (planner).
- **Use-case:** Any question of which pages a product has, needs, or must not have — core inventory, trust documents, conditional screens — or when a change touches PAGES.md territory.
- **Usage:** `/pages [main|secondary|complementary] [plan|list|new <x>|audit]`

---

#### `parity`

- **Path:** [`Groups/Design/parity/SKILL.md`](./Groups/Design/parity/SKILL.md)
- **Description:** Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually renders on a real device/emulator, for any UI framework. Covers the full pipeline (mockup + on-device capture, frame/chrome-noise normalization, similarity scoring, regional diagnosis) and an autonomous convergence loop that iterates capture→compare→diagnose→fix→rebuild without pausing for check-ins until threshold is met. Also covers: inventorying ItC (interact-to-change) components like dropdowns/drawers/modals and forcing their states via query params; dummy/placeholder mockup data needing fixtures so content mismatches don't masquerade as layout bugs; transition/animation ('smoothing') parity beyond static screenshots; and navigating past obstacle screens (splash/onboarding/permissions) without getting stuck. Use for pixel/visual parity with a design, automated visual regression, or an agent iterating to a similarity score. Triggers: parity, visual parity, pixel parity.

---

#### `resources`

- **Path:** [`Groups/Design/resources/SKILL.md`](./Groups/Design/resources/SKILL.md)
- **Description:** Resource files for any platform: images, icons, fonts, audio, video, documents, color values - the files, not the systems that serve them. Fourteen tools: recolor (family or picked pixel), convert/fix-extension, rotate/flip/scale/resize/crop, favicon/app icon sets, OG images, splash screens, optimization with before/after sizes, CDN localization (browser-UA fonts, sniffing), inventory (duplicates, unused, external URLs, sizes), CSS Color 4 + WCAG contrast, a Bun.Image variants/ThumbHash script, and conform - probe a generated sheet, split it into slots fitted to a BOM delivery spec (size, aspect, DPR), review the files on a checkerboard with alpha-edge facts, then verify each one. Audio/video use ffmpeg; renames are shell moves + reference updates. Rules: names, brand-vs-content, formats by purpose, ask-first splash choices. Triggers: favicon, icons, splash, OG, recolor, convert, optimize, localize, color, rename, unused resources, conform, split a generated image, sprite sheet, probe sheet.
- **Use-case:** The user asks to create, convert, transform, recolor, organize, rename, localize or optimize project resources (images, icons, fonts, video, splash/loading screens, favicons, OG images), to split and fit generated images to their delivery spec, or to audit a resource folder for duplicates and unused files. Also /resources.
- **Usage:** `/resources [the resource, folder or task - icons, favicon, splash, og, optimize, localize, inventory, rename, recolor, convert, transform, conform]`

---

#### `scss`

- **Path:** [`Groups/Design/Style/scss/SKILL.md`](./Groups/Design/Style/scss/SKILL.md)
- **Description:** SCSS/Sassy CSS best practices and coding guidelines for maintainable, scalable stylesheets

---

#### `stateful`

- **Path:** [`Groups/Design/stateful/SKILL.md`](./Groups/Design/stateful/SKILL.md)
- **Description:** Derive every state a user-visible screen can enter, then implement the approved ones — pending, empty, stale, partial; provider down, degraded, throttled, maintenance; no connection at launch; extreme latency; expired session; refused entitlement; unknown values; device suspended, killed, storage-full; races; integrity and breach conditions. Platform-neutral: web, mobile, desktop, terminal, kiosk, embedded, any stack, and prototypes. Never a fixed checklist: states derive from the screen's own dependencies through nine condition axes, each candidate passes four evidence gates and a severity triage, and unknown input gets a designed rendering rather than the happy path. Use for "handle all the states", "what states can this screen have", "make it state-complete", "audit for missing states", "this breaks when the network is slow or gone", "it hangs or shows nothing when the server is down", "/stateful <file|screen|app>". Not for polishing existing states, from-scratch screens, or headless state machines.

---

#### `styleup`

- **Path:** [`Groups/Design/Style/styleup/SKILL.md`](./Groups/Design/Style/styleup/SKILL.md)
- **Description:** Turns an existing project's styling into a maintainable, professional system on any stack: inventories every hardcoded or duplicated style, works inside the styling system the project already uses (or makes one evidence-based build-vs-library decision only when it has none), builds a semantic token layer as the single source of truth, migrates all consumers in pixel-safe slices, and locks the result with no-hardcoding guards plus before/after parity evidence. Use when asked to styleup/style-up a project, make styles maintainable or professional, centralize colors/typography/ spacing/radii, remove hardcoded or duplicated styles, introduce design tokens, or decide whether to adopt a styling library versus staying framework-native.

---

#### `styling`

- **Path:** [`Groups/Design/Style/styling/SKILL.md`](./Groups/Design/Style/styling/SKILL.md)
- **Description:** Platform-neutral rules for writing NEW styling on any stack (HTML/Web, Blazor, MAUI, Qt): per-module stylesheets, no monolith; role-named tokens as single source of truth; styling as a chain of layers, downward-only imports (values -> tokens -> mixins/utilities/functions -> composed styles -> module scope; layer count is the project's call, not this skill's); expressive names over ambiguous ones - the ambiguity trap: do not call everything 'card' and patch it per site; thin bases fine, expressive layers chosen not mandated; module classes are file-private; conditional/runtime discipline: states as class mappings or state attributes, runtime values as dynamic tokens, inline only for calculated numbers; composition helpers (joiner, merge-on-conflict, variant registry). Use when styling structure is yours, when it sprawls into inline dumps or built class strings, or asked how to organize CSS/XAML/QML. Not for retrofitting projects into tokens (styleup), redesign (denoise), or component galleries (components).

---

### Favor

#### `design-taste-frontend`

- **Path:** [`Groups/Favor/design-taste-frontend/SKILL.md`](./Groups/Favor/design-taste-frontend/SKILL.md)
- **Description:** tasteskill 2.5.1, the anti-slop frontend skill. Builds professional company websites at the level of figma.com and x.ai: plain copy in a voice of its own, one system, one section per screen, equal edges, real photographs and real product UI (licensed stand-in photographs when the client has none; a product render only when the brief asks for 3D), a hero entrance and one or two dealt moments on every page, shader effects and scenes only on tech, gaming and software pages, quiet micro-interactions, and a checker and finish gate that enforce it in a real browser. Use this whenever you build, design, redesign, restyle, polish or review a landing page, company, product, shop, cafe, hotel, studio, SaaS, AI, developer-tool or game site, as static HTML/CSS or inside an existing React, Next.js, Vue, Svelte, Astro or Tailwind project, or when the user says a page looks generic, templated or "AI-made".

---

#### `taste`

- **Path:** [`Groups/Favor/taste/SKILL.md`](./Groups/Favor/taste/SKILL.md)
- **Description:** Smart design router skill that clarifies user intent to route to either ui-taste (apps/dashboards/iOS) or design-taste-frontend (landing pages/showcases).

---

#### `ui-taste`

- **Path:** [`Groups/Favor/ui-taste/SKILL.md`](./Groups/Favor/ui-taste/SKILL.md)
- **Description:** Give your coding agent better UI taste. Build and polish web and iOS interfaces with Uizze's anti-ui-slop playbooks and optional real-product references. Use for UI design, implementation, redesign, critique, or a final visual review in Claude Code, Codex, Cursor, or Copilot.

---

### Files

#### `document`

- **Path:** [`Groups/Files/document/SKILL.md`](./Groups/Files/document/SKILL.md)
- **Description:** Markdown documents: five jobs, the default entry whenever a task produces, restructures, shortens or rewords a document - self-invoked, not only when /document is typed. WRITE a new document (normal/comprehensive/concise) matching the user's purpose and evidence rules. REORGANIZE a messy doc set into one-concern-per-file with a README per directory as the map. SEPARATE the subject the user names into its own readable document. SUMMARIZE without losing meaning (normal/extreme): TL;DR, executive summary, digest, recap. REPHRASE sentence by sentence - improve grammar, flow and word choice only inside each sentence, preserving structure, boundaries, claims, certainty and the author's voice; return the reworded text alone. Triggers: 'write a report about X', 'refactor these docs', 'separate X from Y', 'summarize this', 'rephrase this'. Each job loads only its own method; modes are named in the request. Restructuring pair: separate first, then reorganize. Not for code, slides, or spreadsheets.
- **Use-case:** Any task that produces, restructures, shortens or rewords a Markdown document — writing one, reorganizing a doc set, giving a named subject its own document, summarizing/condensing a source, or rephrasing sentences without touching structure — whether or not the user names this skill.
- **Usage:** `/document [what to write, the docs to reorganize, the seam to cut, the source to summarize, or the text to rephrase]`

---

#### `pdf`

- **Path:** [`Groups/Files/pdf/SKILL.md`](./Groups/Files/pdf/SKILL.md)
- **Description:** Use this skill whenever the user wants to do anything with PDF files, in either of its two modes. READ mode: extract text from a PDF into .txt with scripts/pdf_extract.py - page ranges, layout vs raw engines, page markers, cleaning, a quality report (textless pages, font damage), and export as numbered module files (e.g. --module-lines 200) with a manifest, so long documents can be read selectively instead of dumped into context; also tables, images, OCR for scans, metadata, encrypted files. WRITE mode: create new PDFs, merge, split, rotate, watermark, fill and validate PDF forms, encrypt/decrypt, fix glyphs. If the user mentions a .pdf file - to read it, to search it, or to produce one - use this skill.

---

#### `postmortem`

- **Path:** [`Groups/Files/postmortem/SKILL.md`](./Groups/Files/postmortem/SKILL.md)
- **Description:** Blameless, self-contained incident documents: postmortem, incident report, RCA, bug write-up, "what went wrong". Modes: file (default) or folder. FILE: one Markdown doc, commands quoted inline, repo files cited by path + commit SHA. FOLDER: a package named "Postmortem - [Component] - [What broke] - [YYYY-MM-DD]" (sanitized) with index.md, the bundled reader index.html, and evidence/, investigation/, fix/, verification/ holding every artifact copied in, SHA256-indexed, secrets redacted, plus a Files and Artifacts Index and a "How we reached this conclusion" narrative with dead ends, so the folder alone re-runs the reasoning. Its 18-section template covers symptom, build and environment traceability, exposure window, timing interval, blast radius, causal chain, cause category, investigation log, fix, evidence level V0-V5, verification, rare-bug soak math, prevention with owner/due/ticket/DoD. Full SHAs, UTC timestamps, quantified claims, never "human error" as a root cause. Prose follows the /document skill.
- **Use-case:** The user asks for a postmortem, incident report, RCA, root-cause analysis, bug write-up, "what went wrong", or a blameless review of an outage, crash or regression.
- **Usage:** `/postmortem [file|folder] [one-line incident hint]`

---

#### `summarize`

- **Path:** [`Groups/Files/summarize/SKILL.md`](./Groups/Files/summarize/SKILL.md)
- **Description:** Use this skill whenever the user wants to shorten content without losing its meaning — summarize, condense, distill, recap, abridge, or extract key points from an article, report, transcript, thread, email chain, conversation, or document, including TL;DR, executive summary, abstract, digest, or brief requests. Trigger even on a bare "summarize this" with no further instruction, and when the user wants the shortest/most extreme version. Also trigger for conversation/Q&A summarization with role-specific instructions ("keep my questions, summarize the agent's answers") and for requests specifying a custom output structure ("put questions on top under headers, answers below") — this skill decides whether the request preserves the source's shape or needs a new one. Not for line-level copyediting/proofreading at the same length — see process-business-writing.

---

### Generalize

#### `polyglot`

- **Path:** [`Groups/Generalize/polyglot/SKILL.md`](./Groups/Generalize/polyglot/SKILL.md)
- **Description:** Teaches AI agents how to design and author universal, general, and language-agnostic agent skills, and how to write balanced, representative polyglot code examples. Use when creating or refactoring agent skills, coding standards, templates, or architectural specifications.

---

#### `revoke`

- **Path:** [`Groups/Generalize/revoke/SKILL.md`](./Groups/Generalize/revoke/SKILL.md)
- **Description:** Sanitise an artifact by revoking what ties it to a specific project, person, customer or deployment: the substance survives, the identity does not. Use when a report, spec, config, log or screenshot must leave its origin: inventory what is specific (names, ids, endpoints, secrets, dates, paths), choose per item [redact] [pseudonymize] [generalize] [aggregate] [keep] under one substitution map, verify nothing leaks (token/entropy sweeps, metadata, the map), and check the argument survives. No findings, no changes: with nothing identifying, the artifact ships byte-identical with a clean report; cosmetic rewording is editing, not revocation. Modes: /revoke partial masks values to fragments (A****) for owner-view screens - never secrets; /revoke image paints opaque blocks over visible identifiers (blur is not revocation), strips metadata. Not polyglot (stack-neutral); revoke is identity-neutral. Never to hide wrongdoing, evade a legal hold, strip safety notices or erase accountability; the original stays intact.
- **Use-case:** The user asks to sanitise, redact, anonymise, de-identify, genericise or "remove anything that identifies our project/customer" from a document, passage, config, log, screenshot, image or case study before sharing or reusing it. Also /revoke, /revoke partial (owner-recognition masks), /revoke image (pixel-level redaction of a picture).
- **Usage:** `/revoke [artifact or path] + [where it is going] | partial: [values] + [who will see them] | image: [image path] (+ regions, else revoke all visible identity)`

---

### Git

#### `branch`

- **Path:** [`Groups/Git/branch/SKILL.md`](./Groups/Git/branch/SKILL.md)
- **Description:** Plans, names, and safely runs Git branches, including repositories several agents share. Three situations differ: alone; beside other agent processes (a second session or tool, e.g. Claude Code + Codex) sharing one .git; and your own subagents in this process. Where sessions can collide, the claim is a session-scoped ledger plus an atomic ref that git refuses to clobber - acquire, release, never steal; collisions resolve by renaming, splitting scope, or serializing. Ask-first where no standard exists, after detecting what the repo answers: naming, PR-on-origin versus local merge, whether a fix needs its own branch or may ride the feature flow, whether agent authorship is disclosed (a Co-authored-by trailer, an agent segment in the branch name) or deliberately absent, branch lifetime, who integrates. Permanent policy goes into AGENTS.md (agents-md owns it); session choices stay in the claim file. Covers worktree isolation, integration order, merge-tree conflict pre-flight, destructive-op gates.
- **Use-case:** The user asks how to branch, which branch to create, how to name branches, how to run several agents or sessions on one repo without collision, whether to use worktrees, what a branch strategy should be, or is about to create/merge/delete branches in a repo shared with other agents.
- **Usage:** `/branch [plan | name | worktree | claim | policy] [topic]`

---

#### `commit`

- **Path:** [`Groups/Git/commit/SKILL.md`](./Groups/Git/commit/SKILL.md)
- **Description:** Professional git commits, in two modes. GUIDE (default, writes nothing): detect the repo's incumbent convention from its history, split work into atomic units, stage with git add -p, write an imperative subject that survives git log --oneline, a what/why body, readable trailers - plus scenario calls: when to commit, gray zones, a fix interrupting a feature, wip vocabulary, squash or not, repairing history behind a backup ref. INIT (/commit init): co-author this repository's written commit discipline - read what the history and existing tooling do, ask the eight questions the repo cannot answer (shape, types, budget, named branches, ticket keys, body policy, agent authorship (trailer + branch segment), enforcement), draft one document, merge never clobber existing prose, install nothing: no hook, no git config, no CI file - enforcement is the maintainers' choice. Rails: no --no-verify, no committing unread files, no claiming unrun tests, no rewriting pushed history.
- **Use-case:** The user asks to commit, to write or review a commit message, to split work into professional commits, or to tidy local history. Init mode when they ask to set up commit conventions here, write down the project's commit rules, or document a commit policy. Also /commit, /commit init.
- **Usage:** `/commit [init] — or a hint like 'split into atomic commits'`

---

#### `diffs`

- **Path:** [`Groups/Git/diffs/SKILL.md`](./Groups/Git/diffs/SKILL.md)
- **Description:** Read git diffs like evidence, not text: triage huge diffs and search diff history. Establishes the right baseline (A..B vs A...B, worktree/staged/HEAD, merge base), surveys a change set (stat, name-status, renames, generated/binary/whitespace), reads hunks correctly (arithmetic, function context, word-diff, color-moved), spots risk (removed error handling, changed defaults, boundaries, mode bits, dependency and migration changes, secrets), and searches with pickaxe -S/-G, message-level --grep, log -L, git grep at a revision, range-diff, remerge diffs. Topic dossier (--topic): messages + code + history in four budgeted channels, never a -p dump. Also answers "is this diff truthful?" - message vs changes, tests present, debug leftovers, partial staging, scope creep. Ships scripts/diff_survey.py (deterministic triage, --json, --fail-on, budgets). Use for reviewing PRs or commits, investigating what a commit did, hunting where a string was added or removed, or when a diff is too large to read.
- **Use-case:** The user asks what a commit/PR/branch changed, asks to review a diff, points at a huge or confusing diff, asks where a string or behaviour was introduced or removed, or a change must be verified against its description.
- **Usage:** `/diffs [range|staged|worktree|merge <sha>] [path...]`

---

### Prospecting

#### `mine`

- **Path:** [`Groups/Prospecting/mine/SKILL.md`](./Groups/Prospecting/mine/SKILL.md)
- **Description:** Runs a deep, budgeted, multi-source dig to understand not just what a class of thing looks like but WHY - and, when asked to decide, runs the options through a fair trial and ranks them. Three modes: read-mining (census repos, docs, papers, datasets, talks and chase their why) ends in a distilled document; run-mining (one identical hard-case trial per candidate) ends in a ranked verdict with a score table; case-mining (a topic's distinct concrete situations, each attested or labeled derived) ends in a coverage-mapped catalog where the count is a target, never padding. The user can direct the how ("/mine this PDF, 100 pages per subagent" is honored literally). Long artifacts get a noise-and-density map first; reach pipelines (PDF to text, OCR, transcription) are gated on one real sample. Resumes from plan.md. Trigger on "/mine", mining a topic, resuming a dig, "find the best 5 libraries for X and test them on hard cases", or "enumerate the cases of X". Approve a verified source plan first.

---

#### `smelt`

- **Path:** [`Groups/Prospecting/smelt/SKILL.md`](./Groups/Prospecting/smelt/SKILL.md)
- **Description:** Turns a completed mine run — or any research corpus of checkpoints, distillations, plans, and witness notes — into a durable, evidence-linked knowledge base another agent can consume. Trigger on "/smelt", "smelt the mine", "turn the mine for X into a knowledge base", "compress the mining folder", "make this research reusable", "build a knowledge base from these files", or any request to preserve everything learned across many large files without losing knowledge. Takes a source folder and a destination; works file by file into a running knowledge file, then reconciles folders globally. Verifies every reference URL the run left behind — exhaustively, never a sample — recording status and handling dead links, and reports each source file's smelt yield (what share of its knowledge entered the base) sorted top yield to bottom. Writing is free-form — no template — and every claim stays traceable to its source. Never summarizes sources away, never deletes a finding, always keeps the evidence pointer.

---

### Search

#### `dig-binary`

- **Path:** [`Groups/Search/dig-binary/SKILL.md`](./Groups/Search/dig-binary/SKILL.md)
- **Description:** Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracing, network protocols, native binaries (PE, ELF, Mach-O), bytecode (JVM, Dalvik, Python, .NET), archives (ZIP, JAR, APK, TAR, ASAR), and local data stores. Use when source code is missing, obfuscated, or partial and internal models, APIs, hidden behaviors, or error causes must be uncovered.

---

#### `investigate`

- **Path:** [`Groups/Search/investigate/SKILL.md`](./Groups/Search/investigate/SKILL.md)
- **Description:** Investigate local files, codebases, datasets, and external Agent Skills. Use for high-precision searches across heterogeneous formats, diagnosing unfamiliar architectures, inspecting or comparing Skills from SkillsMP, GitHub, and other public sources, temporarily using or remixing external Skills, and synthesizing evidence into structured reports. Does not install external Skills unless explicitly requested.

---

#### `search-deeply`

- **Path:** [`Groups/Search/search-deeply/SKILL.md`](./Groups/Search/search-deeply/SKILL.md)
- **Description:** Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems problems. Use when the user requests very deep research, production-grade architecture analysis, lifecycle design, formal state machines, ownership models, race-condition handling, resource pools, platform constraints, failure-mode analysis, anti-patterns, or any study that must go far beyond shallow answers. Triggers include deep research, architecture study, implementation-oriented, formal state machine, ownership analysis, failure modes, anti-patterns, decision matrix.

---

### Special

#### `display-to-user`

- **Path:** [`Groups/Special/display-to-user/SKILL.md`](./Groups/Special/display-to-user/SKILL.md)
- **Description:** Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "let me see", or "give me a link to see" what you've done to their project — the current state of files, or just the changes so far. Also trigger this if the user asks for a way to visually browse the project tree, preview a README or HTML file you produced, or share a live view of the repo with someone else. This spins up a local web viewer (file tree + git status + file preview) and tunnels it with ngrok so the user gets a real clickable URL back, rather than you pasting file contents into chat.

---

#### `tray-inspection`

- **Path:** [`Groups/Special/tray-inspection/SKILL.md`](./Groups/Special/tray-inspection/SKILL.md)
- **Description:** Comprehensive workflow and Win32 inspection procedures for Windows system tray items, including listing active tray icons, reading explorer toolbar memory, extracting native HICON bitmaps/PNGs, capturing high-DPI tray snips, and diagnosing tray state or badging issues.

---

#### `viz-planning`

- **Path:** [`Groups/Special/viz-planning/SKILL.md`](./Groups/Special/viz-planning/SKILL.md)
- **Description:** Use this skill when planning, designing, or architecting a data visualization system, dashboard, chart component, reporting tool, or analytics app — anything built once and used repeatedly, or involving real complexity (unstable schemas, growing/streaming datasets, multiple sources, many categories, outliers, filtering or persisted state). Walks through data source stability, schema evolution, volume, semantics, chart selection, grouping/aggregation/outlier handling, filtering and state architecture, layout, and configuration precedence BEFORE any chart gets built, so the wrong visualization or a fragile pipeline doesn't get picked by default. Trigger even when the user just says "help me build a dashboard for X" or "I need to visualize this data" without naming any of these specifics — the point is surfacing considerations they haven't thought of yet. Do NOT use for one-off requests like "chart this CSV" or "plot Q3 revenue" against already-clean, already-understood data — just chart it directly.

---

### Talk

#### `chat`

- **Path:** [`Groups/Talk/chat/SKILL.md`](./Groups/Talk/chat/SKILL.md)
- **Description:** Relaxed conversation mode the user starts and ends. The user wants to talk something through, not get work done: the agent listens, answers in short plain sentences, follows their lead, and changes nothing. Invoked only by the user with /chat [topic]; never self-started, and never entered by the agent because a conversation happens to sound casual.
- **Use-case:** Never. This skill is user-invoked only - /chat, /chat with me about <topic>. The agent must not start it on its own.
- **Usage:** `/chat [topic, optional]`

---

#### `explain`

- **Path:** [`Groups/Talk/explain/SKILL.md`](./Groups/Talk/explain/SKILL.md)
- **Description:** Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-day (a security flaw nobody has fixed yet)". Use this whenever the user asks you to explain, simplify, clarify, break down, or "explain like I'm new to this", or says a previous answer was too technical, confusing, full of jargon, or hard to follow. Also use it proactively whenever your own answer is about to use a specialized or industry-specific term (security, finance, medicine, law, engineering, programming, etc.) and the user hasn't signaled expert familiarity with that field.

---

#### `grill-me`

- **Path:** [`Groups/Talk/grill-me/SKILL.md`](./Groups/Talk/grill-me/SKILL.md)
- **Description:** Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.

---

#### `honest`

- **Path:** [`Groups/Talk/honest/SKILL.md`](./Groups/Talk/honest/SKILL.md)
- **Description:** Answers honestly instead of agreeably, and says what it understood before it judges anything. Use when the user asks 'can this really work', 'will this work', 'is this our best solution', 'answer me honestly', 'be honest with me', /honest, or wants a second opinion that is not their own opinion returned warmer. Order: restate the request in its strongest readable form; if the answer turns on something unstated, name it, answer conditionally, ask the one question; then the verdict, the reason, the cost nobody mentioned, and confidence where it matters. No opening flattery, no compliment sandwich, no ritual pushback, no fixed output template - if the idea is sound, say so briefly and stop. Disagreement is earned by the analysis, never performed. Holds the position under tone until new evidence or a better argument arrives, and concedes plainly when wrong. Applies to plans, designs, code, estimates, writing, and decisions. Not rude, not theatrical, not a substitute for evidence the agent could go and check.
- **Use-case:** The user asks whether something will really work, whether it is the best option, to be honest/blunt, or is getting agreement where they need a judgment. Also /honest.
- **Usage:** `/honest [the claim, plan, or decision to assess]`

---

#### `idk`

- **Path:** [`Groups/Talk/idk/SKILL.md`](./Groups/Talk/idk/SKILL.md)
- **Description:** Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't know", "not sure what I need", "I don't know how to explain it", "I can't put it into words", or similar explicit expressions of uncertainty about their own intent. This is NOT a general clarifying-questions skill — it only triggers on that explicit signal, not on every vague or underspecified request. Once triggered, it guides the user from a fuzzy feeling toward a clear, named intent through a calm, jargon-free conversation, optionally looking around the project's code and docs for clues, and ends with a plain-language review that maps what the user said onto the standard technical term for it.

---

#### `inquire`

- **Path:** [`Groups/Talk/inquire/SKILL.md`](./Groups/Talk/inquire/SKILL.md)
- **Description:** Build a rich, interactive question page (HTML) when the agent must get several important decisions from the user before or during work. Use it when there are 2 or more open questions whose answers change the project, design, architecture, or approach, and the user needs context, trade-offs, diagrams, or examples to choose well. Also use it when the available question tools are too limited (few questions, short text, no visuals). Triggers include "ask me questions first", "clarify before you start", "what do you need from me", planning a project, picking a tech stack or architecture, configuring something with real trade-offs. Do NOT use it for one quick question (ask in chat) or for questions whose answer can be inferred or looked up.

---

#### `judge`

- **Path:** [`Groups/Talk/judge/SKILL.md`](./Groups/Talk/judge/SKILL.md)
- **Description:** Acts as a fair, unbiased judge comparing two or more candidates (libraries, frameworks, tools, architectural approaches, vendors, design options, or any comparable set of choices). Use whenever the user wants a rigorous, evidence-based comparison or recommendation rather than a quick opinion — phrases like "which is better", "compare X vs Y", "help me choose between", "which should I use", "evaluate these options", or "judge these candidates". Always trigger this for "best library for X" or "X vs Y" style questions, even if the user doesn't say "judge" or "compare" explicitly. This skill runs many web searches per candidate across multiple dimensions (ecosystem health, maintenance activity, API design, popularity/adoption, usage patterns, code quality, performance, real-world evaluations) and demands honesty, bravery in stating a real verdict, and zero bias toward any candidate — it never pulls punches to be diplomatic and never recommends something just because it's popular or familiar.

---

#### `tldr`

- **Path:** [`Groups/Talk/tldr/SKILL.md`](./Groups/Talk/tldr/SKILL.md)
- **Description:** Answer in the shortest honest form instead of the usual full explanation — a word, a phrase, or one short sentence, with no preamble, hedging, or recap of what was done. Use this whenever the user says "tldr", "tl;dr", asks you to be brief, asks for a short answer, a one-word answer, "just tell me yes or no", "in short", "sum it up", or reacts to a normal-length reply with something like "too long", "just answer", "shorter", or "get to the point." Also use it any time the user is clearly asking a plain yes/no/status/confirmation question about something already discussed ("does this work now?", "did that fix it?", "is it done?") and a short answer would fully satisfy them — even without the word "tldr." Always trigger this even if the user's phrasing is casual or in a language other than English.

---

#### `walkthrough`

- **Path:** [`Groups/Talk/walkthrough/SKILL.md`](./Groups/Talk/walkthrough/SKILL.md)
- **Description:** Slow, step-by-step mode for working through a big or confusing problem (a project, a decision, a messy situation) at a steady, unhurried pace instead of jumping straight to a solution. Use this whenever the user explicitly asks to "walk through" something, says "let's go slow," "slow down," "one step at a time," or invokes /walkthrough — even if they don't use those exact words but are clearly asking not to be rushed. Explains things in plain, everyday language rather than heavy technical jargon, stays honest about trade-offs and difficulties instead of just telling the user what they want to hear, and pauses after each step to check in before moving on. Do not use this for quick questions or when the user wants a fast, direct answer — only when they've asked for the slow walkthrough pace.

---

### Viber

#### `adapt`

- **Path:** [`Groups/Viber/adapt/SKILL.md`](./Groups/Viber/adapt/SKILL.md)
- **Description:** Grows a project's own Viber version. Viber has fixed foundations, but no two projects walk the same path. When the journey needs a capability nothing covers, adapt proves the gap is real by walking a short ladder (a Viber or deck Skill, a project document, an installable Skill, a how-to recipe) and only when every rung fails creates a small project Skill, preferably an extension of the closest existing Skill. Every adaptation is recorded in the Viber section of the project's AGENTS.md. Never edits the fixed base, never runs what it creates, never creates a Skill where a document, rule or existing Skill would do. Triggers: 'we keep doing this by hand', 'no skill covers this', 'this project needs its own skill', 'adapt'. Not catalog authoring (skill-creator), fixed recipes (how-to-do), the rest of the rulebook (agents-md).
- **Use-case:** A need keeps returning that no Skill covers, the same instruction or correction is given repeatedly, a project domain has no owning Skill, a deck Skill should become part of this project's path, or the user asks for a project-specific Skill. Also /adapt.
- **Usage:** `/adapt [the gap or repeated need - or nothing, to scan the current work for gaps]`

---

#### `agents-md`

- **Path:** [`Groups/Viber/agents-md/SKILL.md`](./Groups/Viber/agents-md/SKILL.md)
- **Description:** Creates/audits AGENTS.md - agent rulebook: obligations+references not docs, rules/ per-topic referenced is the recommendation, inline stays valid; one owner per fact (brief+pointer). 19 sections: instructions; context fence value+REACH+docs-root MUST-ASK; how-to router (also owns exec/env/version policy); startup; delegation; privacy - cascade/gitignore; resourceful - local-first; authority - ask-per-session; version control - VCS tiers, parked-work, identity; ambiguity - Exact/Broad, weighty MANDATORY, 1-file records; golden rules - never-bend, violation-shaped; review - rulebook-violations lead, then named tasks; skills - per-skill rows; facts - corrections beat memory; before-between-after - per-phase rituals (read/dedup/type-check), current prompt overrides; voice - a register per surface user's own; sync blocks - multi-home meanings, a per-block table (site+line), meaning not letters, same-change duty; sections never deleted; maintenance - same-change+date. Writes ONLY AGENTS.md.
- **Use-case:** The user asks to create, restructure, or audit AGENTS.md (or an equivalent agent instruction file), to define how the main agent delegates to subagents, or says "agents-md this project". Also /agents-md.
- **Usage:** `/agents-md [project root, defaults to current repo]`

---

#### `architecture`

- **Path:** [`Groups/Viber/architecture/SKILL.md`](./Groups/Viber/architecture/SKILL.md)
- **Description:** Orchestrates and drafts an application's complete technical architecture documentation suite across its core pillars (language conventions, error handling, visual UI/interaction, relational/SQL data modeling, plugin and settings extensibility under the Open/Closed Principle, cross-platform multi-device mechanics, accessibility/sensory adaptation, and display/notation architecture (how values are expressed - precision levels, container fit, locale display, voice-typeface pairings)), invoking each specialized sub-pillar to author binding specifications into the project's documentation suite (<docs>/ or <docs>/architecture/).
- **Usage:** `/architecture <project root or app name>`
- **Sub-skills:** `accessibility`, `display`, `plugin`

---

#### `accessibility`

- **Path:** [`Groups/Viber/architecture/accessibility/SKILL.md`](./Groups/Viber/architecture/accessibility/SKILL.md)
- **Parent:** `architecture`
- **Description:** Orchestrates and authors an application's Accessibility Architecture specification into <docs>/architecture/accessibility-architecture.md. Moves beyond compliance checklists to design a comprehensive system spanning visual adaptation (high-contrast mode, eye-comfort presets like warm-cream/slate, user-tunable themes), typographic flexibility (multi-font selection, dyslexia-friendly fonts like Lexend/OpenDyslexic, fluid rem scaling without clipping), cognitive density tiers (compact vs standard vs spacious/verbose), comfort-reading modes, user autonomy and permission hygiene (contextual permissions, zero unexpected modals or popups), reduced motion, and assistive operability.
- **Usage:** `/accessibility [project root or app name]`

---

#### `display`

- **Path:** [`Groups/Viber/architecture/display/SKILL.md`](./Groups/Viber/architecture/display/SKILL.md)
- **Parent:** `architecture`
- **Description:** Orchestrates and authors an application's Display Architecture specification into <docs>/architecture/display-architecture.md — how values and text are EXPRESSED to users. Owns the notation spectrum (exact 4,982,317 vs grouped 5,000,000 vs compact 5M vs prose "nearly 5 million"; 500_000 stays source-side) and assigns a precision level per surface class; container-fit discipline (every display slot declares a character/width budget; overflow is a defect - fixed-width cards must never let a plain number strike through; fallback ladders and tabular figures); locale display rules via Intl/ICU (separators, Arabic-Indic vs Western numerals, calendars, Arabic plural categories, bidi isolation inside RTL text); and the voice-medium-typeface pairing — not every voice matches every typeface and vice versa, so each surface class declares its (voice register, typeface + figure style, notation level) triple coherently, always under the accessibility pillar's user-override precedence.
- **Usage:** `/display [project root or app name]`

---

#### `plugin`

- **Path:** [`Groups/Viber/architecture/plugin/SKILL.md`](./Groups/Viber/architecture/plugin/SKILL.md)
- **Parent:** `architecture`
- **Description:** Authors an application's plugin and settings architecture as one extensibility system. Settings and plugins are the same family: a closed host exposes a small extension contract, and an open set of contributions adds behavior without editing shared code. Use when designing, reviewing or refactoring settings pages, configuration catalogs, feature flags, per-tenant or per-platform preferences, extension points, module systems, or plugin hosts. Decides build-time versus runtime loading per axis, enforces an Open/Closed growth gate, and specifies descriptor data, contribution registries, layered composition, scope and storage, renderer shapes, consumer authorities, migration, versioning, trust and failure isolation.
- **Usage:** `/plugin [project root or app name]`

---

#### `commitments-md`

- **Path:** [`Groups/Viber/commitments-md/SKILL.md`](./Groups/Viber/commitments-md/SKILL.md)
- **Description:** Creates and maintains COMMITMENTS.md - the project's declared goals, priorities and trade-offs - or a small Commitments section in AGENTS.md when tiny. Premise: you cannot get the gold in every case. Some goals are mutually exclusive, some reinforce each other, and every priority has a price, a horizon (MVP vs later) and, where possible, a measurable bar. The skill never invents priorities: it collects the stated goals, maps which ones compete, asks which wins when they collide and what is sacrificed, marks the pairs that do not conflict so nobody pays for a fake trade-off, and records the hard constraints that are never traded. Placement: a small set goes into AGENTS.md; a big set (several dimensions, conflict tables, phases) becomes COMMITMENTS.md with a pointer from AGENTS.md. Triggers: 'what are our priorities', 'what should we sacrifice', 'is DX more important than perf here', 'define the trade-offs'. Not the idea itself (idea-md), not choosing the stack (techstack/thebest), not task planning (planner).
- **Use-case:** The user states competing goals, asks which priority wins, wants the project's trade-offs written down, or a project needs its commitments recorded/updated. Also /commitments-md.
- **Usage:** `/commitments-md [the project, or the goals/priorities to record]`

---

#### `glossary-md`

- **Path:** [`Groups/Viber/glossary-md/SKILL.md`](./Groups/Viber/glossary-md/SKILL.md)
- **Description:** Maintains one unambiguous project vocabulary in alphabetical letter blocks. Golden rule for what earns a block: the word as used here carries more than the dictionary sense - redefined or made-concrete ordinary words ('eye', 'minimal'), project coinages ('Melody' for a workflow), private-sense abbreviations, transliterations (Basr, بصر), Franco spellings, names/codenames. The project's own language is the canon, never English; bilingual terms show both forms together; article-led names file under the head noun ('Pit, The' under P). Each block: term (acronym spelled out), all forms, a 2-5 line meaning, 'Used in:' refs; keep identities generic - run 'revoke' before the glossary leaves the project. Lives in AGENTS.md's `# Glossary`, extracted to GLOSSARY.md when past the section budget. Self-invoke on learning, write the block in the same task; unknown means stay pending - never invent etymology. Also /glossary-md, 'add this term', 'what does X mean here'. Owns glossary content; agents-md owns AGENTS.md.
- **Use-case:** The agent encounters or uses a project-specific, foreign, transliterated, or redefined term for the first time; the user asks to record or look up a term; or terminology appears mixed across docs and needs one canonical list. Also /glossary-md.
- **Usage:** `/glossary-md [the term(s), or 'audit' to find mixed terminology]`

---

#### `idea-md`

- **Path:** [`Groups/Viber/idea-md/SKILL.md`](./Groups/Viber/idea-md/SKILL.md)
- **Description:** Turns a raw project prompt - any language, any mess - into IDEA.md: the project's complete idea document, readable by anyone, technical or not. First the idea's inspiration - a SET of sources: name every product it draws from (Medium, Dev.to…), what each contributes, its relationship (instance of / similar to / a slice of - mixed is normal), what is its own invention, and what it refuses per source. If the prompt never names one, the agent ASKS ('Is this project similar to X?') instead of guessing. Then plain prose: what it is, its audience and audience types, everything it includes and explicitly does not - written as free-form paragraphs, not fixed bullet sections. Unclear points become idea-level questions only (name, scope boundaries, access rules, editorial stance) - never platform, stack or hosting, which belong to later stages. No system analysis. Triggers: 'write the idea file', 'turn this into IDEA.md', a spoken project vision. Feeds the lifecycle's first phase.
- **Use-case:** The user describes a project idea - however rough, in any language - and wants it written as IDEA.md or a project overview, or asks to sharpen/update an existing IDEA.md. Also /idea-md.
- **Usage:** `/idea-md [the project prompt, or the path to update]`

---

#### `readme-md`

- **Path:** [`Groups/Viber/readme-md/SKILL.md`](./Groups/Viber/readme-md/SKILL.md)
- **Description:** Create, review, and update professional README files grounded in the actual project, never in assumptions or nonexistent features. Use when asked to write, fix, or refresh a README or project introduction. It inspects real sources (manifests, entry points, scripts, tests) before writing, separates implemented from planned, identifies the primary audience and picks a project-appropriate structure, asks the README voice/style (minimal / engineering / deep-DX / showcase / hybrid) with facts identical in any veoice, writes motivation without fabricated origin stories, uses only real commands verified against project config, refuses to fabricate badges/links/screenshots, offers motivation-phrasing options when positioning is open, asks only about intent-dependent decisions, and honestly reports what was tested vs reviewed. Preserves useful existing structure when updating; targeted edits; respects git state; draft mode. Triggers: readme, write/update the readme, README is outdated, document this project/repo.

---

#### `steering`

- **Path:** [`Groups/Viber/steering/SKILL.md`](./Groups/Viber/steering/SKILL.md)
- **Description:** Interactive documentation architecture and steering taxonomy skill. Transforms project requirements or legacy documentation into the Two-Tier Steering Taxonomy (.steering/ with perception/ [product, domain, capabilities, policy] and tech/ [stack, structure, function, doctrine, playbook], plus shared-plus-area splitting) and outside-taxonomy folders (features, reference). Operates in four gated phases with deep grill-me interviewing: (1) Contextual Discovery & Architectural Grill-Me Interview, (2) Ordered Placement & Passage-Level Role Analysis, (3) Distribution Plan Proposal & Approval Gate, and (4) Materialization & Index Synchronization. Use when asked to create or organize project documentation, apply the steering taxonomy, distribute requirements into .steering/, or migrate legacy docs.
- **Use-case:** The user wants to structure a project's documentation, distribute raw requirements across .steering/ and docs/, audit or migrate existing documentation into the Two-Tier Steering Taxonomy, or invokes /steering.
- **Usage:** `/steering [project path, raw requirements, or 'migrate']`

---

#### `system-md`

- **Path:** [`Groups/Viber/system-md/SKILL.md`](./Groups/Viber/system-md/SKILL.md)
- **Description:** Produces and maintains SYSTEM-COMPONENTS.md for a confirmed application: an architectural inventory of the functional building blocks - subsystems, services, engines, integrations, processors, data systems, infrastructure - each with purpose, responsibilities, in/out-of-scope ownership, inputs and outputs, error handling, configuration, related components, plus an ASCII relationship map and a "removing it would" summary table. Answers "what exists and what does each piece own" without reading all the code. Application-scoped: in a monorepo, one document per confirmed app, never one blended document across apps. Reusable-unit catalogs (UI builder blocks, and code units generally) belong to UNITS.md and are owned by units-md, not here; a button or card never appears in SYSTEM-COMPONENTS.md, a queue or rate limiter never in UNITS.md. Documents only - no code changes, no enforcement.
- **Use-case:** The user asks to document or map the system's components, "what subsystems does this app have", write or refresh SYSTEM-COMPONENTS.md, produce a component hierarchy and relationship map for onboarding, or needs one document per application in a monorepo.
- **Usage:** `/system-md [app path, defaults to the confirmed application]`

---

#### `units-md`

- **Path:** [`Groups/Viber/units-md/SKILL.md`](./Groups/Viber/units-md/SKILL.md)
- **Description:** Generates, refreshes, and audits a project's UNITS.md - the index of reusable units an agent reads before implementing, so it extends what exists instead of building a parallel one. Each entry is one row of facts: name, responsibility, where it lives (a path that must exist), what it depends on, what it replaces, its status, and the date the claim was checked; the header carries the four duties agents-md section 4 promises - read it in full first, reuse or extend with a stated reason, add a new reusable unit in the same task, and name who updates it. Built from the code, never from what docs claim or from plausible guesses. Use for "make a UNITS.md", "build the units index / component catalog", "we keep reinventing things that exist", "refresh UNITS.md", "does this already exist", when AGENTS.md section 4 points at a units file that does not exist, or before a fan-out so workers reuse instead of duplicating. Not a task list, not a backlog, not architecture documentation, and it never edits AGENTS.md itself.
- **Use-case:** The user asks to create, regenerate, refresh, or audit a units/component/registry index (often `docs/UNITS.md`); AGENTS.md's units duty points at a file that does not exist; work is being delegated in parallel and duplication is the risk; or the user complains that the project keeps rebuilding what it already has.
- **Usage:** `/units-md [generate|refresh|audit] [project root, defaults to current repo]`

---

### Video

#### `create-video`

- **Path:** [`Groups/Video/create-video/SKILL.md`](./Groups/Video/create-video/SKILL.md)
- **Description:** Turn a vague video request into locked, numeric direction, then lay out, verify and deliver a professional video project. Loads after the hyperframes entry point has routed the job and written BRIEF.md, and never competes with it or the hyperframes domain skills. Converts the brief into six independent axes — genre, pacing, visual, camera, editing, tone — plus aspect, duration, audio and scenes, each resolving to numbers: cuts per minute, seconds per arrival, transition milliseconds, easing. scripts/spec.py validates the spec and derives a build sheet with a per-scene arrival budget; scripts/scaffold.py writes the project structure and passes hyperframes lint; scripts/qa.py gates the render on measurable thresholds — dead air, all-clips-at-t=0, dwell, loudness, true peak, safe-zone ink — and motion promises are measured on rendered frames. Use for launch, demo, explainer, ad, promo, reel, short or hero video when direction must be pinned, a project structured, or quality proven.

---

#### `watch-video`

- **Path:** [`Groups/Video/watch-video/SKILL.md`](./Groups/Video/watch-video/SKILL.md)
- **Description:** Watch a video by reconstructing it from frames plus a timestamped transcript, measure how objects move through it, and write structured markdown notes. Downloads with yt-dlp, extracts auto-scaled JPEG frames with ffmpeg, gets captions (Whisper API fallback), then reads frames and speech together. scripts/motion.py compares two frames or a whole frame dump and reports which way the dominant object went as one of eight compass directions, in-place (including rotation about itself), or cannot-determine. Use when the user asks to watch, analyze, summarize, transcribe, take notes on, or explain a video, asks what is shown on screen at a given moment, asks where an object went, whether the camera pans, or about motion or editing style, wants a presentation or editing style replicated, hands over a YouTube/Vimeo/TikTok/X/Twitch/Loom/Instagram URL or a local mp4/mov/mkv/webm and asks about its content, or types /watch-video.
- **Usage:** `/watch-video <video-url-or-local-path> [section or question]`

---

### Standalone (repository root)

#### `animation`

- **Path:** [`animation/SKILL.md`](./animation/SKILL.md)
- **Description:** Animation meta-skill — a router, nothing more. Routes any motion request to the sub-skill that holds the functionality: `life` (UI motion — micro, component, transition, entrances and exits, hover/press feedback, group choreography (cast, stagger, sequence), scroll, springs, onboarding intros, discovery, prototypes, animation review), `ascii` (character/terminal motion — ASCII intro or loader, image or video to ASCII, plasma and wave fields, per-glyph cascades, Three.js AsciiEffect), `svg` (25 SVG/logo animation styles — chrome-liquid, draw-fill, elastic-entrance, neon, unroll and 20 more, with light/dark variants). Use when the user asks for animation, motion, transitions, a page or route to move, an animated logo, a retro/ASCII effect, or wants an interface to "feel alive", even if no one says the word animate. Adds no rules or standards of its own: those belong to the sub-skill performing the work. Out of this domain: static visual quality, component state galleries, mockup fidelity, real video.
- **Use-case:** Any motion or animation request — UI transitions, micro-interactions, animated logos/SVGs, ASCII or terminal motion — where the work must first be assigned to the right sub-skill. Also /animation.
- **Usage:** `/animation [life|ascii|svg] <command or style> <target>`
- **Sub-skills:** `ascii`, `life`, `svg`

---

#### `ascii`

- **Path:** [`animation/ascii/SKILL.md`](./animation/ascii/SKILL.md)
- **Parent:** `animation`
- **Description:** Build ASCII and character-based animations for web, terminal, or CLI. Use when the user asks for an ASCII animation, terminal intro or loader, image or video to ASCII, retro or hacker text motion, generative plasma or wave fields, character-art shaders, Three.js AsciiEffect, per-character cascade or domino effects, gradient or masked coloring on glyphs, or interactive ASCII. Always clarify the desired kind of animation with the user before coding. Supports Bun.Image as the preferred image pipeline when Bun is available.

---

#### `life`

- **Path:** [`animation/life/SKILL.md`](./animation/life/SKILL.md)
- **Parent:** `animation`
- **Description:** Designs, builds, reviews, and prototypes UI animation through three commands - micro, component, transition (one element, one visual unit, one state-to-state move with forward and back). Choreographs groups that move together - cast roles (lead/support/decoration/static), choose each pair's relation (together, overlap, sequence, carry, linked), no stagger on high-frequency UI, a timing table before code. Resolves vague requests like "make it feel premium" or "that bouncy thing when it opens", finds animation opportunities when the user does not know what to animate, proposes creative options as ASCII or HTML prototypes before touching production code, and reviews its own work against a craft bar. Use whenever the user mentions animation, motion, entrances, exits, intros, transitions, micro-interactions, easing, springs, scroll reveals, hover or press feedback, stagger, choreography, "feels mechanical", "too much going on", or wants an interface to feel more alive or polished, even if they never say "animate".

---

#### `svg`

- **Path:** [`animation/svg/SKILL.md`](./animation/svg/SKILL.md)
- **Parent:** `animation`
- **Description:** Animate a static, flat SVG logo or icon (solid-fill <path> elements) with one of twenty-five animation styles: chrome-liquid, draw-fill, loading-loop, elastic-entrance, rise, iris, neon, pulse, flip, comet, focus (rack-focus, blur resolves), crt (TV power-on + scanlines), chroma (RGB ghosts converge), mosaic (tiled mask dissolve), ripple (turbulence warps geometry), spark (a travelling spark reveals), engrave (emboss under raking light), grain (noise-threshold dissolve), tide (wavy waterline rises), polarity (inverting band sweeps), blinds (slats open), assemble (fragments fly in and lock), lantern (a wandering light reveals), pinwheel (wedges scale open), unroll (falls from a top hinge). Per-style signatures are in the SKILL.md table. Trigger when the user asks to animate a logo/SVG, names any of these effects, wants an existing treatment replicated on a new file, or needs light/dark theme variants. Always preserves fill-rule=evenodd so letterform holes (Arabic ص/ه, Latin a/o/e) never fill in solid.
- **Usage:** `/svg <style> <file.svg> (style: liquid|draw|load|elastic|rise|iris|neon|pulse|flip|comet|focus|crt|chroma|mosaic|ripple|spark|engrave|grain|tide|polarity|blinds|assemble|lantern|pinwheel|unroll)`

---

#### `avatar`

- **Path:** [`avatar/SKILL.md`](./avatar/SKILL.md)
- **Description:** Creates avatars without defaulting to one style. An avatar is a stand-in for an absent entity, so the skill first reads the request on four axes - medium, source of truth (reference image, name, seed, brief, photo), determinism, and parts-ness (one fixed picture vs a swappable system) - then picks an approach from a living catalog (data.csv). Full lifecycle: brief, approach choice, build, parts contract (boundary, anchor, independence, style, overlap, combination-tested - any medium), a universal debugging taxonomy, delivery, and mandatory catalog write-back so every new approach and built resource is recorded. One verified approach today - the modular explodable SVG rig (approaches/modular-svg-rig/) - as one row among many, not the identity of the skill. Use for a profile picture, character portrait, avatar family, swappable/mix-and-match parts, monogram/identicon/dicebear-style defaults, an avatar from a reference image, or how to build any of it.
- **Use-case:** The user asks for an avatar, profile picture, character or portrait to be created, varied, modularized, debugged or systematized - including "make me an avatar", "recreate this character", "give me 4 haircuts that swap", "default avatars for our users", "why does my part swap break the face".
- **Usage:** `/avatar [who/what it represents] + [source: reference image / name / brief] + [fixed vs swappable, sizes, count]`

---

#### `benchmark`

- **Path:** [`benchmark/SKILL.md`](./benchmark/SKILL.md)
- **Description:** Benchmark candidates on task-derived dimensions, in normal or ultra mode. Think first: which decision is being made (faster, more accurate, less memory) and how each will be measured - never a fixed list. Report the plan; ask the expected run time when unspecified: 5 min means ~10 iterations, an hour allows 100+. NORMAL measures the environment as-is (GC on, no warmup, no pinning) - what the deployment feels like; ULTRA fights noise for fairness (warmup, interleaved A/B/A/B, pinned core, locked frequency where permitted). Same language for every candidate, defaulting to the project's; say so when harness overhead rivals the work measured. Correctness gate first: a fast wrong answer is not a faster candidate. Measure in an isolated env (venv, temp prefix) - never global packages - and restore any system control touched. Reports median/p95 with spread and a noise floor, never a bare mean; 'inconclusive' when the gap sits inside the noise. scripts/bench_stats.py: stats, bootstrap verdict, budget math.
- **Use-case:** The user asks which of two or more approaches/libraries/implementations is faster, leaner, or more accurate; asks for a benchmark, a perf comparison, timings, or "is X better than Y"; or a measured number is needed to settle a design choice.
- **Usage:** `/benchmark [normal|ultra] [candidates] — or 'how long do I want this to run?'`

---

#### `caution`

- **Path:** [`caution/SKILL.md`](./caution/SKILL.md)
- **Description:** Informed-consent gate on the user's answers: screen every reply (chat, AskUserQuestion, command flags, hook or server input) for a decision whose cost the answerer may not know. Flags the guard, never the goal: storing data on a server, syncing devices or keeping history is the product and gets no card; storing it unencrypted, syncing it in plaintext, or keeping it forever without a cap is what gets flagged. Consequences are not only attacks - data loss, unbounded DB/memory/queue/log growth, irreversible actions, outward-facing contracts, removed safety nets. On a match it raises a visible DANGER mark in the chat, states the failure as a future postmortem headline with mechanism, blast radius and undo cost, names the cheapest adequate alternative, and re-asks once; then it accepts the answer, closes the loop in one line, and never re-opens it. Writes no files and keeps no log - the conversation is the record. A severity ladder keeps it quiet on recoverable calls and informed answers - not risk theater.
- **Use-case:** Any answer, choice, confirmation or instruction from the user that removes a protection, accepts unbounded growth or cost, is hard to undo, commits something outward-facing, or declines an option the agent offered (especially "no" to encryption, auth, backups, limits, validation, retention caps). Also when the agent is about to ask a yes/no question whose "yes" or "no" has a serious consequence.
- **Usage:** `/caution [the answer or decision to screen — or the question about to be asked]`

---

#### `close-topics`

- **Path:** [`close-topics/SKILL.md`](./close-topics/SKILL.md)
- **Description:** Guided, conversational, topic-by-topic technical specification: close one design area before opening the next. Use when a project has undecided architecture (scrapers, workers, pipelines, caching, data models, queues, storage, deployment) and the user wants to work through it sequentially - ask targeted questions with real options and trade-offs, collect the decision, write it into a specification document in the project's docs, update the index, then hand off to the next topic. Stops at design: no implementation until every agreed topic is resolved and the user says go. Standalone independent skill. Not for choosing a technology stack (techstack), not for deciding how to build something the agent already owns (dtb), not for planning a task list (planner), not for reorganizing or splitting docs (document).
- **Use-case:** The user wants to "work through the design topic by topic", nail down missing architecture decisions, resolve open technical questions before building, review what a project has not specified yet, or invokes /close-topics. Also when a spec is half-written and the gaps need closing one at a time.
- **Usage:** `/close-topics [topic to close, or 'what is still unspecified?']`

---

#### `compare`

- **Path:** [`compare/SKILL.md`](./compare/SKILL.md)
- **Description:** Write professional, well-reasoned comparisons between two or more subjects of any kind — technologies, files, projects, code modules, books, documents, biological processes, products, strategies, or any named options. Use whenever the user asks to compare, evaluate trade-offs, distinguish, or choose between things, including "which is better," "what's the difference," or "help me decide." Supports open-ended discovery of relevant aspects and dimension-based comparison on user-specified or researched criteria. Enforces real differentiators only, "why it matters" reasoning, independent research, graded quantitative claims, and neutral context-driven conclusions.

---

#### `design`

- **Path:** [`design/SKILL.md`](./design/SKILL.md)
- **Description:** Design work, one skill, four modes: design-md (author the project's canonical DESIGN.md: machine-readable tokens + human rationale, Google Labs design.md conventions - "/design DESIGN.md <file>"), playfile (throwaway design-review waves: self-contained linked HTML screens, URL-forced states, README dossiers - "/design a playfile"), prototype (interactive URL-driven prototype system: dev dock, component stories, per-component state trees, dedup guards - "/design prototype <screen>"), calibrate (extract the full design, visual and interaction DNA of a North-Star reference implementation and apply it to a project - "calibrate the /design of X to Y"). The router picks ONE mode and reads only its method.md. Triggers: DESIGN.md, design tokens, playfile, quick linked HTML mockups, prototype this, dev dock, stories gallery, calibrate design, match this app's design to a reference. Not for UI redesign passes, page inventories or mockup-to-device parity - those stay separate skills (denoise, pages, parity).
- **Use-case:** The user asks to author a DESIGN.md, run a wave of linked HTML review screens, build or extend an interactive URL-driven prototype, or calibrate a project's design to a reference implementation.
- **Usage:** `/design [design-md|playfile|prototype|calibrate] <target>`

---

#### `dont-stop`

- **Path:** [`dont-stop/SKILL.md`](./dont-stop/SKILL.md)
- **Description:** Forces the agent to keep working autonomously until the ENTIRE goal is truly finished, across all phases, with no mid-way stops, no "phase 1 done, ready for phase 2" check-ins, and no premature summaries. The agent only stops when (a) the whole goal is complete and verified, or (b) every technical option is exhausted and the only remaining step needs something from the outside world (e.g. real API keys, credentials, paid accounts, physical access). Use this skill whenever the user says "don't stop", "keep going", "finish it all", "do everything", "end to end", "full project", "until it's done", "autonomous", "don't ask me, just do it", or hands over a large, multi-phase, or long-running task, even if they never mention this skill by name. Also use it for any big build, migration, refactor, or debugging task where stopping early to report progress would waste the user's time.

---

#### `generate`

- **Path:** [`generate/SKILL.md`](./generate/SKILL.md)
- **Description:** Universal image AND video generation via RESTful providers (xAI, OpenAI, Gemini, KovAPI/NezhaGate) through registry data.csv: vendors and media types are data rows. Encapsulated per-media docs (media/image.md, media/video.md). Shared engine: concurrent --batch N with progress bar; --variations; --prompts-file; persistent context (--context new|<id>, seed with --context-seed); image inputs auto-encoded; video duration/fps; billing via usage.jsonl ledger; atomic download with results.jsonl for --salvage; keys masked. Triggers: generate, generate image, generate video, text-to-video, image-to-video, batch images, edit image, genimage, kovapi, nezha.

---

#### `learning-test`

- **Path:** [`learning-test/SKILL.md`](./learning-test/SKILL.md)
- **Description:** Write and run a "learning test" (term coined by Jim Newkirk, popularized by Robert C. Martin/Uncle Bob in Clean Code ch.8 "Boundaries") to empirically discover how a third-party library/framework/API actually behaves, instead of guessing, relying on stale training knowledge, or trusting docs that may be incomplete, outdated, ambiguous, or missing the exact case. Use whenever the Agent or the user is uncertain about real behavior/limits of an external dependency — "how does X actually behave", "what happens if...", "does X support...", "what's the limit of...", docs contradict themselves or don't cover the scenario, or before writing production code against an unfamiliar API. Also trigger on "write a learning test for X" or "figure out the limits of X". The test is small, real, executable code calling the actual API the way production code would, to characterize true behavior — not a mock or doc summary. Trigger this instead of guessing at or fabricating claims about library behavior.

---

#### `no-framework`

- **Path:** [`no-framework/SKILL.md`](./no-framework/SKILL.md)
- **Description:** Build Single Page Applications using NoF (No Frameworks) — Navigo (~4KB routing) plus a choice of small UI libraries (Preact by default, or VanJS / Nano JSX via `--ui`), no React/Vue/Angular runtime or mandated structure. Use whenever scaffolding a small-to-medium SPA that should stay framework-free. Requires verifying current library versions/API (chosen UI library, Navigo, @preact/signals or Nano Stores) before writing code — pinned versions, especially fast-moving ones like @preact/signals, can go stale; the `updated` field above is a staleness signal, not a guarantee. Any vanilla-JS-compatible library is fair game, including Tailwind/Sass (`--styler`) and Nano Stores for cross-library state; StyleX is excluded (tied to React). Covers scaffolding, state/signals/derive patterns, routing, components, rendering, debugging, and production paths (no-bundler htm, and Vite JSX). Not a fit for very large multi-page apps, large teams, or heavy animation needs — see "when to use".

---

#### `parallelize`

- **Path:** [`parallelize/SKILL.md`](./parallelize/SKILL.md)
- **Description:** Plan and run parallel work: the main agent decides in chat how to fan out a large or newly approved job, keeps the most sensitive work for itself, and hands bounded slices to subagents in waves that respect the harness concurrency cap. Use when the job is large enough to split, a plan was just approved, the user says "parallelize the work", "run agents in parallel", "fan this out", "use a worker pool", "split this across agents", "parallelize with staggering", or the agent sees three or more independent chunks. Core rules: no two agents write the same file; interfaces and naming decided before launch; the main agent never idles while subagents work; wave size follows dependencies and review load; a failed slice re-runs alone; staggering delays start times and never replaces dependency ordering. Not for deciding what to build (planner), writing the brief (subagent), or the pre-code gates (implement).
- **Use-case:** A job is large or an approved plan is about to be executed, or the user asks to parallelize/fan out/spawn workers — including "/parallelize with staggering <spec>" — also self-initiated when a task has several genuinely independent chunks.
- **Usage:** `/parallelize [the plan, task, or scope to parallelize] [with staggering <spec>]`

---

#### `personalize`

- **Path:** [`personalize/SKILL.md`](./personalize/SKILL.md)
- **Description:** Updates the user's GLOBAL agent instruction file (the personal AGENTS.md every project loads) so settled questions never get re-asked - an agent asking "which package manager?" when the global file answers is the idiot-agent this skill kills. Modes: "/personalize that i like bun and bunx" distills a statement into an enforceable preference line (behavior not transcript, explicit exception boundary); bare /personalize asks what to set, showing existing lines; "/personalize the section X in current AGENTS.md into global" promotes it - personal defaults up, project decisions stay, machine-specific routed out; copy unless told "move". Ladder: current prompt > project AGENTS.md (respects the global; overrides only explicitly) > global preference. Dedupe and refine over append; vague statements sharpened or refused, never written. Triggers: personalize, remember I always prefer, never ask me about X again, set my global default.
- **Usage:** `/personalize [preference statement | promotion: the section X in current AGENTS.md into global | empty to be asked]`

---

#### `pick`

- **Path:** [`pick/SKILL.md`](./pick/SKILL.md)
- **Description:** Pick the right PRODUCTION library for a development task instead of hand-rolling it - answers lookup questions from data.csv, a verified catalog across UI pieces, TypeScript correctness, data layer, backend runtime, testing, tooling and CLI. Core stance: a maintained production library beats self-implementation for anything an agent would otherwise build twice (vaul for bottom sheets instead of a DIY sheet; typia/zod for narrowing-validating instead of type gymnastics). Recommends one library with task, why, when_not, and alternatives; records only what was verified against npm/docs, never memory. Triggers: pick a library for X, what should I use for toasts/bottom sheets/drag-drop/validation/jobs, is there a library for this, don't hand-roll this, /pick. Not for deciding a tech stack (techstack), nor for inventing new categories the catalog does not cover without saying so.
- **Use-case:** A task calls for a component or mechanism a library probably already owns — before writing custom code for UI pieces, validation, state, fetching, jobs, CLI UX, tests, or tooling.
- **Usage:** `/pick [<task or keyword>|list|categories|refresh]`

---

#### `reveal`

- **Path:** [`reveal/SKILL.md`](./reveal/SKILL.md)
- **Description:** Competitive-intelligence investigation into how unique a project idea actually is: how much already exists, who built it, how well it works, and what genuinely differentiates the proposal. Splits the idea into search axes (never one query), discovers implementations across engines, code hosts, app stores, startup directories, communities, archives and native-language sources - obscure and defunct included - then investigates each competitor on ten dimensions, scores similarity 0-100 with reasons, assesses uniqueness from eight lenses, and ends in an evidence-backed landscape report with a direct verdict. Reports reality even when disappointing; never claims uniqueness from failing to find a competitor. Triggers: "/reveal", "is this idea taken/already built", "how unique is my project", "find competitors for X", "competitive landscape for X", "has anyone built this". Not a general research dig (mine), choosing between known options (thebest), a stack pick (techstack), or a codebase audit (exmaine).
- **Use-case:** The user wants to know how original a project idea is, who the real competitors are (including ones they have not heard of), how differentiated and viable the idea is against what already exists, or asks to "reveal" / investigate the market for an idea before building it. Also /reveal.
- **Usage:** `/reveal [project idea, or a path to a brief/README] + [target countries / languages / platforms if known]`

---

#### `seam`

- **Path:** [`seam/SKILL.md`](./seam/SKILL.md)
- **Description:** Place and enforce the one file that knows the third party - the framework, the vendor SDK, the platform driver - so every layer above it speaks the project's own vocabulary. Covers the import wall and the markup wall, hard-zero versus ratcheted severity, arming a gate (glob liveness, planted violations, controls, doc/registry code parity, one baseline per auditor, wall-time budget), where enforcement actually bites, disjoint migration batches and counts-file keying, codemod mechanics, and the per-component ownership that adopting a framework component transfers. Use when someone says "only X may be used in Y" and nothing enforces it, when a component swap is planned, or when a boundary rule has been green for a suspiciously long time.
- **Usage:** `/seam <the boundary to place, or the auditor to arm>`

---

#### `sly`

- **Path:** [`sly/SKILL.md`](./sly/SKILL.md)
- **Description:** Resourceful route-finding when the obvious path is blocked: capture the value, not the access. INVOKED ONLY WHEN THE USER ASKS - '/sly', 'be /sly and find a solution', 'think /sly and tell me what to do', 'be cunning about this', 'how do we get X without Y'. Never self-activate on a missing capability: report it, offer /sly. Once asked, run the full hunt: separate the real goal from the proposed method, verify the block, state the value needed, then produce at least three materially different routes across the five families (reroute, replace, rebuild from observed behavior, reshape, reduce), gate them on access parity, score on eight axes, pick on merit not cleverness. Hard lines: never bypass authentication or protections, never use credentials or private data not yours, never exploit, never damage or overload a third-party system, never exceed the user's own authorization - a route needing any of those is not a route. ToS/licensing are a trade-off note, not a gate. Derived data is verified, never faked.
- **Use-case:** Only when the user explicitly asks for it - "/sly", "be /sly about that", "think /sly and tell me what we need to do", "be cunning, find another way", or "how do we get X without access to Y". Never self-activate on a blocked path.
- **Usage:** `/sly [what is blocked] + [what you actually need from it]`

---

#### `spike`

- **Path:** [`spike/SKILL.md`](./spike/SKILL.md)
- **Description:** Turn "will this break it?" into numbers. A measurement, not a decision - pick the smallest renderable unit that carries a claim, derive its state list from code, capture computed styles, tight crops, node inventories and interaction facts before and after one reversible change, and report drift by category, including the drift that refutes the claim. Use when someone is about to win an argument by asserting something measurable, before adopting or swapping a component, or when a pixel-perfect diff is being cited as proof about behaviour.
- **Usage:** `/spike <the claim being tested>`

---

#### `take-a-breath`

- **Path:** [`take-a-breath/SKILL.md`](./take-a-breath/SKILL.md)
- **Description:** Force a deliberate pause before implementing. Stop the urge to code from scratch, calm the overwhelmed engineering impulse, and apply sober judgment about whether a mature, production-proven solution already exists. Use when the agent is about to write custom code for a common problem, when the user says take a breath, pause and evaluate, don't reinvent, prefer existing solutions, or when the task feels like it might already have a solid library, framework, platform feature, or established pattern. Triggers include take-a-breath, take a breath, pause and think, don't reinvent the wheel, prefer proven solutions, evaluate existing options.

---

#### `techstack`

- **Path:** [`techstack/SKILL.md`](./techstack/SKILL.md)
- **Description:** Recommend a technology/framework/library/tech stack (mobile, web, backend, desktop, infra) in any language or platform via rigorous, current, requirements-driven evaluation, never memorized popularity. Trigger on "recommend a tech stack", "React Native vs Flutter", choose/add/replace-tech requests. Discover by topic search, never memory; classify by scope; weigh consolidated vs specialists; count only features the project will use. Pin every capability claim to the candidate's latest stable version (from registry/releases, not memory) and ground it in real-world proof - before calling a capability awkward, find a real app that does it. Surface parity is not implementation parity - probe how daily-used capabilities are delivered. Compare via a yes/no capability matrix; split a product's distinct modes into separate candidate rows. Weigh the dimensions that matter; state trade-offs honestly. Two modes: normal (primary tech plus close dependencies) and ultra (every real need), on "ultra"/"full coverage".

---

#### `theskills`

- **Path:** [`theskills/SKILL.md`](./theskills/SKILL.md)
- **Description:** Pin skills as fixed, auto-apply behavior and persist that into the agent's memory context, so future sessions run them without being asked. Run at the start of a conversation or project to load the pinned set and apply it all session: pinning `clean-code` with the trigger "writing or editing code" makes every later turn that writes code run clean-code first. The registry (.theskills/pins.json) is the source of truth; `sync` renders it into the AGENTS.md managed block — the baseline every harness reads — plus, only when the harness has them, secondary layers: a feedback memory entry with its MEMORY.md index line, or notes a session-start hook injects. `status` audits drift across the layers that exist. Pins resolving to no invocable skill are refused. Use for "make X a fixed skill", "always use X", "pin these skills", "so you never have to ask me to run X", /theskills, or to list/add/pause/unpin/sync/audit the set. Not for running one skill once, and not general memory cleanup (the remember skill).
- **Use-case:** /theskills at the start of a session or project; the user asks that certain skills always apply, wants the pinned list seen or changed, or a repo has .theskills/pins.json.
- **Usage:** `/theskills [bootstrap|pin <skill> --when "…"|list|sync|status]`

---

#### `tier-up`

- **Path:** [`tier-up/SKILL.md`](./tier-up/SKILL.md)
- **Description:** Installs and runs the three-tier type architecture in a project: the raw type is named in exactly one file per primitive family, every domain meaning becomes a brand with one creation point and a stated policy, and every record is a shape assembled from brands; imports follow tier order and never skip. Opt-in — chosen by the project or the user, never imposed. Includes the conversion path for existing code (raw → tier 1 → tier 2 → tier 3 → boundary) with per-stage steps and a migration done-list. Trigger on "tier-up", "tiered types", "the tier system", "primitives brands shapes", "no raw types outside one file", "adopt the tier architecture", "promote this to a brand", converting a module to full typing rigor. The general craft — brands in any idiom, the compiler-first ladder, validation libraries, database constraints, the master vocabulary — is owned by /type-up; say so and stop rather than reinventing it. "Tier" here means the type-system tiers only, never architecture layers.
- **Use-case:** The project or user chose the three-tier type system, or code must be converted to it; also maintaining one tier in a project that already has the folders (primitives/, brands/, shapes/).
- **Usage:** `/tier-up [surface or module] [new | convert]`

---
#### `type-up`

- **Path:** [`type-up/SKILL.md`](./type-up/SKILL.md)
- **Description:** Enhances a codebase's type system so bugs surface at check time instead of runtime, in any language: brands for raw types, creation points, and boundary checks that turn untrusted data into typed values. Use when the user asks to improve, tighten or audit types, remove stringly-typed or primitive-obsessed code, add branded/NewType/opaque types, validate config or API contracts, make wrong values an error (compile-time and runtime), use the project's validation library (Zod, Valibot, Pydantic, Hypothesis, serde…), or convert a raw-typed surface. Compiler first: rejection is moved to compile time wherever possible. Golden rule: reuse existing types, never reinvent them. The opt-in three-tier architecture (primitives, brands, shapes) and its conversion path are a separate skill, /tier-up; do not impose naming schemes or that architecture unless the project or user chooses them.

---

## Archive

Skills under `Archive/` are kept for reference and are not linked or synced by `manager.py`.

- [blockiya](./Archive/Needs Work/blockiya/SKILL.md) — Enforce and apply the Blockiya architectural pattern for UI construction across component frameworks. Use when designing, reviewing, refactoring, or implementin…
- [check-violations](./Archive/Needs Work/check-violations/SKILL.md) — Universal, language-agnostic agent skill to audit codebases, architectures, contracts, and visual/data invariants for rule violations using fast scriptable chec…
- [chekr](./Archive/Needs Work/chekr/SKILL.md) — Run and remediate SNDUK Chekr architectural checks (@chekr/cli v0.3.2). Use when fixing check-violations, writing custom .chekr/checks, using @chekr-ignore bloc…
- [cross-platform-refactor](./Archive/Needs Work/cross-platform-refactor/SKILL.md) — Framework for auditing and refactoring ANY multi-platform codebase (mobile/desktop/web, any language/framework — MAUI, React Native, Flutter, Kotlin Multiplatfo…
- [stateful](./Archive/Needs Work/stateful/SKILL.md) — Derive every state a user-visible screen can enter, then implement the approved ones — pending, empty, stale, partial; provider down, degraded, throttled, maint…
- [artcraft](./Archive/artcraft/SKILL.md) — General skill for working with ArtCraft's family of open-source, agent-drivable design apps (Rust alternatives to vendor-locked tools) on Windows and Linux. Use…
- [building-fonts-from-svg](./Archive/building-fonts-from-svg/SKILL.md) — Builds installable TrueType fonts (.ttf, plus .woff/.woff2) in Python from SVG glyph drawings using fontTools and skia-pathops, including generating stylized le…
- [client-response](./Archive/client-response/SKILL.md) — Turns a client's project requirement message plus a Q&A conversation (developer questions and the client's answers) into one organized project-description file.…
- [contribute-agents](./Archive/contribute-agents/SKILL.md) — Coordinate multiple AI subagents that collaboratively work on a task, critique each other's reasoning, and converge on a documented conclusion. Use when the use…
- [dbug-backend](./Archive/dbug-meta-skill/backend/SKILL.md) — Debug a backend service when the symptom lives in server-side behaviour — API/route returns wrong or errors, middleware/auth/DI surprises, background jobs/queue…
- [dbug-database](./Archive/dbug-meta-skill/database/SKILL.md) — Debug database-layer problems — live DB disagrees with the schema definition (schema drift), migrations to author/verify/roll forward safely, missing/duplicate/…
- [dbug-frontend](./Archive/dbug-meta-skill/frontend/SKILL.md) — Debug browser/client-side problems — UI shows wrong/empty/stale data, a click does nothing or the wrong thing, console errors, requests that look wrong in the N…
- [dbug-instrumentation](./Archive/dbug-meta-skill/instrumentation/SKILL.md) — Controlled observation and artifact discipline during a debug session — use the moment you feel the urge to add a console.log, write a scratch check script, or…
- [dbug-investigation](./Archive/dbug-meta-skill/investigation/SKILL.md) — The core reasoning engine of dbug — use for the actual investigation of any bug: classify the problem, decide what to ask the user, gather and rank evidence, ma…
- [dbug-production](./Archive/dbug-meta-skill/production/SKILL.md) — Debug what you cannot reproduce at the desk — production-only failures, intermittent ("once a day"), only-under-load, only-one-customer/tenant, crash-after-N-ho…
- [dbug-regression-testing](./Archive/dbug-meta-skill/regression-testing/SKILL.md) — Turn every real bug into a permanent regression test — use when a failure is confirmed and about to be fixed (or was just fixed and has no test). Drives the fai…
- [document-db-attach-chain](./Archive/document-db-attach-chain/SKILL.md) — Batched, immutable, order-guarded cross-collection reads for document databases (RxDB, PouchDB, Dexie/IndexedDB, MongoDB) via an engine-agnostic attachOne/attac…
- [eas-build-archive](./Archive/eas-build-archive/SKILL.md) — Diagnose and shrink what `eas build` uploads for Expo and React Native projects. Use when an EAS Build archive is unexpectedly large or slow, when a build fails…
- [openbackgrounds](./Archive/openbackgrounds/SKILL.md) — Reconstruction kit for 50 animated backgrounds - aurora ribbons, galaxy spiral, particle waves, flow fields, raymarched crystals, metaballs, fluid ripples, wire…
- [powerup](./Archive/powerup/SKILL.md) — Orchestrate lightweight single-purpose improvement skills (any nested directory ending in up) against an existing project. Lists available powerups, validates t…
- [stories](./Archive/stories/SKILL.md) — Behavior stories for a system application, discovered systematically and written into the verification code itself. One real-world way a system can be entered o…
- [unit-agent](./Archive/unit-agent/SKILL.md) — Command-line Junie interface for running code tasks. Use this skill to orchestrate Junie subtasks via CLI, especially when you need specific configurations like…
- [up-agents](./Archive/up-agents/SKILL.md) — Launch staggered parallel worker subagents plus a delayed reviewer agent. Use when the user says up-agents, up agents, up-agents N + 1, spawn workers, worker po…
- [using-agent-skills](./Archive/using-agent-skills/SKILL.md) — Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill tha…
- [visual-enhancer](./Archive/visual-enhancer/SKILL.md) — Audits any code that produces a visual/rendered output — web components (HTML/React/Vue/Svelte/CSS), design mockups, Storybook stories, CLI/TUI output (ink, ble…
- [yo-engineer](./Archive/yo-engineer/SKILL.md) — Produces a professional structure.md — a project's folder tree paired with an Authority Table mapping every shared decision to one owner — built only from docum…
- [yo-nerdy](./Archive/yo-nerdy/SKILL.md) — Use whenever a user wants to deeply study, dissect, reverse-engineer, or fully specify every detail of ONE specific part, feature, flow, or subsystem of a large…
