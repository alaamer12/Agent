# Principles — The Doctrine Every Agenda Inherits

## Contents
- The one move underneath everything
- The stereotype library (bad thinking, named)
- The counter-moves (good thinking, named)
- The self-audit gate (run this before presenting any structure.md)
- Single-ground and the Authority Table
- Named absences

This file is stack-agnostic. Every file in `agendas/` assumes you've read this first — an agenda is a set of hypotheses to test against project evidence, not a set of defaults to apply.

---

## The one move underneath everything

A convention is a **hypothesis about this project**, not a fact about it, until evidence pins it down. Bad thinking treats conventions as already-settled — reaches for the nearest one and builds on it. Good thinking treats every convention as on probation: apply it only after something in *this* project's evidence affirmatively supports it, and drop it the moment something contradicts it — even mid-draft, even after already writing good reasoning that assumed it.

Everything below is that move, named at the places it fails and the places it works.

---

## The stereotype library — bad thinking, named

A named reflex is one you can catch next time. An unnamed one just feels like thinking.

**The requirement-substitution reflex.** The user states a requirement explicitly — a deploy target, a constraint on what languages are allowed, a scope boundary — and the answer that gets built satisfies a *different*, unstated, more familiar requirement instead, because the familiar one is easier to reach for. This is not the same failure as the professional-shape reflex below, and the difference matters: the professional-shape reflex fills a *gap* — evidence nobody supplied — with a convention. This reflex *overrides evidence already in hand*. Told "deploy to Railway," building a Dockerfile isn't filling a gap about deployment — Railway builds directly from the project's manifest; a Dockerfile answers a question ("how do we containerize this") that was never asked, and quietly substitutes it for the one that was ("how does this deploy to Railway specifically," which usually just means a Railway config file, if anything at all). Told "workers can be written in any language," building a single-language worker fleet isn't a missing-evidence default — the requirement was stated, in full, and got overwritten by "workers are normally one language" anyway. The fix for a gap is to go find evidence. The fix here is different and cheaper: stop overriding evidence that was already given. The tell: re-read the specific words the user used before drafting — if the draft answers a nearby, more familiar question instead of the one actually asked, this is what happened.

**The professional-shape reflex.** Reaching for a piece because "every serious project has one" — not because a project-specific fact calls for it, and *no requirement said otherwise either way*. The tell: you can't cite a fact about *this* project that justifies the piece, only what similar projects usually have. Distinguishing this from the requirement-substitution reflex above matters — this one fires into silence (nothing was said), that one fires over something that was said.

**The over-engineering-for-generality reflex.** Building a full abstraction — a client class, a generic adapter layer — for something a benchmark or prior decision already pinned to one specific, thin shape. This is the most dangerous member of the family because it looks like rigor. More code, more layers, more "proper" structure reads as diligence. It's actually amnesia: designing as if a decision already on record hadn't been made.

**The elevation reflex.** A feature quietly becomes a requirement because the tree gave it a load-bearing folder. Nobody decided this — the layout did. Watch for anything the system would fail without, that was only ever asked for as "store this" or "track that."

**Premise-staleness blindness.** A decision made two rounds ago curdles from "a choice we made, revisit if things change" into "the shape of the world, unquestioned." The tell: a structural assumption with no recent evidence behind it, still shaping new decisions as if it were still fresh.

**The symmetrization reflex.** A real asymmetric relation — X belongs to Y, doesn't just work alongside it — gets rendered as sibling folders. The most dangerous one: no self-review catches it, because adjacent folders satisfy every stated rule ("a home per concept," "clean separation"). Flat feels organized. Organized is not the same claim as correct. Only checking the *original relationship*, not the folder-naming convention, catches it.

**The eloquence-as-substitute reflex.** Pouring real, good reasoning into the sub-question you *can* answer, while the actual blocker is a handful of unasked questions the whole shape depends on. Fluent reasoning about the wrong question is, from the inside, indistinguishable from having addressed the real one — that's exactly why it's dangerous.

---

## The counter-moves — good thinking, named

**Re-read the user's literal words before drafting, and hold them over any convention.** Before applying anything from an agenda or a general default, check whether the user already answered this specific question in their own words. If they did, that answer wins outright — it is not one input to weigh against convention, it is the requirement. Building toward a familiar-sounding but different target (Docker, when the stated target was a specific platform; a single-language fleet, when the stated requirement was language-agnostic) is not a defensible interpretation of an ambiguous request — it's replacing a clear answer with a more comfortable one.

