# readme — review checklists

Load this file at two moments: when auditing an existing README (workflow
§1) and during the final review before declaring done (§12). Everything here
is a question to answer with evidence, not a form to fill.

## Auditing an existing README (issue hunt)

Compare the README line by line against the *current* project:

- [ ] Outdated descriptions (no longer what the project does)
- [ ] Incorrect or stale installation / usage instructions
- [ ] Features described that no longer exist
- [ ] Features implemented but undocumented
- [ ] Generic or meaningless intro text
- [ ] Missing prerequisites (runtimes, services, credentials, config)
- [ ] Wrong commands, paths, script names, environment/config names
- [ ] Unsupported claims (performance, security, scale, "the best")
- [ ] Sections that no longer serve the project's purpose
- [ ] Redundancy that makes the README harder to navigate
- [ ] Broken or invented links, anchors, badge URLs, asset paths

Fix the hits; keep everything accurate and useful even where its placement
isn't where your taste would put it (preserve established structure).

## Evidence sweep (before writing anything)

The proportionate investigation — pick what exists for this project:

- structure & entry points · package manifests / metadata · core modules and
  public APIs · user-facing interfaces · config files · dependency manifests
  and lockfiles · install/build scripts · existing docs · tests and
  representative examples · CI and release config · deployment instructions ·
  license · contribution guidelines

Classify as you go: **implemented / partial / planned / experimental** —
and note which claim maps to which file, so every sentence in the README
has a source.

## Final review passes

### Accuracy
- Description matches the actual project?
- Features/capabilities correctly represented; planned distinguished from
  implemented?
- Technical claims each trace to evidence?
- Install/usage consistent with real scripts and config?

### Clarity
- Primary audience can grasp the purpose quickly?
- Motivation specific and meaningful (not invented, not a stack restatement)?
- Explains value rather than listing technologies?
- No repetition or generic filler ("powerful", "seamless", empty intros)?
- Holds the chosen voice/style (§2b) consistently start to finish (hybrids state their seam)?
- If restyled, the fact core matches the original claim-for-claim (tone edits never smuggled
  claim edits)?

### Structure
- Sections appropriate to *this* project's type and audience?
- Important information where readers will look for it?
- Links, anchors, asset paths valid (checked, not assumed)?
- Headings and Markdown formatting consistent? Code fences closed?

### Completeness
- Covers what its stated purpose and audience require?
- Prerequisites and real limitations documented where relevant?
- Requested languages handled; localized versions substantively identical;
  identifiers/commands/config keys untranslated?
- Every explicit user requirement satisfied?

### Verification honesty
- Split the output into: **tested** / **reviewed against config** /
  **could not verify (why)** — and say so in the report.
- No claim that links, commands, builds, or examples were verified unless
  the check was actually performed.

## Completion criteria

Done when all hold:

1. README created/updated at the appropriate path.
2. Description accurately reflects the project.
3. Purpose/motivation expressed meaningfully where relevant.
4. Structure suits the project and its primary audience.
4b. Chosen voice/style (or repo-established default) held throughout and its guardrails respected
   (marketing claims still evidenced; deep-DX keeps a quick start up front; minimal still lists
   blockers).
5. Technical claims and instructions grounded in evidence.
6. Links, examples, assets checked to the extent practical.
7. Explicit user requirements and material content decisions addressed.
8. Final review passes run; in-scope findings fixed.
9. Material verification limitations communicated honestly.

The README need not contain every detail about the project — its
completeness is determined by purpose and audience, never by section count.
