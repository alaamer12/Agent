# Example — Requirement Substitution: A Language-Agnostic Requirement, Built Single-Language

**Proves:** the requirement-substitution reflex in `../../../../principles.md` — a stated "any language" requirement for workers got overridden by an unstated single-language convention.

**Redaction note:** project name, domain, and field names are genericized. The stated requirement and the substitution error are preserved exactly.

---

## The situation

The user stated a specific requirement for the worker fleet: workers should be addable in any language — the fleet should be language-agnostic by design, not committed to one runtime.

## What got built (first draft)

```text
workers/
├── provider-a/src/index.ts
├── provider-b/src/index.ts
└── provider-c/src/index.ts     ← wraps a Python-only tool in a subprocess call,
                                    just to keep the file a .ts file
```

Every worker lives under one language, including the one whose actual dependency isn't JS at all — it gets forced into a `.ts` file via a subprocess wrapper purely so the fleet stays visually uniform.

## Why this is wrong, precisely

This is not "the evidence didn't specify a language, so JS got defaulted to" — that framing would make it a professional-shape reflex, fixable by going and finding the missing evidence. But the evidence wasn't missing. The user said, directly, that any language should be addable. The draft built the opposite: one language, with a workaround bolted on for the one dependency that didn't fit. The requirement was overridden by "worker fleets are normally one language for consistency" — a convention nobody asked for, applied in place of an explicit instruction to not do that.

The subprocess wrapper is the tell. It's extra code that exists solely to make a non-JS dependency *look* like a JS worker — effort spent defending the wrong answer rather than building the one that was actually requested.

## What should have been built

```text
workers/
├── js/
│   ├── provider-a/src/index.ts
│   └── provider-b/src/index.ts
└── python/
    └── provider-c/
        ├── pyproject.toml
        └── worker.py            ← a real Python project, not a wrapper pretending
                                     to be TypeScript
```

Split by language at the top of the fleet, each worker native to whatever language actually fits its dependency, with a shared contract (wire format, not source language) as the thing that keeps them interoperable. This is what "any language" actually meant when it was stated — not "we'll guess if a second language becomes necessary," but "the structure itself should not assume one language in the first place."

## What this proves

Same root cause as the Railway/Dockerfile case, different surface: a clear, stated requirement lost to a more familiar convention. The fix wasn't "notice that one dependency happens to prefer Python" framed as evidence-gathering — the requirement was never actually in question. The fix was simpler and more upstream: take the user's stated words as the answer the first time, instead of building the conventional shape and only correcting toward the stated requirement after it was pointed out.
