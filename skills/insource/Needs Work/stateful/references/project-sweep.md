# Sweep mode — a whole product surface at once

Entered when the target is an app, a whole navigation or command set, a folder of screens, or
"all the pages".
Default is still one screen at a time; the user opts into the sweep, or asks for it directly.
Platform-neutral: "product surface" means every user-visible screen however it is declared — routes,
action/command handlers, window or scene registries, menu trees, dialog stacks, terminal modes.

Sweeping screen-by-screen is the wrong move: most states recur, and a recurring state implemented per
screen ends up implemented N different ways. So the sweep's product is **two different things** — a
global mechanism, and a short per-screen residue.

## 1. Enumerate screens

Take the list from wherever the project declares its screens: the router or route table, the
navigation/scene stack, the command or action registry, the window/menu manifest, the CLI's
subcommand tree, the TUI's mode map — **not** from a file-tree scan (that returns components, partials
and layouts as if they were pages). Where the project declares screens, read the declaration.

Then classify each: **page** (own entry point + owns its data) · **overlay** (modal/sheet/dialog over
a page) · **shell** (chrome, nav, or window frame wrapping several). Only pages get the full pass;
shells and overlays are handled in step 4 as *owners*, not as victims. Report the count and the split
before continuing, and get a nod if the number is large.

## 2. Extract the eight facts per page

`inventory.md`, once per page. Keep it to the recording block — no prose. For > ~15 pages, do a
stratified pass first: sample one page from each area of the app (a browse page, a detail page, a
form page, a list-with-filters page, a settings page), run the full derivation on those, and use the
sample to build the cross-cutting set. Then confirm the remainder against it rather than re-deriving
everything from zero. Say which pages were sampled and which were inferred, and offer to run the rest.

## 3. Cluster

A state is **cross-cutting** when either test passes:

- **Frequency** — it appears on ≥ half the screens that can have it.
- **Shared mechanism** — it is produced by code the screens all share: the transport/provider wrapper,
  the session store, the connectivity or radio listener, the entry guard, the last-resort error
  boundary, the feature-flag service, the deserialisation boundary, the app shell, the local-store/cache
  layer, the device or driver abstraction. A state produced once at that layer *is* a global state even
  if only three screens show it.

Everything else is **screen-specific** — typically entity-lifecycle states (family E), the action
family for that screen's particular write (C), and the emptiness nuances of that screen's collections.

## 4. Cross-cutting ⇒ one owner, every screen, no exceptions

**This is the rule that makes the sweep worth doing.** A cross-cutting state is assigned exactly one
owning layer, implemented once there, and applies to **every screen without exception or per-screen
opt-out**. No screen may render its own competing version of a state the shared layer already owns —
that's how a product ends up with three different no-connection notices and two activity markers
stacked on each other.

| Cross-cutting cluster | Natural owner |
|---|---|
| `failed` / `timed-out` / `absent` / `refused` coming off the transport | the provider wrapper → screen condition; last-resort boundary as backstop |
| no-connection-at-entry, lost-mid-session notice, reconnecting, `throttled` | connectivity service + shell-level notice |
| maintenance, incident, client-incompatible | the shell's startup/capability check — takeover where warranted |
| not-signed-in, expired-mid-session, entitlement-limited | entry guard + shell |
| pending, background-refresh, stale indicators | the data/cache layer + a shared placeholder shell |
| unrecognised values / contract drift | the deserialisation boundary (tolerant reader), never the screen |
| transient-notice arbitration (family F) | a single notification queue in the shell |
| host lifecycle (suspend, kill-restore, low power, storage full) | the platform/host adapter, one place |

Then, per screen, wire the screen's resolver to consume what the owner emits. Wiring is not
re-implementing: if the shared layer already says `blocked(no-connection, no-cache)`, the screen
renders that and nothing else.

Anything genuinely needing a per-screen exception is **not cross-cutting** — reclassify it and say so.
If a screen's need contradicts the global decision hard enough to demand an exception, stop and raise
it as a design conflict for the user to settle; do not quietly fork the mechanism.

## 5. Consult — two approvals, not one

Present both tables (format in `assets/templates/matrix-template.md`), and get the user to settle, in order:

1. **The cross-cutting set + its owner per row.** Highest leverage; one row here is N screens.
   Also confirm the precedence order (`precedence-resolution.md`) — in a sweep it is a *product-wide*
   decision, including which contested positions were taken, and it must be written down once.
2. **The screen-specific residue**, grouped by screen. This is where rows get cut for budget; the
   cross-cutting set should not be bargained down.

Also confirm scope: "shared shells + wire every screen" vs "shared shells + the 5 worst screens now"
vs "audit only", and the **forcing hook** every screen inherits (query param / launch arg / env var /
dev menu). Be explicit about the diff size before touching code — a sweep legitimately changes many
files.

## 6. Implement shared-first

1. The owner layers, one at a time, each verified against a screen that already exercises it.
2. Wire screens to consume it — screen by screen, smallest first.
3. Screen-specific states last.

After each owner lands, **re-scan screens for duplicated handling** and remove it. Dedup is part of
the step, not a later cleanup: the sweep's failure mode is ending with both a global and a local
version of the same state.

## 7. Report

- Screens found: pages vs overlays vs shells; sampled vs inferred
- Cross-cutting states, each with its owner, and the screens now covered by it
- Screen-specific states added, per screen
- Duplicated handling **removed** (name the files)
- The global precedence order as adopted, and the contested positions as settled
- Conflicts raised and how the user settled them
- Screens left unhandled, and what it would take to finish them

Update whatever registry the project's conventions require for newly added shared blocks, in the
same change.
