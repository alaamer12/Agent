# 08 — Side-by-Side Identity & Sandboxing

> Requirements and patterns for executing multiple variants or tenants of the same application concurrently on a single machine or device without resource collisions.

---

## 1. The Multi-Instance Coexistence Challenge

When developing white-label products, staging/production environments, or multi-tenant builds, users or QA engineers must frequently install and run two versions of the app side-by-side:
- `App (Production)` alongside `App (Staging)`.
- `App (Tenant Alpha)` alongside `App (Tenant Beta)`.

Without strict identity and resource isolation, installing one variant overwrites the other, corrupts local databases, hijacks deep links, or deadlocks IPC mutexes.

---

## 2. The Four Pillars of Identity Isolation

```
                   Side-by-Side Coexistence
                              │
     ┌────────────────────────┼────────────────────────┐
     ▼                        ▼                        ▼
[ 1. Package Identity ]  [ 2. Storage Sandbox ]  [ 3. Deep Link Schemes ]
Unique Bundle/App ID     Isolated SQLite &       Namespaced URL Schemes
Per Variant              Filesystem Directories  Per Build
                              │
                              ▼
                     [ 4. IPC & Mutexes ]
                     Namespaced System Locks
                     & Notification Channels
```

### 1. Application / Package Identifier Isolation
Never share package identifiers across variants. Derive the ID from the build flavor:
- Production: `com.company.product`
- Staging: `com.company.product.staging`
- Enterprise White-label: `com.partner.product`

### 2. Isolated Storage Sandboxes & SQLite Paths
Local persistence must partition storage based on the active variant and tenant:

```csharp
// Infrastructure/Storage/SandboxedDatabasePathResolver.cs
public static class SandboxedDatabasePathResolver
{
    public static string GetDatabasePath(string appVariant, string tenantId)
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        // Explicit variant + tenant namespace ensures zero collision
        var basePath = Path.Combine(appData, "IsolatedAppData", appVariant, tenantId);
        
        if (!Directory.Exists(basePath))
        {
            Directory.CreateDirectory(basePath);
        }
        
        return Path.Combine(basePath, "app_data.db3");
    }
}
```

### 3. Namespaced Deep Link URL Schemes
If both Production and Staging register `app://open`, the operating system makes an arbitrary choice on which app handles the deep link.
- Production: `product://oauth-callback`
- Staging: `product-staging://oauth-callback`

### 4. IPC Mutexes & Single-Instance Guards
Desktop applications often enforce single-instance execution via OS-level Mutexes or Named Pipes. If the mutex name is hardcoded, running Staging will fail because Production is holding the lock:

```csharp
// Desktop Single-Instance Mutex Isolation
string mutexName = $"Global\\Application_{AppFlavor.Current}_{AppTenant.Current}_SingleInstanceMutex";
using var mutex = new Mutex(true, mutexName, out bool createdNew);
if (!createdNew)
{
    // Bring existing instance of THIS specific variant to front
    return;
}
```
