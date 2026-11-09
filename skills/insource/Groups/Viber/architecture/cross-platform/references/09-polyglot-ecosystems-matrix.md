# 09 — Polyglot Ecosystems & Toolchain Matrix

> Toolchain mechanics, compilation directives, file-suffix resolution, and source-set architecture across the four major cross-platform ecosystems: React Native / Expo, Flutter, Kotlin Multiplatform (KMP), and .NET MAUI / Uno Platform.

---

## 1. Toolchain Resolution Comparison Matrix

| Ecosystem | File-Level Extension Dispatch | Conditional Compilation Directives | Dependency Injection / Abstraction | Platform Views / Native Host |
| :--- | :--- | :--- | :--- | :--- |
| **React Native / Expo** | `.android.tsx`, `.ios.tsx`, `.web.tsx`, `.native.tsx` (Metro bundler) | `Platform.select({ ... })` (Avoid inline in JSX) | Inversion of Control via TypeScript Interfaces or Context | Fabric Native Components / TurboModules |
| **Flutter / Dart** | Conditional Imports: `import 'x.dart' if (dart.library.io) 'x_io.dart'` | `defaultTargetPlatform`, `kIsWeb` | `get_it`, `Riverpod`, or Abstract Repositories | PlatformView (`AndroidView`, `UiKitView`) |
| **Kotlin Multiplatform** | Gradle Source Sets: `commonMain`, `androidMain`, `iosMain`, `desktopMain` | `expect / actual` declarations at compile-time | `Koin`, `kotlin-inject`, or Pure Interfaces | Compose Multiplatform Interop (`UIKitView`, `SwingPanel`) |
| **.NET MAUI / Uno** | `Platforms/Android/`, `Platforms/iOS/`, `Platforms/Windows/` | `#if ANDROID`, `#if IOS`, `#if WINDOWS` (Restricted to platform folders) | Microsoft.Extensions.DependencyInjection (`IServiceCollection`) | Native View Handlers (`ViewHandler<TVirtual, TNative>`) |

---

## 2. Deep Dive by Ecosystem

### 1. React Native & Expo (Metro Bundler)

Metro resolves extensions in a prioritized sequence:
1. `ComponentName.[platform].[extension]` (e.g. `ModalPresenter.android.tsx`)
2. `ComponentName.native.[extension]` (Shared mobile fallback for iOS + Android)
3. `ComponentName.[extension]` (Base shared fallback, including web)

#### Metro Configuration Guard (`metro.config.js`)
```javascript
const { getDefaultConfig } = require('expo/metro-config');
const config = getDefaultConfig(__dirname);

// Ensure proper platform extension resolution order
config.resolver.sourceExts = ['expo.ts', 'expo.tsx', 'ts', 'tsx', 'js', 'jsx', 'json'];
module.exports = config;
```

---

### 2. Flutter & Dart

Dart achieves build-time tree shaking through conditional import statements without needing a C-style preprocessor:

```dart
// lib/infrastructure/file_storage/storage_gateway.dart
// Conditional export mapping:
export 'storage_gateway_stub.dart'
  if (dart.library.io) 'storage_gateway_io.dart'
  if (dart.library.html) 'storage_gateway_web.dart';

abstract class StorageGateway {
  Future<void> saveFile(String filename, List<int> bytes);
  factory StorageGateway() => getStorageGateway();
}

// storage_gateway_io.dart
import 'dart:io';
StorageGateway getStorageGateway() => IoStorageGateway();
class IoStorageGateway implements StorageGateway {
  Future<void> saveFile(String filename, List<int> bytes) async {
    final file = File(filename);
    await file.writeAsBytes(bytes);
  }
}
```

---

### 3. Kotlin Multiplatform (KMP)

KMP enforces strict physical separation of platform code through Gradle source sets. Shared code lives in `commonMain` and can only compile against symbols available across all targets:

```kotlin
// commonMain/com/app/core/network/HttpEngineFactory.kt
package com.app.core.network

import io.ktor.client.engine.*

expect object HttpEngineFactory {
    fun create(): HttpClientEngine
}

// androidMain/com/app/core/network/HttpEngineFactory.android.kt
package com.app.core.network

import io.ktor.client.engine.*
import io.ktor.client.engine.okhttp.*

actual object HttpEngineFactory {
    actual fun create(): HttpClientEngine = OkHttp.create()
}

// iosMain/com/app/core/network/HttpEngineFactory.ios.kt
package com.app.core.network

import io.ktor.client.engine.*
import io.ktor.client.engine.darwin.*

actual object HttpEngineFactory {
    actual fun create(): HttpClientEngine = Darwin.create()
}
```

---

### 4. .NET MAUI & Uno Platform

.NET MAUI uses MSBuild SDK Multi-Targeting. While `#if` directives exist, **they must never appear in shared business or UI code**. Keep them locked inside `Platforms/` or use Partial Classes:

```xml
<!-- CoreProject.csproj multi-targeting definition -->
<PropertyGroup>
  <TargetFrameworks>net9.0-android;net9.0-ios;net9.0-maccatalyst;net9.0-windows10.0.19041.0</TargetFrameworks>
</PropertyGroup>

<!-- Exclude platform folders from compiling in other platform targets -->
<ItemGroup Condition="$(TargetFramework.StartsWith('net9.0-android')) != true">
  <Compile Remove="Platforms\Android\**\*.cs" />
</ItemGroup>
```

#### Clean Partial Class Mechanics:
```csharp
// Shared/Services/HapticFeedback.cs
public partial class HapticFeedback
{
    public partial void PerformClick();
}

// Platforms/Android/HapticFeedback.Android.cs
public partial class HapticFeedback
{
    public partial void PerformClick()
    {
        Android.Views.View.PerformHapticFeedback(Android.Views.FeedbackConstants.ContextClick);
    }
}
```
