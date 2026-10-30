# Comparison and Remixing

Use this reference when the user asks to compare Skills or create a new Skill from existing Skills.

## Comparison

Investigate each candidate independently before comparing them.

Compare:

1. Purpose and scope
2. Activation description
3. Core workflow
4. Decision logic
5. Progressive disclosure
6. References/scripts/assets
7. Tool dependencies
8. Degree of freedom vs constraints
9. Validation and error handling
10. Safety and side effects
11. Maintainability
12. Fit for the requested task

Do not equate length with quality.

## Remixing

Treat source Skills as design material.

Build a capability matrix:

    source skill -> capability -> keep/change/reject -> reason

Then design the new Skill around the target outcome.

Resolve:
- conflicting assumptions
- duplicate instructions
- incompatible tool requirements
- different output conventions
- unnecessary scope

Prefer a clean new workflow over concatenation.

## Copyright and licensing

Check the source repository's license before copying substantial text or code.

Distinguish:
- learning from a technique
- reusing an idea
- copying instructions/prompts
- copying code
- creating a derivative package

If the user intends to publish the remix and licensing is unclear, flag the issue.

## New Skill structure

Prefer:

    skill-name/
    ├── SKILL.md
    ├── references/
    │   └── detailed-guidance.md
    ├── scripts/
    │   └── helper.py
    └── assets/
        └── template.md

Put only routinely needed workflow instructions in `SKILL.md`.
