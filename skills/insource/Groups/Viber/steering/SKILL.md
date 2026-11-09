---
name: steering
description: >-
  Interactive documentation architecture and steering taxonomy skill. Transforms project requirements
  or legacy documentation into the Two-Tier Steering Taxonomy (.steering/ with perception/ [product,
  domain, capabilities, policy] and tech/ [stack, structure, function, doctrine, playbook], plus
  shared-plus-area splitting) and outside-taxonomy folders (features, reference). Operates in four
  gated phases with deep grill-me interviewing: (1) Contextual Discovery & Architectural Grill-Me Interview,
  (2) Ordered Placement & Passage-Level Role Analysis, (3) Distribution Plan Proposal & Approval Gate,
  and (4) Materialization & Index Synchronization. Use when asked to create or organize project
  documentation, apply the steering taxonomy, distribute requirements into .steering/, or migrate legacy docs.
when_to_use: >-
  The user wants to structure a project's documentation, distribute raw requirements across .steering/
  and docs/, audit or migrate existing documentation into the Two-Tier Steering Taxonomy, or invokes /steering.
argument-hint: "[project path, raw requirements, or 'migrate']"
---

# Steering — The Two-Tier Steering Taxonomy Skill

> **Terminology rule (mandatory).** The directory name `function/` in the tech tier (`tech/<area>/function/`) is always referred to as the **steering function folder** in prose, headings, index files, commit messages, and agent output. Never write just "function" or "the function folder", because in code "function" denotes a single code subroutine. Full specification: [`references/function.md`](references/function.md).
> (Note: Its business-tier counterpart is [`references/capabilities.md`](references/capabilities.md), which carries no naming ambiguity).

## 1. Purpose & Core Philosophy

The **steering** skill organizes project knowledge into a clean, non-overlapping documentation wiki governed by the **Two-Tier Steering Taxonomy**.

Every successful project begins with a clear idea before diving into deep technical implementations. To preserve clarity as a project grows, the taxonomy enforces a strict architectural boundary between **business understanding** and **technical engineering execution**:

1. **`perception/` (Business Understanding)**: Captures why the product exists, what domain entities and states exist, what the system provides, and what policies/rules govern it. This tier is **version-stable**; it remains true across complete technical rewrites, migrations, and refactoring.
2. **`tech/` (Technical Engineering & Architecture)**: Captures the concrete tools, static repository layouts, runtime technical mechanisms, engineering invariants, and operational runbooks. This tier is **evolvable** and can be versioned (e.g., `tech/` or `tech/v1/`, `tech/v2/`).

### ⚠️ Anti-Assumption Law (No Silent Decisions)
An agent must **never** unilaterally assume or invent directory structures, technology stacks, or architectural boundaries. Whenever an architectural fork is reached, the agent must formulate a decision round following the **`grill-me`** protocol (presenting options with pros & cons, a clear recommendation, and pausing for user confirmation).

---

## 2. The Folders Across Both Tiers

Every piece of project knowledge lands in exactly one canonical home (`One fact, one file`):

### A. Perception Tier (`.steering/perception/`)
*Holds conceptual and business knowledge. Survives complete technical rewrites.*

| Folder | Question It Answers | Sentence Shape | Reference Spec |
| :--- | :--- | :--- | :--- |
| **`product/`** | Why does this product exist, for whom, and what are the objectives? | *"We serve X so that Y"* | [`references/product.md`](references/product.md) |
| **`domain/`** | What things exist in this world and how do they relate? | *"An X is a Y that belongs to Z"* | [`references/domain.md`](references/domain.md) |
| **`capabilities/`** | What does the system provide or do across features? | *"The system does X"* | [`references/capabilities.md`](references/capabilities.md) |
| **`policy/`** | What is allowed, forbidden, and who decides? | *"must / must not / may / only / who decides"* | [`references/policy.md`](references/policy.md) |

> **Agent Mnemonic**: **`product`** is why and for whom; **`domain`** is nouns and relationships; **`capabilities`** is verbs the system performs; **`policy`** is modal verbs (must, may, forbidden).

### B. Tech Tier (`.steering/tech/`)
*Holds technical architecture, standards, and operational execution. Evolvable across versions.*

