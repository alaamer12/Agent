# Report templates (Step 6: scope report; Step 8: post-change summary)

> **Illustrative, not exhaustive.** The buckets, column names, and scope options below are shapes to adapt, not a required form. Rename a bucket to fit the change, drop the ones that are empty, add one the project needs, and propose a hybrid scope when that fits better. Nothing here assumes a particular language, framework, or repository layout.

Fill this in and present it before editing anything. Keep it scannable: the user has to make one decision from it. Delete any bucket that has zero hits rather than printing "0".

Send it as your message text, then call your structured question tool (for example `ask_user_input_v0`) with the scope question below. If you have no such tool, end the message with the numbered question instead.

---

## Template

```markdown
**Change requested:** <one line: what is changing, from -> to>
**You pointed at:** <seed location, or "no specific location">

I searched the whole workspace, not just that spot. I found **<N> places
across <F> files** that this change touches:

| Bucket | Count | Examples |
|---|---|---|
| Core (the change itself) | <n> | `<file>:<line>` |
| User-facing (UI text, messages, docs strings shown to users) | <n> | `<file>:<line>`, `<file>:<line>` |
| Internal (identifiers, style or theme hooks, callers) | <n> | `<file>:<line>`, `<identifier>` ×<k> |
| Contracts (public APIs, storage schema, wire formats, env) | <n> | `<item>` |
| Verification (tests, mocks) | <n> | `<file>` |
| Docs | <n> | `<file>` |
| Historical (likely leave) | <n> | `<file>` |
| Possible look-alikes | <n> | `<file>:<line>` |

**Needs your call**
- `<contract item>`: <what would break if changed>
- `<look-alike item>`: <why it may mean something different>

**Languages:** <n locales found: list>. <pipeline-managed? natural-language keys? fallback configured?>
(Delete this line when the project has no locales. If it has, fold the translation
policy into the scope question or ask it as the second question: translate all /
translate + flag for native review / source locale only, pipeline fills the rest.)

**Cannot verify from here:** <external systems, DB rows, other repos, or "nothing">

**My recommendation:** <scope>, because <one-line reason>. This is only a
suggestion.
```

---

## The scope question

Ask one question, offering a small set of mutually exclusive choices built from the buckets you actually found. Name each choice in the words of this change. Illustrative shapes, not a fixed menu:

- `[just the spot you named]`
- `[the change + everything that shows or explains it]`
- `[everything except contracts]`
- `[everything, including contracts]`

**Question:** "How far should I take this change?"

Drop choices that do not apply, and add a hybrid when the findings call for one (for example `[everything, keeping the old public name as a deprecated alias]`). Mark your recommended choice in the message body, not by reordering or pre-selecting.

If the user might want to review individual items, use a second question (three questions total is the ceiling), such as whether to include tests and docs, only when that bucket is large and separable. Otherwise fold it into the scope choices.

---

## Plain-text fallback (no question tool)

End the report with the choices in prose, bracketed, and invite a different answer:

```markdown
**How far should I take this?** I could do `[just the spot you named]`, or
`[the change plus everything that shows or explains it]`, or `[everything except
contracts]`, or `[everything, including contracts]`. Those are only starting
points: tell me a different split or a hybrid if that fits better.
```

---

## Post-change summary (Step 8)

Do not write "all remaining matches are intentional" from memory. Prove it. Re-run the sweep, then reconcile every remaining hit against the skip-list the user approved. A hit that is not on that list is a miss, even if the visible UI already looks right.

Why this matters: a line like `<h1 className="catalog__title">Explore the topics</h1>` reads correctly on screen, yet still contains `catalog__title`. Counting only visible text makes that line look fixed when it is not.

Reproduce it mechanically with the same skip list you showed the user:

```bash
python scripts/sweep.py "<old text>" "<old key>" "<old translation>" \
  --allow CHANGELOG.md --allow vendor      # prints APPROVED / UNAPPROVED per hit; exit 1 if any UNAPPROVED
```

```markdown
**Done.** Scope: <chosen scope>.   Change: <old> -> <new>   (wording | meaning | removal)
Source of truth: <where it originates and how it reaches the UI>

**Updated**
- Source/UI: <files>
- Locales: <n> languages (<list>) - translated: <list>; flagged for native review: <list>; left to pipeline: <list>
- Metadata/a11y: <files>
- Docs: <files>
- Tests/snapshots: <files>  (snapshots regenerated via <command>)

**Reconciliation of remaining matches**

| Remaining | Where | Approved to leave? |
|---|---|---|
| <n> | `<file>` | yes: <reason, e.g. "/catalog route, your choice"> |
| <n> | `vendor/audio-lib.js` | yes: unrelated third-party look-alike |
| <n> | `CHANGELOG.md` | yes: historical record |

Unapproved remaining: **0**

**Verification:** positive sweep <result> | locale parity <result> | tests/lint/build <result>

**Needs a human / your decision:** <native review, CMS or dashboard edits, store listings, production DB rows, terms wording, images/screenshots, or "none">
**Cannot verify from here:** <other repos, external dashboards, or "nothing">
**Noticed but not touched:** <unrelated typos, broken links, duplicated copies worth consolidating, or "none">
```

**The rule:** "Unapproved remaining" must be 0 before you send this. If it is not 0, fix those hits and re-sweep first. If you cannot fix one (for example it needs a decision you have not asked about), stop and ask instead of listing it as done.