**Premises ledger before generation.** Before drawing anything, list what's decided-with-evidence, what's assumed, what's flat-out unasked. This is the single move that catches the eloquence reflex — an unasked question shows up in the ledger before any words get spent defending an answer to a different one. It also catches requirement-substitution: a requirement that's actually decided-with-evidence should never lose to something merely assumed.

**Evidence has to earn the default, in both directions.** Not "never use convention X," not "always use it" — X gets used if and only if something in *this* project's evidence calls for it. Reflexively distrusting every convention because conventions burned you once is the professional-shape reflex wearing a contrarian coat. Balance isn't splitting the difference between the two failure modes; it's refusing to run either one on autopilot.

**A correction is premise-replacement until proven otherwise.** When corrected, the reflex is to patch the one line. The discipline is to ask: what else was I believing that was only true under the premise that just died? Multiple blindnesses often share one dead premise — patch-one-line finds the first, not the rest.

**Nest asymmetric relations; never flatten them into adjacency.** Before drawing two things as siblings, ask: does the second exist independent of the first, or only because of it? Only-because-of is a child, not a peer — draw it as one, even though siblings will always look tidier.

**Named absences instead of guesses.** When a decision is real but genuinely not yet made, the honest artifact is a structural placeholder with a revisit trigger — not a confident pick that quietly becomes load-bearing. Helpfulness that outruns the evidence is the failure mode, not the virtue.

**Audit your own next output for the rule you just adopted.** Adopting a principle doesn't install it — it gives you a new thing to check yourself against, on your own most recent work, not just the thing that prompted the correction.

---

## The self-audit gate

Run this against every drafted `structure.md` before presenting it — not a vague "review your work," this specific list, in this order (requirement-fidelity first, because it's cheaper to check and more severe when it fails):

1. **Requirement-fidelity check.** For every piece in the draft, was there a specific requirement in the user's own words that this piece answers — or does it answer a nearby, more familiar question instead? Go back to what was actually said, not what's easy to recall having intended. A Railway deploy target answered with a Dockerfile, or an "any language" requirement answered with a single-language fleet, are this check's canonical failures — a stated requirement quietly swapped for a comfortable substitute.
2. **Professional-shape check.** For every piece that matches a common convention (Dockerfile, client class, dedicated subsystem, ORM layer, test pyramid shape...) that check 1 didn't already flag: can you point to a project-specific fact that justifies it? If not, cut it or flag it as unverified.
3. **Elevation check.** Does anything the project only ever asked for as a feature now behave like a dependency the system can't run without? If so, either the system needs an explicit fallback path, or the piece needs to be demoted back to optional.
4. **Staleness check.** Is any structural decision resting on a premise from earlier in the process that hasn't been re-checked against the most recent evidence?
5. **Symmetrization check.** Any pair of sibling folders where one thing actually only exists because of the other? If so, nest it.
6. **Eloquence check.** Is there a section with unusually confident, detailed reasoning sitting next to a section that's thin or hand-waved? Thin sections are often the real blocker wearing a disguise — check whether the detailed section is answering a question nobody asked instead of the one that's actually load-bearing.
7. **Named-absence check.** Any decision that got guessed instead of flagged? If the evidence doesn't support a pick, it goes in as a named absence with a revisit trigger, not as a confident line in the tree.

If any check fails, fix it before presenting — don't present with a caveat. A caveated wrong answer is still a wrong answer with extra steps.

---

## The Authority Table, as an artifact

`references/decision-spectra.md` covers *when* a decision earns a single shared ground — that reasoning lives there once, not here. This section is about the artifact that records the answer once a decision has earned it.

The tree is a map of folders. The Authority Table is a map of *decisions* — and it's the part that actually prevents drift, because folders don't stop someone from redeciding a threshold in a second place six months from now; a table with a "single ground" column and a "protecting test" column does.

Every structure.md this skill produces includes an Authority Table: decision → single ground → consumers → protecting test. When a new constant or rule appears later, it gets a row, or the addition is rejected regardless of how clean the code looks.

---

## Named absences

A named absence is a decision the project genuinely hasn't made yet, given structure anyway — a file, a slot, an entry in the Authority Table marked "reserved, not frozen" — instead of either (a) silently guessing, or (b) leaving nothing and letting the gap get filled ad hoc later by whoever hits it first.

A named absence needs:
- **What decision is missing** (stated precisely enough that answering it is unambiguous)
- **Where it will live once decided** (the file/package that becomes its ground)
- **What would trigger revisiting it** (a condition, not a date — "when ranking quality matters" beats "in Q3")

Named absences are not TODOs. A TODO is "get to this later." A named absence is "this is structurally real and deserves a reserved seat even though we don't yet know what sits in it."
