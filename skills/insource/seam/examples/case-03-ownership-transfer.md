# Case 03 — a clean visual diff, a broken keyboard

*Names, paths and numbers here are illustrative. The shape is what transfers.*

## The claim being tested

"Swap our card for the framework's card. It will be a visual change; the look is the risk."

The swap was measured properly for looks: same states captured before and after, computed styles
diffed, tight crops compared. The verdict came back: the appearance survives, two cosmetic
differences, nothing structural. That verdict was correct and completely useless, because the risk
that materialised was not the one the claim named.

## What actually broke

Two days after the swap, the keyboard path on the list screen was reported as broken. Four separate
transfers of ownership had happened, all invisible to a style diff:

| Internal | The framework's card | What it cost us |
| --- | --- | --- |
| **Focus node** | the card itself is not focusable; it renders an inner button that takes focus | our wrapper styled `outline` on the outer element, so the visible ring vanished. Tab landed on something with no visible indicator |
| **Child nodes** | two extra wrapper `div`s around the slot we author | our `> * + * { margin }` spacing rule stopped matching direct children; every card in the list lost its gap, one of the two "cosmetic" diffs the style run had already waved off |
| **Flag conflict** | `variant="elevated"` and the outline flag are not exclusive; the second silently wins | a consumer passing both got a different card than the props describe, with no error anywhere |
| **Fallthrough** | with multiple root nodes, our `class` and `data-*` landed on an inner node, not the root | our test hook found the wrong box, and the card's accessible name came from markup we never wrote |

Nothing here is visible in a screenshot of a resting card. The first, second and fourth are visible
only by focusing the element or reading its node list; the third is visible only when someone passes
the combination.

## What was added

1. **Per-component intake**, not per-framework: name in our vocabulary, legal prop combinations
   decided in the wrapper, focus contract declared, fallthrough target pinned, node list recorded.
   Eight steps, run once for the card and once again for the next thing adopted.
2. **An internals ledger**: one row per adopted component — vendor version, focus node, extra
   wrappers, flag conflicts, fallthrough destination, and who re-verifies it on an upgrade. The card
   got a row. The eleven components already inside the seam got rows retroactively, which was the
   expensive part and the honest one.
3. **The interaction step moved into the spike's checklist.** The visual measurement was not wrong;
   it was incomplete, and the incompleteness was not reported as a limit of the method.
4. A standing note in the seam doc: adopting a component transfers ownership of its internals to the
   seam, per component, not once.

## The lesson about the shape of the estimate

The swap was estimated as `1 component × (a look fight)`. The true cost was
`1 component × (look fight + four internals) + 11 components × (retroactive intake)`. The
retroactive part is what nobody budgets: the seam already held components adopted before anyone asked
where their focus ring lands, and the ledger says those rows are empty.

The tell to remember: **clean visual diff plus a broken keyboard or focus path means the diff was not
the measurement you needed.** See [../references/ownership-transfer.md](../references/ownership-transfer.md).
