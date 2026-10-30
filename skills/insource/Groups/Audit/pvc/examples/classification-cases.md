# Classification cases

> Drill cases for the decisions in [`../references/`](../references/). Each case gives a real-looking shape, the question, then the answer and the rule it comes from. Work top to bottom, or jump to the case type you are stuck on. Cover sheet: [`../assets/templates/view-design-sheet.md`](../assets/templates/view-design-sheet.md).

Answer each with three things — **role**, **pole**, and **whether the name is honest**. A correct classification that is named wrongly will still be broken the next time someone reads the folder.

---

## Case 1 — the modal

A dialog with a heading, one sentence of explanation, and two buttons. A developer says "it's a reusable component, we have a Modal library".

<details>
<summary>Answer</summary>

**View.** It presents context + a decision + purposeful actions — a complete focused interaction. Its buttons are Components; the heading and sentence are Decoration; the library dialog primitive underneath is a UI Element. "Reusable" describes the implementation, not the role. [`roles.md`](../references/roles.md) §8, [`worked-trees.md`](./worked-trees.md) §2.
Name: `ConfirmationModalView`, not `ConfirmationModal` — the suffix is the claim that it consults facts and selects cases.
</details>

## Case 2 — the flat `components/` dump

```
components/
├── SearchPageComponent
├── SearchViewComponent
├── SearchTitleComponent
├── SearchKeywordsComponent
└── SearchChipComponent
```

<details>
<summary>Answer</summary>

Four different roles hiding behind one word: Page, View, Decoration, Decoration, UI Element. The structure communicates only that a framework can render them. [`structure.md`](../references/structure.md) §6, [`naming.md`](../references/naming.md) §3.
Fix: split by role into the feature's tiers, keep `Chip` in the global primitive layer, and drop the `Component` suffix everywhere.
</details>

## Case 3 — the fact suffix that renders

```
EtaLoadingState    → renders a spinner and a countdown line
SearchDisabledCondition → renders "Search unavailable"
```

<details>
<summary>Answer</summary>

