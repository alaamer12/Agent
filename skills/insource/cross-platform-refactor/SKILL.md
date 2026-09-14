---
name: cross-platform-refactor
description: "Framework for auditing and refactoring ANY multi-platform codebase (mobile/desktop/web, any language/framework — MAUI, React Native, Flutter, Kotlin Multiplatform, Swift, Electron, etc.) into one that is both fully cross-platform (no shared file secretly depends on one platform) and fully abstracted (no duplicated UI/interaction logic). Use when porting an app to new platforms, auditing for platform-leaking code, eliminating scattered 'if platform == X' conditionals, standardizing platform value/capability resolution, splitting desktop-vs-mobile UI layouts wrongly sharing one tree, or turning duplicated UI behavior into reusable components. Trigger even without the words 'cross-platform'/'abstraction' — e.g. 'make this work on mobile too', 'this only works on Windows', 'get rid of all the platform ifs', 'the mobile version looks wrong', 'why do we have three different confirm dialogs'."
---

# Cross-Platform Refactor

A framework for taking any multi-platform codebase from "leaky and duplicated" to "cleanly separated and reusable" — without a behavior rewrite, and without being tied to any single language or UI framework.

## Why this exists

Multi-platform codebases rot in exactly two independent ways, and most refactors only fix one of them:

