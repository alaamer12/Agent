# Display Architecture Principles — the four domains

## 1. The notation spectrum

One value, legitimate forms, ordered by what the reader is doing:

| level | form | example | the reader's question | where it belongs |
|---|---|---|---|---|
| **L0 exact** | every digit true | `4,982,317` / `٤٬٩٨٢٬٣١٧` | "what exactly?" | receipts, invoices, reconciliation tables, counters being acted on, legal/financial statements |
| **L1 grouped** | full magnitude, readable | `5,000,000` | "how big, roughly exactly?" | report bodies, table cells with room, article text quoting figures |
| **L2 compact** | abbreviated scale | `5M`, `4.98M`, `500K` | "about how many?" at a glance | stat cards, badges, chart axes, chips, mobile rows |
| **L3 prose** | rounded, spoken | "nearly 5 million", "about 5M" | "give me the story" | empty-state copy, notifications, marketing, onboarding |
| **source-side** | digit separators | `500_000` | developer legibility | code literals and seed data ONLY — never rendered to a user |

Rules that make it an architecture instead of a preference:

- The level is **assigned per surface class** in the display doc before implementation; the
  implementer picks the level's form for the locale, not the level itself.
- **No silent downgrades.** A receipt rendering `5M` is a lie by rounding; a dashboard spending
  L0 on every card is noise. When a surface shows L2, the L0 value must be reachable (tooltip,
  detail route, `sr-only` span) — compression hides, never destroys.
- Thresholds are written, not felt: e.g. dashboards switch to compact at ≥ 10,000; tables keep
  grouped up to the column budget, then the fallback ladder (§2) runs; financial products may
  pin everything L0. The doc records the actual chosen numbers.
- Mixed levels in one visual comparison are a defect: if two figures sit side by side to be
  compared, they share a level and a denominator ("5M of 8M" works; "5M of 8,213,004" does not).

## 2. Container-fit discipline

A display slot is a contract: **the container declares what it can hold; the notation conforms
to it.** The failure that named this rule: a fixed-width KPI card (`min-height`, oversized
`text-[32px]` value) rendering raw `5,000,000` struck through the card boundary — the number was
correct and the display was broken.

- **Budgets are per slot, in characters-at-style** (or measured width in `ch` of the value's
  typeface), stated in the surface-class table: card value ≤ 6 glyphs at display size, table
  column ≤ 11, axis tick ≤ 4.
- **Fallback ladder, declared not improvised**: L0 → L1 → L2 → abbreviated + expand affordance
  (tooltip / detail / press-and-hold). The ladder ends in *reachability of the exact value*, so
  the last rung never truncates meaning — ellipsis alone is a dead end.
- **Tabular figures** (`font-variant-numeric: tabular-nums`, lining by default) wherever digits
  align, update, or animate — proportional digits jitter, and jitter is the ui pillar's CLS
  violation wearing a typography costume. Count-up animations reserve the widest frame.
- **Worst-case test strings** are part of the spec: every slot is verified against the widest
  legitimate value of its level in its widest target locale — `999,999,999,999`, its German
  `999.999.999.999`, and its Arabic-Indic form (which renders wider). A slot that survives only
  the demo data failed.

## 3. Locale display rules (i18n)

Formatting is **delegated to the locale layer, always**: `Intl.NumberFormat` / `Intl.DateTimeFormat`
/ ICU message files in whatever the stack provides — never hand-rolled comma math, never
`toFixed()` dressed as i18n. What the architecture declares once, app-wide:

- **Numerals**: Western-Arabic (`5,000,000`) vs Arabic-Indic (`٥٬٠٠٠٬٠٠٠`) is a product voice
  decision, not a per-screen one; the choice is recorded and applied through the locale tag, and
  never mixed across surfaces of one product.
- **Separators and spacing** come from the locale (`5.000.000` de, `5 000 000` fr with NBSP,
  `٥٬٠٠٠٬٠٠٠` ar); currency symbol position, minus-sign form, and percent spacing too.
- **Calendars**: Gregorian default; Hijri (or product calendar) only by written decision, with
  conversion rules for storage (stays ISO; calendars are display-layer).
- **Plurals**: ICU plural categories, including Arabic's zero/one/two/few/many — "٥ أيام" is not
  "5 day(s)"; the `n==1 ? 's' : ''` pattern is a defect in any RTL-targeting product. Message
  files carry the plural forms, the code carries only the number.
- **Bidi hygiene**: every number, unit, identifier, URL, and mixed-direction fragment inside RTL
  text is **isolated** (`<bdi>`, `dir="auto"`, or FSI…PDI at the text layer) — visual order is
  not logical order, and an unisolated "5M" in an Arabic sentence can reorder or strand its
  sign. Layout mirroring belongs to the ui pillar; string-level direction safety belongs here.
- **Expansion budgets feed §2**: Germanic/Finnish +30–40% over English; Arabic labels are
  compact but digit forms are wider. The container table's worst-case row is locale-aware.

## 4. Voice ↔ medium ↔ typeface

The voice register (AGENTS.md section 18 where the rulebook owns it) is not only *what* is said —
the medium says it too. A typeface carries a voice; a notation level carries one as well; all
three must corroborate:

| surface class | voice register | medium (typeface + figures) | notation | coherent? |
|---|---|---|---|---|
| ops console / admin | terse, professional | grotesk, tabular lining figures | L0/L1 with compact chips | audit-familiar |
| marketing stat | confident, friendly | rounded display face, proportional | L2/L3 prose | trustworthy-approachable |
| legal / financial doc | exact, neutral | serif, lining tabular | L0 only | weight-bearing |
| consumer mobile glance | warm, simple | system UI face | L2 max | low-ceremony |

- **Not every voice matches every typeface and vice versa.** The pairing roster is declared per
  surface class as a triple; introducing a typeface or a voice change reopens the roster row for
  every surface it touches (same-change duty — this is a sync block in the rulebook's sense).
- **Mismatch is a defect class**: playful rounded display carrying reconciliation figures;
  monospaced code-feel in consumer prose; L3 rounding inside an L0 contract. Review checks the
  triple, not each half.
- **Precedence rule, absolute**: the accessibility pillar's user choices (font switcher,
  dyslexia-friendly face, 200% zoom, density tier) override any pairing — the pairing defines
  defaults, never locks. When user-selected typeface changes metrics, §2's budgets recompute
  against the widest allowed face, not the default one.
- **The medium reaches notation**: same value, different voice surfaces — dashboard `4.98M`,
  receipt `4,982,317`, empty-state "almost five million". The architecture maps each surface's
  voice to its level; no surface freelances between them.