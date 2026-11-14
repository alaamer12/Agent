# App boundary discovery protocol

`system-md` writes **one `SYSTEM-COMPONENTS.md` per application**. Before anything is written, the agent
must know which applications exist - and it never takes that from the folder tree alone. This file is the
protocol for finding the candidates, showing the evidence, and getting the user's confirmation.

---

## 1. The core principle

> **Project structure does not define the document's scope; confirmed application boundaries do.**

A single repository may contain:

- several distinct applications (`apps/web`, `apps/mobile`, `apps/admin`);
- a backend API service, a web frontend and a mobile client;
- one modular application spread across many directories;
- independent standalone packages that are not applications at all.

Each confirmed application can have its own language, data access rules, UI technology and error-handling
requirements - which is exactly why one blended `SYSTEM-COMPONENTS.md` across apps is wrong, and why a
wrong boundary produces a document that describes nothing real.

---

## 2. Discovery and confirmation workflow

Run this before step 2 of the procedure in `SKILL.md`. Nothing downstream runs on an assumed boundary.

```text
┌──────────────────────────────────────────────────────────┐
│ Stage 1: Structural scan & candidate detection           │
│ • Scan the root, apps/, packages/, services/, src/       │
│ • Look for entry points and deployables:                 │
│   Program.cs, main.go, main.rs, __main__.py, index.ts,   │
│   App.tsx, package.json "main"/"bin", Cargo.toml [[bin]],│
│   pyproject [project.scripts], Dockerfile, compose,      │
│   mobile/desktop manifests, CI deploy jobs               │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 2: Preliminary boundary formulation                │
│ • Group folders into candidate application entities      │
│ • Name each candidate's nature:                          │
│   - Web app / SPA / SSR                                  │
│   - Native mobile app (iOS / Android / cross-platform)   │
│   - Desktop client (Windows / macOS / Linux)             │
│   - Headless worker / background service / daemon        │
│   - API backend service                                  │
│ • Mark what is NOT an app: shared libraries, generated   │
│   clients, tooling, config packages                      │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 3: Mandatory user confirmation                     │
│ • Present the candidate map with its evidence            │
│ • Ask explicitly: "Are these the application boundaries  │
│   for your project?"                                     │
│ • Let the user correct, merge, or split applications     │
└────────────────────────────┬─────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│ Stage 4: Per-app document mapping                        │
│ • One SYSTEM-COMPONENTS.md per confirmed application,    │
│   at its root or docs folder (apps/<app>/...)            │
│ • Single-app project: one document at the project root   │
│ • Shared code: listed in the app that consumes it, with  │
│   a pointer to where it actually lives                   │
└──────────────────────────────────────────────────────────┘
```

### Evidence, not names

A folder name is a hint; a manifest, an entry point or a deploy target is evidence. `services/` may hold one
application or ten; `packages/ui` is usually a library, not an app. For every candidate, record the files that
make it one - those are what the user reviews in Stage 3.

| Signal | Usually means |
|---|---|
| Own entry point + own deploy/run target | an application |
| Own manifest but only imported by others | a library - list it under its consumers |
| One entry point, many feature folders | one modular application, not several |
| Generated code, scripts, CI config | not an application |

---

## 3. Prompting contract

Present the discovered boundaries as a structured question, with evidence per candidate:

```text
Based on my scan of the repository, I found these candidate application boundaries:

1. Application: 'web-portal'
   - Path: apps/web/
   - Evidence: apps/web/package.json (next build/start), apps/web/app/layout.tsx
   - Tech stack: TypeScript, Next.js, React
   - Nature: Web frontend (has UI)

2. Application: 'feed-worker'
   - Path: services/worker/
   - Evidence: services/worker/cmd/worker/main.go, deploy/worker.Dockerfile
   - Tech stack: Go
   - Nature: Background daemon / pipeline (headless - no UI)

Not applications: packages/ui (component library used by web-portal), packages/config.

Do these boundaries reflect your project, or should any be adjusted, merged or split?
```

Only after the user confirms or adjusts this map does the agent write any `SYSTEM-COMPONENTS.md`.

---

## 4. Re-confirming on refresh

A boundary already confirmed - documents exist at the agreed paths - does not need to be re-asked on every
refresh. Ask again only when the evidence changed: a new entry point or deployable appeared, an app was
removed, or two apps were merged. Then show only the changed part of the map.
