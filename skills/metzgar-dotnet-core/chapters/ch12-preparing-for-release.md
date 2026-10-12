# Chapter 12: Preparing for release

## Core Idea
Turning a library into a releasable artifact is two jobs: **packaging** it as a
**NuGet** package with correct metadata and dependencies, and **signing** its
assemblies with a **strong name** so consumers can verify *who* produced the
assembly. Strong naming establishes **identity, not tamper-proofing** — it is
not a security boundary. `dotnet pack` handles the common case; project
references, resource assemblies, and delay-signing each need extra handling on
.NET Core.

## Frameworks Introduced
- **NuGet packaging (`dotnet pack`)**: Produces a `.nupkg` (a zip) with a `lib/<tfm>/`
  folder and a generated `.nuspec`. Metadata (id, version, authors, license,
  dependencies) is driven from `.csproj` MSBuild properties.
  - *When to use*: any library you distribute internally or on nuget.org.
  - *How*: set package properties in `.csproj`, run `dotnet pack`, push to a **NuGet feed**.
- **Assembly signing / strong names**: Signs an assembly with a developer's private
  key; the **public key token** becomes part of the assembly's full name
  (`Name, Version, Culture, PublicKeyToken`), proving origin.
  - *When to use*: publishing libraries others reference and must trust the identity of.
  - *How*: generate a **signing key** (`sn.exe -k`), reference the `.snk` from `.csproj`
    (`SignAssembly` + `AssemblyOriginatorKeyFile`).

## Key Concepts
- **Project references are treated like package references by default.** `dotnet pack`
  assumes each project ships as its own package, so a referenced project (`Foo`) is
  emitted as a *dependency* in the `.nuspec`, not bundled into the package DLL.
- **`PackageId` is the dependency `id`.** The `<dependency id="...">` written into the
  `.nuspec` comes from the referenced project's `PackageId`.
- **NuGet feed = anywhere packages live.** Options range from a file-share folder
  (zero setup) to `NuGet.Server` on IIS, the NuGet Gallery source, or hosted feeds
  (MyGet, ProGet, Artifactory).
- **`nuget.config` resolution walks upward.** The nearest `nuget.config` (project dir up
  to root) is used first, then global config files. `dotnet` lists the config files used
  after a restore.
- **Symbols/source packaging.** `--include-symbols` emits `*.symbols.nupkg`;
  `--include-source` also adds a `src/` folder.
- **Resource (satellite) assemblies are not auto-packaged.** Localized
  `*.resources.dll` satellite assemblies must be added manually.
- **Delay-signing** lets developers build without holding the private key: the assembly
  is stamped with only the **public key**; real signing happens later in a controlled
  build. On Windows/.NET Framework you must skip verification for such an assembly.

## Mental Models
- **Package = zip + manifest.** Rename `.nupkg` to `.zip` to inspect `lib/` and `.nuspec`.
- **Signing key = public/private pair.** Private key signs; public key (token) verifies
  and lives in the manifest. Guard the private key like Microsoft does (few humans,
  controlled system).
- **Strong name answers "who," not "is it intact."** Authenticity of *origin*, distinct
  from encryption or malware protection.

## Anti-patterns
- Assuming `dotnet pack` bundles referenced projects — it emits them as dependencies.
- Publishing an unsigned library where identity matters — cannot be verified.
- Treating strong naming as a tamper/security guarantee — it is identity only.
- Committing the private `.snk` to every workstation instead of delay-signing.
- Expecting delay-signing or `sn.exe -Vr` verification-skip to work on .NET Core /
  non-Windows — they don't (Framework + Windows only).
- Forgetting to manually add satellite `*.resources.dll` for localized packages.

## Code Examples
```xml
<!-- Bar.csproj: package metadata + bundling project references into the package -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.0</TargetFramework>
    <!-- Package metadata surfaced on nuget.org -->
    <PackageId>Bar</PackageId>
    <Version>1.0.0</Version>
    <Authors>Bar</Authors>
    <PackageLicenseExpression>MIT</PackageLicenseExpression>
    <!-- Strong-name signing (.NET Core) -->
    <SignAssembly>true</SignAssembly>
    <AssemblyOriginatorKeyFile>mykey.snk</AssemblyOriginatorKeyFile>
    <!-- Delay-signing (.NET Framework only) -->
    <!-- <DelaySign>true</DelaySign>
         <AssemblyOriginatorKeyFile>mykey.public.snk</AssemblyOriginatorKeyFile> -->
    <!-- Workaround: copy referenced project DLLs INTO the package -->
    <TargetsForTfmSpecificBuildOutput>
      $(TargetsForTfmSpecificBuildOutput);CopyProjectReferencesToPackage
    </TargetsForTfmSpecificBuildOutput>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Foo/Foo.csproj" />
  </ItemGroup>
  <Target Name="CopyProjectReferencesToPackage"
          DependsOnTargets="ResolveProjectReferences">
    <ItemGroup>
      <BuildOutputInPackage Include="@(_ResolvedProjectReferencePaths)"/>
    </ItemGroup>
  </Target>
</Project>
```
```bash
# Build the package (rename .nupkg -> .zip to inspect lib/ and .nuspec)
dotnet pack
dotnet pack --include-symbols      # also emits Bar.1.0.0.symbols.nupkg
dotnet pack --include-source       # symbols + src/ folder

# Alternative: bundle project references via the nuget client (Framework)
nuget update -self                 # ensure NuGet 4.0+
nuget pack Bar.csproj -IncludeReferencedProjects

# Publish to a file-share NuGet feed and register it
nuget add Bar.1.0.0.nupkg -source \\myfileshare\nuget
nuget sources add -Name myfeed -Source \\myfileshare\nuget -configfile nuget.config
nuget sources list

# Generate a signing key + extract public key (Windows SDK, dev prompt)
sn.exe -k mykey.snk
sn.exe -p mykey.snk mykey.public.snk
sn.exe -Vr myassembly.dll          # skip verification for delay-signed (Win/Framework)
```
- **What it demonstrates**: metadata lives in `.csproj`; project references default to
  *dependencies* unless a custom MSBuild target copies them into `BuildOutputInPackage`;
  a file share is a zero-setup feed; strong-name vs delay-sign properties; `sn.exe` is
  Windows-only for keys and verification-skip.

