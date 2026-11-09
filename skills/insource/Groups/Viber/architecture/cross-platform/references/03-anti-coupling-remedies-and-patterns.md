# 03 — Anti-Coupling Remedies & Architectural Patterns

> Concrete, production-tested architectural solutions for eliminating platform and idiom conditionals. Every identified anti-pattern is matched with its exact, fully articulated replacement.

---

## 1. The Anti-Pattern Catalog

| Anti-Pattern | Immediate Symptom | Concrete Architectural Remedy |
| :--- | :--- | :--- |
| **1. Idiom Checking in Views** | `if (DeviceInfo.Idiom == Desktop)` inside rendering code | **View Barrel Layout Swapping & Behavior Injection** |
| **2. Inline Platform Preprocessors** | `#if ANDROID`, `Platform.OS === 'ios'` inside shared UI | **Builder-resolved files (`.android.ts`) or Abstract Interfaces** |
| **3. Hardcoded Platform Metrics** | Inline platform paddings, status bar offsets, color branches | **Semantic Design Tokens with Platform Resolvers** |
| **4. Direct Hardware Access in ViewModels** | Calling OS GPS, Camera, or Bluetooth directly from shared state | **Abstract Capability Services injected via IoC / DI** |
| **5. Asymmetric Feature Crashes** | Unhandled `NotSupportedException` on platforms lacking a sensor | **The `PlatformCapability<T>` Graceful Fallback Pattern** |
| **6. Micro-Responsive Inlining** | Ternary width checks scattered across JSX/XAML tree | **Adaptive Container Primitives with Named Breakpoints** |

---

## 2. Remedy Deep Dives: Bad Code vs. Explicit Solution

### Pattern 1: Direct Idiom Checking in Shared UI

#### ❌ Defective Implementation
```csharp
// ✘ Pollutes shared UI with layout bifurcation and device branching
public class ProductCardView : ContentView
{
    public ProductCardView()
    {
        if (DeviceInfo.Current.Idiom == DeviceIdiom.Desktop)
        {
            Content = new HorizontalStackLayout {
                new Image { WidthRequest = 200 },
                new VerticalStackLayout { new Label { Text = "Desktop Details" } }
            };
        }
        else
        {
            Content = new VerticalStackLayout {
                new Image { WidthRequest = 100 },
                new Label { Text = "Mobile Compact" }
            };
        }
    }
}
```

#### ✅ Production Architectural Remedy: View Barrel with Layout Separation
Split the layout representations into distinct files; the View acts as a layout dispatcher consuming a single shared ViewModel.

```csharp
// 1. Shared View Barrel (ProductCardView.xaml.cs)
public partial class ProductCardView : ContentView
{
    public ProductCardView()
    {
        InitializeComponent();
        // Dispatches to the declared form-factor layout without inlining UI structures
        Content = DeviceInfo.Current.Idiom == DeviceIdiom.Desktop 
            ? new ProductCardDesktopLayout() 
            : new ProductCardMobileLayout();
    }
}

// 2. Desktop Layout (ProductCardDesktopLayout.xaml)
<Grid ColumnDefinitions="240, *">
    <Image Grid.Column="0" Source="{Binding ThumbnailUrl}" Aspect="AspectFill" />
    <VerticalStackLayout Grid.Column="1" Padding="16">
        <Label Text="{Binding Title}" FontAttributes="Bold" FontSize="18" />
        <Label Text="{Binding DetailedDescription}" />
    </VerticalStackLayout>
</Grid>

// 3. Mobile Layout (ProductCardMobileLayout.xaml)
<VerticalStackLayout Spacing="8">
    <Image Source="{Binding ThumbnailUrl}" HeightRequest="140" Aspect="AspectFill" />
    <Label Text="{Binding Title}" FontAttributes="Bold" FontSize="14" />
</VerticalStackLayout>
```

---

### Pattern 2: Inline Platform Preprocessors in Logic

#### ❌ Defective Implementation
```typescript
// ✘ Contaminates business logic with OS checks
export class PaymentService {
  async processPayment(amount: number) {
    if (Platform.OS === 'ios') {
      return ApplePay.request(amount);
    } else if (Platform.OS === 'android') {
      return GooglePay.request(amount);
    } else {
      return WebStripe.checkout(amount);
    }
  }
}
```

#### ✅ Production Architectural Remedy: Abstract Interface & Platform Injection

```typescript
// 1. Contract Definition (shared/contracts/IPaymentProvider.ts)
export interface IPaymentProvider {
  readonly providerId: string;
  isAvailable(): Promise<boolean>;
  pay(amount: number, currency: string): Promise<PaymentReceipt>;
}

// 2. Android Implementation (platforms/android/GooglePayProvider.ts)
export class GooglePayProvider implements IPaymentProvider {
  readonly providerId = 'google_pay';
  async isAvailable() { return NativeGooglePay.canMakePayments(); }
  async pay(amount: number, currency: string) {
    return NativeGooglePay.execute(amount, currency);
  }
}

// 3. iOS Implementation (platforms/ios/ApplePayProvider.ts)
export class ApplePayProvider implements IPaymentProvider {
  readonly providerId = 'apple_pay';
  async isAvailable() { return NativeApplePay.canMakePayments(); }
  async pay(amount: number, currency: string) {
    return NativeApplePay.execute(amount, currency);
  }
}

// 4. Shared Consumer (shared/services/CheckoutCoordinator.ts)
export class CheckoutCoordinator {
  constructor(private readonly paymentProvider: IPaymentProvider) {}

  async checkout(amount: number) {
    if (!await this.paymentProvider.isAvailable()) {
      throw new Error(`Provider ${this.paymentProvider.providerId} is not available on this device.`);
    }
    return this.paymentProvider.pay(amount, 'USD');
  }
}
```

---

### Pattern 3: Hardcoded Platform Metrics in Styles

#### ❌ Defective Implementation
```tsx
// ✘ Scattered magic numbers and runtime platform conditionals
const styles = StyleSheet.create({
  header: {
    paddingTop: Platform.OS === 'ios' ? 44 : 24,
    height: Platform.OS === 'web' ? 64 : 80,
    backgroundColor: Platform.OS === 'android' ? '#2196F3' : '#007AFF',
  }
});
```

#### ✅ Production Architectural Remedy: Semantic Design Tokens

```typescript
// design-system/tokens.ts
export interface ThemeTokens {
  headerHeight: number;
  statusBarOffset: number;
  primaryColor: string;
}

// design-system/tokens.native.ts
export const tokens: ThemeTokens = {
  headerHeight: 56,
  statusBarOffset: 24,
  primaryColor: '#0066CC',
};

// design-system/tokens.web.ts
export const tokens: ThemeTokens = {
  headerHeight: 64,
  statusBarOffset: 0,
  primaryColor: '#0052A3',
};

// consumer.tsx
import { tokens } from './design-system/tokens';

const styles = StyleSheet.create({
  header: {
    paddingTop: tokens.statusBarOffset,
    height: tokens.headerHeight,
    backgroundColor: tokens.primaryColor,
  }
});
```
