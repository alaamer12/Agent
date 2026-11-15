# Move 5: concatenated-text stats → visual encoding

## The shape of the "before"

A group of related counts that share one whole (e.g. an outcome breakdown, a resource split, a funnel stage) is expressed as one run of text, all at the same visual weight, joined by separators: `N found · N accepted · N pending · N rejected`. The reader has to hold each number in mind and mentally compute proportion — nothing on screen shows the *shape* of the split, only its digits.

Diagnostic question: is there more than one number here that only makes sense **relative to the others** (a share of a whole), currently expressed only as text? If yes, this move applies.

## The shape of the "after"

The same numbers get a second, parallel representation as a small proportional visual — most often a segmented bar, sometimes a ring or a sparkline depending on what the surrounding layout has room for — where each category's share of the whole is shown by size/angle rather than only by digit. A compact legend beneath or beside it keeps the exact numbers available for anyone who wants precision, so nothing is lost, only supplemented. The color used for each category's segment stays consistent with however that category is represented anywhere else in the interface (the same "accepted" green in a summary chart elsewhere, say).

What makes this a *reasoning-driven* move rather than a component to install:
- The visual doesn't need to be a bar. `[a horizontal segmented bar]` vs `[a small ring/donut]` vs `[a sparkline]` vs `[a horizontal small-multiple of dots/blocks]` are all valid instances — the choice depends on how much horizontal space the surrounding layout actually has and how many categories there are (a bar degrades gracefully with more categories than a ring does).
- The legend doesn't need special styling — reusing whatever the interface already uses for small secondary text is usually right; inventing a new visual language just for this one stat is itself a form of noise.
- Nothing about this move requires a specific templating syntax, a specific class-naming convention, a specific UI framework, or even a web stack at all — the identical reasoning applies to a percentage breakdown in a native mobile app, a CLI-rendered stat, or a printed report: replace concatenated proportional numbers with a small visual encoding of their shares, plus a legend for precision.

## A minimal, illustrative sketch (not a template to copy)

```
[some small proportional shape — a bar, a ring, or similar —
 divided into segments sized to each count's share of the total]
[a short legend line: category name + exact number, for each segment,
 styled however this interface already styles small secondary text]
```
The concrete tags, class names, or component calls that would realize this sketch are entirely dependent on the actual codebase being edited and are deliberately not specified here.
