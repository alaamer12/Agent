# Examples

These describe transformations by their **structure and reasoning**, not by handing over one fixed markup/code shape to copy. No example here is tied to a specific framework, templating language, or component library — any concrete syntax shown is explicitly marked as one illustrative instance among many (`[e.g. ...]`), never *the* answer.

Applying a move from `SKILL.md` means reasoning from the structural description below and expressing it in whatever the input's own language, framework, and styling system already is — plain HTML, a native mobile UI toolkit, a terminal UI, a design tool's component model, or anything else. If a person or agent reading these files comes away thinking "so I should write a `<div class="yield__bar">` with three `<i>` children," that's the wrong takeaway — the right takeaway is "so I should replace a concatenated stat string with a proportional visual plus a compact legend, built however this codebase already builds small visual elements."

- `stat-encoding.md` — move 5: text stats → visual encoding
- `inline-warning.md` — move 6: inline warning → full-width/full-card callout
- `pill-vs-text.md` — move 3: scanned-across vs. confirmed-within values
- `dwell-time-palette.md` — move 8: regional color weighted by attention
- `chart-ink.md` — move 11: chart-junk removal
- `one-job-per-row.md` — move 2: a unit doing one job vs. many
- `rerun-detection.md` — recognizing input that's already been through a pass (including Claude's own prior output), and re-approaching it with genuinely different, input-derived directions instead of a smaller patch job

The six files above each isolate a single move. The three below instead assemble several moves together, at full-pass granularity, to show what a complete pass at each mode actually looks like — read these when the question is "what does a whole Lite/Medium/Ultra result look like," not just "what does this one move do":

- `mode-lite-fullpass.md` — a complete Lite pass, and how to tell if it silently drifted toward Medium
- `mode-medium-fullpass.md` — a complete Medium pass, and the two directions it can drift wrong (under- and over-delivering)
- `mode-ultra-fullpass.md` — a complete Ultra pass, including how to actually reason through the light/dark and page-count judgment calls instead of defaulting past them

For the `/accessible taste` command's side-by-side picker shell, see `../assets/taste-picker-template.html` — a generic template regenerated per run, not a fixed design.
