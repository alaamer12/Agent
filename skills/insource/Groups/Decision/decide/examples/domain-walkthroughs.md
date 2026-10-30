# The same method in different domains

All candidate names, dimensions and showcase types below are illustrative, not exhaustive or mandatory. They show how the shape of the page changes with the domain. A hybrid or unlisted choice is always acceptable. Real runs must take every figure and snippet from supplied or found sources.

## Shape by domain

| Domain | Example candidates | Dimensions that tend to matter | Showcase shape | Extra tab worth considering |
|---|---|---|---|---|
| Programming languages | [language A] [language B] [language C] | runtime speed, memory use, concurrency model, tooling, hiring | the same small task in each language, with inner file tabs | Migration, Team ramp-up |
| Databases | [database A] [database B] [database C] | read and write throughput, consistency guarantees, operations effort, scale limits | schema and queries, backup and restore | Operations, Cost |
| CLI and developer tools | [tool A] [tool B] [tool C] | startup time, disk use, lockfile behavior, monorepo support | install and first run, a typical session | Migration |
| Cloud services | [a managed queue] vs [a self-hosted broker] | price at the user's scale, limits, regions, lock-in, support | setup steps, sample configuration | Cost model, Risks |
| Consumer products | [laptop A] [laptop B] [laptop C] | price, durability, battery, support, fit for the use | photo gallery per candidate (candidate tabs, with views such as [front] [side] [in use]) and a spec table; images verified with `scripts/check_images.py` | Where to buy |
| Audio and video gear | [microphone A] [microphone B] | sound quality, noise, price, durability | audio or video clips per candidate (candidate tabs); checked with `scripts/check_media.py` | Where to buy |
| Strategies or approaches | [build] vs [buy] vs [hybrid] | cost, time, risk, reversibility | a worked scenario for each | Timeline, Risks |

Candidate names in the table are placeholders. Real runs use the user's candidates.

If a showcase tab adds nothing for the domain, say so to the user and offer another second tab.

## Showcase layout, polyglot

A showcase block has candidate tabs, and a candidate can have inner file tabs. The same layout holds code in any language. Language idioms change between versions, so a real run fetches current examples from official sources. Below, the layout shown for one trivial task in three language families (illustrative only; in a real run fetch the snippets from official docs and cite them).

Task: read lines from a file and count them.

```go
// main.go (compiled, static types)
package main

import ("bufio"; "fmt"; "os")

func main() {
	f, _ := os.Open("input.txt")
	defer f.Close()
	n := 0
	for s := bufio.NewScanner(f); s.Scan(); { n++ }
	fmt.Println(n)
}
```

```python
# app.py (interpreted, dynamic types)
from pathlib import Path

print(sum(1 for _ in Path("input.txt").open()))
```

```rust
// src/main.rs (compiled, ownership model)
use std::{fs::File, io::{BufRead, BufReader}};

fn main() -> std::io::Result<()> {
    let n = BufReader::new(File::open("input.txt")?).lines().count();
    println!("{n}");
    Ok(())
}
```

Tabs: `Go | Python | Rust`; inner tabs for a candidate that needs several files, for example `Cargo.toml` and `src/main.rs`.

## Before and after: removing a single-domain assumption

| Before (assumes web UI) | After (domain-agnostic) |
|---|---|
| "Pick the framework with the best time to interaction." | "Pick the dimensions that matter for this kind of candidate, for example [time to interaction] for a UI framework or [write throughput] for a database." |
| "Showcase: basic usage, state, nested components." | "Offer showcase types that fit the domain, for example [basic usage] or [schema and queries]. The user can combine or add their own." |
| "Code tabs: `app.js`, `main.js`." | "Inner tabs are the files the candidate needs, for example [`main.go`, `go.mod`] or [`app.py`, `requirements.txt`]." |
| "Ecosystem is always a dimension." | "Ecosystem is a dimension when it matters, which is common for frameworks, languages and platforms." |
