# Platform Capability Contract Template

> Architectural template for encapsulating asymmetric, non-uniform device capabilities into safe, exception-free tokens.

---

## 1. Universal Contract Definition (C#)

```csharp
namespace App.Shared.Capabilities;

/// <summary>
/// Encapsulates a hardware or OS feature that may not exist on all targets.
/// </summary>
/// <typeparam name="TFeature">The interface contract representing the capability.</typeparam>
public sealed class PlatformCapability<TFeature> where TFeature : class
{
    public bool IsSupported { get; }
    public string? UnsupportedReason { get; }
    private readonly Func<TFeature>? _accessor;

    private PlatformCapability(bool isSupported, Func<TFeature>? accessor, string? unsupportedReason)
    {
        IsSupported = isSupported;
        _accessor = accessor;
        UnsupportedReason = unsupportedReason;
    }

    public static PlatformCapability<TFeature> Supported(Func<TFeature> accessor) =>
        new(true, accessor, null);

    public static PlatformCapability<TFeature> Unsupported(string reason) =>
        new(false, null, reason);

    /// <summary>
    /// Executes an async action with the feature if available; otherwise triggers the fallback.
    /// Never throws NotSupportedException.
    /// </summary>
    public async Task<TResult> ExecuteAsync<TResult>(
        Func<TFeature, Task<TResult>> action,
        Func<Task<TResult>> fallbackAction)
    {
        if (IsSupported && _accessor != null)
        {
            return await action(_accessor());
        }
        return await fallbackAction();
    }
}
```

---

## 2. Universal Contract Definition (TypeScript)

```typescript
export interface PlatformCapability<TFeature> {
  readonly isSupported: boolean;
  readonly unsupportedReason?: string;
  readonly feature?: TFeature;
  executeAsync<TResult>(
    action: (feature: TFeature) => Promise<TResult>,
    fallbackAction: () => Promise<TResult>
  ): Promise<TResult>;
}

export function createCapability<TFeature>(
  feature: TFeature | null | undefined,
  unsupportedReason = "Feature not supported on this platform"
): PlatformCapability<TFeature> {
  if (feature) {
    return {
      isSupported: true,
      feature,
      executeAsync: async (action, _) => action(feature)
    };
  }
  return {
    isSupported: false,
    unsupportedReason,
    executeAsync: async (_, fallback) => fallback()
  };
}
```
