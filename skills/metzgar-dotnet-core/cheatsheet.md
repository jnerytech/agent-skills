# Cheatsheet — .NET Core in Action

## Decision rules
- **Building a reusable library?** → target `netstandard` (lowest version that has your APIs). **An app?** → target `netcoreapp*`.
- **Need to run without a framework install / in a container?** → `dotnet publish -r <RID> --self-contained`.
- **Data access — which tool?** → hand-rolled ADO.NET only if you need max control/perf; **Dapper** if you want mapping but own the SQL; **EF Core** if you want code-first schema + LINQ + migrations.
- **DI lifetime?** → stateless service = `Transient`; per-web-request state = `Scoped`; shared/expensive+thread-safe = `Singleton`. Never inject a shorter-lived service into a longer-lived one (captive dependency).
- **Can't prove all test cases with one `[Fact]`?** → use `[Theory]` + `[InlineData]`.
- **Sharing test setup?** → same class: constructor; cleanup: `Dispose`; across-class expensive: `IClassFixture`/`ICollectionFixture`.
- **Branching per platform?** → API availability = `#if <TFM>` (compile-time); OS behavior = `RuntimeInformation.IsOSPlatform` (runtime).
- **Perf concern?** → measure first (xUnit.Performance → PerfView/perfcollect), fix the hot path, re-measure. Never optimize unmeasured.
- **Bug survives the IDE debugger?** → escalate to SOS (WinDBG/CDB on Windows, LLDB on Linux/mac) against a self-contained app.
- **Porting a Framework app?** → run the **Portability Analyzer** before writing any code.

## Framework (TFM) vs Runtime (RID)
| | Selects | Examples | Branch with |
|---|---|---|---|
| **TFM** | which API surface you compile against | `netstandard2.0`, `netcoreapp2.0`, `net461` | `#if`, `<TargetFrameworks>` |
| **RID** | which OS/arch you run on | `win-x64`, `linux-x64`, `osx-x64` | `RuntimeInformation`, `-r` on publish |

RID is hierarchical: `linuxmint.17.1-x64` → `linuxmint.17.1` → `linuxmint` → `linux`. If a specific RID fails, try a broader parent.

## DI service lifetimes
| Register | Instance per | Use for |
|---|---|---|
| `AddTransient` | every resolve | lightweight stateless services |
| `AddScoped` | web request | per-request state (e.g. DbContext) |
| `AddSingleton` | app lifetime | shared, thread-safe, expensive-to-create |

## ORM trade-off
| | ADO.NET | Dapper | EF Core |
|---|---|---|---|
| SQL written by | you | you | generated |
| Boilerplate | high | low | lowest |
| Migrations | none | none | yes |
| Change tracking | no | no | yes |
| Best when | max control | thin mapping | code-first + LINQ |

## Not ported to Core (find a replacement)
WPF/XAML · AppDomains · .NET Remoting (→REST) · ASMX (→Web API) · LINQ to SQL (→EF Core) · WCF *services* (client only) · WF · distributed `System.Transactions`.

## i18n terms (not synonyms)
- **Internationalization (i18n)** = the whole world-ready process.
- **Globalization** = culture-aware code (formatting/calendars).
- **Localizability review** = check it *can* be localized.
- **Localization (l10n)** = produce locale resources.
- **Invariant culture** = use for persisted/interchange data.

## Common SOS commands (App index)
`!dumpheap -stat` (heap by type) · `!do <addr>` (dump object) · `!da <addr>` (dump array) · `!clrstack -a` (managed stack + args) · `!help` (SOS help).

## xUnit CLI (via test runner, App B)
`-trait "name=value"` (OR filter) · `-notrait` (AND exclude) · `-method`/`-class`/`-namespace "fully.qualified"` (target) · `-parallel none|collections|assemblies|all` · `-xml <file>` (results). Note: `dotnet test -?` shows CLI help, not xUnit's.

## .NET Standard by version (App C, cumulative)
- **1.0** collections, LINQ, IO streams, reflection, regex, tasks, XML r/w
- **1.1** +concurrent collections, ETW, HTTP, Numerics, PLINQ
- **1.3** +file IO, sockets, console, cryptography
- **1.5** +AssemblyLoadContext · **1.6** +OpenSSL crypto
- **2.0** +XLinq/XmlDocument/XPath/XSL, serialization, DataSet, Mail/WebSockets, memory-mapped files, thread pools

## NuGet cache locations (App D)
- Downloaded `.nupkg`: Mac/Linux `~/.local/share/NuGet/Cache` · Windows `%LocalAppData%\NuGet\Cache`
- Extracted (used at build): Mac/Linux `~/.nuget/packages` · Windows `%UserProfile%\.nuget\packages`

## Key `dotnet` verbs
`new` (scaffold) · `restore` · `build` · `run` · `test` · `publish` (deploy+runtime) · `pack` (make .nupkg) · `nuget push` (upload) · `sln`/`add`/`remove` (solution & refs).
