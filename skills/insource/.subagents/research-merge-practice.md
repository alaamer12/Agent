# Research: merge practice — practitioner rules, anti-patterns, real failure stories

Domain slice: **how professionals run merges safely, what must never be done, and the decision rules for
"both sides advanced — which code is correct?"**
Out of scope (owned by other agents): git's internal machinery (object/ort algorithm detail), and
data-format merging (JSON/CSV/schema merge semantics). Cross-references to the Linus "don't invent
behavior in a merge" doctrine are marked as such and not duplicated at length.

## 0. Method and evidence rules

* Every rule below carries a URL and a block quote taken from the fetched page.
* Quotes were taken from the rendered page text (the fetched HTML/Markdown converted to text). Where the
  source is a man page, asciidoc emphasis markers (`_..._`, `*...`) and Git's `…` ellipsis were normalised;
  wording was not changed. Quoted code/commands are reproduced as displayed.
* Claims that could not be backed by a fetched page are quarantined in §7 (UNVERIFIED) and must not be
  presented as sourced facts in the skill.
* Local read-only probes (scratch repos under `%TEMP%/mergetest.H7Sz8A`, git 2.46.2.windows.1) are recorded
  in §6 with their raw output, including one place where observed behaviour contradicts the man page.

Sources fetched (33): Atlassian (4 pages), Pro Git (3 sections), git man pages/guides (12), git official
howto `revert-a-faulty-merge`, GitHub docs (3), VS Code docs, Thoughtworks Radar, trunkbaseddevelopment.com
(2), Graphite (2), Martin Fowler bliki, bors-ng, dev.to incident report, Cargo FAQ, Composer docs,
Factory (agent guidance), CodeRabbit (agent docs).

---

## 1. Practitioner rules that survive contact with production

### 1.1 The one rule about rewriting history — "public" is the line, not "pushed"

> The golden rule of `git rebase` is to never use it on *public* branches.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

> So, before you run `git rebase`, always ask yourself, "Is anyone else looking at this branch?" If the
> answer is yes, take your hands off the keyboard and start thinking about a non-destructive way to make
> your changes (e.g., the `git revert` command). Otherwise, you're safe to re-write history as much as you
> like.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

Note the test is *observability by others*, not "did it touch a remote": the same page allows force-pushing
after a private-branch cleanup —

> One of the only times you should be force-pushing is when you've performed a local cleanup *after* you've
> pushed a private feature branch to a remote repository (e.g., for backup purposes). This is like saying,
> "Oops, I didn't really want to push that original version of the feature branch. Take the current one
> instead." Again, it's important that nobody is working off of the commits from the original version of the
> feature branch.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

and states the branch-scoped version of the rule:

> But again, this only works for *private* feature branches. If you're collaborating with other developers
> via the same feature branch, that branch is *public*, and you're not allowed to re-write its history.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

Pro Git's canonical one-liner (the sentence to put in the skill verbatim):

> **Do not rebase commits that exist outside your repository and that people may have based work on.**
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

> If you only ever rebase commits that have never left your own computer, you'll be just fine. If you rebase
> commits that have been pushed, but that no one else has based commits from, you'll also be fine. If you
> rebase commits that have already been pushed publicly, and people may have based work on those commits,
> then you may be in for some frustrating trouble, and the scorn of your teammates.
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

Git's own manual is blunt about the downstream cost:

> Rebasing (or any other form of rewriting) a branch that others have based work on is a bad idea: anyone
> downstream of it is forced to manually fix their history. This section explains how to do the fix from the
> downstream's point of view. The real fix, however, would be to avoid rebasing the upstream in the first
> place.
> — https://git-scm.com/docs/git-rebase (RECOVERING FROM UPSTREAM REBASE)

### 1.2 Merge is the non-destructive option; rebase buys linearity with traceability

> Merging is nice because it's a *non-destructive* operation. The existing branches are not changed in any
> way. This avoids all of the potential pitfalls of rebasing (discussed below).
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

> But, there are two trade-offs for this pristine commit history: safety and traceability. If you don't
> follow the Golden Rule of Rebasing, re-writing project history can be potentially catastrophic for your
> collaboration workflow. And, less importantly, rebasing loses the context provided by a merge commit—you
> can't see when upstream changes were incorporated into the feature.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

The rebase-vs-merge argument is a *history-policy* argument, not a correctness argument — the trees are identical:

> Note that the snapshot pointed to by the final commit you end up with, whether it's the last of the
> rebased commits for a rebase or the final merge commit after a merge, is the same snapshot — it's only the
> history that is different. Rebasing replays changes from one line of work onto another in the order they
> were introduced, whereas merging takes the endpoints and merges them together.
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

Both camps, stated fairly (use this when the skill has to justify a choice instead of dogmatically picking):

> One point of view on this is that your repository's commit history is a **record of what actually
> happened.** It's a historical document, valuable in its own right, and shouldn't be tampered with. […]
> The opposing point of view is that the commit history is the **story of how your project was made.** You
> wouldn't publish the first draft of a book, so why show your messy work? […] Now, to the question of
> whether merging or rebasing is better: hopefully you'll see that it's not that simple.
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

> You can get the best of both worlds: rebase local changes before pushing to clean up your work, but never
> rebase anything that you've pushed somewhere.
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

Operational compromise documented for the PR flow: clean up **before** opening the PR, merge **after**:

> If you use pull requests as part of your code review process, you need to avoid using `git rebase` after
> creating the pull request. As soon as you make the pull request, other developers will be looking at your
> commits, which means that it's a *public* branch. Re-writing its history will make it impossible for Git
> and your teammates to track any follow-up commits added to the feature. Any changes from other developers
> need to be incorporated with `git merge` instead of `git rebase`. For this reason, it's usually a good
> idea to clean up your code with an interactive rebase *before* submitting your pull request.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

and "rebase-then-merge" for a fast-forward integration:

> by performing a rebase before the merge, you're assured that the merge will be fast-forwarded, resulting
> in a perfectly linear history. This also gives you the chance to squash any follow-up commits added during
> a pull request.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

Safety valve for an agent that is not confident:

> If you're not entirely comfortable with `git rebase`, you can always perform the rebase in a temporary
> branch. That way, if you accidentally mess up your feature's history, you can check out the original
> branch and try again.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

### 1.3 Merge early and often: the size of the conflict is a function of elapsed time

> Merging in Git is typically fairly easy. Since Git makes it easy to merge another branch multiple times,
> it means that you can have a very long lived branch but you can keep it up to date as you go, solving
> small conflicts often, rather than be surprised by one enormous conflict at the end of the series.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

> Git's philosophy is to be smart about determining when a merge resolution is unambiguous, but if there is
> a conflict, it does not try to be clever about automatically resolving it. Therefore, if you wait too long
> to merge two branches that diverge quickly, you can run into some issues.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

Thoughtworks Technology Radar, **Hold** rating on long-lived branches (this is the institutional verdict):

> A merge is a merge. Regardless of the source control tool or pattern you use. If you wait more than a day
> or two to merge, you could hit a big merge conflict. This becomes a real issue if you have a larger team.
> If you have more than a few people waiting to merge, you can have a serious a bottleneck. Introducing
> patterns like Gitflow require the discipline to merge often to be successful.
> — https://www.thoughtworks.com/en-de/radar/techniques/long-lived-branches-with-gitflow

> Essentially, long-lived branches are the opposite of continuously integrating all changes to the source
> code, and in our experience continuous integration is the better approach for most kinds of software
> development.
> — https://www.thoughtworks.com/en-de/radar/techniques/long-lived-branches-with-gitflow

Trunk-Based Development reference (Paul Hammant) — the branch-lifetime budget, stated as a rule:

> A source-control branching model, where developers collaborate on code in a single branch called 'trunk'*
> and resist any pressure to create other long-lived development branches by employing documented
> techniques. They therefore avoid merge hell, do not break the build, and live happily ever after.
> — https://trunkbaseddevelopment.com/

> The short-lived feature branch should only last a day or two and never diverge from the trunk enough so
> that a merge back is problematic. After the seal of approval from code reviewers and CI daemons, it should
> be merged back into the trunk. It should be deleted, as proof of convergence.
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

> Shared branches off mainline/main/trunk are bad at any release cadence
> — https://trunkbaseddevelopment.com/ (section heading)

> Super scaled is merge/patch queues of course
> — https://trunkbaseddevelopment.com/

Also a specific anti-drift rule that applies to agents collaborating on branches:

> If there is more that one developer (and the developer's pairing partner, or the developer's own coding
> agents) on the same short-lived feature branch, then that branch is at risk of not being short-lived.
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

### 1.4 A merge commit's job is integration — do not invent behavior in it

This is the doctrine; git documents it as an explicit prohibition on the `--no-commit` escape hatch:

> With `--no-commit` perform the merge and stop just before creating a merge commit, to give the user a
> chance to inspect and further tweak the merge result before committing. […] You should refrain from
> abusing this option to sneak substantial changes into a merge commit. Small fixups like bumping
> release/version name would be acceptable.
> — https://git-scm.com/docs/git-merge

The reviewer-side tooling for auditing that nothing was invented is the combined diff (§1.8) and the "narrow
resolution" instruction from the agent literature:

> Keep the resolution narrow. Avoid unrelated formatting, dependency updates, or refactors that make the
> merged behavior harder to inspect. Run formatters only where repository instructions require them.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

> The merge commit's job is integration" — cross-reference: the Linus doctrine is covered by the internals
> agent; the *observable* form of it in primary sources is the `--no-commit` warning above plus the evil
> merge definition in §2.1.

