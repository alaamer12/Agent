---
name: package-audit-and-cleanup
description: Audit and cleanup of project dependencies in a monorepo. Use when identifying unused libraries, removing redundancy, or optimizing package sizes across workspaces.
---

# Package Audit and Cleanup

## Overview

In a large monorepo, dependencies can quickly become redundant, outdated, or unused. This skill provides a systematic workflow for auditing `package.json` files across all workspaces (apps and packages), identifying "ghost" dependencies, and safely removing them without breaking the build or runtime.

---

## When to use this skill

- After a major refactoring where components were moved or replaced.
- When noticing bloat in `node_modules` or bundle sizes.
- To resolve redundancy where multiple packages depend on the same libraries that are already provided by shared "kit" packages.
- Periodic repository health checks.

---

## Workflow

### 1. Identify Target Surface
Select the package or workspace to audit (e.g., `apps/mobile`, `packages/features/*`).

### 2. Systematic Code Scan
Do NOT rely on your internal knowledge of the codebase. Use a script to verify usage.
- Scan all source files (`.ts`, `.tsx`, `.js`, `.jsx`).
- Check configurations: `babel.config.js`, `metro.config.js`, `app.json`, `tsconfig.json`.
- Identify "Essential Native Stubs": Some libraries like `react-native-screens` or `react-native-safe-area-context` are required for native runtime even if not explicitly imported in JS.

### 3. Redundancy Check (Monorepo Specific)
In this repository, many features are provided by "kits" (e.g., `@kit/shared`, `@kit/i18n`).
- If a package depends on `react-i18next` but also imports `@kit/i18n`, the direct dependency is likely redundant as `@kit/i18n` should export the necessary translation hooks.
- If a package depends on `expo-haptics` but imports `@kit/shared`, check if `@kit/shared` provides a haptics utility.

### 4. Categorize Dependencies
- **Used**: Actively imported or required for config/native.
- **Unused**: No references found in code or config.
- **Redundant**: Used, but provided by a shared kit.
- **Dev-only**: Used only in tests or build scripts, but listed in `dependencies`.

### 5. Implementation & Cleanup
- Move dev-only tools to `devDependencies`.
- Remove **Unused** and **Redundant** candidates.
- Run `bun install` to update the lockfile.

### 6. Verification
- **Build**: Ensure the workspace still builds.
- **Typecheck**: Run `bun run typecheck` in the modified workspace(s).
- **Runtime**: (If possible) Verify core functionality related to removed packages.

---

## Best Practices

- **Peer Dependencies**: Core libraries used across many packages (like `react`, `react-native`, `zod`) should often be `peerDependencies` in feature packages to ensure version consistency.
- **Barrel Imports**: Be careful when auditing barrel imports (`index.ts`). Removing a package might break an export that is used elsewhere.
- **Side Effects**: Some packages are imported just for side effects (e.g., `import 'server-only'`). These won't show up in variable usage but are critical.

---

## Audit Script Template
See `reference.md` for a reusable Node.js script to automate the detection of unused dependencies.
