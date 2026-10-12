# Chapter 10: Building world-ready applications

## Core Idea
Anything exposed to the user — strings, dates, numbers, sort order, calendars — depends on region and culture. Making an app **world-ready** means never hard-coding those assumptions: separate user-facing strings from code (resources), let .NET pick the right version at runtime by **CultureInfo**, and use an **invariant culture** for machine-to-machine (persisted) data. The chapter reworks a console air-conditioner controller (`ACController`) through the full **internationalization** process.

## Frameworks Introduced
- **Microsoft.Extensions.Logging**: Write a log message once; multiple providers/subscribers consume it independently. Pluggable via `ILogger` / `ILoggerProvider` and a `LoggerFactory` with chained `Add*()` extension methods (`AddConsole()`, or a custom `AddRobust()`). *Use when* logs must fan out to several sinks (files, web services) that vary by deployment. *How*: implement `ILogger` + `ILoggerProvider`, register with `factory.AddProvider(...)`, create loggers with `loggerFactory.CreateLogger<T>()`.
- **Localization extensions (IStringLocalizer / resource files)**: `Microsoft.Extensions.Localization` wraps `ResourceManager` in an intuitive indexer API. Backed by `.restext`/`.resx` resource files compiled into satellite assemblies per culture. *Use when* you want the default (neutral) string to live in code as the lookup key. *How*: `ResourceManagerStringLocalizerFactory.Create(type)` → `IStringLocalizer`; look up with `localizer["Full text {0}", arg]`.
- **EventSource / EventListener**: A producer/consumer event system in .NET Standard. On Windows, `EventSource` taps kernel **ETW**; works cross-platform without ETW. *Use when* the same telemetry must reach several consumers with different formats/filters (e.g. localized log for user, invariant log for manufacturer), possibly cross-process. *How*: subclass `EventSource` with `[Event(id)]` methods calling `WriteEvent(id, ...)`; subclass `EventListener`, override `OnEventWritten`, and `EnableEvents(source, level)`.

## Key Concepts
- **Internationalization (i18n)** — *i + 18 letters + n*. The **overall process**, comprising three steps: Globalization, Localizability review, Localization. NOT a synonym for the steps.
- **Globalization (g11n)** — aka *world-readiness*. **Designing/developing** so the app can *adapt* to any region/culture (strings, dates, numbers, sort order, formats). Does NOT mean every culture ships built-in — you must not need code changes to add a language later.
- **Localizability review (l12y)** — a **review step** (like a code review focused on globalization) verifying the app is globalized and ready for translation. Uses dummy cultures to surface breakage (e.g. string-length assumptions).
- **Localization (l10n)** — the **act of translating** resources into specific cultures (produce Spanish/Arabic resource files). Happens late in the lifecycle; usually outsourced to translators.
- **Invariant culture** — a fixed, install-independent culture built into .NET; use for persisted/machine-consumed data so formats don't shift with politics or user locale.

## Mental Models
- **Key/resource separation**: the string is a *resource* retrieved by *key*; code holds the key, resource files hold the translations. Satellite assemblies (`<culture>/App.resources.dll`) are searched by `ResourceManager` based on culture.
- **Two audiences, two cultures**: user gets localized output (`CurrentUICulture`); manufacturer gets **invariant** culture + `DateTime.UtcNow`. EventSource lets one emit feed both listeners.
- **CurrentCulture vs CurrentUICulture**: `CurrentCulture` = formatting (dates, times, numbers, sort). `CurrentUICulture` = which resources `ResourceManager` loads. Culture is per-*thread* (use `CultureInfo.DefaultThreadCurrent(UI)Culture` for all threads; async/await flows culture across threads).

## Anti-patterns
- **String concatenation for sentences**: `"Exhaust Air Temp: " + value + " C"` bakes in word order; breaks RTL languages (the `C` should be on the left). Use placeholders `{0}` inside the resource string instead.
- Hard-coding `Console.WriteLine` as "the log" — no way to redirect or vary by culture/sink.
- Assuming translated strings are the same length as English.
- Using `ResourceManager` keys like `ExhaustAirTemp` — developer can't see the actual message without opening the resx, and a missing key throws.
- Persisting data in the user's culture (calendar/number formats drift → unparseable by back-end).