## Reference Tables

### Package metadata (`.csproj` MSBuild property → `.nuspec`)
| Property | Purpose |
|---|---|
| `PackageId` | Package id (and dependency `id` when referenced) |
| `Version` | Package version; new upload required to change license |
| `Authors` / `Owners` | Displayed on nuget.org |
| `Description` | Package description |
| `PackageLicenseExpression` | License (Microsoft favors MIT) |
| `SignAssembly` + `AssemblyOriginatorKeyFile` | Strong-name signing |

### Signing options
| Option | Key used | Where it works | When to use |
|---|---|---|---|
| **Full strong-name signing** | private `.snk` | .NET Core & Framework | Official/release builds; assembly gets real signature + public key token |
| **Delay-signing** | public `.snk` only | .NET **Framework**, **Windows** only | Dev builds where the private key is withheld; stamp public key now, sign later; must `sn.exe -Vr` to skip verification |

### Packaging flags
| Flag | Effect |
|---|---|
| `--include-symbols` | Extra `*.symbols.nupkg` |
| `--include-source` | Symbols package + `src/` source |
| `-IncludeReferencedProjects` (nuget) | Bundle referenced project DLLs |
| `/p:NuspecFile=... /p:NuspecBasePath=...` | Pack from a hand-built `.nuspec` + folder |

## Worked Example
Ship `Bar` (which references `Foo`) as one signed package on a private feed.
1. **Metadata**: in `Bar.csproj` set `PackageId`, `Version`, `Authors`,
   `PackageLicenseExpression` (MIT).
2. **Bundle the project reference**: add the `CopyProjectReferencesToPackage` target so
   `Foo.dll` lands in `lib/netstandard2.0/` instead of appearing as a `<dependency>` in the
   `.nuspec` (default `dotnet pack` behavior emits `Foo` as a dependency).
3. **Resource assemblies** (if localized, e.g. ACController with `ar-SA`): extract the
   generated `.nuspec`, build a `pack/` folder containing `lib/netcoreapp2.0/*.dll` plus the
   `ar-SA/ACController.resources.dll` satellite, then
   `dotnet pack /p:NuspecFile=ACController.nuspec /p:NuspecBasePath=./pack`.
4. **Sign**: `sn.exe -k mykey.snk`; add `SignAssembly=true` +
   `AssemblyOriginatorKeyFile=mykey.snk` to the `.csproj` so the built DLL carries a strong
   name (public key token in its full name). For a Framework dev flow, delay-sign with the
   public key and `sn.exe -Vr` to skip verification.
5. **Publish**: `dotnet pack`, then `nuget add Bar.1.0.0.nupkg -source \\myfileshare\nuget`;
   register with `nuget sources add ... -configfile nuget.config`. Consumers restoring
   against `myfeed` now get the signed `Bar` with `Foo` inside.

## Key Takeaways
- Package metadata is just `.csproj` properties; nearly everything shown on nuget.org
  is set there.
- `dotnet pack` treats project references as dependencies — bundle them with a custom
  MSBuild target or `nuget pack -IncludeReferencedProjects`.
- A file share is the simplest NuGet feed; `nuget.config` is easy and belongs in source
  control.
- Satellite/resource assemblies must be packaged manually via a hand-built `.nuspec`.
- Strong names prove **identity** (origin via public key token) — not integrity/security.
- Delay-signing and `sn.exe` verification-skip are **Windows + .NET Framework only**;
  not supported on .NET Core.

## Connects To
- **Ch 3**: MSBuild `.csproj` custom `<Target>` and item groups (`BuildOutputInPackage`,
  `TargetsForTfmSpecificBuildOutput`) — packaging reuses the build-target mechanics.
- **Ch 11**: multi-target packages — `lib/<tfm>/` layout and per-TFM dependency groups in
  the `.nuspec` extend to multiple target frameworks.
- **Ch 10**: localized resources / satellite assemblies that must be manually packaged here.
- **Ch 6**: configuration options — why XDT `.config` transforms don't apply to .NET Core.
