# Stress Test: Am I Confused About Where This Goes?

> This document is a self-check for document and passage placement under the **Two-Tier Steering Taxonomy**. It diagnoses confusion patterns, applies boundary tests from [`placement.md`](placement.md), and records how representative cases land across both tiers. See [`index.md`](index.md) for the master index.

---

## 1. How to Use This

1. Run the passage through the **Ordered Decision Flow** in [`placement.md`](placement.md).
2. If the passage mixes multiple concerns, **split by role at the passage level** before filing.
3. Apply the **Tier Test**: *"If the entire technology stack were rewritten, would this passage still be true?"* (Yes: `perception/`, No: `tech/`).
4. Select the matching folder in that tier. If two folders seem to fit, run the boundary test for that pair in [`placement.md`](placement.md).

---

## 2. Signs You Are Confused (Defect Patterns from Real-Project Tests)

| Sign / Defect Pattern | What It Usually Means | Rule That Resolves It |
| :--- | :--- | :--- |
| **Mixed rule plus enforcement** (*"Wallet cannot be negative, enforce with row lock"*) | A business constraint combined with a technical implementation mechanism. | Split by passage: business rule to `perception/policy`, technical locking mandate to `tech/doctrine`. |
| **Authority boundary plus implementation** (*"Operators cannot edit formulas; implemented in code"*) | A governance policy mixed with code architecture. | Split by passage: governance limit to `perception/policy`, code ownership standard to `tech/doctrine`. |
| **Dependency plus token lifecycle** (*"SNDUK provides prices via bearer token refresh"*) | Strategic data source integration mixed with technical protocol details. | Split by passage: partner provider relationship to `perception/capabilities`, technical auth refresh lifecycle to `tech/function`. |
| **System isolation boundary plus repository tree** | Business autonomy decision mixed with static monorepo directory layout. | Split by passage: system independence to `perception/policy` (or `product`), monorepo tree to `tech/structure`. |
| **Module list written as a folder tree** | Domain concepts and functional modules disguised as file paths. | Functional capabilities belong in `perception/capabilities`; actual file/directory trees belong in `tech/structure`. |
| **Business decision inside a stack file** (*"We use separate DB from partner"*) | A strategic boundary stated as a technical fact. | Move strategic decision to `perception/policy`; keep `tech/stack` strictly stating *"We use PostgreSQL"*. |
| **Mirroring technical folders into perception** | Forcing `stack`, `structure`, or `playbook` into `perception/`. | Forbidden: Perception defines only `product`, `domain`, `capabilities`, `policy`. |
| **Bloated product overview** | Listing every tier, entity, and state in the product overview. | Keep `product` concise (one sentence per audience pointing to `domain`); move entity and concept depth to `perception/domain`. |

---

## 2.1 The 8 Real-World Mixed Cases (Real-Project Test Benchmark)

During the real-world validation test across 51 documentation files, the agent misclassified files by treating each file as an indivisible monolithic unit rather than splitting at the passage level. Below are the 8 canonical mixed cases, the root cause of confusion, and their exact two-tier resolutions:

### Case 1: `portfolio-invariants`
- **Confusion**: Combining business financial constraints with database concurrency mechanics.
- **Passage A (Perception)**: *"A user's virtual wallet cash balance can never become negative; no leverage or overdraft is allowed across any tier."* ➔ **`perception/policy/non-negative-cash.md`** (Business invariant).
- **Passage B (Tech)**: *"Every purchase validates amount against balance. Concurrent debit requests on the same wallet are serialized via atomic row-level locks or transaction isolation."* ➔ **`tech/doctrine/balance-validation.md`** (Engineering mandate for data layer).

### Case 2: `code-owned-scoring-and-medals`
- **Confusion**: Mixing operator governance permissions with code ownership standards.
- **Passage A (Perception)**: *"Operators cannot edit or customize the Skill Score formulas or medal award criteria from the admin console."* ➔ **`perception/policy/scoring-governance.md`** (Operator entitlement & authority limits).
- **Passage B (Tech)**: *"Skill Score calculation equations and medal qualification rules are code-owned (hardcoded in repository algorithms and modified only via code pull requests)."* ➔ **`tech/doctrine/code-owned-logic.md`** (Technical engineering mandate).

