# Project Structure — [Component/App Name]

> **Scope:** [What this structure covers — one project, one app within a larger repo, a specific boundary.]
> **Read alongside:** [Links to related docs this structure assumes or maps onto — a components doc, a scope doc, tech convention docs.]
> **Deployment note:** [State the deploy target and any structural consequence it has — e.g. "builds from lockfile, no Dockerfiles in this repo" — only if evidence supports it; omit rather than guess.]

---

## The Governing Rule

[State the single-ground principle in one or two sentences, plus any project-specific corollaries CI/review should enforce — numbered, each one a concrete, checkable rule, not a vague aspiration.]

1. [Corollary — e.g. "No literals in services: a threshold appearing inline when a rules file owns it is a defect."]
2. [Corollary]
3. [Corollary]

---

## The Tree

```text
[The actual tree. Every non-obvious folder gets an inline comment explaining WHO OWNS what decision or WHAT ROLE it plays — not just what type of file lives there. A folder with no comment should be self-evident from its name alone; if it needs explaining, it needs a comment, not a longer name.]
```

---

## Authority Table

| Decision (kind) | Single ground | Consumers | Protecting test |
|---|---|---|---|
| [Decision] | [The one file/package that owns it] | [Everything that imports/depends on it] | [What test breaks if it drifts] |

**When a new constant or rule appears:** it lands on a row, or the change that introduces it is rejected regardless of how clean the code looks.

---

## Named Absences

[Only include this section if there are real ones — don't pad it. Each entry: what's undecided, where it will live once decided, what triggers revisiting it.]

- **[decision.ts]** — [what's not yet decided] — [revisit trigger, a condition not a date]

---

## Optional-Feature Status

[Only include if something in the tree is optional-but-present — a feature whose absence shouldn't break anything else. State explicitly: what happens if it's disabled, and what (if anything) depends on it as a fallback.]

## Related Components

- [Link] — [what it's the ground for, relative to this tree]
