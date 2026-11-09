# Placement: Where Does a Document Go?

> This document governs which steering folder—or which non-steering home—a document or requirement passage belongs in: the Two-Tier ordered decision flow, boundary tests between folders, passage-level splitting, and worked examples. The folders themselves are defined in:
> - **Perception Tier**: [`product.md`](product.md), [`domain.md`](domain.md), [`capabilities.md`](capabilities.md), [`policy.md`](policy.md).
> - **Tech Tier**: [`stack.md`](stack.md), [`structure.md`](structure.md), [`function.md`](function.md) (steering function folder), [`doctrine.md`](doctrine.md), [`playbook.md`](playbook.md).
> See [`index.md`](index.md) for the master taxonomy map.

---

## 1. The Ordered Decision Flow

Ask these questions in sequence and stop at the first match:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        ORDERED DECISION FLOW                           │
└────────────────────────────────────────────────────────────────────────┘
  1. Is it about exactly ONE single feature?
     ➔ Outside the taxonomy: Feature Documentation (docs/features/<feature>.md).
       (Boundary Test: If feature X were deleted, would this doc still be true?)

  2. Is it general project-wide how-to-work guidance?
     ➔ Outside the taxonomy: AGENTS.md, CONTRIBUTING.md, or developer setup.

  3. Is it reference documentation or historical records?
     ➔ Outside the taxonomy: docs/reference/ (schemas, APIs), docs/decisions/
       (ADRs), incident records (postmortems), glossary, or roadmap.

  4. Otherwise, it is a STEERING document. Apply the Tier Test:
     "If the entire technology stack were rewritten, would this still be true?"

     ├── YES ➔ PERCEPTION TIER (perception/)
     │   ├── Why the product exists, target audience overview, business goals?
     │   │   ➔ perception/<area>/product/
     │   ├── Nouns, entities, roles, relationships, lifecycle states?
     │   │   ➔ perception/<area>/domain/
     │   ├── What the system provides or does across features (system verbs)?
     │   │   ➔ perception/<area>/capabilities/
     │   └── What is permitted/forbidden, or who has authority (must/may)?
     │       ➔ perception/<area>/policy/
     │
     └── NO ➔ TECH TIER (tech/)
         ├── Tools, runtimes, frameworks, external services ("We use X")?
         │   ➔ tech/<area>/stack/
         ├── Static layout, repo boundaries, directory trees, file naming?
         │   ➔ tech/<area>/structure/
         ├── System-wide technical runtime mechanisms (steering function folder)?
         │   ➔ tech/<area>/function/
         ├── Engineering guidelines & technical mandates for a specific part?
         │   ➔ tech/<area>/doctrine/
         └── Step-by-step operational recipe to run/configure a task?
             ➔ tech/<area>/playbook/
