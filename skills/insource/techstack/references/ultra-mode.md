# Ultra Mode

Normal mode decides the primary technology and its closest dependencies. Ultra mode does that **and** makes sure the *whole system* is covered: every real need the system has gets a deliberate decision instead of being left to "we'll handle it later" or "we can write that ourselves."

Ultra mode is about **coverage that is proportional to the system**, not about adding tools. A correct ultra-mode answer for a small, simple system can be short. Breadth comes from honestly examining the system; it is never a goal in itself.

## What ultra mode changes

Everything in `process.md` still applies (verify first, requirements before options, existing-project awareness, honest trade-offs, the agent decides). Ultra mode adds:

1. A deeper Step 1: surface how the system behaves, not just what it is (see "Inputs to the inventory").
2. A **concern inventory** (Step 2.5 in `process.md`), described below.
3. Step 0 verification **per chosen tool**, not only for the primary technology.
4. The **DIY rule**.
5. A richer output shape.

## The concern inventory

A *concern* is anything the system must handle beyond its core business logic: something that, if unhandled, becomes a failure, a risk, or a recurring cost. Do not recite a fixed list of concerns. Derive them from this system.

### Inputs to the inventory

Use the requirements and feature list from Step 1, plus the existing footprint from Step 2. Walk the system through these lenses, phrasing each finding in the system's own vocabulary:

- **What comes in:** sources, shapes, and how much of it can be trusted.
- **What happens to it:** transformation, storage, state, ordering, time.
- **What goes out:** consumers, formats, guarantees the system promises.
- **What can fail:** dependencies, networks, partial failure, overload, bad data, and what the system must do when each happens.
- **What changes over time:** schema, config, load, data volume, team, requirements.
- **Who and what is trusted:** identity, permissions, secrets, hostile input.
- **How it is run:** build, ship, observe, debug, operate, and who does that.

These are lenses, not a checklist. A lens that produces nothing for this system produces nothing. If a lens cannot be answered from the available context and the answer would change a verdict (for instance, what must happen when a dependency fails, or how much load to expect), ask the user rather than guess; the inventory is only as good as the understanding behind it. Questioning depth follows `question-method.md`.

### The trace rule

Every concern in the inventory must carry a trace:

> Because **[specific requirement / feature / constraint / scale fact]**, this system needs **[concern]**.

No trace, no concern. If a concern cannot be tied to something the system actually does or faces, drop it. This is the main guard against over-engineering.

### Verdicts

Each concern ends in exactly one verdict:

- **Needed:** pick a specific tool and justify it (see "Depth").
- **Needed, platform covers it:** name the native platform or runtime feature as the chosen tool. This is a real choice and goes in the stack explicitly.
- **Deferred:** the need is real but the system has not reached the point where it pays off. State the concrete trigger that would make it worth adopting (a traffic level, a team size, a new feature). The reason must be about *this system's scale or stage*, never "we can build it ourselves."
- **Not needed here:** state why, in one line, tied to the system.

Verdicts other than Needed are first-class answers, not failures.

### Depth

For every Needed concern, naming a tool is not enough. Give the detail that makes the choice actionable for this system:

- the semantics that matter here (what exactly it applies to, what it must not apply to, and the failure behavior it implies),
- the settings or policy that follow from the requirements, with the reasoning,
- where it plugs into the chosen core and anything it must be compatible with,
- the cost it adds (dependency weight, learning curve, operational burden) and the trade-off accepted.

If the depth cannot be filled in from the requirements, that is a signal the concern is not understood yet: either ask, or change the verdict.

### Fit between tools

Check the picks against each other, not just against the core. Avoid overlapping tools that solve the same concern twice, and confirm the picks work with the chosen core and with each other. A concern covered by something already chosen is a verdict ("covered by X"), not a new tool.

### Consolidation pass

After every concern has a verdict, group the needed concerns and apply `tiers-and-discovery.md` (Part 3). For each group, evaluate a single higher-tier tool (meta-library) against separate specialists, in both directions, and decide per group: fully consolidated, fully separate, or a hybrid. A consolidated tool counts only for the concerns it covers at adequate depth for this system; nominal support is not coverage, and capabilities it brings that the system will not use are carried weight, not credit. The topic searches that build the candidate list must include the higher-tier angle, so consolidated options are actually found.

### Proportionality check

Before presenting, compare the inventory's size to the system's size and stakes. If it reads like a generic production checklist rather than a description of this system, the inventory has inflated: cut every entry whose trace is thin.

## The DIY rule

In ultra mode, **"we can do it ourselves" is not an accepted reason** to leave a real need unassigned or unevaluated. This covers phrasings like "it's simple enough to write," "not worth a dependency for one function," or "just implement it inline." For every real need, evaluate the best available tool and decide on the merits: fit, maintenance, quality, cost against this system's need.

What this does **not** mean:

- It does not force a tool onto a need the system doesn't have. Not-needed and Deferred verdicts remain valid.
- It does not override a constraint the *user* states about this project (for example a hard rule about dependencies, licensing, or package or binary size). That is a requirement from Step 1 and still binds.
- It does not mean ignoring cost. Adoption cost is weighed against *this system's* need, as with any dimension. Only the generic argument that building it yourself is possible is removed.

## Output shape

Use the ultra variant in `assets/templates/recommendation-template.md`. Lead with the core recommendation, then the concern table with each row's trace, choice, detail, and trade-off, then the packaging decision for each group (consolidated, separate, or hybrid, and why), then the Deferred and Not-needed lists, then the usual trade-offs and "if priorities shift" sections. Worked illustrations are in `examples/ultra-examples.md`.
