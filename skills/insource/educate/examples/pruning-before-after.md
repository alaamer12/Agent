# Pruning example: `Installation.md`

This shows the kind of cut that step 1 (Prune) makes, assuming the project detected in step 2 uses **Bun** and is on **Node-compatible tooling** (i.e. the npm/yarn instructions are genuinely irrelevant here, not just less preferred).

## Before (raw, as retrieved by Scrape) — 27 lines

```markdown
# Installation

Welcome to the installation guide for AwesomeLib! This section will walk
you through everything you need to know to get AwesomeLib up and running
in your project. AwesomeLib supports a wide variety of package managers
so you can choose whichever one fits your workflow best.

## Prerequisites

Before installing, make sure you have Node.js 18 or later installed on
your system. You can check your current version by running `node -v`
in your terminal.

## Installing with npm

If you're using npm as your package manager, simply run the following
command in your project's root directory:

```
npm install awesomelib
```

## Installing with Yarn

If you prefer Yarn, you can install AwesomeLib with:

```
yarn add awesomelib
```

## Installing with Bun

Bun users can install AwesomeLib with:

```
bun add awesomelib
```

> **Note:** AwesomeLib requires `libfoo` version 2.x or later to be
> installed as a peer dependency on Linux systems. Without it, native
> bindings will fail to load at runtime with a cryptic segfault.

## Next steps

Once installed, head over to the Configuration guide to set things up.
```

## After (pruned) — 10 lines

```markdown
# Installation

Requires Node.js 18+.

```
bun add awesomelib
```

> **Note:** Requires `libfoo` v2.x+ as a peer dependency on Linux, or
> native bindings fail to load at runtime with a segfault.

See Configuration for setup.
```

## What changed and why

- The npm and Yarn install blocks were removed — the project uses Bun, so keeping them would only cost context window for no benefit.
- The marketing preamble ("Welcome to the installation guide...") was removed — it carries no actionable information.
- The prerequisites section was folded into a single line — the actual requirement (Node 18+) survived; the instruction on *how* to check your Node version did not, since that's general knowledge, not specific to this library.
- **The peer-dependency note was kept, and only lightly trimmed** — this is exactly the kind of information step 1 says to never drop: skipping it would mean the agent (or the user) hits a runtime segfault with no idea why, on a platform (Linux) that's genuinely likely to apply.
- The "Next steps" pointer was kept as a one-line cross-reference, since it's what lets the index (built in step 3) link installation to configuration.
