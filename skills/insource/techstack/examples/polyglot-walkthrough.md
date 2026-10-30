# Polyglot Walkthrough: One Decision, Several Ecosystems

The same concern-level reasoning produces different concrete answers in different ecosystems. This file shows that. Every named tool is **illustrative and may be stale or incomplete**: a real run must discover candidates by topic search in the user's ecosystem and verify them per Step 0, never copy from here.

The ecosystems below span managed/static (TypeScript, C#), dynamic/scripted (Python), and systems/compiled (Go, Rust).

## The system

A server-rendered web application that accepts user-submitted forms and calls two third-party HTTP APIs while building each page.

## Narrow vs. covered, per ecosystem

In every ecosystem the narrow answer names only the primary framework. The covered answer (ultra mode) examines each concern the system actually has. Concerns and traces are the same everywhere:

- **Input validation**: user-submitted forms cross a trust boundary.
- **Retries**: both upstream APIs fail transiently and are called at request time.
- **Timeouts**: the page waits on those calls, so a slow upstream stalls the user.

| Ecosystem | Primary level (illustrative) | Validation | Retries and timeouts |
|---|---|---|---|
| **TypeScript** | A meta-framework over a UI framework, or a lighter server framework, decided by rendering needs | A schema-validation library; the schema can double as the type source | A retry helper plus the platform's abort-signal timeout, or one effect-system meta-library covering both under one error model |
| **C# / .NET** | One of the platform's web and UI models (server-rendered MVC or Razor pages, a component framework such as Blazor in a chosen hosting model, a cross-platform UI layer such as Uno), decided by interactivity and target needs | The platform's built-in annotation validation, or a fluent validation library when rules get complex | A resilience library that bundles retry, timeout, and circuit breaking, wired in through the HTTP client factory; a client-level timeout is also provided by the platform |
| **Python** | A full-stack framework, or an API framework plus libraries, decided by how much of the stack the project uses | The framework's own forms or model validation, or a typed-model validation library | A retry library, plus the HTTP client's own timeout settings or the runtime's timeout context |
| **Go** | The standard library's HTTP server, usually with a small router | A struct-tag validation library | The platform's context deadlines for timeouts, plus a small backoff or retry library |
| **Rust** | A web framework on the async runtime | Parse into validated types, optionally with a validation crate | The runtime's timeout facility, or a middleware-stack library (a consolidated tool) that provides retry and timeout layers |

Observations the walkthrough is meant to teach:

1. **The "platform covers it" verdict is common in some rows and rare in others.** Go and Rust lean on platform features for timeouts; C# often has a consolidated resilience library as the default answer. Do not carry one ecosystem's habits into another.
2. **The consolidated-versus-separate question appears in every row, in different forms.** A resilience bundle in .NET, a middleware stack in Rust, and an effect-system meta-library in TypeScript each trade per-concern depth for one coherent model. Evaluate them with the usage test and the critical-depth question from `references/tiers-and-discovery.md`.
3. **The application-model choice is itself decided by requirements.** In .NET especially, picking among server-rendered, component-based, and cross-platform UI models is a real decision; each model's distinctive capabilities must be checked against what the project will use, not the other way around.
4. **The retry and timeout rows depend on each other** in every ecosystem: retry attempts must fit within the timeout budget.

## Tier labels across ecosystems

| Tier | Illustrations (verify before use) |
|---|---|
| Library | A validator, a retry helper, a date utility, in any ecosystem |
| Meta-library | An effect-system toolkit (TypeScript), a resilience bundle (.NET, Java), a middleware-stack library (Rust), a large general-purpose utility collection (Java, C++) |
| Framework | A UI component framework or a web framework in any of the ecosystems above |
| Meta-framework | An opinionated layer over a framework that decides routing, rendering, and build conventions (common in JavaScript); in other ecosystems the equivalent may be a distribution or starter layer, or the platform's own framework may already play this role |

Where a candidate doesn't fit a tier cleanly (several .NET and Java options straddle framework and platform), say so and use the scope question: how many of the project's needed concerns does this single dependency decide or replace?
