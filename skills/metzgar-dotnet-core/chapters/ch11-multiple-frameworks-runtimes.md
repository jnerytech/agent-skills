# Chapter 11: Multiple frameworks and runtimes

## Core Idea
The .NET Standard gives one universal API surface, but it is not comprehensive. When you port from .NET Framework/Xamarin, or need OS-specific or version-specific behavior, a single project must emit code that varies by **framework** (which APIs are available) and/or by **runtime** (which OS you run on). The .NET Core SDK lets you consolidate all of that into one project and one NuGet package (`dotnet pack`). This chapter shows three tools: the **Portability Analyzer** (assess a port), **multi-targeting** (branch by framework at build time), and **runtime detection** (branch by OS at run time).

## Frameworks Introduced
- **.NET Portability Analyzer**: A tool (CLI executable + Visual Studio 2017 plugin) that reports where your code uses APIs unavailable in a chosen target framework and suggests substitutes. *When*: before/during a port from .NET Framework or Xamarin to .NET Core/Standard. *How*: install the VS plugin, set target platforms in settings, run from the project's right-click menu, read the results pane / HTML report, aim for 100%.
- **Multi-targeting (`TargetFrameworks` + conditional MSBuild)**: One project builds binaries for several **TFMs**. Add `<TargetFrameworks>` (plural), branch source with `#if` preprocessor directives, and add `Condition="'$(TargetFramework)' == '...'"` on `<PropertyGroup>`/`<ItemGroup>` to give each TFM its own references and to include/exclude files. *When*: an API exists on one framework but not another (e.g. `EventProvider` only on .NET Framework). *How*: build one TFM with `dotnet build --framework <tfm>`, or all TFMs with plain `dotnet build`.
- **Runtime-specific code (RIDs, `#if`, `RuntimeInformation`)**: Making code behave differently per OS. *When*: you call native/OS-specific libraries (libuv, zlib) via P/Invoke. *How*: NuGet does **not** branch by runtime the way it branches by framework and there are **no per-runtime build settings**, so you cannot use `#if` on the RID — you must detect the OS at run time with `RuntimeInformation.IsOSPlatform(OSPlatform.Windows/Linux)`. Declare supported runtimes with `<RuntimeIdentifiers>` so consumers know where the library works.

## Key Concepts
- **Framework (TFM) vs Runtime (RID) — the central distinction of the chapter:**
  - A **framework** is a *set of available APIs*, identified by a **Target Framework Moniker (TFM)** like `netstandard2.0`, `net45`/`net46`, `netcoreapp2.0`. Known at **build time** → branch with `#if` and MSBuild conditions.
  - A **runtime** is *akin to an operating system* (see §3.1.3), identified by a **Runtime Identifier (RID)** like `win-x64`, `linux-x64`, `osx-x64`, `osx.10.11-x64`, `ubuntu-x64`, or the broad `win`/`linux`. Only fully known at **run time** → branch with `RuntimeInformation`.
- A preprocessor directive runs *before compilation*. C# has no macros, but `#if`/`#endif` give conditionally compiled code.
- The preprocessor symbol is **auto-derived from the TFM**: special chars → underscores, uppercased. So `net46` → `NET46`, `netcoreapp2.0` → `NETCOREAPP2_0`. You do not define these yourself.
- In a multi-target NuGet package, each TFM gets its own `lib/<tfm>/` folder and its own binary; an executable TFM ships an `.exe`, a non-self-contained .NET Core lib ships a `.dll` (see ch. 3).

## Mental Models
- **Two axes, two branch points.** Framework = *what APIs exist* (decided when compiling → `#if`). Runtime = *what OS you land on* (decided when executing → `RuntimeInformation`). Do not confuse them: you cannot `#if WIN_X64`.
- **NuGet folders = frameworks, not runtimes.** The package layout (`lib/net46`, `lib/netcoreapp2.0`) encodes framework variants only. Runtime variation lives inside one binary and resolves at run time.
- **Isolate the variant.** Put framework/OS-specific code in one class/file so the rest of the codebase stays clean.

## Anti-patterns
- Scattering `#if`/`#endif` throughout method bodies — hurts readability. Prefer isolating variant code in a dedicated class, or keep two whole files each fully wrapped in `#if`/`#endif` and include/exclude via `<Compile Remove/>` conditions.
- Trying to branch native code by runtime with `#if` or per-runtime build options — there are none; detect the OS at run time instead.
- Forgetting to exclude framework-incompatible files from compilation: `MyEventSource.cs` compiles fine under `net46` but fails under `net45` (no `EventChannel`) unless removed.
- Targeting `net45` when your code uses `EventChannel` — that class did not exist until `net46`. Either target `net46` or drop the `Channel` specification.

