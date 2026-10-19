---
name: decide
description: Helps the user choose between candidates (software in any language or platform, databases, tools, cloud services, products, approaches) by researching them fairly and delivering one rich HTML decision page. The Compare tab has a dated freshness section, per-dimension winners (ties allowed), charts, tables, ratings, sources and a goal-based verdict. The Showcase tab shows real examples (code, images, audio, video, documents, specs or sample output, whichever fits) with candidate tabs. The page exports to PDF. Use this whenever the user wants to decide, choose, pick, evaluate, or compare options, asks "which is best", "X or Y?", "should I use...", "help me pick a...", or mentions /decide, even if they do not ask for a page or report.
---

# Decide

Help the user reach a decision they can defend. Gather the user's goal and data, research fairly, and deliver one self-contained HTML page. The page is a small wizard: Compare first, then Showcase. Its structure follows the task and the domain, not a fixed template.

Options and examples in this skill's files are illustrative, not exhaustive or mandatory. A hybrid or unlisted answer is always acceptable. The skill is not tied to any language, platform or domain.

## Workflow

1. **Intake.** Ask before building. Read `references/intake.md`, ask the questions in one short message, and wait for the answers. Do not guess the goal, candidates, showcase types or palette.
2. **Gather data.** Use data the user supplied first. If they have none, run `/compare` if that skill exists. Otherwise search the web or another available source. Never fill gaps from memory. Record a source for every claim, and note today's date as the comparison date.
3. **Choose dimensions.** Read `references/method.md`. Pick the dimensions that matter for this goal and this kind of candidate. Skip any that do not apply.
4. **Analyze fairly.** Read `references/fairness.md`. Ties, tiers, equal weights and source grading are mandatory.
5. **Build the page.** Read `references/page-structure.md`, then `references/pdf-export.md`. Look at `examples/domain-walkthroughs.md` to see how the shape changes by domain. `examples/ui-frameworks-example.html` is working output for one domain, a picture of quality and not a template. Do not copy its data, code or section list. Its figures, versions, dates and snippets are a frozen snapshot and may be wrong today, so never reuse them.
6. **Verify.** Run `python scripts/check_page.py <page.html> --pdf <out.pdf>`. Fix every problem it reports. If the page shows media, also run the matching checker: `scripts/check_images.py` for images, `scripts/check_media.py` for audio, video, PDFs, 3D models and fonts (add `--hosted` when publishing, `--browser` for a real render test). For any other medium, write a checker first (see `references/media.md`). Look at a few rendered PDF pages if you can.
7. **Deliver.** Use the environment's normal delivery (publish tool if present, otherwise save the file and present it). Reply briefly: what is on the page, the verdict in one line, the comparison date, and the caveats (unverified claims, version conflicts, ties). Mention the Export PDF button. End with one question: which of the page's dimensions matter most to the user.
8. **Iterate until they decide.** Read `references/iteration.md`. Use the user's answer to re-weight the rating, extend a section, add a tab, add or remove candidates, or redo the search and compare step. Repeat as often as the user wants. When they decide, offer a short decision record.

## Hard rules

- Rely on supplied or found data, never on memory. Mark anything without a source as unverified on the page.
- Show the comparison date in its own freshness section (compared on, data covers, re-check by). The comparison goes out of date, so the page must say when it was made.
- Be fair. Several candidates can share first place. Do not invent a single winner when the data shows a tie.
- Use equal weights for the rating unless the user states priorities. Label the rating as derived, not measured.
- Tie the verdict to the user's goal. Name what would change the answer.
- Ask the user once whether they forgot any candidates. If they add none, continue with the ones named.
- Ecosystem is a dimension only when it matters. Writing model or ease of use sits under developer or user experience.
- The Showcase is not always code. It can show [code] [images] [audio] [video] [documents] [3D models] [spec sheets] [sample outputs] [step lists] or any other medium that helps the decision. Everything shown must come from official docs or other sources found in this session (or files the user uploaded), with the source cited. Never invent URLs. Verify every media file with its checker, write a checker if none exists, and never leave a broken item on the page.
- Default to the light theme, with `?theme=dark` for dark. Use the user's palette if they give one.
- Use two tabs (Compare, Showcase) by default. Add more only when the request calls for them, including later in the conversation.
- Do not stop at delivery. Think with the user: ask which dimensions matter, then keep refining until they decide.

## Files

- `references/intake.md`: questions to ask and what to do with the answers
- `references/method.md`: the evaluation method and example dimensions by domain
- `references/fairness.md`: ties, tiers, rating, source grading, freshness, wording rules
- `references/page-structure.md`: how to build the HTML (blocks, freshness section, tabs, focus mode, charts, tables, showcase, visual rules, gotchas)
- `references/pdf-export.md`: print stylesheet and PDF rules
- `references/iteration.md`: the closing question and how to handle follow-ups
- `references/media.md`: any medium in the showcase, how to verify it, and how to write a new checker
- `scripts/check_media.py`: verifies audio, video, PDFs, 3D models and fonts (exists, right file type, not an error page, plays)
- `scripts/check_images.py`: verifies every image reference exists, decodes and is not an error page; flags missing alt text and missing fallbacks
- `scripts/check_page.py`: checks the script for the unclosed-tag bug, validates syntax, requires the freshness section, tests PDF pagination
- `examples/domain-walkthroughs.md`: the same method applied to different domains
- `examples/ui-frameworks-example.html`: example of good output (web UI frameworks)
