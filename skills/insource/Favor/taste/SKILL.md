---
name: taste
description: Smart design router skill that clarifies user intent to route to either ui-taste (apps/dashboards/iOS) or design-taste-frontend (landing pages/showcases).
---

# Taste Router

A lightweight router skill that determines the appropriate design workflow by asking clarifying questions and delegating to the corresponding skill available in the agent environment.

## Workflow

1. **Clarify Intent:**
   - When a design or UI improvement request is ambiguous, ask the user:
     * Is this an **interactive app, dashboard, or native mobile interface**?
     * Or is it a **landing page, marketing site, or corporate showcase**?

2. **Route:**
   - **Apps, Dashboards, Mobile (iOS):** Activate and follow the `ui-taste` skill.
   - **Landing Pages, Showcase Sites, Marketing:** Activate and follow the `design-taste-frontend` skill.
