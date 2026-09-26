<!--
  A short excerpt illustrating the TONE and SHAPE of a run-mining Phase 4
  output — the counterpart to distillation-excerpt.md (which shows read-mining).
  Not a template to fill and not a complete example. The point: unlike a
  read-mining run, ONE thing here is deliberately structured — the score table —
  because the comparison *is* the deliverable. Everything around it is the same
  free-form, cause-and-cost reasoning as any distillation: it leads with the
  conclusion, not a per-candidate recap, and it ends by naming when the ranking
  flips. Note the honesty markers a read-mining checkpoint uses, carried over:
  reach bounds ("7 of 12 hard cases"), a stated-vs-judged label on the subjective
  metric, and every specific claim traceable to a run you actually executed.
-->

**Trial:** 12 frozen OCR inputs chosen to break, not flatter — a skewed phone
photo of a receipt, a two-column scanned page, handwriting, low-contrast white-on-
grey, a table with no ruling, Devanagari and Arabic text, a screenshot, a blurred
frame. Every engine got the identical PNGs, same 8 s-per-image wall clock, one
cold run each after a warm-up. "Correct" = field-level match against hand-keyed
ground truth; a crash or a blank on an input is a gate-fail, not a zero.

| Engine | Correct @ hard (of 12) | Latency p50 | Peak RSS | Gate | Ship-ready license |
|---|---|---|---|---|---|
| Tesseract 5 + tiling | 7 | 2.6 s | 410 MB | pass | Apache-2.0 |
| cloud-ocr-A | 11 | 0.9 s | 60 MB | pass | **paid / no self-host** |
| docstruct-ml | 9 | 4.8 s | 1.9 GB | pass | MIT |
| pdf-parse-native | 3 | 0.1 s | 25 MB | **fails all scanned inputs** | MIT |
| hybrid: tesseract → cloud-ocr-A on low-confidence | **11** | 2.9 s | 430 MB | pass | Apache-2.0 **+ paid on fallback** |

The headline is boring until you look at *which seven* Tesseract clears and
*which four* it doesn't: it is excellent on clean captures and screenshots and
falls over entirely on handwriting and the unruled table, which is exactly where
the cloud engine earns its keep — and exactly the two cases the mobile product
actually ships. So the raw-accuracy column and the deployment decision point in
opposite directions. pdf-parse-native is the control that proves the fixture set
was real: it never had a chance on images and we would have shipped it as a
"fast, dependency-free win" on the easy inputs alone.

The hybrid is the honest recommendation for *this* product, and it is a
different answer than "highest accuracy wins" would imply: run the cheap local
engine, and pay the cloud call only on the low-confidence outputs, which are the
handwriting/table cases and turn out to be ~15% of real traffic. That trades the
cloud engine's per-call cost down to a fraction of requests while keeping its
accuracy on the inputs that matter. It also inherits a license tail the pure
Tesseract path does not — a paid dependency stays in the build even if it's
called rarely — which is the cost side of the decision, stated because the table
can't show it. **If you are allowed to send images to a third party and the per-
call budget is genuinely open, just take cloud-ocr-A and skip the hybrid.** The
ranking inverts the moment self-hosting and data-residency stop being
constraints; they were doing quiet work in every row above.

Two caveats that survive into any use of this table. The accuracy denominator is
12 inputs — enough to separate engines that fail hard, not enough to rank the top
two from their four-point margin, so "hybrid ≈ cloud" is a tie inside the noise,
not a 2-point win. And the style/UX judgement bundled into "usable output" was
ours, not measured against a user — a `judged` claim, not a `stated` one.

...
