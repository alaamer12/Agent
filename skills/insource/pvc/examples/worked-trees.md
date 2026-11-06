# Worked trees

> The single canonical home for every worked tree in this system. The rules these trees apply live in [`../references/placement.md`](../references/placement.md), [`../references/view-and-rendition.md`](../references/view-and-rendition.md), and [`../references/facts.md`](../references/facts.md); code in five frameworks is [`polyglot-walkthrough.md`](./polyglot-walkthrough.md). If a tree appears anywhere else, that copy is stale — this file is the source of truth.
>
> `.*` in these trees means "your framework's unit extension" — `.tsx`, `.vue`, `.razor`, `.svelte`, `.rs` ([`../references/framework-adapters.md`](../references/framework-adapters.md)). Folder names are illustrative too; no rule here checks spelling ([`../references/placement.md`](../references/placement.md) §3.1).

## 1. Search — role classification of one View

The interface:

```
Search
Search for users, posts, or topics...

[ 🔍 Search..................... ]

Common searches:
[React] [Python] [JavaScript]
```

```
SearchView                        ← VIEW (one meaningful section)
├── Title            → Decoration
├── Description      → Decoration
├── SearchInput      → Component  (the primary functional focus)
│   ├── SearchIcon   → UI Element / Leading Aligner
│   ├── Input        → UI Element
│   └── ClearButton  → UI Element / Trailing Aligner
└── CommonKeywords   → Decoration
    └── Chip[]       → UI Elements
```

The whole thing is one View. `SearchInput` is its primary Component. The surrounding text explains the interaction rather than performing it, so it is Decoration. The leading and trailing pieces are Aligners — positional Decorations. The raw controls are primitives.

## 2. Modal — the classic "it's just a component" case

```
ConfirmationModalView              ← VIEW, not a Component
├── ConfirmationText   → Decoration / Aligner
├── ConfirmAction      → Component
└── CancelAction       → Component
```

It is a View because it presents a complete focused interaction: context, a decision, and purposeful actions. Its buttons are Components because each has a user-facing purpose; the underlying button control is a UI Element. That the modal is *implemented* with a framework's dialog primitive says nothing about its role ([`../references/roles.md`](../references/roles.md) §8).

## 3. Page — composition only

```
ProfilePage
├── ProfileHeaderView
│   ├── ProfileAvatar   → Component
│   ├── ProfileName     → Decoration
│   └── EditProfile     → Component
├── ProfileStatisticsView
│   ├── StatisticsTitle → Decoration
│   └── Statistics      → Component
└── ProfileActionsView
    ├── FollowUser      → Component
    └── MoreActions     → Component
```

The Page names sections and stops. It never composes a `Button` or an `Input` directly. Same feature, laid out:

```
features/profile/
├── views/         ProfileHeaderView · ProfileStatisticsView · ProfileActionsView
├── components/    ProfileAvatar · EditProfile · Statistics · FollowUser · MoreActions
├── decorations/   ProfileName · StatisticsTitle
└── behaviour/     feature fact sources and services
```

## 4. Global-Local via Component/Rendition symmetry

Two sibling Renditions of one View share a *partial* Component that means nothing outside this View:

```
features/funds/
└── views/
    └── FundCardView/
        ├── FundCardView.*           ← VIEW: reads the layout-toggle Condition,
        │                               selects one Rendition                    [LOCAL to the folder]
        ├── FundCardListRendition.*  ← Rendition: _FundCard + List-only pieces    [LOCAL]
        ├── FundCardGridRendition.*  ← Rendition: _FundCard + Grid-only pieces    [LOCAL]
        ├── _FundCard.*              ← GLOBAL-LOCAL (a): the genuinely overlapping
        │                               part only — not either Rendition's body
        └── _FundCardActions.*       ← WRAPPER COMPONENT [LOCAL]: AddToWatchlist,
                                        CompareFund, RemoveFund do not coordinate
```

Classification, one line each:

```
_FundCard         → Global-Local Component — 2 real consumers in this folder,
                    zero reason to exist if either sibling is deleted (placement.md §3)
_FundCardActions  → Wrapper Component — no role of its own, pure structural grouping
├── AddToWatchlist→ Component — Local HERE; would be Global-Local to funds/ if
├── CompareFund     placed in funds/components/ instead (placement.md §3.1)
└── RemoveFund    → Component
FundCompactBadge  → Decoration / Aligner — Local HERE, same caveat
```

Two things this tree is built to show. `_FundCard` is deliberately **partial**: each Rendition still renders its own unique sub-pieces alongside it. Over-extracting the whole Rendition body misrepresents parts that were never shared. And `AddToWatchlist` / `FundCompactBadge` are Local *here* purely because of where they are drawn — placing them one level up in the feature's own tier would make them Global-Local by the tier test regardless of consumer count. Placement, not nature.