Both are **defects, not judgment calls**. A name ending in `State`/`Condition` must return data, and something that renders must be a Rendition or a View ([`view-and-rendition.md`](../references/view-and-rendition.md) §3). The first is a Rendition named `MaintenanceLoadingRendition` (or the View's own default case); the second is `SearchDisabledRendition`. A Rendition must be named for what it *displays*, never for the fact that triggered it ([`naming.md`](../references/naming.md) §4b). What kind of fact each name refers to is `/states`' question; the naming prohibition is this skill's.
`scripts/check_pvc.py` flags this pattern mechanically in every supported language.
</details>

## Case 4 — the Rendition that reads a store

A `SearchErrorRendition.vue` imports the search store to get the error text, so the caller doesn't have to pass props.

<details>
<summary>Answer</summary>

It is no longer a Rendition. Reading a fact source — a hook, a composable, a store, an injected service, a `use_resource` call — promotes it to **View** ([`view-and-rendition.md`](../references/view-and-rendition.md) §5). Either rename it `SearchErrorView`, or keep it a Rendition and pass `message` in.
The shortcut is exactly the "case that also acts as the chooser" collapse §5 describes: the parent View stopped selecting, and now two units both claim to own the same branch set.
</details>

## Case 5 — three buttons in a row

`ProfileButtons` wraps a Follow button, a Message button, and a Report button. No shared state, no exclusivity, no ordering requirement.

<details>
<summary>Answer</summary>

**Wrapper Component** — no role of its own, forwarding fanned out to several targets ([`composition-shapes.md`](../references/composition-shapes.md) §3-§4). A plural, purposeful-sounding name smuggled in a responsibility it does not have. Rename `_ProfileButtons` if it sits beside the specific siblings it is scoped to.
If the three start coordinating — reporting disables follow, or order becomes meaningful — it becomes an ordinary **Component**. The test is coordination, never size or count.
</details>

## Case 6 — the debounce pair

`SearchInput` exists, and `DebouncedSearchInput` wraps it with the app's shared `useDebounce`. Nobody else in the feature imports the plain one, because this feature's search is defined as search-as-you-type.

<details>
<summary>Answer</summary>

`DebouncedSearchInput` = **Specialised Component**, Local, composed not copied. `useDebounce` = **Global capability mechanism** (owns a timer effect but produces neither State nor Condition). The plain `SearchInput` is underscored — `_SearchInput` — because no real standalone consumer exists ([`composition-shapes.md`](../references/composition-shapes.md) §5).
Had the feature *also* shipped a Go-button search View that needed the undebounced version, `_SearchInput` keeps its plain name and stays importable. That is a product question first — see Case 11.
</details>

## Case 7 — the shared card body

`FundCardListRendition` and `FundCardGridRendition` both render `_FundCard`. It is meaningless outside `FundCardView`.

<details>
<summary>Answer</summary>

**Global-Local, configuration (a)** — more than one consumer, so not Local; no reason to exist outside a closed family, so not Global. Colocated at the nearest common ancestor of its consumers, inside the View's own folder, underscore-prefixed ([`placement.md`](../references/placement.md) §3, §5; [`worked-trees.md`](./worked-trees.md) §4).
Extract only the genuinely overlapping part. Pulling either Rendition's whole body into the shared file misrepresents parts that were never shared.
</details>

## Case 8 — one consumer, but at the tier

`AddToWatchlist` sits in `funds/components/` and is currently imported by exactly one file. A reviewer says "one consumer → move it inside that View's folder, it's Local".

<details>
<summary>Answer</summary>

The reviewer applied the wrong test. A feature's own `components/` tier was deliberately built as that feature's pool, so anything placed there is **Global-Local, locked to `funds/`**, regardless of current consumer count ([`placement.md`](../references/placement.md) §3.1). Consumer-counting governs files *inside a View's folder*; design-intent governs tiers.
The next quarter's second consumer changes nothing about the file — which is precisely the instability that tells you count was never the right question for a tier.
</details>

## Case 9 — the checkout receipt line

`OrderSummary` and `PaymentConfirmation` are two unrelated Components that both render `_ReceiptLine`. No View above them, no Renditions, no facts. A developer argues Global-Local "only applies to Rendition siblings".

<details>
<summary>Answer</summary>

Global-Local is a **general placement test**, answerable for any two siblings sharing implementation ([`placement.md`](../references/placement.md) §4). The Component/Rendition symmetry merely made the first case easy to notice; it is not a precondition. [`worked-trees.md`](./worked-trees.md) §5 is this exact tree.
</details>

## Case 10 — the tempting cross-feature import

`funds/components/AddToWatchlist` needs the same row layout as `checkout/components/_ReceiptLine`, and a developer imports from `checkout/components/` because "both folders are called `components/`".

<details>
<summary>Answer</summary>

Two separate tiers that share a **name**, not a family. Nothing may cross between sibling features' tiers ([`placement.md`](../references/placement.md) §3.1, §5; [`worked-trees.md`](./worked-trees.md) §8). Same visual depth or the same folder spelling is never evidence of a relationship — only an actual import establishes one, and this one is the violation.
If the row really is purpose-agnostic, promote it to the app-wide layer and both features consume *that* — a third decision, made deliberately, not by accident of folder naming.
</details>

## Case 11 — the hedge

A feature might fire search on keystroke or on a Go button. The team builds both `SearchInput` (eager, fully wired, independently imported) and `DebouncedSearchInput` "so we can switch later".

<details>
<summary>Answer</summary>

This is the failure the axiom exists for: a **product decision that was never made**, disguised as architectural flexibility ([`settled-behavior.md`](../references/settled-behavior.md) §2, §5). No placement rule can classify it, because the input to the classification is missing.
Correct move: go get the decision. Then exactly one of the two shapes survives, and `_SearchInput`'s underscore follows from it (Case 6). Keeping both alive produces two parallel implementations that silently diverge while the real behaviour is settled by trial and error in production.
If both behaviours are genuinely required by *different* settled features, that is a different, answered question — and each feature classifies on its own facts.
</details>

## Case 12 — the primitive that learned about accounts

`Button` has a `variant="delete-account"` branch and imports an icon set named for the settings feature.

<details>
<summary>Answer</summary>

Role drift in the wrong direction. A primitive must be blind to features ([`roles.md`](../references/roles.md) §7, [`primitives-and-imports.md`](../references/primitives-and-imports.md) §1); the moment it knows what it is used for, it is a **Component** and belongs in that feature. Keep `Button` knowing only about `disabled`, `loading`, `size`, `variant`, `type`, and children.
Also check the tier: if features are reaching past `adaptive` to the raw framework control to get this styling, that is a Law 2 violation ([`primitives-and-imports.md`](../references/primitives-and-imports.md) §3).
</details>

## Case 13 — the Page doing layout work

`SearchPage` renders the search input, wires `onChange`, and holds the results array so the header can show a count.

<details>
<summary>Answer</summary>

The Page has taken on View and Component responsibilities. A Page composes Views and stops ([`roles.md`](../references/roles.md) §3, §9). Lift the interaction into `SearchView`; if two sections genuinely need the same result count, that value's *kind* and owner are `/states`' decision, and only once it is settled does [`placement.md`](../references/placement.md) decide where the file sits.
</details>

## Case 14 — the View with no Renditions

`StatisticsView` returns exactly one thing: `<Statistics />`. A reviewer objects that "every View needs a set of Renditions".

<details>
<summary>Answer</summary>

The reviewer has the rule slightly backwards. A View is always the parent of its cases — this one has **exactly one**, the default, which needs no name or file because there is nothing to disambiguate it from ([`view-and-rendition.md`](../references/view-and-rendition.md) §2). Add a loading or empty case and the role does not change; only the count does.
But check the premise: if `StatisticsView` consults no fact at all and can only ever emit one fixed output, it was never a View — it is a Component or Decoration wearing a role suffix ([`naming.md`](../references/naming.md) §3).
</details>

## Case 15 — same control, three roles

```
Button                    standalone, in the primitive layer
ConfirmDeletion           wraps Button with a purpose
SearchInput               uses Button as its trailing Clear action
```

<details>
<summary>Answer</summary>

UI Element → Component → (Component consuming a UI Element). Classification is contextual: the same implementation plays different roles in different compositions ([`roles.md`](../references/roles.md) §8). This is why role cannot be a property stamped onto a file once — it is a claim about what the file is doing *here*.
</details>

## Case 16 — the seam case

`useSearchState()` lives inside `SearchView/`. Two other features want to import it, and the developer proposes moving it to `shared/behaviour/` "so everyone can own it".

<details>
<summary>Answer</summary>

Two questions are tangled here, and they belong to different skills. **Ownership** — who caused the request, who may cancel it, whether two consumers can share one instance — is `/states`, and its answer is that two siblings cannot jointly own one fetch. **Location** — where the file may sit so consumers can find it legitimately — is [`placement.md`](../references/placement.md) §3/§3.1, and it does not follow the wish to share: promote it only if it is genuinely purpose-agnostic (a generic async source others wrap), which is exactly the wrapper case in [`../references/view-and-rendition.md`](../references/view-and-rendition.md) §6.
The order matters: settle ownership first, then place the file. Deciding by "which folder is convenient" is the failure this seam exists to prevent.
</details>
