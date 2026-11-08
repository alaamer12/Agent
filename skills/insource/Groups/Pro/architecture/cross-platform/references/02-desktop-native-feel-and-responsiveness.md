# 02 — Desktop Native Feel & Form-Factor Responsiveness

> Architectural guidelines for delivering first-class desktop and tablet experiences. Eradicating the "stretched phone app" anti-pattern through window awareness, hover interactions, keyboard orchestration, and contextual menus.

---

## 1. The "Stretched Mobile" Smell

A cross-platform app compiled for macOS or Windows that looks and behaves like an oversized phone screen is an architectural failure. The symptoms are unmistakable:
- Full-width touch bars stretching across a 32-inch 4K monitor.
- Giant touch-target buttons with no mouse hover state or cursor change.
- Modals that slide up from the bottom of the screen covering the entire desktop display.
- Inability to resize, tile, or operate in multi-window environments.
- Total absence of keyboard navigation, accelerators, and right-click context menus.

```
                    ❌ THE STRETCHED PHONE (WRONG)
┌────────────────────────────────────────────────────────────────────────┐
│ [≡] Search                                                (User Avatar)│
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│                      Search Input Box (Massive)                        │
│                                                                        │
│                        Card 1 (Full 1920px wide)                       │
│                                                                        │
│                        Card 2 (Full 1920px wide)                       │
│                                                                        │
├────────────────────────────────────────────────────────────────────────┤
│  [ Home ]            [ Search ]            [ Profile ]    (Bottom Bar) │
└────────────────────────────────────────────────────────────────────────┘

                    ✅ NATIVE DESKTOP ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────┐
│ App Title / Menu Bar (File  Edit  View  Window  Help)           [-] [X]│
├───────────────┬────────────────────────────────────────────────────────┤
│ Navigation    │ Search [ Ctrl+K ]                         Sort [v]  ⚙  │
│ Sidebar       ├────────────────────────────────────────────────────────┤
│               │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│ • Dashboard   │ │ Grid Card 1  │ │ Grid Card 2  │ │ Grid Card 3  │ ... │
│ • Analytics   │ └──────────────┘ └──────────────┘ └──────────────┘     │
│ • Settings    │ Right-click context menus, hover row highlights,       │
│               │ multi-pane details, and precise cursor feedback.       │
└───────────────┴────────────────────────────────────────────────────────┘
```

---

## 2. Window Architecture & Resizing Resilience

Desktop applications exist in dynamic windowed environments. Unlike mobile apps that occupy full screen space, desktop layouts must handle:
1. Continuous dynamic resizing without state destruction.
2. Minimum, maximum, and default window geometry constraints.
3. Multi-window workflows (e.g. detaching an inspector, opening a secondary document).

### Breakpoint Architecture vs. Device Idiom

Never query `DeviceInfo.Idiom == Desktop` to decide layout widths. Instead, use an architectural container that responds to available width thresholds:

```typescript
// architecture/responsive/BreakpointContainer.ts
export type Breakpoint = 'compact' | 'medium' | 'expanded';

export function resolveBreakpoint(width: number): Breakpoint {
  if (width < 600) return 'compact';      // Typical Phone
  if (width < 1024) return 'medium';     // Tablet portrait / Small Desktop window
  return 'expanded';                     // Full Desktop / Large Tablet landscape
}
```

---

## 3. Interaction Mechanics: Pointer, Hover & Cursors

Touch screens use direct finger manipulation (tap, pinch, drag). Desktop environments use indirect high-precision pointing devices with distinct phases:
- **Hover Phase:** Elements must visually respond *before* click (subtle elevation, border contrast, background tint).
- **Cursor Management:** Interactive elements must declare their cursor intent (`pointer`, `text`, `grab`, `not-allowed`).
- **Scroll Wheel & Trackpad:** Smooth kinetic scrolling with discrete delta handling.

### Behavior Injection Pattern (Polyglot)

Isolate pointer behavior from core business logic using composable interaction behaviors:

#### React Native / Web
```tsx
// ui/behaviors/HoverableCard.tsx
import { useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

export function HoverableCard({ children, onClick }: CardProps) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Pressable
      onPress={onClick}
      // @ts-ignore - Web / Desktop specific pointer props
      onHoverIn={() => setIsHovered(true)}
      onHoverOut={() => setIsHovered(false)}
      style={[
        styles.base,
        isHovered && styles.hovered,
        { cursor: 'pointer' }
      ]}
    >
      {children}
    </Pressable>
  );
}
```

#### .NET MAUI / C#
```csharp
// UI/Behaviors/PointerHoverEffect.cs
namespace App.UI.Behaviors;

public class PointerHoverEffect : PlatformBehavior<VisualElement>
{
    public Color HoverColor { get; set; } = Colors.LightGray.WithAlpha(0.2f);
    private Color _originalColor;

#if WINDOWS || MACCATALYST
    protected override void OnAttachedTo(VisualElement bindable)
    {
        base.OnAttachedTo(bindable);
        var pointerGesture = new PointerGestureRecognizer();
        pointerGesture.PointerEntered += (s, e) => {
            _originalColor = bindable.BackgroundColor;
            bindable.BackgroundColor = HoverColor;
        };
        pointerGesture.PointerExited += (s, e) => {
            bindable.BackgroundColor = _originalColor;
        };
        bindable.GestureRecognizers.Add(pointerGesture);
    }
#endif
}
```

---

## 4. Keyboard Orchestration & Accelerators

A desktop app without keyboard shortcuts is unusable for power users. Cross-platform architecture must accommodate:
1. **Focus Rings:** Visible, high-contrast tab navigation indicators.
2. **Global Shortcuts:** e.g., `Ctrl+F` / `Cmd+F` (Search), `Ctrl+S` (Save).
3. **Modal Escapes:** Pressing `Esc` must cleanly dismiss overlays, flyouts, and dialogs.

```
                    Keyboard Event Bus
                            │
               ┌────────────▼────────────┐
               │    KeyBindingRegistry   │
               └────────────┬────────────┘
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
  [ Ctrl+K / Cmd+K ]     [ Escape ]       [ Tab Navigation ]
  Trigger Global Search  Close Flyout     Focus Next Cell
```

---

## 5. Contextual Menus & Native Modals

Never force a full-screen sliding modal onto a desktop monitor. Use contextual UI concepts:

| Mobile Paradigm | Desktop Native Paradigm |
| :--- | :--- |
| Long-press triggers full-width ActionSheet | Secondary click (Right-click) opens a native Context Menu positioned at cursor |
| Bottom modal sheet covering bottom 60% of viewport | Anchored flyout / Popover attached directly to the invoking button |
| Full-screen settings view | Multi-tab Preferences window or modal dialog with explicit OK/Cancel buttons |
| In-app navigation stack with back arrow | Window Titlebar navigation, back/forward mouse buttons, or keyboard history shortcuts |
