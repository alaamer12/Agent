# Worked Walkthrough: Accessibility Architecture for a Clinical & Operations Portal

> **Scenario:** A healthcare operations platform (MedFlow) used by doctors, nurses, and administrative dispatchers across desktop workstations and tablet devices.

---

## 1. Discovery Interview Transcript (Summary)

**Agent:** *"We are establishing MedFlow's architecture. Who uses this system, and under what conditions?"*
**User:** *"Nurses and dispatchers stare at it for 12-hour shifts. Some work in dim triage rooms, others under harsh fluorescent lights. We have lots of complex patient charts and fast-moving triage queues. Several clinicians have dyslexia, and eye fatigue is a huge complaint."*

**Agent:** *"Understood. For visual adaptation and eye-comfort, should we introduce a High-Contrast mode for dimmed triage screens, plus warm-paper and muted slate presets to fight glare during long shifts?"*
**User:** *"Yes! Exactly. Pure black dark mode gives clinicians headaches, but a soft slate dark mode and a warm cream mode would be perfect. Also, high contrast for emergency triage is essential."*

**Agent:** *"For typography and cognitive load: should we support dyslexia-optimized fonts (like Lexend/Atkinson Hyperlegible), dynamic zoom without clipping, and density tiers (Compact for emergency dispatchers vs Spacious with full explanations for junior nurses)?"*
**User:** *"Yes! Dispatchers need maximum rows on their screens, but chart review needs comfort reading without distractions."*

**Agent:** *"Lastly, regarding autonomy and permissions: should we enforce a strict ban on cold browser notification prompts, requiring explicit opt-in only when setting patient alarms, with zero unprompted modal takeovers?"*
**User:** *"Absolutely. Unexpected popups during clinical entry are dangerous."*

---

## 2. Resulting Architecture Output (`<docs>/architecture/accessibility-architecture.md`)

```markdown
# MedFlow — Accessibility Architecture Specification

## 1. Visual Adaptation Architecture
- **Root Theming Engine**: CSS variables supporting `data-theme="light|slate|warm-cream"` and `data-contrast="normal|high"`.
- **Triage High-Contrast Mode**:
  - Secondary metadata boosted from `#64748b` (4.5:1) to `#0f172a` (12:1).
  - Triage urgency status pills (Critical, Urgent, Stable) use dual-encoding: distinct border shapes + text labels + high-contrast ink (never color alone).
- **Shift Eye-Comfort Presets**:
  - `slate`: `#1e293b` background with `#f8fafc` text (low-glare night shift).
  - `warm-cream`: `#faf7f2` background with `#27272a` text (fluorescent daylight shift).

## 2. Typography & Dyslexia Support
- Font-family selector in Clinician Preferences:
  - `Default Sans`: Inter / System-UI
  - `Dyslexia-Optimized`: Lexend (weighted baselines and wide apertures)
- Fluid rem-based typography: Layout scales gracefully to 200% zoom with automatic table horizontal scrolling (zero text truncation or CSS `overflow: hidden` on vital patient notes).

## 3. Cognitive Density & Focused Reading
- **Density Tiers**:
  - `compact`: 28px table rows, 4px cell padding for multi-bed triage dispatchers.
  - `spacious`: 48px rows, full vital status badges and step-by-step medication administration prompts.
- **Triage Focus Mode**:
  - Single-key toggle (`Alt + F`) hides department navigation rails and patient lists, dedicating 100% of viewport to the active patient chart with a 65ch reading measure.

## 4. Permission Hygiene & Interruption Safety
- Zero browser alert prompts on load.
- Alarms and alerts are queued in a persistent non-modal status ticker; high-severity emergency overrides trigger sound only if clinician enabled audio alerts for that specific ward.
- Destruction of records requires two-step confirmation with a 15-second undo toast buffer.
```
