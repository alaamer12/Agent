# capabilities

> This document defines the `capabilities` steering folder: what the system provides or does across features. It lives in the **perception tier** (`perception/`); see [`index.md`](index.md) for the taxonomy overview.

**Holds.** Business-level functional capabilities: what the system does, calculates, or executes across features and surfaces (sentence shape: *"The system does X"* or *"The console provides Y"*). A core capability that the entire application is built around (such as media playback in a streaming app or asset valuation in a simulator) belongs here at the business level.

**Shape.** Topic-named Markdown files describing system actions and behaviors (e.g., `virtual-trading.md`, `periodic-sync.md`, `cms-authoring.md`).

**Does not hold.**
- Business rules about what is permitted, forbidden, or who decides ([`policy.md`](policy.md)).
- Conceptual entities, roles, and states ([`domain.md`](domain.md)).
- Technical runtime mechanisms, caching, or protocol details (which belong in the tech tier's steering function folder; see [`function.md`](function.md)).
- Single-feature implementation mechanics (which belong in feature documentation outside the taxonomy).

**The test.** System verbs. Does the statement describe what the system or console does, calculates, or provides?
- *Capabilities vs. Policy*: "The system updates standings approximately once per minute" is a capability (system behavior). "Users cannot trade while standings are recalculating" is a policy (forbidden constraint).
- *Capabilities vs. Domain*: The states of a competition (open, active, concluded) are `domain`. The automated transition that closes a competition on its end date is `capabilities`.

**Example (`perception/shared/capabilities/virtual-portfolio`).**
"Every user account starts with an initial virtual cash balance and can allocate funds across listed external assets. The system calculates holding valuations and net profit/loss based on periodic price feeds received from the data provider."

**Example (`perception/admin/capabilities/cms-controls`).**
"The operator console allows administrators to author, update, and publish interface strings, educational questions, and level thresholds dynamically without requiring application deployments."
