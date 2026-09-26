# Move 6: inline warning → full-width/full-card callout

## The shape of the "before"

A warning or error is attached to its subject by being squeezed into the same visual container as other, unrelated content — a caption line under a form field, a colored span wrapped inside a table cell alongside a name and other metadata, a small red note appended after a toggle row. It's technically adjacent to what it's warning about, but it competes for space and attention with everything else in that same container, and often wraps awkwardly or gets visually deprioritized to the smallest, dimmest text on the screen — the opposite of what a warning should be.

Diagnostic question: is there a warning/error currently sharing a container with other unrelated content, rather than occupying its own space? If yes, this move applies.

## The shape of the "after"

The warning gets its own container, sized to the full width (or full card/section) of whatever region it belongs to — not shrunk to fit inside something else. Structurally it carries, in order: an icon signaling severity, a short bold headline stating the concrete problem in plain language, one supporting sentence with the detail or cause, and — where there's a fix — a direct action the reader can take right there. The background uses a soft tint of the relevant status color (not a saturated, alarming fill) so it reads as an important, calm signal rather than a shout.

This is also the natural moment to rewrite the copy itself, independent of layout: technical or blame-the-data phrasing ("value does not match expected schema," "classifier term list mismatch") becomes a plain statement of the actual consequence and, where possible, the fix — a copy change that matters as much as the layout change but is easy to skip if only the markup gets attention.

What makes this reasoning-driven rather than a component to install:
- "Full-width" doesn't mean literally 100% of the viewport — it means the full width of whatever logical region this warning belongs to (a row spanning a table's columns, a card's own width, a section's content column). The specific unit of "full" depends entirely on the surrounding layout.
- The action, if present, can be a link, a button, or an inline control — whichever matches how actions are already expressed elsewhere in that interface. Introducing a new action pattern just for warnings creates inconsistency, which is itself a form of noise this skill is trying to remove.
- None of this depends on a specific markup element, a specific CSS methodology, or a specific platform — the identical shape (icon, bold claim, explanation, action, soft severity-tinted background, full logical width) applies whether the surrounding interface is a web table, a native settings screen, or a terminal dashboard rendering colored panels.

## A minimal, illustrative sketch (not a template to copy)

```
[a container spanning the full width of its logical region, background
 tinted softly in the warning/danger color already used elsewhere for that status]
  [severity icon]  [bold: the concrete problem, plainly stated]
                   [one sentence: cause or detail]
                   [optional: a direct action, styled like other actions nearby]
```
The concrete element, attribute, or component that would realize this sketch is deliberately not specified — it depends entirely on the codebase being edited.
