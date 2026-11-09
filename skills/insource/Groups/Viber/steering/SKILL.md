---
name: steering
description: >-
  Interactive documentation architecture and steering taxonomy skill. Transforms project requirements
  or legacy documentation into the Six-Folder Steering Taxonomy (.steering/ with doctrine, stack,
  structure, product, the steering function folder, and playbook, plus shared-plus-area splitting)
  and outside-taxonomy folders (features, reference). Operates in four gated phases: (1) Contextual
  Discovery & Gap Interview, (2) Ordered Placement & Split-by-Role Analysis, (3) Distribution Plan
  Proposal & Approval Gate, and (4) Materialization & Index Synchronization. Use when asked to create
  or organize project documentation, apply the steering taxonomy, distribute requirements into
  .steering/, or migrate legacy docs.
when_to_use: >-
  The user wants to structure a new project's documentation, distribute raw requirements across
  .steering/ and docs/, audit or migrate existing documentation into the Six-Folder Steering Taxonomy,
  or invokes /steering.
argument-hint: "[project path, raw requirements, or 'migrate']"
---

# Steering — The Interactive Six-Folder Documentation Taxonomy Skill

> **Terminology rule (mandatory).** The steering folder whose directory name is `function` is always called the **steering function folder** in prose, headings, index files, commit messages, and agent output. Never write just "function" or "the function folder" for it, because in code "function" means a single function. The bare directory name `function/` appears only in file paths and layouts. Full specification: [`references/function.md`](references/function.md).

## 1. Purpose

The **steering** skill turns raw project requirements, spoken ideas, or messy legacy docs into a clean, non-overlapping documentation wiki governed by the **Six-Folder Steering Taxonomy**.

Instead of dumping files or guessing missing boundaries, **steering** follows a strict **4-Phase Interactive Workflow** that interviews the user to close gaps, designs an explicit **Distribution Plan** using the taxonomy's ordered decision flow and boundary tests, waits for user approval, and only then writes the files.

---

## 2. The Six Steering Folders & Outside-Taxonomy Homes

Every piece of project knowledge lands in exactly one canonical home (`One fact, one file`):

### A. Inside `.steering/` (Cross-Cutting Reference Layer)

Organized via the **shared-plus-area** pattern (`shared/` for facts true across *every* app/area, plus area folders like `web/`, `mobile/`, `admin/`, `backend/` that add area-specific files and **never override** shared files):

| Steering Folder | Question It Answers | What It Holds | Reference Spec |
| :--- | :--- | :--- | :--- |
| **`product/`** | What is the product, for whom, and why? | Product-level overview: purpose, target users, key features at a high level, business objectives. | [`references/product.md`](references/product.md) |
| **`stack/`** | What is this project built with? | Languages, frameworks, libraries, databases, hosting, external services stated as *"We use X"*. | [`references/stack.md`](references/stack.md) |
| **`structure/`** | How is the project organized? | Static shape: architecture boundaries, modules, directory trees, file/folder naming conventions. | [`references/structure.md`](references/structure.md) |
| **`function/`** (**steering function folder**) | How does the system work as a whole, beyond any one feature or part? | System-wide runtime functionality shared across features (`error-ux`, accessibility, lifecycles, shared upstream integrations, or the core capability the entire platform is built around). | [`references/function.md`](references/function.md) |
| **`doctrine/`** | How should this specific part or task be done, and what is mandated for it? | Guidelines and non-negotiable mandates for a specific component, layer, or activity (test quality, portfolio invariants, data deletion, API error format, CMS vs. code boundaries), with rationale. | [`references/doctrine.md`](references/doctrine.md) |
| **`playbook/`** | How do I operate this specific task? | Step-by-step operational recipes to *run* or *configure* a specific task (rotate tokens, seed data, run containers, release a version). | [`references/playbook.md`](references/playbook.md) |

### B. Outside `.steering/` (Governed by Placement Flow)

