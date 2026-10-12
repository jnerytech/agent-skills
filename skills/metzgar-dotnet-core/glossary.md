# Glossary — .NET Core in Action

**ADO.NET** — low-level data-access API: Connection/Command/DataReader/Transaction (Ch 5).
**AppDomain** — Framework isolation boundary for unloading assemblies; not ported to Core (Ch 1).
**ASP.NET Core** — rewritten, cross-platform web stack (dropped `System.Web`); 1M+ req/s (Ch 1, 2, 7).
**async/await** — C# constructs for non-blocking I/O-bound work (Ch 7).
**Azure Blob Storage** — cloud object store accessed over REST/signed HTTP (Ch 7).
**[Benchmark]** — xUnit.Performance attribute marking a microbenchmark method (Ch 9).
**Class fixture (IClassFixture)** — xUnit shared context across all tests in one class (Ch 4).
**CLI (dotnet)** — cross-platform command-line tooling; the book's lowest-common-denominator surface (Ch 1, 2).
**CLR** — Common Language Runtime; managed execution engine (GC + JIT) (Ch 1).
**Collection fixture (ICollectionFixture)** — xUnit shared context across multiple test classes (Ch 4).
**Configuration** — layered settings (JSON/env/in-memory) via `IConfiguration` (Ch 6, 7).
**CultureInfo** — represents a locale for globalization/formatting (Ch 10).
**Dapper** — micro-ORM: maps query results to objects, you write the SQL (Ch 6).
**DataReader** — forward-only streaming reader over query results (Ch 5).
**DbContext / DbSet** — EF Core's unit-of-work and per-entity query surface (Ch 6).
**Delay-signing** — sign an assembly's identity later, deferring the private key (Ch 12).
**Dependency Injection (DI)** — supplying dependencies via `IServiceCollection`; lifetimes Transient/Scoped/Singleton (Ch 6).
**Entity Framework Core (EF Core)** — full ORM with LINQ queries + migrations (Ch 6).
**EventListener** — in-process consumer of `EventSource` events (Ch 10).
**EventSource** — structured event emitter (ETW/EventPipe), replaces EventProvider (Ch 10, 11).
**[Fact]** — xUnit attribute for a parameterless, always-true-or-fail test (Ch 4).
**Globalization** — making code culture-aware (formatting, calendars) (Ch 10).
**HttpClient** — client for outbound HTTP calls; reuse instances (Ch 7).
**Internationalization (i18n)** — the overall process of making an app world-ready (Ch 10).
**Invariant culture** — culture-neutral formatting for persisted/interchange data (Ch 10).
**IStringLocalizer** — pulls localized strings from resource/satellite assemblies (Ch 10).
**ItemGroup** — MSBuild element listing inputs (files, references, packages) (Ch 3).
**JIT** — just-in-time compilation of IL to native code (Ch 1, 9).
**Kestrel** — ASP.NET Core's cross-platform web server (Ch 2, 7).
**launch.json** — VS Code debug configuration file (Ch 8).
**LLDB** — cross-platform native debugger; hosts SOS on Linux/macOS (Ch 8).
**Localizability review** — audit that an app *can* be localized before doing it (Ch 10).
**Localization (l10n)** — producing locale-specific resources (Ch 10).
**Micro-ORM** — thin object mapper (Dapper) with hand-written SQL (Ch 6).
**Microsoft.Extensions.Logging** — pluggable logging abstraction (`ILogger`) (Ch 10).
**Migration (EF)** — versioned schema change generated from model diffs (Ch 6).
**MSBuild** — the build engine driving `.csproj` (PropertyGroups/Targets/ItemGroups) (Ch 3).
**.NET Core** — framework + .NET Standard Library + common infrastructure (Ch 1).
**.NET Standard Library** — API contract shared by all .NET implementations (Ch 1, App C).
**NuGet** — package manager/format (`.nupkg`) and feeds (Ch 6, 11, 12).
**PackageReference** — `.csproj` element declaring a NuGet dependency (Ch 3).
**PerfView** — Windows profiler for CPU/GC/exceptions on Core (Ch 9).
**perfcollect** — script to capture perf traces on Linux via EventPipe (Ch 9).
**Portability Analyzer** — reports which Framework APIs won't port to Core (Ch 1, 11).
**PropertyGroup** — MSBuild element holding build properties (Ch 3).
**RID (Runtime Identifier)** — OS/arch target string (e.g. `linux-x64`), hierarchical (Ch 11, App A).
**RuntimeInformation** — API to branch on OS/architecture at runtime (Ch 11).
**Self-contained app** — app published with its runtime, no machine-wide install (Ch 2, 8).
**Service lifetime** — Transient (per resolve) / Scoped (per request) / Singleton (per app) (Ch 6).
**SOS (Son of Strike)** — debugger extension for inspecting managed state (Ch 8).
**SQLite** — file/in-memory relational DB, ideal for prototyping/tests (Ch 5).
**Startup class** — configures services + request pipeline in ASP.NET Core (Ch 2, 7).
**Strong name** — cryptographic assembly *identity* (not tamper security) (Ch 12).
**Target Framework Moniker (TFM)** — build target string (`netstandard2.0`, `netcoreapp2.0`, `net461`) (Ch 3, 11, App A).
**Target (MSBuild)** — a named, ordered set of build tasks (Ch 3).
**[Theory] / [InlineData]** — xUnit data-driven test with supplied cases (Ch 4).
**Trait** — xUnit test category metadata for filtering (Ch 4).
**Transaction** — atomic all-or-nothing set of DB operations (Ch 5).
**TypeInfo** — Core's home for reflection ops moved off `Type` (Ch 1).
**WinDBG / CDB** — Windows native debuggers hosting SOS (Ch 8).
**xcopy-deployable** — deploy by copying a self-contained folder (Ch 1).
**xUnit** — the .NET Core unit-test framework used throughout (Ch 4).
**xUnit.Performance** — microbenchmark harness built on xUnit (Ch 9).
