# Product Feel & Brand Identity

The `## Overview & Product Feel` section is the emotional and operational anchor of `DESIGN.md`. When an agent faces an ambiguous edge case not covered by a specific rule, it relies on this section to make the correct aesthetic decision.

---

## 1. The Three-Question Discovery

Before writing a single color or token, answer these three questions with the user:

### 1.1 The Metaphor Test
> *"If this product were a physical object, vehicle, or architectural space, what would it be?"*
- **Surgical Tool / Cockpit**: Linear, Bloomberg Terminal, Ableton Live (dense, high contrast, zero fluff, immediate tactile feedback).
- **Architectural Gallery**: Figma, Apple, Stripe (balanced white space, precise typography, deliberate hero moments).
- **Warm Editorial / Workshop**: Notion, Basecamp, Substack (generous line height, readable serif or grotesque sans, relaxed density).
- **Industrial Utility**: AWS Console, GitHub, Grafana (monospaced data, information-dense tables, low cognitive friction).

### 1.2 The Emotional Adjective Triad
Pick exactly three opinionated adjectives that describe the user's emotional state inside the application:
- Examples: `Calm, Surgical, Trustworthy`
- Examples: `Vibrant, Playful, Unapologetic`
- Examples: `Quiet, Authoritative, Focused`

### 1.3 The Explicit Negative Identity ("What We Are Never")
State what the brand must **never** be perceived as:
- *"Never playful or toy-like (no bouncy spring physics, no pastel pill buttons)."*
- *"Never sterile or generic enterprise (no washed-out gray table headers, no cookie-cutter Bootstrap vibes)."*
- *"Never hyperactive or noisy (no glowing gradient borders, no decorative background mesh blobs)."*

---

## 2. Defining the Product Register

| Register | Primary Audience | Key Characteristics | Target Density |
|---|---|---|---|
| **Operational SaaS** | Developers, Ops, Analysts | High density, tabular data, dark/slate mode, fast keyboard shortcuts | Compact (32px–36px controls) |
| **Consumer Web / App** | Everyday users, mobile-first | Friendly touch targets, warm neutrals, approachable type, generous whitespace | Spacious (44px–48px controls) |
| **B2B Productivity** | Knowledge workers, teams | Moderate density, clear hierarchy, calm surface borders, subtle states | Standard (36px–40px controls) |
| **Showcase / Marketing** | Prospective customers | Bold typography, high-impact photography, deliberate hero entrances | Fluid & Editorial |

---

## 3. Authoring the Overview Section

A production-ready Overview section follows this template:

```markdown
## Overview & Product Feel

[Product Name] is a [category/domain] designed for [target users] to [core job to be done].

### Personality Statement
The product embodies the feel of an **engineered precision instrument**. Every element must earn its place; visual ornamentation that does not contribute to data legibility or workflow efficiency is eliminated. The UI prioritizes cognitive calm, tabular alignment, and immediate feedback over flashy decoration.

- **Tone**: Focused, calm, and surgical.
- **Visual Stance**: Architectural sharpness with minimal 4px radii, hairline 1px borders, and deliberate typographic scale.
- **Explicit Anti-Identity**: We are never a generic template, never playful with cartoonish bounce physics, and never cluttered with ungrounded floating cards.
```
