---
name: steering
version: 1.0.9
author: Amr
specialized: none
description: >-
  Interactive documentation architecture and steering taxonomy skill. Transforms project requirements
  or legacy documentation into the Two-Tier Steering Taxonomy (.steering/ with perception/ [product,
  domain, capabilities, policy] and tech/ [stack, structure, function, doctrine, playbook], plus
  shared-plus-area splitting with minimalist shared and area-delta semantics) and outside-taxonomy folders (features, reference). Operates in four
  gated phases with mandatory per-tech-directory interviews and pattern-first structure authoring:
  (1) Contextual Discovery & Architectural Grill-Me Interview, (2) Ordered Placement & Passage-Level
  Role Analysis, (3) Distribution Plan Proposal & Approval Gate, and (4) Materialization & Index
  Synchronization. Use when asked to create or organize project documentation, apply the steering
  taxonomy, distribute requirements into .steering/, or migrate legacy docs.
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
An agent must **never** unilaterally assume or invent directory structures, technology stacks, architectural boundaries, runtime mechanisms, engineering mandates, or operating procedures.

**Every existing or planned `tech/<area>/<folder>/` directory must complete its own Tech Directory Interview before the agent authors an examination, technical design, distribution topology, mapping, steering file, or draft for that directory.** Code and existing documents are evidence to question, not permission to skip the interview. The absence of an apparent architectural fork is not a waiver.

Follow the **`grill-me`** protocol: present the evidence, ask focused questions, offer options with pros and cons plus a recommendation when a real choice exists, and wait for the user's answer. Only an explicit user answer settles a decision. The shared gate and ledger contract are defined in [`references/documentation-conventions.md`](references/documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate); each tech-folder reference adds its mandatory question set.

### Drafting Open-Topic Rule (No Silent Pending)

