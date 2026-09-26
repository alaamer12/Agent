// PlatformStartupHooks.Android.cs  ✅ new file
public static partial class PlatformStartupHooks
{
    public static partial void ConfigureWindowChrome(MauiAppBuilder builder) { /* no-op on Android */ }
    public static partial void RegisterPlatformServices(IServiceCollection services) { /* nothing yet */ }

    public static partial void ConfigureStatusBar(MauiAppBuilder builder) =>
        builder.ConfigureLifecycleEvents(events => events.AddAndroid(a =>
            a.OnCreate((activity, _) => activity.Window?.SetStatusBarColor(Colors.Transparent.ToPlatform()))));
}
