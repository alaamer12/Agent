---
name: dig-binary
description: Universal software reverse engineering and black-box system inspection across all layers: web/JS bundles, runtime tracing, network protocols, native binaries (PE, ELF, Mach-O), bytecode (JVM, Dalvik, Python, .NET), archives (ZIP, JAR, APK, TAR, ASAR), and local data stores. Use when source code is missing, obfuscated, or partial and internal models, APIs, hidden behaviors, or error causes must be uncovered.
---

# Universal Software Reverse Engineering & Black-Box Inspection

A comprehensive methodology and toolkit for reverse engineering modern software systems when source code is absent, incomplete, or obfuscated. It covers static artifact dissection (web bundles, native binaries, bytecode, archives), dynamic runtime tracing (process arguments, environment variables, I/O monitoring), network protocol reconstruction (REST, GraphQL, Protobuf/gRPC, WebSockets), and data storage analysis (SQLite, LevelDB, serialization models).

---

## When to Use This Skill

- Investigating packaged applications, desktop apps (Electron, JVM, native), CLI tools, or web services whose source is not in the workspace.
- Uncovering hidden or undocumented API endpoints, route paths, payload schemas, and authentication flows.
- Analyzing compiled archives and bundles (`.jar`, `.zip`, `.apk`, `.asar`, `.tar`, `.whl`, `.nupkg`).
- Inspecting compiled bytecode: JVM (`.class`), Kotlin metadata, Python (`.pyc`), Android (`.dex`), or .NET assemblies.
- Dissecting web/frontend bundles: minified JavaScript, source maps (`.map`), Webpack/Vite chunks, and local storage.
- Extracting strings, symbols, API imports, and constants from native executables and libraries (`.exe`, `.dll`, `.so`, `.dylib`).
- Diagnosing obscure runtime or backend errors (e.g. licensing restrictions, `FORBIDDEN_EMAIL`, auth rejections) by reconstructing client validation logic vs backend policy checks.

---

## The 5-Stage Universal Reverse Engineering Workflow

```
[1. System Footprint] ──> [2. Artifact Triage] ──> [3. Deep Dissection] ──> [4. Protocol & Data] ──> [5. Dynamic Probing & PoC]
```

### Stage 1: System Footprint & Environment Tracing
Identify how the software executes, where it stores data, and what environment variables control it:
1. **Trace launcher shims and entry scripts**:
   - Inspect `.bat`, `.cmd`, `.sh`, or wrapper scripts to find installation directories, data caches, and argument routing.
   - Example: Shims often map paths like `%USERPROFILE%\.local\share\<app>` or `/usr/local/share/<app>` and parse CLI flags before spawning the binary.
2. **Inspect configuration cascades & environment**:
   - Check local configs (`config.json`, `.env`, settings in `%APPDATA%`, `~/.config`, Windows Registry).
   - Look for undocumented debug flags, channel switches, proxy overrides (`HTTP_PROXY`, `ALL_PROXY`), or mock endpoints.

### Stage 2: Artifact & Package Triage
Examine the package structure, formats, and constituent libraries:
1. **Detect target architecture & packaging**:
   - **Archives**: ZIP, JAR, APK, TAR, wheel (`inspect.py <file> -p "<pattern>"`).
   - **Web / Electron**: `resources/app.asar`, `package.json`, bundled node_modules, minified `.js` bundles.
   - **Bytecode**: JVM `.class`, Android `.dex`, Python `.pyc`.
   - **Native**: PE (`.exe`/`.dll`), ELF (`.so`), Mach-O (`.dylib`).
   - **Storage**: SQLite databases (`.db`, `.sqlite`), LevelDB (`.ldb`).
2. **Locate critical functional modules**:
   - Filter entries by domain keywords: `auth`, `token`, `trial`, `promo`, `license`, `client`, `proxy`, `gateway`, `api`, `config`, `service`.