## 5. Global-Local with no View, no Rendition, and no fact

The pole is a general placement test, not a consequence of Component/Rendition symmetry. Here it applies with none of that machinery present — two ordinary sibling Components sharing a sub-piece:

```
features/checkout/
└── components/                 ← the feature's own Component tier
    ├── OrderSummary.*          ← Component: the cart before payment
    ├── PaymentConfirmation.*   ← Component: the result after payment
    └── _ReceiptLine.*          ← GLOBAL-LOCAL: consumed by both above, and no other
                                    feature has any use for "a checkout receipt line"
```

Nothing consults a fact. Nothing selects between sibling outcomes. There is no View above them making a choice. Delete both consumers and `_ReceiptLine` has no remaining consumer and no reason to exist, so the §3 test answers Global-Local, placed at the nearest common ancestor of its two consumers.

## 6. The two Global-Local configurations, side by side

The same `funds/` feature, drawn to show both configurations at once:

```
features/funds/
│
├── views/
│   └── FundCardView/
│       ├── FundCardView.*              LOCAL to the folder
│       ├── FundCardListRendition.*     LOCAL to the folder
│       ├── FundCardGridRendition.*     LOCAL to the folder
│       ├── _FundCard.*                 (a) GLOBAL-LOCAL — §3's test: real,
│       │                                 countable consumers in this exact folder
│       └── _FundCardActions.*          LOCAL — Wrapper Component
│
├── components/                 (b) THE TIER ITSELF is GLOBAL-LOCAL, locked to funds/
│   │                             — §3.1's test. Everything placed here is available
│   ├── AddToWatchlist.*        to any View funds/ has now or ever will have,
│   ├── CompareFund.*           regardless of how many import it today.
│   └── RemoveFund.*            No underscore needed: the tier signals the lock.
│
├── decorations/                (b) same tier-lock
│   └── FundCompactBadge.*
│
└── behaviour/                  (b) same tier-lock
    └── useLayoutToggleCondition.*   CONDITION (fact only, read-only to every
                                       consumer); tier-locked to funds/, not owned
                                       by FundCardView specifically
```

**Both configurations legitimately coexist in one feature.** `_FundCard` stays inside `FundCardView/` because it is scoped to that View's two Renditions and promoting it to `funds/components/` would be a lie — no other View in `funds/` has any use for the partial shared body of one specific card. `AddToWatchlist` has no inherent tie to `FundCardView`, so placing it at the tier states "any View this feature grows may use these" — a design decision, not a consumer count.

## 7. The full composite project tree

Every concept in this system in one consistent structure.

