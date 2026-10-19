# Designing a question

## Anatomy

Each question carries what the user needs to answer without wondering why it was asked.

| Field | Purpose |
|---|---|
| `q` | The actual question, one decision, phrased neutrally. |
| `about` | What is being decided and in which situations it matters. |
| `why` | Why you are asking: what changes depending on the answer. Shown in a highlighted box. |
| `terms` | Plain explanations of concepts that may be unclear. |
| `vis` | A table, diagram, list, code, or chart that helps compare or understand. |
| `opts` | The options, best first. |
| `hi` | `true` only for a question that shapes the whole design. Use on at most 2 questions. |

## Options

- **Order by your preference.** First is the one you would choose, second is your next, and so on. The page labels the first "Recommended" and shows "My choice 2 of 3". Base the order on knowledge and experience, not on effort. If you truly have no preference, say so in `about`.
- **Count**: 2 to 5 options. Do not pad. Two honest options beat four weak ones.
- **Titles** are short names. **Descriptions** say what the option is and how it works, so the user needs no outside knowledge.
- **No "Other" option.** The page always adds "Write your own answer" at the end. For multiple choice it combines with the selected options; for single choice it replaces them.
- **Make hidden consequences visible.** Use `**bold**` or `==highlight==` for the detail a user may overlook (costs that appear later, things that cannot be undone, limits).
- **Do not duplicate** the same sentence across options; put what is shared in `about`.

## Single vs multiple choice

- `single`: the options are mutually exclusive (one scheduler, one database).
- `multi`: the options are independent and can add up (storage targets, notification channels, features to include).

## Choosing the trade-off shape

Pros and cons are not always right. Pick the shape that matches the question, using `facets` (`h` heading, `tone`, `i` items). Pros/cons stay available as the shorthand `pros` and `cons`.

| Question type | Shape |
|---|---|
| Option judged on its own | `pros` + `cons` |
| Choosing one thing over a named alternative (Next.js vs Nuxt, rclone vs a provider CLI) | `Advantages over Nuxt` (good) + `Disadvantages versus Nuxt` (bad). The other option gets the mirror pair. |
| Fit questions | `Choose it when` (info) + `Avoid it when` (bad) |
| Effort and outcome | `You gain` (good) + `You give up` (bad) |
| Requirements | `Requires` (neutral) + `What happens next` (info) |
| Risk | `Risk` (bad) + `How to reduce it` (info) |

You can mix more than two facets in one option. Keep each list to 2 to 5 items. Use the same headings, in the same order, on every option of a question so they line up.

## Supporting content inside an option

Add `vis` to an option when it shows a difference words cannot:

- a diagram that runs the same scenario through each option (identical axes, so differences are visible);
- the exact config or command, with its language, for syntax highlighting and a copy button;
- a numbered `steps` block with the real setup procedure;
- a small table of numbers.

## Wording

- One decision per question. No "and".
- Neutral: do not argue for your recommendation in the question text. The ordering and the option content carry it.
- Do not explain the interface ("click an option"). The page does that.
- Use the user's terms from the conversation.
