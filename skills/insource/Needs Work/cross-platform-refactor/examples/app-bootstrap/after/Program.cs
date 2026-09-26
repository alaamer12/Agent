// Program.cs  ✅ composition root — no inline platform conditionals left
public static class Program
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder.UseMauiApp<App>();

        PlatformStartupHooks.ConfigureWindowChrome(builder);
        PlatformStartupHooks.RegisterPlatformServices(builder.Services);
        PlatformStartupHooks.ConfigureStatusBar(builder);

        return builder.Build();
    }
}
