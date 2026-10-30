---
name: search-deeply
description: Perform multi-pass deep technical research and produce implementation-oriented architecture studies for complex systems problems. Use when the user requests very deep research, production-grade architecture analysis, lifecycle design, formal state machines, ownership models, race-condition handling, resource pools, platform constraints, failure-mode analysis, anti-patterns, or any study that must go far beyond shallow answers. Triggers include deep research, architecture study, implementation-oriented, formal state machine, ownership analysis, failure modes, anti-patterns, decision matrix.
---

# Search Deeply

## Overview

Conduct rigorous, multi-pass technical research that yields a single recommended, implementable architecture rather than a catalog of options. Separate documented facts from patterns and recommendations. Prefer primary sources. Always produce formal state machines, clear ownership models, race-condition defenses, failure-mode tables, anti-pattern analysis, a decision matrix, and a progressive practice exercise.

## When to Apply

Activate for any request that demands a production-grade architecture study — resource lifecycle, concurrent ownership, pooling/reuse, platform constraints, hybrid or multi-runtime systems, or any domain where shallow answers fail under real load, rapid change, or long sessions.

## Core Workflow (Mandatory Multi-Pass)

1. **PASS 1 — Conceptual model**  
   Extract and carefully separate every relevant lifecycle or concern (component, view hierarchy, visibility/focus, resource instance, resource state, network/IO, application, platform/OS, user interaction, etc.). Determine the control hierarchy. Explicitly decide which lifecycles may control which others and which couplings are unsafe.

2. **PASS 2 — Primary documentation**  
   Consult official sources first (standards, runtime docs, framework lifecycle docs, platform constraints). Record what is guaranteed, implementation-defined, or only observed.

3. **PASS 3 — Real-world patterns**  
   Gather publicly discussed production architectures. Label every statement: documented fact | public engineering discussion | common industry pattern | architectural recommendation (this study). Never present speculation as fact. Do not invent internals of closed systems.

4. **PASS 4 — Platform & performance constraints**  
   Investigate real limits (memory, concurrency, thermal, backgrounding, network transitions, hardware resources). Attribute each constraint to the correct layer (application framework, runtime, OS, hardware, external service).

5. **PASS 5 — Challenge conclusions**  
   Actively seek evidence that contradicts the emerging recommendation. Document disagreements and resolve them with explicit reasoning.

6. **PASS 6 — Synthesis**  
   Produce ONE primary architecture. Define ownership hierarchy, state machines (intent versus actual), source of truth for “active” or “focused” items, pool/reuse rules, prepare/activate/release/dispose semantics, and exact mapping of framework + platform lifecycle events onto the architecture.

## Required Output Sections

Structure the final report with these numbered sections (adapt titles only when the domain truly demands different names):

1. Executive Summary  
2. Problem Definition  
3. Lifecycle / Concern Concepts  
4. Core Resource Lifecycle  
5. Container / Collection Lifecycle  
6. Active / Focus Selection  
7. Ownership & Pool / Reuse Architecture  
8. Preparation / Window / Prefetch Strategy  
9. Platform-Specific Considerations  
10. Framework / Runtime Lifecycle Integration  
11. Race Conditions & Cancellation  
12. State Machines (Intent + Actual)  
13. Module / Component Architecture  
14. Manager / Controller API  
15. Network / Cache / External Dependency Architecture  
16. Virtualization / Recycling / Windowing  
17. Performance Model & Practical Limits  
18. Failure Modes Table  
19. Anti-Patterns  
20. Recommended Architecture (single hierarchy)  
21. Implementation Blueprint (language-agnostic + representative polyglot snippets)  
22. Practice Exercise (leveled, progressive, solution withheld)  
23. Testing Strategy  
24. Decision Matrix  
25. Open Questions / Experimental Validation  
26. Final Recommendation  

End with a single clear paragraph that answers the core ownership question for the problem at hand.

## Research Quality Rules

- Prefer primary sources and cite them.  
- Distinguish fact / discussion / pattern / recommendation.  
- Never invent internals of closed or proprietary systems.  
- When sources disagree, surface the disagreement and justify the chosen conclusion.  
- Separate intent (what the system wants) from actual runtime state (what is currently true).  
- Design formal state machines; do not rely on prose alone.  
- Treat rapid change, concurrent operations, and stale asynchronous work as first-class concerns.  
- Provide concrete, measurable starting limits for the target environment rather than universal magic numbers.  
- Keep the skill and all examples language- and framework-agnostic; supply polyglot comparative snippets only where they illuminate a principle.

## Supporting Resources

- Detailed methodology and pass checklists → `references/deep-research-methodology.md`  
- Full report template with section prompts → `assets/templates/architecture-study-template.md`  
- Universal ownership, state-machine, and race-defense patterns → `examples/universal-lifecycle-patterns.md`  
- Generalized anti-pattern catalog and failure-mode template → `references/anti-patterns-and-failure-modes.md`

## Polyglot & Universal Constraints

Follow the polyglot skill strictly:
- Anchor everything in architectural principles, not specific syntax or vendors.
- Never mandate a single language, framework, runtime, or platform.
- Present trade-off spectra and let the user decide.
- When code is shown, provide 2–4 representative languages spanning different paradigm families.
- Frame every constraint as a trade-off the user can accept or reject.