`Pending` is valid during Draft [DR], but never silent. Announce each newly discovered question in chat immediately, state what it blocks, and ask whether to answer now or explicitly defer. Write only the structured `Pending (Drafting)` marker defined in [`references/documentation-conventions.md`](references/documentation-conventions.md#drafting-open-topic-lifecycle), never a bare `pending`, `not defined yet`, `TBD`, or placeholder. Deferral opens the marker; it does not close the topic. Replace wrong living content directly; never write `Moved to`, `retired`, or assumption labels. Before declaring Draft [DR] complete, close every marker through `close-topics`; any unresolved marker means drafting is incomplete.

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
| **`structure/`** | How is the codebase and repository statically organized? | *"Members of X live in Y and new members must satisfy Z"* | [`references/structure.md`](references/structure.md) |
| **`function/`** (**steering function folder**) | How does the platform work technically as a whole? | *"The platform executes technical mechanism X"* | [`references/function.md`](references/function.md) |
| **`doctrine/`** | What engineering guidelines and technical mandates apply to this part? | *"When implementing part X, you must satisfy invariant Y"* | [`references/doctrine.md`](references/doctrine.md) |
| **`playbook/`** | How do I operate or run this specific task? | *"To execute X: step 1, step 2, step 3"* | [`references/playbook.md`](references/playbook.md) |

**Structure authoring rule:** Treat trees as labeled current snapshots, approved targets, or illustrative examples—not mandatory layouts. Mark growable groups with `...` and a compact membership/extension rule; keep true closed sets closed. See [`references/structure.md`](references/structure.md#pattern-first-authoring-rule).

**Shared-folder rule:** `shared/` is the minimalist canonical core and passes the [Universal Scope Test](references/layout.md#universal-scope-test) only when every confirmed area needs the same fact. Area files link to shared content and write only their local delta; never copy, shadow, override, or merge area material into shared.

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
  Phase 1: Contextual Intake & Per-Directory Grill-Me Interview
  • Read requirements, IDEA.md, existing code, configs, and documentation.
  • Enumerate every existing or planned tech directory under shared/ and
    each confirmed <area>/: stack, structure, steering function folder,
    doctrine, playbook. Do not create or interview absent empty folders.
  • For EACH directory: inspect evidence, ask its mandatory questions,
    resolve contradictions, record decisions, and obtain user confirmation.
  • Mark the directory Settled or keep it Pending/Blocked. Evidence alone
    never settles it; a global "looks good" does not settle missing rows.
  • STOP: no examination or design authoring for an unsettled directory.
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
  • Verify every in-scope tech directory is Settled; show its decision
    recap and evidence in the Tech Directory Decision Ledger.
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

### Phase 1: Contextual Intake & Per-Directory Grill-Me Interview

1. **Inception**: For a new project, clarify vision, users, and domain purpose from `IDEA.md` or the user. For an existing system, inspect real code, configuration, and documentation; cite facts and never invent missing architecture.
2. **Enumerate the Tech Directory Decision Ledger**: Confirm `shared/` and every application area, then create one row per existing or planned `stack/`, `structure/`, steering function folder (`function/`), `doctrine/`, and `playbook/` directory. Mark an absent folder **Not applicable** only when the user confirms no content is planned.
3. **Interview Each Directory**: Follow [`references/documentation-conventions.md`](references/documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate) and the folder's questionnaire. Gather and label evidence, expose gaps and conflicts, ask focused questions, present choices with pros and cons plus a recommendation, and finish with that directory's decision recap.
4. **Settle Explicitly**: Mark **Settled** only after the user confirms the directory recap or explicitly delegates its decisions. Code, documents, lint, silence, agent recommendations, and global approval are not confirmation. Missing or deferred answers remain **Pending interview**, **Awaiting user**, or **Blocked**.
5. **Enforce the Gate**: For an unsettled directory, do not author its examination, technical design, topology, mapping, steering files, or speculative drafts. Read-only evidence gathering, questions, and the ledger are allowed. Never absorb unsettled content into a later phase.

### Phase 2: Ordered Placement & Passage-Level Role Analysis

Apply the ordered flow and passage-level splitting in [`references/placement.md`](references/placement.md):
1. Route single features, reference material, ADRs, and general project guidance outside the taxonomy.
2. Apply the Tier Test per passage: if it survives a complete technical rewrite, place it in `perception/`; otherwise place it in `tech/`.
3. Select the owning folder with its boundary tests and link technical implementations to their governing perception facts.
4. Apply the [Universal Scope Test](references/layout.md#universal-scope-test): use `shared/` only for every-area facts; otherwise use the owning area and keep local delta files linked to shared content.
5. Analyze or map technical passages only when their target directory is Settled.

### Phase 3: Distribution Plan Proposal (Approval Gate)

Draft and present the **Distribution Plan** before writing files:
1. **Gate Check**: Show the Tech Directory Decision Ledger and stop if any in-scope directory is not Settled.
2. **Directory Topology Tree**: Show the two-tier structure (`perception/` with its 4 folders, `tech/` with its 5 folders) across `shared/` and `<area>/`.
3. **Section-by-Section Mapping Table**: Columns for `Source Passage`, `Extracted Concern`, `Target Path`, `Boundary Test Justification`, and `Shared/Area Scope Justification`.
4. **Pause**: Require user approval before writing files.

### Phase 4: Materialization & Index Synchronization

Once approved, create all files adhering strictly to [`references/documentation-conventions.md`](references/documentation-conventions.md):
1. **Recheck the Gate**: Confirm every target tech directory remains Settled; reopen its interview if new evidence changes a settled decision.
2. **One Fact, One File Across Tiers**: A business policy is stated in `perception/policy/`. The engineering standard enforcing it lives in `tech/doctrine/` and links to the policy file.
3. **Strict Cross-Tier Link Direction**:
   - Files in `tech/` link up to `perception/`.
   - Files in `perception/` **never link to `tech/`** (preventing link rot when technical implementations change).
4. **`index.md` in Every Directory**: Every directory contains an `index.md` listing its contents. Never use `README.md` inside `.steering/`.
5. **Terminology Rule**: Inside `tech/`, the directory `function/` is always called the **steering function folder** in text and headers.
6. **Pattern-First Structure**: Label tree authority, illustrate growth with `...` plus a compact rule, and never turn example paths into mandates.
7. **Minimalist Shared Plus Area Delta**: Keep only every-area facts in `shared/`; area files link to the shared owner and contain only local additions. Never copy, shadow, override, or merge area content into shared.
8. **Drafting Closure**: Before declaring Draft [DR] complete, enumerate and close every `Pending (Drafting)` marker; any unresolved marker means drafting is incomplete.

---

## 5. Reference Library

| File | What It Governs |
| :--- | :--- |
| [`references/index.md`](references/index.md) | Master map of the Two-Tier Steering Taxonomy |
| [`references/placement.md`](references/placement.md) | Tier Test, Ordered Decision Flow, boundary tests, and passage-level splitting |
| [`references/stress-test.md`](references/stress-test.md) | 30 test cases diagnosing placement confusion and real-project defect patterns |
| [`references/layout.md`](references/layout.md) | Tree layout, Universal Scope Test, minimalist shared and area-delta contracts, and index.md conventions |
| [`references/documentation-conventions.md`](references/documentation-conventions.md) | Authoring conventions plus the mandatory per-tech-directory interview, decision ledger, and authoring gate |
| [`references/product.md`](references/product.md), [`domain.md`](references/domain.md), [`capabilities.md`](references/capabilities.md), [`policy.md`](references/policy.md) | Perception folder definitions, ownership tests, and examples |
| [`references/stack.md`](references/stack.md) | `stack/` definition, mandatory interview questions, and decision output |
| [`references/structure.md`](references/structure.md) | `structure/` definition, mandatory interview questions, and decision output |
| [`references/function.md`](references/function.md) | Steering function folder definition, mandatory interview questions, and terminology rule |
| [`references/doctrine.md`](references/doctrine.md) | `doctrine/` definition, mandatory interview questions, and decision output |
| [`references/playbook.md`](references/playbook.md) | `playbook/` definition, mandatory interview questions, and decision output |
| [`references/migration.md`](references/migration.md) | Rules and starting map for migrating legacy documentation |
