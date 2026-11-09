# Move 3: fold non-scanned values into plain text, keep scanned values distinct

## The shape of the "before"

A row or card lists several attributes, and all of them get the same treatment — each wrapped as its own small distinct visual object (a pill, badge, chip, tag), regardless of what the reader actually does with that value. The result is a run of many same-weight objects that all compete for attention equally, even though, functionally, only one or two of them are things a reader compares *across* many rows, while the rest are only ever read *within* the one row someone is already looking at.

Diagnostic question: for each attribute currently rendered as its own distinct object, would a reader ever scan down a whole list of rows looking specifically for this value, to compare or filter by it? Or would they only ever notice it once they're already reading this particular row for another reason?

## The shape of the "after"

Split the attributes into two groups based on the answer above, not based on any fixed category like "type stays a badge, config never does" — the split is a judgment call about *this* interface's actual use, and it can come out differently for the same kind of attribute in a different context.

- **Scanned-across values** (the reader compares these while scanning many rows) keep their own distinct visual treatment — whatever this interface already uses for that (a colored pill, an icon, a short label) — because that distinctness is exactly what makes scanning fast.
- **Confirmed-within values** (the reader only checks these once already reading this one row) collapse into a single plain-text line, with emphasis (bold, a stronger color) reserved only for the specific part of that line that's actually decision-relevant — not the whole line, and not none of it.

What makes this reasoning-driven rather than a rule to apply uniformly:
- The same literal attribute (say, a status label) might be a scanned-across value in one interface (a list the user filters by status constantly) and a confirmed-within value in another (a detail view where status is mentioned once, for context, and never compared across items). The visual treatment should follow the actual use in *this* interface, not a fixed mapping of attribute-name to treatment.
- Folding several values into one plain-text line doesn't mean stripping all structure — a consistent separator (however this interface already separates small inline facts) and selective bold/color on the one or two values worth a glance is still a deliberate design decision, not just concatenation.

## A minimal, illustrative sketch (not a template to copy)

```
[scanned-across value(s): kept as their own small distinct visual object(s),
 styled however this interface already styles that kind of object]
[confirmed-within values: one plain-text line, [separator] between them,
 emphasis only on the value(s) actually worth a glance]
```
The concrete element or component realizing either half of this sketch depends entirely on the codebase being edited, and is deliberately not specified here.
