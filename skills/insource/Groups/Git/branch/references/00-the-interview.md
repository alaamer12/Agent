# The interview — what to ask, in what order, and when not to

Branching has no standard, so the strategy is a set of decisions the user makes once. This file is about
extracting those decisions **without interrogating someone about things the repository already answers**.

## Before asking anything, read the repo

```bash
git symbolic-ref --short HEAD                                   # is the trunk main, master, develop?
git fetch --quiet                                                # then look at what really exists
git for-each-ref --sort=-committerdate --format='%(refname:short)\t%(committerdate:short)' refs/heads/ | head -20
git for-each-ref --format='%(refname:short)' refs/remotes/origin | head -20   # are branches deleted after merge?
git log --oneline --merges -10                                  # merge commits, or squash-merged noise?
git log --format='%an <%ae>' -20 | sort | uniq -c               # author identity, co-author trailers
test -f AGENTS.md && grep -niA8 "workflow\|branch\|commit\|author" AGENTS.md | head -40
ls .github/workflows .github/PULL_REQUEST_TEMPLATE.md .gitlab-ci.yml 2>/dev/null
git config --get pull.rebase; git config --get merge.ff; git config --get advice.pushForceRejected
```

Read the answers, not the file names. Twenty live `feature/*` branches with squash merges and deleted remotes
tells you the whole strategy without asking. A repo where every author is the same person and history is linear
is a solo trunk-based project, whatever its README says.

| Evidence found | Meaning | Action |
|---|---|---|
| `AGENTS.md` states branch rules | already decided | **do not ask**; follow it |
| Branch names cluster in one pattern | incumbent convention | follow it, mention it, ask only about gaps |
| Merge commits into `main` with `Merge pull request #123` | PR-side, merge-commit policy | do not ask "PR or local?"; do ask about lifetime |
| Only `main` and short-lived single-purpose branches | trunk-ish | ask about the fix-separation rule, nothing else |
| A `develop` branch that everyone merges into | Git Flow residue | ask whether it is still wanted (it is usually a liability now) |
| Fresh repo, no history | genuinely undecided | ask the whole set |

## The questions

Ask once, in a single round, and make each one answerable in a word. Never ask a question whose answer you can
read off the repository — that is how you lose the user's patience and get "whatever you think" answers.

### 1. Naming

"How should branches be named?" Offer the pattern, not the abstract idea:

- `feature/add-login-page`, `fix/header-bug`, `release/v1.2.0`, `chore/upgrade-node` — Conventional Branch
  (see [`02-naming.md`](02-naming.md)); machine-checkable, CI can key on the prefix.
- `1234-add-login-page` — issue-first, best when the tracker is the spine of the work.
- `amro/feature/login-page` — owner-first, best when several people or agents are the confusing variable.
- `add-login-page` — flat; fine for a solo project that never names more than a handful of branches.
- whatever the repo already does.

### 2. Where merging happens

"Is a PR on the origin side the merge point, or are you solo so branches are just organization and you merge
locally?" Explain what the answer changes:

- **PR-side**: branch names and history shape become contract surface — protection rules, CI path filters,
  `Closes #` semantics, review assignment. Deleting a branch after merge is normal; force-push to a shared
  branch is the thing that hurts other people.
- **Local/solo**: no external gate exists, so the discipline has to live in the **lifetime cap** and the commit
  hygiene, or a solo repo quietly becomes twelve branches of which nobody remembers the state of six.

### 3. Separation policy

"Does every fix get its own branch, or is a fix commit inside the feature branch fine?"

- Strict separation: `fix/*` stays cherry-pickable onto a release while the feature is unfinished; every
  interrupt costs a branch.
