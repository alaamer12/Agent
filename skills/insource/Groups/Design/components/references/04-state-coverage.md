# State coverage

The gallery's only claim is "here is every state this component can be in". That claim is either checked or
worthless, and the checking is mechanical enough that no one should eyeball it.

## Deriving the set (per component, not per template)

Borrow `prototype`'s hunt rather than inventing a state checklist:

1. **Walk the conditions the component actually touches.** A toggle never has "no results"; a table always
   does. Enumerate by asking what the component reads: its value, its validity, its async source, the user's
   permission, the selection set, the container width.
2. **Rotate reviewer stances** over it: the first-time user (empty), the impatient one (loading, double
   submit), the hostile one (rejected input, `<script>` in a field), the one on a slow connection (stale,
   retry), the one without rights (permission-denied), the one with too much data (overflow, 90-character
   name, 400 chips).
3. **Admit a candidate through four gates:**
   - *evidence* — the product can reach it (a real trigger exists);
   - *reachability* — a user or a network condition actually causes it;
   - *distinctness* — it looks or behaves differently from an admitted state;
   - *consequence* — recovery differs. Two states whose recovery is identical merge into one card.
4. **Fail closed on unknown.** "Something we did not anticipate" is a state; render it as unknown, never as the
   happy path.

A component with three real states gets three cards. Padding to a checklist inflates coverage while showing
nothing new — the same defect as a test that asserts nothing.

## The four coverage defects

| Defect | Meaning | Detector |
|---|---|---|
| **declared, not implemented** | the registry promises a state the renderer never branches on — the card silently renders the default look | `stories_check.mjs coverage` reports the key as unbranched, unless the state declares `via: "props"` |
| **implemented, not declared** | the renderer handles a state nobody can reach from the gallery | read the renderer's branches against the registry; each `stateKey ===` in the source should have a matching state entry |
| **two states, one picture** | identical props under two keys | `duplicate:` finding from `validate` |
| **props-driven without props** | `via: "props"` states whose props are indistinguishable | the `coverage` note lists them for visual confirmation — the tool cannot see pixels, so a human must |

Run both commands, then **look at the cards**. The script narrows the search; it does not certify.

## `via: "props"` — the honest escape hatch

Some states differ only in data: `valid` vs `at-max` is a value, not a code path. Declaring
`via: "props"` says "no branch here, and that is correct", and the checker stops demanding a dead `if`.
Abusing it is visible: the tool lists those states and asks you to confirm their props differ. Adding
`if (stateKey === "valid") { /* does nothing */ }` purely to satisfy a linter is the failure mode this field
exists to prevent.

## Unreachable and aspirational states

A state with no trigger in the product does not get a card. If it is *planned*, it goes in the project's
roadmap or a note, not in the gallery — because the gallery is read as a statement of what the component does
today, and a reviewer will otherwise build against a state nobody implemented.

When a state is genuinely reachable but the component cannot show it yet (the async error path is not wired),
the correct artifact is a card that renders the **failure to render** plus a line in the report. A fake that
looks real is worse than a hole you can see.

## Coverage as a review artifact

The matrix is the deliverable, so make it countable:

```text
COMPONENTS  16 declared · 16 rendering · 0 error cards
CARDS       61 states · 4 via:props awaiting visual confirmation
GAPS        file-picker: no permission-denied state (trigger exists in upload flow)
            slider: at-max not distinct from valid at 12px density — merged
URLS        cards.txt: 61 lines, one per card, facets preserved
```

`GAPS` is the section a reviewer reads first. A report with an empty `GAPS` line is a claim that the
enumeration was exhaustive — say honestly what was not walked.
