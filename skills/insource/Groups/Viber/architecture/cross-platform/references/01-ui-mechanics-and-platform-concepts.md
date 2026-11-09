# 01 — UI Mechanics, Platform Concepts & View Barrels

> Foundational architectural mechanics for cross-platform user interfaces. Distinguishing between uniform controls with native tweaks (`PlatformComponent`), divergent platform paradigms (`PlatformConcept`), layout separation via `View Barrels`, and build-time vs. runtime immutability.

---

## 1. The Core UI Dichotomy

In cross-platform engineering, confusing styling differences with architectural divergence is the root cause of brittle codebases. We classify every platform-specific UI requirement into one of two fundamental categories:

```
Platform UI Requirement
├── Same role, same layout structure, platform-specific touch/render?
│   └── PLATFORM COMPONENT (PlatformComponent)
│       e.g., Button, Checkbox, TextField, Slider, Modal Backdrop
│
└── Same functional goal, completely divergent interaction & layout paradigm?
    └── PLATFORM CONCEPT (PlatformConcept)
        e.g., Primary Navigation (Tabs vs. Sidebar vs. Drawer),
              Master-Detail (Drill-down push vs. Split-view pane),
              Context Actions (Bottom ActionSheet vs. Right-Click Context Menu)
```

---

## 2. PlatformComponents: Same Shape, Native Rendering

A `PlatformComponent` shares its interface, layout expectations, and visual signature across all targets. It requires native adaptation only for OS-level integration:
- Native focus outlines and keyboard navigation.
- Platform haptics or ripple effects on press.
- OS-specific text rendering metrics or elevation shadows.

### The `_X.{Family}` Pattern

Never leak OS checks into consumer call sites. Wrap platform variations inside private or internal helpers using the prefix `_X` or file-level suffix dispatch:

#### React Native / TypeScript
```tsx
// components/Button/_X.android.tsx
import { TouchableNativeFeedback, View } from 'react-native';

export function _ButtonSurface({ children, onPress, style }: SurfaceProps) {
  return (
    <TouchableNativeFeedback useForeground onPress={onPress}>
      <View style={style}>{children}</View>
    </TouchableNativeFeedback>
  );
}

// components/Button/_X.ios.tsx
import { TouchableOpacity } from 'react-native';

export function _ButtonSurface({ children, onPress, style }: SurfaceProps) {
  return (
    <TouchableOpacity activeOpacity={0.7} onPress={onPress} style={style}>
      {children}
    </TouchableOpacity>
  );
}

// components/Button/Button.tsx (Shared Consumer - Zero Platform Knowledge)
import { _ButtonSurface } from './_X';

export function Button({ label, onPress, variant }: ButtonProps) {
  return (
    <_ButtonSurface onPress={onPress} style={styles[variant]}>
      <Text style={styles.text}>{label}</Text>
    </_ButtonSurface>
  );
}
```

#### Flutter / Dart
```dart
// lib/ui/primitives/button/_x_surface.dart
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';

abstract class ButtonSurface {
  static Widget build({
    required BuildContext context,
    required VoidCallback onPressed,
    required Widget child,
  }) {
    if (defaultTargetPlatform == TargetPlatform.iOS || 
        defaultTargetPlatform == TargetPlatform.macOS) {
      return CupertinoButton(
        padding: EdgeInsets.zero,
        onPressed: onPressed,
        child: child,
      );
    }
    return InkWell(
      onTap: onPressed,
      child: child,
    );
  }
}
```

---

## 3. PlatformConcepts: Architectural Role Divergence

A `PlatformConcept` satisfies an abstract system requirement where the visual representation is radically different across device categories.

### Neutral Naming Law
> **The shared contract must be named for its abstract role, never after the visual construct of any single platform.**

| Prohibited Biased Name | Neutral Architectural Name | Mobile Representation | Desktop / Web Representation |
| :--- | :--- | :--- | :--- |
| `TabBar` / `BottomNav` | `NavigationShell` | Bottom Navigation Bar / Tabs | Left Collapsible Sidebar |
| `MasterDetailFlyout` | `HierarchicalExplorer` | Stack Navigator (Push/Pop) | Dual-Pane Split View |
| `ActionSheetPicker` | `ContextOptionSelector` | Bottom Sliding Sheet | Hovering Dropdown Menu |
| `PullToRefresh` | `DataRefreshTrigger` | Swipe-down gesture physics | Explicit Refresh Action Button |

---

## 4. View Barrels: Composition & Layout Separation

When an entire screen or complex view changes its layout architecture between form factors, **do not inject boolean checks or media queries inside child templates.**

Use a **View Barrel**. A View Barrel:
1. Connects to the single source of truth (`ViewModel`, `Store`, or `Hook`).
2. Owns state orchestration, event handling, and data binding.
3. Delegates purely to form-factor-specific layout trees.

