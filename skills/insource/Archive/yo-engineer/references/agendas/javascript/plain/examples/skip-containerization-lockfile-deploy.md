# Example — Requirement Substitution: Docker Answering a Question Railway Didn't Ask

**Proves:** the requirement-substitution reflex in `../../../../principles.md` — a stated deploy target got silently translated into a different, more familiar requirement instead of being looked up directly.

**Redaction note:** project name, domain, and field names are genericized. The stated requirement and the substitution error are preserved exactly.

---

## The situation

The user stated a specific, unambiguous deployment requirement: the project deploys to Railway. Nothing else about deployment was asked for or implied.

## What got built

```text
project/
├── Dockerfile
├── docker-compose.yml
└── apps/orchestrator/...
```

## Why this is wrong, precisely

This is not a case of "no evidence existed, so a convention filled the gap" — that would be the professional-shape reflex, and the fix for that is going and checking the project's evidence. Here, evidence already existed: the user said Railway. The error is that "deploys to Railway" got quietly answered with "needs a Dockerfile" — a nearby, familiar-sounding requirement standing in for the one that was actually stated. Railway builds directly from a project's manifest/lockfile by default; it does not require a Dockerfile at all. Nothing about "Railway" implies "containerize this" — that inference was supplied, not derived.

This is worth being exact about, because the point is not "Docker is the wrong tool" in general. Docker remains legitimate for a different, real purpose — mimicking a production-like environment during local testing. That purpose was never stated as a requirement either. So the failure isn't "chose Docker instead of not-Docker" — it's **answering a requirement that was never asked ("give us container isolation") in place of the one that was ("deploy this to Railway"), and never even checking what Railway itself specifically wants.**

## What should have been built

```text
project/
├── railway.json          ← or railway.toml — Railway's own deploy configuration,
│                             only if the project's build/start needs actually require
│                             anything beyond what Railway infers automatically
└── apps/orchestrator/...
```

The correct move was to go find out what Railway specifically requires or supports — not to reach for the generic, familiar answer to "how do serious projects get deployed." In many cases that's nothing beyond the manifest Railway already reads; in some cases it's a small Railway-specific config file. Either way, the artifact that exists (if any) should trace to Railway's own deployment model, not to a general-purpose containerization convention that was never requested.

## What this proves

The lesson generalizes past Docker specifically: **a stated requirement is not evidence to weigh against convention — it's the answer.** The failure here wasn't a missing fact that a reasonable default filled in. It was a present, explicit fact (Railway) that got overridden by a more familiar-sounding but unrequested one (Docker) anyway. The fix isn't "evaluate whether containerization is worth its cost here" — it's "go look up what the thing the user actually named requires, instead of substituting the nearest convention for it."
