---
name: details-up
description: Guided, conversational topic-by-topic system design, discovery, and architectural specification workflow. Use when discussing complex architectures, reviewing missing project requirements, aligning technical decisions before implementation, or when the user wants to tackle topics sequentially one by one (ask questions, collect user decisions, close/document the topic into markdown, and advance to the next topic).
---

# Details-Up Workflow

The **Details-Up** skill establishes a structured, conversational, topic-by-topic architecture discovery and specification process. It prevents chaotic decision-making by breaking complex projects down into discrete technical topics, thoroughly clarifying each topic through targeted interactive questions, recording the concluded decisions into dedicated specification documents, and seamlessly transitioning to the next topic.

---

## Core Philosophy & Principles

1. **Sequential Focus (One Topic at a Time):** Never jumble unrelated architectural questions across multiple system layers into one discussion. Fully close topic $N$ before opening topic $N+1$.
2. **Interactive Clarification & Proposal:** Present clear options with concrete pros, cons, and trade-offs rather than open-ended ambiguity. Let the user guide and decide.
3. **Living Documentation:** Once a topic is agreed upon, immediately crystallize the decisions into a formal technical markdown document (`Docs/...`) and update master index maps.
4. **Implementation Gatekeeping:** Stay in thinking/discussion mode until all design topics are formally resolved. Only proceed to code implementation when explicitly commanded by the user.

---

## The 4-Stage Lifecycle

```text
┌────────────────────────────────────────────────────────┐
│                   Details-Up Cycle                     │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Stage 1: Agenda & Topic Triage                       │
 │ • Identify missing design pillars or checklist items │
 │ • Select the next focused topic                      │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Stage 2: Deep Dive & Conversational Clarification    │
 │ • Present architectural trade-offs                   │
 │ • Ask targeted choice/free-form questions            │
 │ • Iterate until user reaches decision                │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Stage 3: Topic Closure & Formal Documentation        │
 │ • Author/update dedicated specification doc (Docs/)  │
 │ • Update master indices (Docs/README.md)             │
 │ • Commit/checkpoint clean changes                    │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Stage 4: Next Topic Hand-Off                         │
 │ • Summarize outcome briefly                          │
 │ • Propose next logical topic on agenda               │
 └──────────────────────────────────────────────────────┘
```

---

## Operational Guidelines

### 1. Topic Scoping & Question Formatting
* Group related questions into atomic proposals.
* State why each option matters (e.g., runtime performance, memory footprint, offline resilience, maintainability, DX).
* Respect the user's answers unconditionally—do not repeatedly re-ask decided points unless the user changes direction.

### 2. Document Authoring Standard
When closing a topic:
* **Target Location:** Place documents in the project's appropriate documentation directory or specification pillar (e.g., `docs/tech/`, `docs/design/`, `docs/architecture/`).
* **Content Depth:** Include concrete interfaces, state transition tables, data flow diagrams, and error handling strategies. Avoid superficial summaries.
* **Cross-References:** Link the new document in the project's master index or documentation table of contents (e.g., `README.md`, `docs/README.md`).

### 3. Transitioning to the Next Topic
After saving the documentation:
1. Provide a concise bullet-point summary of the closed topic.
2. Review remaining items from the agenda (or `todo` list).
3. Prompt the user for the next topic to start the cycle again.
