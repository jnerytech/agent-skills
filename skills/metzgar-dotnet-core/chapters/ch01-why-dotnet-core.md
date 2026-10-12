# Chapter 1: Why .NET Core?

## Core Idea
.NET Core is a small, modular, open-source, cross-platform reboot of .NET: the same C#/CLR heritage, but redesigned so one library can run on Windows, Linux, macOS, mobile, and containers, and so Microsoft (and the community) can innovate fast without the .NET Framework's backwards-compatibility handcuffs.

## Frameworks Introduced
- **The .NET Standard Library**: a formal contract of APIs that *every* .NET implementation (.NET Framework, .NET Core, Xamarin) implements, so a library compiled against it is binary-shareable across all of them.
  - When to use: writing a library meant to run on more than one .NET platform (backend + mobile + desktop).
  - How: target `netstandard` (not a specific runtime); as long as a new runtime supports your dependent libraries, it supports you — no rebuild/redistribute.
- **xcopy-deployable modular deployment**: an app + all its dependencies live in one folder; deploying = copying the folder.
  - When to use: containers, side-by-side versioning, any platform where you can't assume a framework is pre-installed.
  - How: `dotnet publish` gathers dependencies into the output folder.
- **CLI-first tooling**: the `dotnet` Command-Line Interface is the lowest-common-denominator surface, so examples work regardless of editor/OS.
  - When to use: Docker containers, headless Linux, editor-agnostic workflows.

## Key Concepts
- **.NET Core**: three things at once — a framework (incl. ASP.NET Core, UWP), the .NET Standard Library, and the common infrastructure.
- **CLR (Common Language Runtime)**: the managed execution engine (GC + JIT) carried over from .NET Framework and tuned further for Core.
- **ASP.NET Core**: full rewrite of ASP.NET (dropped legacy `System.Web`/classic ASP) crossing 1M+ plaintext requests/sec vs ~50K for .NET 4.6.
- **Container density**: more customers per host; smaller footprint = higher density. Containers virtualize the OS, holding only app + deps.
- **.NET Portability Analyzer**: CLI + VS plugin that reports which of your Framework APIs won't port to Core (covered in ch11).

## Mental Models
- Think of the .NET Standard Library as the **USB spec of .NET**: code to the standard once, plug into any conforming runtime.
- Backwards compatibility is a **double-edged sword** — it protects existing apps but freezes innovation; Core cuts the tie so ASP.NET Core / EF Core can move fast while `System.Collections`-tier libraries keep Framework-grade rigor.
- Prefer **containers over VMs** for cloud scaling: VMs cost GBs + minutes to start + redundant OS memory; containers cost MBs + seconds + app-only memory, and behave identically on any host.

## Anti-patterns
- **Assuming Core == Framework-on-Linux**: it's a deliberate subset. Microsoft ports on customer demand, not wholesale.
- **Porting reflection-heavy code blindly**: many `Type` operations moved to the new `TypeInfo` class in Core — expect refactoring.
- **Relying on Windows-only stacks in portable code**: WPF/XAML, AppDomains, .NET Remoting, ASMX, LINQ to SQL, WCF *services*, WF, and `System.Transactions` are not ported.

## Reference Tables
| Framework feature | Status in .NET Core | Replacement |
|---|---|---|
| WPF/XAML | Not ported (UI) | none (no cross-platform UI) |
| AppDomains | Not ported | process isolation / AssemblyLoadContext |
| .NET Remoting | Not ported | REST services |
| ASMX web services | Not ported | Web API |
| LINQ to SQL | Not ported | Entity Framework Core (ch6) |
| WCF services | Client only | ASP.NET Core Web API |
| System.Transactions (distributed) | Not ported | app-level coordination |

## Worked Example — the claims architecture
An auto-insurer wants claims adjusters to enter accident data *from the scene* (offline-capable), get instant estimates, and pull policy data. Pre-Core this meant: separate iOS + Android + desktop codebases, business logic **rewritten in each language**, split ownership between server and mobile teams, sync pain, and peak-load hardware sizing.

With .NET Core + Xamarin + the .NET Standard Library: the proprietary evidence-collection business logic becomes **one shared library** consumed by web services *and* the mobile app → consistent behavior, lower maintenance. During a natural-disaster demand spike, ASP.NET Core's throughput + container elasticity let the backend scale instead of falling over. This is the recurring payoff the book returns to: write once, run and scale everywhere.

## Key Takeaways
1. Target `netstandard` for libraries you want to share; target a specific runtime only for apps.
2. Core wins on deployment (xcopy/folder), performance (ASP.NET Core), and cloud density (containers) — the three reasons to adopt.
3. Only the Framework gets bug-fixes going forward; **new features land in Core**.
4. Before porting a Framework app, run the .NET Portability Analyzer first.
5. Reflection differs: watch for `Type` → `TypeInfo` moves.
6. If you hit a Framework bug, a Core workaround/PR is often faster than waiting on a Framework release.

## Connects To
- **Ch 2**: turns these promises into a running Hello World app + web app.
- **Ch 11**: the Portability Analyzer and multi-framework/runtime targeting in depth.
- **Ch 6**: Entity Framework Core, the replacement for LINQ to SQL.
- **.NET Standard**: appendix C enumerates what each version includes.
