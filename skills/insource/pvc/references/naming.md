# Naming — what a name must signal

> Names are the load-bearing part of this architecture: they are how a reader identifies a role without opening the file. Consolidates every naming rule in one home — [`roles.md`](./roles.md) tells you the role, this tells you what to call it. Read [`facts.md`](./facts.md) and [`view-and-rendition.md`](./view-and-rendition.md) first for why two of these suffixes are hard prohibitions.

## 1. The suffix table

| Role | Suffix / shape | Example |
| --- | --- | --- |
| Page | `…Page` | `SearchPage`, `ProfilePage` |
| View | `…View` | `SearchView`, `ConfirmationModalView` |
| Component | purpose, **no suffix** | `SearchInput`, `PaymentForm`, `ConfirmDeletion` |
| Decoration | what it supplies | `SearchDescription`, `CommonKeywords`, `PasswordHint` |
| Aligner | no suffix — role read from position | `SearchIcon`, `ClearButton` |
| UI Element | the primitive's own name | `Button`, `Input`, `Chip` |
| Rendition | what it **displays** + `…Rendition` | `SearchDisabledRendition`, `MaintenanceRendition` |
| State fact source | `…State` | `useSearchState`, `searchState()` |
| Condition fact source | `…Condition` | `useNetworkCondition`, `MaintenanceCondition` |
| Wrapper / scoped-shared | `_` prefix | `_FundCardActions`, `_FundCard`, `_ReceiptLine` |
| Specialised Component | base purpose + capability | `DebouncedSearchInput` |

Adapt the casing and file conventions to your framework — a Blazor unit is `SearchView.razor`, a Vue unit is `SearchView.vue`, a Dioxus function is `search_view()` — but keep the *word* signalling the role. See [`framework-adapters.md`](./framework-adapters.md).

## 2. General rule

A name communicates either **what the object represents** or **what purpose it serves**. Both fail → the name is noise:

```
avoid:  Container1, Section2, ComponentA, Wrapper, Box, Thing, MainView,
        SectionView, ContentView, DataHandler
```

`MainView` and `SectionView` are the same failure as `Container1` with a role suffix attached — a suffix does not make a meaningless name meaningful unless the section is genuinely, recognisably "the main section".

## 3. Role suffixes are not decorative

A `View` suffix means the unit consults facts and selects between cases. A `Component` name means one purposeful function. Using them as styling rather than as claims is what makes a codebase unreadable:

```
✘  SearchTitleComponent, SearchKeywordsComponent   → hides that these are Decorations
✘  ConfirmationModal (as "just a reusable component") → it is a View; name it so
✔  SearchTitle / CommonKeywords                     → role visible from the name
✔  ConfirmationModalView                            → a focused interaction, correctly labelled
```

The base law behind all of this: a framework's unit is not an architectural Component ([`roles.md`](./roles.md) §1), so the framework's naming habits are not a naming convention here.

## 4. The two hard prohibitions

**(a) A fact suffix must never be used by something that renders.**

```
✔  useSearchState()          → returns data
✔  SearchLoadingRendition    → returns markup
✘  SearchState               → returns markup: a Rendition wearing a fact suffix
✘  SearchDisabledCondition   → same defect
✘  EtaLoadingState           → same defect
```

No exceptions, regardless of which fact prompted it. This is the single most common defect in this system and the one [`../scripts/check_pvc.py`](../scripts/check_pvc.py) detects most reliably.

**(b) A Rendition is named for what it displays, never for the fact that triggered it.**

The disabled Rendition of a search displays a "search unavailable" message; it is not itself the offline condition. Naming from the trigger rather than the content is what makes the two concepts collapse back into each other.

If a Rendition needs its *own* internal fact branching, that is the point at which it has stopped being a Rendition — rename it as a View ([`view-and-rendition.md`](./view-and-rendition.md) §5). A Rendition that calls a fact source has silently promoted itself.

## 5. Vocabulary inside names and comments

Say **branch** or **case** for a View's outcomes; reserve **State** and **Condition** exclusively for the facts. "SearchView has four branches" is unambiguous; "four states" forces the reader to guess between two real concepts. Rule and reasoning: [`view-and-rendition.md`](./view-and-rendition.md) §4.

## 6. The `_` prefix

`_` signals **"shared-but-scoped, not an independent export"** — a reader scanning the folder can tell at a glance which file is the View, which are its Renditions, and which is internal scoped implementation. It applies to:

- **Global-Local configuration (a)** — a file beside the specific siblings it is scoped to ([`placement.md`](./placement.md) §5). Files in a feature-wide tier do **not** need it; the tier folder already signals the lock.
- **Wrapper Components** — no responsibility of its own beyond grouping ([`composition-shapes.md`](./composition-shapes.md) §4).
- **A Specialised Component's base** — only when no standalone consumer exists for this feature's settled behaviour ([`settled-behavior.md`](./settled-behavior.md) §3 gates this; it is a decision, not a default).

The prefix is a convention, **not a mechanical requirement** — nothing enforces it, and no rule's answer changes if a project spells it differently or uses a `internal/` subfolder instead. It exists so a reader learns "not for import" without opening the file, for the same reason a Rendition is described as not independently addressable.

## 7. Aligners specifically

Because Aligners are Decorations ([`roles.md`](./roles.md) §6), their names do not need the word `Aligner`. `SearchIcon` and `ClearButton` are fine; their role is read from their positional relationship to the primary Component. **Aligner is an architectural classification, not a naming convention** — inventing `SearchLeadingAligner` would name the role instead of the thing.

## 8. The name test

Before committing, read the name in the parent's composition:

```
<SearchView>  contains SearchDescription, SearchInput, CommonKeywords
```

Can a reader who has never opened a file tell which is the primary function and which are supporting? If not, the names are carrying no information — which is the defect this whole file exists to prevent.
