# Hypothesis Template (Copy into every `.planner/hypothesis/NN-*.md`)

```markdown
# Hypothesis N — Short Title

## User Requirement Statement
[Direct quote or precise paraphrase of the relevant part of the user request.
Keep it as close as possible to the original wording.]

## Interpolation
[This is the “I think your query could mean that …” part.

Enriched professional interpretation. Expand the requirement using:
- Understanding of the stated (and already clarified) goal
- Local project context (existing architecture, conventions, dependency versions)
- Research findings (current recommended patterns, API stability, community practice)
- Professional engineering judgment (scalability, robustness, security, observability, maintainability)
- Reading between the lines (see professional-thinking.md)

Stay at the level of principles and architecture. Do not lock into a single language, framework, or library.
Make the implicit explicit. A good interpolation turns a request into a precise, testable expectation.]

## Supporting Evidence
- **Local**
  - [path/to/file or config] — relevant excerpt or observation
- **Research**
  - [source or key fact] — why it matters
- **Assumptions**
  - [explicit list of assumptions the hypothesis rests on]

## Open Questions
- [Any remaining ambiguity that the user should resolve]
- [Alternative interpretations that were considered and why they were set aside]
```

## Quality Checklist for Each Hypothesis

- [ ] Traceable to the original request or a clear engineering necessity
- [ ] Interpolation is richer than the raw statement but does not invent unrelated features
- [ ] Stays language-agnostic / technology-neutral (polyglot principle)
- [ ] Evidence section is non-empty (local, research, or both)
- [ ] Assumptions are listed explicitly
- [ ] Open questions are honest; do not hide uncertainty
---
