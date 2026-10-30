// Program.cs  ❌ composition root, several unrelated inline platform blocks
public static class Program
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder.UseMauiApp<App>();

#if WINDOWS
        builder.ConfigureLifecycleEvents(events => events.AddWindows(w =>
            w.OnWindowCreated(window => window.ExtendsContentIntoTitleBar = true)));
#endif
#if WINDOWS
        builder.Services.AddSingleton<ISystemTrayService, WindowsSystemTrayService>();
#endif
#if ANDROID
        builder.ConfigureLifecycleEvents(events => events.AddAndroid(a =>
            a.OnCreate((activity, _) => activity.Window?.SetStatusBarColor(Colors.Transparent.ToPlatform()))));
#endif

        return builder.Build();
    }
}