| Folder | Question It Answers | Sentence Shape | Reference Spec |
| :--- | :--- | :--- | :--- |
| **`stack/`** | What is this project built with? | *"We use X for Y"* | [`references/stack.md`](references/stack.md) |
| **`structure/`** | How is the codebase and repository statically organized? | *"X lives in directory Y"* | [`references/structure.md`](references/structure.md) |
| **`function/`** (**steering function folder**) | How does the platform work technically as a whole? | *"The platform executes technical mechanism X"* | [`references/function.md`](references/function.md) |
| **`doctrine/`** | What engineering guidelines and technical mandates apply to this part? | *"When implementing part X, you must satisfy invariant Y"* | [`references/doctrine.md`](references/doctrine.md) |
| **`playbook/`** | How do I operate or run this specific task? | *"To execute X: step 1, step 2, step 3"* | [`references/playbook.md`](references/playbook.md) |

### C. Outside the Steering Taxonomy
Content that sits alongside `.steering/` and is governed by [`references/placement.md`](references/placement.md):
- **Standing Idea**: `docs/IDEA.md` (or `IDEA.md` at root): plain-language concept and non-goals.
- **Feature Documentation**: `docs/features/<feature>.md`: detailed behavior of a single feature.
  - *User Journeys*: Documented within or alongside feature docs (e.g. `docs/features/<journey>.md`) focusing on sequence and hand-offs. They are **not** a perception folder.
- **Reference Documentation**: `docs/reference/`: relational database schemas, column DDL, and API wire contract payloads.
- **Decision & Incident Records**: `docs/decisions/` (ADRs) and incident postmortems.
- **General Guidance**: `AGENTS.md` / `CONTRIBUTING.md`: project-wide workflow rules and agent obligations.

---

## 3. The 4-Phase Interactive Workflow

Never author steering files on unconfirmed assumptions. Execute these four phases in order:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                    STEERING 4-PHASE WORKFLOW                           │
└────────────────────────────────────────────────────────────────────────┘
  Phase 1: Contextual Intake & Grill-Me Architectural Interview
  • Read provided requirements, IDEA.md, or existing codebase.
  • Identify all structural and architectural decision forks (Areas,
    folder layouts in structure/, framework flavors in stack/, boundaries).
  • Run interactive Grill-Me rounds using ask_question tool (or numbered
    rounds with pros/cons & recommendations). Never assume!
                                  │
                                  ▼
  Phase 2: Ordered Placement & Passage-Level Role Analysis
  • Apply the Tier Test: "If the tech stack were rewritten, is this still true?"
    (Yes: perception/, No: tech/).
  • Apply the Golden Rule: split mixed source material by PASSAGE, not by file.
  • Run boundary tests (capabilities vs policy, domain vs product, etc.).
                                  │
                                  ▼
  Phase 3: Distribution Plan Proposal (Approval Gate)
  • Present the complete Directory Topology tree showing perception/ and
    tech/ under shared/ and <area>/, plus docs/features/ and docs/reference/.
  • Present the Mapping Table showing Source Passage, Target Path, and
    Boundary Test Justification.
  • STOP and wait for explicit user confirmation.
                                  │
                                  ▼
  Phase 4: Materialization & Index Synchronization
  • Author steering files adhering to references/documentation-conventions.md:
    - One fact, one file across tiers (no duplicating facts).
    - Cross-tier link direction: tech links to perception; perception NEVER links to tech.
    - Every folder gets an index.md (never README.md).
    - In tech tier, include steering function folder reminder where required.
  • Verify that every index.md matches the created files on disk.
