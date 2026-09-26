# PVC Rules, Violations, and Classification Checklist — Full Reference

> Canonical home for hard rules, violations, classification checklist, and anti-patterns. Conceptual role definitions live in `architecture-core.md`.

---

## 1. Classification Decision Checklist

When classifying any UI unit, walk this checklist in order:

1. Is this an application route or full screen?  
   → **Page**

2. Is this a meaningful, user-recognizable section of a screen (or of another section) with its own purpose?  
   → **View** (even if nested)

3. Is this a purposeful functional/interactive unit the user engages with inside the View?  
   → **Component**

4. Does this provide supporting context, explanation, emphasis, or information around the primary functionality?  
   → **Decoration**

5. Does this Decoration have a clear positional relationship to a Component (leading/trailing/top/bottom)?  
   → **Aligner** (specialized Decoration)

6. Is this a lowest-level, generic, reusable interface primitive with no application-specific knowledge?  
   → **UI Element**

If still ambiguous, ask the five diagnostic questions and prefer the higher-level role that matches user-facing purpose.

---

## 2. Hard Rules

1. **Role over implementation** — Never classify solely because something is a framework component.
2. **Purpose over size** — Classification comes from purpose and abstraction level, not physical size.
3. **Composition over rigid hierarchy** — Views may contain Views; Components may contain other Components when natural. A View may contain zero, one, or many Components. No artificial depth limits.
4. **Context matters** — Role is contextual to the current composition.
5. **Pages remain compositional** — A Page communicates “what makes up this screen”, not every internal detail.
6. **Views must have clear purpose** — Create a View only when the section is conceptually recognizable to users as a section, interaction, state, or focused piece of UI. Do not create Views merely because elements occupy a rectangle.
7. **Downward dependency direction** — Page → View → Component → UI Element. Primitives must never depend on feature-specific Views or Components.
8. **UI Elements stay generic** — A Button/Input/etc. must not know about “Delete Account”, “Search”, “Checkout”, etc.
9. **State and business logic live outside pure UI hierarchy** — Prefer hooks/composables/stores/services; the Component consumes them. The PVC model defines the UI composition layer only.
10. **Feature ownership and UI role are orthogonal** — Features own domain-specific UI; the PVC roles describe how that UI is constructed.
11. **Code must reflect the architecture** — Reading the component tree and file names should reveal the PVC composition. The code itself is the representation of the model.
12. **API follows purpose, not DOM** — Component and View public APIs expose user-facing purpose (value, onSearch, onClear). They must not leak internal class names, icon positions, padding, or layout details.
13. **Framework neutrality** — Express PVC roles the same way regardless of React, Vue, Svelte, Solid, Angular, or other component models. Adapt only the implementation syntax, never the architectural meaning.


## 3. Explicit Violations (Detect and Refactor)

### Structural / Naming
- Flat `components/` folder containing Pages, Views, Decorations, and UI Elements mixed together.
- Names such as `SearchPageComponent`, `SearchViewComponent`, `SearchTitleComponent`.
- Creating a View solely because a group of elements occupies a rectangle (`MainView`, `SectionView`, `ContainerView`, `ContentView` without real purpose).
- Forcing every Decoration or Aligner into its own folder when co-location would be clearer.
- Extracting every small markup fragment into a separate Component without reuse or purpose justification (anti-pattern names: SearchTitle, SearchSectionContainer, SearchWrapper, SearchContent, SearchLayout).
- Assuming every View must have exactly one “primary” Component.

### Dependency
- UI Element importing a feature View or Component.
- Component depending on a Page.
- Circular or upward imports that reverse the abstraction direction.

### Responsibility
- Page containing deep primitive markup or complex layout logic instead of View composition.
- UI Element that knows about “Delete Account”, “Search query”, “Checkout total”, etc.
- Component or View whose public API exposes internal DOM structure, class names, or layout props instead of purposeful props.

### Conceptual
- Treating every framework component as an architectural Component.
- Using “Component” as the only vocabulary for every rendered unit.
- Confusing implementation technology with architectural role.
- Treating “primary Component” as a hard requirement instead of common-case language.

---

## 4. Recommended Refactor Patterns

| Violation | Recommended Action |
|-----------|--------------------|
| Flat components/ dump | Split by role under features/ and ui/elements/ |
| Page with primitives | Extract meaningful Views; keep Page as pure composition |
| Generic Button named DeleteAccountButton | Move feature knowledge into a Component that uses the generic Button |
| Deep nested markup with no roles | Introduce View → Component → Decoration boundaries |
| Everything co-located in one file | Extract only purposeful Components and reusable pieces |
| Over-extraction | Collapse small single-use Decorations back next to their View |
| DOM-leaking Component API | Redesign API around user purpose (value, onSearch, onClear) |
| View without clear purpose | Merge back into parent or rename to a recognizable section |

---

## 5. API Design Guidance

- **Component API** should reflect user purpose (`value`, `onSearch`, `onClear`), not internal DOM details.
- **View API** should expose the meaningful section contract; internal composition stays private.
- **UI Element API** should stay generic (`disabled`, `size`, `variant`, `onClick`, `children`).

---

## 6. Quick Anti-Pattern Catalog

```
# Bad — semantic information erased
components/
├── SearchPageComponent
├── SearchViewComponent
├── SearchInputComponent
├── SearchTitleComponent
├── SearchDescriptionComponent
├── SearchKeywordsComponent
├── SearchChipComponent
└── ...

# Good — roles visible
features/search/
├── views/SearchView/
├── components/SearchInput/
└── decorations/
    ├── SearchDescription/
    └── CommonKeywords/
ui/elements/
├── Button/
├── Input/
└── Chip/
```

```
# Bad — Page doing everything
function SearchPage() {
  return (
    <div>
      <h1>Search</h1>
      <input ... />
      <button>Clear</button>
      {/* results, chips, etc. */}
    </div>
  );
}

# Good — Page composes Views
function SearchPage() {
  return (
    <>
      <SearchView />
      <SearchResultsView />
    </>
  );
}
```

```
# Bad — over-extraction inside a View
SearchTitle
SearchDescription
SearchSectionContainer
SearchWrapper
SearchContent
SearchLayout

# Good — keep simple supporting pieces close or inline
<section>
  <h1>Search</h1>
  <p>Search for users, posts, or topics.</p>
  <SearchInput />
  <CommonKeywords />
</section>
```

---

## 7. Folder Creation Decision Heuristic

Not every architectural role needs its own folder. The filesystem optimizes for:

- discoverability
- ownership
- locality
- maintainability
- project size

It must **not** become a bureaucratic copy of the conceptual diagram.

Prefer project-level role folders (`views/`, `components/`, `decorations/`) over per-View nested role trees.

---

## 8. Final Diagnostic Sentence

When in doubt, complete this sentence for the unit under review:

> “This unit’s architectural role is ______ because its responsibility in the current composition is ______.”

If you cannot complete the sentence cleanly, the classification is incomplete.
