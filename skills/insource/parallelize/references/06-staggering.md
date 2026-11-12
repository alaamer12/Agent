# Staggering starts

Staggering delays when an agent is allowed to begin. It changes the schedule only: the ownership table, interfaces, wave membership, and dependency graph are exactly what they were without it.

Use it when simultaneous starts would contend for one shared resource — an API rate limit, one dev server, a staging database, a package registry, a CI runner, a browser pool — or when an early slice must establish state that later slices read. Do not use it for independent local work with no shared resource, and never as a substitute for a real dependency or readiness check.

## Asking for it

The user can invoke any of these (the trigger word is `staggering`):

```
/parallelize with staggering 30 — <task>
/parallelize with staggering each 0/30/60 — <task>
/parallelize with staggering main 60 — <task>
/parallelize <task> with staggering each 20 + main 45
```

Natural-language equivalents map to the same schedule:

| User says | Spec |
|---|---|
| "stagger the workers by 30 seconds" | `30` |
| "start every worker 20 seconds after launch" | `each 20` |
| "wait 0/30/90 before workers 1/2/3" | `each 0/30/90` |
| "only worker 2 waits 45 seconds" | `w2=45` |
| "only the main waits a minute" | `main 1m` |
| "use the up-agents exponential schedule, 30s base" | `exp 30` |

If the delay or the target is missing ("stagger them"), ask one question before launching. Do not pick a default.

## Grammar

`with staggering <spec>`, where `<spec>` is one base schedule, optional explicit overrides, and optional main delay, joined by `+`:

| Clause | Meaning |
|---|---|
| `<duration>` | Linear ramp. The k-th member of the wave waits `(k-1) × duration`. |
| `each <duration>` / `all <duration>` | Every subagent waits the same absolute duration. |
| `each <d1>/<d2>/...` | Explicit absolute delay per slice, in slice-index order. Missing tail entries are 0. |
| `wN=<duration>` | Override one subagent's delay. `w1=0` means start immediately. |
| `main <duration>` / `main=<duration>` | Delay the main agent's own slice by that amount (see below). |
| `exp <duration>` / `exponential <duration>` | `duration × (2^(k-1) - 1)` for the k-th member of the wave. |
| `none` | Explicitly disable staggering. |

- Durations are seconds by default. Accept `30s`, `2m`, `1m30s`, `0`.
- `wN` refers to the **global slice number in the plan**, so `w3=45` means the same slice in every wave.
- An `each` list describes the **wave being launched**, in slice-index order. Entries past that wave's member count are ignored, and a slice with no entry starts at 0. The same spec is reused for the next wave unless the user gives a per-wave list.
- A one-slice wave needs no stagger; state its delay as 0 unless the user asked for that slice explicitly.
- Use `/` only inside an `each` list and `+` between clauses.
- A leading `stagger` is accepted as noise: `with staggering stagger 30` means `30`.

**Precedence:** an explicit `wN` beats the `each` list, which beats the base schedule. The base schedule is exactly one of `each`/`all`, a linear ramp, or `exp`; if two are written, ask instead of guessing. `main` is independent and can accompany any base schedule.

## The schedule table

State this in chat with the fan-out plan, before spawning:

| Agent | Wave | Delay | Wave-relative start | Why |
|---|---|---|---|---|
| Main | — | `main` value or 0 | — | Own slice only; pre-wave work is immediate |
| W1 | 1 | 0s | 0:00 | First starter |
| W2 | 1 | 30s | 0:30 | Same shared API |
| W3 | 1 | 60s | 1:00 | Same shared API |

Compute against the actual number of subagents in each wave. If the plan changes (a slice is folded back into the main), recompute and restate the schedule before the next launch.

## Waves

- The clock resets at each wave's launch. A delay is relative to that wave, not the whole run.
- Wave boundaries are still dependency- and integration-driven. Never launch wave 2 on a timer just because wave 1's delays elapsed; integrate first.
- Staggering never increases the concurrency cap. It can only reduce simultaneous starts.

## Dependencies beat delays

A delay is a floor, not an authorization:

- If slice B consumes slice A's output, B waits for A to return, even if B's timer expired first.
- If an agent starts and its dependency is missing, the brief must say what to do (wait, stub, or return blocked) — not guess the interface.
- A delay cannot make two slices with overlapping write sets safe. Ownership still decides.
- If the real need is "wait until file X exists", use a readiness check in the brief; a sleep is a guess.

## Main-agent delay

`main <d>` applies only after the main has launched the wave:

1. Pre-wave work (interfaces, shared files, snapshot, plan) happens immediately — it is what unblocks the wave.
2. The main launches every subagent in the wave.
3. The main waits `<d>` before touching its **own slice's files**. During the wait it may monitor, answer questions, and unblock subagents.
4. If a subagent reports ready early and the main's input is needed, the main may answer; the delay governs file work, not conversation.

Use `main` when the main's slice would otherwise collide with the first starters on the shared resource, or when the main should see the first results before editing its own paths.

## Brief: first action

Every delayed subagent's brief opens with:

```
SCHEDULE: sleep {N}s before doing anything else. Do not read, write, or run project commands
before the sleep completes. After it, re-read the files you own; the tree may have changed.
```

Use the platform's sleep command: PowerShell `Start-Sleep -Seconds N`, POSIX `sleep N`, CMD `timeout /t N /nobreak`. For `0`, omit the block entirely.

The brief still carries the same snapshot, owned paths, do-not-touch list, done-when checks, and return format. The sleep does not weaken any of them.

## External CLI agents

The same schedule applies when slices are separate processes. Start each process in the background with the sleep as its first shell command, or delay the process launch itself. Log the scheduled start and the actual start next to each slice; a process that starts late is a schedule fact, not a failure.

## Cost and safety

- Staggering trades wall-clock time for shaped load. Say what the run loses: if the last starter waits 90s, the wave's completion moves by at least that much.
- Keep the ramp small relative to slice duration. If the total delay exceeds the expected wave time, propose a smaller step instead of silently applying it.
- Do not stagger agents that only read disjoint local files; there is nothing to protect.
- Do not use staggering to mask a missing interface, a missing test, or a race you have not diagnosed.
- If the user insists on a schedule that is clearly wasteful, apply it and state the cost — it is their call.

## Difference from up-agents

`up-agents` always adds a reviewer subagent and reserves a 60% reviewer-delay buffer for the last worker. This skill has no reviewer role: the main integrates. `exp <d>` reproduces its worker formula, but no reviewer buffer is added. `up-agents` hard-codes one schedule; here the user can specify per-subagent, all-subagent, or main-only delays and combine them.

## Checklist

- [ ] Parsed the spec into a schedule table (or asked once).
- [ ] Stated the schedule in chat with the fan-out plan.
- [ ] Kept ownership, interfaces, and dependency order unchanged.
- [ ] Added the sleep line to every delayed brief; omitted it for 0.
- [ ] Confirmed `main` delays only the main's own slice, not pre-wave work.
- [ ] Reported the schedule and its wall-clock cost in the final report.