## Code Examples
```xml
<!-- Listing 11.11: multi-target csproj with per-framework references and file exclusion -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFrameworks>netcoreapp2.0;net45</TargetFrameworks>
    <RuntimeFrameworkVersion Condition=" '$(TargetFramework)' == 'netcoreapp2.0' ">2.0.0-*</RuntimeFrameworkVersion>
  </PropertyGroup>
  <ItemGroup Condition=" '$(TargetFramework)' == 'net45' ">
    <Reference Include="System" />
    <Reference Include="Microsoft.CSharp" />
    <Compile Remove="MyEventSource.cs" />   <!-- keep EventSource file out of the net45 build -->
  </ItemGroup>
</Project>
```
```csharp
// Listing 11.7/11.9: build-time branching by FRAMEWORK via preprocessor directives
using System;
#if NET45
using System.Diagnostics.Eventing;
#endif
namespace SampleEventSource {
  public class Program {
#if NET45
    private static readonly Guid Provider = Guid.Parse("B695E411-F53B-4C72-9F81-2926B2EA233A");
#endif
    public static void Main(string[] args) {
#if NET45
      var eventProvider = new EventProvider(Provider);      // old .NET Framework API
      eventProvider.WriteMessageEvent("Program started");
#else
      MyEventSource.Instance.ProgramStart();                 // .NET Core EventSource
#endif
      // Do some work
#if NET45
      eventProvider.WriteMessageEvent("Program completed");
      eventProvider.Dispose();
#else
      MyEventSource.Instance.ProgramStop();
#endif
    }
  }
}
```
```csharp
// Listing 11.15: run-time branching by RUNTIME (OS) via RuntimeInformation
using System;
using System.Runtime.InteropServices;
namespace Xplat {
  public static class PidUtility {
    public static int GetProcessId() {
      var isWindows = RuntimeInformation.IsOSPlatform(OSPlatform.Windows);
      var isLinux   = RuntimeInformation.IsOSPlatform(OSPlatform.Linux);
      if (isWindows)   return (int)Interop.WindowsPid.GetCurrentProcessId(); // DllImport native
      else if (isLinux) return Interop.LinuxPid.GetPid();                    // DllImport native
      else throw new PlatformNotSupportedException("Unsupported platform");
    }
  }
}
```
- **What it demonstrates**: The same problem solved on both axes. `#if NET45` picks *APIs* at compile time (one binary per TFM); `RuntimeInformation.IsOSPlatform` picks *OS implementations* at run time (one binary, many OSes). The MSBuild `Condition` attributes tailor references and source files per TFM without duplicating the whole project.

## Reference Tables

| Axis | Identifier | Examples | Means | Decided at | Branch with |
|------|-----------|----------|-------|-----------|-------------|
| **Framework** | TFM (Target Framework Moniker) | `netstandard2.0`, `net45`, `net46`, `netcoreapp2.0` | which APIs are available | build time | `#if`, `Condition` in csproj |
| **Runtime** | RID (Runtime Identifier) | `win-x64`, `linux-x64`, `osx-x64`, `osx.10.11-x64`, `ubuntu-x64`, `win`, `linux` | which OS/platform | run time | `RuntimeInformation.IsOSPlatform` |

| csproj element | Purpose |
|----------------|---------|
| `<TargetFramework>` | single TFM |
| `<TargetFrameworks>` (plural) | multi-target list, `;`-separated |
| `<RuntimeIdentifiers>` | declare supported RIDs (informational for consumers; no per-RID build) |
| `Condition="'$(TargetFramework)' == 'net45'"` | apply a PropertyGroup/ItemGroup to one TFM only |
| `<Compile Remove="File.cs" />` | exclude a source file from that TFM's build |

| Way to branch code | Granularity | Cost |
|--------------------|-------------|------|
| Multi-target build (`TargetFrameworks` + conditions) | per framework | separate binaries, biggest isolation |
| `#if`/`#endif` | per framework, inline | readability suffers if overused |
| `RuntimeInformation.IsOSPlatform` | per OS, run time | only option for runtime branching |

| Symbol derivation | TFM → symbol |
|-------------------|--------------|
| replace special chars with `_`, uppercase | `net46` → `NET46`, `netcoreapp2.0` → `NETCOREAPP2_0` |

