# Subject Types and Inspection Procedures

Treat every side with equal evidentiary care. Never invent content that is not present.

## Named concepts, technologies, products, processes, strategies

- Research each side independently (primary sources + independent analysis, practitioner discussion, critical commentary).
- Prefer current information for fast-moving domains; rely on domain knowledge for settled ones.
- Pull distinguishing traits for each side before narrowing.

## Files (any kind)

- Read both files (or the relevant portions).
- Identify concrete differences and similarities: structure, content, style, correctness, completeness, edge cases, documentation.
- If the user names focus areas, stay inside them; otherwise surface the highest-signal differences.
- For binary or non-text files, describe observable differences (size, format, metadata) and ask for more context if needed.
- Never invent content that is not in the files.

## Code modules or packages inside a codebase

- Inspect the actual source, tests, exports, and call sites.
- High-signal dimensions (derive or use user-specified): responsibility boundaries, coupling, cohesion, public API surface, test coverage, error handling, performance characteristics, documentation, dependencies.
- Prefer concrete evidence (call graphs, import counts, test assertions, specific behaviors) over abstract labels.
- Surface strengths of each module and where one is weaker relative to the other.

## Entire projects or repositories

- Inspect structure, key entry points, configuration, tests, documentation, dependency graphs, and any available metrics (build size, test results, CI status).
- Research external context only when relevant (adoption, issue activity) and grade those claims.
- Identify real strengths and weaknesses of each project relative to the other on the same axes.
- If large, prioritize dimensions that matter for the user's stated goal (maintainability, onboarding, performance, security surface, etc.).

## Books, papers, or long documents (often PDFs)

- Prefer the actual files when provided. Use the pdf skill or equivalent to extract text/structure.
- If files are missing, ask the user to supply the PDFs or the specific chapters/sections needed. Do not invent book content.
- Compare on user-specified dimensions or on high-signal ones derived from the texts (thesis, evidence quality, methodology, scope, audience, conclusions, writing clarity).
- Quote or paraphrase sparingly and accurately; never reconstruct substantial copyrighted text.

## Arbitrary or mixed subjects

- Apply the same principles: inspect or research each side on equal footing, list candidate differences, filter with the differentiator test, explain why each difference matters, conclude by context.
- If one side is local and the other external, still treat both with independent evidence.
