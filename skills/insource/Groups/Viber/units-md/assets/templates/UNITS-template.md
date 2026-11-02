# UNITS

<!-- units-md: use this skeleton only when the project has no incumbent units/catalog format. If one exists,
     follow its headings, ids and ordering instead - see references/01-the-file.md ("Merging into a convention"). -->

<One paragraph: this file is the index of reusable units in <project>, so work extends what exists instead of
building a parallel one. It is an index, not documentation: one row of facts per unit, detail lives in the code
and in each unit's own doc.>

**Excluded from scope:** <vendored dependencies / generated clients / build output / fixtures / <packages not
covered by this pass>>.

**Last refreshed: <YYYY-MM-DD>**

## How to use

Before implementing or planning anything:

1. **Read this file in full.** An index read partially is an index ignored.
2. **Reuse or extend.** If a unit covers, or partly covers, what the task needs, use it. Building a parallel
   component requires stating the reason in the change.
3. **Add new units in the same task.** If the change creates a new reusable unit, its entry belongs in this file
   in that same change - not as a follow-up.
4. **Owner:** <whoever changes the unit updates its row>. For delegated work, subagents report the row back and
   the <master agent / integrator> merges it, so two workers never edit this file at once.

## <Area, e.g. Outbound and platform>

### U-001: <Responsibility as a name, not a folder>
- **Purpose:** <One line: what it does, so a reader can decide whether it covers their need.>
- **Where:** <project-root-relative path that exists, e.g. `src/net/http.py`; several allowed, comma-separated>
- **Depends on:** <unit ids, or `-`>
- **Status:** <active | deprecated | experimental | unknown>
- **Verified:** <YYYY-MM-DD - the day this claim was checked against the code>

<!-- Optional fields, add only when they carry information:
- **Used by:** <who depends on this, when it is not obvious>
- **Reuse instead of:** <the parallel implementations this unit replaces>
- **Owner:** <team or person, when it is not "whoever changes the code">
- **Notes:** <constraints and gotchas: "one instance assumed", "not safe on the request path">
-->

## <Area, e.g. Domain rules>

### U-002: <name>
- **Purpose:** <...>
- **Where:** <...>
- **Depends on:** U-001
- **Status:** <...>
- **Verified:** <...>

---

Validate before handing the file over:

```bash
python <skill-dir>/scripts/units_lint.py docs/UNITS.md --strict --max-age 90
```

Ids are monotonic: never renumber existing entries, never reuse a retired id. A deprecated unit keeps its place
and points at its replacement.
