# 04 — Asymmetric Capabilities & The PlatformCapability<T> Pattern

> Architectural handling of non-uniform device capabilities (biometrics, NFC, camera, push notifications, Bluetooth). Eradicating runtime exceptions through capability discovery, feature tokens, and declared fallback policies.

---

## 1. The Asymmetric Hardware Problem

In a cross-platform application, assuming hardware parity across targets is fatal. For example:
- A mobile phone has a multi-axis gyroscope, biometric fingerprint sensor, camera, and cellular radio.
- A desktop workstation running the same app has none of those, but possesses multiple high-resolution displays, mouse wheels, and a physical QWERTY keyboard.
- A web browser sandbox restricts Bluetooth and raw file system access.

Calling an unsupported API directly results in unhandled `NotSupportedException` or fatal application crashes.

---

## 2. The `PlatformCapability<T>` Contract

Instead of scattering `if (hasBiometrics)` across view models, encapsulate asymmetric device capabilities into a strongly typed **Capability Token**:

```csharp
// Architecture/Contracts/PlatformCapability.cs
namespace App.Architecture.Contracts;

public sealed class PlatformCapability<TFeature>
{
    public bool IsSupported { get; }
    public string? UnsupportedReason { get; }
    private readonly Func<TFeature>? _featureAccessor;

    private PlatformCapability(bool isSupported, Func<TFeature>? featureAccessor, string? unsupportedReason)
    {
        IsSupported = isSupported;
        _featureAccessor = featureAccessor;
        UnsupportedReason = unsupportedReason;
    }

    public static PlatformCapability<TFeature> Available(Func<TFeature> accessor) =>
        new(true, accessor, null);

    public static PlatformCapability<TFeature> Unavailable(string reason) =>
        new(false, null, reason);

    public TFeature Feature =>
        IsSupported && _featureAccessor != null 
            ? _featureAccessor() 
            : throw new InvalidOperationException($"Capability {typeof(TFeature).Name} is unavailable: {UnsupportedReason}");

    public async Task<TResult> ExecuteAsync<TResult>(
        Func<TFeature, Task<TResult>> action, 
        Func<Task<TResult>> fallbackAction)
    {
        if (IsSupported && _featureAccessor != null)
        {
            return await action(_featureAccessor());
        }
        return await fallbackAction();
    }
}
```

---

## 3. Real-World Case: Biometric Authentication vs. PIN Fallback

### Polyglot TypeScript / React Native Implementation

```typescript
// contracts/BiometricsCapability.ts
export interface IBiometricSensor {
  authenticate(prompt: string): Promise<boolean>;
}

export interface CapabilityResult<T> {
  readonly isSupported: boolean;
  readonly feature?: T;
  readonly reason?: string;
}

// services/AuthenticationCoordinator.ts
export class AuthenticationCoordinator {
  constructor(
    private readonly biometrics: CapabilityResult<IBiometricSensor>,
    private readonly pinAuthService: IPinAuthService
  ) {}

  async authenticateUser(): Promise<boolean> {
    if (this.biometrics.isSupported && this.biometrics.feature) {
      try {
        const success = await this.biometrics.feature.authenticate("Log into account");
        if (success) return true;
      } catch (err) {
        console.warn("Biometric authentication failed, falling back to PIN.", err);
      }
    }

    // Graceful fallback without throwing or halting workflow
    return this.pinAuthService.promptForPin();
  }
}
```

---

## 4. UI Degradation Rules

When a capability is unavailable on a target:
1. **Silent Fallback:** If the capability is an enhancement (e.g. haptic feedback), degrade silently without user intervention.
2. **Alternative Method:** If the capability is required for security (e.g. biometrics), substitute with the platform standard (e.g. master password or PIN prompt).
3. **Adaptive UI Concealment:** If an entire feature depends on absent hardware (e.g. QR code camera scanner on a desktop without a webcam), do not disable the button with a cryptic error—replace the view with manual text entry.
