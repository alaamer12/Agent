# Investigation levels

Analyze the levels the candidate patterns touch. The aim is to find patterns across the system, not just inside single files. Each level lists guiding questions, places to look, and the evidence to capture.

## Contents
- Code level
- Business level
- Application level
- System and architecture level
- Resource level

## Code level

- **Questions:** Which functions or classes carry too many responsibilities? Is logic duplicated or diverging? Are names truthful? Do comments match behavior? Are errors handled or hidden? Are abstractions used more than once?
- **Look at:** largest and most-changed files, outliers in complexity, suppression comments, catch blocks, TODO density, duplicate clusters.
- **Capture:** file and line ranges, LoC, complexity, nesting, parameter counts, duplicate pairs, excerpt (short).

## Business level

- **Questions:** What are the invariants? Where is each enforced? Do two places implement the same rule differently? Does the model's vocabulary match the domain? Are responsibilities in the right component?
- **Look at:** pricing, eligibility, state-machine, permission and validation code; domain docs; tests named after rules; SQL constraints and triggers.
- **Capture:** a rule-to-location map, with any divergence shown side by side.

## Application level

- **Questions:** How are use cases orchestrated? Is validation at the boundary? Where is authorization checked? Where do transactions begin and end? How is state held? How do errors propagate to callers?
- **Look at:** controllers/handlers, service layer, middleware, DTOs, transaction scopes, error mappers, state stores.
- **Capture:** one traced path per key use case with notes on validation, authz, transaction and error behavior.

## System and architecture level

- **Questions:** What is the real dependency direction? Are there cycles? Where are subsystem boundaries and who owns each dataset? How does a failure in one integration propagate?
- **Look at:** import/dependency graph, service-to-service calls, shared schemas, queues, deployment config, health and retry settings.
- **Capture:** dependency edges that violate the documented or evident architecture, cycle lists, ownership conflicts, failure-propagation notes.

## Resource level

- **Questions:** Does the project reimplement what a dependency, the framework, or an internal utility already offers? Are official assets (logos, icons, brand colors, SDKs) available but recreated?
- **Look at:** dependency manifests versus hand-written helpers; `utils/` contents; asset folders; icon libraries; vendor SDKs versus custom clients.
- **Capture:** the existing resource (name, version), the duplicate implementation location, and how they differ.
