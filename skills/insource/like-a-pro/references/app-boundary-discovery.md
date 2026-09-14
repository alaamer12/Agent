# App Boundary Discovery Protocol

The `like-a-pro` meta-skill operates strictly at the **application level**, never assuming the entire repository is a single application or guessing boundaries solely from folder hierarchies.

---

## 1. The Core Principle

> **Project structure does not define the Like-a-Pro scope; confirmed application boundaries do.**

A single repository may contain:
- Multiple distinct applications (e.g. `apps/web`, `apps/mobile`, `apps/admin`).
- A backend API service + web frontend + mobile client.
- A single modular application organized across many directories.
- Independent standalone packages.

Each confirmed application within a project may possess different programming languages, different database access rules, different UI technologies, and distinct error handling requirements.

---

## 2. Boundary Discovery & Confirmation Workflow

The agent executes the boundary discovery protocol before invoking any child convention skill:

```text
┌────────────────────────────────────────────────────────┐
│             App Boundary Discovery Flow                │
└────────────────────────────────────────────────────────┘

 ┌──────────────────────────────────────────────────────┐
 │ Stage 1: Structural Scan & Candidate Detection       │
 │ • Scan repository root, packages/, apps/, src/       │
 │ • Look for application entry points (Program.cs,     │
 │   main.go, index.ts, App.tsx, package.json, Docker)  │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Stage 2: Preliminary Boundary Formulation            │
 │ • Group folders into candidate application entities  │
 │ • Identify application nature:                       │
 │   - Web App / SPA / SSR                              │
 │   - Native Mobile App (iOS / Android / Cross)        │
 │   - Desktop Client (Win / Mac / Linux)               │
 │   - Headless Worker / Background Service Daemon      │
 │   - API Backend Service                              │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Stage 3: Mandatory User Confirmation                 │
 │ • Present the candidate boundary map to the user     │
 │ • Explicitly ask: "Are these the application         │
 │   boundaries for your project?"                      │
 │ • Allow user to correct, merge, or split apps        │
 └──────────────────────────┬───────────────────────────┘
                            │
                            ▼
 ┌──────────────────────────────────────────────────────┐
 │ Stage 4: Per-App Execution Mapping                   │
 │ • For each confirmed application, determine child    │
 │   skills to trigger (language, sql, errors, ui)      │
 └──────────────────────────────────────────────────────┘
```

---

## 3. Example Prompting Contract

When presenting discovered boundaries, use a structured question format:

```text
Based on my scan of the repository structure, I have identified the following candidate application boundaries:

1. Application: 'web-portal'
   - Path: apps/web/
   - Tech Stack: TypeScript, Next.js, React
   - Nature: Web Frontend (Has UI)
   - Proposed Standards: language-conventional (TS), errors-handling, ui-rules

2. Application: 'feed-worker'
   - Path: services/worker/
   - Tech Stack: Go
   - Nature: Background Daemon / Pipeline (Headless - No UI)
   - Proposed Standards: language-conventional (Go), sql-conventional, errors-handling

Do these application boundaries accurately reflect your project architecture, or would you like to adjust or merge any of them?
```

Only after the user confirms or adjusts this map does the agent proceed to run child skills for each application.