Also, the merge message is part of the audit trail, not decoration:

> Invoke an editor before committing successful mechanical merge to further edit the auto-generated merge
> message, so that the user can explain and justify the merge. The `--no-edit` option can be used to accept
> the auto-generated message (this is generally discouraged).
> — https://git-scm.com/docs/git-merge

(For an autonomous agent, `--no-edit` is usually unavoidable; the compensating control is to state the
resolution decisions in the PR body — §4.)

### 1.5 Neither side is authoritative. The merge base plus both intents are

Git's own framing of why a conflict exists:

> Among the changes made to the common ancestor's version, non-overlapping ones […] are incorporated in the
> final result verbatim. When both sides made changes to the same area, however, Git cannot randomly pick
> one side over the other, and asks you to resolve it by leaving what both sides did to that area.
> — https://git-scm.com/docs/git-merge

> Conflicts generally arise when two people have changed the same lines in a file, or if one developer
> deleted a file while another developer was modifying it. In these cases, Git cannot automatically
> determine what is correct. […] It is then the developers' responsibility to resolve the conflict.
> — https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts

Why the default two-way view is insufficient — the base must be shown:

> The default format does not show what the original said in the conflicting area. You cannot tell how many
> lines are deleted and replaced with Barbie's remark on your side. The only thing you can tell is that your
> side wants to say it is hard and you'd prefer to go shopping, while the other side wants to claim it is
> easy. […] You can sometimes come up with a better resolution by viewing the original.
> — https://git-scm.com/docs/git-merge

> In addition to the <<<<<<<, =======, and >>>>>>> markers, it uses another ||||||| marker that is followed
> by the original text.
> — https://git-scm.com/docs/git-merge (diff3/zdiff3)

So the standing instruction is: `git config merge.conflictStyle zdiff3` (or `diff3`) before resolving
anything, and remember the index carries all three sides:

> Stage 1 is the common ancestor, stage 2 is your version and stage 3 is from the `MERGE_HEAD`, the version
> you're merging in ("theirs").
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

### 1.6 Recover the *intent* of each side before editing (the actual methodology)

> Another useful tool when resolving merge conflicts is `git log`. This can help you get context on what may
> have contributed to the conflicts. Reviewing a little bit of history to remember why two lines of
> development were touching the same area of code can be really helpful sometimes.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

> We can further simplify this though to give us much more specific context. If we add the `--merge` option
> to `git log`, it will only show the commits in either side of the merge that touch a file that's currently
> conflicted. […] If you run that with the `-p` option instead, you get just the diffs to the file that ended
> up in conflict. This can be **really** helpful in quickly giving you the context you need to help
> understand why something conflicts and how to more intelligently resolve it.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

The manual lists the same inspection set:

> Look at the diffs. `git diff` will show a three-way diff, highlighting changes from both the `HEAD` and
> `MERGE_HEAD` versions. `git diff AUTO_MERGE` will show what changes you've made so far to resolve textual
> conflicts. • Look at the diffs from each branch. `git log --merge -p <path>` will show diffs first for the
> `HEAD` version and then the `MERGE_HEAD` version. • Look at the originals. `git show :1:filename` shows
> the common ancestor, `git show :2:filename` shows the `HEAD` version, and `git show :3:filename` shows the
> `MERGE_HEAD` version.
> — https://git-scm.com/docs/git-merge (HOW TO RESOLVE CONFLICTS)

And the same "intent, not text" rule stated for AI agents, plus what extra context the agent needs:

> Read both sides and the common ancestor before editing. The base shows what each branch changed, while
> tests and call sites reveal the contract those edits were meant to preserve. For a renamed function plus a
> new validation rule, the correct result may combine the new name with the new check. Choosing one side
> wholesale would silently discard valid work.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

> Give the agent the pull request description, acceptance criteria, recent changes to the affected files,
> and relevant ownership rules. Generated files need their source identified. Lockfiles need the package
> manager and approved regeneration command. Database schemas and API definitions need compatibility
> requirements, not just syntax checks.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

Commercial automation states intent-analysis as its core mechanism (independent corroboration of the same
framing): "For each file, it determines what problem the changes on each branch were solving (not just what
changed, but why), so the resolution reflects the actual goals of both sides."
— https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md

### 1.7 Tests are the arbiter, because a clean textual resolution proves nothing

> Review the final code even when the unresolved conflict count is zero. Resolving a textual conflict does
> not establish that the code works.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

> Accepting both does not guarantee valid code. You might still need to remove duplicates or combine the
> logic manually.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

> First, resolve and save every conflicting file, then stage the resolutions. Inspect the staged diff and
> run the relevant tests before continuing.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

Fowler's argument for why tests are the only real defence (and why the "merge" step is where they pay):

> By a semantic conflict I mean a situation where Jez and I make changes which can be safely merged on a
> textual level but cause the program to behave differently […] The first of these is SelfTestingCode. Tests
> are effectively probing our code to see if their view of the code's semantics are consistent with what the
> code actually does. If Jez is expecting certain things to happen with the code he's calling and has tests
> for that, then they will break when he integrates. […] The other technique that helps is to merge more
> often.
> — https://martinfowler.com/bliki/SemanticConflict.html

> So the first point here is that however powerful your tooling is, it will only protect you from textual
> conflicts. The particularly annoying point is that semantic conflicts are harder to spot and harder to fix.
> — https://martinfowler.com/bliki/SemanticConflict.html

The concrete validation recipe for an agent:

> Search for conflict markers, inspect the staged diff, and run the smallest tests that exercise both
> branches' intent. Then run the repository's required broader checks. A merge involving authentication
> should cover allowed and denied paths. A lockfile conflict should include a fresh install or integrity
> check. A generated client should be rebuilt from its schema.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

### 1.8 Audit your own resolution (and later, everyone else's) with the combined diff

> If we resolve the conflict and run `git diff` again, we'll see the same thing, but it's a little more
> useful. […] This shows us that "hola world" was in our side but not in the working copy, that "hello
> mundo" was in their side but not in the working copy and finally that "hola mundo" was not in either side
> but is now in the working copy. This can be useful to review before committing the resolution.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

> You can also get this from the `git log` for any merge to see how something was resolved after the fact.
> Git will output this format if you run `git show` on a merge commit, or if you add a `--cc` option to a
> `git log -p` (which by default only shows patches for non-merge commits).
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

The per-side review commands, which answer "what did *this merge* introduce":

> To compare your result to what you had in your branch before the merge, in other words, to see what the
> merge introduced, you can run `git diff --ours` […] If we want to see how the result of the merge differed
> from what was on their side, you can run `git diff --theirs`. […] Finally, you can see how the file has
> changed from both sides with `git diff --base`.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

### 1.9 Start clean, or you lose the ability to back out

> First of all, if at all possible, try to make sure your working directory is clean before doing a merge
> that may have conflicts. If you have work in progress, either commit it to a temporary branch or stash it.
> This makes it so that you can undo **anything** you try here. If you have unsaved changes in your working
> directory when you try a merge, some of these tips may help you preserve that work.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

Git issues an explicit **Warning** in the manual:

> Running `git merge` with non-trivial uncommitted changes is discouraged: while possible, it may leave you
> in a state that is hard to back out of in the case of a conflict.
> — https://git-scm.com/docs/git-merge

> Before applying outside changes, you should get your own work in good shape and committed locally, so it
> will not be clobbered if there are conflicts. […] To avoid recording unrelated changes in the merge
> commit, `git pull` and `git merge` will also abort if there are any changes registered in the index
> relative to the `HEAD` commit.
> — https://git-scm.com/docs/git-merge (PRE-MERGE CHECKS)

The `--autostash` convenience has a documented bite:

> use with care: the final stash application after a successful merge might result in non-trivial conflicts.
> — https://git-scm.com/docs/git-merge

Atlassian's classification of the two failure points is useful for an agent's triage step:

> A merge will fail to start when Git sees there are changes in either the working directory or staging area
> of the current project. […] The local state will need to be stabilized using `git stash`, `git checkout`,
> `git commit` or `git reset`.
> — https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts

### 1.10 Know which operation you are in, and prefer abort over improvisation

> The `git merge --abort` option tries to revert back to your state before you ran the merge. The only cases
> where it may not be able to do this perfectly would be if you had unstashed, uncommitted changes in your
> working directory when you ran it, otherwise it should work fine.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

> Aborting removes the conflict-resolution work for that operation. Copy any edits you want to keep first.
> Git attempts to restore the pre-operation state, but might not be able to reconstruct uncommitted changes
> that existed before the operation.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

> Conflicts can occur during a merge, pull, rebase, cherry-pick, or stash restore. The file resolution tools
> are similar, but the meaning of each side and the steps to finish depend on the operation.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

> If you are unsure which operation is active, run `git status` in the repository's terminal for Git's
> current state and next action.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

Finishing differs per operation (a table worth reproducing in the skill):

| Operation | How to finish |
| --- | --- |
| Merge (incl. merging pull) | merge commit message + **Commit** |
| Rebase (incl. **Pull (Rebase)**) | `git rebase --continue`; "Git might stop at another conflicting commit" |
| Cherry-pick | `git cherry-pick --continue`; "Repeat if a sequence of commits encounters more conflicts" |
| Stash restore | "Review the restored files and commit them when ready. A stash conflict does not require a merge commit." |
— https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

### 1.11 `--ours` / `--theirs` swap during rebase: never pick a side by name

The man page is unambiguous, and gives the reason:

