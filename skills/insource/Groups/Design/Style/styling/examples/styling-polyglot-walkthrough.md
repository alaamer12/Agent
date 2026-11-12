# Worked scenario across four platforms

One scenario — a card with tone variants, a state-driven button, and a progress bar whose fill is
runtime data — shown before (the way it gets written under pressure) and after, on [HTML/CSS],
[Blazor], [.NET MAUI], and [Qt QML]. Same three layers everywhere: tokens, system, call site.

## HTML / Web

Before — the monolith, raw values, constructed class names, inline dump:

```html
<!-- styles.css: 4,000 lines, everything in it -->
<div class="bg-{{ themeColor }}-100" style="padding:16px;border-radius:12px;
     background:{userColor};box-shadow:0 2px 8px rgba(0,0,0,.3)">
  <button onclick="btn.className = 'btn ' + (busy ? 'btn-loading-red' : 'btn-idle-green')">
</div>
<script>
  bar.style.width = pct + "%";
  document.styleSheets[0].insertRule(`.x${pct}{width:${pct}%}`); // per-value rule: leak
</script>
```

After — scoped files, tokens, mapping, runtime variable:

```css
/* tokens.css (shared core) */
:root { --surface: #fff; --border: #e2e8f0; --radius-md: 12px; --space-4: 16px;
        --elevation-1: 0 2px 8px rgb(0 0 0 / .08); --accent: #2563eb; --on-accent: #fff; }
[data-theme="dark"] { --surface: #0f172a; --border: #334155; }

/* dashboard/card.css (module scope) */
.card { background: var(--surface); border: 1px solid var(--border);
        border-radius: var(--radius-md); padding: var(--space-4); }
.primary-card   { box-shadow: var(--elevation-1); }
.secondary-card { background: var(--surface-muted); }
.progress > .bar { width: var(--fill, 0%); background: var(--accent); }
.btn[aria-busy="true"] { opacity: .6; pointer-events: none; }
```

```tsx
const toneClass = { primary: "primary-card", secondary: "secondary-card" } as const;

<div class={cx("card", toneClass[tone], className)}
     style={{ "--border-color": userChosenColor } as CSSProperties}>   /* runtime value, named channel */
  <button class="btn btn--primary" aria-busy={busy}>                  /* state attribute, not class math */
  <div class="progress" style={{ "--fill": `${pct}%` } as CSSProperties}>
    <div class="bar" />
  </div>
</div>
```

## Blazor

Before — one global `site.css`, hard-coded hex in components, per-render class strings:

```razor
<div style="background:#fff;padding:16px;border-radius:12px"
     class="@("card-" + tone.ToString().ToLower() + (dark ? " dark" : ""))">
```

After — CSS isolation + tokens referenced, never built:

```razor
<!-- Components/Dashboard.razor -->
<div class="card @ToneClass[Tone]" style="--fill:@(Fraction.ToString("P0", CultureInfo.InvariantCulture))">
    <Progress class="progress" />
</div>

@code {
    [Parameter] public Tone Tone { get; set; }
    [Parameter] public double Fraction { get; set; }
    private static readonly Dictionary<Tone, string> ToneClass = new()
    {
        [Tone.Primary] = "primary-card",
        [Tone.Secondary] = "secondary-card",
    };
}
```

```css
/* Components/Dashboard.razor.css — scoped by the compiler; consumes shared tokens */
.card        { background: var(--surface); border: 1px solid var(--border);
               border-radius: var(--radius-md); padding: var(--space-4); }
.progress ::deep .bar { width: var(--fill, 0%); background: var(--accent); }
```

Theme values still come from one `tokens.css` map at `wwwroot` level; isolation scopes structure,
tokens keep the single source of truth.

## .NET MAUI

Before — literals at consumption sites, a new style swapped in code-behind per state:

```xml
<Frame BackgroundColor="#FFFFFF" CornerRadius="12" Padding="16" />
```

```csharp
card.Style = isDark ? darkStyle : lightStyle;   // style chosen in logic, values duplicated
```

After — role tokens as `DynamicResource`, keyed styles with `BasedOn` as the variant registry,
state through `VisualStateManager`, numbers through bindings:

```xml
<!-- Tokens/Colors.xaml (merged at app level): values exist once -->
<Color x:Key="Surface">#FFFFFF</Color>
<Color x:Key="Accent">#2563EB</Color>
<x:String x:Key="RadiusMd">12</x:String>

<!-- Features/Dashboard/Styles.xaml: base + thin variant layers -->
<Style x:Key="Card" TargetType="Frame">
  <Setter Property="BackgroundColor" Value="{DynamicResource Surface}" />
  <Setter Property="CornerRadius"    Value="{DynamicResource RadiusMd}" />
  <Setter Property="Padding"         Value="16" />
</Style>
<Style x:Key="PrimaryCard" TargetType="Frame" BasedOn="{StaticResource Card}">
  <Setter Property="BorderColor" Value="{DynamicResource Accent}" />
</Style>
```

```xml
<Frame Style="{DynamicResource PrimaryCard}">
  <ProgressBar Progress="{Binding Fraction}" />   <!-- runtime data via binding, not generated styles -->
  <Button Text="Save">
    <VisualStateManager.VisualStateGroups>
      <VisualStateGroup x:Name="Common">
        <VisualState x:Name="Busy"><VisualState.Setters>
          <Setter Target="SaveButton.IsEnabled" Value="False" />
        </VisualState.Setters></VisualState>
      </VisualStateGroup>
    </VisualStateManager.VisualStateGroups>
  </Button>
</Frame>
```

Theme flip = swap the token dictionary's values (or use platform-aware resources); the styles
above consume roles, so no page changes and no `Style = ...` branching in code-behind.

## Qt QML

Before — inline literals everywhere, JS assigning colors at runtime:

```qml
Rectangle { color: "#ffffff"; radius: 12; padding: 16 }
Component.onCompleted: bar.color = app.darkMode ? "#0f172a" : "#ffffff"  // theme logic at call site
```

After — a `Theme` singleton (tokens), a base card the variants `inherit`, bindings for runtime
values, `states` for discrete UI state:

```qml
// Theme.qml (pragma Singleton — one authority)
QtObject {
    property color surface: "#ffffff"
    property color accent:  "#2563eb"
    property real  radiusMd: 12
    property color textPrimary: "#0f172a"
}

// Card.qml (base pattern)
Rectangle { color: Theme.surface; radius: Theme.radiusMd; padding: 16; border.color: Theme.border }

// PrimaryCard.qml (upper layer via inherit)
Card { border.color: Theme.accent }

// usage
PrimaryCard {
    ProgressBar { position: model.fraction }                    // runtime data as binding
    Button {
        states: State {
            name: "busy"; when: control.busy
            PropertyChanges { control.enabled: false; control.opacity: 0.6 }
        }
    }
}
```

Dark mode = the singleton reassigns role values (or Controls' style does it); call sites never
mention themes.

## What stayed identical across all four

1. Values live once, under role names; components consume roles.
2. Variants are declared names (`primary-card`, keyed `BasedOn` styles, `inherit` types) — never
   constructed strings.
3. Discrete state goes through the platform's own state mechanism (`aria/data`, bound class name,
   `VisualStateManager`, QML `states`).
4. Continuous runtime values enter as one named number (`--fill`, `Progress`, `position`) — inline
   only carries the value, the style layer carries the look.
5. Each module's style scope is its own file; the shared core is tokens + base + utilities only.
