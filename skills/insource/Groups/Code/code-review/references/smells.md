# The smell baseline — 12 portable judgement calls

Applies to the Standards axis *underneath* whatever the repo documents.
Two binding rules:

1. **The repo overrides.** A documented repo standard always wins;
   where it endorses something the baseline would flag, suppress the
   smell.
2. **Always a judgement call.** Each smell is a labelled heuristic
   ("possible Shotgun Surgery"), never a hard violation. And skip
   anything tooling already enforces — that's lint's job, not the
   review's.

From Fowler, *Refactoring* ch. 3, trimmed to the twelve that read
straight off a diff. Each is *what it is* → *how to fix*:

- **Mysterious Name** — a name that doesn't reveal what it does or
  holds. → rename; if no honest name comes, the design is murky.
- **Duplicated Code** — the same logic shape in more than one hunk or
  file. → extract the shared shape, call it from both.
- **Feature Envy** — a method reaching into another object's data more
  than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields/params travelling together
  (a type wanting to be born). → bundle into one type, pass that.
- **Primitive Obsession** — a primitive/string standing in for a domain
  concept deserving its own type. → give the concept a small type.
- **Repeated Switches** — the same switch/if-cascade on the same type
  recurring across the change. → polymorphism, or one shared map.
- **Shotgun Surgery** — one logical change forcing scattered edits
  across many files. → gather what changes together into one module.
- **Divergent Change** — one file edited for several unrelated reasons.
  → split so each module changes for one reason.
- **Speculative Generality** — abstraction/params/hooks for needs the
  spec doesn't have. → delete; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller
  shouldn't depend on. → hide the walk behind one method on the first
  object.
- **Middle Man** — a class/function that mostly just delegates. → cut
  it, call the real target directly.
- **Refused Bequest** — a subclass ignoring or overriding most of what
  it inherits. → drop the inheritance, use composition.

Matching rule: read the diff hunk by hunk; a smell earns a line only
when the hunk *shows* it — never a whole-file vibe report. Report as
`**Consider:** possible <smell> — <evidence> → <named remedy>` so the
judgement-call status is visible in the label itself.
