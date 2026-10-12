# Chapter 2: Building your first .NET Core applications

## Core Idea
Install the .NET Core SDK once and use the cross-platform .NET CLI (`dotnet`) to scaffold, build, run, publish, and package both console and ASP.NET Core apps — the same commands and containers working identically across Windows, Linux, macOS, and Docker.

## Frameworks Introduced
- **.NET Core SDK + .NET CLI**: the self-contained toolchain (`dotnet` command) that is consistent on every OS and replaces the deprecated DNVM/DNU/DNX tools.
  - When to use: all development in this book; install from https://dot.net → Get Started → pick your OS.
  - How: Windows (Visual Studio 2017 Community or command line), Linux (per-distro instructions), macOS (`.pkg`, OS X 10.11+), Docker (`microsoft/dotnet` base image).
- **ASP.NET Core**: the web framework for .NET, rebuilt from the ground up for .NET Core; produces HTTP services and websites.
  - When to use: build a web service or website; deep coverage in Andrew Lock's *ASP.NET Core in Action*.
  - How: `dotnet new web` (minimal service) or `dotnet new mvc` (full website template).
- **Kestrel**: the cross-platform web server built for ASP.NET Core, shipped in the `Microsoft.AspNetCore.All` metapackage and wired up by `WebHost.CreateDefaultBuilder`.
  - When to use: automatically — it hosts every ASP.NET Core app; listens on `http://localhost:5000` by default.

## Key Concepts
- **.NET CLI**: the `dotnet` command-line interface, universal across all operating systems.
- **csproj / project file**: MSBuild-based XML file describing the project; by default includes *all* source files under the project folder (no explicit file listing).
- **Package restore**: `dotnet restore` expands the full dependency tree and downloads missing packages into the local cache; implicit since .NET Core 2.0.
- **NuGet**: the package store from which the CLI downloads dependencies (e.g. Kestrel) and stores them centrally.
- **Metapackage**: a package that references many other packages (e.g. `Microsoft.AspNetCore.All`).
- **Startup class**: the ASP.NET class whose `Configure` method defines how requests are handled — "starts the web application" (vs. `Program` which starts the web server).
- **Framework-dependent deployment**: publish only your binaries + packages; target machine must have the .NET Core SDK installed.
- **Self-contained application**: publish that bundles all .NET Core assemblies so it runs on a machine without the SDK; requires `RuntimeIdentifiers` in the csproj.
- **xcopy-deployable**: .NET Core is designed to deploy by simply copying the publish folder's files to the target.

## Mental Models
- **Think of `Program` vs `Startup` as**: `Program` starts the *web server* (Kestrel); `Startup` starts the *web application* (request handling).
- **Use `dotnet new console` when** you want a Hello World / quick reference; use `dotnet new web` for a barebones HTTP service; use `dotnet new mvc` when you want a full website (closer to VS "New Project").
- **Use framework-dependent deployment when** the target has the SDK; use self-contained (with a runtime identifier) when it doesn't.
- **Think of the container as one artifact** usable across dev, test, and production — killing the "it works on my machine" friction.

## Anti-patterns
- **Listing every source file explicitly in the csproj**: unnecessary in .NET Core — the project folder convention includes everything automatically.
- **Relying on Windows-specific resources**: .NET Core is self-contained and doesn't depend on the Windows-only .NET Framework, so don't assume it.
- **Using DNVM/DNU/DNX**: deprecated; use the .NET CLI instead.
- **Forgetting `UseUrls` before containerizing a web app**: default `localhost:5000` can't be reached from outside the container — you must bind `http://*:5000/` and `EXPOSE` the port.

## Code Examples
```csharp
// Listing 2.1 — Program.cs, Hello World console app (dotnet new console)
using System;
namespace hwapp {
    public class Program {
        public static void Main(string[] args) {
            Console.WriteLine("Hello World");
        }
    }
}
```
```xml
<!-- Listing 2.2 — hwapp.csproj -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>netcoreapp2.0</TargetFramework>
  </PropertyGroup>
</Project>
```
```csharp
// Program.cs for the web app — starts Kestrel, references Startup
public static IWebHost BuildWebHost(string[] args) =>
    WebHost.CreateDefaultBuilder(args)
        .UseStartup<Startup>()
        .Build();
```
```csharp
// Listing 2.5 — trimmed Startup.cs
public class Startup {
    public void Configure(IApplicationBuilder app, IHostingEnvironment env,
                          ILoggerFactory loggerFactory) {
        loggerFactory.AddConsole();
        if (env.IsDevelopment())
            app.UseDeveloperExceptionPage();
        app.Run(async (context) =>
            await context.Response.WriteAsync("Hello World"));
    }
}
```
- **What it demonstrates**: the minimal shape of a console app, its MSBuild csproj, and how `Program` (server) + `Startup` (request pipeline via anonymous method + async/await + injected services) compose an ASP.NET Core service.

