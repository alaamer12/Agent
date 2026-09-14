---
name: tailwind-css-master-skill
description: >
  Use when answering any Tailwind CSS queries, deciding which sub-skill directory to consult,
  building design systems, migrating from v3 to v4, configuring Tailwind v4 CSS-first themes,
  fixing dynamic string interpolation bugs (bg-${color}), or refactoring AI-slop utility soup.
  Serves as the master routing skill across all curated Tailwind CSS sub-skills (v4 configuration,
  v3-v4 migration, design systems, dynamic class safety, utility soup refactoring, tailwind-merge,
  and validator linting rules).
license: MIT
compatibility: "Designed for Claude Code / AI Agents. Requires Tailwind CSS v3.4 or v4.0+."
metadata:
  version: "1.0"
---

# Tailwind CSS Master Routing Skill

> **Target Version**: Tailwind CSS v4 (with v3 migration & backwards compatibility)  
> **Purpose**: Serves as the central entry point and routing decision tree for AI agents and developers. Directs queries to the correct domain skill directory based on intent (design, v4 syntax, v3->v4 migration, error resolution, anti-pattern checks).

---

## 🧭 Quick Routing Matrix

| Intent / Developer Request | Target Directory | Primary File |
| :--- | :--- | :--- |
| **Upgrade / Migrate project from v3 to v4** | [tailwind-impl-migration-v3-v4](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-migration-v3-v4) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-migration-v3-v4/SKILL.md) |
| **v4 Syntax comparison vs v3 (`@theme`, `@utility`, `@reference`)** | [tailwind-core-v3-vs-v4](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-core/tailwind-core-v3-vs-v4) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-core/tailwind-core-v3-vs-v4/SKILL.md) |
| **Configure Tailwind v4 CSS-first theme & custom tokens** | [tailwind-impl-config-v4](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-config-v4) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-config-v4/SKILL.md) |
| **Avoid AI-Slop UI & build cohesive token design systems** | [tailwind-core-design-system](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-core/tailwind-core-design-system) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-core/tailwind-core-design-system/SKILL.md) |
| **Fix broken dynamic classes (`bg-${color}-500`)** | [tailwind-errors-dynamic-classes](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-errors/tailwind-errors-dynamic-classes) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-errors/tailwind-errors-dynamic-classes/SKILL.md) |
| **Refactor unmaintainable utility stacks ("utility soup")** | [tailwind-errors-utility-soup](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-errors/tailwind-errors-utility-soup) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-errors/tailwind-errors-utility-soup/SKILL.md) |
| **Component prop overrides & `clsx` + `tailwind-merge`** | [tailwind-impl-tailwind-merge](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-tailwind-merge) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-tailwind-merge/SKILL.md) |
| **Scoped `@apply` & `@reference` in Vue/SFCs** | [tailwind-impl-apply-directive](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-apply-directive) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-impl/tailwind-impl-apply-directive/SKILL.md) |
| **Code Review, Anti-Pattern Validation & Linting Rules** | [tailwind-agents-validator](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-agents/tailwind-agents-validator) | [SKILL.md](file:///c:/Users/amrmu/Downloads/TailwindCSS-Claude-Skill-Package-main/tailwind-agents/tailwind-agents-validator/SKILL.md) |

---

## 🌳 Interactive Decision Tree

```
Developer Task / Question
│
├── 1. MIGRATE / UPGRADE
│   └── Moving v3 -> v4? 
│       └── Load: `tailwind-impl/tailwind-impl-migration-v3-v4`
│       └── Load: `tailwind-core/tailwind-core-v3-vs-v4`
│
├── 2. SYNTAX & CONFIGURATION (v4)
│   ├── Setting up `@theme`, `@import "tailwindcss";`, or `@utility`?
│   │   └── Load: `tailwind-impl/tailwind-impl-config-v4`
│   └── Configuring Next.js / Vite build plugins?
│       └── Load: `tailwind-impl/tailwind-impl-build-nextjs` or `tailwind-impl-build-vite`
│
├── 3. DESIGN SYSTEM & AI-SLOP PREVENTION
│   ├── Designing tokens, HSL/OKLCH color scales, typographic hierarchy?
│   │   └── Load: `tailwind-core/tailwind-core-design-system`
│   └── Cleaning up 30+ unmaintainable inline utility classes?
│       └── Load: `tailwind-errors/tailwind-errors-utility-soup`
│
├── 4. BUG FIXES & COMPONENT PATTERNS
│   ├── Dynamic class interpolation (`bg-${color}`) missing in build?
│   │   └── Load: `tailwind-errors/tailwind-errors-dynamic-classes`
│   ├── Merging component props & resolving class conflicts?
│   │   └── Load: `tailwind-impl/tailwind-impl-tailwind-merge`
│   └── `@apply` directive failing in Vue/Svelte scoped styles?
│       └── Load: `tailwind-impl/tailwind-impl-apply-directive`
│
└── 5. LINTING & CODE REVIEW
    └── Reviewing codebase for anti-patterns (R-01, R-02 severity)?
        └── Load: `tailwind-agents/tailwind-agents-validator`
```

---

## 🔍 Agent Context Inspection Rules

When answering user queries using this repository:
1. **Always start at the subfolder's `SKILL.md`**: It contains concise rules, syntax guidelines, and directive instructions.
2. **Deep-dive into `references/` when needed**:
   - `methods.md`: Step-by-step algorithms & code transformation strategies.
   - `examples.md`: Practical before-and-after code snippets.
   - `anti-patterns.md`: Explicit examples of code to avoid.
