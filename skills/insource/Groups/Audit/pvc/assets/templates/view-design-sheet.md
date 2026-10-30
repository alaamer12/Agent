# View design sheet — `<screen or feature name>`

> Fill this before scaffolding. Every blank row is a question the architecture cannot answer for you, and a guessed answer becomes a hedge, a misplaced file, or a Component that cannot be classified. Copy this file into the feature folder or ticket. Reference: [`../../references/settled-behavior.md`](../../references/settled-behavior.md).

## 1. Scope

```
Screen / route:
Feature or domain it belongs to:
Who is the user of this section, and what are they trying to do?
One sentence on the section's purpose (if this needs "and", it is two Views):
```

## 2. Behavior — settle before you build

| Question | Decided answer | Source of the decision |
| --- | --- | --- |
| What is the primary interaction? | | |
| What fires it — keystroke, blur, button, timer? | | |
| What is the *one* accepted failure mode? | | |
| Is any alternative behavior still live? (if yes → **not settled**) | | |
| What is explicitly out of scope for this feature? | | |

> If two rows are unanswerable, stop and get the product decision. Do not build both shapes "to be safe".

## 3. Facts this section consumes

| Fact / value | Does this section create it, or only read it? | Kind + owner |
| --- | --- | --- |
| | | `/states` |
| | | `/states` |

`/pvc` needs one input from this table to place the roles: **read vs create**. Classifying each value as a State or a Condition, deciding who owns it and where its source file lives, is the `/states` skill's workflow — run it here, then bring the answer back to §6 below.

## 4. Branches the View can present

Say **branch** or **case**, never "state".

| Branch | Rendition name (what it displays) | Reached by |
| --- | --- | --- |
| default / success | (usually unnamed — the View's single case) | |
| loading | | |
| empty | | |
| error | | |
| disabled / offline / unauthorized | | |

## 5. Composition

```
Page:
└── View:
    ├── Decoration:
    ├── Component (primary function):
    │   ├── Aligner (leading):
    │   └── Aligner (trailing):
    └── Nested View (if any):
```

## 6. Placement — the poles

| Unit | Global / Global-Local / Local | Which test decided it (§3 consumers vs §3.1 tier intent) | Folder |
| --- | --- | --- | --- |
| | | | |
| | | | |

For each `_`-prefixed file: name the closed family that consumes it. If you cannot enumerate the family, it is not Global-Local.

## 7. Grouping check

| Grouping | Do the children coordinate? | Verdict |
| --- | --- | --- |
| | no → Wrapper Component / yes → Component | |

## 8. Primitive layer

| Primitive needed | Exists in `ui/adaptive`? | If not, add `ui/base` re-export + `ui/adaptive` skin |
| --- | --- | --- |
| | | |

Nothing imports `ui/base` or the framework control directly except `ui/adaptive`.

## 9. Names

Every unit gets its role suffix or purpose name per [`naming.md`](../../references/naming.md). No unit that renders may be named `…State` or `…Condition`.

## 10. Before writing code

- [ ] Every behavior row in §2 has one decided answer.
- [ ] No fact renders; no Rendition consults.
- [ ] Each shared file's pole is decided by a named test.
- [ ] The name of every unit tells a reader its role without opening it.
- [ ] `python scripts/check_pvc.py <src>` is clean, or every finding is explained.

---

## Filled example (illustrative, not a mandate)

```
Screen: /search   Feature: search   Purpose: find records by free text.
Behavior: fires on keystroke, 300ms debounce. Decided — the eager variant is NOT live.
Facts:    searchState       — this section creates it (its own request)   → classified + owned via /states
          networkCondition  — this section only reads it                  → same
Branches: success (unnamed default) · loading · error · disabled
Placement: _SearchInput Global-Local (a) → SearchInput/  (family: DebouncedSearchInput only)
           useSearchState Global-Local (b) → features/search/behaviour/
           useNetworkCondition Global → shared/conditions/
Grouping:  none — the three result actions each coordinate nothing and stay separate.
```