```
src/
│
├── app/
│   ├── routes/                         index · funds · checkout · search
│   └── pages/
│       ├── FundsPage.*                 ← PAGE: composes Views, no primitive detail
│       ├── CheckoutPage.*              ← PAGE
│       └── SearchPage.*                ← PAGE
│
├── features/
│   ├── funds/                                            ══ §4 and §6 ══
│   │   ├── views/FundCardView/
│   │   │   ├── FundCardView.*          ← View: reads the toggle Condition,
│   │   │   │                              selects a Rendition
│   │   │   ├── FundCardListRendition.*  ← Rendition: data in, markup out
│   │   │   ├── FundCardGridRendition.*  ← Rendition
│   │   │   ├── _FundCard.*              ← GLOBAL-LOCAL (a), §3's consumer test
│   │   │   └── _FundCardActions.*       ← LOCAL, Wrapper Component (no role)
│   │   ├── components/                 ← GLOBAL-LOCAL (b), LOCKED to funds/
│   │   │   ├── AddToWatchlist.*        ← consumed today by _FundCardActions;
│   │   │   ├── CompareFund.*              tier-locked regardless
│   │   │   └── RemoveFund.*
│   │   ├── decorations/                ← GLOBAL-LOCAL (b), LOCKED to funds/
│   │   │   └── FundCompactBadge.*      ← glanceable, non-interactive, an Aligner
│   │   │                                 relative to _FundCard
│   │   └── behaviour/                  ← GLOBAL-LOCAL (b), LOCKED to funds/
│   │       └── useLayoutToggleCondition.*  ← CONDITION: fact only, read-only
│   │
│   ├── checkout/                                                       ══ §5 ══
│   │   └── components/                 ← GLOBAL-LOCAL (b), LOCKED to checkout/ —
│   │   │                                 a SEPARATE tier from funds/components/.
│   │   │                                 Sharing the folder NAME is not sharing a
│   │   │                                 family: no import may cross between them.
│   │   │   ├── OrderSummary.*
│   │   │   ├── PaymentConfirmation.*
│   │   │   └── _ReceiptLine.*          ← also satisfies §3's narrower test on its
│   │   │                                 own: two real, countable consumers, no
│   │   │                                 View, no Rendition, no fact anywhere
│   │   │
│   └── search/                                                          ══ §1 ══
│       ├── views/SearchView/
│       │   ├── SearchView.*            ← View: READS useNetworkCondition (shared),
│       │   │                              OWNS useSearchState (its own fetch)
│       │   ├── SearchDisabledRendition.*  ← LOCAL (offline branch)
│       │   ├── SearchLoadingRendition.*   ← LOCAL (loading branch); forwards to
│       │   │                                 the global LoadingRendition —
│       │   │                                 forwarding, not tier-locking
│       │   └── SearchErrorRendition.*     ← LOCAL (error branch)
│       ├── components/SearchInput/
│       │   ├── _SearchInput.*          ← Component. Underscored because this
│       │   │      · uses adaptive Icon    feature's search is SETTLED as
│       │   │      · uses adaptive Input   keystroke-firing and no standalone
│       │   │      · uses adaptive Button  caller wants it undebounced — the
│       │   │                              settled-behavior gate, not a default
│       │   └── DebouncedSearchInput.*  ← SPECIALISED COMPONENT: composes
│       │                                  _SearchInput + the shared debounce
│       │                                  mechanism. LOCAL — one-off fusion,
│       │                                  not Global-Local (no family, one pairing)
│       ├── decorations/
│       │   └── SearchDescription.*     ← GLOBAL-LOCAL (b), locked to search/
│       └── behaviour/
│           └── useSearchState.*        ← STATE: caused and owned by whichever View
│                                          in search/ calls it; tier-locked
│
├── ui/                                                    ══ TRUE GLOBAL ══
│   ├── base/                         ← GLOBAL, no lock. The only place the
│   │   ├── Button.*                     framework/platform primitive may exist,
│   │   ├── Input.*                      re-declared under this system's name.
│   │   ├── Icon.*                       A one-line re-export is a complete,
│   │   ├── Text.*                       correct file — do not add props or logic
│   │   └── Spinner.*                    to justify it.
│   ├── adaptive/                     ← GLOBAL, no lock. base + this system's skin:
│   │   ├── Button.*                        variants, tokens, states, generic
│   │   ├── Input.*                           decorators. Still purpose-agnostic,
│   │   ├── Icon.*                            still zero feature knowledge, built
│   │   ├── Text.*                            ONLY from ui/base/. Components
│   │   └── Spinner.*                         consume THIS tier, never base.
│   └── renditions/
│       └── LoadingRendition.*        ← GLOBAL Rendition: reusable, parameterised,
│                                         still data-in / markup-out
│
└── shared/                                                  ══ TRUE GLOBAL ══
    ├── conditions/                   ← GLOBAL, no lock. "shared/" is a folder NAME,
    │   ├── useNetworkCondition.*          not required vocabulary — what makes
    │   └── useMaintenanceCondition.*      these Global is that any feature may
    │                                      import them
    ├── views/MaintenanceView/
    │   ├── MaintenanceView.*         ← GLOBAL View: READS useMaintenanceCondition,
    │   │                                 OWNS the nested ETA State below — the
    │   │                                 asymmetric composition, facts.md §5
    │   ├── behaviour/
    │   │   └── useMaintenanceEtaState.* ← STATE owned by THIS View specifically:
    │   │                                    LOCAL to the folder despite sitting
    │   │                                    physically under shared/ — ownership
    │   │                                    is decided by causation, never by
    │   │                                    which ancestor folder a file sits in
    │   ├── MaintenanceLoadingRendition.* ← LOCAL
    │   ├── MaintenanceErrorRendition.*   ← LOCAL
    │   └── MaintenanceRendition.*        ← LOCAL (the default/success case)
    └── behaviour/
        ├── useAsyncState.*           ← GLOBAL generic State mechanism: owns
        │                                 whatever request it is handed. A local
        │                                 State source may wrap it — ownership
        │                                 passes through the wrapper unchanged
        └── useDebounce.*             ← GLOBAL generic CAPABILITY mechanism. Owns a
                                          timer effect but produces NEITHER State
                                          nor Condition: it is not consulted by a
                                          View to select a Rendition, it is a
                                          mechanism a Component consumes to reshape
                                          when it acts. Reused by DebouncedSearchInput
```

## 8. What does *not* make something Global-Local

- Sitting at the same visual depth as a sibling feature. `funds/` and `checkout/` are siblings; nothing crosses between them, so no lock exists between them.
- Sharing a folder *name* with another feature's tier. `funds/components/` and `checkout/components/` are two separate locks, not one pool.
- Having only one consumer today, when the file was placed in a feature's own tier. The tier's design intent overrides the count.
- Being physically nested under a folder called `shared/`. Only actual importability by any feature makes something Global — `shared/` is a naming convention, not a mechanism.
- Being a fact source at all. State and Condition ownership is settled by causation before placement is asked ([`../references/facts.md`](../references/facts.md) §5), which is the one documented place the poles do not apply.
