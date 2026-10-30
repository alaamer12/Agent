# Deep Research Methodology

## Progressive Disclosure Intent

This reference expands the six mandatory passes defined in SKILL.md. Load it when the agent needs the detailed checklist for each pass or when the problem domain is especially large.

---

## PASS 1 — Conceptual Model Checklist

For every lifecycle or concern that appears in the problem:

- Name it precisely.
- Identify its natural owner (component, manager, platform, user gesture, external system, etc.).
- List the events or signals that advance or reverse it.
- Decide which other lifecycles or concerns it is allowed to control and which it must never control.
- Explicitly answer: “Should this concern be directly coupled to component mount/unmount (or equivalent)?”

Typical concerns to separate (adapt and extend for the domain):

- Container / collection / feed item
- UI component / view
- View hierarchy / DOM / native view tree
- Visibility / focus / viewport
- Resource instance (connection, handle, player, worker, buffer, …)
- Resource state / readiness
- Intent / desired state
- Actual runtime state
- Network / IO / external dependency
- Application / page / session
- OS / process / activity / background
- Framework navigation / keep-alive / caching
- User gesture / interaction
- Hardware / accelerator limits

Control hierarchy rule of thumb: higher-level intent drives lower-level resources; lower-level resources never unilaterally decide higher-level intent.

---

## PASS 2 — Primary Documentation Checklist

Sources to consult first (order matters):

1. Relevant language / runtime / standard APIs
2. Framework or library lifecycle and resource-management documentation
3. Platform / OS constraints and backgrounding rules
4. Hardware or accelerator limits when applicable
5. Formal standards (WHATWG, W3C, RFCs, etc.)

Record for each claim:

- Exact source + version or date
- Whether the behavior is guaranteed, implementation-defined, or only experimentally observed

---

## PASS 3 — Real-World Pattern Extraction

Rules:

- Never claim knowledge of closed-source internals.
- Tag every statement:
  - **Documented fact**
  - **Public engineering discussion**
  - **Common industry pattern**
  - **Architectural recommendation (this study)**
- Prefer conference talks, engineering blogs from teams that ship similar systems, and high-quality open-source implementations that solve comparable constraints.

---

## PASS 4 — Platform & Performance Constraints

Attribute every observed constraint or failure to the correct layer:

| Layer                  | Typical concerns                                      |
|------------------------|-------------------------------------------------------|
| Application framework  | component lifecycle, reactivity, keep-alive, routing  |
| Runtime / bridge       | resource limits, interop, configuration               |
| OS / process           | background restrictions, memory pressure, thermal     |
| Hardware / accelerator | concurrency limits, memory bandwidth, power           |
| External service       | rate limits, latency, availability, consistency       |
| Resource itself        | internal state machine, recovery, cleanup semantics   |

Collect concrete, measurable starting limits (not universal constants):

- Maximum simultaneous live instances of the expensive resource
- Size of the preparation / prefetch window
- Cleanup / release threshold when items leave the window
- Memory or concurrency growth under rapid change or long sessions

---

## PASS 5 — Challenge Phase

Deliberately search for:

- Counter-examples where the emerging architecture failed in production
- Cases where a simpler architecture performed better
- Platform or runtime changes that invalidated previous assumptions
- Performance or correctness cliffs that appear only under load, rapid change, or long sessions

Document each contradiction and the resolution chosen for this study.

---

## PASS 6 — Synthesis Rules

- Select exactly one primary architecture.
- Define the ownership chain in a single hierarchy.
- Separate **intent state** (what the system wants) from **actual runtime state** (what is currently true).
- Specify the single source of truth for “which item is active / focused”.
- Define prepare / activate / release / dispose transitions with explicit cancellation semantics.
- State how framework and OS lifecycle events map onto the manager or controller.
- Provide practical starting numbers for the target environment together with the measurement method that will refine them.

---

## Race-Condition & Stale-Work Defense Patterns

Always address:

- Stale asynchronous completion (generation / sequence / token / epoch)
- Cooperative cancellation (AbortController, context cancellation, CancellationToken, etc.)
- Ownership transfer (who is allowed to mutate or drive the resource)
- Listener / observer detachment on release
- Ignoring results after disposal
- Concurrent activation or mutation attempts

Minimal generation-token pattern (language-agnostic):

```
currentGeneration ← currentGeneration + 1
myGeneration ← currentGeneration
… perform asynchronous work …
if myGeneration ≠ currentGeneration → discard result (stale)
```

or an explicit cancellation token / signal per activation.

---

## State Machine Design Notes

- Prefer a small, explicit set of states over a large informal vocabulary.
- Distinguish terminal states (DISPOSED, FATAL_ERROR) from recoverable ones.
- Intent states are owned by the manager / controller; actual states are observed from the resource or runtime.
- Transitions must be cancelable when a newer intent arrives.

---

## Output Discipline

- One recommended architecture, not a menu of equal options.
- Formal state machines (tables or diagrams).
- Failure-mode table with Detection / Cause / Recovery / Cleanup / User-visible or system-visible behavior.
- Anti-pattern list with concrete failure modes.
- Decision matrix with a clear winner.
- Leveled practice exercise that withholds the full solution.
- Final one-paragraph answer to the core ownership question of the study.