## Reference Tables

| Command | Purpose |
|---|---|
| `dotnet new console` | Scaffold Hello World console app (creates Program.cs + `<name>.csproj`) |
| `dotnet new web` | Scaffold barebones ASP.NET Core HTTP service (adds Startup.cs, wwwroot) |
| `dotnet new mvc` | Scaffold full ASP.NET Core MVC website from template |
| `dotnet restore` | Expand dependency tree, download packages to cache (implicit since 2.0) |
| `dotnet run` | Build (if needed) and run the app |
| `dotnet publish -c Release` | Consolidate binaries into publish folder (framework-dependent) |
| `dotnet publish -c Release -r <RID>` | Self-contained publish for a runtime (e.g. `linuxmint.17.1-x64`) |
| `dotnet pack -c Release` | Produce a NuGet package (`.nupkg`) for distribution |
| `dotnet <app>.dll` | Run a published framework-dependent app on the target machine |

| Docker command | Purpose |
|---|---|
| `docker run -it microsoft/dotnet:latest` | Pull/run the .NET Core base image (includes SDK) |
| `docker build -t hwapp .` | Build image from Dockerfile |
| `docker run -it hwapp` | Run the console-app container |
| `docker run -it -p 5000:5000 hwwebapp` | Run web container, mapping port 5000 |

**Dev tools**: Visual Studio 2017 (Windows, free Community; F5/Ctrl-F5, auto-restore, New Project wizard replaces `dotnet new`), Visual Studio for Mac (rebranded Xamarin Studio), Rider, and **OmniSharp** — open-source plugins bringing .NET to Atom, Sublime, Brackets, Emacs, Vim, and VS Code (the "C#" extension in VS Code).

## Worked Example
**Console → web → Docker, end to end:**
1. `mkdir hwapp && cd hwapp && dotnet new console` → creates Program.cs + hwapp.csproj. `dotnet run` prints `Hello World`.
2. New folder `hwwebapp`; `dotnet new web` → csproj references `Microsoft.AspNetCore.All`, plus Program.cs (Kestrel via `CreateDefaultBuilder().UseStartup<Startup>()`) and Startup.cs (`Configure` responds `Hello World` to every request). `dotnet run` → Kestrel listens on `http://localhost:5000`; browse to confirm.
3. Publish the console app: `dotnet publish -c Release` yields four files (`hwapp.deps.json`, `hwapp.dll`, `hwapp.pdb`, `hwapp.runtimeconfig.json`). Copy to any machine with the SDK and run `dotnet hwapp.dll`.
4. Containerize the console app with a **Dockerfile**:
   ```dockerfile
   FROM microsoft/dotnet:latest
   COPY bin/Release/netcoreapp2.0/publish/ /root/
   ENTRYPOINT dotnet /root/hwapp.dll
   ```
   `docker build -t hwapp .` then `docker run -it hwapp` → prints `Hello World`.
5. Containerize the web app: add `.UseUrls("http://*:5000/")` to Program.cs, add `EXPOSE 5000/tcp` to the Dockerfile (ENTRYPOINT `hwwebapp.dll`), then `dotnet publish -c Release && docker build -t hwwebapp . && docker run -it -p 5000:5000 hwwebapp`. Test at `http://localhost:5000`.

## Key Takeaways
1. One SDK, one CLI — `dotnet` behaves identically on every OS, so build/test/prod stay consistent.
2. Learn the five verbs you'll reuse all book: `restore`, `new`, `run`, `publish`, `pack`.
3. .NET Core csproj is lean MSBuild XML — no need to enumerate source files.
4. `Program` boots Kestrel; `Startup.Configure` defines the request pipeline.
5. Deploy by copying the publish folder; choose framework-dependent (SDK required on target) vs. self-contained (bundle runtimes via `RuntimeIdentifiers` + `-r <RID>`).
6. For containers, publish then `COPY` into `microsoft/dotnet:latest`; remember `UseUrls` + `EXPOSE` for web apps.
7. Any text editor works — VS 2017, VS for Mac, Rider, or OmniSharp-powered editors like VS Code.

## Connects To
- **Ch 1**: makes concrete the cross-platform, self-contained, container-friendly .NET Core introduced conceptually in chapter 1.
- **Ch 3**: dives into the project (csproj) files and MSBuild build system used here to build more substantial applications.
- **Ch 7**: builds on the ASP.NET Core + Kestrel + Startup foundation to create a real microservice.
