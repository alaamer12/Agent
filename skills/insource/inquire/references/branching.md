# Branching (dynamic follow-ups)

An answer can reveal new questions, new options, or whole branches. Everything is evaluated live in the browser. A follow-up can itself lead to another follow-up.

## The `when` rule

Put `when` on a **question** (shows or hides the question) or on an **option** (shows or hides that option). A rule is an object:

| Rule | Meaning |
|---|---|
| `{"q":"sched","is":[1]}` | question `sched` currently has option index 1 selected (any of the listed indexes) |
| `{"q":"keep","custom":true}` | the user typed their own answer to `keep` |
| `{"all":[rule, rule]}` | every rule is true |
| `{"any":[rule, rule]}` | at least one rule is true |
| `{"not":rule}` | the rule is false |

Option indexes are the 0-based positions in `opts`, counting every option, including ones hidden by their own `when`.

Rules for question `when`: refer only to **earlier** questions. A hidden question counts as unanswered, so its dependants hide too (cascade). Option `when` may refer to earlier questions or to earlier options of the same question.

## Examples

Follow-up question after one option:
```json
{"id":"mailer","when":{"q":"sched","is":[1]}, "q":"Does this server have a working mail relay?", ...}
```
A question two levels deep (shown only after the previous follow-up is answered "No"):
```json
{"id":"fallback","when":{"q":"mailer","is":[1]}, ...}
```
An extra option that appears when another option is chosen:
```json
{"t":"Lock uploads for 30 days","when":{"q":"target","is":[0]}, ...}
```
A question triggered by a typed custom answer:
```json
{"id":"legal","when":{"q":"keep","custom":true}, ...}
```

## What the user sees

- Numbers follow the structure: top level `1.0`, `2.0`; follow-ups `1.1`, `1.2`; deeper `1.1.1`. They recompute as branches appear and disappear.
- Follow-ups are indented one step per level (up to 3 levels).
- A dashed line with a dot connects the chosen option to the follow-up it opened. It disappears when the answer changes.
- Revealed options carry a "New option" tag; follow-up questions a "Follow-up" tag.
- Progress counts only visible questions.

## Rules of good branching

1. **Branch only on real consequences.** A follow-up exists because the earlier answer makes a new decision necessary, as in "you chose cron, so how will failures reach you?".
2. **Place each follow-up directly after its parent** (and after the parent's other follow-ups) in `qs`. Otherwise the connector line crosses unrelated questions. The checker warns.
3. **Depth ≤ 3.** Deeper chains are hard to follow; merge or restructure.
4. **Every branch has a way out.** Every visible question needs at least one option, and the custom answer is always available.
5. **No loops and no forward references.** The checker rejects them.
6. **Do not hide the important questions behind answers.** Questions every path needs stay unconditional.
7. **Explain the link.** Say in `why` which earlier answer caused the question ("You chose cron, so...").

## What the agent receives

Only visible questions appear in the answer JSON. A question hidden by branching is omitted, so its absence means "not applicable".