- Flow-tolerant: fewer moves, honest history ("this fix landed inside that feature because the feature exposed
  it"), but a half-finished feature can now block an urgent fix — which is exactly when the mechanism in
  [`commit`'s fix-interrupts-feature reference](../../commit/references/12-fix-interrupts-feature.md) gets used.

Ask which of those two worlds they live in. Solo + no release branches → the second is usually right. Anything
shipped to users from a tagged release line → the first is usually right.

### 4. Lifetime and complexity

"How long may a branch live, and how many kinds of branch do you want?"

Defaults worth proposing: **merge within a day** (DORA's measured elite pattern is three or fewer active
branches and merging at least daily); no branch kind you do not use; `release/*` only if you actually ship
from it; no `develop` unless two versions are truly developed in parallel.

### 5. Authorship disclosure — ask this one explicitly

Two places an agent's fingerprint can appear, and people feel differently about both. If `AGENTS.md`,
`.mailmap`, git config, or the recent history already answers it, **do not ask** — read the answer and quote
where you found it.

- **In commits**: do they want a co-authorship trailer, e.g.
  `Co-authored-by: Qoder (Qwen) <noreply@…>` — or none, with the agent treated as a tool the human operated?
  Existing convention is visible: `git log --format='%(trailers:key=Co-authored-by)' -20 | grep -c .`
- **In branch names**: an agent-identity segment, e.g. `qoder-qwen/feature/login-page`, `claude/fix-header-bug`,
  or the vendor-neutral Conventional Branch `ai/` type — or nothing, so an agent branch is indistinguishable
  from a human one.

Why it matters rather than being cosmetic:

- It is the only cheap way to keep **provenance legible in the repository itself**, and to let a pipeline
  require a heavier review or a security scan on machine-authored work (`ai/*`, `claude/*` are in the
  specification precisely for that).
- It sets what a reviewer learns from `git log` about who did the work, which is an accountability choice, not
  a formatting choice.
- In multi-agent sessions (situation B/C in [`03-agent-coordination.md`](03-agent-coordination.md)), an owner or
  agent segment in the name is also what makes a collision *readable*: `codex/fix-parser` vs `claude/fix-parser`
  explains itself; two identically-named branches do not.

Put the question plainly and offer the three real options:

```text
Authorship: how do you want agent-authored work to be identifiable?
  commits    (a) Co-authored-by: <product> (<model>) <noreply@…>   (b) nothing, the human is the author
  branches   (a) agent/identity segment: qoder-qwen/…, claude/…, ai/…   (b) nothing, no agent segment
Whichever you pick, I will write it into AGENTS.md so nobody is asked twice.
```

Refusing the trailer is a legitimate choice; so is asking for it. What is not legitimate is either option being
decided silently by the agent, in either direction — adding attribution nobody asked for is as much an
unconsented change as erasing the provenance of who did the work. Note also that a trailer is a **public claim**
once pushed: it names a product and a model in a shared artifact, so a wrong guess is not harmless.

## After the answers

Restate the strategy in five lines and get agreement:

```text
trunk main · naming <type>/<description> with an agent segment when authored by a tool (qoder-qwen/…)
merge locally into main after tests; PR only for releases
fixes may ride the feature branch; a fix during an unfinished feature uses the cherry-pick path
branch lifetime: merge same day, delete after merge
commits: Co-authored-by: Qoder (Qwen) <noreply@…>; branches carry the agent segment
```

Then write it where it belongs: **`AGENTS.md` for the permanent case** ([`05-permanent-policy.md`](05-permanent-policy.md)),
or say plainly "this holds for this session only" when the user did not want it durable. An answer that lives
only in the transcript will be re-asked by the next session — which is exactly the cost this section exists to
avoid.

## What not to ask

- Anything the repo says (trunk name, merge style, whether PRs are used, authorship trailers).
- "Git Flow or trunk-based?" as a vocabulary test. Ask about release cadence and who integrates, then recommend.
- The agent's own implementation choices: worktree path layout, whether to use `git worktree` at all when the
  project is trivially small, how the claim file is formatted.
- Re-litigating a recorded answer because you would choose differently. The user's decision wins; note the
  disagreement in one clause and move on.
