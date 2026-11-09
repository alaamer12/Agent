# domain

> This document defines the `domain` steering folder: the business concepts, entities, roles, lifecycle states, and vocabulary that carry relationships and behavior. It lives in the **perception tier** (`perception/`); see [`index.md`](index.md) for the taxonomy overview.

**Holds.** The domain model: entities, roles, lifecycle states, and concepts that have relationships and business meaning. It tells the reader what things exist in this world and how they connect to one another (sentence shape: *"An X is a Y that belongs to Z"*).

**Shape.** Topic-named Markdown files (e.g., `user-tiers.md`, `leagues.md`, `portfolio-concepts.md`).

**Does not hold.**
- Why the product exists or its high-level audience overview ([`product.md`](product.md)).
- What the system does or transitions it executes ([`capabilities.md`](capabilities.md)).
- Rules about what is permitted or forbidden ([`policy.md`](policy.md)).
- Bare dictionary definitions with no relationships (which belong in a glossary outside the taxonomy; see [`placement.md`](placement.md)).
- Technical database tables, column types, or schemas (which belong in technical reference documentation outside the taxonomy).

**The test.** Nouns and relationships. If the sentence defines a concept, an entity, a role, or a lifecycle state, it belongs in `domain`.
- *Goal-change test*: If the organization changes its business goals or marketing audience, `product` changes while `domain` remains stable. If a new business entity or tier is created, `domain` changes.
- *Reference test*: If other documents link to this passage to understand what a term means and how it relates to other entities, it is `domain`.

**Example (`perception/shared/domain/user-tiers`).**
"A user tier represents the experience and autonomy level of an account holder. There are three tiers. The youngest tier is managed by a guardian account, which has oversight of the child's progress and savings goals."

**Example (`perception/shared/domain/group-competitions`).**
"A competition group is an association of users competing on shared return metrics. A group belongs to either an institution or a family, has a membership roster, and progresses through three lifecycle states: open, active, and concluded."
