## Command/mode skills declare `argument-hint`

A skill that presents **commands or modes** to the user must declare `argument-hint:` in its frontmatter. The hint is the one place the agent UI learns what may follow `/skill-name` — a skill that routes on `lite|medium|ultra` but shows no hint leaves the user guessing the vocabulary exists.

```yaml
---
name: denoise
version: 1.0.1
author: Amr
specialized: none
argument-hint: "[lite|medium|ultra] <target>"
description: ...
---
```

Value rules: double-quote whenever the hint starts with `[` or contains `: ` (both break plain YAML); list alternatives with `|`, placeholders with `<...>`, optional parts with `[...]`; keep it one line. Bump the skill's `version` when you add or change a hint.

### What "really has commands or modes" means

`manager.py lint` decides from **structural evidence in the SKILL.md body**, never from loose vocabulary. Prose that merely mentions the words — "dark mode", "run these shell commands", "maintenance", a doc-outline heading like "7. Commands, examples, and verification honesty" — is invisible to the detector.

**Strong signals (any one fires the rule):**

- An interface heading naming the surface: `## Commands`, `## Modes`, `## The two modes`, `## Operating Modes`, `## READ mode - ...`. Headings are excluded when they read as prose (more than 7 words, numbered doc-outline items of 5+ words, or containing connectives like `than`, `via`, `needs`, `step`, `why`).
- The skill's **own** slash address used with an argument: `` `/mistakes <id>` ``, `` `/animation life micro <target>` ``. Mentions of *other* skills' commands (`/dtb`, `/tmp`) never count — that was the largest false-positive class in the inventory.
- At least two distinct `Mode A`/`Mode B` letters present.

**Weak signals (two are needed together):**

- Enumeration phrases: "three commands - micro, component, transition", "both modes", "several subcommands".
- Bold/plain `Commands:` or `Modes:` line labels.

**What does NOT count** (verified against real inventory hits):

- Commands of the *target project*, not the skill: a ripgrep cheatsheet heading in `update/references`, git vocabulary, or "shell commands in CI" prose — the rule polices the skill's own interface.
- A bundled script's CLI inside `references/` (`scripts/catalog.py list/search`) is the skill's tooling; it becomes an argument surface only when `when_to_use` exposes it to the user — which is why `fahlwy` declares its hint.
- `method.md` module files inside a battery: modules are never invoked on their own, so the battery's router-side `argument-hint` covers the whole tree — the detector reads `SKILL.md` bodies on purpose.
- Template and pattern headings — "Sweep mode" in a `assets/` mockup template, "Failure Modes Table" in a study template, "Dark mode" in a style-knowledge file — content, not interface.

### When a skill has commands/modes in substance but not by these shapes

Add the `argument-hint` anyway — the rule exists for the user's benefit, and the detector is a floor, not a ceiling. When the detection is genuinely wrong (the words describe the target project's commands, not the skill's own interface), waive it on the skill rather than mutating the skill or weakening the detector:

```yaml
lint-accept:
  argument-hint: "Explains README command sections; the skill itself takes no commands."
```

Acceptance mechanics: [lint-accept.md](lint-accept.md).

```bash
python manager.py lint --strict            # argument-hint findings fail the run
python manager.py lint --strict --verbose  # evidence shown per skill
```