1. **Cross-platformality breaks** — code that lives in a shared/platform-neutral location but secretly only works on the platform it was written for (an inline `if platform == X` buried in shared logic, a capability called unconditionally that crashes or no-ops on other platforms, an asset or animation that silently doesn't exist elsewhere).
2. **Abstractionality breaks** — the same interaction, dialog, formatter, or validation logic hand-rolled slightly differently at two or more call sites, because no one promoted it to a single reusable unit the first time it repeated.

A codebase can pass an audit for one of these and still be a mess by the other. Always check both, and treat them as genuinely separate defect classes with separate fixes — don't let one review pass stand in for the other.

**Read `references/principles.md` first, in full, before starting any audit or refactor.** It defines the vocabulary (Platform / Platform Family / Capability / Variant / Base Unit / Specialization / Barrel) that everything below assumes. For the fully-worked, unabridged version of this framework — including the Master-Slave execution model for delegating a large refactor across subagents and the full Mobile Architectural Parity Matrix — see `references/universal-guideline.md`.

## Workflow

### Step 1 — Establish ground truth before touching code

Don't rely on a stale mental model of the codebase or a previous session's findings. For the platform(s)/languages/frameworks actually in play:

- Identify the one canonical place platform identity is determined (or note that none exists yet — that's the first thing to create). If the language has no static type system, this includes checking whether a closed Platform Type (constant set) already exists — see `references/principles.md` §1a — before any barrel or selector is built on top of raw strings.
- Confirm how this specific framework actually resolves platform-suffixed files — auto-detected by the bundler, requiring manual build configuration, or an entirely different non-filename mechanism. See `references/utilities.md` §3 before assuming any convention "just works" (Expo/React Native auto-detects `.ios.`/`.android.`; .NET requires you to configure the `.csproj` yourself; Kotlin Multiplatform and Flutter don't use filename suffixes at all).
- Run a live search for the platform-conditional syntax native to this stack (see `references/utilities.md` for what that looks like per ecosystem) across the whole source tree. Every hit outside the canonical location is a candidate violation.
- Inventory what UI primitives and base components already exist (see `references/primitives.md`) — this determines whether the refactor plan needs a "build the missing primitive first" phase.

### Step 2 — Classify findings, don't just list them

For every hit from Step 1, classify it as one of:
- **Real violation** — a shared file/module with an actual platform-conditional branch, or a capability/asset called without a supported/unsupported distinction, or a block-level component sharing one layout tree across platforms that actually need different structure.
- **Already clean** — looks suspicious (e.g. history mentions a platform bug) but the current code has no actual branch. Document why and leave it — don't force a split that adds churn with no risk reduction.
- **Canonical-exempt** — the one legal platform-identity file, and the compile-time selector helper itself if its own internals require a native conditional.

Write findings incrementally as you find them (file, one-line description, suggested fix), not batched at the end — this lets triage and even the start of fixes happen before the audit finishes.

### Step 3 — Build/extend the toolkit before refactoring call sites

Almost every real violation reduces to one of a small number of shapes. Read `references/utilities.md` for the concrete pattern (with real-world examples across several ecosystems, so you can pick or adapt the one that fits this project's language/framework) and `references/examples-refactors.md` for full before/after code:

- A single value, constant, or factory that should differ per platform → a compile-time/build-time **select** helper.
- An optional feature some platforms don't have at all → a **capability** wrapper that makes "not supported" a first-class, explicit outcome.
- A shared module with several operations, only some of which vary → split into a shared shell + per-platform implementation files (this is the **file → files** refactor shape).
- A handful of small platform-only side effects living inline inside one file (very common in app startup/composition-root code) → extracted into a named platform-only hook, without necessarily creating new files for every single line (this is the **inside-the-file** refactor shape — see `references/examples-refactors.md` §2).
- A block-level UI component or full screen rendering meaningfully different content per platform → a thin host shell + one real layout implementation per platform family (the **view/layout barrel** pattern).

**If a required Base Unit or primitive doesn't exist yet, the plan must include creating or extending it as its own phase — before writing the specialization that depends on it.** See `references/primitives.md` for exactly how to scope that phase; skipping it is the single most common way this kind of refactor produces a worse mess than it started with (duplicated ad-hoc primitives invented under time pressure by whoever hits the gap first).

### Step 4 — Execute in small, verified slices

- Fix one violation (or one small group of closely related violations) at a time. Build/compile/run the relevant target after each change — a broken build should always be traceable to the single most recent change, not discovered three files later.
- This is a restructuring refactor, not a behavior rewrite: platforms that already work must keep working identically. New/not-yet-supported platforms are allowed to keep an explicit, honest no-op/placeholder — the goal is to make the codebase *ready* to receive a real implementation, not to necessarily write every platform's implementation in the same pass, unless the user asked for that.
- If delegating a slice to a subagent, give it full context (the exact violation, the file-layout convention from `references/utilities.md`, the relevant excerpt of `references/principles.md`) and verify its output yourself — re-run the platform-conditional search and the build, don't accept a self-report.

### Step 5 — Close the loop

- Update (or create) a running catalog of Base Units/primitives: mechanism, base type, purpose, status. This is what stops the next person from reinventing something that already exists.
- Re-run the full-repo search from Step 1 and confirm the only remaining hits are the canonical-exempt ones.
- If this refactor introduced a new toolkit shape not covered by `references/utilities.md`, note it — the toolkit is expected to grow as real codebases surface shapes beyond "single value" and "simple capability."

## Reference files

- **`references/principles.md`** — vocabulary and the three architectural pillars (Cross-Platformality file-separation, Abstractionality Base→Specialization hierarchy, View/Layout Barrel for composite components). Read this first, always.
- **`references/universal-guideline.md`** — the full unabridged framework this skill is distilled from, including the Master-Slave delegation model for large refactors, the Full Mobile Architectural Parity Matrix template, and the anti-pattern quick-reference table. Read when the condensed version in `principles.md` isn't enough, or when planning how to orchestrate a large multi-file refactor.
- **`references/utilities.md`** — the "select" and "capability" utility patterns, shown in concrete (not pseudo-only) form across several real ecosystems, to make clear the *concept* is what transfers, not any specific function name or syntax.
- **`references/examples-refactors.md`** — an index into the `examples/` directory: real, complete before/after project trees (not just inline code blocks) covering the file→files shape, the inside-the-file shape, the multi-member module split, and the layout-barrel shape. `view` the actual `examples/*/before/` and `examples/*/after/` directories, don't just read the index.
- **`references/primitives.md`** — how to inventory existing primitives/base units, decide whether a required one is missing, and scope a "create or extend the primitive" phase correctly (not too narrow, not gold-plated) before building on top of it.
