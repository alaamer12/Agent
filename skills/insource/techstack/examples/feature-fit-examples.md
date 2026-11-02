# Feature-Fit Worked Examples

These illustrate the pattern from Step 1B of the process: a feature can be natively supported by one technology, awkward/workaround-heavy in another, and effectively impractical in a third — even when all three are broadly "capable" of the project category. Verify specifics via search before repeating any of these as current fact (see Step 0) — libraries and platform APIs change, and these are meant to show the *shape* of the reasoning, not to be quoted as always-true.

## Mobile

- **Deep native hardware access** (e.g. custom Bluetooth LE protocols, background audio processing, ARKit/ARCore-level AR): natively straightforward in fully native development (Swift, Kotlin); in cross-platform stacks (for example React Native, Flutter, .NET MAUI or Uno, Kotlin Multiplatform) it is usually reachable through bindings or native modules, but each adds a custom native layer, so the "write once" benefit partly erodes for that feature. Web-view-hosted approaches (for example Ionic/Capacitor) often need a custom native plugin.
- **Pixel-perfect platform-specific UI polish** (matching iOS and Android native look and feel, including subtle platform gestures): more naturally achieved with fully native UI or with stacks that render native controls; stacks with their own custom rendering give consistency across platforms rather than per-platform fidelity; web-view-hosted approaches can need extra work to avoid feeling like a website. Which side of this each candidate falls on must be verified.
- **Simple CRUD app with a handful of screens and no unusual hardware needs**: the case where the fastest-to-deliver option in the team's ecosystem has few real feature-fit downsides. The trade-off is mostly long-term native feel, not any specific feature being blocked.

## Desktop and cross-platform UI

- **One codebase on Windows, macOS, and Linux with native-feeling UI**: the answer differs by ecosystem. Candidates include web-technology shells, a managed-runtime cross-platform UI framework, a native toolkit with bindings, or per-platform native apps. Which fits depends on how much of the UI is custom, how much platform integration is needed, and what the team already writes. Discover the current candidates for the ecosystem via topic search rather than from memory.
- **Windows-only line-of-business tool**: the platform's first-party UI stack may be the simplest, best-supported choice, and cross-platform options would be carried weight.

## Ecosystem note

Everything above is phrased by capability, not by product. When naming products, name them across more than one ecosystem (for example, cross-platform mobile and desktop options exist in the JavaScript, .NET, Kotlin, Dart, and native-toolkit ecosystems) and verify each via Step 0. Do not let the ecosystem the agent knows best set the shortlist.

## Web frontend

- **Heavy real-time collaborative editing** (e.g. multiple cursors, operational transforms/CRDTs): well-supported by libraries built around that exact problem; bolting real-time collaboration onto a framework/architecture not designed for fine-grained reactive state can mean significant custom plumbing.
- **SEO-critical, content-heavy marketing pages**: naturally suited to frameworks with strong server-side rendering/static-generation support; a pure client-side SPA architecture can achieve this too, but often needs an added SSR layer or a separate static site generator bolted on.
- **Complex, highly interactive data-dense dashboards**: favors frameworks/libraries with mature state-management and virtualization ecosystems; a framework optimized for simplicity/small bundle size may lack the ecosystem to handle this without significant custom work.

## Backend

- **Very high-concurrency I/O-bound workloads** (e.g. tens of thousands of simultaneous long-lived connections): naturally suited to platforms built around lightweight concurrency primitives (event loops, green threads/actors); achievable elsewhere but may require careful architecture (worker pools, external queues) to avoid becoming a bottleneck.
- **CPU-bound heavy numerical/ML workloads**: naturally suited to ecosystems with mature numerical/ML libraries and native-extension support; possible elsewhere via bindings to native code, but that's an added integration layer rather than a first-class capability.
- **Strict compile-time type safety across a large team**: naturally suited to statically-typed languages/frameworks; achievable with gradual typing or added tooling in a dynamically-typed stack, but that's a bolt-on discipline rather than an enforced guarantee.

## Mechanism parity — same capability list, different internals

The pattern the feature table cannot catch: two candidates tick every box identically, use the same
API shapes, and still feel different to work with daily, because *how* they deliver a capability is
not the same. Worked illustration (verify fresh before repeating as current):

- **Two Vue component ecosystems, say an Ionic-based kit vs a self-contained one (e.g. Ionic-Vue vs
  Quasar).** Both claim forms, focus states, themable components, date pickers — the checklist ties.
- **Focus:** the Ionic-style kit largely rides the platform's native focus (its components are thin
  wrappers over standard elements/web components); the self-contained kit maintains its own internal
  notion of which component is focused, independent of the browser's. Same feature, different
  mechanism — and the mechanism difference leaks as lower accessibility, keyboard-flow surprises and
  screen-reader incoherence that no feature table predicts.
- **Styling customization:** the wrapper-style kit lets you restyle through ordinary selectors and
  its documented variables; the self-contained kit seals its internals, so real customizations need
  piercing (`:deep()` selectors, specificity fights). If the community answer to "how do I change
  this component's style" is a piercing workaround, extension has become penetration.
- **How to catch this before choosing:** for the two or three capabilities used *every screen*
  (focus/forms, styling overrides, scrolling), read each candidate's theming and a11y docs and inspect
  its **public repository**: the component source itself, the issue tracker and discussions, plus Q&A
  sites — search the capability with "accessibility", "custom style", "override". Published code needs
  no black-box probing; read what is already public. If the published record gives no answer, report that honestly as an unknown rather than deciding the tie by assumption. Tie on features, split on mechanism. A month into the project, mechanism is what "was this a bad decision?" actually
  measures.

## How to use these

Treat these as prompts for the kind of question to ask about *this* project's actual feature list, not as a lookup table to apply mechanically. When the user names a feature not covered here, research its real support level across the actual candidates under consideration (Step 0's verification discipline applies) rather than guessing from a pattern that happens to look similar.
