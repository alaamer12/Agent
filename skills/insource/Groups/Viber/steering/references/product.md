# product

> This document defines the `product` steering folder: the high-level overview of what the product is, for whom, and why. It lives exclusively in the **perception tier** (`perception/product/`); it does not exist in the technical tier. See [`index.md`](index.md) for the taxonomy overview.

**Holds.** The product-level overview:
- **Purpose**: Why the product exists and the problem it solves.
- **Target Audience**: High-level user segments, each described in a single concise sentence.
- **Key Features (High Level)**: The core pillars of the offering in broad strokes.
- **Business Objectives**: Measurable product and growth goals.

The entire product overview document should be concise enough to be read in two minutes.

**Does not hold.**
- Detailed concept, entity, or state definitions (which belong in [`domain.md`](domain.md)).
- Specific system calculations or execution behavior (which belong in [`capabilities.md`](capabilities.md)).
- Business rules or constraints (which belong in [`policy.md`](policy.md)).
- Technical stack, architecture, or code layout (which belong in the `tech/` tier).
- Deep single-feature walkthroughs (which belong in feature documentation outside the taxonomy).

**The test.** Does it answer *"what is this product, for whom, and why?"* across the entire offering? If a sentence begins to define an entity, detail an audience tier's internal fields, or explain lifecycle states, it belongs in `domain.md`.

**The One-Sentence Audience Rule.** In `product`, describe each audience segment in a single sentence and point to `domain` for conceptual depth. For example:
> *"Audience: individual learners across three experience tracks, guardians managing youth accounts, and institutions sponsoring leagues; see `domain/user-tiers.md`."*

**Example (`perception/shared/product/overview`).**
"The platform is an interactive financial education simulator that teaches personal investing through risk-free virtual portfolios benchmarked against real-world fund prices. It aims to demystify mutual funds and build long-term financial literacy across all demographics."
