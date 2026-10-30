# Rich content

Rich content can appear in three places: the **context**, the **question** (`vis`), and each **option** (`vis`). Use it wherever it makes a decision clearer. It is never mandatory. A diagram that only restates a sentence should be a sentence.

## Block types

| Block | Use for | Fields |
|---|---|---|
| string | a paragraph (inline: `` `code` ``, `**bold**`, `==highlight==`) | |
| `h` | a sub-heading inside the context | `t` |
| `ascii` | a diagram of flow, structure, time, or relationships | `t` (string or list of lines), `cap` |
| `code` | exact commands or config, highlighted, with a Copy button | `t`, `l` (language), `f` (file name label), `cap` |
| `table` | comparing attributes | `h` (header cells), `r` (rows), `cap` |
| `list` | requirements, criteria, short enumerations | `i`, `cap` |
| `steps` | a procedure with every micro-step | `i`: `[["Title","Detail"], ...]` |
| `chart` | a few numbers to compare | `title`, `max`, `b`: `[["label", value], ...]` |
| `src` | real sources | `i`: `[["Name","https://..."], ...]` |

Code languages with highlighting: `bash`/`sh`, `python`, `javascript`/`js`, `typescript`/`ts`, `json`, `yaml`, `sql`, `ini`, `diff`, `markup`/`html`/`xml`, `css`, `go`, `rust`. Other languages display unhighlighted.

Pick the block by the idea: process or architecture → `ascii`; exact instructions → `code` or `steps`; attributes across options → `table`; magnitude → `chart`; criteria → `list`.

## Rules for ASCII diagrams

A diagram earns its place only when the **layout itself** communicates: order, containment, direction, time, or connection. Words placed inside box shapes are decoration.

1. **One idea per diagram.** Flow, structure, timeline, comparison, or states. Not all at once.
2. **Choose the form that matches the idea.**

| Idea | Form |
|---|---|
| Process or pipeline | vertical or horizontal chain with numbered steps |
| Architecture | boxes for parts, labelled arrows for what flows, nesting for containment |
| Time or failure behaviour | a time axis with events, and what happens after a miss |
| Comparing options | two diagrams with the same axes, one in each option |
| States | boxes with labelled transitions |
| Layers | a stack, top to bottom |
| Choices | a tree with the question at each fork |

3. **Label every arrow** with what moves or what triggers it.
4. **Mark where the decision applies**: `◀── Decision 2: where copies go`.
5. **Show failure and edge paths**, not only the happy path, when the decision depends on them.
6. **State the consequence** in a line under the diagram ("If this disk fails, the invoices are gone.").
7. **Width ≤ 80 columns** (the checker warns above 96). Phones scroll it sideways.
8. **Align precisely.** Use a monospace grid, count columns, keep box edges straight. Use only single-width characters: `─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ▶ ◀ ▲ ▼ ✔ ✘`.
9. **Add a legend** when symbols are not obvious.
10. **Caption** (`cap`): one line saying what to notice.

### Weak

```
[ Start ] -> [ Do work ] -> [ End ]
```
Three words in boxes. Nothing a sentence does not say.

### Strong

```
 ┌───────────┐  writes   ┌─────────────────┐
 │  Web app  │──────────▶│  PostgreSQL 16  │
 └───────────┘           │  18 GB          │
                         └────────┬────────┘
                                  │ stored on
                         ┌────────▼────────┐
                         │  Disk (single)  │ ◀── the only copy
                         │  120 GB free    │
                         └─────────────────┘
 Today: no backups. If this disk fails, the invoices are gone.
```
It shows containment, direction, the single point of failure, and the consequence.

### Strong (time and failure)

```
night 1         night 2 (server off)           boot
02:00 ✔ ran     02:00 ✘ missed ╌╌╌╌╌╌╌╌╌╌╌╌▶  ↻ runs now
```
Put the same two lines in the sibling option with the last symbol changed to `∅ never runs`; the difference is visible at a glance.

## Tables, lists, charts, sources

- **Tables**: same attributes in the same order for every option; put units in the header; `table` rows must have as many cells as the header. Use `**bold**` for the cell that matters.
- **Charts**: horizontal bars, good for 2 to 6 values. Set `max` to a meaningful limit (for example free disk) and put the limit in the title.
- **Sources**: only URLs you actually retrieved. Never invent a link. If a figure is illustrative, say so in `cap`.
- **Code**: show real, runnable commands; set `f` to a file name or purpose; set `l`.

## Where each kind of content goes

- **Context**: current state diagram, environment table, process flow, glossary table, assumptions list.
- **Question**: a comparison table, a requirements list, a process diagram marking this decision, a chart of cost or size.
- **Option**: the scenario diagram for that option, its config or commands, its setup `steps`.