### Stage 3: Deep Dissection & Representation Analysis
Analyze the underlying instructions, metadata, or serialized structures without heavy decompilation toolchains:
1. **Bytecode & Constant Pools**:
   - In JVM `.class` files, extract UTF-8 string tables and constants:
     ```bash
     python C:\Users\amrmu\.junie\skills\dig-binary\scripts\inspect.py <jar_or_class> -e "<ClassName>.class"
     ```
   - Identify enum definitions and error reasons (e.g., `NOT_FOUND`, `EXPIRED`, `ALREADY_USED`, `ACTIVATIONS_LIMIT_REACHED`).
   - Inspect Kotlin serialization descriptors (`<Class>$$serializer.class`) to discover exact JSON field mappings.
2. **Web Bundles & Source Maps**:
   - Search minified JS for route definitions, API clients (`fetch`, `axios`), and state stores.
   - Extract `.map` source maps if available to recover original unminified TypeScript/JavaScript source files.
3. **Native Binaries**:
   - Extract ASCII and UTF-16LE strings: `python inspect.py <file.exe> -s`.
   - Check imports/exports for network, registry, and crypto APIs.

### Stage 4: Protocol, State & Data Modeling
Reverse engineer network communications and data schemas:
1. **Reconstruct API Endpoints & Routes**:
   - Extract URL literals and route patterns:
     ```bash
     python C:\Users\amrmu\.junie\skills\dig-binary\scripts\inspect.py <target_path> -u
     ```
   - Map route fragments (e.g., `/api/trial/activate`, `/v1/chat`) to discovered proxy/backend hosts.
2. **Reconstruct Payloads & Authentication**:
   - Identify expected `Content-Type` (JSON, Protobuf, multipart), `User-Agent`, and auth headers (`Bearer <token>`, `X-Api-Key`).
   - Decode JWT tokens for inspection of claims and scopes:
     ```bash
     python C:\Users\amrmu\.junie\skills\dig-binary\scripts\inspect.py dummy -j "<jwt_token>"
     ```
3. **Inspect Local Persistence**:
   - Inspect SQLite database schemas (`sqlite3 <db> ".schema"`) or LevelDB key-value stores to uncover cached states, offline queues, and session credentials.

### Stage 5: Dynamic Probing & PoC Verification
Confirm hypotheses through targeted, non-destructive verification:
1. **Build a standalone minimal reproducer (PoC)**:
   - Create a clean script (e.g., Python using standard `urllib` or `requests`) targeting the discovered endpoint with deduced headers and auth tokens.
2. **Differentiate Client vs Server Enforcement**:
   - Determine whether a restriction or error originates from client-side input validation (enums in bytecode/JS) or backend-level policy checks (e.g., `FORBIDDEN_EMAIL` returned by backend proxy despite client accepting code format).
3. **Document Findings with Actionable Evidence**:
   - Record exact request/response pairs, status codes, payload structures, and underlying business rules.

---

## Supporting Resources

- **`references/cli-recipes.md`**: Complete command-line cookbook of battle-tested one-liners for PowerShell, Bash, and Python `-c` (in-memory archive exploration, constant-pool string dumps, URL carving, port snooping, and live endpoint probes).
- **`references/bytecode-and-archive-analysis.md`**: Deep dive into JVM `.class` headers (`0xCAFEBABE`), Constant Pool specification, Kotlin metadata structures, archive streaming inspection, and native binary headers.
- **`references/runtime-network-and-bundle-analysis.md`**: Technical reference for Electron/ASAR packages, minified JS & source maps, native IAT/ELF symbols, Protobuf/gRPC wire format, GraphQL introspection, and SQLite/LevelDB data carving.
- **`scripts/inspect.py`**: Zero-dependency cross-platform utility to inspect archives (ZIP/JAR/APK/TAR), scan directory trees, parse JVM constant pools, extract binary strings, carve URLs/endpoints, and decode JWT payloads.
