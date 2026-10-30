# Authoring a component

The gallery is only as honest as the renderers behind it. A component is authored once and consumed by pages
and stories alike; here is the shape that survives that.

## The signature

```js
/** @param {object} props  @param {string} stateKey  @returns {Element} */
export function numericField(props, stateKey) { … }
```

- **Pure with respect to the page.** No fetching, no globals, no reading the current URL, no writing to shared
  state. It builds an element; the caller decides where it goes.
- **Idempotent.** Calling it twice returns equivalent elements. A renderer with module-level counters or
  captured DOM breaks the moment the gallery re-renders on a keystroke.
- **Never reads facets.** Theme/density/direction are CSS concerns; a renderer branching on
  `document.dataset.theme` duplicates what tokens already do and disagrees with them after a refresh.

## Real states, not paint

The test for every state: *would the browser behave differently?*

| State | Real implementation | Impostor |
|---|---|---|
| `disabled` | `el.disabled = true`, `aria-disabled`, no pointer events, focus skipped, and the label stays legible | `opacity: .5` on a live control |
| `invalid` | `aria-invalid="true"`, the error rendered in the field's error slot, the message from the same validator the product uses | red border only |
| `required` | `aria-required`, the empty-submit message path | an asterisk |
| `loading` | the declared region only shimmers; the rest of the form stays usable | a full-card shimmer |
| `readonly` | selectable text, no editing affordance | disabled styling |
| `valid` | the accepted value, formatted as the product formats it | the default render, unlabelled |
| `empty` | the placeholder and hint the product shows before any data | an input with `""` and no context |

An impostor is worse than a missing card: it passes review and ships a component that does not behave.

## Accessibility is part of the state

Each card is the smallest place to check it, so check it there:

- Every control gets a name — `aria-label`, a real `<label for>`, or visible text. A card with an unnamed
  input is a card that will ship unnamed.
- Focus order and visible focus ring survive the state: a disabled control must not be tabbable; an error must
  be reachable by a screen reader from the field it describes (`aria-describedby`).
- Role switches where the widget is one: `role="switch"` + `aria-checked`, `aria-expanded` on the picker,
  `aria-live="polite"` on the validation message so it announces once.
- Hit targets stay ≥ ~24px in `compact` density, including icon-only buttons.
- Color is never the only signal: `invalid` carries a message, not just a red ring — which is also what makes
  the card readable in a screenshot.

## Copy rules

- **Subject-grounded, never Lorem.** A numeric field about request limits shows a request limit; a file picker
  shows `cookies.txt`, not `file.pdf`.
- **Write the error the product would write**, in the product's language, including the recovery: "القيمة يجب
  أن تكون بين 10 و3600" beats "خطأ".
- **Include the ugly cases deliberately**: a 90-character value, an unbroken token with no spaces (a URL or an
  ID — the classic overflow), a string containing `<script>` (must be rendered as text, never interpreted),
  digits mixed with Arabic, an emoji, a trailing space.
- **RTL text with Latin identifiers** is a bidi test in disguise; put the Latin token in the middle of the
  Arabic sentence, not at the end.

The `<script>` case is not hypothetical and it is a security property of the renderer: build DOM with
`textContent` and `createElement`. A renderer that does `el.innerHTML = props.value` makes the gallery an
attack surface with the reviewer's own browser on the wrong end of it.

## The story entry that proves it

Adding a component means adding its registry entry in the same change — the component and its story are one
unit of work:

```js
{
  id: "file-picker", name: "اختيار ملف", renderer: "file-picker",
  caption: "اسم الملف فقط يظهر، والمحتوى لا يُقرأ في المتصفح.",
  states: [
    { key: "empty",    label: "فارغ",  via: "props" },
    { key: "selected", label: "محدد",  via: "props" },
    { key: "invalid",  label: "نوع مرفوض", note: "الامتداد غير مدعوم" },
  ],
  props: {
    empty:    { label: "ملف الجلسة", hint: "لم يتم اختيار ملف بعد" },
    selected: { label: "ملف الجلسة", file: "cookies.txt", action: "تغيير" },
    invalid:  { label: "ملف الجلسة", file: "session.exe", error: "النوع غير مدعوم" },
  },
}
```

Then: `validate`, `coverage`, render the three URLs, look. If a card is indistinguishable from its neighbour,
either the props are wrong, the state is not real, or the renderer does not implement it — all three are
findings, and all three are cheaper to fix now than in the page that adopts the component.

## When the component is not ready

Say so in the report and render the gap: a card whose renderer is missing shows the dashed
"renderer غير موجود" placeholder. A hole you can see gets fixed; a plausible-looking card gets shipped.