```
                  ┌───────────────────────────────┐
                  │    SearchPageViewModel        │
                  │    (Data, Search, Results)    │
                  └──────────────┬────────────────┘
                                 │ Injected Props / State
                  ┌──────────────▼────────────────┐
                  │       SearchView (Barrel)     │
                  │   Selects Layout Representation│
                  └───────┬───────────────┬───────┘
                          │               │
            ┌─────────────▼─────┐   ┌─────▼─────────────┐
            │   SearchView.phone│   │  SearchView.desktop│
            │   Single Column   │   │  Multi-Column Grid │
            │   Bottom Sheets   │   │  Split Filter Pane │
            └───────────────────┘   └───────────────────┘
```

### Complete Implementation: Kotlin Multiplatform (Compose)

#### Contract & ViewModel
```kotlin
// shared/features/search/SearchViewState.kt
data class SearchUiState(
    val query: String = "",
    val results: List<SearchResultItem> = emptyList(),
    val isLoading: Boolean = false,
    val selectedFilter: String? = null
)

interface SearchPresenter {
    val state: StateFlow<SearchUiState>
    fun onQueryChanged(query: String)
    fun onFilterSelected(filterId: String)
}
```

#### Shared Barrel
```kotlin
// shared/features/search/views/SearchView.kt
package com.app.features.search.views

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import com.app.features.search.SearchPresenter

@Composable
fun SearchView(presenter: SearchPresenter) {
    val state by presenter.state.collectAsState()
    
    // Dispatches to the platform layout without inlining conditional widgets
    SearchLayoutRendition(
        state = state,
        onQueryChange = presenter::onQueryChanged,
        onFilterSelect = presenter::onFilterSelected
    )
}

// expect declaration resolved at compile time or via source sets
@Composable
expect fun SearchLayoutRendition(
    state: SearchUiState,
    onQueryChange: (String) -> Unit,
    onFilterSelect: (String) -> Unit
)
```

#### Mobile Layout
```kotlin
// androidMain/com/app/features/search/views/SearchLayoutRendition.android.kt
@Composable
actual fun SearchLayoutRendition(
    state: SearchUiState,
    onQueryChange: (String) -> Unit,
    onFilterSelect: (String) -> Unit
) {
    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(value = state.query, onValueChange = onQueryChange)
        FilterChipRow(selected = state.selectedFilter, onSelect = onFilterSelect)
        LazyColumn(modifier = Modifier.weight(1f)) {
            items(state.results) { item ->
                MobileCompactResultCard(item = item)
            }
        }
    }
}
```

#### Desktop / Tablet Split Layout
```kotlin
// desktopMain/com/app/features/search/views/SearchLayoutRendition.desktop.kt
@Composable
actual fun SearchLayoutRendition(
    state: SearchUiState,
    onQueryChange: (String) -> Unit,
    onFilterSelect: (String) -> Unit
) {
    Row(modifier = Modifier.fillMaxSize()) {
        // Dedicated persistent desktop sidebar for filtering
        FilterSidebar(
            modifier = Modifier.width(280.dp),
            selected = state.selectedFilter,
            onSelect = onFilterSelect
        )
        VerticalDivider()
        Column(modifier = Modifier.weight(1f).padding(24.dp)) {
            DesktopSearchBar(value = state.query, onValueChange = onQueryChange)
            Spacer(modifier = Modifier.height(16.dp))
            LazyVerticalGrid(columns = GridCells.Adaptive(minSize = 320.dp)) {
                items(state.results) { item ->
                    DesktopDetailedResultCard(item = item)
                }
            }
        }
    }
}
```

---

## 5. Build-Time vs. Runtime Immutability

Platform identity resolution operates in two distinct tiers:

### 1. Build-Time Static Resolution (Preferred)
Code bound to target-specific toolchains must be partitioned at compile/bundle time using toolchain mechanisms (e.g. Metro extensions `.android.ts`, Kotlin `expect/actual`, C# Multi-targeting).
- **Zero Runtime Overhead:** Dead code elimination strips non-relevant platforms from the binary.
- **Strict Isolation:** Target OS APIs cannot leak into incompatible platform bundles.

### 2. Runtime Environment Detection (Cached & Immutable)
When platform dispatch must happen at runtime (e.g. Flutter dynamic OS switches, web user-agent adaptation), environment detection must be evaluated **exactly once** and cached as an immutable token:

```csharp
// Runtime Platform Cache Example (.NET / C#)
public static class CurrentPlatform
{
    public static readonly bool IsDesktop = 
        OperatingSystem.IsWindows() || OperatingSystem.IsMacOS() || OperatingSystem.IsLinux();
        
    public static readonly bool IsMobile = 
        OperatingSystem.IsAndroid() || OperatingSystem.IsIOS();
        
    public static readonly PlatformFamily Family = 
        IsDesktop ? PlatformFamily.Desktop : PlatformFamily.Mobile;
}
```

> [!CAUTION]
> Never re-evaluate platform detection inside hot rendering loops, layout measurement passes, or component build methods. Always bind to static or memoized tokens.
