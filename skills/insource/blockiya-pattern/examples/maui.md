# Blockiya — .NET MAUI + C# (MVVM-Adjacent)

The same `UserProfileBlock` scenario, third paradigm family: compiled, XAML-bound, MVVM. This port is the strongest argument that Blockiya is not a React pattern — **MAUI practically implements it by construction**: a ViewModel cannot contain CSS, an `ICommand`/event is already "fire intent upward", and the page already owns navigation. What Blockiya adds on top is the same discipline it adds in React: derivation before binding, compound encapsulation of interaction state, adapters isolating plugins, and the 3–7 prop/intent ceiling.

Mapping shorthand: **Blockiya → ViewModel (+ its orchestrating `ContentView`)**, presentational child → XAML view bound to a derived record, primitive → token-driven style/`ContentView`, adapter → wrapper control around a NuGet plugin, intent → C# `event`, hooks → services injected by the DI container.

## 1. Tokens and primitives

Zero-styling enforced one level deeper than React: literal colors/margins are banned in composing views; everything resolves through token resources.

```xml
<!-- Resources/tokens.xaml -->
<ResourceDictionary>
    <x:Double x:Key="SpaceMd">16</x:Double>
    <Color x:Key="TextMuted">#6B7280</Color>
    <Style x:Key="LabelMuted" TargetType="Label">
        <Setter Property="TextColor" Value="{StaticResource TextMuted}" />
    </Style>
</ResourceDictionary>
```

```csharp
// Shared/Ui/TextBlock.cs — a primitive: BindableProperties accept token KEYS, not raw values
public class TextBlock : Label
{
    public static readonly BindableProperty ToneProperty =
        BindableProperty.Create(nameof(Tone), typeof(string), typeof(TextBlock), "Body",
            propertyChanged: (b, _, v) => ((TextBlock)b).Style =
                (Style)Application.Current.Resources[$"Label{v}"]!);
    public string Tone { get => (string)GetValue(ToneProperty); set => SetValue(ToneProperty, value); }
}
```

## 2. Behavioral — Dropdown owns its open state

MAUI's idiomatic answer is a `Popup` (or `MenuFlyout`): the trigger button opens it and **no consumer ever reads an `IsOpen`** — the encapsulation rule is satisfied by the control's very API.

```csharp
// Shared/Ui/Behavioral/DropdownPopup.cs — CommunityToolkit.Maui Popup as an e.g. base
public partial class ActionsPopup : Popup
{
    public event EventHandler<string>? ItemSelected;   // clean intent-shaped exit
    public ActionsPopup() => InitializeComponent();     // list of items lives inside
    private void OnItem(object s, TappedEventArgs e)
    {
        ItemSelected?.Invoke(this, (string)e.Parameter);
        _ = CloseAsync();                              // closes itself; caller sees none of it
    }
}
```

## 3. Adapter — the third-party avatar is unknown to the ViewModel

```csharp
// Adapters/UserAvatar/AvatarImageSource.cs — token translation + event translation
public static class AvatarImageSource
{
    private static readonly Dictionary<string, int> SizePx = new() { ["Sm"] = 32, ["Lg"] = 96 };
    public static ImageSource For(string name, string sizeToken)
        => ImageSource.FromUri(new Uri($"https://api.dicebear.com/9.x/beam/svg?seed={Uri.EscapeDataString(name)}&size={SizePx[sizeToken]}"));
}
```

```xml
<!-- Adapters/UserAvatar/UserAvatarView.xaml — lifecycle (caching/failure fallback) owned here;
     the library's theming API maps to tokens inside this file only -->
<Image Source="{Binding Source, Converter={StaticResource AvatarConverter}}"
       HeightRequest="{Binding SizePx}" VerticalOptions="Start" />
```

The ViewModel binds only `Name` and `SizeToken` — it has no idea a URI-backed image plugin renders the face.

## 4. Models, data layer, deriver