## Code Examples
```csharp
// 1. ILogger via Microsoft.Extensions.Logging — custom provider chained on the factory
var loggerFactory = new LoggerFactory().AddRobust();          // AddRobust = custom extension
ILogger logger = loggerFactory.CreateLogger<Telemetry>();

public class RobustLogger : ILogger
{
    public IDisposable BeginScope<TState>(TState state) => throw new NotImplementedException();
    public bool IsEnabled(LogLevel logLevel) => logLevel > LogLevel.Debug;   // everything above Debug
    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state,
        Exception exception, Func<TState, Exception, string> formatter)
        => Console.WriteLine(string.Join(" ",
               DateTime.Now.ToString(CultureInfo.InvariantCulture.DateTimeFormat), // invariant for persistence
               logLevel, formatter(state, exception)));
}
public class RobustLoggerProvider : ILoggerProvider
{
    public ILogger CreateLogger(string categoryName) => new RobustLogger();
    public void Dispose() { }
}
public static class RobustLoggerExtension
{
    public static LoggerFactory AddRobust(this LoggerFactory factory)
    { factory.AddProvider(new RobustLoggerProvider()); return factory; }
}

// 2. IStringLocalizer pulling a resx/restext string — full text IS the key
var locOptions = new LocalizationOptions { ResourcesPath = "resources" };
var resourceFactory = new ResourceManagerStringLocalizerFactory(
    Options.Create(locOptions), loggerFactory);
IStringLocalizer localizer = resourceFactory.Create(typeof(Telemetry));
logger.LogInformation(localizer["Exhaust Air Temp: {0} C"], TempControl.ExhaustAirTemp);
// If the key isn't found, IStringLocalizer writes the key itself (no exception).

// 3. EventSource emitting localized events + EventListener consuming them
[EventSource(LocalizationResources = "ACController.resources.EventSource")]
public class ACControllerEventSource : EventSource
{
    [Event(1)] public void ExhaustAirTemp(double temp) => WriteEvent(1, temp);  // key: event_ExhaustAirTemp
    [Event(2)] public void CoolantTemp(double temp)    => WriteEvent(2, temp);
    [Event(3)] public void OutsideAirTemp(double temp) => WriteEvent(3, temp);
}
public class ConsoleEventListener : EventListener
{
    protected override void OnEventWritten(EventWrittenEventArgs e)
        => Console.WriteLine(e.Message, e.Payload[0]);   // e.Message is the localized template
}
// wiring:
using var listener = new ConsoleEventListener();
listener.EnableEvents(Controller.Events, EventLevel.Verbose);
```
- **What it demonstrates**: (1) a custom logging provider registered through a chained extension method and forced to invariant-culture timestamps; (2) `IStringLocalizer` using the human-readable string as the lookup key so the message is visible in code and never throws on a miss; (3) an `EventSource` whose event messages are localized via `LocalizationResources` (convention key `event_<MethodName>`) and an `EventListener` that receives the already-localized `Message` with substitutable `Payload`.

## Reference Tables

| Term | Abbr | One line |
|------|------|----------|
| Internationalization | i18n | The whole process = globalization + localizability review + localization |
| Globalization | g11n | World-readiness: design so the app *can adapt* to any culture without code changes |
| Localizability review | l12y | Review/test step confirming it's globalized and ready to translate (dummy cultures) |
| Localization | l10n | Actually translating resources for specific cultures |
| Invariant culture | — | Fixed built-in culture for persisted/back-end data |

