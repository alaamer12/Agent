# References

Local map for the deep catalogs used by the `refactor` skill. Load only the file that matches the smell or transformation you are applying — do not load all of them at once.

| File | Concern |
|------|---------|
| [smell-catalog.md](smell-catalog.md) | Code smells by family (Bloaters, OO Abusers, Change Preventers, Dispensables, Couplers) + smell→refactoring map |
| [composing-methods.md](composing-methods.md) | Mechanics for Extract/Inline Method & Variable, Replace Temp with Query, Split Temporary Variable, Method Object |
| [moving-features.md](moving-features.md) | Mechanics for Move Method/Field, Extract/Inline Class, Hide Delegate, Remove Middle Man |
| [organizing-data.md](organizing-data.md) | Mechanics for Magic Number, Data Value→Object, Encapsulate Field/Collection, Type Code variants |
| [simplifying-conditionals.md](simplifying-conditionals.md) | Mechanics for Decompose/Consolidate Conditional, Guard Clauses, Polymorphism, Special Case, Assertion |
| [refactoring-workflow.md](refactoring-workflow.md) | Green-to-green cycle, timing (preparatory / comprehension / litter-pickup), Rule of Three, Branch by Abstraction, Parallel Change, when not to refactor |

You must update this file whenever a reference is added, removed, or renamed.
