# Architecture Study Template

Copy this structure and fill every section. Do not omit numbered sections; adapt titles only when the domain truly requires different names.

---

# 1. Executive Summary

- One-paragraph problem restatement
- One-paragraph recommended architecture
- Key numbers (max live instances, preparation window, etc.)
- Core ownership answer in one sentence

# 2. Problem Definition

- Precise statement of the functional and non-functional constraints
- Non-goals
- Success criteria (latency, resource cost, correctness under rapid change, long-session stability, etc.)

# 3. Lifecycle / Concern Concepts

List every lifecycle or concern that appears. For each:

- Owner
- Events or signals that advance it
- Which other concerns it is allowed to control
- Explicit coupling decision (especially versus component mount/unmount or equivalent)

# 4. Core Resource Lifecycle

- Formal state machine for the expensive or stateful resource
- Intent states versus actual runtime states
- Allowed transitions and cancellation points

# 5. Container / Collection Lifecycle

- Independent container state machine if needed
- How container state drives focus selection and resource intent

# 6. Active / Focus Selection

- Candidate mechanisms evaluated
- Chosen source of truth
- Handling of rapid change, incomplete transitions, layout shifts, programmatic navigation, concurrent signals

# 7. Ownership & Pool / Reuse Architecture

- Evaluation of ownership candidates (container, item, manager, store, dedicated controller, etc.)
- Chosen hierarchy (diagram)
- Pool or reuse size rationale
- Acquisition / release / dispose rules

# 8. Preparation / Window / Prefetch Strategy

- Exactly what is prepared, prefetched, mounted, or materialized
- Distinction between different levels of preparation (metadata, partial, full, decoded, etc.)
- Practical window size and any adaptive rules

# 9. Platform-Specific Considerations

- Attribution table (framework / runtime / OS / hardware / external service / resource itself)
- Concrete limits and background / foreground / interruption behavior
- Any platform signals that must be observed

# 10. Framework / Runtime Lifecycle Integration

- Mapping of framework or runtime events onto manager / controller methods
- Cases where component lifecycle alone is insufficient

# 11. Race Conditions & Cancellation

- Concrete scenarios (rapid focus change, stale acquisition, concurrent mutation, etc.)
- Chosen defense (generation / epoch token, cancellation token, ownership lock, etc.)
- Guarantees provided

# 12. State Machines

- Intent state machine
- Actual runtime state machine
- Container-level state machine (if used)
- Interaction diagram

# 13. Module / Component Architecture

- Visual or presentation components versus logic modules
- Responsibility boundaries
- What must never live inside a single item component

# 14. Manager / Controller API

- Public methods (activate, prepare, release, disposeAll, …)
- Inputs, outputs, events, cancellation, error handling
- Ownership of instances

# 15. Network / Cache / External Dependency Architecture

- How external dependencies interact with the resource lifecycle
- Caching, prefetch, and consistency implications
- Offline or degraded-mode extension points

# 16. Virtualization / Recycling / Windowing

- Whether collection items, resource instances, or both are windowed or recycled
- Interaction with the ownership and pool design
- Trade-offs

# 17. Performance Model & Practical Limits

- Resource cost ranking (memory, concurrency slots, CPU, network, hardware accelerators, etc.)
- Starting limits for the target environment
- Measurement method that will refine the numbers

# 18. Failure Modes Table

Use the template from `references/anti-patterns-and-failure-modes.md`. Add domain-specific rows as needed.

# 19. Anti-Patterns

List the relevant anti-patterns with concrete failure modes for this domain.

# 20. Recommended Architecture

- Single hierarchy diagram
- Explanation of every layer
- Why alternatives were rejected

# 21. Implementation Blueprint

- Language-agnostic design
- Representative polyglot snippets (2–4 languages spanning different paradigm families) for the critical paths only
- No complete application; focus on architecture clarity

# 22. Practice Exercise

Leveled progressive exercise (Level 1 … Level N). For each level:

- Objective
- Requirements
- Constraints
- Expected behavior
- What the learner must implement
- Tests to write
- Failure cases to exercise
- Success criteria

Do **not** reveal the full solution.

# 23. Testing Strategy

- Functional, lifecycle, race, performance, resource-usage, network / dependency, platform, long-session
- Concrete measurement methods (time-to-ready, focus-to-active latency, live instance count, memory growth, etc.)

# 24. Decision Matrix

Columns: Architecture | Memory / Resource Cost | Performance | Startup / Activation Latency | External Cost | Complexity | Scalability | Platform Suitability | Framework Suitability | Recommended?

Clear winner row.

# 25. Open Questions / Experimental Validation

Items that must be measured on the target environment before final numbers are locked.

# 26. Final Recommendation

One clear paragraph answering the core ownership question of the study:

> What owns the lifecycle of the resource, what determines when it becomes active or focused, how many instances should exist, when they are prepared / reused / released, and how framework + platform lifecycle events interact with that system?

---

## Citation Discipline

After every important technical claim place an inline citation. Prefer primary sources. When sources disagree, surface the disagreement inside the relevant section.
