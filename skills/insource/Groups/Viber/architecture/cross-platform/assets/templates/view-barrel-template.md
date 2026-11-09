# View Barrel Template

> Canonical layout-dispatcher template separating UI layout representations from shared state and view models.

---

## 1. File Structure

```
views/[Feature]View/
├── [Feature]View.tsx             # The View Barrel (Connects State to Renditions)
├── _[Feature]DesktopLayout.tsx   # Layout 1: Multi-column, wide-screen representation
└── _[Feature]MobileLayout.tsx    # Layout 2: Single-column, stacked touch representation
```

---

## 2. Implementation Template (TypeScript / React)

### The View Barrel (`[Feature]View.tsx`)
```tsx
import React from 'react';
import { useBreakpoint } from '@/shared/ui/responsive/useBreakpoint';
import { use[Feature]State } from '../../state/use[Feature]State';
import { _[Feature]DesktopLayout } from './_[Feature]DesktopLayout';
import { _[Feature]MobileLayout } from './_[Feature]MobileLayout';

export function [Feature]View() {
  // 1. Single source of truth (Shared ViewModel / State Hook)
  const state = use[Feature]State();
  
  // 2. Container width breakpoint resolver (Pure geometric measurement)
  const { isExpanded } = useBreakpoint();

  // 3. Delegation to dedicated layout renditions
  return isExpanded ? (
    <_[Feature]DesktopLayout state={state} />
  ) : (
    <_[Feature]MobileLayout state={state} />
  );
}
```

### The Desktop Layout (`_[Feature]DesktopLayout.tsx`)
```tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { [Feature]UiState } from '../../state/types';

interface Props {
  state: [Feature]UiState;
}

export function _[Feature]DesktopLayout({ state }: Props) {
  return (
    <View style={styles.desktopContainer}>
      {/* Multi-pane desktop layout with persistent sidebar/inspector */}
      <View style={styles.sidebar}>
        {/* Filter controls, tree views, or navigation */}
      </View>
      <View style={styles.content}>
        {/* Main data grids, detailed cards, actions */}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  desktopContainer: { flexDirection: 'row', flex: 1 },
  sidebar: { width: 320, borderRightWidth: 1, borderColor: '#E0E0E0' },
  content: { flex: 1, padding: 24 }
});
```

### The Mobile Layout (`_[Feature]MobileLayout.tsx`)
```tsx
import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { [Feature]UiState } from '../../state/types';

interface Props {
  state: [Feature]UiState;
}

export function _[Feature]MobileLayout({ state }: Props) {
  return (
    <ScrollView style={styles.mobileContainer}>
      {/* Linear, touch-optimized single-column layout */}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  mobileContainer: { flex: 1, padding: 12 }
});
```