```csharp
// Entities/User.cs
public sealed record User(int Id, string Name, string Email, UserRole Role);
public enum UserRole { Admin, Editor, Viewer }

// the derived view type — the XAML views bind THIS, never User (derive before you bind)
public sealed record DisplayUser(string FullName, string Email, string RoleBadge);

// Features/Users/Blockiyas/UserProfileBlock/UserProfileDeriver.cs — module scope, stable
public static class UserProfileDeriver
{
    private static readonly Dictionary<UserRole, string> Badges = new()
        { [UserRole.Admin] = "Admin", [UserRole.Editor] = "Editor", [UserRole.Viewer] = "Viewer (read only)" };
    public static DisplayUser Derive(User u) => new(u.Name, u.Email, Badges[u.Role]);
}

// Features/Users/Services/IUserRepository.cs — the "queries/" layer: DI'd, never inline HTTP
public interface IUserRepository { Task<User> GetAsync(int id, CancellationToken ct); Task<User> SaveAsync(User u, CancellationToken ct); }
```

## 5. Intent lifecycle — `useIntent` already exists in the ecosystem

CommunityToolkit.Mvvm's `AsyncRelayCommand` (e.g.) gives the exact `useIntent` contract for free: `IsRunning` = `isLoading`, `ExecutionTask.Exception` handling = `error`, `CanExecute` gating = disabled buttons. Where it doesn't cover a case, a tiny `IntentRunner` mirrors the TS utility 1:1 — same named-ownership rule, native expression:

```csharp
// Shared/BlockiyaCore/IntentRunner.cs  (port of useIntent — one owner for the lifecycle)
public sealed class IntentRunner : ObservableObject
{
    [ObservableProperty] private bool _isRunning;
    [ObservableProperty] private string? _lastError;

    public event EventHandler? Ran;
    public async Task Run(Func<CancellationToken, Task> handler, CancellationToken ct = default)
    {
        IsRunning = true; LastError = null;
        try { await handler(ct); }
        catch (Exception ex) { LastError = ex.Message; }
        finally { IsRunning = false; Ran?.Invoke(this, EventArgs.Empty); }
    }
}
```

## 6. The Blockiya — `UserProfileViewModel`

