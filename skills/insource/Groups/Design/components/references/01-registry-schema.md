# The registry schema

`js/stories.registry.js` is the contract. The shell renders from it, the descriptor filter reads state keys
from it, the URL is derived from it, and the checker validates it. Keep it **pure data**: no DOM, no
functions, no imports — a renderer is referenced by key, never embedded.

```js
export const meta = {
  title: "كتالوج المكوّنات",
  caption: "كل حالة لها renderer مستقل و descriptor مشتق من الـ props.",
  facets:   { dir: ["rtl","ltr"], theme: ["light","dark","system"], density: ["comfortable","compact"] },
  defaults: { dir: "rtl", theme: "system", density: "comfortable" },
};

export const components = [
  {
    id: "numeric-field",
    name: "رقم ذو حدين",
    renderer: "numeric-field",
    caption: "min/max/step من الـ descriptor، ورسالة الخطأ جزء من الحالة.",
    states: [
      { key: "valid",   label: "صحيح", via: "props" },
      { key: "invalid", label: "خطأ",  note: "القيمة فوق الحد الأعلى" },
      { key: "disabled",label: "معطل" },
    ],
    props: {
      valid:    { value: 30, unit: "ثانية", min: 0, max: 3600 },
      invalid:  { value: 5000, error: "القيمة يجب أن تكون بين 10 و3600" },
      disabled: { value: 4, min: 1, max: 10 },
    },
  },
];
```

## Field rules (the checker enforces these)

| Field | Rule | Why |
|---|---|---|
| `id` | kebab-case, unique, **stable** | it is in the URL and in permalinks teammates saved; renaming one breaks their bookmarks silently |
| `name` | display name in the product's language | it is the section heading a designer scans |
| `renderer` | key resolving to a renderer function | the seam between data and DOM |
| `caption` | one line: what the component is for | a card without context becomes a shape quiz |
| `states[]` | ≥1, unique kebab `key`, non-empty `label` | a "component with one state" is a bug in the enumeration, not a simple component |
| `states[].note` | optional: what triggers this state in the real product | turns a picture into a spec |
| `states[].via` | `"props"` when the renderer takes no branch on the key | stops the check from demanding a dead `if` — and forces the props to be visibly different |
| `props` | keyed by state key; every declared state either has props or is marked | an unknown key is a typo that hides an unrendered state |
| `facets` (per component) | optional overrides, values must be declared in `meta.facets` | a component that is LTR-only, or has no compact mode, says so here |
| unknown fields | rejected | a field nobody reads is documentation pretending to be data |

## Two duplicate-card traps the checker catches

1. **Identical props under two keys.** `valid` and `preview` with the same object → two cards, one picture.
   Either the states genuinely differ (then the props differ) or one is not a state.
2. **`via: "props"` with no prop difference.** The tool cannot see pixels, so it lists those states as a note
   and asks you to confirm. Confirm means: look at both cards rendered.

## Deriving the state list (do not invent it)

A state belongs in the registry only if it is *reachable in the product* and *visibly different*. The
derivation method is `prototype`'s state hunt, applied per component rather than per screen: rotate reviewer
stances over the component, walk only the condition axes it actually touches, and admit a candidate through
the evidence / reachability / distinctness / consequence filter. Merge states whose recovery is identical;
reject states with no trigger. Full procedure: [`04`](04-state-coverage.md).

The common families, for orientation — not a checklist to fill:

```text
value:    empty · valid · at-min · at-max · overflowing(long content)
input:    validating · invalid(rejected) · readonly · disabled
async:    loading(partial region) · error · stale · retrying
context:  required-off (blocked with a reason) · permission-denied · unknown/unresolvable
selection:none · one · many · collapsed
```

A component that legitimately has three states has three cards. Padding to the list above is the failure mode
of a gallery: it inflates coverage while showing nothing new.

## Growing the registry

- Add the state to `states[]`, the data to `props{}`, then implement the branch — in that order. The registry
  is the specification; the renderer follows it.
- When a component graduates from story-only to used-in-a-page, move the renderer into `js/components/` and
  change the import, not the registry entry. The `id` must survive.
- Registry entries may carry `since` or `owners` (allowed fields) when the project tracks them; do not add
  other metadata — put that in the component's own doc.