### Case 3: `periodic-sync`
- **Confusion**: Conflating product freshness cadence with transport protocol design.
- **Passage A (Perception)**: *"Leaderboard standings and portfolio valuations are not real-time; they update periodically on a 1-minute cadence."* ➔ **`perception/capabilities/periodic-sync.md`** (System operational capability).
- **Passage B (Tech)**: *"The client refrains from opening WebSocket rooms; periodic synchronization is achieved via lightweight client polling or scheduled background workers."* ➔ **`tech/doctrine/polling-over-sockets.md`** (Technical communication pattern).

### Case 4: `snduk-integration`
- **Confusion**: Blending external business dependency with token lifecycle recipes.
- **Passage A (Perception)**: *"The platform relies on Snduk as the official authoritative source of truth for fund registry data and NAV pricing."* ➔ **`perception/capabilities/external-fund-data.md`** (External domain integration capability).
- **Passage B (Tech)**: *"Client handles HTTP 401 Unauthorized via silent token refresh interceptors."* ➔ **`tech/function/snduk-token-refresh.md`** (Steering function folder: runtime mechanism).
- **Passage C (Tech)**: *"Step-by-step procedure for rotating expired API keys in production."* ➔ **`tech/playbook/rotate-snduk-token.md`** (Operational recipe).

### Case 5: `repo-layout`
- **Confusion**: Merging business domain autonomy with static monorepo layout.
- **Passage A (Perception)**: *"The application maintains absolute isolation from partner services, preserving operational independence."* ➔ **`perception/policy/system-autonomy.md`** (Strategic policy).
- **Passage B (Tech)**: *"Monorepo workspace organization, package boundaries (`/apps`, `/packages`), and import alias configurations."* ➔ **`tech/structure/repo-layout.md`** (Physical directory layout).

### Case 6: `admin-tree`
- **Confusion**: Formatting operational capabilities as a file directory tree.
- **Passage A (Perception)**: *"The admin console provides 8 operational modules: Organization Provisioning, CMS Content Control, User Auditing, Tier Config..."* ➔ **`perception/capabilities/admin-operations.md`** (Operational business capabilities).
- **Passage B (Tech)**: *"The physical directory structure of the admin portal pages and components (`/src/pages/admin/...`)."* ➔ **`tech/structure/admin-tree.md`** (Directory and component tree).

### Case 7: `platform` (in `stack/`)
- **Confusion**: Stating an architectural independence boundary as a tool list.
- **Passage A (Perception)**: *"The platform runs on an independent database and dedicated top-level domain separate from the parent company."* ➔ **`perception/policy/platform-isolation.md`** (Business isolation rule).
- **Passage B (Tech)**: *"Database: PostgreSQL 16. Runtime: Node.js / Bun. Language: TypeScript."* ➔ **`tech/stack/platform.md`** (Pure tool roster naming concrete technologies).

### Case 8: `admin-framework` (in `stack/`)
- **Confusion**: Writing capability descriptions in `stack` without naming actual technologies.
- **Resolution**: A file in `tech/stack` that only describes what the admin UI can do without naming frameworks or libraries is misplaced. Capability prose belongs in **`perception/capabilities`**. `tech/stack` strictly enumerates concrete tools (e.g. *"Vue 3, Tailwind CSS, Pinia"*).

---

## 2.2 The Reference Benchmark Files from Real Testing

When reviewing documentation sets, use these tested baselines as standard points of comparison:

- **Pure Business Benchmark (7 Files)**:
  - `overview.md` ➔ `perception/product`
  - `org-provisioning-policy.md` ➔ `perception/policy`
  - `virtual-trading-engine.md` ➔ `perception/capabilities`
  - `age-tier-adaptation.md` ➔ `perception/capabilities` (with tier definitions in `domain`)
  - `game-identity-and-audio.md` ➔ `perception/capabilities`
  - `dynamic-cms-authority.md` ➔ `perception/capabilities`
  - `localization-and-regions.md` ➔ `perception/capabilities`