Zero-styling is trivially satisfied (C# renders nothing). It owns state, talks to the service, derives before exposing, fires events and **stops**.

```csharp
// Features/Users/Blockiyas/UserProfileBlock/UserProfileViewModel.cs
public partial class UserProfileViewModel : ObservableObject
{
    private readonly IUserRepository _repo;
    private User? _source;                       // server truth (reactive source)

    [ObservableProperty] private bool _isBusy = true;
    [ObservableProperty] private string? _loadError;
    [ObservableProperty] private bool _isEditing;
    [ObservableProperty] private User? _draft;   // useDerivedState: editable, re-seeded on source change
    public IntentRunner SaveIntentRunner { get; } = new();

    public DisplayUser? Display => _source is null ? null : UserProfileDeriver.Derive(_source);

    // intents out — the ViewModel's job ends at raising them
    public event Action<User>? SaveIntent;
    public event Action<int>? DeleteIntent;

    public UserProfileViewModel(IUserRepository repo) => _repo = repo;

    public async Task LoadAsync(int id, CancellationToken ct)
    {
        IsBusy = true; LoadError = null;
        try
        {
            _source = await _repo.GetAsync(id, ct);
            Draft = _source with { };            // draft re-seeds whenever source arrives/changes
            OnPropertyChanged(nameof(Display));
        }
        catch (Exception ex) { LoadError = ex.Message; }
        finally { IsBusy = false; }
    }

    public void StartEdit() { Draft = _source; IsEditing = true; }
    public void CancelEdit() { Draft = _source; IsEditing = false; }   // discard = re-seed, not mutate

    [RelayCommand]
    private Task SaveAsync(CancellationToken ct) => SaveIntentRunner.Run(async ct =>
    {
        if (Draft is null) return;
        var saved = await _repo.SaveAsync(Draft, ct);
        _source = saved; Draft = saved;          // server truth flows through the deriver
        IsEditing = false;
        OnPropertyChanged(nameof(Display));
        SaveIntent?.Invoke(saved);               // fire upward — and STOP
    }, ct);

    [RelayCommand]
    private void RequestDelete() => DeleteIntent?.Invoke(_source?.Id ?? 0);  // no confirm here
}
```

## 7. The view and the page

`UserProfileView.xaml` composes **primitives only** (token styles, `TextBlock`, `Text`, spacing via styles) and binds — it contains no logic; the code-behind is empty, which is the tell that the split is honest:

```xml
<!-- Features/Users/Blockiyas/UserProfileBlock/UserProfileView.xaml (excerpt) -->
<VerticalStackLayout Spacing="{StaticResource SpaceMd}" BindingContext="{Binding .}">
    <Label Text="Loading…" Style="{StaticResource LabelMuted}" IsVisible="{Binding IsBusy}" />
    <Label Text="{Binding LoadError}" Style="{StaticResource LabelDanger}" IsVisible="{Binding LoadError, Converter={StaticResource IsNotNull}}" />

    <!-- display state -->
    <VerticalStackLayout IsVisible="{Binding IsEditing, Converter={StaticResource Invert}}">
        <adapter:UserAvatarView Name="{Binding Display.FullName}" SizeToken="Lg" />
        <TextBlock Text="{Binding Display.FullName}" Tone="Heading" />
        <TextBlock Text="{Binding Display.Email}" Tone="Muted" />
        <TextBlock Text="{Binding Display.RoleBadge}" Tone="Label" />
        <Button Text="Actions" Command="{Binding OpenActionsCommand}" />   <!-- popup owns open state -->
    </VerticalStackLayout>

    <!-- edit state — controlled inputs: TwoWay to Draft fields only -->
    <VerticalStackLayout IsVisible="{Binding IsEditing}">
        <Entry Text="{Binding Draft.Name}" />
        <Entry Text="{Binding Draft.Email}" />
        <Button Text="Save" Command="{Binding SaveCommand}"
                IsVisible="{Binding SaveIntentRunner.IsRunning, Converter={StaticResource Invert}}" />
        <ActivityIndicator IsRunning="{Binding SaveIntentRunner.IsRunning}" />
        <Button Text="Cancel" Command="{Binding CancelEditCommand}" />
    </VerticalStackLayout>
</VerticalStackLayout>
```

The **Page** is the React `<<Page>>` equivalent: subscribes to intents, owns the post-intent UX — confirmation and navigation are XAML/code-behind concerns, never the ViewModel's:

```csharp
// Features/Users/ UserPage.xaml.cs — post-intent decisions live here
public partial class UserPage : ContentPage
{
    private readonly UserProfileViewModel _vm;
    public UserPage(UserProfileViewModel vm) { _vm = vm; BindingContext = vm;
        _vm.SaveIntent += async u => await this.ToastAsync("Profile saved");   // page decides
        _vm.DeleteIntent += async id => {
            if (await DisplayAlert("Delete", "Delete this account?", "Yes", "No"))  // confirm HERE
                { await Repo.DeleteAsync(id); await Shell.Current.GoToAsync(".."); }
        };
    }
    protected override async void OnAppearing() => await _vm.LoadAsync((int)BindingContext.Id, CancellationToken);
}
```

## Port notes

- **The MVVM analogy the user drew is load-bearing:** MAUI already separates knows (ViewModel) from shows (XAML). Blockiya doesn't fight it — it sharpens it: derived records over raw entity binding, intent events over service calls inside VMs, adapters over raw plugin references in XAML, 3–7 ceiling as a refactor signal on VM public surfaces.
- `AsyncRelayCommand.IsRunning`/`CanExecute` = `useIntent`'s `isLoading` + disabled button — MAUI ships the canonical intent lifecycle; `IntentRunner` is shown only for stacks that don't.
- "Zero styling" translates to: composing views reference **token resources/styles only**; literal `Color`/`Thickness` values belong in `tokens.xaml` and primitive internals.
- `Display` is the mechanical "derive before you pass": XAML binds `DisplayUser` and cannot see `UserRole` exists — same as the Dumb views in the React/Vue ports.
