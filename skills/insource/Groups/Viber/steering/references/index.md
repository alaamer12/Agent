# Steering Files: The Two-Tier Steering Taxonomy

> This is the entry point and master index of the **Two-Tier Steering Taxonomy**: the foundational architecture, the folders of both tiers at a glance, and links to all governing references.
> **Terminology reminder.** The directory name `function/` in the tech tier (`tech/<area>/function/`) is always referred to as the **steering function folder**, never just "function". Full rule: [`function.md`](function.md).

This document set defines how project knowledge is structured across two fundamental tiers:
- **`perception/` (Business Understanding)**: Conceptual, stable across technical rewrites and migrations.
- **`tech/` (Technical Architecture)**: Engineering standards, stack choices, structure, and execution (evolvable and versionable).

You must update this file whenever a document is added, removed, or moved.

> **Mandatory authoring gate.** Every existing or planned tech directory receives its own evidence-backed interview and user-settled decision recap before examination, design, topology, mapping, or steering-file authoring. Follow [`documentation-conventions.md`](documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate) and the mandatory questions in each tech-folder reference. Existing code or documents are evidence, not a waiver.
> **Shared scope rule.** `shared/` is the minimalist canonical core and passes the [Universal Scope Test](layout.md#universal-scope-test) only when every confirmed area needs the same fact. Area files link to shared content and carry only their local delta; they never copy, shadow, or override it.
> **Drafting open-topic rule.** Disclose each new unanswered question immediately, use only the structured `Pending (Drafting)` marker, and close every marker before Draft [DR] completes. Follow the [Drafting Open-Topic Lifecycle](documentation-conventions.md#drafting-open-topic-lifecycle).

---

## Reference Documents

| Document | What It Governs |
| :--- | :--- |
| [`index.md`](index.md) | Master overview of the Two-Tier Steering Taxonomy, folder roster, and document index |
| [`product.md`](product.md) | Perception tier: Why does this product exist, for whom, and what are the objectives? |
| [`domain.md`](domain.md) | Perception tier: What entities, roles, and lifecycle states exist, and how do they relate? |
| [`capabilities.md`](capabilities.md) | Perception tier: What does the system provide or do across features? |
| [`policy.md`](policy.md) | Perception tier: What is permitted, forbidden, and who holds decision authority? |
| [`stack.md`](stack.md) | Tech tier: What tools, languages, frameworks, and databases is the project built with ("We use X")? |
| [`structure.md`](structure.md) | Tech tier: Static organization plus pattern-first rules for illustrative, current, and target trees |
| [`function.md`](function.md) | Tech tier (**steering function folder**): What system-wide technical runtime mechanisms span features? |
| [`doctrine.md`](doctrine.md) | Tech tier: What engineering guidelines and technical mandates govern specific parts or layers? |
| [`playbook.md`](playbook.md) | Tech tier: What step-by-step operational recipes exist to run or configure specific tasks? |
| [`placement.md`](placement.md) | Tier Test, Ordered Decision Flow, boundary tests, and passage-level splitting |
| [`stress-test.md`](stress-test.md) | Diagnostic self-check: 30 representative test cases covering real-project defect patterns |
| [`layout.md`](layout.md) | Visual tree layout, Universal Scope Test, minimalist shared and area-delta contracts, non-override rules, and index.md conventions |
| [`documentation-conventions.md`](documentation-conventions.md) | Authoring rules plus the mandatory per-tech-directory interview, decision ledger, and examination/design authoring gate |
| [`migration.md`](migration.md) | Rules and starting map for migrating legacy documentation into the Two-Tier taxonomy |

---

## The Folders at a Glance

### 1. Perception Tier (`perception/`)
*Answers business questions; remains stable across complete technical rewrites.*

| Folder | Question It Answers | Sentence Shape |
| :--- | :--- | :--- |
| [`product`](product.md) | Why does this product exist, for whom, and what are the objectives? | *"We serve X so that Y"* |
| [`domain`](domain.md) | What things exist in this world and how do they relate? | *"An X is a Y that belongs to Z"* |
| [`capabilities`](capabilities.md) | What does the system provide or do? | *"The system does X"* |
| [`policy`](policy.md) | What is allowed, forbidden, and who decides? | *"must / must not / may / only / who decides"* |

### 2. Tech Tier (`tech/`)
*Answers technical engineering questions; evolvable and optionally versioned (e.g. `tech/v1/`, `tech/v2/`).*

| Folder | Question It Answers | Sentence Shape |
| :--- | :--- | :--- |
| [`stack`](stack.md) | What is this project built with? | *"We use X for Y"* |
| [`structure`](structure.md) | How is the codebase organized, and how do new members join it? | *"Members of X live in Y and new members must satisfy Z"* |
| [`steering function folder`](function.md) | How does the system work technically as a whole? | *"The platform executes technical mechanism X across features"* |
| [`doctrine`](doctrine.md) | What engineering guidelines and mandates apply to this part? | *"When implementing part X, you must satisfy invariant Y"* |
| [`playbook`](playbook.md) | How do I operate or run this specific task? | *"To execute X: step 1, step 2, step 3"* |

---

## The Tier Test and Cross-Tier Link Direction

- **The Tier Test**: For every passage, ask: *"If the entire technology stack were rewritten, would this passage still be true?"* (Yes: `perception/`, No: `tech/`).
- **Cross-Tier Link Direction**: Files in `tech/` link to their governing concepts in `perception/`. Files in `perception/` **never link to `tech/`**, ensuring perception documentation remains completely immune to technical refactoring or link rot.