| Category | Typical Path | What It Holds | Deciding Rule |
| :--- | :--- | :--- | :--- |
| **Standing Idea** | `IDEA.md` | Plain-language project vision, inspirations, inclusions, exclusions (authored via `idea-md`). | Pre-spec project concept |
| **Feature Docs** | `docs/features/*.md` | Everything specific to a single feature. *Test: If feature X were deleted, would this doc still be true? If no -> feature doc.* | Placement Rule #1 |
| **General Guidance** | `AGENTS.md`, `CONTRIBUTING.md` | Project-wide, rarely updated workflow rules, package manager commands, agent obligations. | Placement Rule #2 |
| **Reference & Records** | `docs/reference/*.md`, `docs/decisions/*.md` | Data schemas (tables/columns), API endpoint references, ADRs, postmortems, glossaries, roadmaps. | Placement Rule #3 |

---

## 3. The 4-Phase Interactive Workflow

Never write `.steering/` files in the dark. Execute these four phases in order:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                    STEERING 4-PHASE WORKFLOW                           │
└────────────────────────────────────────────────────────────────────────┘
  Phase 1: Contextual Intake & Gap Interview
  • Read provided requirements, IDEA.md, or existing docs/codebase.
  • Check for missing taxonomy dimensions (areas/apps, shared vs. area
    boundaries, core capabilities, binding mandates, external integrations).
  • If gaps exist: ask concise, targeted questions and wait for answers.
                                  │
                                  ▼
  Phase 2: Ordered Placement & Split-by-Role Analysis
  • Run every requirement passage through the Ordered Decision Flow
    (references/placement.md).
  • Apply the Golden Rule: split any mixed passage by role (e.g., split
    a feature flow from its binding doctrine mandate or database schema).
  • Verify uncertain items against the 30-file Stress Test
    (references/stress-test.md).
                                  │
                                  ▼
  Phase 3: Distribution Plan Proposal (Approval Gate)
  • Present (or write as a draft) the complete Directory Topology tree
    (.steering/shared, .steering/<area>, docs/features, docs/reference)
    and the Section-by-Section Mapping Table showing exact destinations
    and boundary-test justifications.
  • STOP and wait for the user's explicit approval or adjustments.
                                  │
                                  ▼
  Phase 4: Materialization & Index Synchronization
  • Upon approval, write every steering and outside-taxonomy file
    following references/documentation-conventions.md:
    - One fact, one file (cross-reference instead of duplicating).
    - Every folder inside .steering/ gets an index.md (never README.md).
    - Describe behavior, not fragile mechanism, in doctrine.
  • Verify that every index.md matches the created files on disk.
