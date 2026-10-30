// PlatformStartupHooks.Windows.cs  ✅ new file
public static partial class PlatformStartupHooks
{
    public static partial void ConfigureWindowChrome(MauiAppBuilder builder) =>
        builder.ConfigureLifecycleEvents(events => events.AddWindows(w =>
            w.OnWindowCreated(window => window.ExtendsContentIntoTitleBar = true)));

    public static partial void RegisterPlatformServices(IServiceCollection services) =>
        services.AddSingleton<ISystemTrayService, WindowsSystemTrayService>();

    public static partial void ConfigureStatusBar(MauiAppBuilder builder) { /* no-op on Windows */ }
}
