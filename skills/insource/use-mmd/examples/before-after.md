# Before / after — the six mistakes this skill exists for

Each pair: what a diagram looks like when it starts explaining, and what it looks like when it only
draws. Examples are illustrative shapes, not real systems.

## 1. Node repeats its panel

```mermaid
%% BEFORE — panel says REVIEWERS; every node re-says it
subgraph R["REVIEWERS"]
    R1(["code-review<br/>Reviewer Role"])
    R2(["doc-review<br/>Reviewer Role"])
end
```

```mermaid
%% AFTER — the panel carries the category
subgraph R["REVIEWERS"]
    R1(["code-review"])
    R2(["doc-review"])
end
```

## 2. Sentence node

```mermaid
%% BEFORE
C["Collect every raw record<br/>normalize fields, drop duplicates<br/>and stamp the batch date"]
```

```mermaid
%% AFTER — name only; the sentence is the runbook's job
C["normalize batch"]
```

## 3. One entity duplicated per context

```mermaid
%% BEFORE — the same helper drawn twice, named by target
V1["validate · schema"] -.-> S[("schema store")]
V2["validate · api"]  -.-> A["api layer"]
```

```mermaid
%% AFTER — one independent node, meaning on the edges
V(["validate"])
V -. "schema" .-> S[("schema store")]
V -. "api" .-> A["api layer"]
```

## 4. Text legend with ASCII glyphs

```mermaid
%% BEFORE — names colors in words; rots with the palette
L["LEGEND<br/>■ green: Blocking · ■ blue: Advisory · ▢ band: environment"]
```

```mermaid
%% AFTER — swatch nodes reuse the same classDefs; only
%% non-colorable grammar (line styles) stays as text
subgraph LG["LEGEND"]
    LL["solid: flow · dashed: advisory"]
    LS1["Blocking"]
    LS2["Advisory"]
end
classDef blocking fill:#fee2e2,stroke:#dc2626
classDef advisory fill:#dbeafe,stroke:#2563eb
class LS1 blocking
class LS2 advisory
```

## 5. Placeholder node for the future

```mermaid
%% BEFORE — a node for things that do not exist
subgraph T["TOOLS"]
    T1(["formatter"])
    T2(["future tools register here as they are made"])
end
```

```mermaid
%% AFTER — existence only; growth is a document rule
%% ("a new tool registers here and gets a spec file" lives in the doc)
subgraph T["TOOLS"]
    T1(["formatter"])
end
```

## 6. Mechanics that bite after edits

```mermaid
%% BEFORE — raw angle brackets swallow the label; a renamed id
%% left its class line behind (ghost)
W["write to out/<name>.json"]
class W writer
class WI writer   %% WI no longer exists

%% AFTER — escaped, ghosts cleaned
W["write to out/&lt;name&gt;.json"]
class W writer
```

Verify after every edit: `subgraph` count = `end` count; each id in exactly one `class` line; every arrow
target exists; a step inserted mid-chain rewires its connector instead of dangling off the end.
