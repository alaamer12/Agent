---
name: refactor
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

Score structural quality by how many of the eight [Quick Diagnostic](#quick-diagnostic) rows pass:

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

See [references/refactoring-workflow.md](references/refactoring-workflow.md) for the full cycle, timing (preparatory / comprehension / litter-pickup), Branch by Abstraction, Parallel Change, and when *not* to refactor.

## Six Focus Areas

### 1. Code Smells as Triggers

Smells are surface indicators of deeper design problems. Name the smell, then apply its prescribed refactorings.

Five families: Bloaters, Object-Orientation Abusers, Change Preventers, Dispensables, Couplers.

Most common / most expensive: **Long Method**, **Duplicate Code**.

| Smell signal | Typical fix |
|--------------|-------------|
| Method > ~10 lines or needs a comment | Extract Method |
| One change touches many classes | Move Method / Field (Shotgun Surgery) |
| One class has many reasons to change | Extract Class (Divergent Change) |
| Same params travel together | Introduce Parameter Object |
| Copy-pasted logic | Extract Method + Pull Up |

Full catalog with detection heuristics → [references/smell-catalog.md](references/smell-catalog.md)

### 2. Composing Methods

Most refactoring starts here. Break long methods into short, intention-revealing pieces that read like prose.

- **Extract Method** is the single most important refactoring — master it first
- Urge to write a comment? Extract the block and use the comment as the name
- Inline Method / Variable when the indirection adds nothing
- Replace Temp with Query; Split Temporary Variable; Replace Method with Method Object when locals are too tangled

Mechanics and before/after → [references/composing-methods.md](references/composing-methods.md)

### 3. Moving Features Between Objects

The core OO question: where should this responsibility live?

- Move Method / Field when a method uses more of another class’s data than its own (Feature Envy)
- Extract Class when one class does two jobs; Inline Class when one does almost nothing
- Hide Delegate (Law of Demeter) vs Remove Middle Man (pure forwarding)

Mechanics → [references/moving-features.md](references/moving-features.md)

### 4. Organizing Data

Replace primitives, magic numbers, and exposed fields with small domain objects that enforce invariants.

- Replace Magic Number with Symbolic Constant
- Replace Data Value with Object (`Email`, `Money`, `DateRange`)
- Encapsulate Field / Collection
- Replace Type Code with Subclasses or Strategy

Mechanics → [references/organizing-data.md](references/organizing-data.md)

### 5. Simplifying Conditional Logic

Deep nests and long switches are the hardest code to read and the most bug-prone.

- Decompose Conditional → named condition + named branches
- Replace Nested Conditional with Guard Clauses (edge cases first, main path flat)
- Consolidate Conditional Expression
- Replace Conditional with Polymorphism (gold standard for type-based branches)
- Introduce Special Case (Null Object) / Introduce Assertion

Mechanics → [references/simplifying-conditionals.md](references/simplifying-conditionals.md)

### 6. Safe Workflow & Scale

- Rule of Three for duplication
- Preparatory refactoring before the feature
- Characterization tests when legacy code has none
- Branch by Abstraction / Parallel Change for production-scale moves

Details → [references/refactoring-workflow.md](references/refactoring-workflow.md)

## Practical Patterns (Quick Reference)

### Extract Method (the workhorse)

```diff
- async function processOrder(orderId) {
-   // 50 lines fetch + validate + price + inventory + ship + notify
- }
+ async function processOrder(orderId) {
+   const order = await fetchOrder(orderId);
+   validateOrder(order);
+   const pricing = calculatePricing(order);
+   await updateInventory(order);
+   const shipment = await createShipment(order);
+   await sendNotifications(order, pricing, shipment);
+   return { order, pricing, shipment };
+ }
```

### Guard Clauses over Nested Conditionals

```diff
- function process(order) {
-   if (order) {
-     if (order.user) {
-       if (order.user.isActive) {
-         if (order.total > 0) return processOrder(order);
-         else return { error: 'Invalid total' };
-       } ...
- }
+ function process(order) {
+   if (!order) return { error: 'No order' };
+   if (!order.user) return { error: 'No user' };
+   if (!order.user.isActive) return { error: 'User inactive' };
+   if (order.total <= 0) return { error: 'Invalid total' };
+   return processOrder(order);
+ }
```

### Parameter Object / Domain Types

```diff
- function createUser(email, password, name, age, address, city, country, phone) { ... }
+ interface UserData {
+   email: string;
+   password: string;
+   name: string;
+   age?: number;
+   address?: Address;
+   phone?: string;
+ }
+ function createUser(data: UserData) { ... }
```

### Strategy over Type Switch

When a conditional branches on type or mode and will grow, replace it with Strategy or polymorphism rather than adding another `else if`.

## Common Mistakes

| Mistake | Why it fails | Fix |
|---------|--------------|-----|
| Refactoring without tests | No safety net | Characterization tests first |
| Big-bang rewrite | Structure + behavior mixed | Smallest steps, green after each |
| Two hats at once | Neither change verifiable | Refactor commit, then feature commit |
| Extracting tiny methods with poor names | Indirection without clarity | Name must remove need to read the body |
| Ignoring the smell catalog | Reinvents fixes | Name the smell → apply its recipe |
| Polishing doomed code | Waste | Check lifespan first |
| Optimizing while refactoring | Conflates clarity and speed | Clarity first, then profile |

## Quick Diagnostic

| Question | If No | Action |
|----------|-------|--------|
| Do tests pass before you start? | No safety net | Write or fix tests first |
| Can you name the smell? | Refactoring by instinct | Identify smell → prescribed refactoring |
| Is each method under ~10–20 lines and one thing? | Long Method | Extract Method |
| Does each class have one reason to change? | Divergent Change / Large Class | Extract Class |
| Are there duplicated blocks? | Most expensive smell | Extract shared logic |
| Do type-based conditionals use polymorphism? | Switch Statements remain | Replace Conditional with Polymorphism |
| Are you committing after every green step? | Risk of lost work / mixed changes | Commit after each safe transformation |
| Are names intention-revealing? | Comments or mental simulation required | Rename / Extract until the name is enough |

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
