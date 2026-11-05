# Agent Skills Catalog

This repository contains a comprehensive collection of modular Agent Skills. Each skill provides specialized domain instructions, operational workflows, patterns, and best practices for agents.

Total skills available: **129**

## Quick Index

- [dig-binary](Groups/Search/dig-binary/SKILL.md) — Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracin...
- [blockiya](Archive/Needs Work/blockiya/SKILL.md) — Enforce and apply the Blockiya architectural pattern for UI construction across component frameworks. Use when designing...
- [check-violations](Archive/Needs Work/check-violations/SKILL.md) — Universal, language-agnostic agent skill to audit codebases, architectures, contracts, and visual/data invariants for ru...
- [chekr](Archive/Needs Work/chekr/SKILL.md) — >- Run and remediate SNDUK Chekr architectural checks (@chekr/cli v0.3.2). Use when fixing check-violations, writing cus...
- [contribute-agents](Archive/contribute-agents/SKILL.md) — Coordinate multiple AI subagents that collaboratively work on a task, critique each other's reasoning, and converge on a...
- [cross-platform-refactor](Archive/Needs Work/cross-platform-refactor/SKILL.md) — Framework for auditing and refactoring ANY multi-platform codebase (mobile/desktop/web, any language/framework — MAUI, R...
- [prototype](Groups/Design/prototype/SKILL.md) — Build interactive design prototypes as small modular JS-rendered web projects: thin HTML entry points, shared vs per-page js/css...
- [display-to-user](Groups/Special/display-to-user/SKILL.md) — Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "l...
- [document-db-attach-chain](Archive/document-db-attach-chain/SKILL.md) — Batched, immutable, order-guarded cross-collection reads for document databases (RxDB, PouchDB, Dexie/IndexedDB, MongoDB...
- [explain](Groups/Talk/explain/SKILL.md) — Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-...
- [how-to-do](Groups/Agent/how-to-do/SKILL.md) — Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are do...
- [idk](Groups/Talk/idk/SKILL.md) — Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't ...
- [investigate](Groups/Search/investigate/SKILL.md) — Investigate local files, codebases, datasets, and external Agent Skills. Use for high-precision searches across heterogeneous formats, diagnosing unfamiliar architectures, inspecting...
- [antipattern](Groups/Audit/antipattern/SKILL.md) — Investigate a project and document the anti-patterns that genuinely threaten *this* codebase: three modes (named scope / existing doc / undefined), evidence-first findings with impact and confidence rated separately, rules written as Avoid · Instead · Applies when · Why it matters · Exceptions · Compliance check (optional before/after example), selections collected via `/inquire` or a marked `[-]` checklist, output as ANTIPATTERN.md plus an HTML report. Identifies and documents only — never fixes or enforces.
- [ladder](Groups/Audit/ladder/SKILL.md) — Find, design and harden ladders: audits the code for the tiers, layers, fallbacks and precedence chains already hiding in it, reports findings with file:line evidence, offers the fitting shapes with trade-offs and asks which to take, records the decision in the project's own doc format, then implements it without nested conditionals (pure decide over data, effects at the boundary)...
- [sly](sly/SKILL.md) — Route-finding when the obvious path is blocked: capture the value, not the access. Only on explicit request (`/sly`, "be /sly about that"): verify the block, restate the goal without the blocked thing, then generate reroute / replace / rebuild-from-observed-pattern / reshape / reduce options, gate them on access parity, score on eight axes and report the trade-offs...
- [chat](Groups/Talk/chat/SKILL.md) — Relaxed conversation mode the user starts and ends (`/chat [topic]`): short plain sentences, one idea per turn, no files/commands/tools that change anything, no offers to start work; user-invoked only and enforced with `disable-model-invocation: true`...
- [revoke](Groups/Generalize/revoke/SKILL.md) — Sanitise an artifact by revoking what ties it to a project, person, customer or deployment: inventory what is specific, choose [redact]/[pseudonymize]/[generalize]/[aggregate]/[keep] under one map, verify nothing leaks, keep the argument intact. Identity-neutral, not stack-neutral (polyglot)...
- [collection](Groups/Design/collection/SKILL.md) — Method for producing a coherent brand-illustration image collection for a project: determine the style once (shared Style DNA - medium, brand palette hexes, guard lines like 'strictly 2D vector, no 3D rendering'), determine where the set lives and how code consumes it (folder + slot filenames as the contract: drop a correctly named image in, no code change), determine how each frame behaves. The usage names the manifest file (e.g. on-boarding.md): slot->file->subject->status mapping (shipped/replaced/reused/no-image/pending, closing with whether anything is pending), hard rules (never in any image: no text/letters/numbers/brand logos - embedded in every prompt, violation = regenerate) and soft rules (dimensions, aspect, negative space - recommended, judgment calls), per-frame prompts in fixed sections (Style / Character / Action / Palette & Background) with verbatim character canon, save names, and reference-chaining from a style anchor so nothing drifts. Regenerate-only-if-needed: shipped artwork is left alone. Template + worked onboarding excerpt included. Not single-image prompts (imagegen), real-asset sourcing (fahlwy), or asset management (assets).
- [commit](Groups/Git/commit/SKILL.md) — Professional git commits in two modes. GUIDE (default, writes nothing): atomic change-based units, imperative subjects, what/why bodies, readable trailers; detects the repo's incumbent convention from its history instead of importing one, and resolves the scenario calls (when to commit, type/scope gray zones, a fix interrupting a feature, squash or not, repairing history behind a mandatory backup ref, releases and tags). INIT (`/commit init`): co-authors the repository's written commit discipline — probe the history and existing tooling, ask the seven questions the repo cannot answer, draft one policy document, merge never clobber — and installs nothing; enforcement (hook, linter, CI, review-only) stays the maintainers' choice in their own stack...
- [pdf](Groups/Files/pdf/SKILL.md) — Two modes. READ: extract PDF text to .txt with pdf_extract.py (page ranges, layout vs raw engines, page markers, cleaning, quality report) and export as numbered module files with a manifest for reading long docs selectively. WRITE: create/merge/split/rotate/watermark/encrypt PDFs and fill forms...
- [components](Groups/Design/components/SKILL.md) — Component-in-isolation stories gallery beside prototype's pages/: JSON registry (id, name, states) rendered one card per state, search + '@state: disabled' descriptors mirrored as ?show-only=disabled, dir/theme/density facets, shared-or-cloned renderers decided with the user, state-coverage checks...
- [honest](Groups/Talk/honest/SKILL.md) — Answers honestly instead of agreeably: says what it understood first, flags the ambiguity that changes the answer, then gives the verdict, the unmentioned cost, and real confidence. No flattery, no ritual pushback, no template. Use on 'can this really work', 'is this our best solution', 'be honest with me'...
- [language-handling](Groups/Pro/language-handling/SKILL.md) — Establishes idiomatic, language-specific coding standards for one application: toolchain and tooling, zero-warning...
- [ui-handling](Groups/Pro/ui-handling/SKILL.md) — Establishes frontend visual and interaction contracts: skeleton-pairing for zero CLS, responsive reflow, elastic text, slot-based...
- [error-handling](Groups/Pro/error-handling/SKILL.md) — Establishes an application's error architecture: contract paradigm (Result / exceptions / hybrid), payload...
- [sql-handling](Groups/Pro/sql-handling/SKILL.md) — Engine-agnostic SQL standards in two phases: the SQL conventions document (dumb store, prohibitions, types, parameterization)...
- [like-a-pro](like-a-pro/SKILL.md) — Root meta-skill orchestrator that reproduces production-grade engineering standards and conventions across applications....
- [mine](mine/SKILL.md) — Runs a deep, budgeted, multi-source research dig to understand not just what a class of thing looks like, but WHY — the ...
- [no-framework](no-framework/SKILL.md) — > Build Single Page Applications using NoF (No Frameworks) — a lightweight architecture defaulting to VanJS (~1KB, fine-...
- [persona](Groups/Agent/persona/SKILL.md) — > Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full beha...
- [planner](Groups/Code/planner/SKILL.md) — Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifi...
- [polyglot](Groups/Generalize/polyglot/SKILL.md) — Teaches AI agents how to design and author universal, general, and language-agnostic agent skills, and how to write bala...
- [scrape](Groups/Crawl/scraping/scrape/SKILL.md) — Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all...
- [scraper-optimizer](Groups/Audit/scraper-optimizer/SKILL.md) — Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory...
- [search-deeply](Groups/Search/search-deeply/SKILL.md) — Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems ...
- [senior-refactor](Groups/Audit/senior-refactor/SKILL.md) — Universal multi-platform refactoring skill to decouple codebases across TypeScript/React Native, Go, Rust, Flutter, and ...
- [subagent](Groups/Agent/subagent/SKILL.md) — Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized...
- [theskills](theskills/SKILL.md) — Pin chosen skills as fixed, auto-apply behavior and persist that into the agent's memory context (a managed AGENTS.md ...
- [summarize](Groups/Files/summarize/SKILL.md) — Use this skill whenever the user wants to shorten content without losing its meaning — summarize, condense, distill, rec...
- [take-a-breath](take-a-breath/SKILL.md) — Force a deliberate pause before implementing. Stop the urge to code from scratch, calm the overwhelmed engineering impul...
- [tray-inspection](Groups/Special/tray-inspection/SKILL.md) — Comprehensive workflow and Win32 inspection procedures for Windows system tray items, including listing active tray icon...
- [crosscheck](Groups/Audit/crosscheck/SKILL.md) — Cross-check a task, codebase, or research question by blind orthogonal discovery: dispatch N isolated subagents (N >= 2), each with a distinct cognitive lens - empirical/pattern-scanning, structural/behavioral, adversarial, product-pragmatist - none seeing the others' findings, hypotheses, or methods, then synthesize the reports into one reconciled document. Every finding is labelled by how it was found: consensus (corroborated by independent lenses), solitary (visible to only one lens), conflict (scouts disagree, tie broken by direct inspection), or dismissed (candidate proven a false positive). Phase 0 pauses to disambiguate scope with the user first. Writes .repertoire/findings/<topic>-findings.md; scout reports stay in .repertoire/agents/ unless --cleanup...
- [type-up](type-up/SKILL.md) — >- Converts plain primitive types (string, number, boolean, etc.) into a professional typing system with semantic aliase...
- [unit-agent](Archive/unit-agent/SKILL.md) — Command-line Junie interface for running code tasks. Use this skill to orchestrate Junie subtasks via CLI, especially wh...
- [up-agents](Archive/up-agents/SKILL.md) — >- Launch staggered parallel worker subagents plus a delayed reviewer agent. Use when the user says up-agents, up agents...
- [using-agent-skills](Archive/using-agent-skills/SKILL.md) — Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the ...
- [visual-enhancer](Archive/visual-enhancer/SKILL.md) — Audits any code that produces a visual/rendered output — web components (HTML/React/Vue/Svelte/CSS), design mockups, Sto...
- [parity](Groups/Design/parity/SKILL.md) — Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually ren...
- [viz-planning](Groups/Special/viz-planning/SKILL.md) — Use this skill when planning, designing, or architecting a data visualization system, dashboard, chart component, report...
- [yo-nerdy](yo-nerdy/SKILL.md) — > Use whenever a user wants to deeply study, dissect, reverse-engineer, or fully specify every detail of ONE specific pa...
- [dtb](Groups/Decision/dtb/SKILL.md) — "Do the Best": decide HOW the work is done while the user keeps owning WHAT is built. Treat a provided design/prototype as a constraint (improve execution, never replace direction), find the systems behind the visible requirement (a "search feature" = normalization, index, ranking, filters, empty/error states), compare 2-4 real options on criteria that matter here, pick the strongest appropriate solution, and record lasting decisions as question -> options -> choice -> consequences -> reversal. Best is not the first that works and not the most complex. Pairs with iwts and shares its `.iwts/<task>/decisions/` path; runs alone...
- [iwts](Groups/Decision/iwts/SKILL.md) — Autonomous ownership mode ("I Want to Sleep"): the user delegates the project and leaves, the agent acts as the responsible senior engineer to completion. Owns who decides and when to stop (two stop conditions only), per-task git-ignored `.iwts/<slug>/` state that survives a dead session, decision records with reversal boundaries; delegates decision *method* to dtb. Not for tasks with the user present...
- [animation](animation/SKILL.md) — Animation **meta-skill**: a router with no functionality of its own, holding three sub-skills underneath — `life` (UI motion: micro, component, transition, entrances/exits, feedback, scroll, springs, discovery, prototyping, review), `ascii` (character/terminal motion: ASCII intros and loaders, image/video→ASCII, plasma fields, Three.js AsciiEffect), `svg` (25 SVG/logo animation styles with light/dark variants). Invoke `/animation <life|ascii|svg> …`; rules, tokens, a11y and craft bars stay with the sub-skill that performs the work...
- [postmortem](Groups/Files/postmortem/SKILL.md) — Blameless, self-contained incident documents (postmortem, incident report, RCA, bug write-up): 18 mandatory sections, a **second-story** table (blameless is not nameless), at most 8 **verified** action items with owner/due/ticket/DoD, evidence levels V0–V5, rare-bug soak math, publication within 5 business days and postmortem quality metrics. Two modes — **file** (one Markdown doc, permalinks) or **folder** (index.md + bundled index.html reader + evidence/, investigation/, fix/, verification/ with every artifact copied in, SHA256-indexed, secrets redacted, a Files and Artifacts Index and a "How we reached this conclusion" narrative with dead ends). Prose follows `/document`; `scripts/pm_check.py` validates sections, action caps, owners, links, checksums and the reader...
- [bequeath](Groups/Agent/bequest/bequeath/SKILL.md) — End-of-session asset harvesting: review the whole conversation, propose candidates (name, type, original purpose, proposal, future use, direct-vs-generalize), and create **nothing** until the user selects — silence is not approval. Then generalize only the approved items (parameters, no hardcoded paths/names/versions/assumptions), test beyond the original example, state verification honestly (automated / manual / partial / unverified), and store each asset in `bequest/<slug>/` beside its tests with a card (what, when, how, inputs, outputs, dependencies, assumptions, verification). `scripts/bequest_check.py` scaffolds the directory and validates cards, index coverage, links, secrets, machine paths and duplicates. Not session state, not global skills...
- [heir](Groups/Agent/bequest/heir/SKILL.md) — Acknowledge previous agents before rebuilding: at the start of a task, read `bequest/INDEX.md`, match only what this task needs, read the asset card (inputs, dependencies, assumptions, verification status), check for drift, and **run its tests before trusting it**. Then reuse, adapt or extend in place — updating the card and citing provenance, never forking a competing copy. Hands off to `bequeath` at session end. The reading half of the bequeath/heir pair...
- [diffs](Groups/Git/diffs/SKILL.md) — Read git diffs as evidence: establish the right baseline (A..B vs A...B, staged vs worktree vs HEAD, merge base), survey a change set with `scripts/diff_survey.py` (per-file status, churn, rename/binary/whitespace-only/generated/dependency/migration flags, risk summary, `--json`, `--fail-on high`), triage deletions and manifests before logic, read hunks correctly (hunk arithmetic, `-M` renames, `-w`, word-diff, color-moved, histogram when a diff looks insane), spot risk (removed error handling, changed defaults, boundaries, mode bits, weakened tests, secrets), search history with pickaxe `-S`/`-G`, message-level `--grep`, `log -L`, `git grep <rev>`, `range-diff`; the topic dossier `--topic Sentry` bundles commit messages + per-file code counts + pickaxe history under one byte budget (measured: naive `-S -p` dumps run to tens of k tokens where the complete dossier holds ~600, and it also covers the message channel), and read merges with `--cc`/`--remerge-diff`. Reviews truthfulness too: message vs hunks, tests, debug leftovers, partial staging, scope creep. Multi-commit level: `--per-commit` maps a range (merges tagged, never double-counted) and reports **hidden churn** — files the aggregate diff under-reports because commits cancelled out; `--first-parent` for merge-heavy history, `--cwd` for another checkout... Token-efficient by design: `--file /tmp/big.diff --hunks --match <func>` indexes hunks by function and prices them in bytes, `--hunk 1,4 --budget 4` fetches only what you asked for — one function out of a 5 000-line diff costs ~150 bytes of context, not 50 KB...
- [benchmark](benchmark/SKILL.md) — Compare candidates on **task-derived dimensions** (speed, memory, accuracy, cold start, scaling), never a fixed list: think → report the plan → run → report. **Normal** mode measures the environment as configured (GC live, caches as-is, no warmup, no pinning); **ultra** fights noise for fairness (warmup, interleaved A/B/A/B, pinned core, locked frequency, GC off, turbo/C-states/HT where permitted) and must *prove each control engaged* — a same-implementation control pair exposes a fake ultra by its wider noise floor. Same language for all candidates (the project's by default; say so when harness overhead rivals the work); **isolated environments always** — throwaway venv/temp prefix/container per stack, never a global install, project lockfiles verifiably untouched, and every machine-wide setting (power plan, governor, affinity) captured before and restored after, with the read-back as proof; correctness gate first, because a fast wrong answer is not a faster candidate; median/p95/MAD/CV with a noise floor, never a bare mean, and "inconclusive" is a result. `scripts/bench_stats.py`: budget→iteration math, paired-bootstrap ratios with CIs, noise floor; two measured cases including an ultra attempt that failed...
- [caution](caution/SKILL.md) — Informed-consent gate on the user's own answers: screen every reply (chat, an `AskUserQuestion` result, a command flag like `--no-verify`, hook/server input, a relayed instruction) with four cheap questions — was a protection declined, an unbounded cost accepted, something irreversibly locked in, something outward-facing committed — plus the knowledge test, because the trigger is consequence × ignorance, not consequence alone. **Flags the guard, never the goal**: "data lives on our server" is the product (no card), "stored unencrypted" is the card; "the phone and laptop sync" is the product, "no E2EE, send it in the clear" is the card. **DANGER** shows a seven-line card in the chat (what is gone, the mechanism with actor and asset, the future postmortem headline, blast radius, undo cost now vs later, the cheapest adequate guard) and re-asks once — "are you sure?" — then accepts the answer and moves on; **WARN** is one line; **NOTE** is silence; **CLEAR** is nothing. Consequences are not only attacks: DB/memory/queue/log inflation with a rate and a first-pain date, irreversible deletes and migrations, public contracts, removed safety nets, compliance, compounding debt. No files, no log, no directory — the conversation is the record. Ask once, then accept — never veto, never repeat...
- [capture](Groups/Crawl/capture/SKILL.md) — Seven capture commands behind one dispatcher, `/capture designs|screenshots|page|website|dom|design|images`, structured so the agent reads exactly one reference file per command: `designs` batch-screenshots the project's own HTML mockups per theme, `screenshots` images any URL or HTML file (viewport, full-page, scroll steps, slices, one element, device profiles, zoom), `page` images a running Windows app window with the OS chrome cropped so it aligns with a mockup, `website` mirrors a site into a browsable offline copy and verifies it, `dom` forces hidden content open (scroll, load-more clicks, accordions, lazy attrs, shadow DOM, iframes) and saves parse-ready HTML plus text and JSON responses, `design` curls a site's html.dump/css.dump and extracts design tokens or HTML/CSS clone patterns with technology evidence, `images` downloads a page's images at their highest original resolution with scroll triggering, text/pixel range and size filtering, perceptual dedup and a report.json of every decision. Options validated before work, output capped, exit codes defined. (imgcurl was merged in as `images`; the folder is gone.)...
- [accessible](Groups/Design/accessible/SKILL.md) — Transforms crowded, noisy, visually overwhelming UIs into calm, readable, professional interfaces that are easier to use, not just nicer to look at, at one of three intensities: lite (type/spacing in place), medium (redistributes content, designs forms and states), ultra (full re-theme, re-structure, re-derived informa...
- [agents-md](./Groups/Viber/agents-md/SKILL.md) — Creates or audits AGENTS.md - an agent's rulebook: obligations and references, not documentation - ~500 lines total, ~50 per section - longer sections become referenced docs. Interviews; nineteen sections: agent instructions (the interview ASKS the user's standing behavioral directives - skill declaration lines like "last line names skills used", skill-usage floors like "attempt one skill per response", mandatory pre-workflows like "grill-me before implementing" - user-chosen shapes, empty says none recorded); mandatory context with the active-scope fence (version/channel, excluded scope; each dimension names its REACH - what it governs and how the agent recognizes it, e.g. a docs/[main] vs docs/[canary] split, a build flag, a naming pattern - never a bare label); how-to router (REPLACES Development Workflow, Debugging, Execution, Environment and Version: procedures AND their policy live in registered how-to docs - WHICH task classes a project routes and what its docs are named is the project's own; the illustrative pairings: a [development doc] holds branch model + operational meanings, a [debugging doc] the playbook, a [commands doc] shell rule with its failure + the one package manager, a [configuration doc] the secrets strategy and .env route, a [release doc] the version policy - scheme SHAPE with cited spec (never a live value), WRITTEN bump rule + who per component, dual tracks, declaration-site sync, attachment blocks; what binds is the shape: task class -> routed doc, read-before-act, write-back same change, and a thick-enough router (linter flags <4 routed classes - procedures squatting in the rulebook); grown kinds split into folders like debugging/db.md + web.md; the agent reads only its task's file (token efficiency), section 2 owns the paths, the router names docs; read-before-act + write-back duties); registered indexes carry duties on the row (units: read-before-implement, reuse over duplicate, entry in the same task - the standalone Units section folded into section 2's registry); design; startup; delegation - briefs, doc lists, autonomy, reports; privacy - hidden paths cascade, .gitignore syncs, cache asks; resourceful - local over global (global installs = named exceptions); authority - ask per session (default) or fixed: external installs/processes, DB writes, credentials; when blocked, say honestly what cannot be done and ask; version control - authority over whichever VCS the project uses (git, Unity VCS/Plastic, Perforce, SVN; commands illustrate, concepts bind): inspect/check-in tiers, outward-ask, never-without-order, parked-work (stash/[shelve]) policy with naming pattern, change identity (the authorship answer the commit and branch skills look for before asking); ambiguity - how the agent asks: Exact (named implementation specifics chosen by the user) or Broad (intent only, agent picks internals best-for-project), or both by weight with the user's Exact list written down; MANDATORY always-ask on weight-bearing decisions (irreversible, costly, security, cross-module), never trivia; consequential asks route through caution; critical questions settled before any anonymous run; owns decision records: one file per decision at <docs>/decisions/<slug>.md (never a combined decisions.md that explodes), each anchored Date + Commit + App-Version, the ask-or-decide call itself recorded, run ledger at <docs>/decisions/states.md - whatever the project's anonymous/autonomous modes are, they are thin operating modes, this section is the convention; golden rules - the never-bend list phrased in violation shape (no hardcoding - always use DB tables); review - when a review runs (a named task or the diff self-review) the rulebook-violation pass leads it, in code AND docs - review-time law, not an always-on job; then named tasks (Docs: stale passages, unlinked docs nothing points to, docs over 500 lines become a folder named after the doc with index.md; DB: learn all tables, hunt hardcoded/mocked data); docs-root is a MUST-ASK when undeclared - there is no project without docs, they are the source of truth; the subagent block gained a GOLDEN clause; version - the version-number policy section (schemes [SemVer]/[CalVer]/[SDK-style]/[base+tag] are illustrative, not a menu - cite the spec [semver.org]/[calver.org]/[keepachangelog.com], never restate or invent its rules; WRITTEN bump rule replacing probabilistic guessing; who may bump; declaration-site sync handed to section 24's table when the number has more than one home (20 owns the bump rule, 24 owns the where); dual public/internal versioning; each attachment its own subsection - ### Changelog, ### Release notes, ### Public docs, ### Tags - with the file-by-file procedure in <docs>/versioning.md); one owner per fact - a section that touches another section's or a doc's data writes a brief + pointer, never a restatement; facts - the corrections ledger: fixed paragraph (verified facts contradict what agent training would assume and WIN over memory; suspect facts re-verified and re-dated, never argued from memory; dated bullets believed/actual/proven accumulate for the life of the project the moment verification contradicts a prior belief, FACTS clause travels in the subagent block); linter 30 fixtures, nineteen sections; before-between-after - the always-on task rituals in three phases (BEFORE: what to read/confirm first; BETWEEN: standing checks like 'search for an existing implementation before writing a new one'; AFTER: gates like the type-check command the stack owns, lint, self-review vs golden rules) - the user's CURRENT prompt overrides them per task, a standing wish edits the section, bullets grow for the project's life; voice - the register the agent speaks and writes in, chosen per SURFACE: replies to the user / public documents (README, release notes, help) / internal documents (decision records, reports, how-to docs) may each carry their own mode [concise]/[explanatory]/[verbose]/[ponytail] (the lazy-senior-dev minimum: shortest statement that still proves the point) - one voice everywhere is a valid explicit choice, never a silence-default; the user's own vocabulary and directness set the conversational level; no surface speaks off-script - written artifacts take their surface row's register; sync blocks - writable meanings with more than one home (two SDKs of one feature, doc pairs, config mirrors, the version declaration sites section 20 points here for): blocks sync in MEANING not letters, one table per block (location + line anchor + what each home carries), tables born in their own file by default (<docs>/sync-blocks.md - they grow block by block; AGENTS.md keeps the law, duty and pointer), an edit to one side's meaning lands on every row in the same change; all sections exist at creation - empty = guide paragraph + 'none recorded', never deleted; a section's identity is its title and order - heading depth, numbering and subsection shape belong to the writer and the harness, flexibility never erases identity or content; skills - one row per project skill: when it applies and what to read/do first; maintenance - same-change update; checked review date. Audits existing files (move-out map, no silent deletion, foreign blocks pass through); writes ONLY AGENTS.md...
- [personalize](./Groups/Viber/personalize/SKILL.md) — Updates the user's GLOBAL agent instruction file (the personal AGENTS.md every project loads) with standing preferences so settled questions never get re-asked - an agent asking "which package manager?" when the global file answers is the idiot-agent this skill kills. Modes: "/personalize that i like bun and bunx" distills the statement into an enforceable preference line (behavior not transcript, explicit default + exception boundary); bare /personalize asks what to set, showing the existing lines first; "/personalize the section X in current AGENTS.md into global" promotes it - personal defaults up, project decisions stay, machine-specific routed to AGENTS.local.md; copy unless told "move"; a contradiction stops and asks. Ladder: current prompt > project AGENTS.md (respects the global; overrides only explicitly, with reason) > global preference. Dedupe and refine over append (one owner per fact); vague statements sharpened or refused, never written.
- [secondary-pages](./Groups/Design/secondary-pages/SKILL.md) — Secondary DOCUMENTS nobody markets and everybody needs: ToS, Privacy, Cookies, Acceptable Use (violations + what they lead to), Contact, About, FAQ, Status, Security/vulnerability disclosure, Accessibility, Refund/Shipping, Community, Legal notice/Impressum, DPA, Takedown, Child privacy, Delete-account, Unsubscribe, Changelog, Anti-fraud — deep-researched catalog with ONE reference file per type (required blocks, professional writing rules, the questions to ask, failure patterns). Works on ANY platform — "page" is shorthand: [web] route, [desktop]/[mobile] app surface, [embedded] view; shared contracts across platforms keep ONE canon location (usually web; other surfaces REDIRECT or EMBED, a bundled offline copy is a declared synced duplicate, never a second original). The agent ALWAYS asks which documents to create (long list); never invents facts (retention days, refund windows, registration numbers come from the user or config); documents describing what the project does not do stay out — no over-engineering of what is not true; unclear+material gets one clarification question. Duties binding every document: PII/contract data never hardcoded (env/config + json/txt message templates), light static content with no app logic or hydration, and where a web canon exists full SEO (indexable, sitemap.xml, robots-aware, canonical). Placement per document is the user's decision - the shapes in references/presentation.md (route, footer, signup inline, modal, accordion) are examples, not a menu, bound only by the reader contract: full current text one step away, stable canon URL, consent gates the whole document; engineering rules in references/engineering.md.
- [amongus](Groups/Agent/amongus/SKILL.md) — Tiny awareness skill: another agent works in the same project. On trigger say exactly COPY That! and continue silently. Unfamiliar edits are the teammate, not corruption - never panic/revert/restore work you didn't touch; re-read before editing, keep changes additive; on same-file collision wait for them to finish or take another file and return; numbered-identity generosity whenever agents work anonymously by any means (devXX taken first stays theirs - shift to dev73, never contest). Use when confused changes appear in the tree, shared-agent repos, or the user says amongus.
- [anti-slop](Groups/Audit/anti-slop/SKILL.md) — Review UI and product-design quality for a page, selected routes, an application, or a repository. Use when asked to find, explain, prioritize, or guide correction of design anti-patterns using visual/contextual evidence, source inspection, or both. Routes through a 67-pattern catalog and keeps findings evidence-based;...
- [artcraft](Archive/artcraft/SKILL.md) — General skill for working with ArtCraft's family of open-source, agent-drivable design apps (Rust alternatives to vendor-locked tools) on Windows and Linux. Use when asked to use an ArtCraft app, design UIs (login screens, landing pages, mobile/desktop frames) with these apps, discover and drive their CLI/MCP command s...
- [ascii](animation/ascii/SKILL.md) — Build ASCII and character-based animations for web, terminal, or CLI. Use when the user asks for an ASCII animation, terminal intro or loader, image or video to ASCII, retro or hacker text motion, generative plasma or wave fields, character-art shaders, Three.js AsciiEffect, per-character cascade or domino effects, gra...
- [assets](./Groups/Design/assets/SKILL.md) — Asset management for any platform: images, icons, fonts, audio, video, documents and color values - the resource files themselves, not the systems that serve them. Eleven tested tools: recolor (a color family or a picked pixel), convert/fix-extension, rotate/flip/scale/resize/crop, favicon and app-icon sets, OG images, legacy splash screens, optimization with before/after reporting, localization of CDN assets (browser-UA fonts, byte sniffing), an inventory (duplicates, unreferenced files, external URLs, sizes per category), color conversion across CSS Color 4 spaces with WCAG contrast, and a Bun.Image script for variants plus ThumbHash placeholders. Audio/video use ffmpeg directly; renames: shell moves + reference updates. Platform specs are sourced (Apple 1024 layered icons, Android adaptive/12 splash API, favicon sizes). Rules: names, brand-vs-content, formats by purpose, ask-first splash choices. Triggers: favicon, icons, splash, OG, recolor, convert, optimize, localize, color, rename, unused assets...
- [backend](Groups/Code/dbug/backend/SKILL.md) — Debug a backend service when the symptom lives in server-side behaviour — API/route returns wrong or errors, middleware/auth/DI surprises, background jobs/queues/workers, timeouts, connection pools, retries, environment/config not loading, module/workspace resolution failing in a monorepo, or "is it our code or the dat...
- [branch](Groups/Git/branch/SKILL.md) — Plans, names, and safely runs Git branches, including repositories several agents share. Three situations differ: alone; beside other agent processes (a second session or tool, e.g. Claude Code + Codex) sharing one .git; and your own subagents in this process. Where sessions can collide, the claim is a session-scoped l...
- [commitments-md](Groups/Viber/commitments-md/SKILL.md) — Creates and maintains COMMITMENTS.md - the project's declared goals, priorities and trade-offs - or a small Commitments section in AGENTS.md when tiny. Premise: you cannot get the gold in every case. Some goals are mutually exclusive, some reinforce each other, and every priority has a price, a horizon (MVP vs later) a...
- [compare](compare/SKILL.md) — Write professional, well-reasoned comparisons between two or more subjects of any kind — technologies, files, projects, code modules, books, documents, biological processes, products, strategies, or any named options. Use whenever the user asks to compare, evaluate trade-offs, distinguish, or choose between things, inc...
- [context](Groups/Agent/context/SKILL.md) — Project-context reconstruction — build a reliable mental model of a project from all available artifacts (docs, source, config, git history with a 5-commit default, Flush notes, images, prototypes, design artifacts) before any work. Two modes: light (default) inspects and reads only, never running tests, builds, instal...
- [create-video](Groups/Video/create-video/SKILL.md) — Turn a vague video request into locked, numeric direction, then lay out, verify and deliver a professional video project. Loads after the hyperframes entry point has routed the job and written BRIEF.md, and never competes with it or the hyperframes domain skills. Converts the brief into six independent axes — genre, pa...
- [database](Groups/Code/dbug/database/SKILL.md) — Debug database-layer problems — live DB disagrees with the schema definition (schema drift), migrations to author/verify/roll forward safely, missing/duplicate/wrong rows, constraints and RLS/policy surprises, ORM-generated SQL that isn't what it looks like, slow queries and execution-plan regressions, locks/deadlocks,...
- [dbug](Groups/Code/dbug/SKILL.md) — The debugging meta-skill. Investigate, debug, fix, and verify any problem in a codebase as a disciplined process — never "change code until the error disappears". ALWAYS use this when something is broken, wrong, failing, unexpected, regressed, or hard to reproduce — mentions of bug, error, exception, crash, 500, timeou...
- [decide](Groups/Decision/decide/SKILL.md) — Helps the user choose between candidates (software in any language or platform, databases, tools, cloud services, products, approaches) by researching them fairly and delivering one rich HTML decision page. The Compare tab has a dated freshness section, per-dimension winners (ties allowed), charts, tables, ratings, sou...
- [detailsup](Groups/Pro/detailsup/SKILL.md) — Guided, conversational, topic-by-topic technical specification: close one design area before opening the next. Use when a project has undecided architecture (scrapers, workers, pipelines, caching, data models, queues, storage, deployment) and the user wants to work through it sequentially - ask targeted questions with...
- [document](Groups/Files/document/SKILL.md) — Markdown documents: five jobs, the default entry whenever a task produces, restructures, shortens or rewords a document - self-invoked, not only when /document is typed. WRITE a new document (normal/comprehensive/concise) matching the user's purpose and evidence rules. REORGANIZE a messy doc set into one-concern-per-fi...
- [eas-build-archive](Archive/eas-build-archive/SKILL.md) — Diagnose and shrink what `eas build` uploads for Expo and React Native projects. Use when an EAS Build archive is unexpectedly large or slow, when a build fails with a Gradle/CocoaPods or toolchain version mismatch that works locally, when a custom dev client throws "Cannot find native module", when secrets or generate...
- [educate](Groups/Crawl/scraping/educate/SKILL.md) — Turns documentation retrieved by the Scrape skill into a pruned, project-relevant, indexed, version-aware knowledge base so the agent never has to re-read or re-search the full raw docs again. Use whenever the user asks to "learn"/"study" a library or framework's docs, wants deep or repeated work with a specific depend...
- [exmaine](Groups/Audit/exmaine/SKILL.md) — Examine a project from the inside out, starting at AGENTS.md: follows every doc path it declares (design docs, units, glossary, commitments, decisions, skill sources), reads them, sweeps the code against what the docs claim, and delivers a complete overview that orients an agent fully around the project. Strictly static and read-only - never runs install/test/build/serve; anything unprovable by reading is reported as an unverifiable runtime claim. /exmaine full = complete examination: every area checked against stated intent, intent-ledger vs code cross-check pass by pass, gap ledger of broken pointers/orphans/contradictions, ending in the full project overview. Static evidence levels E0-E5, "passes" means consistent-by-construction never "works". Not a verdict run (please-verify), not refactoring, not runtime debugging.
- [fahlwy](Groups/Crawl/fahlwy/SKILL.md) — Over-smart asset-source hunter. Find and PROVE a required number of working free asset sources (images, avatars, video, audio, icons, fonts, PDF books, brand logos) by fetching real bytes and validating magic signatures - never stopping at a guessed URL. Keeps its catalog as queryable CSV (data.csv: category, provider,...
- [fix](Groups/Code/fix/SKILL.md) — After root-cause diagnosis with dbug, resolve the problem and improve the relevant implementation so the same or similar problems become easier to identify, understand, or prevent in the future. Use together with dbug whenever a problem has been understood and a fix is being applied. Covers immediate fix, local-context...
- [flush](Groups/Agent/flush/SKILL.md) — Agent continuity capture, manual — persist working state before session end, environment change, loss, milestone, handoff, or when the conversation grew too large: CONTEXT.md (how we got here — decisions, reversals, what worked/failed, open questions), PLAN.md (the ACTUAL plan, not the original), SNAPSHOT.md (facts ver...
- [frontend](Groups/Code/dbug/frontend/SKILL.md) — Debug browser/client-side problems — UI shows wrong/empty/stale data, a click does nothing or the wrong thing, console errors, requests that look wrong in the Network tab, state that diverges from what the server sent, unexpected re-renders, or "works locally but not in the browser" — use whenever the observable failur...
- [genimage](Archive/genimage/SKILL.md) — Universal image generation through any RESTful provider — xAI, OpenAI, Gemini, or OpenAI-compatible gateways (NezhaGate, Apidot, newer) — via a growing provider registry (data.csv): a new vendor is a row, not a redesign. Concurrent --batch N with progress bar + state table; --variations, --prompts-file; persistent cont...
- [glossary](Groups/Viber/glossary/SKILL.md) — Maintains one unambiguous project vocabulary in alphabetical letter blocks. Golden rule for what earns a block: the word as used here carries more than the dictionary sense - redefined or made-concrete ordinary words ('eye', 'minimal'), project coinages ('Melody' for a workflow), private-sense abbreviations, transliter...
- [goal](Groups/Code/goal/SKILL.md) — Define clear, unbreakable, achievable goals with explicit completion criteria and resource awareness. Use when setting objectives, starting complex work, verifying task completion, or when goals involve environment or resource constraints. Triggers include goal, define goal, set objective, success criteria, verify comp...
- [grill-me](Groups/Talk/grill-me/SKILL.md) — Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
- [idea-md](Groups/Viber/idea-md/SKILL.md) — Turns a raw project prompt - any language, any mess - into IDEA.md: the project's complete idea document, readable by anyone, technical or not. First the idea's inspiration - a SET of sources: name every product it draws from (Medium, Dev.to…), what each contributes, its relationship (instance of / similar to / a slice...
- [implement](Groups/Code/implement/SKILL.md) — Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates, in order: (1) a coding brief naming the app/module being coded and which stack-agnostic concerns it touches (interfaces, styling, a11y, navigation, forms, persistence, platform, concurrency, errors,...
- [impurities](Groups/Audit/impurities/SKILL.md) — Project-wide defect discovery and remediation through self-designed iterations — never a fixed checklist. Assess the actual project (runtime, resources, dependencies, assets, build, CI, config, platforms), then design and run as many focused investigate-and-remediate iterations as its specific risks warrant: investigat...
- [inquire](Groups/Talk/inquire/SKILL.md) — Build a rich, interactive question page (HTML) when the agent must get several important decisions from the user before or during work. Use it when there are 2 or more open questions whose answers change the project, design, architecture, or approach, and the user needs context, trade-offs, diagrams, or examples to cho...
- [instrumentation](Groups/Code/dbug/instrumentation/SKILL.md) — Controlled observation and artifact discipline during a debug session — use the moment you feel the urge to add a console.log, write a scratch check script, or "just quickly query the DB": routes debug output through a dev-only, scope-gated facility instead of scattered prints, keeps every throwaway script in .debuggin...
- [investigation](Groups/Code/dbug/investigation/SKILL.md) — The core reasoning engine of dbug — use for the actual investigation of any bug: classify the problem, decide what to ask the user, gather and rank evidence, map the pipeline, run the hypothesis loop, use Git forensics when it "worked before", locate the first invalid state, design a root-cause fix that is minimal but...
- [isolate](Groups/Audit/isolate/SKILL.md) — Isolate code that varies along one or more axes (platform, release channel such as canary/stable, audience or region, tenant, hardware tier, experiment cohort) so every difference has exactly one home and no file name has to carry two dimensions. Works on a module or a whole project. Small tasks are isolated directly,...
- [judge](Groups/Talk/judge/SKILL.md) — Acts as a fair, unbiased judge comparing two or more candidates (libraries, frameworks, tools, architectural approaches, vendors, design options, or any comparable set of choices). Use whenever the user wants a rigorous, evidence-based comparison or recommendation rather than a quick opinion — phrases like "which is be...
- [learning-test](learning-test/SKILL.md) — Write and run a "learning test" (term coined by Jim Newkirk, popularized by Robert C. Martin/Uncle Bob in Clean Code ch.8 "Boundaries") to empirically discover how a third-party library/framework/API actually behaves, instead of guessing, relying on stale training knowledge, or trusting docs that may be incomplete, out...
- [life](animation/life/SKILL.md) — Designs, builds, reviews, and prototypes UI animation through three commands - micro (a single element), component (a whole component as one visual unit), transition (moving between states, views, or pages, always with forward and backward motion). Resolves vague requests such as "make it feel premium", "an onboarding...
- [openbackgrounds](Archive/openbackgrounds/SKILL.md) — Reconstruction kit for 50 animated backgrounds - aurora ribbons, galaxy spiral, particle waves, flow fields, raymarched crystals, metaballs, fluid ripples, wire globes, radar sweeps, film grain. Use when asked to build, recreate, port, match, or choose an animated background for a hero section, landing page, app shell,...
- [packages](Groups/Audit/packages/SKILL.md) — One run, two jobs over a project's dependencies, any ecosystem (JS/TS, Python, Go, Rust, JVM, .NET…) and any project shape. Job 1 — redundancy audit: classifies each dependency as explicit (imported) or implicit (needed without any import: toolchain binaries, native/link-time stubs, config plugins, entry-point-discover...
- [parallize](Groups/Code/parallize/SKILL.md) — Plan and run parallel work: the main agent decides in chat how to fan out a large or newly approved job, keeps the most sensitive work for itself, and hands bounded slices to subagents in waves that respect the harness concurrency cap. Use when the job is large enough to split, a plan has just been approved, the user s...
- [please-verify](Groups/Audit/please-verify/SKILL.md) — Broad verification of a project or delivered body of work - not just the last step - answering one question: is the work actually complete and sufficiently verified? Starts from the user's ask (conversation, IDEA.md, plan, AGENTS.md), never from the agent's own summary, and sweeps requirements, completeness, bugs, rule...
- [powerup](Archive/powerup/SKILL.md) — Orchestrate lightweight single-purpose improvement skills (any nested directory ending in up) against an existing project. Lists available powerups, validates the user request, and independently delegates each selected powerup to a subagent via professional-subagent. Use when the user invokes /powerup or asks to poweru...
- [production](Groups/Code/dbug/production/SKILL.md) — Debug what you cannot reproduce at the desk — production-only failures, intermittent ("once a day"), only-under-load, only-one-customer/tenant, crash-after-N-hours, and heisenbugs that vanish when observed; plus concurrency investigation (races, deadlocks, interleaving reconstruction) and resource-growth analysis (memo...
- [pvc](Groups/Audit/pvc/SKILL.md) — Role-based UI construction (Page → View → Component, plus Decoration, Aligner, UI Element, Rendition) — framework-agnostic architecture for building or auditing UI code in React, Vue, Solid, Svelte, Blazor, Dioxus or any component system. Use when designing a screen or feature folder, deciding what a piece of UI actual...
- [readme-md](Groups/Files/readme-md/SKILL.md) — Create, review, and update professional README files grounded in the actual project, never assumptions or nonexistent features. Inspects real sources (manifests, entry points, scripts, tests) first; separates implemented from planned; identifies primary audience; asks the README voice/style — minimal setup / engineering overview / deep developer-experience (build-from-source, branch & channel navigation, contribution path) / marketing showcase (project as product) / hybrid — facts identical in any voice: voice changes reorder and re-register, never re-claim (references/voice-and-tone.md holds the voice-vs-tone model, the five levers table, per-voice guardrails, and the restatement technique). Real commands only, no fabricated badges/links/screenshots, honest tested-vs-reviewed reporting; targeted edits over rewrites; draft mode...
- [recall](Groups/Agent/recall/SKILL.md) — Recall, in two modes, on one rule: report only what you can actually find. Mode A answers "do you remember when I said X?", "did I mention Y?", or /recall <topic> from what is really present - live context, plus past-chat or memory tools when present: open with Yes, No, or Partly, quote the user's own words verbatim on...
- [refactor](Groups/Code/refactor/SKILL.md) — Surgical code refactoring that improves structure and maintainability without changing behavior. Use when the user says refactor this, clean up this code, fix code smells, extract method, replace conditional, move method, introduce parameter object, eliminate duplication, break down god class/function, improve type saf...
- [regression-testing](Groups/Code/dbug/regression-testing/SKILL.md) — Turn every real bug into a permanent regression test — use when a failure is confirmed and about to be fixed (or was just fixed and has no test). Drives the fail → fix → pass loop, picks the lowest test layer that actually exercises the broken path, and decides honestly when a test is NOT reasonable (needs disproportio...
- [seo](Groups/Audit/seo/SKILL.md) — Universal 100-point on-page SEO playbook for ANY web stack (Next.js, SvelteKit, Nuxt, Blazor, ASP.NET, Rails, Laravel, Django, Dioxus, Leptos, Astro, Hugo, static HTML - SSR, SSG or client-rendered). Use when the user wants to build, audit, or auto-fix pages so the raw first HTML packet scores 100/100 on Wincher-style...
- [stateful](Archive/Needs Work/stateful/SKILL.md) — Derive every state a user-visible screen can enter, then implement the approved ones — pending, empty, stale, partial; provider down, degraded, throttled, maintenance; no connection at launch; extreme latency; expired session; refused entitlement; unknown values; device suspended, killed, storage-full; races; integrity...
- [states](Groups/Audit/states/SKILL.md) — Classify any fact an app consults as a State or a Condition, decide who owns it, and settle whether a consumer may read it or must create it. Use when deciding loading vs offline, error vs permission-denied, empty vs feature-flag-off, or any "is this my own request or something external" question; when placing a fact s...
- [stories](Groups/Code/stories/SKILL.md) — Behavior stories for a system application, discovered systematically and written into the verification code itself. One real-world way a system can be entered or broken, told by four facts: cause (T Timeframe / U User / S service-platform / X meta covering all), true frequency (H/M/L/Rare), what the user is PROMISED to...
- [styling](Groups/Design/styling/SKILL.md) — Platform-neutral rules for writing NEW styling well on any stack (HTML/Web, Blazor, MAUI, Qt): per-module style scopes instead of monolithic files, role-named tokens as single source of truth, styling as a chain of layers with downward-only imports (values -> compiled tokens -> mixins/utilities/functions -> composed styles -> module scope; layer count is the project's call, never fixed by the skill; the topmost layer - pages - wears zero styling, thin builder/wrappers only; a closed variant contract with extend-never-bypass guardrails can do the work of layering itself), minimal layered utilities (card -> primary-card/secondary-card) with the expressive-naming law (the ambiguity trap: never call everything 'card' and patch per site - payment cards are not stats cards; module classes are file-private), build-time vs runtime discipline (class mappings, state attributes, runtime variables, inline only for calculated values), and composition helpers generalized (joiner, merge-on-conflict, variant registry). Goals: maximum reusability, minimum overriding, maximum flexibility, minimum inline styling. Boundaries: retrofit goes to styleup, redesign to accessible...
- [svg](animation/svg/SKILL.md) — Animate a static, flat SVG logo or icon (solid-fill <path> elements) with one of twenty-five animation styles: chrome-liquid, draw-fill, loading-loop, elastic-entrance, rise, iris, neon, pulse, flip, comet, focus (rack-focus, blur resolves), crt (TV power-on + scanlines), chroma (RGB ghosts converge), mosaic (tiled mas...
- [system-md](Groups/Pro/system-md/SKILL.md) — Produces and maintains SYSTEM-COMPONENTS.md for a confirmed application: an architectural inventory of the functional building blocks - subsystems, services, engines, integrations, processors, data systems, infrastructure - each with purpose, responsibilities, in/out-of-scope ownership, inputs and outputs, error handli...
- [techstack](techstack/SKILL.md) — Recommend a technology/framework/library/tech stack (mobile, web, backend, desktop, infra) in any language or platform via rigorous, current, requirements-driven evaluation, never memorized popularity. Discover candidates by topic search, never memory; classify by scope (library to meta-framework); weigh consolidated vs specialists; count only features the project will use. Surface parity is not implementation parity: probe how constantly-used capabilities are actually delivered (native vs re-implemented focus/forms, style hooks vs :deep()-style penetration) - equal feature lists hide the internals that make a pick feel wrong later. Weigh ecosystem, maintenance, API design, abstraction, quality, performance, mechanism and fit; state trade-offs honestly. Two modes: normal (primary tech plus close dependencies) and ultra (every real need: validation, retries, caching, observability)...
- [test](Groups/Code/test/SKILL.md) — General testing principles and ethics for any test the agent writes or reviews — unit, integration, contract, e2e, property, invariant, regression, or pipeline. Use whenever writing, refactoring, reviewing, or deciding what tests a change needs. Covers one-reason-to-fail, test vs verifier distinction, test data as cont...
- [thebest](Groups/Decision/thebest/SKILL.md) — Evidence-based option choice for THIS project: gather proof, hand the user a verdict - "this is likely best for us, based on these tests and research" - and stop; the USER decides (dtb is the reverse). Frame hard constraints first (stack, platform, license, AGENTS.md) and eliminate violating options visibly, before tes...
- [tldr](Groups/Talk/tldr/SKILL.md) — Answer in the shortest honest form instead of the usual full explanation — a word, a phrase, or one short sentence, with no preamble, hedging, or recap of what was done. Use this whenever the user says "tldr", "tl;dr", asks you to be brief, asks for a short answer, a one-word answer, "just tell me yes or no", "in short...
- [treat](Groups/Audit/treat/SKILL.md) — Evaluate how adopted tools and libraries want to be used and recommend structure or adaptations that respect their model - concepts, patterns, constraints. Reviews a named tool, or discovers model-heavy candidates from the dependency manifests when none is named. Version-aware: the model comes from docs for the install...
- [units-md](Groups/Viber/units-md/SKILL.md) — Generates, refreshes, and audits a project's UNITS.md - the index of reusable units an agent reads before implementing, so it extends what exists instead of building a parallel one. Each entry is one row of facts: name, responsibility, where it lives (a path that must exist), what it depends on, what it replaces, its s...
- [update](Groups/Code/update/SKILL.md) — Change something everywhere it lives, leaving no stale copy behind. Use for ANY change request: reword copy or docs; rename a term, identifier, file, route, or brand; change a value (price, limit, version, color, date), a behavior, or a rule; alter an interface or schema; swap a dependency; move a path; upgrade, deprec...
- [walkthrough](Groups/Talk/walkthrough/SKILL.md) — Slow, step-by-step mode for working through a big or confusing problem (a project, a decision, a messy situation) at a steady, unhurried pace instead of jumping straight to a solution. Use this whenever the user explicitly asks to "walk through" something, says "let's go slow," "slow down," "one step at a time," or inv...
- [watch-video](Groups/Video/watch-video/SKILL.md) — Watch a video by reconstructing it from frames plus a timestamped transcript, measure how objects move through it, and write structured markdown notes. Downloads with yt-dlp, extracts auto-scaled JPEG frames with ffmpeg, gets captions (Whisper API fallback), then reads frames and speech together. scripts/motion.py comp...

## Skills Details

### 1. [backend-db-debugging](./backend-db-debugging/SKILL.md)

- **Directory:** `backend-db-debugging`
- **Title:** Universal Backend & Database Debugging
- **Description:** Universal workflows, patterns, and templates for debugging backend services, databases, schema drift, migrations, environment loading, and module/package path resolution in ephemeral scratch environments.

**Overview & Usage:**
A project-agnostic, production-grade guide for inspecting database schemas, validating backend service layers, resolving workspace/monorepo module paths, dynamically discovering environment variables, and verifying database migrations safely in ephemeral scratch environments.

---

### 2. [dig-binary](./Groups/Search/dig-binary/SKILL.md)

- **Directory:** `dig-binary`
- **Title:** Universal Software Reverse Engineering & Black-Box Inspection
- **Description:** Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracing, network protocols, native binaries (PE, ELF, Mach-O), bytecode (JVM, Dalvik, Python, .NET), archives (ZIP, JAR, APK, TAR, ASAR), and local data stores. Use when source code is missing, obfuscated, or partial and internal models, APIs, hidden behaviors, or error causes must be uncovered.

**Overview & Usage:**
A comprehensive methodology and toolkit for reverse engineering modern software systems when source code is absent, incomplete, or obfuscated. It covers static artifact dissection (web bundles, native binaries, bytecode, archives), dynamic runtime tracing (process arguments, environment variables, I/O monitoring), network protocol reconstruction (REST, GraphQL, Protobuf/gRPC, WebSockets), and data storage analysis (SQLite, LevelDB, serialization models).

---

### 3. [blockiya](./Archive/Needs Work/blockiya/SKILL.md)

- **Directory:** `blockiya`
- **Title:** Blockiya Pattern Skill (Polyglot)
- **Description:** Enforce and apply the Blockiya architectural pattern for UI construction across component frameworks. Use when designing, reviewing, refactoring, or implementing orchestrators, features, pages, views, or project structure that must follow Blockiya rules — zero visual concerns in orchestrators, derive-before-pass, intents-only-upward, stereotypes, adapters, Strict utilities, growth signals, UML notation, or recommended feature-slice layout. Works for React, Vue, Svelte, Solid, and similar. Triggers include blockiya, Blockiya pattern, orchestrator block, strict blockiya, blockiya-core, derive before pass, fire intents and stop, zero styling blockiya, Atomic stereotype, Compound stereotype, behavioral primitive, adapter wrapper, UML notation, Vue Blockiya, framework-agnostic Blockiya.

**Overview & Usage:**
Apply the Blockiya architectural pattern rigorously across component frameworks (React, Vue Composition API, Svelte, Solid, Angular signals, etc.).

---

### 4. [check-violations](./Archive/Needs Work/check-violations/SKILL.md)

- **Directory:** `check-violations`
- **Title:** check-violations — Universal Invariant & Architectural Violation Auditing
- **Description:** Universal, language-agnostic agent skill to audit codebases, architectures, contracts, and visual/data invariants for rule violations using fast scriptable checkers (regex, lightweight rules, scriptable Python/JS/C#), reserving AST only when strictly necessary.

**Overview & Usage:**
Systematically audit, detect, and remediate violations of architectural invariants, coding contracts, visual fidelities, and data schemas across any technology stack. This skill abstracts inspection mechanisms—whether static analysis, runtime verification, or visual/structural diffing—into a universal, language-agnostic workflow.

---

### 5. [chekr](./Archive/Needs Work/chekr/SKILL.md)

- **Directory:** `chekr`
- **Title:** Chekr — SNDUK architectural checks
- **Description:** >- Run and remediate SNDUK Chekr architectural checks (@chekr/cli v0.3.2). Use when fixing check-violations, writing custom .chekr/checks, using @chekr-ignore blocks, pruning cache, auditing violations.json, or parallel per-package remediation.

**Overview & Usage:**
Custom static analysis for this monorepo. Rules live in `.chekr/checks/`; config in `chekr.config.js`. CLI: **@chekr/cli v0.3.2**.

---

### 6. [antipattern](./Groups/Audit/antipattern/SKILL.md)

- **Directory:** `antipattern`
- **Title:** Antipattern — investigate the project, document what to avoid
- **Description:** Investigates a software project, researches the engineering anti-patterns that matter for its stack, gathers evidence from code, architecture, business rules and dependencies, and documents which anti-patterns agents must avoid (usually as ANTIPATTERN.md). Findings are rated for impact and confidence separately, kept to what project evidence supports, and a clean audit is a valid result. Identifies, investigates, recommends and documents only. Do NOT use to fix, refactor or enforce rules, for general code review, or to change application behavior.

**Overview & Usage:**
Picks a mode from the request and what discovery finds (A: named scope, B: existing documentation, C: undefined), understands the project before judging it, researches candidates from the project's own stack, and investigates with evidence at the code, business, application, architecture and resource levels. Rules are specific, scoped and checkable, validated by `scripts/check_spec.py`; the user chooses which findings become rules, by answering `/inquire` or by marking a `[-]` checklist. Large trees are split into non-overlapping read-only passes whose results are re-verified, secret values are never reproduced, and nothing outside the spec and report is written.

---

### 7. [code](./code/SKILL.md)

- **Directory:** `code`
- **Title:** Code — brief, toolchain, docs-grounded, then write
- **Description:** Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates, in order: (1) a coding brief naming the app/module being coded and which stack-agnostic concerns it touches (interfaces, styling, a11y, navigation, forms, persistence, platform, concurrency, errors, build); (2) root inspection to detect the real toolchain (lockfile decides - bun.lock->bun, package-lock.json->npm, Cargo.lock->cargo, go.mod->go, uv/poetry.lock->python; binding project rules outrank inference); (3) targeted grounding of ONLY the touched concerns in CURRENT official docs for each ecosystem, via the `scrape` skill when available (cache + grep over re-fetching; WebFetch fallback), with trade-off questions to the user instead of silent picks. Use before scaffolding/editing source in any stack (TypeScript frameworks, Rust, Python, Go, ...) - it exists to stop coding from model memory that went stale. Chain with project standards skills when present.

**Overview & Usage:**
Never let a code edit start from memory. Every ecosystem drifts - Rust editions and trait APIs churn, Python frameworks deprecate whole patterns, JS component APIs get renamed between majors, Go stdlib gains context-aware variants - so a confident-looking API from training time is a latent bug. Three gates precede the first edit to source. The invariant: **grounding beats guessing, in any language.**

---

### 8. [contribute-agents](./Archive/contribute-agents/SKILL.md)

- **Directory:** `contribute-agents`
- **Title:** Contribute Agents
- **Description:** Coordinate multiple AI subagents that collaboratively work on a task, critique each other's reasoning, and converge on a documented conclusion. Use when the user wants two or more agents to discuss, debate, review, or jointly solve a problem (e.g. "have two agents argue about X", "run a panel of reviewers on this design", "make agents challenge each other's evidence") and wants a supervised discussion with an explicit termination condition and a final report.

**Overview & Usage:**
Orchestrate a supervised, multi-agent collaboration: several subagents work on the same task from different personas, communicate through a shared workspace, critically review each other instead of agreeing by default, and stop only when an explicit termination condition is met. You (the calling agent) act as the **Observer/Orchestrator** — you set up the collaboration, delegate the subagents, monitor them, and produce the final report. You never inject your own reasoning into their discussion.

---

### 9. [cross-platform-refactor](./Archive/Needs Work/cross-platform-refactor/SKILL.md)

- **Directory:** `cross-platform-refactor`
- **Title:** Cross-Platform Refactor
- **Description:** Framework for auditing and refactoring ANY multi-platform codebase (mobile/desktop/web, any language/framework — MAUI, React Native, Flutter, Kotlin Multiplatform, Swift, Electron, etc.) into one that is both fully cross-platform (no shared file secretly depends on one platform) and fully abstracted (no duplicated UI/interaction logic). Use when porting an app to new platforms, auditing for platform-leaking code, eliminating scattered 'if platform == X' conditionals, standardizing platform value/capability resolution, splitting desktop-vs-mobile UI layouts wrongly sharing one tree, or turning duplicated UI behavior into reusable components. Trigger even without the words 'cross-platform'/'abstraction' — e.g. 'make this work on mobile too', 'this only works on Windows', 'get rid of all the platform ifs', 'the mobile version looks wrong', 'why do we have three different confirm dialogs'.

**Overview & Usage:**
A framework for taking any multi-platform codebase from "leaky and duplicated" to "cleanly separated and reusable" — without a behavior rewrite, and without being tied to any single language or UI framework.

---

### 10. [prototype](./Groups/Design/prototype/SKILL.md)

- **Directory:** `prototype`
- **Title:** Prototype — JS-rendered, modular, URL-driven design prototypes
- **Description:** Build interactive design prototypes as small modular JS-rendered web projects. HTML pages are thin entry points (JS generates the interface); js/ and css/ split shared layers (_app.js, theme tokens) from per-page modules; a zero-dep dev server gives every page a clean direct URL (/funds) that works on entry, refresh, and query. State model: per-component state trees, deeply queryable — every interactive component (bottom sheet, modal, dropdown) exposes all its modes and sub-states as params (?open=plain|selection|loading|error, ?loading=header|input-fields|all, ?error=kind), init via the same render path clicks use, writing back while preserving unrelated state, with push/replace history and one central unit-tested helper owning mechanics. Keeps honest-state discipline (no fake skeletons, no trigger-less modes), never-lorem copy, frameless viewports, gallery index for 2+ screens, opt-in dead-control audit. Triggers: 'prototype this app/idea', 'make this a prototype'.

**Overview & Usage:**
The redesign of `design-mockup`: same promise — any screen state reproducible by a link — on a new architecture: JavaScript-rendered pages, module ownership, layered CSS, routed clean URLs, and centralized query-state mechanics. Includes a verified starter project (`assets/starter/`) with a passing state-helper test suite and working clean-URL server.

---

### 11. [display-to-user](./Groups/Special/display-to-user/SKILL.md)

- **Directory:** `display-to-user`
- **Description:** Use this skill whenever you (Claude) are running as a remote coding agent and the user asks you to "show", "display", "let me see", or "give me a link to see" what you've done to their project — the current state of files, or just the changes so far. Also trigger this if the user asks for a way to visually browse the project tree, preview a README or HTML file you produced, or share a live view of the repo with someone else. This spins up a local web viewer (file tree + git status + file preview) and tunnels it with ngrok so the user gets a real clickable URL back, rather than you pasting file contents into chat.

**Overview & Usage:**
Give the user (or someone they forward the link to) a live, browsable view of the project you're working in: a file tree, git change highlighting, and rendered previews of Markdown/HTML files — reachable from a public URL via ngrok, since you're running remotely and the user can't just open `localhost` themselves.

---

### 12. [docs-refactor](./docs-refactor/SKILL.md)

- **Directory:** `docs-refactor`
- **Title:** Docs Refactor
- **Description:** Reorganize a messy set of Markdown/text documentation into a clean, one-concern-per-file structure with a per-directory README acting as a local map. Use this when the user explicitly asks to refactor, reorganize, restructure, clean up, or de-duplicate a documentation set — phrases like "refactor these docs," "these files are a mess, can you reorganize them," "split this doc up," "our docs keep repeating the same stuff," or "give this folder a proper structure." Do not trigger on requests to just edit or fix content in a single existing file, or to write a brand-new doc from scratch — this skill is specifically for restructuring an existing multi-file (or single bloated-file) documentation set.

**Overview & Usage:**
A skill for taking documentation that has grown organically — usually AI-generated, usually across many sessions — and turning it into a set of files that each own exactly one concern, with a README at every directory level acting as a mini-map for whoever (human or AI) lands there next.

---

### 13. [document-db-attach-chain](./Archive/document-db-attach-chain/SKILL.md)

- **Directory:** `document-db-attach-chain`
- **Title:** Document DB Attach Chain
- **Description:** Batched, immutable, order-guarded cross-collection reads for document databases (RxDB, PouchDB, Dexie/IndexedDB, MongoDB) via an engine-agnostic attachOne/attachMany/attachGroup chain (attachTo(...).one().many().group()) built on a small per-engine FetchAdapter. Use whenever writing query code that combines documents from two or more collections/tables on RxDB, PouchDB, Dexie, or MongoDB — e.g. attaching a post's author, a user's related records, or "posts with comments and comment authors" style reads. Also use when asked for a "join" helper, an "ODM-style" or "Drizzle-like" relation utility for these engines, or when attachOne/attachMany/attachGroup/attachTo are named directly. On MongoDB, check "Choosing a strategy" first — this pattern is the fallback there, not the default (prefer $lookup). Do NOT use for one schema-declared relationship read repeatedly on an engine with native population (e.g. RxDB's .populate()) — see "When NOT to use this.

**Overview & Usage:**
No document database engine has a universal answer to cross-collection reads: some (RxDB, PouchDB, Dexie) have no server-side query planner spanning collections at all, so "join" only ever means "fetch, then fetch again, then merge in application code." Others (MongoDB) have a real native join (`$lookup`). This skill teaches one engine-agnostic pattern — batched, immutable, order-guarded — for the engines that need it, and is explicit about when an engine has something better.

---

### 14. [explain](./Groups/Talk/explain/SKILL.md)

- **Directory:** `explain`
- **Title:** Explain
- **Description:** Explain things in the easiest way to understand, defining any heavy or technical word the moment it's used — e.g. "zero-day (a security flaw nobody has fixed yet)". Use this whenever the user asks you to explain, simplify, clarify, break down, or "explain like I'm new to this", or says a previous answer was too technical, confusing, full of jargon, or hard to follow. Also use it proactively whenever your own answer is about to use a specialized or industry-specific term (security, finance, medicine, law, engineering, programming, etc.) and the user hasn't signaled expert familiarity with that field.

**Overview & Usage:**
The gap between an expert explanation and a clear one is almost never about the ideas — it's about the words. A correct, complete answer can still fail the reader if it's built out of terms they have to stop and look up. This skill's job is to close that gap: say the true thing, but say it so a smart, motivated person with no background in the topic can follow it on the first read.

---

### 15. [gitter](./gitter/SKILL.md)

- **Directory:** `gitter`
- **Title:** Gitter
- **Description:** Structures git workflow practices. Use when making any code change, committing, branching, resolving conflicts, splitting uncommitted work into atomic commits, opening or reviewing a PR, pushing, organizing parallel streams, cutting a release, choosing a semantic version bump, tagging, or writing a changelog.

**Overview & Usage:**
Git is the safety net. Treat commits as save points, branches as sandboxes, and history as documentation. With agents generating code at high speed, disciplined version control keeps changes manageable, reviewable, and reversible.

---

### 16. [how-to-do](./Groups/Agent/how-to-do/SKILL.md)

- **Directory:** `how-to-do`
- **Description:** Maintains a persistent .htd/ folder of generalized "how to do X in this codebase" procedures, so multi-step tasks are done the same correct way every time across sessions, agents, and models — instead of silently missing a step. ALWAYS check for a .htd/ folder at the repo root before starting ANY coding task, even if not mentioned, and consult it if present. Trigger this — don't wait to be asked — whenever the user says "add", "create", "change", "update", "refactor", "migrate", "wire up", or "integrate" something in a real codebase, including simple-sounding tasks like "add a table" (exactly what this exists for — never skip as too simple). Also trigger on any mention of "how-to-do", ".htd", or standardizing a workflow. After any nontrivial multi-file change in a repo with (or needing) .htd/, use this proactively to record a new procedure, patch an existing one, or confirm no update is needed — skipping this defeats the skill's purpose.

**Overview & Usage:**
A persistent record, local to each repo, of *how* to correctly perform recurring classes of change — so the procedure survives across sessions, across different agents, and across different models, instead of being re-derived (and silently getting a step wrong) every time.

---

### 17. [idk](./Groups/Talk/idk/SKILL.md)

- **Directory:** `idk`
- **Description:** Use this skill whenever the user directly signals they don't know what they want or need — phrases like "idk", "I don't know", "not sure what I need", "I don't know how to explain it", "I can't put it into words", or similar explicit expressions of uncertainty about their own intent. This is NOT a general clarifying-questions skill — it only triggers on that explicit signal, not on every vague or underspecified request. Once triggered, it guides the user from a fuzzy feeling toward a clear, named intent through a calm, jargon-free conversation, optionally looking around the project's code and docs for clues, and ends with a plain-language review that maps what the user said onto the standard technical term for it.

**Overview & Usage:**
The user knows *something* is off, or wants *something* to change, or has a feeling about the project — but they can't articulate it in technical terms, or they're not sure what they actually want yet. They say "idk" not because they're lazy, but because turning a vague feeling into a concrete, actionable request is genuinely hard, especially across a language or expertise gap. Forcing them to pick from a menu of technical options right away just adds friction on top of the uncertainty.

---

### 18. [investigate](./Groups/Search/investigate/SKILL.md)

- **Directory:** `investigate`
- **Title:** Investigation & Search
- **Description:** Investigate local files, codebases, datasets, and external Agent Skills. Use for high-precision searches across heterogeneous formats, diagnosing unfamiliar architectures, inspecting or comparing Skills from SkillsMP, GitHub, and other public sources, temporarily using or remixing external Skills, and synthesizing evidence into structured reports. Does not install external Skills unless explicitly requested.

**Overview & Usage:**
A comprehensive methodology and executable toolkit for investigating complex local filesystems, datasets, and diverse data formats, as well as inspecting, comparing, temporarily using, and remixing public Agent Skills. It emphasizes robust evidence gathering, high-throughput search, source integrity, progressive disclosure, and safe handling of untrusted external content.

---

### 19. [like-a-pro](./like-a-pro/SKILL.md)

- **Directory:** `like-a-pro`
- **Title:** Like-a-Pro Meta-Skill
- **Description:** Root meta-skill orchestrator that reproduces production-grade engineering standards and conventions across applications. Guides the complete lifecycle from Idea -> Details-Up -> App Boundary Confirmation -> Child Skills (language-handling, sql-handling, error-handling, ui-handling, system-creator, details-up); the first four are standalone skills that also work outside the lifecycle.

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

### 22. [packages](./Groups/Audit/packages/SKILL.md)

- **Directory:** `packages`
- **Title:** Packages — Duplicate Audit & Freshness (ecosystem-general)
- **Description:** One run, two jobs over a project's dependencies, in any ecosystem (JS/TS, Python, Go, Rust, JVM, .NET, Ruby, Elixir, …) and any project shape (single module, workspaces/monorepo, multi-manifest/polyglot repo). Job 1 audits duplicates/redundancy by classifying every dependency as explicit (imported) or implicit — installed and load-bearing without imports: toolchain compilers, native/link-time stubs, config plugins, entry-point-discovered packages, blank/side-effect imports, peer deps, codegen, type-only packages — flagging only what is neither. Job 2 checks up-to-date-ness with the ecosystem's native updater when one exists (`go mod tidy`-class, `bun update --latest`, `cargo upgrade`, `poetry show --outdated`, …), else context7/web/registry search — never memory — and always a before/after report for user approval first, with breaking-change checks on every major against the migration guide and the project's real usage.

**Overview & Usage:**
Answers "do we still need all of this?" and "is all of this still current?". Removals require surviving both the text-reference scan and the implicit-kinds checklist (metadata-discovered plugins and native stubs are invisible to grep and break at runtime, not compile time); updates land only after an approved current-vs-latest report grouped by patch/minor/major. `references/ecosystem-playbook.md` holds the per-ecosystem facts (manifests, implicit proofs, native tidiers/updaters, registry queries, verification chains); `references/audit-toolkit.md` holds the universal scan algorithm, a verified JS-family worked example, and the report templates. All tool names are illustrative — the skill's standing rule is to verify current tooling by search, since dependency tooling turns over fast.

---

### 23. [persona](./Groups/Agent/persona/SKILL.md)

- **Directory:** `persona`
- **Title:** Persona & Context Construction
- **Description:** > Construct deep, professional, context-aware personas for subagents of any role — not just a job title, but a full behavioral specification of how the agent thinks, investigates, judges quality, and communicates. Use this whenever building, prompting, or orchestrating a subagent (security reviewer, database engineer, testing engineer, frontend engineer, DevOps/SRE, technical writer, code reviewer, or any other domain specialist) and a generic "you are a senior X" persona would be too shallow. Especially relevant for multi-agent orchestration systems (e.g. contribute-agents) that need distinct professional perspectives per role, and for any task asking to "give this agent a persona," "make this agent think like a senior X," or "construct context for a subagent." The method is role-agnostic — it applies identically whether the role is testing, security, database, frontend, or something else entirely.

**Overview & Usage:**
Build a persona that makes a subagent **reason and behave like an experienced practitioner**, not one that makes it *announce* expertise. The test at every step is: would this text change what the agent notices, how it investigates, and what it accepts as evidence — or is it decorative?

---

### 24. [planner](./Groups/Code/planner/SKILL.md)

- **Directory:** `planner`
- **Title:** Planner
- **Description:** Enforce rigorous, systematic, language-agnostic planning before implementation. Captures the full request, first clarifies vague or slang-heavy language if needed, then generates structured hypotheses that surface explicit requirements plus professional reading-between-the-lines concerns, gathers local and web context, iterates with the user until hypotheses are approved, and finally produces a solid plan. Use in planning-mode or quest-mode, or whenever the user asks for a plan, architecture outline, implementation roadmap, or disciplined decomposition of a complex task. Triggers include planner, planning mode, quest mode, make a plan, rigorous plan, hypothesis-driven planning.

**Overview & Usage:**
Enforce a disciplined, hypothesis-driven, **universal** planning process. The skill is language-agnostic and technology-neutral (polyglot principles). It adapts to the current project and forces thorough coverage of both stated requirements and the professional concerns a senior engineer would notice between the lines.

---

### 25. [polyglot](./Groups/Generalize/polyglot/SKILL.md)

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

### 27. [scrape](./Groups/Crawl/scraping/scrape/SKILL.md)

- **Directory:** `scrape`
- **Title:** Scrape — full framework docs, locally
- **Description:** Fetch full framework documentation as clean local Markdown files. Commands per framework (currently `ionic` covering all guide pages + every API component page; capacitor/react/vue planned) plus `--auto` URL discovery for any Docusaurus-style docs site and explicit `--url` scraping, with a `--verify` mode that proves every page is reachable and server-rendered. Use whenever the agent needs authoritative external docs - e.g. Ionic component props/events/methods/CSS custom properties before building mobile UI, API reference lookups, or confirming doc URLs exist - instead of guessing from memory or fetching pages one by one.

**Overview & Usage:**
One script, `scripts/scrape.py` (Python 3, `requests` + `beautifulsoup4` only), that downloads complete documentation sets as Markdown and guarantees nothing silently: every failure mode (404, JS-rendered page, thin content) is reported.

---

### 28. [scraper-optimizer](./Groups/Audit/scraper-optimizer/SKILL.md)

- **Directory:** `scraper-optimizer`
- **Title:** Scraper Optimizer
- **Description:** Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory-bounded web scrapers and data ingestion pipelines across Python, Go, Node.js, Rust, C#, and Java.

**Overview & Usage:**
Design, profile, and optimize high-throughput web scrapers and stream pipelines that maintain a flat $O(\text{concurrency})$ memory footprint regardless of dataset volume ($O(N)$), preventing container OOM kills (Railway, Kubernetes, Fly.io).

---

### 29. [search-deeply](./Groups/Search/search-deeply/SKILL.md)

- **Directory:** `search-deeply`
- **Title:** Search Deeply
- **Description:** Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems problems. Use when the user requests very deep research, production-grade architecture analysis, lifecycle design, formal state machines, ownership models, race-condition handling, resource pools, platform constraints, failure-mode analysis, anti-patterns, or any study that must go far beyond shallow answers. Triggers include deep research, architecture study, implementation-oriented, formal state machine, ownership analysis, failure modes, anti-patterns, decision matrix.

**Overview & Usage:**
Conduct rigorous, multi-pass technical research that yields a single recommended, implementable architecture rather than a catalog of options. Separate documented facts from patterns and recommendations. Prefer primary sources. Always produce formal state machines, clear ownership models, race-condition defenses, failure-mode tables, anti-pattern analysis, a decision matrix, and a progressive practice exercise.

---

### 30. [senior-refactor](./Groups/Audit/senior-refactor/SKILL.md)

- **Directory:** `senior-refactor`
- **Title:** Senior Refactor: Zero-Coupling & Universal Multi-Platform Architecture
- **Description:** Universal multi-platform refactoring skill to decouple codebases across TypeScript/React Native, Go, Rust, Flutter, and C#/.NET. Eliminates inline preprocessor directives (#if PLATFORM) and runtime OS switch sprawl, establishes 3-tier unit hierarchies (UNITS.md), and swaps view layouts across desktop and mobile. MUST BE USED whenever refactoring client code for cross-platform readiness, resolving platform coupling, splitting partial classes or build tags by OS family, or converting ad-hoc components into base/specialization units. Examples: "refactor this to be platform independent", "eliminate #if WINDOWS", "split into platform files", "extract base and specialization unit", "implement view barrel layout swapping".

**Overview & Usage:**
A comprehensive, language-agnostic skill for transforming tightly-coupled, platform-locked client codebases into clean, decoupled, multi-platform architectures without breaking existing functionality.

---

### 31. [subagent](./Groups/Agent/subagent/SKILL.md)

- **Directory:** `subagent`
- **Title:** Professional Subagent
- **Description:** Create high-quality professional prompts for sub-agents. Use when the main agent needs to delegate work to a specialized sub-agent or worker. Produces a structured brief with hierarchical Context, precise Goal, How, Autonomy Bounds, and Output Contract so the sub-agent stays focused, never decides, and returns full raw results instead of summaries. Also covers pre-delegation environment consistency checks (to prevent sub-agent drift), requirements for exhaustive slightest-detail reporting back to the main agent, and detecting/mitigating race conditions between concurrently running sub-agents (e.g. shared scripts or files). Triggers include sub-agent, subagent, delegate, spawn worker, professional brief, task handoff, isolated prompt, parallel agents, concurrent agents.

**Overview & Usage:**
Generate a complete, self-contained brief that a main agent can hand to a sub-agent. The brief enforces isolation, clear boundaries, full evidence return, and zero decision-making authority.

---

### 32. [summarize](./Groups/Files/summarize/SKILL.md)

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

### 35. [tray-inspection](./Groups/Special/tray-inspection/SKILL.md)

- **Directory:** `tray-inspection`
- **Title:** Windows System Tray Inspection and Diagnostics
- **Description:** Comprehensive workflow and Win32 inspection procedures for Windows system tray items, including listing active tray icons, reading explorer toolbar memory, extracting native HICON bitmaps/PNGs, capturing high-DPI tray snips, and diagnosing tray state or badging issues.

**Overview & Usage:**
Windows system tray icons are managed by Windows Explorer across two distinct toolbar controls (`Shell_TrayWnd` for visible taskbar items and `NotifyIconOverflowWindow` for overflow flyout items). Inspecting, listing, or extracting icons from these areas requires cross-process Win32 memory scanning, toolbar message interception (`TB_BUTTONCOUNT`, `TB_GETBUTTON`), or GDI screen capture.

---

### 36. [crosscheck](./Groups/Audit/crosscheck/SKILL.md)

- **Directory:** `crosscheck`
- **Title:** crosscheck — blind orthogonal multi-agent discovery, then one reconciled verdict
- **Description:** Cross-check a task, codebase, or research question by blind orthogonal discovery: dispatch N isolated subagents (N >= 2), each engineered with a distinct cognitive lens — empirical/pattern-scanning, structural/behavioral, adversarial, product-pragmatist — none of them seeing the others' findings, hypotheses, or methods, then synthesize the reports into one reconciled document. Every finding is labelled by how it was found: consensus (corroborated by independent lenses), solitary (visible to only one lens), conflict (scouts disagree, tie broken by direct inspection), or dismissed (candidate proven a false positive). Use for "crosscheck this", multi-agent discovery, exhaustive audits where anchoring and shared blind spots are the risk, layer-violation or invariant sweeps, and when the orthogonal-scout agents are dispatched. Phase 0 pauses to disambiguate scope with the user first. Writes `.repertoire/findings/<topic>-findings.md`; scout reports stay in `.repertoire/agents/` unless `--cleanup`.

**Overview & Usage:**
Maximize analytical yield, error detection, and strategic discovery by dispatching **N isolated subagents (N ≥ 2)** engineered with **mutually orthogonal cognitive lenses, distinct prompt engineering disciplines, and independent investigative methodologies**. Subagents operate in total isolation with zero knowledge of their peers, eliminating cognitive anchoring, shared bias, and collective blind spots. The master orchestrator then cross-examines, triangulates, and fuses the discoveries into one findings document in which corroboration and lone-wolf findings are separated on purpose: agreement between independent lenses raises confidence, while a finding only one lens saw is kept and flagged as such rather than averaged away.

---

### 37. [type-up](./type-up/SKILL.md)

- **Directory:** `type-up`
- **Description:** >- Converts plain primitive types (string, number, boolean, etc.) into a professional typing system with semantic aliases, documentation, runtime validation, and tests. Use when the user asks for better types, semantic types, branded/NewType types, config typing, API contracts, PathLike-style aliases, schema validation, or professional typing for public surfaces.

**Overview & Usage:**
Turn **basic primitive fields** into a **documented, validated type system** that helps editors, authors, runtime safety, and CI — while remaining practical for consumers.

---

### 38. [unit-agent](./Archive/unit-agent/SKILL.md)

- **Directory:** `unit-agent`
- **Title:** Unit Agent (Junie CLI)
- **Description:** Command-line Junie interface for running code tasks. Use this skill to orchestrate Junie subtasks via CLI, especially when you need specific configurations like --plan, --brave, or custom project locations.

**Overview & Usage:**
Command-line Junie interface for running code tasks autonomously or interactively. Use this skill when you need to delegate a scoped task to Junie itself as a tool, or when the user describes a task that fits the "Junie as a CLI" pattern.

---

### 39. [up-agents](./Archive/up-agents/SKILL.md)

- **Directory:** `up-agents`
- **Title:** up-agents — Staggered Worker Pool + Reviewer
- **Description:** >- Launch staggered parallel worker subagents plus a delayed reviewer agent. Use when the user says up-agents, up agents, up-agents N + 1, spawn workers, worker pool with reviewer, or wants parallel implementation with a final QA pass.

**Overview & Usage:**
Orchestrate **N parallel worker subagents** with **staggered start delays**, then **1 reviewer subagent** that wakes last to build, test, and review.

---

### 40. [using-agent-skills](./Archive/using-agent-skills/SKILL.md)

- **Directory:** `using-agent-skills`
- **Title:** Using Agent Skills
- **Description:** Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.

**Overview & Usage:**
This repo keeps its skills in **`.cursor/skills/`**. Each skill is a directory with a `SKILL.md` (and optional `reference.md`, `references/`, `POWER.md`).

---

### 41. [visual-enhancer](./Archive/visual-enhancer/SKILL.md)

- **Directory:** `visual-enhancer`
- **Title:** Visual Enhancer
- **Description:** Audits any code that produces a visual/rendered output — web components (HTML/React/Vue/Svelte/CSS), design mockups, Storybook stories, CLI/TUI output (ink, blessed, yoga-layout, raw console output), or native UI layout code — and reports concrete, substantive visual/UX enhancements. Use this skill whenever the user invokes "/visual-enhance", asks to "enhance the visual", "improve the UI/UX", "review the design", "make this look better", "check for visual issues", or points at a screen/page/component/mockup/CLI output and asks what could look better — even if they don't use the words "visual enhancer" explicitly. Triggers on both general requests ("/visual-enhance" or "check the whole project") and targeted requests naming a specific file, component, folder, or page. Do NOT use for functional bug fixes, accessibility-only audits, or requests to build a new UI from scratch — this skill is for enhancing what already visually exists in code.

**Overview & Usage:**
Audits existing rendered/visual code and produces a written report of **substantive** visual/UX enhancements — never a redesign, never a list of cosmetic nitpicks. Output only, no code is modified by this skill; the user applies suggested fixes themselves.

---

### 42. [parity](./Groups/Design/parity/SKILL.md)

- **Directory:** `parity`
- **Title:** Parity — Visual Parity Testing & Autonomous Convergence & Autonomous Convergence
- **Description:** Framework for closing the gap between a design mockup (HTML/CSS, Figma export, or reference image) and what actually renders on a real device/emulator, for any UI framework. Covers the full pipeline (mockup + on-device capture, frame/chrome-noise normalization, similarity scoring, regional diagnosis) and an autonomous convergence loop that iterates capture→compare→diagnose→fix→rebuild without pausing for check-ins until threshold is met. Also covers: inventorying ItC (interact-to-change) components like dropdowns/drawers/modals and forcing their states via query params; dummy/placeholder mockup data needing fixtures so content mismatches don't masquerade as layout bugs; transition/animation ('smoothing') parity beyond static screenshots; and navigating past obstacle screens (splash/onboarding/permissions) without getting stuck. Use when the user wants pixel/visual parity with a design, an automated visual regression pipeline, or an agent that autonomously iterates toward a similarity score.

**Overview & Usage:**
A framework for measuring — and then autonomously closing — the gap between a design reference and what a real device actually renders. This is not a one-shot "take a screenshot and diff it" tool; it's built around a **loop an agent runs to convergence on its own**, the same way a human would iterate, but without needing to be prompted after every attempt.

---

### 43. [viz-planning](./Groups/Special/viz-planning/SKILL.md)

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
