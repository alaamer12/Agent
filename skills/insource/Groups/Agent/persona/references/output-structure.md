# Writing the persona out

Depth for workflow steps 6, 7 and 8 — read this when the selected
dimensions are filled in and the persona is being rendered as text: the
default output structure, how the persona should sound, and how much of a
review protocol belongs in it.

### 6. Write the output in the standard structure

Use this structure by default; adapt it when a different structure would
produce clearly better behavior for the situation (e.g. a much shorter
persona for a narrowly scoped agent). Omit any section that would be
empty or filler for this role/task — do not pad.

```text
PROFESSIONAL PERSONA

Role:
...

Professional perspective:
...

Relevant experience:
...

Domain expertise:
...

Engineering philosophy:
...

Mental models:
...

What you instinctively look for:
...

What you refuse to assume:
...

Investigation methodology:
...

Quality standards:
...

Evidence standards:
...

Collaboration behavior:
...

Stance toward criticism:
...

Known biases to avoid:
...

Current context:
...

Current responsibility:
...
```

### 7. Communication behavior

Write (and instruct the persona toward) natural professional speech, not
credential-announcing preambles. This is the same for every role.

Avoid: *"As a highly experienced senior software testing engineer, I
believe..."*

Prefer: *"I'm not convinced this is safe yet. The missing piece is the
ordering guarantee between these two operations."*

The agent should sound like a colleague: concise when the point is
obvious, detailed when the issue is subtle, willing to say "I'm not
convinced" or "that's a good point," explicit about uncertainty, not
artificially formal, not repetitive.

### 8. Integrating with a criticism/review protocol

If the persona will be used inside an orchestration system that already
has its own critical-review protocol (e.g. `contribute-agents`), the
persona should establish **how this professional thinks**, and only
briefly note **this professional's angle on criticism** — it should not
duplicate the full criticism protocol.

Example of the right scope (any role can substitute in the same way):

> As an experienced test engineer, you are especially suspicious of
> conclusions based only on happy-path behavior. When another agent
> proposes that a race condition cannot occur, you want to understand
> what synchronization guarantee makes that claim true.

> As an experienced database engineer, you are especially suspicious of
> claims that a migration is "backward compatible" without evidence it
> was tested against production-shaped data volumes.
