# Owning what you adopt

> The most expensive part of adopting a framework component is not the import. It is that the
> component's internals become **your** problem, one component at a time, forever.

## 1. The claim

When a framework component enters the tree through the seam, ownership of its internals transfers to
the seam — **per component, not once**. Not to the team, not to the design system in the abstract: to
the specific wrapper in the seam tier that now has to know, and keep knowing, how that component
receives focus, what it renders inside itself, which of its flags fight each other, and where our
attributes end up.

Nobody budgets for this, because it does not appear in a visual diff. It appears three weeks later as
"the keyboard path is broken on the new card and nobody can say which change did it".

The tell: **a clean visual diff plus a broken keyboard or focus path.** If the only evidence you have
that an adoption went well is that it looks right, you have evidence about pixels and nothing about
behaviour.

**The trigger is the vendor's name entering the tree, not the line count.** A swap that deletes two
hundred hand-written lines and adds one vendored component reduces the code and *increases* the vendor
surface — and it owes the full intake, exactly like an adoption that added lines. The diff statistic
makes this case look like a simplification, which is how it gets waved through: `-240 / +31` reads as
a cleanup in review, while the tree has just gained a component nobody has focused, a node list nobody
has inventoried, and a ledger row missing from the file that makes upgrades reviewable. Judge the
intake by how many vendor names the change leaves behind, never by whether it shrank the file.

## 2. The four internal families

| Internal | What transfers | How it leaks upward | What the seam must do |
| --- | --- | --- | --- |
| **Focus mechanics** | whether the component is the focus target or hosts one; whether the ring lands on the outer wrapper or an inner node; whether it participates in `:focus-visible`; whether it traps, forwards, or swallows Tab | a consumer styles the wrapper's outline while the inner button is what actually takes focus, so the visible ring appears on the wrong box, or on nothing | decide the focus contract in the wrapper and state it, so no consumer above has to know which node the framework made focusable |
| **Its child nodes** | the extra `div`/`span` layers it renders around what we asked for, their order, their own state classes | our selectors (`> *`, `:first-child`, a spacing rule on children) and our accessibility walk now see nodes we never authored; the framework adds one and our layout quietly shifts | depend on our own attributes, never on its structure; if we must depend on it, that dependency is recorded (§4) |
| **Mutually-exclusive style flags** | prop pairs where one silently wins, or where two together produce a third look nobody designed | a consumer passes both because both are "supported" and gets the framework's precedence rule, which is not documented and changes between versions | the seam refuses the illegal combination — one path in, one meaning per prop — instead of forwarding the argument error upward at runtime |
| **Attribute fallthrough** | where `class`, `style`, `id`, `data-*`, aria attributes and event handlers land when the component has more than one root node or explicitly opts out of inheritance | our test hook, our spacing class, or our `aria-label` is attached to a node two levels down, or dropped entirely | pin the fallthrough target and expose only the attributes whose destination we can name |

The last two are the ones that survive a rewrite: they are **semantic** conflicts, not styling, and
neither the type-checker nor a screenshot objects to them.

## 3. Why it is per component, not per framework

The transfer is not "learn the framework once". Each adopted component has its own DOM shape, its own
prop-precedence table, its own fallthrough behaviour, its own focus node. A tree that adopts twelve
vendor components owes twelve separate reviews, and the review of the thirteenth tells you nothing
about the twelfth.

The count is the cost. Write it down when planning a swap: `N adopted components × (intake review +
one ledger row to keep true on every version bump)`.

## 4. The intake checklist

Per component, at the moment it enters the seam. Steps 4-6 need a running page, not a code read.

```
- [ ] 1 Name it in the seam's own vocabulary; the vendor name stays on one line
- [ ] 2 Declare which props are legal together, and refuse the rest in the wrapper
- [ ] 3 Decide where class/style/data/aria land, and say so in the wrapper's own doc line
- [ ] 4 Focus it. Which node receives it? Where does the visible ring appear? Tab past it both ways
- [ ] 5 Read the node list it renders. Record the depth and the wrappers we must never select through
- [ ] 6 Give it an accessible name the way a consumer would, and confirm the name arrives
- [ ] 7 Add the ledger row (§5); a component without a row is a component nobody owns
- [ ] 8 Ask `treat`: does the library want to be used this way, or are we forcing its shape?
```

Steps 4 and 5 are exactly what a computed-style and pixel diff cannot see, so they belong in the
seam's intake and in a spike's interaction step — the same fact measured by two different skills, on
purpose.

## 5. The internals ledger

One row per adopted component, kept next to the seam (a table in the seam's own doc file is enough —
it is data, not prose):

| Component | Vendor version | Focus node | Extra wrappers | Flag conflicts | Fallthrough target | Who re-verifies on bump |
| --- | --- | --- | --- | --- | --- | --- |
| [card] | [x.y] | [inner button] | [2 divs] | [variant vs outlined] | [outer root] | [the seam owner] |

The ledger is what makes a vendor upgrade reviewable: the diff of the upgrade is scary exactly in
proportion to how many rows it can invalidate, and "we upgraded the framework" is a legitimate reason
to re-run steps 4-6 for each row it touches.

## 6. Where this is not the answer

- A component that never entered through the seam does not have a row; it has a violation. Fix the
  wall first ([the-two-walls.md](./the-two-walls.md)).
- This file does not measure how the swap looks. That is `spike`, and a spike with a clean pixel diff
  and no interaction step is the failure mode this section exists to name
  (`spike/examples/case-02-blind-to-interaction.md`).
- Whether the component's model is being respected at all is `treat`'s question. The ledger records
  the dependency; `treat` tells you whether the dependency is the intended one.
