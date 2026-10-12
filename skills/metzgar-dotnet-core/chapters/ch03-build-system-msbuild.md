# Chapter 3: How to build with .NET Core

## Core Idea
.NET Core builds run on **MSBuild** driven by trimmed-down, convention-based `.csproj` files (C#), `.fsproj` (F#), `.vbproj` (VB). Where .NET Framework hid MSBuild behind Visual Studio, .NET Core targets the command line first and tooling second — so knowing the three MSBuild constructs (`PropertyGroup`, `Target`, `ItemGroup`) plus `PackageReference`/`ProjectReference` lets you customize builds by hand instead of copy-pasting from Stack Overflow. Learn it once, up front.

## Frameworks Introduced
- **MSBuild**: XML-based build engine shared with .NET Framework (replaced `project.json` in .NET Core 2.0).
  - When to use: any time you build/test/publish a .NET project; edit the `.csproj` when defaults no longer fit.
  - How: `dotnet build`, `dotnet run`, `dotnet test`; hand-edit the `.csproj` XML.
- **NuGet**: the package manager for .NET; delivers `PackageReference` dependencies from HTTP feeds.
  - When to use: pulling in external/Microsoft packages, keeping the SDK small.
  - How: `<PackageReference Include="..." Version="..."/>`; default feed `https://api.nuget.org/v3/index.json`; override via `NuGet.config`.
- **.NET Standard**: metapackage that defines one TFM many frameworks support.
  - When to use: **libraries** meant to run on multiple frameworks — pick the lowest compatible `netstandard` version.
  - How: `<TargetFramework>netstandard1.4</TargetFramework>` (console/web apps need `netcoreapp` for an entry point).

## Key Concepts
- **Dependency** = one of three kinds: **target framework**, **package** (NuGet, files/assemblies per framework), or **project** (`ProjectReference`). Metapackages reference many packages and may define a framework (`.NET Standard`); `Microsoft.AspNetCore.All` is a metapackage that does *not* define a framework.
- **Framework (target framework)** — a NuGet concept: a flavor/version of .NET, specified by its **Target Framework Moniker (TFM)** (`net45`, `netcoreapp2.0`, `netstandard1.4`). Set via the `TargetFramework` property or `-f`/`--framework`.
- **Runtime** — OS + CPU architecture (`win10-x64`, `osx.10.11-x64`, `linuxmint.17.1-x86`). Set via `RuntimeIdentifiers` property or `-r`/`--runtime`. Runtime-specific assemblies are natively compiled; the CLI checks runtime support at build.
- **Platform** — vaguest term; in this book means *operating system*. "Cross-platform" = runs on multiple OSes.
- **`using` ≠ dependency** — a `using` only imports a namespace already present in your dependencies.
- **MSBuild is case-sensitive** — camel case with capitalized first letter (`PropertyGroup`, not `propertygroup`).
- **Properties evaluate top-to-bottom** — later definitions override earlier ones; order matters (basis for `Condition` overrides).

## Mental Models
- **Target ≈ method**: a `Target` has a name and only runs when something calls it (via `AfterTargets`, or `dotnet build -t:Name`) — like a method that's dead code until invoked.
- **ItemGroup ≈ array of files**: `Compile`, `None`, `EmbeddedResource` are arrays you `Include`/`Remove` (wildcards allowed). MSBuild feeds the `Compile` ItemGroup to the compiler.
- **Restore is a negotiation**: a `PackageReference` version is a *request*, not a guarantee — restore reconciles all references to a package to one compatible version (forcing an exact version went away in .NET Core 2.0).

## Anti-patterns
- Adding `<Compile Include="**/*.cs"/>` yourself — it duplicates the default glob and **fails the build** (ItemGroups can have duplicates).
- Setting a `Message` to just a bare property value — empty/undefined properties print nothing; always add literal text so you can tell it ran.
- Relying on a data file existing next to the binary without `CopyToOutputDirectory` (or embedding) — it won't be there at runtime.
- Treating `platform`/`runtime`/`framework` as interchangeable — reserve `platform` for OS.

## Code Examples
```xml
<!-- Class library targeting .NET Standard (Listing 3.1) -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard1.4</TargetFramework>
  </PropertyGroup>
</Project>
```
```xml
<!-- Console app: remove a file, copy a data file, define a custom target -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>netcoreapp2.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <None Include="Marvel.csv">
      <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
    </None>
  </ItemGroup>
  <Target Name="TestMessage" AfterTargets="Build">
    <Message Importance="high" Text="Second Foo" />
  </Target>
</Project>
```
```bash
dotnet new console          # scaffold a console project
dotnet build -f netcoreapp2.0
dotnet build -t:TestMessage # run one target directly
dotnet run                  # build + execute
```
- **What it demonstrates**: the `PropertyGroup` (TFM + `OutputType`), an `ItemGroup` manipulating the file set, a named `Target` chained after `Build` via `AfterTargets` using the built-in `Message` task, and the core CLI verbs.

## Reference Tables

| MSBuild element | Role |
|---|---|
| `Project Sdk="Microsoft.NET.Sdk"` | Root; imports SDK defaults/conventions |
| `PropertyGroup` | Key-value properties, evaluated in order (`TargetFramework`, `OutputType`, `RuntimeIdentifiers`) |
| `Target` (`Name`, `AfterTargets`) | Named unit of work; run on chain or via `-t:` |
| `Message` (`Text`, `Importance`) | Built-in task writing to the MSBuild log |
| `ItemGroup` | Array of items (files) |
| `Compile Include/Remove` | Files sent to the compiler (default `**/*.cs`) |
| `None` + `CopyToOutputDirectory` | File the compiler ignores; copy (`PreserveNewest`) to output |
| `EmbeddedResource` | Bake file into the assembly |
| `PackageReference` (`Include`, `Version`) | NuGet dependency |
| `ProjectReference` | Another project (build order auto-resolved; detects cycles) |
| `Condition` | Guard on almost any element (e.g. `"'$(IsFx)' == 'true'"`) |

| Concept | Moniker / form | Example |
|---|---|---|
| TFM — .NET Framework 4.5 | `net45` | `net461` |
| TFM — .NET Core 1.0 | `netcoreapp1.0` | `netcoreapp2.0` |
| TFM — .NET Standard | `netstandard1.4` | libraries only |
| Runtime ID | `os-arch` | `win10-x64`, `osx.10.11-x64` |

## Worked Example — CSV parser build, end to end
1. **Scaffold**: `mkdir CsvParser && cd CsvParser && dotnet new console`.
2. **Add code**: create `CsvReader.cs` (reads a `TextReader`, first line = headers, yields `KeyValuePair<string,string>[]` per row); edit `Program.cs` to feed a verbatim CSV string via `StringReader` and print titles with a LINQ `First(p => p.Key == "Title")`. `dotnet run` prints the film titles — **no `.csproj` change needed** (no external deps, all defaults).
3. **PropertyGroup / Target experiment**: add a custom `Target` with `AfterTargets="Build"` and `Message` tasks; `dotnet build` prints them, or run just it with `dotnet build -t:TestMessage`.
4. **ItemGroup — remove a file**: `<Compile Remove="Program.cs" />` → build fails `CS5001: ... no static 'Main'`, proving `Compile` drives the compiler input.
5. **Externalize data**: move the CSV into `Marvel.csv`; change `Program.cs` to `new StreamReader(new FileStream("Marvel.csv", FileMode.Open))`. Add `<None Include="Marvel.csv"><CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory></None>` so the file lands in `bin/Debug/netcoreapp2.0`.
6. **Or embed it**: swap to `<EmbeddedResource Include="Marvel.csv" />`; read via `typeof(Program).GetTypeInfo().Assembly.GetManifestResourceStream("CsvParser.Marvel.csv")` (needs `using System.Reflection` — in .NET Core reflection moved to `TypeInfo`, no `Type.Assembly`). No external file ships.
7. **Add a dependency**: `<PackageReference Include="xUnit" Version="2.1.0" />` — restore may resolve a different compatible version.
8. **Multi-target with a condition**:
```xml
<PropertyGroup>
  <TargetFramework>netcoreapp2.0</TargetFramework>   <!-- default -->
</PropertyGroup>
<PropertyGroup Condition="'$(IsFx)' == 'true'">
  <TargetFramework>net461</TargetFramework>          <!-- overrides, needs .NET 4.6.1 installed -->
</PropertyGroup>
```
Build the Framework flavor (Windows) — apply the property to **both** steps: `dotnet restore -p:IsFx=true` then `dotnet build -p:IsFx=true` (comma-separate or repeat `-p` for multiple props).

## Key Takeaways
- Three MSBuild constructs cover most needs: `PropertyGroup` (settings), `Target` (work), `ItemGroup` (files).
- Properties are ordered and overridable — combine with `Condition` for multi-targeting without duplicating code.
- Use the `Message` target at `Importance="high"` for build-file debugging; run any target with `-t:`.
- Prefer `netstandard` (lowest compatible) for libraries; `netcoreapp` for executables.
- `CopyToOutputDirectory` ships a companion file; `EmbeddedResource` hides it inside the assembly (best when users might forget to copy it and contents are static).
- CLI-supplied properties (`-p:Name=value`) must be passed to restore *and* build when they affect dependencies.

## Connects To
- **Ch 2**: reuses the projects created there and the `dotnet new`/`run` flow; this chapter opens up the `.csproj` those commands generated.
- **Ch 11**: targeting multiple frameworks (TFMs, conditions, `net461` vs `netcoreapp`) in depth.
- **Ch 12**: NuGet in depth — custom feeds (`NuGet.config`), package versioning, and packaging your own libraries.