```

---

## 4. Detailed Phase Instructions

### Phase 1: Contextual Intake & Gap Interview

1. **Inspect existing context**: Check if the user already provided a comprehensive requirement document, `IDEA.md`, prototype, or legacy `docs/` folder.
2. **Evaluate completeness against the Six Folders**:
   - **Areas (`layout.md`)**: Do we know the distinct application areas (e.g., `shared` + `web` + `admin`, or `shared` + `mob` + `ow` + `admin`)?
   - **Product (`product.md`)**: Are purpose, target users, and high-level objectives clear?
   - **Stack (`stack.md`)**: Are the core technologies known, or should stack files capture only the settled platform facts?
   - **Steering function folder (`function.md`)**: What are the system-wide capabilities, lifecycles, sync models, and external integrations?
   - **Doctrine (`doctrine.md`)**: What are the non-negotiable invariants and boundaries (e.g., cash never negative, what lives in code vs. CMS)?
3. **Ask only what is missing**:
   - If the user has not provided project details yet, ask for the project description or prompt.
   - If specific boundaries are ambiguous, ask **2 to 4 sharp, focused questions** to close the gaps.
   - If the user's prompt is already comprehensive and unambiguous, proceed directly to Phase 2 & 3.

### Phase 2: Ordered Placement & Split-by-Role Analysis

Read [`references/placement.md`](references/placement.md) and apply the **Ordered Decision Flow** to every topic in the requirements:

1. **Is it about exactly one feature?** -> Place in `docs/features/<feature>.md`.
   - *Boundary Test*: If feature X were deleted, would the document still be true? Yes -> **steering function folder**. No -> feature doc. Note that a capability the whole application is built around (e.g., virtual trading in a trading simulator, or video playback in a media app) is the system itself (**steering function folder**), not a single feature.
2. **Is it general project-wide how-to-work guidance?** -> Outside taxonomy (`AGENTS.md`, etc.).
3. **Is it a data schema, API wire reference, decision record (ADR), incident postmortem, glossary, or roadmap?** -> Outside taxonomy (`docs/reference/`, `docs/decisions/`, etc.).
4. **Otherwise, classify into one of the six `.steering/` folders**:
   - *"We use X"* -> `stack/`
   - *"Where things live and static layout"* -> `structure/`
   - *"What the whole product is, for whom, and why"* -> `product/`
   - *"How the system works as a whole across features"* -> `function/` (**steering function folder**)
   - *"Step-by-step recipe to run/operate one specific task"* -> `playbook/`
   - *"Guideline or mandated behavior for one specific part/layer"* -> `doctrine/`
5. **Apply the Golden Rule (Split by Role)**:
   - Never force a multi-concern requirement section into a single folder. Split the passage by role:
     - *Example*: A section on "Organizations & Leagues" that states *"Individuals cannot create organizations on their own; an Admin must approve and create them"* AND describes *"Users join leagues using a Party invite code"* splits into:
       1. `.steering/shared/doctrine/org-provisioning-policy.md` (the binding access-control mandate), and
       2. `docs/features/org-and-party-leagues.md` (the feature workflow).

### Phase 3: Distribution Plan Proposal (Approval Gate)

Before generating the final documentation suite, present the **Distribution Plan** (either inline in chat or saved to `docs/draft/distribution-plan.md` when requested):

1. **Directory Topology Tree**: Show the exact tree under `.steering/` (`shared/` and each `<area>/`, with `index.md` in every folder) and `docs/` (`reference/`, `features/`).
2. **Section-by-Section Mapping Table**: Columns for `Source Requirement`, `Extracted Concern / Fact`, `Target File Path`, and `Placement Rule / Boundary Test Justification`.
3. **Pause for Confirmation**: Explicitly ask the user to confirm or tweak the plan before executing Phase 4. (Only skip this pause if the user explicitly commands immediate execution).

### Phase 4: Materialization & Index Synchronization

Once the user approves the plan, create all files adhering strictly to [`references/documentation-conventions.md`](references/documentation-conventions.md) and [`references/layout.md`](references/layout.md):

1. **Every `.steering/` directory must have an `index.md`**:
   - Never use `README.md` inside `.steering/`.
   - Every `index.md` is a clean list of the folder's children with a one-line description per entry.
   - Include the mandatory **steering function folder** terminology reminder at the top of root, area, and `function/index.md` files.
2. **Shared-Plus-Area Integrity**:
   - Place facts true for *all* areas in `.steering/shared/`.
   - Place facts true for *one* area in `.steering/<area>/`.
   - Never create a file in `<area>/` with the same name to override a file in `shared/`.
3. **One Fact, One File**:
   - State each fact in its single canonical file and link to it from related files using relative Markdown links.
4. **Legacy Migration Mode (`/steering migrate`)**:
   - When migrating existing legacy docs, follow [`references/migration.md`](references/migration.md): never delete original sources (keep in place or archive), move passages without silent rewrites, flag conflicts openly, and verify 100% passage accounting.

---

## 5. Reference Library

Load these internal reference files whenever making placement, boundary, or formatting decisions:

| File | What It Governs |
| :--- | :--- |
| [`references/index.md`](references/index.md) | Master overview of the Six-Folder Steering Taxonomy |
| [`references/placement.md`](references/placement.md) | Ordered decision flow, boundary tests, Golden Rule (split by role), and outside-taxonomy rules |
| [`references/stress-test.md`](references/stress-test.md) | 30 worked file-placement examples and confusion diagnostics |
| [`references/layout.md`](references/layout.md) | `index.md` convention, `shared/` + `<area>/` non-override rules, and sample tree |
| [`references/documentation-conventions.md`](references/documentation-conventions.md) | The 7 writing rules for steering files (one fact one file, behavior over mechanism, cross-referencing) |
| [`references/product.md`](references/product.md) | Definition and test for `product/` |
| [`references/stack.md`](references/stack.md) | Definition and test for `stack/` |
| [`references/structure.md`](references/structure.md) | Definition and test for `structure/` |
| [`references/function.md`](references/function.md) | Definition, test, and mandatory terminology rule for the **steering function folder** (`function/`) |
| [`references/doctrine.md`](references/doctrine.md) | Definition, test, and examples for `doctrine/` |
| [`references/playbook.md`](references/playbook.md) | Definition and test for `playbook/` |
| [`references/migration.md`](references/migration.md) | Constraints and starting map for migrating legacy documentation |