```

---

## 2. The Golden Rule: Split by Role at the PASSAGE Level

> **Golden Rule (Passage-Level Splitting).** Never force a document or requirement block into a single folder as a monolithic unit. Split by role at the level of the **passage**.

A raw requirement typically combines business intentions with technical implementation mandates. Evaluate each sentence or paragraph independently:

### Worked Split Example (Generic)

**Raw Source Passage:**
> *"A customer's virtual wallet balance must never go below zero. No overdraft or leverage in any tier. Concurrent purchase requests on the same wallet must be serialized or checked atomically."*

**Analysis & Placement:**
1. *"A customer's virtual wallet balance can never go below zero. There is no overdraft or leverage in any tier."*
   - Tier Test: Would remain true if the backend was rewritten in Rust, Python, or Go -> **`perception/`**.
   - Folder Test: States a non-negotiable business constraint / forbidden state -> **`perception/shared/policy/non-negative-balance.md`**.
2. *"Every purchase validates amount against the available balance before execution. Concurrent requests on the same wallet are serialized or checked atomically."*
   - Tier Test: Describes technical concurrency locking and database validation mechanics -> **`tech/`**.
   - Folder Test: Engineering mandate for a specific technical part (wallet ledger mutations) -> **`tech/shared/doctrine/balance-validation.md`**.
   - Link Direction: The technical doctrine file references the business policy it enforces (`tech` links to `perception`). The policy file does not mention the technical file.

---

## 3. Boundary Tests

### 3.1 `capabilities` vs `policy` (Perception Tier)

| Statement | Folder | Boundary Rationale |
| :--- | :--- | :--- |
| Every account starts with an initial virtual balance and can allocate it to external assets | `capabilities` | Describes what the system does / provides. |
| The balance can never go below zero; no overdraft or leverage permitted | `policy` | States a forbidden condition / constraint. |
| Operators can edit labels, tier names, and questions from the admin console without a deployment | `capabilities` | Describes what the console capabilities provide. |
| Scoring formulas and award triggers are strictly not editable by operators | `policy` | States authority limits and permissions. |
| An admin can create an organization from the console | `capabilities` | Console functional capability. |
| Individuals cannot create organizations; only an admin provisions them | `policy` | Forbidden action and authority assignment. |
| Standings refresh approximately once per minute | `capabilities` | System operational behavior across features. |

### 3.2 `domain` vs `product` (Perception Tier)

| Content | Folder | Boundary Rationale |
| :--- | :--- | :--- |
| A learning platform for personal finance built on gamification | `product` | Core purpose and definition of the product offering. |
| Audience: individuals across three tiers, guardians, and institutions | `product` | One-sentence audience segment listing pointing to `domain`. |
| Goal: demystify investing for all ages and drive adoption through leagues | `product` | Measurable business objective. |
| A tier is the experience level of an individual user; there are three; the youngest tier's account is created and monitored by a guardian | `domain` | Concept, entity definition, and structural relationship. |
| A group is joined with an invite code, belongs to an institution or family, and has standings | `domain` | Nouns and relational connections between entities. |
| XP converts to a level; a skill score is computed from diversification, task completion, and risk adherence | `domain` | Concepts and how they relate conceptually. |
| A league has three states: open, active, ended | `domain` | Entity lifecycle states. |
| The per-unit price of a fund is called the net asset value | Outside (Glossary) | Standalone vocabulary term without entity relationships. |
| The default starting balance is 100,000 currency units | `capabilities` | Parameter of system behavior, not an entity or product vision. |

### 3.3 `domain` vs `capabilities` (Perception Tier)

- **`domain`** holds nouns, entities, roles, and lifecycle states (*"A league has states: open, active, concluded"*).
- **`capabilities`** holds verbs and system actions (*"A league closes automatically on its end date and snapshots final rankings"*).

### 3.4 Business Decision Expressed as a Technical Fact

When a requirement states a technical arrangement that actually represents a business or strategic boundary, apply the Tier Test:
- *"We maintain an isolated database and distinct domain from the partner platform"* is a business independence decision that remains true across any future technical architecture.
- **Placement**: State it once in `perception/shared/policy/` (or `perception/shared/product/overview.md`).
- **`tech/shared/stack/platform.md`** records only the concrete tools in use (*"We use PostgreSQL 16"*).

---

## 4. Outside the Taxonomy

| Item | Destination | Why |
| :--- | :--- | :--- |
| Single feature specification | `docs/features/<feature>.md` | Fails the deletion test (if feature X is removed, only its doc is deleted). |
| User journeys spanning features | `docs/features/journeys/<journey>.md` (or within feature docs) | User journeys describe end-to-end user flows across multiple features; they live alongside feature documentation with links, not in a separate perception folder. |
| Single user stories | Backlog or inside single feature doc | Atomic user requirements belong inside the owning feature specification. |
| Relational table schemas, column DDL, API route wire payloads | `docs/reference/` | Data schemas and endpoint payloads are reference documentation. |
| Architectural Decision Records (ADRs) | `docs/decisions/` | Historical records explaining past technology evaluations. |
| Operational onboarding or general developer workflows | `AGENTS.md` / `CONTRIBUTING.md` | General, rarely changing guidance. |

---

## 4.1 Clarifying the Layers: Story vs Feature vs Journey vs Steering

To avoid misplacing user workflows and stories, distinguish these four conceptual levels:

1. **User Story** (*"As a user, I want to filter funds by risk rating"*):
   - A single, focused requirement inside one feature.
   - **Home**: Product backlog or a section inside the single feature document. Never in steering.

2. **Feature Document** (`docs/features/<feature>.md`):
   - Comprehensive technical and functional specification for **one** specific capability or component (e.g. `junior-savings.md` or `portfolio-leaderboard.md`).
   - **Test**: *Deletion Test*—if the feature were completely deprecated, this document would be deleted in its entirety without leaving broken holes in the core system taxonomy.

3. **User Journey** (`docs/features/journeys/<journey>.md` or alongside feature docs):
   - An end-to-end, multi-stage user workflow that traverses across **multiple distinct features**.
   - *Example*: *Guardian registers (`auth`) ➔ provisions child account (`guardian-system`) ➔ child completes onboarding quiz (`gamification`) ➔ child makes first mock investment (`trading-engine`) ➔ guardian views progress (`parent-portal`)*.
   - **Why NOT in Perception?** Perception defines the system's static worldview, core concepts (`domain`), overarching abilities (`capabilities`), and constraints (`policy`). A journey is a sequential narrative that choreographs features together; it references the features and links to them without duplicating their internal logic.

4. **Steering Documentation** (`perception/` & `tech/`):
   - System-wide domain architecture, cross-cutting policies, invariant business rules, and foundational technical engineering standards that govern the entire product ecosystem across all features.
