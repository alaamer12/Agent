# Timestamp Representation

- **Description:** The rule that all timestamps are stored and transmitted as UTC ISO-8601 and
  rendered only in the viewer's local timezone; excludes scheduling logic and time-zone
  conversion UI features.
- **Ownership:** AoU — Database (Layer 0), Backend (Layer 1), Frontend (Layer 2).
- **Reason:** No single layer can guarantee the invariant alone: a correct backend that stores
  local time defeats a correct frontend, and column types drift in migrations. The protocol is
  shared, each layer owns its own adherence, and violations are defects in the violating layer.

## How To Do It

Column types without time-zone illusion (`timestamptz`/`TIMESTAMP WITH TIME ZONE` at the
Database), serialization always `Z`-suffix UTC at the Backend, display conversion only at the
Frontend's formatting boundary. A test in each layer guards its own side of the rule.