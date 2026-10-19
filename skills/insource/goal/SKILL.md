---
name: goal
description: Define clear, unbreakable, achievable goals with explicit completion criteria and resource awareness. Use when setting objectives, starting complex work, verifying task completion, or when goals involve environment or resource constraints. Triggers include goal, define goal, set objective, success criteria, verify completion, goal skill, is the goal done.
---

# Goal

Help the agent define a goal and verify that it has actually been achieved. Apply these principles every time a non-trivial objective is set or completion is claimed.

## Core Principles

1. **Clear** — State the goal in precise, unambiguous language. No vague outcomes.
2. **Unbreakable** — The goal statement must not be open to reinterpretation or partial success that pretends to be full success. Success and failure must be binary and observable.
3. **Achievable** — Given the agent's tools, environment, permissions, and the user's constraints, the goal must be reachable.
4. **Finished definition** — Explicitly define the observable conditions under which the goal is considered complete. "Done" must be measurable or demonstrable, not assumed.
5. **Resource-aware** — Account for limited resources (platform, devices, network, time, APIs, credentials). Achievement is always relative to available resources.

## Before Starting Work

1. Restate the goal in one or two precise sentences that satisfy the five principles.
2. List the concrete completion criteria (what evidence proves the goal is met).
3. Identify resource constraints that affect verification (e.g., Linux environment cannot fully verify iOS-native behavior).
4. Communicate any resource limitations and the resulting relative definition of "done" to the user.
5. Obtain explicit user confirmation of the goal statement, completion criteria, and any relative-success interpretation before proceeding.

Example of resource-relative completion:

- Goal: "Build an application that works on iOS."
- Environment: Linux only. No iOS device or simulator available.
- Relative completion: Application builds, runs, and passes tests on Android emulator or available device. Full iOS verification is impossible and is therefore excluded from the success criteria after user confirmation.
- If an iOS environment later becomes available and working, the agent must re-verify the original goal fully.

## During Work

- Keep the goal statement and completion criteria visible and unchanged unless the user explicitly revises them.
- Do not silently expand, shrink, or reinterpret the goal.
- When a resource constraint is discovered mid-work, pause, inform the user, and reconfirm the adjusted completion criteria.

## Verifying Completion

1. Check every stated completion criterion against observable evidence.
2. Produce the evidence (logs, screenshots, test output, file existence, running process, etc.).
3. If any criterion cannot be verified because of missing resources, state that clearly and mark the goal as achieved only relative to the previously confirmed constraints.
4. Never claim full achievement when verification was impossible; claim relative achievement and list what remains unverified.

## Anti-patterns

- Accepting vague goals such as "make it better" or "finish the feature" without completion criteria.
- Declaring success because "it seems to work" without matching the stated criteria.
- Pretending a Linux-only test fully satisfies an iOS goal.
- Changing the goal mid-stream without user confirmation.
- Ignoring newly discovered resource limits instead of reconfirming with the user.
