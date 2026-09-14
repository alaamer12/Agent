# Worked Example (Generic)

This is an invented, illustrative example — a small order-processing system —
used only to show the *shape*, depth, and tone expected of a System
Components document. Do not treat the domain (orders, queues, workers) as
prescriptive; the target application may be a mobile app, a web client, a desktop tool, a compiler, a trading
system, or a background worker daemon. What should transfer is the structure: overview diagram →
component hierarchy tree → numbered per-component sections with a
consistent field set → relationship map → closing summary table.

---

# System Components — {ExampleApp}

> **Version scope:** Base (applies to all versions).
> **Read alongside:** [`runtime-flow.md`](./runtime-flow.md) for sequencing · [`tech/README.md`](./tech/README.md) for implementation conventions · [`UNITS.md`](./UNITS.md) for UI builder units.

---

## System Overview

{ExampleApp} is a single-process service that receives incoming orders,
validates and enriches them, and persists the result while notifying
downstream consumers. There is no external orchestrator; all coordination
happens in-process.

```
┌───────────────────────────────────────────────────────────────┐
│                    {ExampleApp} (Single Process)              │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  INGESTION SUBSYSTEM                   │   │
│  │  ┌──────────┐   ┌────────────┐   ┌──────────┐          │   │
│  │  │  Intake  │→  │  Validator │→  │  Queue   │          │   │
│  │  │  Service │   │            │   │          │          │   │
│  │  └──────────┘   └────────────┘   └────┬─────┘          │   │
│  └──────────────────────────────────────┼─────────────────┘   │
│                                          ▼                    │
│                                   ┌─────────────┐             │
│                                   │ Worker Pool │             │
│                                   └──────┬──────┘             │
│                                          ▼                    │
│                                 ┌─────────────────┐           │
│                                 │  Storage Engine │           │
│                                 └────────┬────────┘           │
│                                          ▼                    │
│                                 ┌─────────────────┐           │
│                                 │ Notification Bus│           │
│                                 └─────────────────┘           │
└───────────────────────────────────────────────────────────────┘
```

---

## Component Hierarchy

```
{ExampleApp}
│
├── Ingestion Subsystem
│   ├── Intake Service
│   ├── Validator
│   └── Order Queue
│
├── Worker Pool
│   └── Enrichment Service
│       └── External Pricing Client
│
├── Storage Engine
│   ├── Database
│   └── Repository Layer
│
├── Notification Bus
│
└── Error System
    ├── Domain Error (Result<T>)
    └── Module Error Files
```

---

## 1. Ingestion Subsystem

### Type
Subsystem

### Purpose
Owns everything from "an order arrives" to "a valid order is queued for
processing." Exists as its own subsystem because ingestion has distinct
reliability requirements (reject bad input fast, never lose a valid order)
from the heavier enrichment work downstream.

### Responsibilities
- Accept incoming order payloads
- Validate structural and business-rule correctness
- Enqueue valid orders for the Worker Pool
- Reject invalid orders with a specific, actionable error

### In Scope
- Structural validation (required fields, types)
- Business-rule validation (e.g. order total > 0)

### Out of Scope
- Pricing enrichment (delegated to Enrichment Service)
- Persistence (delegated to Storage Engine)

### Related Components
- [Worker Pool](#2-worker-pool) — consumes from the Order Queue

---

## 2. Worker Pool

### Type
Subsystem

### Purpose
Coordinates asynchronous order processing, rate limiting, and external enrichment calls before persistence.

### Responsibilities
- Pull orders from the queue
- Orchestrate concurrent processing workers
- Enforce rate limits against downstream external APIs

### In Scope
- Concurrency management and backoff

### Out of Scope
- Order validation (delegated to Ingestion Subsystem)
- Direct database writes (delegated to Storage Engine)

### Subcomponents
- **Enrichment Service:** Fetches pricing metadata
- **External Pricing Client:** HTTP client wrapper

---

## Component Relationship Map

```
{Intake Service}
  │  enqueues to →          {Order Queue}
  │                              │
  └─ consumes via →         {Worker Pool}
                                 │
                                 ↓
                            {Storage Engine}
```

---

## Component Identification Summary

| Component | Type | Removing It Would… |
|---|---|---|
| Ingestion Subsystem | Subsystem | Leave the application unable to accept or validate incoming payloads |
| Worker Pool | Subsystem | Require synchronous processing, creating bottlenecks and dropping traffic spikes |
| Storage Engine | Data System | Lose all order data on restart, violating persistence requirements |
