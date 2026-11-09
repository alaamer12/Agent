# Classification Drill Cases: Standard & Edge Scenarios

> Concrete classification drills modeled after the PVC pattern. Each case presents a real-world scenario, the defect diagnosis, the applicable architectural rule, and the clean production code solution.

---

## Drill 1: The Hybrid Convertible Laptop (Tablet + Keyboard + Touch)

### Scenario
An engineer writes a UI check:
```csharp
if (DeviceInfo.Idiom == DeviceIdiom.Tablet) {
    ShowTouchControls();
} else {
    ShowKeyboardShortcutsOverlay();
}
```
A user runs this on a Microsoft Surface or iPad with a Magic Keyboard attached. The app locks them into touch mode and hides desktop keyboard hints.

### Diagnosis & Rule
> **Rule:** Never infer input capabilities from device idiom. Devices are multi-modal. Query the active pointer and input modality, not the form factor ([`02-desktop-native-feel-and-responsiveness.md`](../references/02-desktop-native-feel-and-responsiveness.md)).

### Clean Architectural Solution
```typescript
// architecture/input/InputModalityService.ts
export type InputMode = 'touch' | 'pointer' | 'keyboard';

export class InputModalityTracker {
  private currentMode: InputMode = 'pointer';

  listen(onChange: (mode: InputMode) => void) {
    window.addEventListener('touchstart', () => onChange('touch'), { passive: true });
    window.addEventListener('mousemove', () => onChange('pointer'), { passive: true });
    window.addEventListener('keydown', () => onChange('keyboard'), { passive: true });
  }
}
```

---

## Drill 2: Compounding Multiple Axes into Filenames

### Scenario
A developer creates:
`GooglePlayBillingService.android.playstore.germany.ts`

### Diagnosis & Rule
> **Rule:** Violation of the **Single-Axis Filename Law** ([`06-multi-axis-isolation-and-escalation-levels.md`](../references/06-multi-axis-isolation-and-escalation-levels.md)). Filenames may express at most one axis of variation.

### Clean Architectural Solution
Deconstruct the compound name into orthogonal layers using **Directory Overlays** (Level 2) or the **Layer Registry** (Level 3):
```
src/
├── channels/
│   └── google-play/
│       ├── BillingService.android.ts   # Platform axis handled via suffix
│       └── BillingService.ts           # Fallback
└── policies/
    └── regions/
        └── eu/
            └── TaxCompliancePolicy.ts  # Regional tax logic separated from billing mechanics
```

---

## Drill 3: Direct Preprocessors in Shared ViewModels

### Scenario
```csharp
public class UserProfileViewModel : BaseViewModel
{
    public async Task PickAvatarAsync()
    {
#if ANDROID
        var intent = new Android.Content.Intent(Android.Content.Intent.ActionPick);
        Platform.CurrentActivity.StartActivityForResult(intent, 100);
#elif IOS
        var picker = new UIKit.UIImagePickerController();
        // UIKit presentation logic in ViewModel
#endif
    }
}
```

### Diagnosis & Rule
> **Rule:** Preprocessor leakage into shared presentation state. ViewModels must remain 100% agnostic of OS SDK symbols ([`03-anti-coupling-remedies-and-patterns.md`](../references/03-anti-coupling-remedies-and-patterns.md)).

### Clean Architectural Solution
Inject an abstract file picker gateway:
```csharp
public class UserProfileViewModel : BaseViewModel
{
    private readonly IFilePickerGateway _filePicker;

    public UserProfileViewModel(IFilePickerGateway filePicker)
    {
        _filePicker = filePicker;
    }

    public async Task PickAvatarAsync()
    {
        var file = await _filePicker.PickImageAsync(new ImagePickerOptions { Title = "Select Avatar" });
        if (file != null)
        {
            AvatarStream = await file.OpenReadAsync();
        }
    }
}
```

---

## Drill 4: Re-evaluating Platform in Component Build Loop

### Scenario
```tsx
export function MetricCard({ title, value }: Props) {
  // ✘ Evaluating Platform.OS and window dimensions on every single render cycle
  const isIOS = Platform.OS === 'ios';
  const isLarge = Dimensions.get('window').width > 1200;
  
  return (
    <View style={{ padding: isIOS ? 12 : 8, elevation: isIOS ? 0 : 4 }}>
      <Text>{title}</Text>
    </View>
  );
}
```

### Diagnosis & Rule
> **Rule:** Runtime platform detection must be immutable and resolved outside hot render loops ([`01-ui-mechanics-and-platform-concepts.md`](../references/01-ui-mechanics-and-platform-concepts.md)). Use static Design Tokens or `_X` private wrappers.

### Clean Architectural Solution
```tsx
import { cardTokens } from '@/shared/theme/cardTokens'; // Pre-resolved statically at launch

export function MetricCard({ title, value }: Props) {
  return (
    <View style={cardTokens.container}>
      <Text style={cardTokens.title}>{title}</Text>
    </View>
  );
}
```

---

## Drill 5: Parallel Reinvention vs. UNITS.md

### Scenario
A developer working on the `analytics` feature creates `AnalyticsDateRangePicker.tsx`, creating their own popover, backdrop, and date grid from scratch because they didn't know `shared/ui/pickers/DateRangePicker.tsx` existed.

### Diagnosis & Rule
> **Rule:** Violation of the **UNITS.md Governance Mandate** ([`05-three-tier-unit-hierarchy-and-units-md.md`](../references/05-three-tier-unit-hierarchy-and-units-md.md)). All visual units must be checked against `UNITS.md` before implementation.

### Clean Architectural Solution
1. Consult `UNITS.md`.
2. Find `DateRangePicker` in Tier 2.
3. Specialize it in Tier 3 by composing the existing unit with analytics presets (e.g. "Last 7 Days", "Last 30 Days").
