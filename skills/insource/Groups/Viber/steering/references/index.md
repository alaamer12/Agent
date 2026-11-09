# Steering Files: The Two-Tier Steering Taxonomy

> This is the entry point and master index of the **Two-Tier Steering Taxonomy**: the foundational architecture, the folders of both tiers at a glance, and links to all governing references.
> **Terminology reminder.** The directory name `function/` in the tech tier (`tech/<area>/function/`) is always referred to as the **steering function folder**, never just "function". Full rule: [`function.md`](function.md).

This document set defines how project knowledge is structured across two fundamental tiers:
- **`perception/` (Business Understanding)**: Conceptual, stable across technical rewrites and migrations.
- **`tech/` (Technical Architecture)**: Engineering standards, stack choices, structure, and execution (evolvable and versionable).

You must update this file whenever a document is added, removed, or moved.

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
| [`structure.md`](structure.md) | Tech tier: How is the repository, monorepo, and codebase statically organized? |
| [`function.md`](function.md) | Tech tier (**steering function folder**): What system-wide technical runtime mechanisms span features? |
| [`doctrine.md`](doctrine.md) | Tech tier: What engineering guidelines and technical mandates govern specific parts or layers? |
| [`playbook.md`](playbook.md) | Tech tier: What step-by-step operational recipes exist to run or configure specific tasks? |
| [`placement.md`](placement.md) | Tier Test, Ordered Decision Flow, boundary tests, and passage-level splitting |
| [`stress-test.md`](stress-test.md) | Diagnostic self-check: 30 representative test cases covering real-project defect patterns |
| [`layout.md`](layout.md) | Visual tree layout across both tiers, shared-plus-area non-override rules, and index.md conventions |
| [`documentation-conventions.md`](documentation-conventions.md) | Authoring rules: one fact one file across tiers, passage-level splitting, and cross-tier link rules |
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
| [`structure`](structure.md) | How is the codebase and repository organized? | *"X lives in directory Y with layout Z"* |
| [`function`](function.md) | How does the system work technically as a whole? | *"The platform executes technical mechanism X across features"* |
| [`doctrine`](doctrine.md) | What engineering guidelines and mandates apply to this part? | *"When implementing part X, you must satisfy invariant Y"* |
| [`playbook`](playbook.md) | How do I operate or run this specific task? | *"To execute X: step 1, step 2, step 3"* |

---

## The Tier Test and Cross-Tier Link Direction

- **The Tier Test**: For every passage, ask: *"If the entire technology stack were rewritten, would this passage still be true?"* (Yes: `perception/`, No: `tech/`).
- **Cross-Tier Link Direction**: Files in `tech/` link to their governing concepts in `perception/`. Files in `perception/` **never link to `tech/`**, ensuring perception documentation remains completely immune to technical refactoring or link rot.
