<!--
  This is a short excerpt illustrating the TONE and SHAPE the FINAL
  DOCUMENT (Phase 4) should have — not a template to fill in, and not a
  complete example (a real run's document would be much longer and would
  emerge from whatever was actually mined). The point is: no headers like
  "Findings," no per-project subsections, no even coverage. Just the
  understanding, written as understanding.

  Per-source checkpoint files (Phase 2) are a different, looser kind of
  writing — the agent's own working notes, not held to this same
  prose-quality bar. See workflow.md → Phase 2 → "Write a checkpoint file"
  for the content floor every one must clear (ground census, why/cost, and a
  closing source ledger), search-and-mining-technique.md → "The ground
  census" for the numbers it opens with, and "The source ledger" for the URLs
  it ends with. There's still no example checkpoint file, on purpose: the floor
  fixes what must be *answerable* from the file, never what it looks like, and
  checkpoints are meant to vary by source rather than converge on one
  demonstrated shape. The thin-vs-grounded opening pair in the census section
  shows that difference without becoming a shape to copy.
-->

Almost every one of these projects arrives at a plugin boundary eventually,
but they get there from opposite directions, and that difference matters
more than the fact that they converge. Zed builds the extension system in
from the start as a WASM sandbox — not because sandboxing was the goal,
but because the team had already committed to a multi-process, GPU-driven
core and wasn't willing to let arbitrary plugin code touch that boundary.
VS Code goes the other way: extensions ran in-process for years, and the
eventual move toward isolation reads less like a plan and more like a slow
accretion of workarounds after enough extensions caused enough freezes that
isolation stopped being optional. Same destination, but one team paid the
cost upfront as an architectural bet and the other paid it later as
technical debt they eventually had to settle.

What's harder to find, and more interesting once you do, is that neither
project's public docs actually say this outright. Zed's docs describe the
WASM boundary as a security feature. It's true, but it undersells the real
reason — the closed issues from the months before the extension API
shipped tell a more honest story about what was actually being protected
against, and it wasn't malicious extensions, it was well-meaning ones
breaking the render loop. VS Code's CONTRIBUTING history has the inverse
problem: the isolation work is well-documented step by step, but nobody
ever writes down *why now* — you have to cross-reference the timing
against a cluster of GitHub issues about extension host hangs to see that
the "why now" was reactive, not planned.

...
