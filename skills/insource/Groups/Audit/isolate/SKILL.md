---
name: isolate
description: Isolate code that varies along one or more axes (platform, release channel such as canary/stable, audience or region, tenant, hardware tier, experiment cohort) so every difference has exactly one home and no file name has to carry two dimensions. Works on a module or a whole project. Small tasks are isolated directly, big tasks get a plan first, and new features are planned so their variants are isolated from the start. Use for "/isolate this project layers", "/isolate src/payments", "/isolate feature regional tax rules", and whenever the user mentions per-platform files, preprocessor or platform conditionals, canary/beta/stable builds side by side, regional or tenant-specific behavior, overlay or layer folders, or filename grids like Widget.Canary.Android, even without the word "isolate". Does NOT cover domain-boundary or microservice design, feature-flag or config-service setup, release and deployment pipelines, or refactoring unrelated to variation.
---

# Isolate

**Isolability** means code can be built, tested, replaced, shipped, or removed without editing code that belongs to a different axis of variation. This skill finds where that property is missing and designs the smallest structure that restores it. The idea stays the same whether the task is auditing old code, refactoring a module, or planning a feature that has not been written yet: make every difference live in exactly one place.

## Scope

**Covers**
- Inventory of the axes a module or project varies along, and classification of each axis.
- Choosing an isolation level per axis set: per-variant files, overlay directories, or layers.
- Designing seams, layer folders, selectors, registration, and the import direction between them.
- Isolating the identity of variants that must run side by side.
- Verification checks, and an ordered migration plan.

**Does not cover**
- Domain modeling, service boundaries, or module decomposition for its own sake.
- Setting up a feature-flag service, remote config, or experimentation platform (it only says when something is data and not code).
- Build, release, signing, or deployment pipelines (it only says what the build must include and exclude).
- Performance, security, or style cleanups with no variation involved.
- Choosing a language or framework. Output always follows the project's own idiom.

## Invocation

`/isolate <scope> [focus]`. Scope is `this project`, a path or module, or `feature: <description>`. Focus is optional, for example `layers`, `identity`, `audit`, `plan`, `refactor`.

- `/isolate this project layers` audits the whole project and designs its layer structure.
- `/isolate src/payments` audits and plans one module.
- `/isolate feature: regional tax rules` designs a feature so its variants are isolated before any code exists.

Modes are audit, plan, and refactor. Infer the mode, and ask once if it is unclear. What happens next depends on task size (see step 1 of the workflow): a small task is isolated directly with no plan, and only a big task gets a written plan and waits for approval before code is edited.

## Standing note on options

Every named option in this skill (axes, ecosystems, mechanisms, tie-break policies) is illustrative, written as `[example]`. It is not a closed menu. A hybrid or an unlisted answer is always acceptable, and a project's own idiom beats any example here. When a choice has real trade-offs, state them and let the user decide.

## Workflow

1. **Fix scope, mode, and size.** Detect the language, build system, and existing layout. Never impose another ecosystem's idiom. Then size the task.
   - **Small** means one component or a few files, one or two axes, no change to identity or build inclusion, no seam contract shared across modules, and no decision the user has not already made. Skip the plan and the template. Do steps 2 to 5 quickly in your head, make the change, run step 7, and end with a few lines: what was isolated, where each difference now lives, and what was checked.
   - **Big** means a whole project or several components, three or more axes, identity or build inclusion changes, a migration across modules, or a trade-off the user must decide (for example the ambiguity policy). Follow every step, deliver the plan, and wait for approval before editing code.
   - If a small task turns out to be big (a second axis appears, a shared contract must change), stop, say so in one sentence, and switch to the big path. When unsure, treat it as small and ask the user only if a real decision is blocking.
2. **Inventory axes.** Run `python scripts/scan_axes.py <path>` (add `--product NAME` when variants must coexist, and `--tokens axis=a,b` for project-specific values). Treat the output as evidence and confirm it by reading code. For a feature with no code yet, list the axes from the requirements instead. For a big task, record each axis in `assets/templates/isolation-plan.md`.
3. **Classify each axis** by four questions: Is it **total** (every variant must answer every seam) or **sparse** (overrides a few things)? Is it bound at **build time** or **runtime**? Does it **feed identity** (must coexist) or is it metadata? Is its value set **open** or fixed? Also check two things that are not code: if the binary would be identical, it is distribution; if only values differ, it is data.
4. **Escalate one level at a time.** Do not open with the final design. Start with the axes that vary today at the simplest level, name the constraint the next axis runs into, then give the next level. Read `references/levels.md`. If the user already has several axes, still show each constraint and its solution in order, so the reasoning is visible.
5. **Design in the project's idiom.** Read `references/layers.md` for the layer mechanism and `references/ecosystems.md` for how seams, build selection, and resolvers map to the project's language. Describe behavior first, then show code only as a sketch in the project's language.
6. **Isolate identity** when variants run together. Read `references/identity.md`.
7. **Verify.** Read `references/verification.md`. Run `python scripts/check_layers.py <layers-root> --base <base-dir> --profile axis=value,...` when a layers tree exists or has been created.
8. **Deliver.** For a big task, write the plan with `assets/templates/isolation-plan.md`. For a small task, give the short summary from step 1 instead. Worked examples of both are in `examples/walkthrough.md`.

## Principles

1. **One axis per filename.** A filename is a coordinate and holds one dimension. If a name needs two, policy has leaked into capability.
2. **Capability versus policy.** The environment supplies capabilities. Channel, audience, and similar axes supply policy on top. Policy never asks which environment it runs on.
3. **Total axes use names, sparse axes use priority.** Coordinates suit axes every variant must answer. Priority chains suit axes that override a few things.
4. **The base owns the contract.** Layers depend on the base. The base never references a layer, and layers never reference each other.
5. **Inclusion versus selection.** The build decides what exists in a binary. One visible resolver decides what is used now.
6. **Differences only.** A layer that copies a whole component is a fork. Keep seams small and named for what varies.
7. **Fail loudly.** A missing seam, an ambiguous overlap, or a duplicate registration is a build or startup error, never a silent production behavior.
8. **Do not over-isolate.** Values are data, an identical binary is distribution, and one axis needs only Level 1.

## Level guide

| Situation | Level |
|---|---|
| One axis varies and every variant must answer it | 1: per-variant files with a name suffix |
| A second sparse axis appears | 2: overlay directories |
| Three or more axes, or an axis must switch at runtime or wrap behavior | 3: layers |

Level 3 works for any number of axes from two upward and is worth its cost once Level 2 would start to form a grid.

## Reference map

Read only what the current step needs. All files are one level below this one.

- `references/levels.md`: the escalation story, scenario, solution, and constraint for each level.
- `references/layers.md`: layer key, registry, resolver, folder layout, import direction, registration.
- `references/ecosystems.md`: how to express seams and build selection per ecosystem, with multi-language sketches.
- `references/identity.md`: collision checklist for side-by-side variants, and what is not code.
- `references/verification.md`: checks, CI, and how to use the scripts.
- `assets/templates/isolation-plan.md`: the plan template, for big tasks only.
- `examples/walkthrough.md`: worked examples of a big audit, a feature plan, and a small direct change.
- `references/Layered Isolability Multi-Axis Code Organization.md`: Original document where this skill has been created inspired from it.