```

---

## 4. Detailed Phase Instructions

### Phase 1: Contextual Intake & Grill-Me Architectural Interview

1. **Idea-First Inception**:
   Every project originates from a core concept before expanding into technical specifics:
   - **Mode A: Inception / New Project**: Look for `IDEA.md` (or `docs/IDEA.md`). If absent or the project is in early conceptualization, clarify the core vision, target users, and domain purpose first. Ground the `perception/` tier before delving into technical architecture.
   - **Mode B: Existing System / In-Flight Codebase**: Inspect existing repository structure, configurations, and documentation. Never fabricate hypothetical directory trees or invent stack components—extract real facts from code and only interview on genuine architectural forks or missing policies.

2. **Detect Structural & Technical Forks**:
   - **Application Areas**: How many distinct areas exist (e.g. `shared`, `web`, `admin`)?
   - **Code Layout (`tech/<area>/structure/`)**: How is the codebase structured (e.g. monorepo packages, PVC layers)? **Never guess directory layouts!**
   - **Tech Stack (`tech/<area>/stack/`)**: What frameworks, languages, and databases are used?
   - **Tech Versioning**: Is the tech tier flat (`tech/`) or versioned (`tech/v1/`)?

3. **Execute Grill-Me Rounds**:
   - For every architectural fork, present: (1) Title, (2) Description with context, (3) Options with pros & cons, (4) Recommended pick with rationale.
   - **Wait for the user's answers.** Never proceed on assumed answers.

### Phase 2: Ordered Placement & Passage-Level Role Analysis

Apply the **Tier Test** and the **Passage-Level Golden Rule** from [`references/placement.md`](references/placement.md):

1. **Is it a single feature?** -> `docs/features/<feature>.md`.
2. **Is it a schema, API reference, or ADR?** -> Outside taxonomy (`docs/reference/`, `docs/decisions/`).
3. **Apply the Tier Test per passage**:
   - *If the entire technology stack were rewritten, would this passage still be true?*
   - **YES** -> **`perception/`**:
     - *Why, for whom, goals?* -> `product/`
     - *Nouns, entities, roles, lifecycle states?* -> `domain/`
     - *What the system provides/does across features (system verbs)?* -> `capabilities/`
     - *Allowed, forbidden, or who decides (modal verbs)?* -> `policy/`
   - **NO** -> **`tech/`**:
     - *Tools & infrastructure ("We use X")?* -> `stack/`
     - *Code/repo static layout & directory trees?* -> `structure/`
     - *System-wide technical runtime mechanisms?* -> `function/` (**steering function folder**)
     - *Engineering guidelines & technical mandates for a part?* -> `doctrine/`
     - *Step-by-step operational runbook?* -> `playbook/`

### Phase 3: Distribution Plan Proposal (Approval Gate)

Draft and present the **Distribution Plan** before writing files:
1. **Directory Topology Tree**: Show the two-tier structure (`perception/` with its 4 folders, `tech/` with its 5 folders) across `shared/` and `<area>/`.
2. **Section-by-Section Mapping Table**: Columns for `Source Passage`, `Extracted Concern`, `Target Path`, and `Boundary Test Justification`.
3. **Pause**: Require user approval before writing files.

### Phase 4: Materialization & Index Synchronization

Once approved, create all files adhering strictly to [`references/documentation-conventions.md`](references/documentation-conventions.md):
1. **One Fact, One File Across Tiers**: A business policy is stated in `perception/policy/`. The engineering standard enforcing it lives in `tech/doctrine/` and links to the policy file.
2. **Strict Cross-Tier Link Direction**:
   - Files in `tech/` link up to `perception/`.
   - Files in `perception/` **never link to `tech/`** (preventing link rot when technical implementations change).
3. **`index.md` in Every Directory**: Every directory contains an `index.md` listing its contents. Never use `README.md` inside `.steering/`.
4. **Terminology Rule**: Inside `tech/`, the directory `function/` is always called the **steering function folder** in text and headers.
5. **Shared-Plus-Area**: Files in `<area>/` add to `shared/`; they never override same-named files in `shared/`.

---

## 5. Reference Library

| File | What It Governs |
| :--- | :--- |
| [`references/index.md`](references/index.md) | Master map of the Two-Tier Steering Taxonomy |
| [`references/placement.md`](references/placement.md) | Tier Test, Ordered Decision Flow, boundary tests, and passage-level splitting |
| [`references/stress-test.md`](references/stress-test.md) | 30 test cases diagnosing placement confusion and real-project defect patterns |
| [`references/layout.md`](references/layout.md) | Tree layout, shared-plus-area non-override rules, and index.md conventions |
| [`references/documentation-conventions.md`](references/documentation-conventions.md) | The authoring conventions across both tiers and cross-tier link rules |
| [`references/product.md`](references/product.md) | Perception: Definition and tests for `product/` |
| [`references/domain.md`](references/domain.md) | Perception: Definition and tests for `domain/` |
| [`references/capabilities.md`](references/capabilities.md) | Perception: Definition and tests for `capabilities/` |
| [`references/policy.md`](references/policy.md) | Perception: Definition and tests for `policy/` |
| [`references/stack.md`](references/stack.md) | Tech: Definition and tests for `stack/` |
| [`references/structure.md`](references/structure.md) | Tech: Definition and tests for `structure/` |
| [`references/function.md`](references/function.md) | Tech: Definition and terminology rule for the **steering function folder** (`function/`) |
| [`references/doctrine.md`](references/doctrine.md) | Tech: Definition and tests for `doctrine/` |
| [`references/playbook.md`](references/playbook.md) | Tech: Definition and tests for `playbook/` |
| [`references/migration.md`](references/migration.md) | Rules and starting map for migrating legacy documentation |
