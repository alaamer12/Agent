# Polyglot Full Walkthrough: Checkout & Payment Flow

> An end-to-end, multi-ecosystem demonstration of refactoring a highly coupled checkout and biometric authorization flow into a clean, platform-decoupled architecture across React Native, Kotlin Multiplatform, Flutter, and .NET MAUI.

---

## 1. The Scenario

The application feature is a checkout screen:
- **Core Logic:** Renders item total, calculates taxes, triggers biometric authorization or falls back to PIN entry, and invokes native OS payment (Apple Pay / Google Pay / Credit Card).
- **Desktop vs. Mobile UI:** On phones, it shows a vertical stack with a bottom sliding sheet for confirmation. On desktop/tablet, it renders a two-column layout with an anchored checkout pane on the right.

---

## 2. React Native / TypeScript Refactoring

### ❌ The Coupled Anti-Pattern
```tsx
// ✘ Pollutes shared view with platform conditionals, device idioms, and direct hardware calls
export function CheckoutScreen() {
  const isDesktop = Dimensions.get('window').width > 1024;
  
  const handlePay = async () => {
    if (Platform.OS === 'ios') {
      const bioAuth = await NativeModules.TouchID.isSupported();
      if (bioAuth) await NativeModules.TouchID.authenticate();
      await ApplePay.requestPayment();
    } else if (Platform.OS === 'android') {
      await GooglePay.requestPayment();
    } else {
      window.location.href = '/stripe-checkout';
    }
  };

  return isDesktop ? (
    <View style={{ flexDirection: 'row' }}>
      <OrderItemsList />
      <DesktopSummaryPane onPay={handlePay} />
    </View>
  ) : (
    <View style={{ flexDirection: 'column' }}>
      <OrderItemsList />
      <BottomFloatingPayButton onPay={handlePay} />
    </View>
  );
}
```

### ✅ The Clean Decoupled Architecture

#### 1. Contract & Capability Definitions
```typescript
// features/checkout/contracts/IPaymentGateway.ts
export interface IPaymentGateway {
  readonly gatewayName: string;
  processPayment(amount: number): Promise<PaymentReceipt>;
}

// features/checkout/contracts/IBiometricSensor.ts
export interface IBiometricSensor {
  authenticate(): Promise<boolean>;
}
```

#### 2. View Barrel (Layout Dispatcher)
```tsx
// features/checkout/views/CheckoutView/CheckoutView.tsx
import { useBreakpoint } from '@/shared/ui/responsive/useBreakpoint';
import { useCheckoutState } from '../../state/useCheckoutState';
import { _CheckoutDesktopLayout } from './_CheckoutDesktopLayout';
import { _CheckoutMobileLayout } from './_CheckoutMobileLayout';

export function CheckoutView() {
  const state = useCheckoutState();
  const { isExpanded } = useBreakpoint();

  return isExpanded ? (
    <_CheckoutDesktopLayout state={state} />
  ) : (
    <_CheckoutMobileLayout state={state} />
  );
}
```

---

## 3. Kotlin Multiplatform (KMP & Compose)

### Clean Decoupled Implementation

#### 1. Common State Machine & Presenter
```kotlin
// commonMain/com/app/checkout/CheckoutPresenter.kt
class CheckoutPresenter(
    private val paymentGateway: PaymentGateway,
    private val biometrics: PlatformCapability<BiometricSensor>
) {
    fun onConfirmOrder(amount: Double) {
        viewModelScope.launch {
            val authenticated = biometrics.executeAsync(
                action = { sensor -> sensor.authenticate("Confirm Payment") },
                fallbackAction = { promptPinDialog() }
            )
            if (authenticated) {
                paymentGateway.processPayment(amount)
            }
        }
    }
}
```

#### 2. View Barrel Layout Delegation
```kotlin
// commonMain/com/app/checkout/views/CheckoutView.kt
@Composable
fun CheckoutView(presenter: CheckoutPresenter) {
    val state by presenter.uiState.collectAsState()
    
    // Dispatches layout without inlining platform or idiom checks
    CheckoutLayoutRendition(
        state = state,
        onPay = presenter::onConfirmOrder
    )
}

@Composable
expect fun CheckoutLayoutRendition(state: CheckoutUiState, onPay: (Double) -> Unit)
```

---

## 4. Flutter / Dart

### Clean Decoupled Implementation

#### 1. Abstract Payment Gateway & Factory
```dart
// lib/features/checkout/contracts/payment_gateway.dart
abstract class PaymentGateway {
  Future<PaymentResult> pay(double amount);
}

// lib/features/checkout/infrastructure/payment_gateway_resolver.dart
import 'package:flutter/foundation.dart';
import 'apple_pay_gateway.dart';
import 'google_pay_gateway.dart';
import 'web_stripe_gateway.dart';

PaymentGateway createPlatformPaymentGateway() {
  if (kIsWeb) return WebStripeGateway();
  if (defaultTargetPlatform == TargetPlatform.iOS) return ApplePayGateway();
  return GooglePayGateway();
}
```

#### 2. Adaptive View Barrel
```dart
// lib/features/checkout/views/checkout_view.dart
class CheckoutView extends StatelessWidget {
  final CheckoutPresenter presenter;

  const CheckoutView({Key? key, required this.presenter}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > 900) {
          return CheckoutDesktopLayout(presenter: presenter);
        }
        return CheckoutMobileLayout(presenter: presenter);
      },
    );
  }
}
```

---

## 5. .NET MAUI / C#

### Clean Decoupled Implementation

#### 1. Platform-Specific Handlers in `Platforms/`
```csharp
// Platforms/Android/Services/AndroidBiometricSensor.cs
namespace App.Platforms.Android.Services;

public class AndroidBiometricSensor : IBiometricSensor
{
    public async Task<bool> AuthenticateAsync(string reason)
    {
        var prompt = new BiometricPrompt.Builder(Platform.AppContext)...;
        return await prompt.AuthenticateAsync();
    }
}
```

#### 2. View Barrel in Shared UI
```csharp
// Shared/Features/Checkout/Views/CheckoutView.xaml.cs
public partial class CheckoutView : ContentView
{
    public CheckoutView(CheckoutViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
        
        // Sets content to dedicated layouts based on container breakpoints
        SizeChanged += (s, e) => {
            if (Width >= 800 && !(Content is CheckoutDesktopLayout))
            {
                Content = new CheckoutDesktopLayout();
            }
            else if (Width < 800 && !(Content is CheckoutMobileLayout))
            {
                Content = new CheckoutMobileLayout();
            }
        };
    }
}
```
