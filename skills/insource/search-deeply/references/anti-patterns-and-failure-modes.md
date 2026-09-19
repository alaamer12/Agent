# Anti-Patterns and Failure Modes

## Common Anti-Patterns in Resource Lifecycle & Ownership Design

These anti-patterns appear across domains that manage expensive, stateful, or concurrent resources (connections, handles, workers, buffers, media surfaces, caches, sessions, etc.). Adapt the concrete names to the domain under study.

| Anti-Pattern | Why it fails | Typical symptom |
|--------------|--------------|-----------------|
| Every item owns a permanent expensive resource | Exhausts limited hardware or memory on large collections | OOM, thermal throttling, progressive degradation after N items |
| Visibility / focus signal directly drives resource mutation | No ownership, no cancellation, races under rapid change | Multiple resources active, stale operations completing |
| UI component owns all resource state | Lifecycle tied only to mount/unmount; ignores page, navigation, or OS events | Resources survive navigation or die too early |
| Making large runtime objects deeply reactive / observed | Triggers expensive tracking on objects that change frequently | Jank, high CPU, unexpected re-renders or recomputations |
| Destroy and recreate the resource on every focus change | Pays full startup / acquisition cost repeatedly | Visible latency, thrashing of limited hardware resources |
| Prefetch or prepare too many resources | Pressure on network, memory, or concurrency limits | Active item starves; high cost; degraded performance |
| Rely only on component mount / unmount | Misses page, keep-alive, background, or session events | Leaked resources, continued work in background |
| Rely only on framework page / navigation lifecycle | Misses rapid focus changes and visibility races | Stale operations after focus moves away |
| No cancellation of asynchronous work | Stale promises or callbacks resolve after ownership changed | Wrong resource activated or mutated |
| Multiple independent components decide activation | No single source of truth | Simultaneous activation, contention, inconsistent state |
| No generation / epoch / token on activation | Classic race | Previous item’s async work finishes and mutates current state |
| Ignoring platform interruption or focus signals | Platform forcibly stops or ducks the resource | Silent failure or unexpected interruption |
| Treating “prepare / prefetch” as full materialization | Wastes bandwidth, memory, or compute | High cost, delayed activation of the true focus item |
| No single owner for mutation | Concurrent writers | Corrupted state, double-free, or undefined behavior |

## Failure-Mode Table Template

For every architecture study produce a table covering the relevant scenarios. Adapt names and add domain-specific rows. Minimum useful columns:

| Scenario | Detection | Cause | Recovery | Cleanup | Observable behavior |
|----------|-----------|-------|----------|---------|---------------------|
| Activation / start rejected by policy | Promise / future / callback rejection or error event | Platform policy, permission, or runtime restriction | Retry under allowed conditions or surface affordance | Keep resource, clear transient error | User sees fallback or explicit control |
| Acquisition / load timeout | Timer after start of acquisition | Network, service, or hardware delay | Abort, surface retry, move focus if appropriate | Cancel token, release partial resource | Spinner then error or skip |
| Stall / waiting / back-pressure | Runtime waiting signal or progress halt | Buffer underrun, queue full, or dependency stall | Continue waiting or apply back-pressure policy | None or limited retry | Indicator or degraded mode |
| External dependency disappears | Offline / error / connection-lost signal | Connectivity or service outage | Pause, mark unavailable | Optional abort of in-flight work | Offline or unavailable message |
| Dependency characteristics change | Connection-type or quality signal | Policy or adaptive logic | Re-evaluate quality / window / priority | None | Possible quality or window adjustment |
| Corrupted or unsupported resource | Error event with specific code | Format, version, or integrity problem | Skip item, report, move to next | Dispose or quarantine resource | Skip or error card |
| Hardware / concurrency limit reached | Error or platform signal | Too many simultaneous instances | Release others, fall back, or skip | Aggressive release of non-focus items | Possible quality drop or delay |
| Multiple concurrent activation attempts | Guard inside manager | Race under rapid change | Ignore subsequent attempts | None | Single activation wins |
| Stale asynchronous completion | Generation / epoch / cancellation token | Async work finishes after focus moved | Ignore result | Abort previous work | No unexpected mutation |
| Component or view unmount while acquiring | Unmount signal + pending work | Navigation or destruction | Abort + dispose | Full release | Clean exit |
| Page / session leave while acquiring | Framework leave event | Navigation | Pause + release non-visible window | Release window | Clean exit |
| Application background while acquiring | Visibility / OS background event | OS lifecycle | Pause all, optional release | Keep metadata / light state | Silent background |
| Application resume | Visibility / OS foreground event | OS lifecycle | Re-evaluate focus item | Re-prepare if needed | Resume focus |
| Resource reused for new item | Source / identity change | Pool / reuse design | Abort previous, reset state | Clear listeners / observers, attach new | Instant switch |
| Identity or source changes while active | Intent change | User or data update | Stop, load new | Abort old | Smooth transition |
| Item recycled by virtualization / windowing | Window move signal | Virtualization | Release resource | Detach | No leak |
| Memory or concurrency pressure | OS signal or observed growth | Too many live instances | Aggressive release of non-focus items | Dispose excess | Possible quality drop |

## Recovery Principles (Universal)

1. Never let a stale asynchronous operation mutate the currently owned or focused resource.
2. Always have a single owner that is allowed to call activate / pause / load / mutate.
3. Prefer pause + keep when the item may return to the window soon.
4. Prefer abort + dispose (or return to pool) when the item has left the preparation window or the page / session is leaving.
5. Surface user- or system-visible recovery only when the focused item is affected; silent recovery for background or non-focused items.
6. Measure and refine pool size, window size, and release thresholds on the target environment; do not treat starting numbers as permanent.