| Culture concern | API / guidance |
|-----------------|----------------|
| Formatting (dates, numbers, sort) | `Thread.CurrentThread.CurrentCulture` |
| Which resources to load | `Thread.CurrentThread.CurrentUICulture` (used by `ResourceManager`) |
| Create a culture | `CultureInfo.CreateSpecificCulture("es-MX")` / `"ar-SA"` / `"en-US"` |
| All threads | `CultureInfo.DefaultThreadCurrentCulture` / `DefaultThreadCurrentUICulture` |
| Persisted / machine data | `CultureInfo.InvariantCulture`; `DateTime.UtcNow` for timestamps |
| Neutral/default culture | omit culture code in filename, or `[assembly: NeutralResourcesLanguage("en-US", UltimateResourceFallbackLocation.Satellite)]` |
| Metric region? | `RegionInfo.IsMetric` |
| restext → resources | `GenerateResource` MSBuild task; embed via `<EmbeddedResource>`; satellite dir `<culture>/App.resources.dll` |

## Worked Example
Take the Chapter 2 `ACController` console app and make it world-ready end-to-end:
1. **Extract strings.** Move `"Exhaust Air Temp:"` out of `Program.cs` into `strings.restext` as `ExhaustAirTemp=Exhaust Air Temp:`. Add `<Resx Include="*.restext"/>` + `<EmbeddedResource Include="*.resources"/>` and a custom MSBuild target running `GenerateResource` (`ExecuteAsTool="false"`); retrieve with `ResourceManager`. Add `strings.es-MX.restext` → builds an `es-MX/ACController.resources.dll` **satellite assembly**.
2. **Swap Console for logging.** Introduce `Microsoft.Extensions.Logging`; build `LoggerFactory().AddRobust()`, inject `ILogger` into `Telemetry`, call `logger.LogInformation(...)`.
3. **Globalize the sentence.** Replace concatenation with placeholders: `ExhaustAirTemp=Exhaust Air Temp: {0} C` so translations reposition `{0}` and `C`.
4. **Adopt IStringLocalizer.** Add `Microsoft.Extensions.Localization`; set `ResourcesPath="resources"`; `resourceFactory.Create(typeof(Telemetry))`; look strings up by full text (`localizer["Exhaust Air Temp: {0} C"]`) — runs even before resources exist (writes the key).
5. **Localizability review.** Do a globalization-focused review; spin up dummy cultures to catch string-length / word-order breakage.
6. **Localize + test RTL.** Add `resources/Telemetry.ar-SA.restext` (Arabic). Set `CultureInfo.CreateSpecificCulture("ar-SA")` on both culture properties. Windows console can't render Arabic/RTL — redirect `dotnet run >> output.txt` and inspect in an editor. (In .NET Core 2.0, publish self-contained so satellite assemblies resolve; use `--no-incremental` since MSBuild misses resource changes.)
7. **Split audiences with EventSource.** Add `ACControllerEventSource` with `LocalizationResources`; `Telemetry.LogStatus()` now only emits events. Register two `EventListener`s — `ConsoleEventListener` (localized, user) and `LoggerEventListener` (feeds `RobustLogger`, invariant culture + UTC, manufacturer). `Controller` becomes `IDisposable` to dispose the listener.

## Key Takeaways
- Separate user-facing text into resource files; let culture select the variant at runtime.
- restext is the simple string-only format; `.resx` (tool-edited XML) is the common richer format.
- `IStringLocalizer` lets the full default string be the key — visible in code, no exceptions, no default resource file needed until translation time (a reason to keep a dummy culture forcing resource creation).
- Use invariant culture + UTC for anything persisted or sent machine-to-machine.
- `EventSource`/`EventListener` decouples emission from formatting and offers keyword filtering; multiple listeners can route the same event to different destinations.
- Most important rule: make no assumptions about how user↔app communication is perceived. Currencies need a stored denomination; numbers stored invariant; addresses/phones/units aren't in the framework.

## Connects To
- **Ch 2**: The `ACController` console app and self-contained publishing (`dotnet publish -r <rid>`) needed for satellite assemblies to resolve in .NET Core 2.0.
- **Ch 6**: The method-chaining / extension-method pattern reused for `AddRobust()` on `LoggerFactory`.
- **Ch 9**: `EventSource` ties into ETW / PerfView diagnostics — the same event infrastructure used for performance tracing.
