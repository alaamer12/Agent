# Fill the scenes, then verify against the spec

Steps 4 and 5 of the pipeline in full: the authoring order inside each scene file,
and what to do with the snapshots once the composition exists. The commands and the
one-line duties stay in the entry point (`../SKILL.md`); the detail is here.

## 4. Fill the scenes

For each scene file, in order:

1. Read the design spec (`frame.md`) first and quote its tokens verbatim —
   `/hyperframes-creative` owns that contract, and its `house-style.md` plus
   `video-composition.md` are the two files it says to read before writing HTML.
2. Pick the shape from the build sheet: a blueprint for a multi-phase scene, or
   2–4 atomic rules. Load `/hyperframes-animation`; read the entry you chose.
   Before hand-building a named look (film grain, glitch, shimmer sweep, CRT),
   search `/hyperframes-registry` for the primitive.
3. **Fill every arrival slot the scaffold made.** The beat count is a floor, not a
   suggestion — a scene that leaves its slots empty is the failure this skill
   exists to prevent.
4. Re-lint per scene. `npx hyperframes check . --json` after each one beats
   discovering five problems at the end.

## 5. Verify against the spec

The spec is the acceptance criteria, not a mood board.

```bash
npx hyperframes check . --json --at-transitions     # lint, runtime, layout, motion, contrast
npx hyperframes snapshot . --at <times> --no-end -o snapshots/scene-NN
python3 scripts/motion.py snapshots/scene-NN/frame-00-at-<a>.png snapshots/scene-NN/frame-01-at-<b>.png
```

`spec.py` prints the exact times, this skill's own absolute `motion.py` path, and
each scene's promised direction — `scripts/motion.py` belongs to this skill, so
nothing here depends on any other skill being installed. A promise measured as
something else, or as `cannot-determine`, is a bug: fix the tween, never re-label
the promise. If motion cannot be measured for some reason, read the two snapshots
yourself and say you eyeballed it rather than implying it was measured.

Then `npx hyperframes preview .` and watch it at real speed — timing that reads
correctly in a still is often wrong in motion. Confirm the Studio row count too:
one decoration host, one row per scene, one caption row, audio rows. A wall of
unlabelled rows means scene markup leaked into the root.
