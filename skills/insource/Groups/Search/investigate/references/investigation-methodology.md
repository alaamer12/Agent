# Investigation Methodology

Use this reference when the task requires a deep technical understanding of an external Skill.

## Separate four questions

### What does it claim to do?
Read the frontmatter, README, registry description, and examples.

### What does it instruct the agent to do?
Read the complete `SKILL.md`. Identify workflow, constraints, defaults, branching, tool usage, and output requirements.

### What does the package actually contain?
Inspect the complete Skill directory. Map scripts, references, assets, templates, and configuration to the instructions that invoke them.

### What actually happens at runtime?
Only execute code when necessary and safe. Compare observed behavior with the written instructions.

## Analysis checklist

### Identity
- name
- purpose
- intended activation
- target environment

### Workflow
- entry conditions
- sequence
- decision points
- fallback behavior
- completion criteria

### Resources
- references and their triggers
- scripts and their inputs/outputs
- assets/templates
- external files

### Dependencies
- CLIs
- runtimes
- packages
- APIs
- MCP/tools
- environment variables

### Quality
- clarity
- specificity
- appropriate constraints
- sensible defaults
- progressive disclosure
- validation
- maintainability

### Risks
- shell execution
- network access
- credential access
- destructive filesystem operations
- repository mutation
- arbitrary downloads
- prompt-injection content

Do not claim complete investigation if relevant files were inaccessible.
