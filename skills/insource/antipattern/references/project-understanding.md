# Understanding the project

## Contents
- What to learn
- Where to look
- Following execution paths
- Scaling the investigation
- Project profile output

## What to learn

- Purpose and business domain: who uses it and what it is for.
- Languages, frameworks, runtime, and dependencies (with versions that matter).
- Application structure and architectural layers.
- Modules, components, services and what each is responsible for.
- Data models, types, schemas and contracts (API specs, protobuf, DB migrations).
- Business rules and workflows, including where each rule is enforced.
- External integrations, APIs, databases, queues, infrastructure.
- Existing conventions and recorded decisions (ADRs, style guides, lint config).

## Where to look

| Question | Sources |
|---|---|
| Purpose, domain | README, docs/, product copy, CLI help, API descriptions |
| Stack and dependencies | manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `*.csproj`, `Gemfile`, `composer.json`), lockfiles |
| Structure and layers | entry points, DI/wiring code, routers, module index files, import graph |
| Contracts | OpenAPI / GraphQL / proto files, DB migrations, shared type packages |
| Business rules | domain/service code, validators, SQL, tests named after behavior, docs |
| Integrations and infra | client modules, env/config files, Dockerfile, compose, IaC, CI workflows |
| Conventions | AGENTS.md, CLAUDE.md, CONTRIBUTING.md, ADRs, linter/formatter/type-checker config |

## Following execution paths

Directory structure is a hint, not evidence. Verify it:

1. Pick two or three important use cases (the main revenue or data path, one write path, one failure path).
2. Trace each from its entry point (route, handler, CLI command, job) through validation, orchestration, domain logic, persistence, and outbound calls.
3. Note where layers are crossed, where rules are applied, and where errors go.
4. Confirm layer boundaries with the real imports, not folder names ("services/" may contain controllers; "domain/" may import the ORM).

## Scaling the investigation

| Project size | Depth |
|---|---|
| Small (a few files to ~50) | Read most files. |
| Medium (hundreds of files) | Read manifests, docs, entry points, and the traced paths. Sample modules by size and churn. |
| Large or monorepo | Pick the in-scope package or service. Map the rest at the dependency level only. Say so in the methodology. |

In Mode A, learn only what the requested patterns touch. In Mode C, cover all eight areas above at least at summary level.

Recent history helps for sizing and intent: `git log --stat` on hot files, `git blame` to see whether a suspicious block is hand-written, old, or recently generated. Use it read-only.

## Project profile output

Keep working notes (not a repo file) of at most one page: purpose, stack, layers with their real dependency direction, key modules, contracts, rules and where they live, integrations, conventions found, and open questions. This feeds section A of the report and anchors every later finding.
