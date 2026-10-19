# Checklists

> One concern: rationalizations to reject, red flags to watch for, and verification lists.  
> Load on demand when reviewing a commit or a release.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I'll commit when the feature is done" | One giant commit is impossible to review, debug, or revert. Commit each slice. |
| "The message doesn't matter" | Messages are documentation. Future you (and future agents) will need to understand what changed and why. |
| "I'll squash it all later" | Squashing destroys the development narrative. Prefer clean incremental commits from the start. |
| "Branches add overhead" | Short-lived branches are free and prevent conflicting work from colliding. Long-lived branches are the problem — merge within 1–3 days. |
| "I'll split this change later" | Large changes are harder to review, riskier to deploy, and harder to revert. Split before submitting, not after. |
| "I don't need a .gitignore" | Until `.env` with production secrets gets committed. Set it up immediately. |
| "It's just a small fix, bump the patch" | Check what consumers can observe. A behavior change they relied on is a major, whatever the diff size. |
| "The changelog is just the commit log" | Commits are for you; the changelog is for consumers, curated by impact. Generating one from raw commits buries what matters. |
| "We'll write the changelog at release time" | By then the impact is reconstructed from memory and half of it is missing. Write the entry with the change. |

## Red Flags

- Large uncommitted changes accumulating
- Commit messages like "fix", "update", "misc"
- Formatting changes mixed with behavior changes
- No `.gitignore` in the project
- Committing `node_modules/`, `.env`, or build artifacts
- Long-lived branches that diverge significantly from main
- Force-pushing to shared branches
- A breaking change shipped under a minor or patch version bump
- A release with no tag, or a version number hand-edited out of sync with the tag
- A user-facing release with no changelog entry, or a changelog that's just dumped commit messages

## Verification

For every commit:

- [ ] Commit does one logical thing
- [ ] Message explains the why, follows type conventions
- [ ] Tests pass before committing
- [ ] No secrets in the diff
- [ ] No formatting-only changes mixed with behavior changes
- [ ] `.gitignore` covers standard exclusions

For every release (anything with consumers):

- [ ] The version bump matches the change: breaking → major, additive → minor, fix → patch
- [ ] The release is tagged, and the version is derived from the tag, not hand-edited out of sync
- [ ] The changelog has a curated, human-readable entry grouped by impact for this version