> Note that during `git rebase` and `git pull --rebase`, `ours` and `theirs` may appear swapped; `--ours`
> gives the version from the branch the changes are rebased onto, while `--theirs` gives the version from the
> branch that holds your work that is being rebased. This is because `rebase` is used in a workflow that
> treats the history at the remote as the shared canonical one, and treats the work done on the branch you
> are rebasing as the third-party work to be integrated, and you are temporarily assuming the role of the
> keeper of the canonical history during the rebase.
> — https://git-scm.com/docs/git-checkout

> Note that a rebase merge works by replaying each commit from the working branch on top of the *<upstream>*
> branch. Because of this, when a merge conflict happens, the side reported as *ours* is the so-far rebased
> series, starting with *<upstream>*, and *theirs* is the working branch. In other words, the sides are
> swapped.
> — https://git-scm.com/docs/git-rebase

> During a rebase, Git's 'ours' and 'theirs' roles are reversed from what you might expect: 'ours' is the
> new base and 'theirs' is your replayed work. Inspect the changes rather than choosing a side by name.
> — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

Verified locally in §6/A: with `feature` rebased onto `main`, `git show :2:f.txt` = `MAIN-INTENT` (i.e.
`--ours`) and `:3:f.txt` = `FEATURE-INTENT` (`--theirs`).

### 1.12 Side-taking flags are policy decisions — write the policy down, in the right place

Ways to take one side, from least to most destructive, all documented:

* Whole-file checkout during a conflict:

> The `git checkout` command can also take `--ours` and `--theirs` options, which can be a really fast way of
> just choosing either one side or the other without merging things at all. This can be particularly useful
> for conflicts of binary files where you can simply choose one side, or where you only want to merge certain
> files in from another branch — you can do the merge and then checkout certain files from one side or the
> other before committing.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

* Strategy option for conflicted hunks only:

> This option forces conflicting hunks to be auto-resolved cleanly by favoring *our* version. Changes from
> the other tree that do not conflict with our side are reflected in the merge result. For a binary file, the
> entire contents are taken from our side. This should not be confused with the `ours` merge strategy, which
> does not even look at what the other tree contains at all. It discards everything the other tree did,
> declaring *our* history contains all that happened in it.
> — https://git-scm.com/docs/git-merge

* The fake merge (strategy `-s ours`) — legitimate only as a bookkeeping device:

> This will basically do a fake merge. It will record a new merge commit with both branches as parents, but
> it will not even look at the branch you're merging in. It will simply record as the result of the merge the
> exact code in your current branch. […] This can often be useful to basically trick Git into thinking that a
> branch is already merged when doing a merge later on.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

* Per-path policy in `.gitattributes`, which is the *declared*, reviewable version of the same idea:

> You can also use Git attributes to tell Git to use different merge strategies for specific files in your
> project. One very useful option is to tell Git to not try to merge specific files when they have conflicts,
> but rather to use your side of the merge over someone else's. […] `database.xml merge=ours` […] In this
> case, `database.xml` stays at whatever version you originally had.
> — https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes

> You have to be careful, though, because the `.gitattributes` file is committed and passed around with the
> project, but the driver […] isn't, so it won't work everywhere. When you design these filters, they should
> be able to fail gracefully and have the project still work properly.
> — https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes

### 1.13 Cherry-pick is a partial merge, not a merge — and it duplicates history

> `git cherry-pick` is a useful tool but not always a best practice. Cherry picking can cause duplicate
> commits and many scenarios where cherry picking would work, traditional merges are preferred instead.
> — https://www.atlassian.com/git/tutorials/cherry-pick

> Cherry picking is a powerful and convenient command that is incredibly useful in a few scenarios. Cherry
> picking should not be misused in place of `git merge` or `git rebase`.
> — https://www.atlassian.com/git/tutorials/cherry-pick

