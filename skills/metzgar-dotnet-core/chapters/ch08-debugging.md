# Chapter 8: Debugging

## Core Idea
.NET Core debugging spans two tiers: **graphical IDE debuggers** (Visual Studio Code, Visual Studio 2017, Visual Studio for Mac) that feel familiar and work cross-platform, and **command-line debuggers** (WinDBG/CDB, LLDB) armed with the **SOS** ("Son of Strike") extension for inspecting managed memory the GUIs can't reach. The IDE handles day-to-day breakpoint work; SOS shines when you need the whole managed heap — especially against a production memory dump over SSH.

## Frameworks Introduced
- **IDE debuggers (VS Code / VS 2017 / VS for Mac)**: launch tests, set breakpoints, break on exceptions, inspect locals and call stacks. Cross-platform via VS Code; richest exception granularity in VS 2017 (break on a specific exception type before the catch).
  - *When to use*: normal iterative debugging where you have source and a project open.
  - *How*: VS Code needs `launch.json` + `tasks.json` in `.vscode/`; VS 2017 needs a **solution** (a folder alone won't discover tests); VS for Mac uses an **Exception Catchpoint**.
- **SOS (Son of Strike) low-level debugging**: an extension hosted inside a command-line debugger that decodes .NET's managed types, functions, heap, and exceptions.
  - *When to use*: inspecting objects **off** the current thread, dumping the entire heap, analyzing a production memory dump, or debugging over a terminal/SSH.
  - *How*: on Windows load into **WinDBG/CDB** (`.loadby sos coreclr`); on Linux/macOS load into **LLDB** (`plugin load .../libsosplugin.so`). Easiest starting point is a **self-contained app** (avoids the child-process maze of `dotnet test`/`dotnet run`).

## Key Concepts
- **launch.json flags**: `justMyCode:false` steps into other teams' libraries; `requireExactSource:false` lets the debugger best-guess the line when your source doesn't exactly match the package; `enableStepFiltering:false` lets you step into properties. `console:"externalTerminal"` mimics VS's external command prompt.
- **tasks.json**: wraps the `dotnet` CLI. `build` task bound to Ctrl-Shift-B (same as VS 2017). `test` is not included by default — add it manually.
- **AggregateException wrapping**: if a `catch` block does work (e.g. `transaction.Rollback()`), a bare `throw;` loses the original stack trace. Wrap the original in an `AggregateException` so only the inner exceptions matter to the debugger.
- **Stop on module load**: CLR must be loaded before you can load SOS/set managed breakpoints. Use `sxe ld:ScmConsole` (CDB) to stop when the assembly loads. LLDB lacks module-load breaks — insert a `Console.ReadLine()` as the first line of `Main` and attach instead.
- **Value vs reference types in SOS output**: value types (`int`, and `struct`s like `DateTime`) show inline/pointer with VT column = 1; reference types show a pointer with VT = 0. `!do` works on reference objects, not on a value-type pointer like `PlacedDate`.
- **SOS commands differ by host**: help is `!help` in WinDBG/CDB but `soshelp` in LLDB; resume is `g` in CDB vs `process continue` in LLDB.

## Mental Models
- **GUI = comfort, CLI = reach.** IDEs hide the SDK's child-process complexity; SOS trades that comfort for total visibility into managed memory.
- **The self-contained app as a debugging fixture.** Publishing self-contained collapses many processes into one predictable executable that carries its own `coreclr.dll` — the sane entry point for SOS.
- **A memory dump is a frozen heap.** SOS's real payoff: copy a production dump to your workstation and walk every live .NET object without setting a single breakpoint.

## Anti-patterns
- Bare `throw;` in a catch block that does real work — silently discards the original stack trace.
- Opening a *folder* in VS 2017 and expecting Test Explorer to find tests (create a solution).
- Trying to drive SOS against `dotnet test`/`dotnet run` as a beginner — you fight spawned restore/build child processes; publish self-contained instead.
- Fighting SOS+LLDB on a Mac via Homebrew (requires building your own CoreCLR to get a matching `libsosplugin.dylib`) — install Xcode for LLDB instead.

## Code Examples
```jsonc
// .vscode/launch.json — configure the CoreCLR debugger
{ "version": "0.2.0", "configurations": [
  { "name": ".NET Core Launch (console)", "type": "coreclr",
    "request": "launch", "preLaunchTask": "build",
    "program": "${workspaceRoot}/bin/Debug/netcoreapp2.0/Test1.dll",
    "args": [], "cwd": "${workspaceRoot}", "console": "internalConsole",
    "stopAtEntry": false, "justMyCode": true,        // false = step into other libs
    "requireExactSource": true,                       // false = best-guess line
    "enableStepFiltering": true },                    // false = step into properties
  { "name": ".NET Core Attach", "type": "coreclr",
    "request": "attach", "processId": "${command:pickProcess}" } ] }
```

```text
# CDB + SOS session on a published self-contained app (Windows)
> "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe" ScmConsole.exe
0:000> sxe ld:ScmConsole            # stop when ScmConsole assembly loads (CLR now present)
0:000> g                            # run until that load
0:000> .loadby sos coreclr          # load SOS relative to coreclr.dll
0:000> !soe -create System.AggregateException   # StopOnException for the type
0:000> g                            # resume; step past access violations until CLR exception
0:000> !pe                          # PrintException on current thread's exception
0:000> !PrintException 00000151b0e51a38   # follow the InnerException pointer it prints
0:000> !clrstack -a                 # managed stack + locals on current thread
0:000> !do 0x00000151b0e35818       # DumpObject: fields of the Order object
0:000> !da <ptr>                    # dump an array (e.g. Main's args)
0:000> !dumpheap -stat              # every live .NET object grouped by type, by size
0:000> !dumpheap -type Exception    # find exceptions (always includes OutOfMemoryException)
```

```text
# LLDB + SOS session on Linux (attach to a paused self-contained app)
$ ps -eclx | grep 'ScmConsole' | awk '{print $2}' | head -1   # get PID
$ ./lldb
(lldb) process attach -p <processid>
(lldb) plugin load /usr/.../libsosplugin.so     # match your .NET SDK version
(lldb) !soe -create System.AggregateException
(lldb) process continue                          # LLDB's resume (not 'g')
(lldb) !pe
(lldb) !dumpheap -type OutOfMemory
```
- **What it demonstrates**: `launch.json` tunes IDE stepping; the CLI sessions show the fixed SOS ritual — *stop on module load → load SOS → break on exception → inspect exception/stack/object/heap* — and how the host debugger (CDB vs LLDB) changes the surrounding commands while the `!` SOS commands stay the same.

## Reference Tables

**Debugger by platform**
| Debugger | Platform | Kind | Notes |
|---|---|---|---|
| Visual Studio Code | cross-platform | GUI | C# extension; `launch.json`+`tasks.json`; break on all exceptions |
| Visual Studio 2017 | Windows | GUI | Break on specific exception before catch; IntelliTrace (Enterprise only); needs a solution to find tests |
| Visual Studio for Mac | macOS | GUI | Exception Catchpoint (= conditional breakpoints); rebranded Xamarin Studio |
| WinDBG + CDB | Windows | CLI | Same engine; WinDBG GUI, CDB command-line; from Debugging Tools for Windows (Windows SDK) |
| LLDB | Linux + macOS | CLI | Part of LLVM; Linux `apt install lldb-3.5`; Mac via Xcode; SOS+LLDB hard on Mac |

**Common SOS commands**
| Command | Host note | Inspects |
|---|---|---|
| `.loadby sos coreclr` / `plugin load libsosplugin.so` | CDB / LLDB | loads SOS itself |
| `!soe -create <Type>` | both | StopOnException: break when type is thrown |
| `!pe` (PrintException) | both | current thread's exception + inner-exception command |
| `!PrintException <addr>` | both | a specific exception object (e.g. the inner one) |
| `!clrstack -a` | both | managed call stack with locals on current thread |
| `!do <ptr>` (DumpObject) | both | a reference object's fields/types |
| `!da <ptr>` | both | contents of an array |
| `!dumpheap -stat` | both | every live object grouped by type, ordered by size |
| `!dumpheap -type <name>` | both | all objects of a type (e.g. `Exception`) |
| `!help <cmd>` / `soshelp` | WinDBG / LLDB | SOS command help |

## Worked Example
Reconstructing the chapter's `CreateOrder` bug end-to-end:

1. **VS Code first.** Open the `DapperDi` folder (`code .`), accept "add required assets" (creates `.vscode/launch.json` + `tasks.json`). Modify `Test1` to build an `Order` missing its `Part` (`//Part = part,`), optionally switch `config.json` to the in-memory database. Click the **Debug Test** codelens above the method.
2. **Break on the exception.** The debugger stops on a `NullReferenceException`, but the stack points at `throw;` — the original trace was lost because the `catch` called `transaction.Rollback()`. Fix by rewrapping the original exception in an `AggregateException`; re-debug and the wrapped exception now surfaces the real inner cause.
3. **Drop to SOS for the heap view.** Publish a **self-contained** app to avoid child processes: set `SqliteDal` to `netstandard2.0`, bump `System.Data.SqlClient` to `4.3.1`, write `ScmConsole/Program.cs` to build the same faulty `Order`, then `dotnet publish -c Debug -r win10-x64`. Run under CDB: `sxe ld:ScmConsole` → `g` → `.loadby sos coreclr` → `!soe -create System.AggregateException` → `g` (resume past two access violations to the CLR exception).
4. **Inspect managed state.** `!pe` prints the `AggregateException` and hands you `!PrintException <inner>` for the `NullReferenceException`, whose stack points at `SqliteScmContext.CreateOrder(...)+0x19f`. `!clrstack -a` shows locals; `!do <orderPtr>` dumps the `Order` — `<Part>k__BackingField` is `0000000000000000` (null), the root cause. `!dumpheap -stat` then reveals every object in memory, including SQLite/DI/CoreCLR internals and the always-present `OutOfMemoryException`. On Linux the same flow runs under LLDB after `plugin load libsosplugin.so`, swapping `g` for `process continue`.

## Key Takeaways
- Most .NET Core debugging tools are free, powerful, and cross-platform; the VS family behaves similarly on Windows/Mac/Linux.
- SOS is the command-line superpower — the only tool that gives you the whole managed heap, ideal for production dumps analyzed offline.
- Wrap exceptions in `AggregateException` when a catch block does work that would otherwise destroy the stack trace.
- Prefer a self-contained app for SOS to sidestep `dotnet test`/`dotnet run` child processes.
- Remember host differences: `.loadby sos coreclr`/`g`/`!help` (CDB) vs `plugin load`/`process continue`/`soshelp` (LLDB); the `!` SOS commands themselves are shared.
- Further tooling: CLRMD (debug via .NET code), SOSEX and MEX (richer WinDBG command libraries), Tess Ferrandez's blog.

## Connects To
- **Ch 2**: VS Code and the **self-contained publish** (`dotnet publish -r <rid>`) introduced there are the foundation for both IDE debugging assets and the single-process fixture SOS needs.
- **Ch 9**: once functional bugs are debugged, **profiling and performance analysis** are the next diagnostic step for issues that aren't crashes but slowdowns.
