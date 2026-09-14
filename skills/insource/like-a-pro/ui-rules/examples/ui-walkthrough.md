# Cross-Platform Walkthrough: Applying ui-rules

This walkthrough demonstrates how an AI agent executes the `ui-rules` skill for applications with visual user interfaces across different frontend technologies.

---

## Pre-Check: UI Activation Gate
The agent inspects the application targets:
- `apps/api`: Headless backend service → **UI rules bypassed.**
- `apps/web`: React Next.js web application → **UI rules activated.**
- `apps/mobile`: Flutter or React Native mobile client → **UI rules activated.**

---

## Step 1: Inquiring & Agreeing on Responsive Breakpoints
The agent discusses form factors with the user:
- Web: Mobile (< 640px), Tablet (640–1024px), Desktop (> 1024px).
- Adaptive strategy: Responsive CSS Grid/Flexbox reflow for web; PlatformSelect block layout swapping for cross-platform clients.

---

## Step 2: Skeleton Loading & Zero CLS Discipline
The agent reviews asynchronous loading states:
- Skeletons use CSS animation or native shimmer controls with exact height/width matching target card components.
- Avoid content jumping by reserving fixed vertical space for headers and actions.

---

## Step 3: Internationalization (i18n) & Text Directionality Discovery
The agent inquires whether the application serves a single locale or multi-lingual/bidirectional audiences:
- *Single-locale LTR (e.g. English-only):* Standard directional layout, single primary font family.
- *Multi-lingual or Bidirectional (e.g. LTR + RTL):*
  - Use logical properties (`margin-inline-start`, `padding-inline-end`) or native alignment abstractions so layout mirrors seamlessly.
  - Wrap mixed numerical values, currencies, or handles in Unicode bidi isolation markers (`\u2068...\u2069`).
  - Configure appropriate script font cascades (e.g., choosing legibility-optimized typefaces matching each supported target language script).

---

## Step 4: Component Implementation Snippets

### Example A: React / Tailwind Web Card Component
```tsx
export function ProjectCardSkeleton() {
  return (
    <div className="p-4 rounded-xl border border-border bg-card animate-pulse space-y-3">
      <div className="h-5 bg-muted rounded w-3/4" />
      <div className="h-4 bg-muted rounded w-1/2" />
      <div className="pt-2 flex justify-between">
        <div className="h-4 bg-muted rounded w-20" />
        <div className="h-4 bg-muted rounded w-16" />
      </div>
    </div>
  );
}
```

### Example B: Cross-Platform Component (Responsive with Dynamic Flow)
```xml
<Grid Style="{StaticResource ProjectCardGrid}"
      FlowDirection="{Binding AppLocale.FlowDirection}">
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto" />
        <RowDefinition Height="Auto" />
    </Grid.RowDefinitions>
    
    <Label Text="{Binding Title}"
           FontFamily="{StaticResource PrimaryHeadlineFont}"
           LineBreakMode="TailTruncation"
           MaxLines="2" />
</Grid>
```

---

## Step 5: Output Artifact
The agent writes the complete UI conventions to:
`.repertoire/.steering/<app-name>/tech/ui-rules.md`
