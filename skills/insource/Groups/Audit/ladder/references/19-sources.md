# 19 — Sources: where each semantics claim came from

"Ladder pattern" is not one standardized term. Each file in this directory states who does it that way;
this is the evidence list behind those claims, so a reader can check the convention rather than trust
the summary. Grouped by the reference file that uses it.

## Terminology and disambiguation (`00`, `17`, `18`)

- Ladder logic / IEC 61131-3 Ladder Diagram: rails, rungs, contacts, coils; scan cycle with input and
  output image tables. [control.com — Ladder Diagram Programming](https://control.com/textbook/programmable-logic-controllers/ladder-diagram-ld-programming/),
  [plcprogramming.io — Contacts, Coils and Power Flow](https://plcprogramming.io/guides/ladder-logic-contacts-coils)
- Duplicate coils: "when two or more output instructions target the same bit in the same scan, the last
  one executed wins" (Allen-Bradley OTE), while IEC 61131-3 semantics treat multiple rungs driving one
  coil as a logical OR — i.e. vendor divergence. [industrialmonitordirect — Duplicated OTE Coils](https://industrialmonitordirect.com/de/blogs/knowledgebase/allen-bradley-ladder-logic-duplicated-ote-coils-and-scan-cycle),
  [ESBMC-PLC: Formal Verification of IEC 61131-3 Ladder Diagrams](https://arxiv.org/pdf/2606.15461),
  [r/PLC thread on two rungs setting the same bit](https://www.reddit.com/r/PLC/comments/m3kuu3/ladder_logic_help_when_you_have_two_rungs_setting/)
- Laddering interviews (means-end chain): repeated "why is that important to you?" climbing
  attribute → functional consequence → psychosocial consequence → value; documented fatigue failure mode.
  [UXmatters — Laddering: A Research Interview Technique for Uncovering Core Values](https://www.uxmatters.com/mt/archives/2009/07/laddering-a-research-interview-technique-for-uncovering-core-values.php),
  [Reynolds & Gutman, Laddering theory, method, analysis, and interpretation](https://ngovietliem.com/wp-content/uploads/2022/12/Reading-3.3-Laddering-theory.pdf),
  [Umbrex — Means-End Chain / Laddering Framework](https://umbrex.com/resources/frameworks/marketing-frameworks/means-end-chain-laddering-framework/)
- Ladder of inference (Argyris; seven steps: observable data → selecting → adding meaning → assumptions
  → conclusions → beliefs → actions). [The Systems Thinker — The Ladder of Inference](https://thesystemsthinker.com/the-ladder-of-inference/),
  [untools — Ladder of inference](https://untools.co/ladder-of-inference/),
  [USC Gould — Understanding the Ladder of Inference](https://gould.usc.edu/news/understanding-the-ladder-of-inference-navigating-cognitive-pitfalls/)
- Levels of abstraction as a design-school term. [d.school — Levels of Abstraction](https://www.interactiondesignantschool.org/literature/article/levels-of-abstraction) (also
  indexed via the `stateful` skill's axis grid).

## First-match-wins as a widespread convention (`00`, `01`, `02`)

- [DataHub — Search V3 Design](https://docs.datahub.com/docs/developers/search-v3-design): "The first
  match wins. A query that matches none stays on the current template unless that template sets a default."
- [Apinizer — Routing and Failover](https://docs.apinizer.com/en/ai-gateway/routing-and-failover): "routes
  are evaluated in order and the first match wins."
- [arXiv 2605.02832 — Policy-Aware Framework for Adaptive Task Allocation](https://arxiv.org/html/2605.02832v2):
  "Rules fire in priority order; the first match wins and short-circuits the remaining rules, matching
  the standard conflict-resolution strategy of forward chaining."
- [replication-conflict-resolution.org — Declarative Merge Rules in YAML](https://www.replication-conflict-resolution.org/conflict-detection-automated-resolution-strategies/auto-merge-rule-engines/writing-declarative-merge-rules-in-yaml/):
  the shadowing warning in as-is form — "a broad `type: order` rule placed above a narrow
  `id_prefix: "order-vip-"` rule will shadow the specific one forever."
- [standard-schema-faker](https://github.com/osbytes/standard-schema-faker): "First match wins across
  the whole `defaultHeuristics` array, ordered by signal strength" — specificity as an ordering story.
- [pi-gauntlet overlay precedence](https://pi.dev/packages/pi-gauntlet): "Overlay precedence, first match
  wins on any conflict: repo root REVIEW.md always wins over everything below it."
- [go-steer/k8s-lookout `leeway`](https://pkg.go.dev/github.com/go-steer/k8s-lookout/pkg/leeway):
  `Ambiguous` (more than one supported rule accepted) *and* `Index` ("the first") — the two fields are
  exactly the audit shape recommended in `15`.

## Semantics and combining rules (`14`, `13`)

- [OASIS XACML 3.0 core spec](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-cd-03-en.html):
  rule/policy combining algorithms including `deny-overrides` ("if any rule evaluates to Deny, the
  policy must return Deny"), `permit-overrides`, `first-applicable`, `only-one-applicable`.
- [The Logic of XACML (arXiv)](https://arxiv.org/html/1110.3706v1) and
  [ScienceDirect version](https://www.sciencedirect.com/science/article/pii/S0167642313001238): the four
  standard combining algorithms named and formalized.
- [Access Control Policy Combining: Theory Meets Practice (Li et al.)](https://www.cs.purdue.edu/homes/ninghui/papers/pca_sacmat09.pdf): why
  order-independent combining exists for security.
- [Cedar / AWS Verified Permissions guides](https://hidekazu-konishi.com/entry/aws_verified_permissions_cedar_complete_guide.html),
  [Lucid policy-as-code](https://docs.lucidcomputing.ai/guides/policy-as-code.html),
  [NVIDIA permission-service policy evaluation](https://docs.omniverse.nvidia.com/ovstorage/permission-service/0.0.52/policy-evaluation.html):
  deny-overrides + default deny, "applications never have to enforce it by convention".
- [Cedar vs Rego vs OpenFGA](https://sph.sh/en/posts/policy-language-comparison-cedar-rego-openfga/),
  [Manning — Authorization in Action ch.7](https://www.manning.com/preview/authorization-in-action/chapter-7):
  scope-match → condition-eval → combining, the three-phase pipeline.
- [DMN hit policy explained (Trisotech)](https://www.trisotech.com/dmn-hit-policy-explained/),
  [Camunda — Choosing the DMN hit policy](https://docs.camunda.io/docs/components/best-practices/modeling/choosing-the-dmn-hit-policy/),
  [Method & Style](https://www.methodandstyle.com/blog/decision-table-hit-policy-explained/),
  [Bizzdesign](https://help.bizzdesign.com/articles/horizzon-help/hit-policies-for-dmn-decision-table-rules),
  [Flowable DMN intro](https://www.flowable.com/open-source/docs/dmn/ch06-DMN-Introduction): `UNIQUE`,
  `FIRST`, `ANY`, `COLLECT`, `RULE ORDER`, `OUTPUT ORDER`, `PRIORITY`.
- [FHIR codesystem for rule combining](http://hl7.org/FHIR/codesystem-permission-rule-combining.html):
  the same deny/permit-override vocabulary standardized outside of access control.

## Priority numbers and conflict resolution (`07`)

- [Drools rule engine](https://docs.drools.org/latest/drools-docs/drools/rule-engine/index.html) and
  [Drools language reference](https://docs.drools.org/latest/drools-docs/drools/language-reference/index.html):
  "Each rule has an integer salience attribute… higher salience values are given higher priority."
- [Drools ch.7 Running](https://docs.drools.org/6.5.0.Final/drools-docs/html/ch07.html): default conflict
  resolution is salience then LIFO; [Agenda-group vs activation-group](https://paras301.medium.com/drools-agenda-group-vs-activation-group-and-how-to-use-them-together-eccd64ff3a7e) for scopes.
- [CLIPS conflict resolution strategies](https://www.csie.ntu.edu.tw/~sylee/courses/clips/bpg/node5.3.html)
  (depth, breadth, simplicity, complexity, lex, mea, random) and
  [Clara rules: conflict resolution and salience](http://www.clara-rules.org/docs/conflictsalience/).
- [Drools decision tables in spreadsheets](https://docs.drools.org/5.4.0.CR1/drools-expert-docs/html/ch06.html):
  a PRIORITY column sets salience per row — the table-plus-number combination.

## Scopes, cascades, and specificity (`03`, `13`)

- [Bifrost routing rules](https://docs.getbifrost.ai/providers/routing-rules): "the first matching rule
  wins… within each scope, rules are sorted by priority (ascending: 0 evaluates before 10)."
- [Bifrost provider routing](https://docs.getbifrost.ai/providers/provider-routing): scope hierarchy
  VirtualKey → Team → Customer → Global, first-match-wins.
- [Maxim — LLM gateway routing, fallback and governance in Bifrost](https://www.getmaxim.ai/articles/llm-gateway-routing-fallback-and-governance-in-bifrost/),
  [Towards AI — Dynamic model routing](https://pub.towardsai.net/dynamic-model-routing-with-an-llm-gateway-df62023bc1c9):
  `chain_rule` re-evaluates the scope hierarchy with the resolved target as new context.
- [nite-coder/bifrost routes.md](https://github.com/nite-coder/bifrost/blob/main/docs/routes.md): NGINX-style
  "if a request matches two prefix rules, the longest matching rule takes priority."
- [MDN — Introduction to the CSS cascade](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Introduction),
  [MDN — Specificity](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity),
  [CSS-Tricks — Cascade Layers guide](https://css-tricks.com/css-cascade-layers/),
  [Wattenberger — The CSS Cascade](https://2019.wattenberger.com/blog/css-cascade): origin and importance →
  layers → specificity → scoping proximity → order of appearance; layers exist because source order was
  being used as a priority system.
- [Longest prefix match routing](https://networklessons.com/ip-routing/longest-prefix-match-routing),
  [AWS — influencing traffic with LPM](https://aws.amazon.com/blogs/networking-and-content-delivery/influencing-traffic-over-hybrid-networks-using-longest-prefix-match/),
  [ServerFault — specificity vs metric](https://serverfault.com/questions/648276/routing-selection-specificity-vs-metric):
  specificity as the primary key, order/administrative distance as tie-break.

## Match trees and large rule sets (`05`)

- [arXiv ESBMC-PLC](https://arxiv.org/pdf/2606.15461) (tree-structured condition semantics) and the
  packet-classification literature (`tcv`-style complete-predicate trees) — nodes carrying an observed
  value, a pattern, and child nodes ending in a decision leaf, as described in policy engines.
- Trie-based URL routing / longest-prefix tables: the same shape keyed on segments or bits.

## Statechart guard ladders (`12`)

- [Stately — Guards](https://stately.ai/docs/guards): "Each transition will be tested in order, and the
  first transition whose guard evaluates to true will be taken."
- [statecharts.dev — Guard](https://statecharts.dev/glossary/guard.html): "the guarded transitions are
  checked, one by one, and the first transition whose guard is true will be used, the others will not be."
- [IBM Rhapsody — specifying statechart guards](https://www.ibm.com/docs/en/engineering-lifecycle-management-suite/design-rhapsody/10.0.1?topic=statecharts-specifying-statechart-guards),
  [Sciencedirect — guard condition overview](https://www.sciencedirect.com/topics/computer-science/guard-condition).

## Visual / no-code builders (`12`)

- Workflow platforms' condition-block docs converge on: branches are evaluated top to bottom, the first
  matching condition wins, most specific or most likely first, fallback last (e.g. Synthflow's
  branching guidance and equivalent notes in agent-platform docs).

## Rules as data and expression languages (`06`)

- [CEL (Common Expression Language)](https://github.com/google/cel-spec) for bounded, side-effect-free
  policy expressions; [Socket / decision-table libraries](https://socket.dev) and
  [Code Effects vs DMN](https://codeeffects.com/content/business-rules-omg-dmn-feel-vs-code-effects) for
  the "when you outgrow tables, you need a full engine" boundary.
- [Bizzdesign / Camunda docs](https://docs.camunda.io/docs/components/best-practices/modeling/choosing-the-dmn-hit-policy/)
  for authoring tables that non-developers maintain.

## Attempt and escalation ladders (`11`)

- [Adaptive model routing and fallback logic with Bifrost](https://dev.to/kuldeep_paul/adaptive-model-routing-and-fallback-logic-routing-around-llm-provider-outages-with-bifrost-4g3m):
  "routing mechanisms execute in a deterministic order: routing rules evaluate first," then fallback.
- [Apinizer — routing and failover](https://docs.apinizer.com/en/ai-gateway/routing-and-failover) for
  provider/model fallback ordering and inheritance.

## Usage note

These pages describe *their* systems, and conventions diverge (Drools salience is higher-wins, Bifrost
priority is lower-wins, `.gitignore` and sudoers are last-match-wins, Cedar is deny-overrides). That
divergence is the reason `00` requires the ordering key, the mode, and the direction to be written down
instead of intuited. Where this skill states behavior without a citation, it is a design recommendation,
not a claim about a named product.
