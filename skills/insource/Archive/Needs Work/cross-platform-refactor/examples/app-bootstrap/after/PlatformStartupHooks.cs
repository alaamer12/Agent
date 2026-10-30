// PlatformStartupHooks.cs  ✅ new file — shared shell, declares the hooks, no platform logic itself.
// NOTE: .NET's file-suffix convention (X.Windows.cs, X.Android.cs) is NOT auto-detected —
// it only works because the .csproj explicitly globs/excludes these files per target
// framework (see references/utilities.md §3). Don't assume this "just works" in every
// framework; check what your build tool actually does before relying on a filename.
public static partial class PlatformStartupHooks
{
    public static partial void ConfigureWindowChrome(MauiAppBuilder builder);
    public static partial void RegisterPlatformServices(IServiceCollection services);
    public static partial void ConfigureStatusBar(MauiAppBuilder builder);
}
