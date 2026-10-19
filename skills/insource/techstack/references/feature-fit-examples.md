# Feature-Fit Worked Examples

These illustrate the pattern from Step 1B of the process: a feature can be natively supported by one technology, awkward/workaround-heavy in another, and effectively impractical in a third — even when all three are broadly "capable" of the project category. Verify specifics via search before repeating any of these as current fact (see Step 0) — libraries and platform APIs change, and these are meant to show the *shape* of the reasoning, not to be quoted as always-true.

## Mobile

- **Deep native hardware access** (e.g. custom Bluetooth LE protocols, background audio processing, ARKit/ARCore-level AR): natively straightforward in fully native (Swift/Kotlin) or React Native/Flutter (via native modules); often requires a custom native plugin layer in Ionic/Capacitor, meaning the "write once" benefit partially erodes for that specific feature.
- **Pixel-perfect platform-specific UI polish** (matching iOS and Android native look/feel exactly, including subtle platform gestures): more naturally achieved in Flutter (full custom rendering) or fully native; can require extra custom CSS/JS work in a WebView-based approach to avoid feeling like a website.
- **Simple CRUD app with a handful of screens and no unusual hardware needs**: this is the case where the fastest option (e.g. Ionic/Capacitor) has few real feature-fit downsides — the trade-off is more about long-term native feel than about any specific feature being blocked.

## Web frontend

- **Heavy real-time collaborative editing** (e.g. multiple cursors, operational transforms/CRDTs): well-supported by libraries built around that exact problem; bolting real-time collaboration onto a framework/architecture not designed for fine-grained reactive state can mean significant custom plumbing.
- **SEO-critical, content-heavy marketing pages**: naturally suited to frameworks with strong server-side rendering/static-generation support; a pure client-side SPA architecture can achieve this too, but often needs an added SSR layer or a separate static site generator bolted on.
- **Complex, highly interactive data-dense dashboards**: favors frameworks/libraries with mature state-management and virtualization ecosystems; a framework optimized for simplicity/small bundle size may lack the ecosystem to handle this without significant custom work.

## Backend

- **Very high-concurrency I/O-bound workloads** (e.g. tens of thousands of simultaneous long-lived connections): naturally suited to platforms built around lightweight concurrency primitives (event loops, green threads/actors); achievable elsewhere but may require careful architecture (worker pools, external queues) to avoid becoming a bottleneck.
- **CPU-bound heavy numerical/ML workloads**: naturally suited to ecosystems with mature numerical/ML libraries and native-extension support; possible elsewhere via bindings to native code, but that's an added integration layer rather than a first-class capability.
- **Strict compile-time type safety across a large team**: naturally suited to statically-typed languages/frameworks; achievable with gradual typing or added tooling in a dynamically-typed stack, but that's a bolt-on discipline rather than an enforced guarantee.

## How to use these

Treat these as prompts for the kind of question to ask about *this* project's actual feature list, not as a lookup table to apply mechanically. When the user names a feature not covered here, research its real support level across the actual candidates under consideration (Step 0's verification discipline applies) rather than guessing from a pattern that happens to look similar.
