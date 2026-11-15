# Review report template

Fill every `<slot>`; delete lines that genuinely don't apply rather
than leaving placeholders. The two axis headings stay even when one
side is empty or skipped.

```markdown
# Review: <change/PR title>

- Fixed point: `<fp>` (merge-base `<sha>`) — `<n>` commits, `<m>` files, `<x>` lines changed
- Spec source: <issue # | path | "no spec available">
- Standards sources: <files | "documented standards: none — baseline only">

## Standards

<findings, severity-labelled, quote + name + remedy each; or: "No
documented-standard violations; baseline: N judgement calls, listed.">

## Spec & Quality

### Spec
(a) missing/partial: <list with spec lines quoted>
(b) scope creep: <list>
(c) implemented-but-wrong: <list>
<or: "Spec axis skipped — no spec available.">

### Five axes
- Correctness: <findings>
- Readability: <findings>
- Architecture: <findings>
- Security: <findings>
- Performance: <findings>

## Summary

- Standards: <n> findings — worst: <one line or "none">
- Spec & Quality: <n> findings — worst: <one line or "none">
(No cross-axis winner — that reranking is what the separation prevents.)

## Verdict

- **<Approve | Request changes>** — <one-sentence reason>

## Verification story

- [ ] Tests pass · [ ] Build succeeds · [ ] Manual/UI/perf evidence: <link/note>
- [ ] Criticals resolved · [ ] Required resolved or deferred-with-bug
```
