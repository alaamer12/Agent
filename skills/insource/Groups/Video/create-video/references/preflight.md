# Preflight — HyperFrames must be installed (hard gate)

The gate is stated in the entry point; this file is the procedure it runs, in order.

**Nothing in this skill runs before this check passes — not the axis lock, not
`spec.py`, not the scaffold.** This skill is the direction layer of a pipeline
whose execution and craft layers (routing, animation, keyframes, audio, CLI,
lint, render) are HyperFrames skills; with those absent, every step downstream
of this skill would dead-end, so proceeding would fake progress, not make it.

1. **Check, don't assume:** verify the HyperFrames skills are actually present
   in this environment — inspect the available-skills listing and the skill
   directories (`skills add` installs into the agent's skills folder; the
   entry skill is `hyperframes`, domain skills like `hyperframes-animation`,
   `hyperframes-core`, `hyperframes-cli` alongside it). Never conclude from
   "video skills usually exist."
2. **Missing → stop with the exact fix, then offer to run it:**
   ```bash
   npx skills add https://github.com/heygen-com/hyperframes --skill hyperframes-animation
   # or: bunx skills add https://github.com/heygen-com/hyperframes --skill hyperframes-animation
   ```
   That command installs from the HyperFrames repo; installing the full set
   (the `hyperframes` entry plus the domain skills this pipeline names) is
   what makes the pipeline complete — ask the user before installing on
   their behalf, since it writes outside the project.
3. **Present → continue:** re-verify the skills are visible, then proceed to
   step 0 (the entry skill must own routing/BRIEF.md per the conflict
   protocol). If the user declines to install, say plainly that this skill
   cannot responsibly run and stop — do not degrade to a hand-rolled
   substitute pipeline.
