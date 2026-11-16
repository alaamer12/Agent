---
name: refactor
version: 1.1.1
author: Amr
specialized: none
description: Surgical code refactoring that improves structure and maintainability without changing behavior. Use when the user says refactor this, clean up this code, fix code smells, extract method, replace conditional, move method, introduce parameter object, eliminate duplication, break down god class/function, improve type safety, or prepare code for a new feature by restructuring. Also trigger for technical debt, smell-driven cleanup, safe transformation sequences, and characterization tests before change. Covers smell catalog, composing methods, moving features, organizing data, simplifying conditionals, and the green-to-green workflow. Not for big-bang rewrites or feature work mixed with structure changes.
license: MIT
metadata:
  version: "2.0.0"
  combines: refactoring-patterns + practical refactor examples
---

# Refactor

> Surgical, behavior-preserving structural improvement of existing code. Entry point for the skill; deep mechanics live in [`references/`](references/README.md).
> Load a reference only when the smell or transformation you are applying matches that file.

## Core Principle

**Refactoring is not rewriting.** It is a sequence of tiny structural moves, each verified green-to-green. You never change *what* the code does — only *how* it is organized. Big-bang rewrites mix structure with behavior and become undebuggable.

Bad structure is the normal cost of shipping under pressure, not a character flaw. Code smells are objective signals; the catalog tells you *where*, the named refactorings tell you *what to do*.

## When to Use / When Not

**Use when:**
- Code is hard to read, extend, or test
- A clear smell is present (Long Method, Feature Envy, Primitive Obsession, etc.)
- You are about to add a feature and the insertion point is messy (preparatory refactoring)
- The same logic appears a third time (Rule of Three)

**Do not use when:**
- No tests exist and writing them is not feasible
- The code is about to be deleted or replaced
- You are under a hard deadline that forbids extra risk
- You are tempted to mix feature work and structure work in the same commit

## Scoring (Goal 10/10)

Score structural quality by how many of the eight [Quick Diagnostic](references/smell-catalog.md#quick-diagnostic) rows pass:

`score = round(passed / 8 × 10)`, adjust down for a single severe smell.

- **9–10**: smells gone, functions do one thing, names reveal intent, duplication eliminated, conditionals use polymorphism where apt, tests cover the paths
- **5–6**: a few smells remain but structure is mostly sound
- **≤3**: pervasive smells or no safety net

Always state the current score, name the smells driving it down, and list the specific refactorings that raise it.

## The Safe Loop

1. **Green** — tests pass (write characterization tests first if missing)
2. **One small transformation** — apply a single named refactoring
3. **Green** — tests still pass
4. **Commit** — capture the safe state
5. Repeat

If tests go red, revert. Do not debug a broken refactoring.

See [references/refactoring-workflow.md](references/refactoring-workflow.md) for the full cycle, timing (preparatory / comprehension / litter-pickup), Branch by Abstraction, Parallel Change, and when *not* to refactor, plus the [Common Mistakes](references/refactoring-workflow.md#common-mistakes) table.

## Six Focus Areas

### 1. Code Smells as Triggers

Smells are surface indicators of deeper design problems. Name the smell, then apply its prescribed refactorings.

Full catalog with detection heuristics, plus the smell signal → typical fix table and the eight-row Quick Diagnostic → [references/smell-catalog.md](references/smell-catalog.md)

### 2. Composing Methods

Most refactoring starts here. Break long methods into short, intention-revealing pieces that read like prose.

Mechanics and before/after → [references/composing-methods.md](references/composing-methods.md)

### 3. Moving Features Between Objects

The core OO question: where should this responsibility live?

Mechanics → [references/moving-features.md](references/moving-features.md)

### 4. Organizing Data

Replace primitives, magic numbers, and exposed fields with small domain objects that enforce invariants.

Mechanics → [references/organizing-data.md](references/organizing-data.md)

### 5. Simplifying Conditional Logic

Deep nests and long switches are the hardest code to read and the most bug-prone.

Mechanics → [references/simplifying-conditionals.md](references/simplifying-conditionals.md)

### 6. Safe Workflow & Scale

Details → [references/refactoring-workflow.md](references/refactoring-workflow.md)

## Practical Patterns (Quick Reference)

Four worked before/after sketches — Extract Method (the workhorse), guard clauses over nested conditionals, parameter object / domain types, strategy over type switch → [references/practical-patterns.md](references/practical-patterns.md)

## Checklist Before Finishing

- [ ] Behavior unchanged (tests green, manual smoke if needed)
- [ ] Each public function/class has a single clear responsibility
- [ ] No remaining obvious smells from the diagnostic
- [ ] Names reveal intent; comments explain *why*, not *what*
- [ ] Dead code, unused imports, and commented-out blocks removed
- [ ] Magic numbers/strings replaced or justified
- [ ] Commits are small and each leaves the suite green

## How to Work

1. Read the target code and run existing tests.
2. Name the smells (use the catalog).
3. Score the current state.
4. Apply the highest-leverage named refactoring first (usually Extract Method or Guard Clauses).
5. Green → commit → next.
6. Re-score; stop when the score and the user’s goal are met.
7. Do not mix feature work into the same commits.

For deep mechanics, load only the reference that matches the smell you are fixing. Do not load all references at once.