Legitimate uses named by the same page: grabbing one shared commit between collaborators, lifting an
isolated bugfix commit to `main` as a hotfix, and resurrecting commits from a closed PR
("Git never loses those commits and through commands like git log and git reflog they can be found and
cherry picked back to life.").

Mechanics:

> Given one or more existing commits, apply the change each one introduces, recording a new commit for each.
> This requires your working tree to be clean (no modifications from the HEAD commit).
> — https://git-scm.com/docs/git-cherry-pick

> An evil merge… [no] — cherry-picking glossary definition: "In SCM jargon, 'cherry pick' means to choose a
> subset of changes out of a series of changes (typically commits) and record them as a new series of changes
> on top of a different codebase."
> — https://git-scm.com/docs/gitglossary

**`-x` provenance marker** — and its documented conditions:

> When recording the commit, append a line that says "(cherry picked from commit …)" to the original commit
> message in order to indicate which commit this change was cherry-picked from. This is done only for cherry
> picks without conflicts. Do not use this option if you are cherry-picking from your private branch because
> the information is useless to the recipient. If on the other hand you are cherry-picking between two
> publicly visible branches (e.g. backporting a fix to a maintenance branch for an older release from a
> development branch), adding this information can be useful.
> — https://git-scm.com/docs/git-cherry-pick

Empirical deviation from that sentence is recorded in §6/E (git 2.46.2 still wrote the trailer after a
conflicted resolution) — so `-x` is a *hint*, and patch-id (§1.14) is the reliable detector.

Cherry-picking **a merge** requires declaring the mainline:

> Usually you cannot cherry-pick a merge because you do not know which side of the merge should be considered
> the mainline. This option specifies the parent number (starting from 1) of the mainline and allows
> cherry-pick to replay the change relative to the specified parent.
> — https://git-scm.com/docs/git-cherry-pick

Duplicate work is detected and can be dropped rather than re-applied:

> `--empty=(drop|keep|stop)`: How to handle commits being cherry-picked that are redundant with changes
> already in the current history.
> — https://git-scm.com/docs/git-cherry-pick

The documented bail-out sequence when the patch no longer fits (note the `-Xpatience` retry):

> The following sequence attempts to backport a patch, bails out because the code the patch applies to has
> changed too much, and then tries again, this time exercising more care about matching up context lines.
> `git cherry-pick topic^` … `git diff` … `git cherry-pick --abort` … `git cherry-pick -Xpatience topic^`
> — https://git-scm.com/docs/git-cherry-pick (EXAMPLES; "spending extra time to avoid mistakes based on
> incorrectly matching context lines")

### 1.14 How git knows "the same change already exists over there" — patch-id (dedup, not ancestry)

> A "patch ID" is nothing but a sum of SHA-1 of the file diffs associated with a patch, with line numbers
> ignored. As such, it's "reasonably stable", but at the same time also reasonably unique, i.e., two patches
> that have the same "patch ID" are almost guaranteed to be the same thing. The main usecase for this command
> is to look for likely duplicate commits.
> — https://git-scm.com/docs/git-patch-id

> Determine whether there are commits in *<head>*..*<upstream>* that are equivalent to those in the range
> *<limit>*..*<head>*. The equivalence test is based on the diff, after removing whitespace and line numbers.
> git-cherry therefore detects when commits have been "copied" by means of git-cherry-pick[1], git-am[1] or
> git-rebase[1]. Outputs the SHA1 of every commit in *<limit>*..*<head>*, prefixed with `-` for commits that
> have an equivalent in <upstream>, and `+` for commits that do not.
> — https://git-scm.com/docs/git-cherry

> we see that the commits A and C (marked with `-`) can be dropped from your `topic` branch when you rebase
> it on top of `origin/master`, while the commit B (marked with `+`) still needs to be kept
> — https://git-scm.com/docs/git-cherry

Rebase consumes this automatically — which is why rebase does *not* duplicate already-landed work, and why
the dedup is the safety net after someone force-pushes:

> Make a list of all commits on your current branch since it branched off from *<upstream>* that do not have
> an equivalent commit in *<upstream>*.
> — https://git-scm.com/docs/git-rebase (DESCRIPTION, step 1)

> commits which are clean cherry-picks (as determined by `git log --cherry-mark` ...) are detected and
> dropped as a preliminary step (unless `--reapply-cherry-picks` or `--keep-base` is passed)
> — https://git-scm.com/docs/git-rebase (`--empty`)

> the fix is easy because *git rebase* knows to skip changes that are already present in the new upstream
> (unless `--reapply-cherry-picks` is given)
> — https://git-scm.com/docs/git-rebase (RECOVERING FROM UPSTREAM REBASE, the easy case)

The limit of the mechanism (this is why duplicated history still happens in practice):

> This only works if `C4` and `C4'` that your partner made are almost exactly the same patch. Otherwise the
> rebase won't be able to tell that it's a duplicate and will add another `C4`-like patch (which will
> probably fail to apply cleanly, since the changes would already be at least somewhat there).
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

> Only works if the changes (patch IDs based on the diff contents) on *subsystem* are literally the same
> before and after the rebase *subsystem* did.
> — https://git-scm.com/docs/git-rebase

Practical audit recipe for "did this commit already land on the other branch?" is `git cherry -v upstream head`
(and `git log --cherry-mark`), which an agent should run **before** cherry-picking a range from a diverged branch.

### 1.15 Fork-point protection — the mechanism behind "rebase didn't eat my commits"

> Use reflog to find a better common ancestor between *<upstream>* and *<branch>* when calculating which
> commits have been introduced by *<branch>*. […] If *<upstream>* or `--keep-base` is given on the command
> line, then the default is `--no-fork-point`, otherwise the default is `--fork-point`.
> — https://git-scm.com/docs/git-rebase

Consequence for scripting (an agent running `git rebase origin/main topic` silently loses the protection):

an explicit `<upstream>` argument switches the default to `--no-fork-point`. `--fork-point` is what makes
`git rebase` (no args, tracked upstream) drop commits that the upstream has already discarded; the
counterpart for "keep my base where it was" is:

> This option is useful in the case where one is developing a feature on top of an upstream branch. While the
> feature is being worked on, the upstream branch may advance and it may not be the best idea to keep
> rebasing on top of the upstream but to keep the base commit as-is.
> — https://git-scm.com/docs/git-rebase (`--keep-base`)

And ORIG_HEAD is *not* a reliable escape hatch mid-rebase:

> When starting the rebase, `ORIG_HEAD` is set to point to the commit at the tip of the to-be-rebased branch.
> However, `ORIG_HEAD` is not guaranteed to still point to that commit at the end of the rebase if other
> commands that change `ORIG_HEAD` (like `git reset`) are used during the rebase. The previous branch tip,
> however, is accessible using the reflog of the current branch (i.e. `@{1}`).
> — https://git-scm.com/docs/git-rebase

### 1.16 Force-push: the lease is the minimum bar

> Usually, `git push` refuses to update a remote ref that is not an ancestor of the local ref used to
> overwrite it. This option overrides this restriction if the current value of the remote ref is the expected
> value. `git push` fails otherwise. Imagine that you have to rebase what you have already published. You
> will have to bypass the "must fast-forward" rule in order to replace the history you originally published
> with the rebased history. If somebody else built on top of your original history while you are rebasing,
> the tip of the branch at the remote may advance with their commit, and blindly pushing with `--force` will
> lose their work. […] It is like taking a "lease" on the ref without explicitly locking it, and the remote
> ref is updated only if the "lease" is still valid.
> — https://git-scm.com/docs/git-push

Atlassian's phrasing of the same hazard for beginners:

> If you try to push the rebased `main` branch back to a remote repository, Git will prevent you from doing
> so because it conflicts with the remote `main` branch. But, you can force the push to go through by passing
> the `--force` flag […] This overwrites the remote `main` branch to match the rebased one from your
> repository and makes things very confusing for the rest of your team. So, be very careful to use this
> command only when you know exactly what you're doing.
> — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

### 1.17 The merge method is a history-policy decision, and the platform documents the trade

> Merge commit — Preserves every commit from the pull request branch and adds an explicit merge point.
> Squash and merge — Combines all commits in the pull request into a single commit on the base branch.
> Rebase and merge — Adds each commit onto the base branch without a merge commit, for a linear history.
> — https://docs.github.com/en/pull-requests/reference/pull-request-merges

> When you click the default **Merge pull request** option on a pull request, all commits from the feature
> branch are added to the base branch in a merge commit. The pull request is merged using the [`--no-ff`
> option](https://git-scm.com/docs/git-merge#_fast_forward_merge).
> — https://docs.github.com/en/pull-requests/reference/pull-request-merges

> The tradeoff is that intermediate commits from the pull request are not preserved as separate commits on
> the base branch.
> — https://docs.github.com/en/pull-requests/reference/pull-request-merges

GitHub's rebase-and-merge is *not* `git rebase` — relevant when a skill says "rebase it":

> Always updates the committer information and creates new commit SHAs, whereas `git rebase` does not change
> the committer information when the rebase happens on top of an ancestor commit. • Drops commits that were
> empty to begin with, such as those created with `git commit --allow-empty`, whereas `git rebase` keeps
> originally-empty commits by default.
> — https://docs.github.com/en/pull-requests/reference/pull-request-merges

`--no-ff` / `--ff-only` semantics for recording an integration point:

> With `--no-ff`, create a merge commit in all cases, even when the merge could instead be resolved as a
> fast-forward. With `--ff-only`, resolve the merge as a fast-forward when possible. When not possible,
> refuse to merge and exit with a non-zero status.
> — https://git-scm.com/docs/git-merge

### 1.18 "Merge master into my branch forever" and squash-then-keep-working are named failure loops

GitHub documents the loop the user asked about (dirty PR after merging base into head, and after squashing):

> Squash merging works best for short-lived branches. If you keep working on the same head branch after a
> squash merge, later pull requests can include commits that were already squashed into the base branch. This
> can make merge conflicts more likely and can force you to resolve the same conflicts more than once. For
> long-running branches, consider using a merge commit or rebasing the branch before opening the next pull
> request.
> — https://docs.github.com/en/pull-requests/reference/pull-request-merges

> Resolving conflicts on GitHub merges the entire base branch into the head branch. If the head branch is the
> default or protected branch, you may be prompted to create a new head branch.
> — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-on-github
> (and: "After you've resolved all your merge conflicts, click **Commit merge**. This merges the entire base
> branch into your head branch.")

The same doc names the "update branch" cycle as merging the whole base in — i.e. the PR diff direction
surprise. The anti-clutter alternative, with Linus's complaint as recorded by git itself:

> When your topic branch is long-lived, however, your topic branch would end up having many such "Merge from
> master" commits on it, which would unnecessarily clutter the development history. Readers of the Linux
> kernel mailing list may remember that Linus complained about such too frequent test merges when a subsystem
> maintainer asked to pull from a branch full of "useless merges".
> — https://git-scm.com/docs/git-rerere (DISCUSSION)

### 1.19 `rerere`: reuse your own judgement, but re-verify it

> In a workflow employing relatively long lived topic branches, the developer sometimes needs to resolve the
> same conflicts over and over again until the topic branches are done (either merged to the "release"
> branch, or sent out and accepted upstream). This command assists the developer in this process by
> recording conflicted automerge results and corresponding hand resolve results on the initial manual merge,
> and applying previously recorded hand resolutions to their corresponding automerge results.
> — https://git-scm.com/docs/git-rerere

> Note that *git rerere* leaves the index file alone, so you still need to do the final sanity checks with
> `git diff` (or `git diff -c`) and *git add* when you are satisfied.
> — https://git-scm.com/docs/git-rerere

> *git rerere* relies on the conflict markers in the file to detect the conflict. If the file already
> contains lines that look the same as lines with conflict markers, *git rerere* may fail to record a
> conflict resolution.
> — https://git-scm.com/docs/git-rerere ([NOTE], workaround: `conflict-marker-size` in gitattributes)

The audit-friendly switch:

> `--no-rerere-autoupdate` is a good way to double-check what git-rerere[1] did and catch potential
> mismerges, before committing the result to the index with a separate git-add[1].
> — https://git-scm.com/docs/git-merge and https://git-scm.com/docs/git-rebase

And the agent-facing verdict on reusing recorded resolutions:

> Repeated conflicts may benefit from Git's recorded resolution mechanism, which stores a manual resolution
> and can reuse it when the same conflict appears again. Treat the reused result as a starting point. Changes
> around the conflict can make an old resolution incomplete even when Git applies it cleanly.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

Fowler, from the other side: identical-text collisions are exactly what tooling can't fix "unless you have
something like git rerere. But that problem is much smaller than semantic conflicts."
— https://martinfowler.com/bliki/SemanticConflict.html (note 1)

### 1.20 Reflog is the safety net for everything local — and it is local, temporary, and unshared

> Git keeps track of updates to the tip of branches using a mechanism called reference logs, or "reflogs."
> — https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog

> Git never really loses anything, even when performing history rewriting operations like rebasing or commit
> amending.
> — https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog

> We can see there are reflog entries for the start and finish of the `rebase` and prior to those is our
> "some WIP changes" commit. We can pass the reflog ref to `git reset` and reset to a commit that was before
> the rebase. `git reset HEAD@{2}`
> — https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog

> Reflogs are stored in directories under the local repository's `.git` directory.
> — https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog (i.e. not pushed anywhere)

> The `expire` subcommand has potential for data loss. […] By default, the reflog expiration date is set to
> 90 days.
> — https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog

Git's own detached-HEAD guidance points at the same tool for recovery: "If we have moved away from commit
`f`, then we must first recover its object name (typically by using git reflog)"
— https://git-scm.com/docs/git-checkout (DETACHED HEAD).

### 1.21 Scale: the queue exists because per-PR testing cannot prove the merged state

> Bors is a GitHub bot that prevents merge skew / semantic merge conflicts, so when a developer checks out
> the main branch, they can expect all of the tests to pass out-of-the-box. […] Bors merges your pull request
> into a staging area, and runs your automated test suite. If the staging branch passes, then it is copied to
> the main branch.
> — https://bors.tech/

> The cool part of separating the merging from the publishing is that the exact integration of pull requests
> that end up in the main branch have already been tested before any developers try to work on it or users
> try to deploy it. It means less reverting commits after merging them, less hunting down others' mistakes
> before being able to do any of your own work.
> — https://bors.tech/

The quantified notion, worth stealing as a vocabulary term for the skill:

> The term "merge skew" is defined as "the number of commits on a trunk branch, ahead of the merge base of a
> merging code change." Said more simply, the merge skew for a pull request is how many other changes have
> merged since it was created or last rebased.
> — https://graphite.com/guides/merge-skew

> While merge conflicts can be cheaply checked for at the exact time of the merge, semantic conflicts would
> require re-running tens of minutes of CI, during which yet more changes might merge.
> — https://graphite.com/guides/merge-skew

> When CI passes on a pull request, it validates the change's original merge base commit and the author's new
> code change. That is a different snapshot of code compared to the codebase immediately after the change is
> merged into trunk — unless the change has just been rebased and has a merge skew of zero.
> — https://graphite.com/guides/merge-skew

The pre-integration build duty (small teams, no queue):

> teams perform a full "pre integrate" build (compile, unit tests, integration tests) on their dev
> workstations before committing/pushing for others (or bots) to see.
> — https://trunkbaseddevelopment.com/

> If you have more than a couple of developers on the project, you are going to need to hook up a build
> server to verify that their commits have **not broken the build** after they land in the trunk, and also
> when they are ready to be merged back into the trunk from a short-lived feature branch.
> — https://trunkbaseddevelopment.com/

### 1.22 Direction rules between release/maintenance branches (where cherry-pick is *correct*)

> Bugs should be reproduced and fixed on the trunk, and then **cherry-picked** to the release branch. A build
> should happen from that, a second confirmation that the issue has been remediated, and that deployment
> should go live (perhaps a point release). If you can not reproduce bugs on the trunk (truly rare), then you
> have permission to go ahead and reproduce it on the release branch, fix it there, and merge back.
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

> But, if you are fixing bugs on the release branch and merging them down to the trunk you are doing it wrong.
> There is a chance you might forget to merge it down, and then there is going to be a regression at the next
> release moment (fresh branch cut from the trunk). Then egg on face, and recriminations.
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

> We only merge from trunk to release branches (if we branch at all), and then only a small percentage of the
> commits to trunk, and only using the cherry-pick method of merging.
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

> Cherry-picking every commit since the branch-cut to the branch from the trunk is the same thing of course.
> (heading: "Merging rather than cherry-pick to/from a release branch")
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

The `-x` marker's raison d'être is exactly this flow (§1.13): "backporting a fix to a maintenance branch for
an older release from a development branch".

---

## 2. Anti-pattern catalog

Format: **name** — what happens / why it is wrong / source.

### 2.1 Evil merge (merge that invents content) — and its malicious use

Definition (git's own glossary):

> An evil merge is a merge that introduces changes that do not appear in any parent.
> — https://git-scm.com/docs/gitglossary

Real incident (single-source practitioner report, 2026; treated as an anecdote — see §7): obfuscated code
committed *inside* a merge commit on `vite.config.js`, invisible to PR review, live ~3.5 months:

> The contributor who clicked "merge" in the PR added code that wasn't in either branch. Git recorded it as a
> normal merge commit, and nobody looked twice.
> — https://dev.to/fimskiy/evil-merge-the-git-attack-that-hid-malware-in-plain-sight-for-35-months-48mk

> GitHub doesn't show merge commit diffs in PRs. The PR review showed the branch changes, which were clean.
> The actual injection happened in the merge step, which nobody reviews because... why would you? It's just
> merging. `git log` shows the merge but not what changed in it. You'd need `git diff <parent1>..<merge>` to
> see it, and nobody runs that routinely.
> — same source

Detection recipe (the honest, mechanical one — reconstruct the expected tree and compare):

> The idea is simple: for every merge commit, reconstruct what git *should* have produced — a clean
> three-way merge of the two parent trees using the common ancestor — and compare it against what the merge
> commit *actually* contains. Any difference means someone edited files during the merge.
> — same source; the same page notes "Git itself has `git show --remerge-diff` which can surface the
> problem, but it requires manual inspection per commit."

The *benign* version is also real (semantic conflicts force hand edits in a merge), which is why the rule is
"declare it in the merge message", not "never do it": Pro Git's combined-diff walkthrough (§1.8) exists
precisely to review a resolution that produced text in neither parent:

> "hola mundo" was not in either side but is now in the working copy. This can be useful to review before
> committing the resolution.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

**Why it is dangerous:** the diff a reviewer looks at is the branch diff, not the merge commit; `git log -p`
skips merge diffs unless `--cc`/`-c` is given (§1.8).
**Agent rule derived:** never add content to a merge/rebase resolution that is not a conflict resolution,
and enumerate every hunk that appears in neither parent in the commit/PR description.

### 2.2 Rebasing (or amending, or `reset`) a branch others built on → duplicated history and a ripple

> If you push commits somewhere and others pull them down and base work on them, and then you rewrite those
> commits with `git rebase` and push them up again, your collaborators will have to re-merge their work and
> things will get messy when you try to pull their work back into yours.
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

> If you run a `git log` when your history looks like this, you'll see two commits that have the same author,
> date, and message, which will be confusing. Furthermore, if you push this history back up to the server,
> you'll reintroduce all those rebased commits to the central server, which can further confuse people.
> — https://git-scm.com/book/en/v2/Git-Branching-Rebasing

> If you now continue development as usual, and eventually merge *topic* to *subsystem*, the commits from
> *subsystem* will remain duplicated forever […] This becomes a ripple effect: anyone downstream from
> *topic* is forced to rebase too, and so on!
> — https://git-scm.com/docs/git-rebase

Atlassian's version of the same arithmetic: "The only way to synchronize the two `main` branches is to merge
them back together, resulting in an extra merge commit *and* two sets of commits that contain the same
changes (the original ones, and the ones from your rebased branch). Needless to say, this is a very confusing
situation." — https://www.atlassian.com/git/tutorials/merging-vs-rebasing

### 2.3 `--ours`/`--theirs` inversion during rebase — "I deleted my own feature with one flag"

See §1.11 (three primary sources) + local probe §6/A.
**Agent rule:** never resolve by side *name*. Resolve by side *identity*: read the labels, or diff against
the recorded base commit SHAs. VS Code's UI labels ("Current"/"Incoming") exist for exactly this reason and
still warn: "'Current' does not always mean your original feature branch."
— https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

### 2.4 Reverting a merge does not undo it — the re-merge silently under-delivers

The user report preserved in git's own howto (a genuine failure story):

> I have a master branch. We have a branch off of that that some developers are doing work on. They claim it
> is ready. We merge it into the master branch. It breaks something so we revert the merge. They make changes
> to the code. they get it to a point where they say it is ok and we merge again. When examined, we find that
> code changes made before the revert are not in the master branch, but code changes after are in the master
> branch.
> — https://raw.githubusercontent.com/git/git/master/Documentation/howto/revert-a-faulty-merge.adoc

Linus's explanation (the doctrine; internals agent may cross-reference):

> But reverting a merge commit also undoes the *data* that the commit changed, but it does absolutely nothing
> to the effects on *history* that the merge had. So the merge will still exist, and it will still be seen as
> joining the two branches together, and future merges will see that merge as the last shared state - and the
> revert that reverted the merge brought in will not affect that at all. […] Yes, it undoes the data, but no,
> it doesn't undo history.
> — same URL

And the second-order trap — the reflexive "revert the revert" is wrong half the time:

> There will be a lot of overlapping changes that result in conflicts. So do not do "revert of revert"
> blindly without thinking..
> — same URL

Decision rule from the same document:

> If the faulty side branch was fixed by adding corrections on top, then doing a revert of the previous
> revert would be the right thing to do. • If the faulty side branch whose effects were discarded by an
> earlier revert of a merge was rebuilt from scratch (i.e. rebasing and fixing …) then re-merging the result
> without doing anything else fancy would be the right thing to do.
> — same URL

Workflow cost:

> When you have a problem you are chasing down, and you hit a "revert this merge", what you're hitting is
> essentially a single commit that contains all the changes (but obviously in reverse) of all the commits
> that got merged. So it's debugging hell […] So from a technical angle, there's nothing wrong with reverting
> a merge, but from a workflow angle it's something that you generally should try to avoid. If at all
> possible, for example, if you find a problem that got merged into the main tree, rather than revert the
> merge, try *really* hard to bisect the problem down into the branch you merged, and just fix it, or try to
> revert the individual commit that caused it.
> — same URL

Pro Git's shorter version of the mechanism:

> The new commit `^M` has exactly the same contents as `C6`, so starting from here it's as if the merge never
> happened, except that the now-unmerged commits are still in `HEAD`'s history. Git will get confused if you
> try to merge `topic` into `master` again: `Already up-to-date.`
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

Escape hatch when the branch was rebuilt: recreate it with all-new commits so the merge base moves —

> You may find this helpful after reverting a topic branch merge, as this option recreates the topic branch
> with fresh commits so it can be remerged successfully without needing to "revert the reversion"
> — https://git-scm.com/docs/git-rebase (`--force-rebase`; the howto spells it `git rebase [-i] --no-ff P`)

Locally reproduced in §6/B.

### 2.5 Silent resurrection: a change reverted on one side reappears after the merge

> With the strategies that use 3-way merge (including the default, `ort`), if a change is made on both
> branches, but later reverted on one of the branches, that change will be present in the merged result; some
> people find this behavior confusing. It occurs because only the heads and the merge base are considered
> when performing a merge, not the individual commits. The merge algorithm therefore considers the reverted
> change as no change at all, and substitutes the changed version instead.
> — https://git-scm.com/docs/git-rebase (reproduced locally, §6/G: no conflict, revert lost)

**Agent rule:** after merging a branch that contains reverts, `git diff HEAD@{1}..HEAD` (or the combined
diff) and grep for the reverted symbol/behaviour; a clean merge is not evidence that a revert held.

### 2.6 `git merge -X ours` / `-s ours` / `merge=ours` used as a "resolve everything" button

Documented semantics and the difference between the three — see §1.12; the trap is stated in the manual:

> This should not be confused with the `ours` merge strategy, which does not even look at what the other tree
> contains at all. It discards everything the other tree did, declaring *our* history contains all that
> happened in it.
> — https://git-scm.com/docs/git-merge

Rebase-specific corollary: "using the `ours` strategy simply empties all patches from the *<branch>*, which
makes little sense." — https://git-scm.com/docs/git-rebase

### 2.7 Lockfile / generated-file hand-merging (a whole conflict class)

Composer states why line merging is *semantically invalid* for lock files, with a worked counter-example:

> Branch 1 has added package A which requires package B. Package B is locked at version `1.0.0`. Branch 2 has
> added package C which conflicts with all versions below `1.2.0` of package B. A text based merge would
> result in package A version `1.0.0`, package B version `1.0.0` and package C version `1.0.0`. This is an
> invalid result, as the conflict of package C was not considered and would require an upgrade of package B.
> — https://getcomposer.org/doc/articles/resolving-merge-conflicts.md

Prescribed method (take one whole side, replay the other side's *intent* with the tool):

> The safest method to merge Composer files is to accept the version from one branch and apply the changes
> from the other branch. […] We choose the branch that has the most changes, and accept the `composer.json`
> and `composer.lock` files from that branch. […] We reapply the changes from the other branch (branch 1). In
> this case we have to run `composer require package/A` again.
> — same URL

> Before committing, make sure the resulting `composer.json` and `composer.lock` files are valid. To do this,
> run the following commands: `php composer.phar validate` / `php composer.phar install [--dry-run]`
> — same URL

Information loss is inherent, so say it in the PR:

> Keep in mind that whenever merge conflicts occur on the lock file, the information, about the exact version
> new packages were locked on for one of the branches, is lost.
> — same URL

Symptom of a wrong resolution:

> This usually happens when composer files are incorrectly merged or the composer.json file is manually
> edited.
> — same URL (output of `composer validate`)

Cargo (Rust) documents the same class and the same remedy:

> The lockfile can also be a source of merge conflicts. […] Conflicts may occur when merging branches or
> PRs, if there are non-trivial conflicts, you can reset all "yours" changes, fix all other conflicts in the
> branch, and then run some cargo command (like `cargo tree` or `cargo check`), which should re-update the
> lockfile with your own local changes. If you previously ran some `cargo update` commands in your branch,
> you can re-run them that this time.
> — https://doc.rust-lang.org/cargo/faq.html

> The purpose of a `Cargo.lock` lockfile is to describe the state of the world at the time of a successful
> build. Cargo uses the lockfile to provide deterministic builds […] Running `git bisect` to find the root
> cause of a bug / Ensuring CI only fails due to new commits and not external factors
> — same URL (why the lockfile stays in VCS despite the conflict pain)

The existence of dedicated tooling is itself the evidence of a conflict class: "Some improvement *could* be
made to git's conflict resolving by using a custom git merge driver."
— https://getcomposer.org/doc/articles/resolving-merge-conflicts.md; and the `.gitattributes` `merge=` escape
hatch (§1.12). "treating generated files as binary" is documented too:

> some text files may be machine generated and not diffable […] you don't want to treat it as such because
> it's really a lightweight database – you can't merge the contents if two people change it, and diffs
> generally aren't helpful.
> — https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes

### 2.8 `.gitignore` in a merge: ignore rules never un-track, so deletions look "lost"

> A gitignore file specifies intentionally untracked files that Git should ignore. Files already tracked by
> Git are not affected
> — https://git-scm.com/docs/gitignore

> The purpose of gitignore files is to ensure that certain files not tracked by Git remain untracked. To stop
> tracking a file that is currently tracked, use `git rm --cached` to remove the file from the index. The
> filename can then be added to the `.gitignore` file to stop the file from being reintroduced in later
> commits.
> — same URL

Reproduced locally (§6/D): adding `tracked.txt` to `.gitignore` on one branch does not remove it; merging
that branch into one where the file was also modified keeps the file tracked, so the "ignored" file reappears
in the other branch's tree. Also note the merge-relevant checkout default: "In the default overlay mode, `git
checkout` never removes files from the index or the working tree."
— https://git-scm.com/docs/git-checkout (`--overlay`)

### 2.9 Merging unrelated histories "to get the code in"

> By default, `git merge` command refuses to merge histories that do not share a common ancestor. This option
> can be used to override this safety when merging histories of two projects that started their lives
> independently. As that is a very rare occasion, no configuration variable to enable this by default exists
> or will be added.
> — https://git-scm.com/docs/git-merge (`--allow-unrelated-histories`; note the word **safety**, and that
> git deliberately refuses to make it a default)

Reproduced in §6/C: the refusal message is `fatal: refusing to merge unrelated histories`, and with the flag
the result is a union of two trees with no conflict markers at all — i.e. nothing warns you if the two
projects have same-named files with different meanings. Related footgun vocabulary: `--orphan`
("the root of a new history totally disconnected from all the other branches and commits")
— https://git-scm.com/docs/git-checkout.

### 2.10 Squash-merging a long-running branch (the "same conflict twice" loop)

See §1.18's verbatim GitHub quote: "later pull requests can include commits that were already squashed into
the base branch. This can make merge conflicts more likely and can force you to resolve the same conflicts
more than once." — https://docs.github.com/en/pull-requests/reference/pull-request-merges
(patch-id (§1.14) is what rebase uses to avoid this; squash deliberately throws commit identity away, so the
protection is gone.)

### 2.11 Rebase-merging a branch containing merges: resolutions silently dropped

> By default, a rebase will simply drop merge commits from the todo list, and put the rebased commits into a
> single, linear branch. With `--rebase-merges`, the rebase will instead try to preserve the branching
> structure within the commits that are to be rebased, by recreating the merge commits. Any resolved merge
> conflicts or manual amendments in these merge commits will have to be resolved/re-applied manually.
> — https://git-scm.com/docs/git-rebase

**Agent rule:** if the input branch has merge commits, rebasing without `--rebase-merges` deletes the
integration history (and vice versa: with `--rebase-merges`, expect to redo every resolution).

### 2.12 Trusting `rerere` / automation output as verified

§1.19 quotes ("you still need to do the final sanity checks with `git diff`"; "catch potential mismerges").

### 2.13 Assuming CI-green on the PR means the merge is safe

> This happens when two commits make changes to different parts of the code that clash with each other, like
> if one adds a new call to a function that the other renames. You need to check the combination, before it
> goes to master.
> — quoted from the Bors essay inside https://graphite.com/guides/merge-skew (the essay URL itself was
> unreachable at fetch time: the *homepage* confirms the scope — "Bors is a GitHub bot that prevents merge
> skew / semantic merge conflicts" — so the quoted passage is secondhand; see §7)

### 2.14 "Unmerge" as a release strategy

> **There is certainly no "code freeze" with Trunk-Based Development**, and **nor is there any "unmerge"** -
> backing commits out of the trunk because they are not ready, or because someone else's release is imminent,
> is equally a sign that the branching model is not working. Code that is not ready should not have been
> merged in the first place; if it is being built up incrementally on the trunk, it should be hidden behind a
> feature flag so that incomplete work has no effect on a release cut at any moment.
> — https://trunkbaseddevelopment.com/youre-doing-it-wrong/

### 2.15 Whitespace/reformatting noise masquerading as conflict (and the sanctioned fix)

> Since in this case, the actual file changes were not conflicting, once we ignore the whitespace changes,
> everything merges just fine. This is a lifesaver if you have someone on your team who likes to occasionally
> reformat everything from spaces to tabs or vice-versa.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging (`-Xignore-all-space`, `-Xignore-space-change`)

> we can extract a copy of each of these versions […] and re-try the merge again for just this single file
> with the little-known `git merge-file` command […] this actually works better than the `ignore-space-change`
> option because this actually fixes the whitespace changes before merge instead of simply ignoring them.
> — same URL

Diagnostic for the reformat-everything class: "every line is removed on one side and added again on the other."
— same URL.

### 2.16 Subtree/`read-tree`-style integration of a foreign project

> It is nice in some ways, for example all the code is committed to a single place. However, it has other
> drawbacks in that it's a bit more complex and easier to make mistakes in reintegrating changes or
> accidentally pushing a branch into an unrelated repository.
> — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

### 2.17 Indirect merges: a PR marked merged without its gates

> A pull request can be marked as merged if its head branch commits become reachable from the base branch
> outside that pull request. This can happen when the same commits are merged through another pull request or
> pushed directly to the default branch. […] Pull requests merged indirectly are marked as `merged` even if
> branch protection rules on that pull request were not satisfied.
> — https://docs.github.com/en/pull-requests/reference/pull-request-merges

---

## 3. Decision rules for "both sides advanced" conflicts

What practitioners actually prescribe, ordered as a ladder an agent can execute.

**R0 — Re-establish state before touching content.** Which operation is in progress, which refs were merged,
what the base is: `git status`, `git log --oneline --left-right HEAD...MERGE_HEAD`, `git merge-base`.
> If you are unsure which operation is active, run `git status` in the repository's terminal for Git's
> current state and next action. — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts
> To get a full list of all of the unique commits that were included in either branch involved in this merge,
> we can use the "triple dot" syntax […] That's a nice list of the six total commits involved, as well as
> which line of development each commit was on. — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging

**R1 — Never let side names decide.** Rebase swaps them (§1.11). Bind each side to a commit SHA and a branch
role ("the integration target" vs "the contributor's work") and write that into your notes before editing.
> Inspect the changes rather than choosing a side by name. — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

**R2 — Show the base.** `merge.conflictStyle = zdiff3` (or `diff3`) is a precondition for reasoning, not a
preference; the default view hides what both sides started from.
> You can tell that the original just stated a fact, and your side simply gave in to that statement and gave
> up, while the other side tried to have a more positive attitude. You can sometimes come up with a better
> resolution by viewing the original. — https://git-scm.com/docs/git-merge

**R3 — Ask *why* each side touched those lines, and let the merge base + both intents define correctness.**
> Reviewing a little bit of history to remember why two lines of development were touching the same area of
> code can be really helpful sometimes. — https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging
> Git cannot randomly pick one side over the other, and asks you to resolve it by leaving what both sides did
> to that area. — https://git-scm.com/docs/git-merge
> The final file still has to preserve the intent of both changes. — https://factory.com/articles/coding-agent-merge-conflict-resolution

**R4 — Default to *union of intents*, not to one winner.** The three legal outcomes are documented by GitHub
in exactly this form:
> Decide if you want to keep only your branch's changes, keep only the other branch's changes, or make a brand
> new change, which may incorporate changes from both branches.
> — https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-on-github
Picking one side wholesale is a *decision*, and it must be justified:
> Choosing one side wholesale would silently discard valid work. — https://factory.com/articles/coding-agent-merge-conflict-resolution

**R5 — Tests are the arbiter of a both-valid resolution; the merge is not finished until they run.**
> Tests are effectively probing our code to see if their view of the code's semantics are consistent with
> what the code actually does. — https://martinfowler.com/bliki/SemanticConflict.html
> Copilot analyzes the conflicting changes, resolves them, and verifies that the build, tests, and linter
> still pass. It then requests your review so you can confirm the resolution before merging.
> — https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github
> Inspect the staged diff and run the relevant tests before continuing. — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

**R6 — If the two intents are mutually exclusive, that is not a merge conflict; it is a design decision.
Stop and escalate.**
> If the branches made incompatible product decisions, stop and report the decision instead of guessing.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution
> **Fundamentally incompatible business logic:** where both changes make mutually exclusive architectural
> decisions that a human needs to decide […] When this happens, the entire resolution attempt is aborted and
> no commit is created for any files. — https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md

**R7 — Decline categories are enumerable; security-critical code is the named one.**
> **Security-critical code:** authentication logic, encryption, secrets handling, or access control
> — https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md
> Where the correct resolution is genuinely ambiguous or involves security-critical logic, the agent
> explicitly declines and flags the conflict for manual review instead of guessing. — same URL

**R8 — Keep the resolution narrow (integration only), and re-audit it against both parents.**
> You should refrain from abusing this option to sneak substantial changes into a merge commit. Small fixups
> like bumping release/version name would be acceptable. — https://git-scm.com/docs/git-merge
> Keep the resolution narrow. Avoid unrelated formatting, dependency updates, or refactors […]
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

**R9 — Regenerate derived artifacts instead of resolving them.** (lockfiles, generated clients, snapshots,
migration locks) — §2.7 rules; and the agent-facing version:
> Generated files need their source identified. Lockfiles need the package manager and approved regeneration
> command. Database schemas and API definitions need compatibility requirements, not just syntax checks.
> — https://factory.com/articles/coding-agent-merge-conflict-resolution

**R10 — Prefer the cheap reset when the resolution is going badly.** `git merge --abort` /
`git rebase --abort` / `git cherry-pick --abort` exist and are documented as returning to the pre-operation
state; re-plan, re-read the base, and retry — don't improvise on top of a half-baked resolution.
> If you tried a merge which resulted in complex conflicts and want to start over, you can recover with
> `git merge --abort`. — https://git-scm.com/docs/git-merge
> `--abort`: Cancel the operation and return to the pre-sequence state. — https://git-scm.com/docs/git-cherry-pick
Caveat §1.9/§1.10 (abort may not restore uncommitted work; abort discards resolution work).

**R11 — After-the-fact arbitration of "was this resolution right?"** combined diff / `git show` on the merge
commit / `git diff <parent>..<merge>`, and, for whole-history auditing, re-merge comparison
(`git show --remerge-diff`, plus evil-merge detectors) — §1.8, §2.1.

**R12 — Reduce the number of both-ahead conflicts as a systemic goal.** Short branches (§1.3), low merge skew
and rebase-before-integrate (§1.21), merge queues for scale (§1.21), and the "one side per file ownership"
declarations in `.gitattributes` (§1.12).

---

## 4. Agent-specific rules (published, product-level)

The strongest material is vendor documentation, since it states what an *automated* resolver is required to do:

1. **Give the resolver the merge base, and have it reason over both sides' goals.**
   > The AI considers the merge base (the common ancestor of both branches) and the changes from each branch
   > to generate a resolution that attempts to preserve the intent of both changes.
   > — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts
2. **Reproduce from pinned inputs, in a clean worktree — a moving branch produces a different conflict.**
   > Record the target branch, source branch, and exact commit identifiers before asking an agent to resolve
   > anything. Fetch the required refs, start from a clean worktree, and reproduce the merge or rebase with the
   > repository's normal command. A moving branch can produce a different conflict minutes later, so pinning
   > the inputs keeps the task reviewable.
   > — https://factory.com/articles/coding-agent-merge-conflict-resolution
   Machine-checked by commercial automation as a race guard:
   > If your branch receives a new commit while resolution is running, CodeRabbit aborts to avoid overwriting
   > the incoming changes. — https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md
3. **Validate the resolution mechanically before declaring success** — markers gone, index clean, build/lint:
   > CodeRabbit verifies that no conflict markers remain, that the merge index is fully cleared, and runs the
   > repository's build and lint commands to surface any errors introduced by the resolution. — same URL
   > Copilot … resolves them, and verifies that the build, tests, and linter still pass.
   > — https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github
4. **Commit as a real merge commit (two parents), never as a squashed fix.**
   > The resolved changes are committed to your branch as a proper merge commit with two parents (your branch
   > and the base branch), so git history accurately reflects the merge.
   > — https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md
5. **Human review is the product's final gate, not an optional step.**
   > It then requests your review so you can confirm the resolution before merging.
   > — https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github
   > Review the agent's analysis and proposed edits in the Chat view and editor. Accept the resolution or
   > adjust it manually, then test the result. — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts
   > **Review suggestions**: While AI can provide valuable assistance, it's essential to review its
   > suggestions to ensure they align with your project's requirements. — https://graphite.com/guides/ai-code-merge-conflict-resolution
6. **Publish the decision trail; name the open human questions.**
   > The pull request should name the conflicting commits, affected files, resolution decisions, and commands
   > run. Reviewers need to see where the agent combined behavior, where it selected one side, and where a
   > human decision remains open. That evidence turns an opaque conflict cleanup into a normal code review.
   > — https://factory.com/articles/coding-agent-merge-conflict-resolution
7. **All-or-nothing, not partial.** (a strong design rule an agent skill should copy)
   > If CodeRabbit declines to resolve any file, no commit is created, not even for the files it could
   > resolve. — https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md
8. **Simulate before mutating.**
   > During PR review, CodeRabbit simulates the merge in a sandbox without modifying your working tree. — same
   > URL (an agent should likewise resolve in a scratch worktree when the outcome is uncertain)
9. **Vocabulary an agent must use correctly**: "Clean Git index ≠ resolved conflict"; and note the tool
   landscape is largely marketing-adjacent — Graphite's own guide concedes the mechanism of its merge queue is
   deterministic, not AI: "While this feature is not AI-powered, Graphite Agent provides AI-driven code
   reviews" — https://graphite.com/guides/ai-code-merge-conflict-resolution
10. **UI affordances an agent will meet**: GitHub's merge box offers "Fix with Copilot", or an `@copilot
    resolve the merge conflicts on this PR` comment
    — https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github; the
    VS Code feature is labelled **experimental**
    — https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts ("AI-assisted conflict resolution is an
    experimental feature and requires GitHub Copilot access").

---

## 5. Recovery playbook (undoing merges and bad resolutions)

| Situation | Move | Source |
| --- | --- | --- |
| Conflict resolution going badly, merge in progress | `git merge --abort` (equivalent to `git reset --merge` when `MERGE_HEAD` exists, modulo autostash) | https://git-scm.com/docs/git-merge |
| Want a hard restart, no uncommitted work to save | `git reset --hard HEAD` — "your repository will be back to the last committed state. Remember that any uncommitted work will be lost" | https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging |
| Rebase stopped mid-way, abandon it | `git rebase --abort` ("Abort the rebase operation and reset HEAD to the original branch") | https://git-scm.com/docs/git-rebase |
| Cherry-pick sequence gone wrong | `git cherry-pick --abort` / `--quit` ("Forget about the current operation in progress") | https://git-scm.com/docs/git-cherry-pick |
| Bad merge is **local only** | "the easiest and best solution is to move the branches so that they point where you want them to" → `git reset --hard HEAD~`; downside: "it's rewriting history, which can be problematic with a shared repository" and "won't work if any other commits have been created since the merge" | https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging |
| Bad merge is **pushed/public** | `git revert -m 1 HEAD`; "The `-m 1` flag indicates which parent is the 'mainline' and should be kept." | same URL; https://raw.githubusercontent.com/git/git/master/Documentation/howto/revert-a-faulty-merge.adoc |
| Re-merging after that revert brings nothing back | branch fixed **on top** → `git revert <the-revert>`; branch **rebuilt from scratch** → re-merge as-is (or recreate with `git rebase --no-ff <fork-point>`) | same howto; `--force-rebase` note in https://git-scm.com/docs/git-rebase |
| Resolution committed but wrong, need a redo of one file | `git show :1:f`/`:2:f`/`:3:f` then `git merge-file` per file, re-`add` | https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging |
| Need the pre-operation tip after a completed rebase | branch reflog: `@{1}`; `git reset HEAD@{2}` — "Git never really loses anything, even when performing history rewriting operations" | https://git-scm.com/docs/git-rebase; https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog |
| Conflicted file re-checkout to get markers back | `git checkout -m <file>` / `git checkout --conflict=diff3 <file>` ("recreate the conflicted merge in the specified paths") | https://git-scm.com/docs/git-checkout |
| Local changes block the switch | `git checkout -m <branch>` autostashes and reapplies; "If reapplying the stash results in conflicts, the entry is saved to the stash list" | same URL |
| Already-pulled rewritten upstream | easy case: `git rebase <upstream>` (patch-id dedup saves you); hard case: `git rebase --onto <newupstream> <fork-point>`, or `git format-patch` of only your commits + apply | https://git-scm.com/docs/git-rebase (RECOVERING FROM UPSTREAM REBASE) |
| Force-push about to happen | `--force-with-lease` at minimum (§1.16) | https://git-scm.com/docs/git-push |

---

## 6. Local experiments (grounding; scratch repos, read-only w.r.t. any real project)

Environment: `git version 2.46.2.windows.1`, repos created under `%TEMP%\mergetest.H7Sz8A\`.

**A — ours/theirs swap during rebase.** `main` has `MAIN-INTENT`, `feature` has `FEATURE-INTENT` in the same
line; `git checkout feature && git rebase main` → conflict; then:

```
git show :2:f.txt  -> MAIN-INTENT      # stage 2 == "ours" == the new base
git show :3:f.txt  -> FEATURE-INTENT   # stage 3 == "theirs" == my work being replayed
conflict markers   -> <<<<<<< HEAD (MAIN-INTENT)  ======= (FEATURE-INTENT) >>>>>>> d2c124e (feat)
```

Confirms §1.11 exactly, including that the marker header `HEAD` shows the *base* branch name during a rebase.
`git rebase --abort` returned HEAD to `feature`.

**B — revert a merge, then re-merge the same branch.** After `git revert -m 1`, adding a new commit to the
same topic branch and merging again produced a **conflict** whose HEAD side contained only the pre-merge
content, with the faulty line preserved in the incoming side:

```
main f.txt after revert: v0
after re-merge: CONFLICT (content): Merge conflict in f.txt
                <<<<<<< HEAD  =======  feature line / more work on topic  >>>>>>> topic
```

and the original topic commit **is** an ancestor of main (`git merge-base --is-ancestor topic~1 main` → yes).
Net: the pre-revert change never returns automatically — you get either a conflict to resolve "by hand, again"
or (in the variant where the faulty work added a whole new file) a merge that lands only the post-revert
commits. Matches §2.4's documented behaviour.

**C — unrelated histories.** `git merge local/main` across two independent repos →
`fatal: refusing to merge unrelated histories`; with `--allow-unrelated-histories` the merge succeeds and
`git ls-files` shows the union (`a.txt`, `b.txt`) with **no** conflict signal. Confirms §2.9: the "safety" is
the refusal, and removing it removes all diagnostics.

**D — gitignore vs tracked file.** Adding `tracked.txt` to `.gitignore` after it was committed:
`git ls-files` still lists it; only `git rm --cached tracked.txt` + commit un-tracks it, and the working-tree
file remains on disk. Confirms §2.8.

**E — `cherry-pick -x` marker.** Clean pick:

```
clean commit

(cherry picked from commit 23646ce…)
```

Conflicted pick (resolved with `git add` + `git cherry-pick --continue`):

```
conflicting commit

(cherry picked from commit 8d8ed2f…)
```

**Discrepancy:** the man page says the trailer is added "only for cherry picks without conflicts", but on
2.46.2 the trailer was still recorded after a conflicted pick. Treat the doc sentence as "not guaranteed in
the conflicted case" and rely on patch-id / `git cherry -v` for dedup (§1.14).

**F — cherry-picking a merge commit.** Without `-m`:

```
error: commit 474d872… is a merge but no -m option was given.
fatal: cherry-pick failed
```

With `-m 1` the sequencer starts (it replays the merge's diff against parent 1). Confirms §1.13. (The scripted
run was noisy here; the error text is the load-bearing result.)

**G — change made on both branches, reverted on one.** Merge of `feat` (reverted) into `main` (kept) produced
`Merge made by the 'ort' strategy.` and `f.txt = v2`: **the revert silently lost, with no conflict.** This is
the documented behaviour in §2.5, reproduced.

---

## 7. UNVERIFIED / weak-source items — do not present as sourced facts

1. **"Merge Friday" as a named, recommended practice.** The user asked for this specifically. I could not find
   a primary engineering post for it; the only hit was a secondhand quote on an unrelated aggregator page
   ("This lead to the existence of something like a merge Friday or a merge week – where all the developers
   took their changes, merged them together into one …" — blog.risingstack.com listing), which describes it as
   a *symptom of bad integration hygiene*, not a target practice. **Use the merge-queue / merge-skew framing
   (§1.21) instead**; if "Merge Friday" is mentioned at all, mark it as folklore.
2. **Google's / Microsoft's own published "merging at scale" pages.** Not fetched. The strongest *fetched*
   third-party claim is: "Google does Trunk-Based Development and have **35000 developers and QA automators**
   in that single monorepo trunk" — https://trunkbaseddevelopment.com/ (itself citing a Google post I did not
   fetch). Do not attribute numbers to Google in the skill without fetching the primary post.
3. **Bors essay text** ("You need to check the combination, before it goes to master.") — reached only via a
   quotation inside https://graphite.com/guides/merge-skew; the essay URL 404'd at fetch time. The bors-ng
   *homepage* statement (§1.21) is verified; the essay sentence is secondhand.
4. **The dev.to evil-merge malware incident** — single anonymous practitioner account, no CVE, no vendor
   advisory, and the quoted GitHub response ("This is an intentional design decision and is working as
   expected.") is not independently confirmable. The *technique* and the *detection method* are verified
   against git's glossary and `--remerge-diff`; the *story* is an anecdote. Also unverified: the author's tool
   claims (Evil Merge Detector, `evilmergediff`).
5. **`git show --remerge-diff`** — mentioned by the dev.to article; I did not fetch the git-merge/git-show man
   page section that documents it. Verify before printing the flag (the internals agent likely covers it).
6. **Wikipedia's "evil merge" wording** — not fetched (StackOverflow returned 403 to the fetcher). The git
   glossary (§2.1) is the better primary source anyway.
7. **git-rebase "BEHAVIORAL DIFFERENCES → Labelling of conflicts markers"** section exists in the page outline
   but was outside the fetched window; I did not quote it. §1.11 relies on `git-checkout`, `git-rebase -m`, and
   VS Code, all of which were read verbatim.
8. **GitHub's older "About merge methods" URL** (404); §1.17 uses the current `pull-request-merges` reference
   page. If the skill needs screenshots/buttons, re-verify names: "Fix with Copilot", "Resolve conflicts",
   "Mark as resolved", "Commit merge", "Update branch" — first four verified in the fetched docs page,
   "Update branch" appears only as "you can update the head branch" prose.
9. **Whether the ours/theirs swap applies identically to `git cherry-pick` conflicts.** VS Code's table asserts
   cherry-pick's "Incoming" = "The commit being applied" (i.e. *not* swapped). https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts
   — verified as a vendor claim, not derived from git docs; a local probe of `:2:`/`:3:` during a conflicted
   cherry-pick was not run.
10. **"Golden army knife"** — the user's term appears nowhere in the fetched sources; the canonical name for
    the anti-pattern is **evil merge** (§2.1). Do not introduce "golden army knife" as if it were established
    terminology.
11. **`git rerere` default state and its safety for automation** — I verified `rerere.enabled` is required and
    the audit flags; I did not verify current defaults per git version.

---

## 8. Source index

Atlassian
- https://www.atlassian.com/git/tutorials/merging-vs-rebasing
- https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts
- https://www.atlassian.com/git/tutorials/cherry-pick
- https://www.atlassian.com/git/tutorials/rewriting-history/git-reflog

Pro Git (git-scm.com book)
- https://git-scm.com/book/en/v2/Git-Branching-Rebasing
- https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging
- https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes

Git manuals / guides
- https://git-scm.com/docs/git-merge
- https://git-scm.com/docs/git-rebase
- https://git-scm.com/docs/git-cherry-pick
- https://git-scm.com/docs/git-checkout
- https://git-scm.com/docs/git-cherry
- https://git-scm.com/docs/git-patch-id
- https://git-scm.com/docs/gitglossary
- https://git-scm.com/docs/git-rerere
- https://git-scm.com/docs/git-push
- https://git-scm.com/docs/gitignore
- https://raw.githubusercontent.com/git/git/master/Documentation/howto/revert-a-faulty-merge.adoc
  (rendered as https://git-scm.com/docs/howto/revert-a-faulty-merge, which redirects)

Platform docs
- https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-on-github
- https://docs.github.com/en/pull-requests/reference/pull-request-merges
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-on-github
- https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts

Practitioner / industry
- https://www.thoughtworks.com/en-de/radar/techniques/long-lived-branches-with-gitflow
- https://trunkbaseddevelopment.com/
- https://trunkbaseddevelopment.com/youre-doing-it-wrong/
- https://martinfowler.com/bliki/SemanticConflict.html
- https://bors.tech/
- https://graphite.com/guides/merge-skew
- https://graphite.com/guides/ai-code-merge-conflict-resolution

Ecosystem tooling (conflict-class evidence)
- https://doc.rust-lang.org/cargo/faq.html
- https://getcomposer.org/doc/articles/resolving-merge-conflicts.md

Agent-specific / incident
- https://factory.com/articles/coding-agent-merge-conflict-resolution
- https://docs.coderabbit.ai/finishing-touches/resolve-merge-conflict.md
- https://dev.to/fimskiy/evil-merge-the-git-attack-that-hid-malware-in-plain-sight-for-35-months-48mk
