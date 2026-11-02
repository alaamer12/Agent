# System Components — Template & Field Reference

Copy-paste skeleton for a new System Components document, plus notes on
each field. See `components-worked-example.md` for a fully worked, real-world
instance of every field below.

---

## Document skeleton

```markdown
# System Components — {ApplicationOrProjectName}

> **Version scope:** {e.g. "Base (applies to all versions) + V1 implementation specifics."}
> **Read alongside:** [`{companion-doc}.md`](./path) for {what it covers} · [`UNITS.md`](./UNITS.md) for UI builder blocks

---

## System Overview

{One tight paragraph: what the system/application IS in one sentence — deployment shape,
whether there's a backend/account system/external dependencies.}

```
{ASCII box diagram — subsystem-level boxes and arrows only, not every leaf component}
```

---

## Component Hierarchy

```
{ApplicationOrProjectName}
│
├── {Subsystem A}
│   ├── {Component}
│   ├── {Component}
│   │   ├── {Subcomponent}
│   │   └── {Subcomponent}
│   └── {Component}
│
├── {Subsystem B}
│   └── ...
│
└── {Cross-cutting infra, e.g. Error System}
    └── ...
```

---

## 1. {Component Name}

### Type
{Subsystem | Service | Engine | Infrastructure | Integration | Processor | Data System | UI System | Architectural Pattern}

### Purpose
{2-4 sentences: what it does, and why it's its own component rather than
folded into a neighbor.}

### Responsibilities
- {Imperative-voice bullet}
- {Imperative-voice bullet}

### Features
{Optional — notable implementation characteristics: algorithms,
concurrency model, specific libraries/primitives used.}

### Inputs
- {What comes in, with type/shape if known, and from where}

### Outputs
- {What goes out, with type/shape if known, and to where}

### In Scope
- {Responsibility this component clearly owns}

### Out of Scope
- {Responsibility it does NOT own — say which component owns it instead}

### Error Handling
{Optional — what fails, how failures are classified (e.g. transient vs.
permanent), what happens on each path.}

### Constraints
{Optional — hard rules that must never be violated.}

### Configuration
{Optional — named config values with defaults, e.g. `poll_interval_seconds` (default: 30)}

### Subcomponents
{Optional — only if this component has its own internal named parts.}

### Related Components
- [{Other Component}](#anchor) — {short verb phrase describing the relationship}

### Internal Entities
{Optional — real class/interface/type names, for code-adjacent docs.}

### Implementation
{Optional — file/folder path where this lives.}

---

## {N}. {Next Component}
...

---

## Component Relationship Map

```
{ASCII flow diagram tracing the primary end-to-end path(s) at component
granularity, with verb-labeled arrows, e.g.:}

{Component A}
  │  acquires token from →  {Component B}
  │  fetches via →          {Component C}
  └─ passes results to →    {Component D}
                                 │
                                 ↓
                            {Component E}

{Cross-cutting relationships, e.g.:}
{Error System} ────── used by ── all modules
```

---

## Component Identification Summary

| Component | Type | Removing It Would… |
|---|---|---|
| {Component} | {Type} | {Specific, concrete consequence — not "it would break"} |
| {Component} | {Type} | {...} |
```

---

## Anchor convention

Markdown headings auto-generate anchors as lowercased, hyphenated text.
Follow this pattern consistently: a numbered heading like `## 3. Diff Engine`
produces anchor `#3-diff-engine`. Use these exact anchors in
`Related Components` and `Out of Scope` cross-links so they resolve.

## Type taxonomy (extend as needed, but stay consistent within one doc)

| Type | Use for |
|---|---|
| Subsystem | A grouping of several components that together implement one major capability (e.g. "Pipeline Subsystem") |
| Service | A component with a clear operational trigger/entry point (timer, request) that orchestrates work |
| Engine | A component whose job is computation/decision logic (diffing, scoring, matching) |
| Infrastructure | Cross-cutting or foundational plumbing (rate limiter, queue, tracker, error system) |
| Integration | The single point of contact with an external system (HTTP client, third-party API wrapper) |
| Processor | Transforms one data shape into another (parser, formatter, transcoder) |
| Data System | Persistence and retrieval (database, repository layer, search index) |
| UI System | The presentation layer and its own internal design system / MVVM / component structure |
| Architectural Pattern | A cross-cutting pattern applied throughout (e.g. MVVM, Hexagonal) rather than a single deployable unit |

## Quick self-check before delivering the doc

- [ ] Component Hierarchy tree lists exactly the same set of components as
      the numbered sections (no orphans either direction)
- [ ] Every `Related Components` and `Out of Scope` link resolves to a real
      anchor in the doc
- [ ] Every top-level component appears exactly once in the closing
      Component Identification Summary table
- [ ] "Out of Scope" entries name the component that *does* own that
      responsibility, not just what's excluded
- [ ] No UI widgets (buttons, cards, inputs) were catalogued as top-level
      components — those belong inside a "UI System" / "Design System"
      component's Subcomponents, or in `UNITS.md`
