# Evaluation method

Options and examples in this file are illustrative, not exhaustive or mandatory. A hybrid or unlisted answer is always acceptable. The method applies to any kind of candidate: software in any language or platform, databases, infrastructure, tools, services, products, strategies.

Work through these in order. Each one becomes a dimension, a bullet, a table row or a note on the page, depending on what the data supports.

1. **What options exist.** Confirm the candidate list. For each one check health: still developed, stable, still used, last commit, archived, deprecated, stable version reached. An unstable candidate is not automatically bad, but say whether the user can depend on it.
2. **How much the user will depend on it.** Fully, or for a few simple things? For partial use, still read the issue tracker and decide whether the problems are edge cases or everyday problems.
3. **Dimensions to compare.** Choose the dimensions that make sense for this kind of thing and this goal. Prefer general, known dimensions that have benchmarks or other measurable evidence. Use as many as are useful (2, 3, 5, 10). Examples, by domain: [programming languages] runtime speed, memory use, concurrency model, tooling; [databases] read and write throughput, consistency guarantees, operational effort; [CLI tools] startup time, scripting ergonomics, portability; [cloud services] price at the user's scale, limits, regions, lock-in; [consumer products] price, durability, support, fit for the use.
4. **Ecosystem.** A dimension only when it matters, which is mostly for frameworks, languages and platforms. A powerful library with an inactive ecosystem can cause future problems. Plain libraries often have no meaningful ecosystem, so skip it.
5. **Room for the future.** A yes or no question. Can this realistically cover a likely future need (for example a mobile technology that could later support the web)? If a path exists the answer is yes. No third answer.
6. **How it works.** The approach or architecture, for example [a bytecode VM] vs [ahead-of-time compiled binaries], [a single-writer store] vs [multi-node replication], [native bridge] vs [own rendering engine] vs [WebView]. The approach shapes the strengths and weaknesses, so explain it.
7. **Developer or user experience.** One dimension that holds several things (for non-software candidates, the equivalent is ease of use and setup):
   - writing model: how code is written, structured, and how it shapes the way you think
   - build speed, and how it behaves as the project grows
   - error clarity: does an error say exactly where the problem is, or is it vague
   - learning curve
8. **Final decision.** Not "which can technically do the job" but "which best reaches the user's goal". Give picks per use case.

Adapt freely. Non-software candidates (products, services, strategies) need different dimensions, so choose by what matters to the buyer or user.