## Worked Example
Porting a Windows event-logging console app to also run on .NET Core:
1. **Assess with the Portability Analyzer.** Install the VS 2017 plugin (Tools → Extensions and Updates → Online → "portability"), restart. In settings choose all .NET Core target platforms. Right-click the project → run. The results pane / HTML report flags `EventProvider` (`System.Diagnostics.Eventing`) as unavailable and suggests `EventSource`. (In the earlier latency sample, `WebRequest` was flagged with substitute `HttpClient`, which reached 100% on both frameworks.)
2. **Write the .NET Core replacement.** Create `MyEventSource.cs` deriving from `EventSource` with `[Event(...)]` methods (`ProgramStart`/`ProgramStop`, `Channel = EventChannel.Operational`, Start/Stop opcodes). Slim `Program.cs` to `MyEventSource.Instance.ProgramStart()/ProgramStop()`.
3. **Add the second framework.** In the csproj switch `<TargetFramework>` to `<TargetFrameworks>netcoreapp2.0;net46</TargetFrameworks>` (must be `net46`, not `net45` — `net45` lacks `EventChannel`). Build one TFM with `dotnet build --framework net46`, or all with `dotnet build`.
4. **Swap APIs per framework with `#if`.** Wrap the old `EventProvider` path in `#if NET46` and the new `EventSource` path in `#else`. The `NET46` symbol is auto-defined from the TFM.
5. **Package and inspect.** `dotnet pack` → rename `SampleEventSource.1.0.0.nupkg` to `.zip`. Inside: `lib/net46/SampleEventSource.exe`, `lib/netcoreapp2.0/SampleEventSource.dll`, plus `.nuspec`, `[Content_Types].xml`, `_rels/.rels`. Each TFM has its own folder and binary (`.exe` for the Framework executable, `.dll` for the non-self-contained Core lib).
6. **Handle a stricter target (`net45`).** Change to `net45`, fix `#if NET46` → `#if NET45`. Build fails (CS0246/CS0103: `EventChannel` missing) because `MyEventSource.cs` still compiles under net45. Add `<Compile Remove="MyEventSource.cs" />` inside the `net45` conditional ItemGroup (Listing 11.11). Now both frameworks build.
7. **Runtime axis (separate scenario).** In an `Xplat` project, add `Interop.WindowsPid.cs` and `Interop.LinuxPid.cs` (each a `[DllImport]` P/Invoke to the native `GetCurrentProcessId`/`SystemNative_GetPid`). Because runtime cannot be branched at build time, `PidUtility.GetProcessId()` calls `RuntimeInformation.IsOSPlatform(...)` to pick the right interop at run time. `dotnet run` prints the PID on Windows, Linux, or Docker. Declare `<RuntimeIdentifiers>win;linux</RuntimeIdentifiers>` (Listing 11.17) so consumers know supported OSes.

## Key Takeaways
- Framework (TFM) and runtime (RID) are different axes: APIs vs OS, build time vs run time.
- `<TargetFrameworks>` (plural) + `#if` + conditional MSBuild = one project, many frameworks; `dotnet pack` bundles all TFMs into one NuGet package with per-TFM `lib/` folders.
- Preprocessor symbols are auto-derived from the TFM (`net46`→`NET46`); don't hand-define them.
- There are **no per-runtime build options** and NuGet doesn't split by runtime — detect the OS at run time with `RuntimeInformation`.
- Run the Portability Analyzer first when porting; aim for 100% and take its substitution suggestions (`WebRequest`→`HttpClient`, `EventProvider`→`EventSource`).
- Watch version-specific API gaps (`EventChannel` needs `net46`, not `net45`) and exclude incompatible files with `<Compile Remove>`.

## Connects To
- **Ch 1**: .NET Standard as the common API baseline that Framework, Core, and Xamarin all implement; "ported vs unported" features are exactly what the Portability Analyzer measures.
- **Ch 3**: MSBuild project files, TFMs, self-contained vs framework-dependent deploys (why the Core binary is a `.dll` not an `.exe`), and including/excluding compile items — the mechanics multi-targeting builds on. Runtime ≈ OS per §3.1.3.
- **Ch 7 / Ch 10**: `HttpClient` (the Portability Analyzer's `WebRequest` substitute) and `EventSource` / event consumers reused here as the cross-framework replacements.
- **Ch 12**: NuGet packaging (`dotnet pack`), inspecting/publishing packages, and signing — the distribution step for the multi-target libraries built here.
