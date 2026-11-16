# Conflict protocol

The four rules that order this skill against the HyperFrames skills named in the
entry point's ownership table (`../SKILL.md`).

When this skill and a HyperFrames skill could both answer, the HyperFrames skill
answers. Four rules make that mechanical rather than a judgement call per turn:

1. **`/hyperframes` is the entry point and owns routing, the intent interview,
   `BRIEF.md`, the review loop, and the production loop.** This skill never runs a
   competing interview, never re-asks what `BRIEF.md` records, and never claims a
   route. It reads the route and continues from it.
2. **No craft is restated here.** Motion, design, audio, media, layout and CLI
   knowledge live in the owners named in that table. If this skill needs one of those, it loads
   the owner. A paragraph here that duplicates an owner is a defect.
3. **Its own claims are the ones nobody made:** the six-axis numeric lock, the
   arrival budget, the scaffolded project shape, the measurable quality bar, the
   delivery matrix, and framework choice.
4. **On a direct contradiction, HyperFrames wins and this skill says so** — and
   reports the conflict, because two skills asserting the same ground is a bug to
   fix in one of them, not a coin flip at runtime.
