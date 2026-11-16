# Viber Structure — The Canonical Project Layout

## 1. Overview

The Viber layout is the standard project structure for a vibe-engineered project: a small set of top-level
homes, each with one job, so every file has exactly one canonical place to live. It comes from what real
projects converge on — a desktop product whose `tools/` mixed Python, PowerShell and C# utilities with their
virtualenv kept **inside** the folder, and a mobile app whose `scripts/` held one verb per file
(`build` · `test` · `run` · `deploy` · `release`) while its generated `artifacts/` and agent `scratch/` were
fully gitignored but allowed to decay into flat piles. The layout keeps the parts that worked and disciplines
the parts that did not.

The layout is a **recommended default, not a cage** (Draft [DR] posture — `lifecycle.md` 1.2, `thaw`): a project may group
code under `src/` or keep it flat, may merge or skip a folder when the stack genuinely does not need it — but
the discipline of each home (organized subfolders, git treatment, disposable-vs-durable) stays.

### Core Principle

**One home per file; visibility where knowledge lives, disposability where output is born.**

Knowledge is committed and visible (`.viber/`); generated output is visible on disk but ignored by git
(`artifacts/`); the agent's mess is quarantined and always deletable (`scratch/`); operations and utilities
are code, committed with the rest (scripts/`, `tools/`); the root holds only root-files.

---

## 2. The Layout

```text
<project-root>/
├── root-files             README · AGENTS.md · .gitignore · LICENSE · manifests — and whatever
│                          else this project keeps at the root                (committed)
├── <code>                 whatever shape the project chose: flat root folders
│                          (Core/ Features/ Services/ …) or src/ — both normal (committed)
├── tools/                 reusable utilities, any language, envs inside (committed; envs/outputs ignored)
├── scripts/               the project's tasks and operations, any verbs   (committed)
├── artifacts/             every generated output                          (fully gitignored)
├── scratch/               the agent's temporary workspace                 (fully gitignored)
└── .viber/                knowledge umbrella + Viber state + skill state  (committed)
```

---

## 3. The Homes

### 3.1. Root-files — stay at the root

Root-files are a **category, not a menu**: `README.md`, `AGENTS.md`, `.gitignore`, `LICENSE`, lockfiles,
platform manifests — and whatever else this project has that belongs at its root. The standing question is
"does this file function or live by convention at the root?" (the root-file test, `supervision.md` 5.1),
not "is it on a list?". `AGENTS.md` additionally carries Viber's activation declaration. Viber never
relocates a root-file, and never prunes one: a new file that belongs at the root joins them.

### 3.2. Code — outside Viber's control

The product's source, in **whatever shape the stack and its author chose**. `src/` is one option, not a
standard: many real projects are **flat** — a row of feature folders (`Core/`, `Features/`, `Services/`,
`UI/`, `Models/`, `Platforms/`, …) sitting directly at the root beside the layout folders, which is the
natural shape for compiled stacks (a .NET app has no reason to hide its architecture inside `src/`) and for
any project that prefers its architecture visible from the first `ls`. Flat is a first-class citizen, not
a fallback. Viber neither reorganizes code nor pressures it into one directory. Build outputs (`bin/`,
`obj/`, `dist/`, `node_modules/`) are ignored, not relocated.

### 3.3. `tools/` — capabilities that help work on the project

Reusable utilities: capture scripts, image comparison, DB audits, icon generators, small test harnesses.
Language-blind — Python, PowerShell, C#, JavaScript, whatever fits the job, side by side.

- **Tools are code.** They are committed like the rest of the codebase.
- **Environments live inside.** A tool's dependencies stay in `tools/` — `tools/.venv` for Python, per-tool
  envs where needed — never a global install, never scattered at the project root. Env folders and build
  outputs are gitignored.
- **Tools answer "help me do X to this project"** (compare two screenshots, audit a database). If it reads
  like running the project itself, it is a script (3.4), not a tool.

### 3.4. `scripts/` — the project's tasks and operations

`scripts/` holds whatever operations the project runs — not only build/test/release. Two equivalent shapes
live here:

- **One verb per file** — `build`, `clean`, `test`, `run`, `watch`, `deploy`, or any verb the project
  invents: a shell, PowerShell, or Python entrypoint per operation. The folder exists because not every
  language supports scripts out of the box; `scripts/` gives every stack the same universal entrypoints.
- **Task definitions** — tasks written as code in the project's own stack: define the task, declare
  dependencies between tasks, run individually or in sequence, pass arguments, and reuse normal program logic
  instead of config sprawl. Every ecosystem has its native dialect — [Rake (Ruby)] · [Jake.js (JavaScript)] ·
  [invoke / Doit (Python)] · [mage / Taskfile (Go)] · [Invoke-Build (PowerShell)] · [MSBuild targets (.NET)] —
  and language-agnostic runners like [Make] or [Just] serve any stack. These are illustrative, not
  exhaustive: use whatever the stack's idiom offers, or hand-written task files where no runner exists —
  the shape (tasks, dependencies, sequencing, arguments) is the point, not the tool.

Either shape: tasks declare dependencies, compose in sequence, and take arguments; they are ordinary
committed code, not configuration files the agent must reverse-engineer.

- The boundary with `tools/`: scripts **are run** — they execute the project's operations and tasks,
  whatever the verb; tools **are used** — reusable capabilities that inspect, capture, generate, or compare,
  often called *by* scripts or by the agent. A one-off script that keeps earning its place as a capability
  graduates to `tools/`.

### 3.5. `artifacts/` — everything the project generates

Screenshots, emulator logs, audit dumps, verdict JSONs, built packages (`.apk`, installers), parity reports —
any file produced by running tools or scripts rather than written by a human.

It deliberately sits **outside `.viber`**:

- **Visible and accessible** — the first place to look for "what did the last run produce", not buried in the
  knowledge tree.
- **Fully gitignored** — output is reproducible; only the knowledge about it is committed.
- **Wholly disposable** — the folder can be deleted at any moment with zero loss.

**The discipline** (the failure seen in real projects: a flat pile of `emu-*.png`, `*.log`, `*.txt`
accumulating at the folder root):

- **Never flat.** One subfolder per producer or purpose: `artifacts/apk/`, `artifacts/logs/`,
  `artifacts/parity/<date>-<task>/`, `artifacts/audits/`.
- **Traceable.** Every artifact names its producer and run — subfolder for the what, date or task slug in the
  filename for the when — so an artifact can be followed back to the command and code that produced it.
- **Nothing durable lives here.** A finding from an audit is knowledge: it is written up into `.viber`
  (steering doc, decision note, or `settled.md`); the raw file stays in `artifacts/` only until the next
  purge. Anything that must survive deletion graduates first.

### 3.6. `scratch/` — the agent's workspace

The agent's quarantine for temporary work: fixture experiments, half-drafted commit parts, dumps, spikes.
Inside it the agent may do anything, no permission needed, because nothing there matters yet.

- **Fully gitignored**, like `artifacts/`.
- **Organized, not flat.** One subfolder per task: `scratch/<yyyymmdd>-<task-slug>/` or
  `scratch/<task-slug>/`. A flat pile is how the "delete anything" promise becomes dangerous.
- **Graduation rule.** Anything that outlives its task moves to its canonical home: code to the code tree, a
  kept output to `artifacts/`, knowledge to `.viber/` (a doc or `settled.md` row). What remains is safe to
  delete forever.
- `scratch/` is **never** a source of truth, and never referenced from committed documents.

### 3.7. `.viber/` — the knowledge umbrella

Everything else the project knows: the registry, the memory files, the flow definitions (`.viber/flow/`), and
every participating Skill's relocatable output — steering docs, features, plans, prototypes
(`supervision.md`, `memory.md`). Committed: that is the transparency the user chose.

The umbrella also absorbs **per-tool and per-skill state directories**. A project that does not use Viber
drifts toward root clutter — every skill that keeps state drops its own dot-folder at the root (an `/iwts`
run leaves `.iwts/`, an agent-team leaves `.subagents/`, and so on), and the root stops meaning anything.
Under supervision that class of relocatable state lives inside the umbrella instead: `.viber/.iwts/`,
`.viber/.subagents/` — each skill's state under `.viber/<its-normal-path>`. The skills themselves need no
knowledge of this: the agent redirects their writes exactly the way `supervision.md` 5.2 reroutes output.
The root stays reserved for root-files, code, and the layout folders — nothing else earns a place there.

---

## 4. Where Does a File Go?

| The file is… | Its home | Git |
|---|---|---|
| a root-file — front door, rulebook, ignores, platform manifest, **or whatever else lives at the root** | project root | committed |
| product source code | the code tree (flat or `src/`) | committed |
| a reusable capability that helps work on the project | `tools/` | committed (envs/outputs ignored) |
| an operation or task the project runs — any verb, script file or task-runner definition | `scripts/` | committed |
| produced by running something, useful to look at, useless to commit | `artifacts/<producer>/` | ignored |
| the agent's temporary mess | `scratch/<task>/` | ignored |
| knowledge: spec, decision, plan, prototype, prototype notes, memory | `.viber/…` | committed |

Two questions settle almost any case: *what is this file for?* (the table above) and *does it survive a
purge?* (if no → `artifacts/` or `scratch/`).

---

## 5. Git Treatment

The `.gitignore` must carry, at minimum (the `init` duty — see `vinit` skill → `references/init.md` 2.8):

```gitignore
artifacts/
scratch/
**/.venv/          # and any language-env equivalent inside tools/
<language build outputs: bin/ obj/ dist/ node_modules/ …>
```

- `artifacts/` and `scratch/` are **fully** ignored — no exceptions, no curated files inside them. If
  something inside deserves committing, it graduates to its canonical home first.
- `tools/`, `scripts/`, `.viber/` are committed; only the environment and output folders inside them are
  ignored.
- A declared-private path missing from `.gitignore` is a defect: fix the ignore line in the same change
  (`agents-md` privacy-sync duty).

---

## 6. Relationship to Supervision

`supervision.md` reroutes participating Skills' **relocatable knowledge** under `.viber/`. The layout refines
that rule: some relocatable outputs already have a canonical home **outside** `.viber`, and they go there
instead.

| A participating Skill produces… | It lands in |
|---|---|
| documentation, specs, decisions, plans, prototypes | `.viber/<normal-path>` (the umbrella) |
| run output — screenshots, logs, builds, verdicts | `artifacts/<producer>/` |
| temporary agent work — fixtures, spikes, drafts | `scratch/<task>/` |
| a utility or operation | `tools/` · `scripts/` |
| source code | the code tree |
| a root-file | the project root |

The umbrella gathers **knowledge**; the layout keeps *output* and *mess* in their visible, disposable places.
Knowledge about an artifact (what was found, what was decided) still goes under `.viber` — the artifact itself
does not.

---

## 7. Rules

- **One canonical home per file** (section 4's table); a file in two homes is a defect.
- **Root-files and code are never rerouted**, and the root stays reserved: root-files (whatever they are),
  the code tree (flat or grouped), and the layout folders — every skill-state dot-folder a project would
  otherwise grow at its root lives under `.viber/` instead (3.7).
- **`artifacts/` and `scratch/` are fully gitignored** and fully disposable; nothing canonical lives in them.
- **Never flat inside them**: one subfolder per producer (`artifacts/`) or per task (`scratch/`); traceable
  names (producer, task, date).
- **Tool environments stay inside `tools/`** — `tools/.venv`, per-tool envs — never global, never at the root.
- **Scripts run; tools assist.** Anything the project executes as an operation or task → `scripts/` (verb
  files or task-runner definitions, with dependencies, sequencing, and arguments); reusable
  inspect/capture/generate/compare capabilities → `tools/`.
- **Graduation before permanence.** A keeper output moves from `scratch/` to `artifacts/` or from
  `artifacts/` to `.viber/` (or the code tree); it does not stay put and get curated into the ignore rules.
- **The layout is the default, not a law** (DR posture): projects adapt the shape to their stack, and the
  discipline travels with each home, not the folder names.

---

## 8. Open Items

1. **Monorepo shape.** How the layout applies when the project is a workspace of apps (`apps/web`,
   `apps/admin`): one `artifacts/` and `scratch/` at the root (this document's default — simpler to purge),
   or per-app copies? The Kabrha Turborepo decision is a natural first test.
2. **`tools/` vs a `packages/` shared library.** A tool that ships inside the product is a package, not a
   tool; the boundary sentence in 3.4 is the seed of that rule.