- **Pure Tech Benchmark (3 Files)**:
  - `configure-snduk-token.md` ➔ `tech/playbook` (Step-by-step configuration runbook)
  - `client-framework.md` ➔ `tech/stack` (Concrete frontend tool roster)
  - `client-tree.md` ➔ `tech/structure` (Physical client directory and component tree)

---

## 3. Representative Placement Table

| # | Topic / Passage | Tier | Destination | Deciding Rule |
|---|---|---|---|---|
| 1 | Product purpose, audience summary, and business goals | Perception | `product` | Whole-product overview |
| 2 | Definition of user tiers, guardian-child links, and concepts | Perception | `domain` | Nouns, entities, and structural relationships |
| 3 | Group competition lifecycle states (open, active, ended) | Perception | `domain` | Lifecycle states of a business entity |
| 4 | Core asset valuation engine and return calculations | Perception | `capabilities` | Core system capability spanning features |
| 5 | Periodic multi-user standing refresh (once a minute) | Perception | `capabilities` | Cross-feature system behavior |
| 6 | Wallet cash balance can never become negative | Perception | `policy` | Forbidden state / business invariant |
| 7 | Individuals cannot create organizations; only admin provisions them | Perception | `policy` | Authority boundary and entitlement rule |
| 8 | Scoring formulas and medal thresholds cannot be edited by operators | Perception | `policy` | Operator governance limitation |
| 9 | Strategic decision to maintain an isolated database from partner platform | Perception | `policy` (or `product`) | Business independence decision (Tier Test) |
| 10 | User journeys spanning multiple features | Outside | `docs/features/<journey>.md` | Sequence across features; lives with feature docs |
| 11 | Single feature specification (e.g. child savings goals) | Outside | `docs/features/<feature>.md` | Single feature scope (deletion test) |
| 12 | Relational database schema, tables, and column DDL | Outside | `docs/reference/` | Data schema reference documentation |
| 13 | Upstream partner API endpoint contract and wire payloads | Outside | `docs/reference/` | API reference documentation |
| 14 | Architectural Decision Record explaining PostgreSQL choice | Outside | `docs/decisions/` | Historical decision record (ADR) |
| 15 | Technologies and libraries in use ("We use TypeScript and Vue 3") | Tech | `stack` | Tool roster ("We use X") |
| 16 | Monorepo package boundaries and workspace layout | Tech | `structure` | Static repository organization |
| 17 | Client-side Page-View-Component (PVC) directory tree | Tech | `structure` | Static code and component layout |
| 18 | System-wide error handling and client feedback UX | Tech | `function` | Steering function folder: technical runtime mechanism |
| 19 | Partner API token refresh and authentication lifecycle | Tech | `function` | Steering function folder: technical integration mechanism |
| 20 | Atomic row-locking and transaction isolation on ledger debits | Tech | `doctrine` | Engineering mandate for a specific technical part |
| 21 | Test quality invariants and property-based test standards | Tech | `doctrine` | Engineering guideline for test quality |
| 22 | API wire error response format and error code registry | Tech | `doctrine` | Technical mandate for API error layer |
| 23 | Recipe: How to seed local test data and verify tables | Tech | `playbook` | Operational recipe to execute a task |
| 24 | Recipe: How to generate and register partner API tokens | Tech | `playbook` | Operational recipe to configure an integration |
| 25 | Recipe: How to execute a production deployment release | Tech | `playbook` | Operational recipe for deployment |
| 26 | General git commit conventions and developer setup commands | Outside | `AGENTS.md` / `CONTRIBUTING.md` | General, project-wide, rarely changing guidance |
| 27 | Standalone term definition without entity relationships | Outside | Glossary | Glossary reference documentation |
| 28 | Outage postmortem and incident timeline | Outside | Incident records | Historical incident record |
| 29 | Long-term multi-quarter feature roadmap | Outside | Roadmap | Product roadmap planning |
| 30 | Code linter rules and naming conventions for local variables | Outside | Linter / coding guide | Identifier naming inside code |
