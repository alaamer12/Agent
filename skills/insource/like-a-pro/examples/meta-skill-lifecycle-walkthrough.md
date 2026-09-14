# End-to-End Walkthrough: Idea to Production Standards with like-a-pro

This walkthrough demonstrates how an AI agent guides a software initiative from a raw idea to full technical specifications and binding conventions using the `like-a-pro` meta-skill lifecycle.

---

## The Scenario

A user starts with an idea: *"I want to build a freelancing project feed checker and notifier that monitors RSS/HTML feeds and alerts freelancers instantly."*

---

## Phase 1: Idea (including Phase 1.5 Product Definition)
- The user has an idea; the agent explores the vision, clarifies goals, user journeys, target platforms, and in-scope vs out-of-scope features.
- Produces initial product vision documents (`README.md`, `DESIGN.md`).

---

## Phase 2: Technical Specification (via details-up)
- Rather than dumping hundreds of technical questions at once, the agent activates `details-up` to systematically establish how the application works.
- Discovers missing technical pillars topic-by-topic:
  - *Topic 1:* Polling engine & rate limiting strategy.
  - *Topic 2:* Local store vs cloud sync architecture.
  - *Topic 3:* Notification delivery & system tray integration.
- Documents each concluded topic into `docs/` before moving to the next.

---

## Phase 3: Standards and System Definition (Like-a-Pro)

After the "how" has been determined, the agent moves into Phase 3 to establish formal, reusable implementation standards and definitions.

### Step 3.1: App Boundary Discovery & Confirmation
Before establishing engineering standards, the agent scans the workspace and confirms application boundaries with the user:
```text
Agent: "Based on my scan of the project, I have identified two distinct applications:
1. 'MostaqlK.App': A .NET desktop client with UI (XAML/MAUI).
2. 'MostaqlK.Worker': A headless background feed scraper.

Do these boundaries accurately reflect your architectural division?"

User: "Actually, both are combined into a single desktop application in V1."

Agent: "Understood. Re-scoped to 1 confirmed application: 'MostaqlK' (Desktop client with background pipeline and UI)."
```

### Step 3.2: Applying Like-a-Pro Child Skills
For the confirmed application, the agent runs the specialized skills:

1. **`language-conventional`:**
   - Detects C# 14 / .NET 10.
   - Enforces `<Nullable>enable</Nullable>`, `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`.
   - Generates `.repertoire/.steering/base/tech/csharp-conventions.md`.

2. **`sql-conventional`:**
   - Agrees on SQLite embedded dumb-store architecture.
   - Generates Stage 1 `.repertoire/.steering/base/tech/sql-conventions.md`.
   - Generates Stage 2 `docs/table-reference.md` mapping entities and functional dependencies.

3. **`errors-handling`:**
   - Discusses failure contract (adopts Three-tier Throw/Result/Neither).
   - Establishes machine-readable error codes (`{DOMAIN}-{NNN}`) and per-module `Errors.cs` factories.
   - Generates `.repertoire/.steering/base/tech/errors-handling.md`.

4. **`ui-rules` (Activated because app has UI):**
   - Agrees on responsiveness (no fixed heights on text containers), skeleton shimmer pairing, 3-tier icons, and RTL support.
   - Generates `.repertoire/.steering/base/tech/ui-rules.md`.

5. **`system-creator`:**
   - Mode A generates `SYSTEM-COMPONENTS.md` inventorying engines, queues, and stores.
   - Mode B catalogs reusable builder blocks in `UNITS.md`.
