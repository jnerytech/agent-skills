# Patterns & Techniques — .NET Core in Action

## Target netstandard for shared libraries
**When**: code meant to run on more than one .NET platform (backend + mobile + desktop).
**How**: set `<TargetFramework>netstandard2.0</TargetFramework>`; target a concrete `netcoreapp*`/`net4x` only for apps or platform-specific code.
**Trade-offs**: lower `netstandard` version = wider reach, fewer APIs. Pick the lowest version that still exposes the APIs you need.

## xcopy / self-contained deployment
**When**: containers, side-by-side versions, hosts without a pre-installed framework.
**How**: `dotnet publish -c Release` (add `-r <RID> --self-contained` to bundle the runtime); copy the output folder.
**Trade-offs**: self-contained = no install dependency but larger payload + you own patching the bundled runtime.

## Multi-targeting with conditional MSBuild
**When**: one library must support several frameworks/runtimes with per-target code.
**How**: `<TargetFrameworks>netstandard2.0;net461</TargetFrameworks>`; guard code with `#if NET461` / `RuntimeInformation.IsOSPlatform(...)`; use `<PropertyGroup Condition="'$(TargetFramework)'=='net461'">` for per-TFM options.
**Trade-offs**: `#if` is compile-time (per TFM); `RuntimeInformation` is runtime (per RID) — use the former for API availability, the latter for OS behavior.

## Arrange-Act-Assert unit test (xUnit)
**When**: verifying a unit of logic.
**How**: `[Fact]` for a single case; promote to `[Theory]` + `[InlineData]`/`[MemberData]` when you can't prove all cases exhaustively. Share setup via constructor; clean up via `IDisposable.Dispose`; share expensive context via `IClassFixture`/`ICollectionFixture`.
**Trade-offs**: fixtures reduce setup cost but couple tests — keep fixture state read-only.

## Parameterized ADO.NET data access
**When**: hand-rolled SQL against a relational DB.
**How**: build a `SqliteCommand`, add values with parameters (`AddParameter`/`@name`), never string-concatenate input; read via `DataReader`; wrap multi-step writes in a `Transaction`.
**Trade-offs**: max control + performance, max boilerplate. Concatenating SQL = injection vuln — always parameterize.

## Micro-ORM (Dapper)
**When**: you want object mapping but keep full control of the SQL.
**How**: `connection.Query<T>(sql, params)` / `connection.Execute(sql, params)`; pass an open transaction to commands for atomicity.
**Trade-offs**: fast, thin; no change tracking/migrations — you still write and maintain SQL.

## Full ORM (EF Core)
**When**: you want the DB modeled from code with generated schema + LINQ.
**How**: define a `DbContext` with `DbSet<T>` properties; query with LINQ; evolve schema via EF migrations.
**Trade-offs**: least boilerplate, most abstraction; watch generated SQL for N+1 and over-fetching.

## Dependency injection wiring
**When**: decoupling services (data access, config, clients) for testability.
**How**: register in `IServiceCollection` — `AddTransient` (per resolve), `AddScoped` (per request), `AddSingleton` (per app); inject via constructor.
**Trade-offs**: pick the shortest lifetime that's correct; a Singleton holding a Scoped dependency is a captive-dependency bug.

## Async ASP.NET Core service call
**When**: any I/O-bound service work (HTTP, storage, DB).
**How**: `async` action returning `Task<IActionResult>`; `await` `HttpClient`/storage calls; reuse one `HttpClient`.
**Trade-offs**: never block async with `.Result`/`.Wait()` — deadlocks/thread starvation.

## Config-driven external resources
**When**: secrets/endpoints (e.g. Azure Blob) that vary per environment.
**How**: layer `IConfiguration` (JSON + env + in-memory for tests); read connection values from config, never hard-code.
**Trade-offs**: keeps secrets out of source; requires disciplined env setup.

## Profile before optimizing
**When**: a performance concern is suspected.
**How**: track microbenchmarks with xUnit.Performance `[Benchmark]`; capture a trace with PerfView (CPU Stacks / GCStats / Exception Stacks) or `perfcollect` on Linux; fix the measured hot path, then re-measure.
**Trade-offs**: measuring costs time but prevents optimizing the wrong thing; profile in Release on representative data.

## Layered diagnostics: IDE debugger → SOS
**When**: a bug survives IDE debugging or only reproduces in production/Linux.
**How**: start with VS Code (`launch.json`)/VS/VS for Mac breakpoints; escalate to SOS under WinDBG/CDB (Windows) or LLDB (Linux/mac) on a self-contained app to inspect heap/stacks/exceptions.
**Trade-offs**: SOS is powerful but host-specific (command syntax differs) — reserve for what the IDE can't show.

## World-ready from the start
**When**: any app that may ship in multiple locales.
**How**: replace `Console.Write` with `Microsoft.Extensions.Logging`; extract UI strings to resource files behind `IStringLocalizer`; persist/interchange data in **invariant culture**; run a localizability review; test an RTL language.
**Trade-offs**: retrofitting i18n late is expensive; invariant-culture storage prevents locale-dependent parsing bugs.

## Publish a NuGet package
**When**: distributing a library.
**How**: set `.csproj` metadata (`PackageId`, `Version`, `Authors`); `dotnet pack`; handle project references + resource/satellite assemblies; `dotnet nuget push` to a feed. Optionally strong-name/delay-sign for identity.
**Trade-offs**: strong naming gives identity, not tamper protection; multi-target packages ship one folder per TFM.
