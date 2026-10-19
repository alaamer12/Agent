# anti-ai-writing

A Claude skill: 22 rules that strip the AI tells out of human-facing prose, gated by an audience test so it never fires on your internal notes and docs.

The problem it solves: AI-drafted text has a recognizable fingerprint (em-dashes, "delve", "I hope this finds you well", antithesis constructions, hedge stacking). Readers spot it, and it costs you credibility. These rules make Claude catch and fix the tells before a draft reaches a person.

What makes it different from a generic "write better" prompt:

- **Audience test first.** The rules apply only when a person other than the author will read the text. Internal notes, wikis, prompts, and commit messages are exempt, because a de-AI pass tuned for outreach prose actively degrades dense internal docs.
- **Caveat protection.** Rule 14 kills stacked hedges ("could potentially") but explicitly protects factual uncertainty labels ("unconfirmed", "unaudited", "estimate"). De-AI'ing a research or financial doc must never strip what you know about how well you know it.
- **Rules only, no scorer.** Half of these tells are judgment calls that regexes can't detect. There is no linter, no 0-100 score, nothing to game.
- **The pass itself has rules.** v1.1 adds what NOT to do when humanizing (no thesaurus-swapping, no fake typos, don't scrub personality: a flat, tell-free text is still AI-shaped), plus rhythm variance, commitment over both-sidesing, and concreteness rules. v1.2 adds the information-density meta-test and the structural-rewrite mandate: detectors match sentence-shape combinations, so formulations like the rule-of-three survive word swaps and even commercial humanisers (per the FT's 2026 test).

## Install

**Claude Code:** clone into your skills directory.

```
git clone https://github.com/iustinvaliza-del/anti-ai-writing-skill .claude/skills/anti-ai-writing
```

Project-level (`<repo>/.claude/skills/`) makes it available to everyone in that repo; personal (`~/.claude/skills/`) makes it yours everywhere. Claude discovers it automatically from the SKILL.md frontmatter.

**claude.ai / Claude Desktop:** Settings → Capabilities → Skills → upload a zip of this folder.

## Use

You mostly don't invoke it. When Claude drafts something a person will read (an email, a post, a deck, a report), the skill's description triggers it. You can also invoke it directly:

- "de-AI this draft"
- "make this sound human"
- "run this through the anti-ai-writing rules"

For internal notes, Claude leaves your text alone. That's by design.

## Versioning

SKILL.md is a versioned export (see the provenance note at its foot) of a canonical file maintained elsewhere. Rule changes land there first and get re-exported here with a version bump. If you fork this for your own team, your fork becomes your canon: edit SKILL.md directly and bump the version in the provenance note.

## License

MIT. Rules 10-18 adapted from [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) by Conor Bronsdon (MIT). See LICENSE.
