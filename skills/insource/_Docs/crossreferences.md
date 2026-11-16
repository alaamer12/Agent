## Manager crossreferences and agent instructions

### Discover references between skills

```bash
python manager.py crossreference
python manager.py crossreference --verbose
python manager.py crossreference --json
```

`crossreference` takes no skill names: every run compares all active registry skills and reports the whole graph. Positional values such as `crossreference iwts` are rejected as unrecognized arguments (exit `2`); to look at one skill, search the output or filter the `--json` edges by `from`/`to`.

Each row means **the source skill's documents mention the target skill's name**, not that a runtime dependency has been proven. The table shows direction, distinct mention-line count, whether the reverse edge also exists, and the first `file:line` witness. `--verbose` shows all witnesses; JSON includes all evidence, excerpts around the matched names, scan statistics, ambiguous names, and read errors.

Matching and ownership rules:

- Scan UTF-8 `.md`, `.mdx`, `.txt`, and `.rst` files, including skill instructions, references, examples, templates, and battery methods. Code, binary assets, root catalog prose, archive trees, `_Resources`, hidden files/directories, and linked files/directories are outside this scan.
- Match complete skill-name tokens, case-insensitively. Plain `iwts`, `/iwts`, inline-code names, and names in Markdown links all count; `pre-iwts` and `iwts_extra` do not match `iwts`. Repetitions on the same source line count once per target.
- The nearest independent skill owns each file. A meta-child's documents are not scanned again for its parent; a battery method's references belong to the battery. Self-mentions do not create edges.
- Skill names come from the discovered skill directory names, consistent with the manager's inventory and folder/name lint rule. Duplicate target names are reported with their candidate paths rather than converted into guessed edges.
- Common words that are also skill names can produce textual matches unrelated to the skill. Inspect the evidence; the command does not infer aliases, understand prose, validate link destinations, or claim that every match is an intentional skill dependency.
- Exit `0` means a complete, unambiguous scan, including an empty graph. Exit `1` means an ambiguous target or an unreadable document/directory. Evidence collected before a read failure remains visible. The command does not write to the manager database.

**Algorithm:** build a hash index from skill-name tokens to skill paths, then tokenize each document once and look up each token. Core matching takes expected `O(P + T + R)` time, where `P` is the combined name length, `T` is the scanned text length, and `R` is the recorded evidence size. Filesystem traversal and deterministic ordering are additional; sorting the graph's `E` edges takes `O(E log E)`. The index, directory-owner map, and evidence are retained in memory, not whole documents. This avoids an all-pairs skill comparison and needs neither Shell sort nor a new dependency.

### Deploy the relocated instruction source

The source for `manager.py agent` is [`_Resources/AGENTS.md`](../_Resources/AGENTS.md), not a root-level `AGENTS.md`. Existing destination filenames inside each agent's home configuration are unchanged.

```bash
python manager.py agent --agents qoder --dry-run
python manager.py agent --agents qoder
python manager.py agent --agents qoder --hard-copy
```

The first command previews the deployment; the other two write to the selected agent's configuration. A missing `_Resources/AGENTS.md` is an error, even if a stale root-level file remains. Moving the source does not itself update previously installed instruction files or links; run `agent` for the intended targets when ready to refresh them.
