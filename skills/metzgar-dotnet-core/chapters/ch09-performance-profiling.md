# Chapter 9: Performance and profiling

## Core Idea
"Premature optimization is the root of all evil" (Hoare) is about optimizing the *wrong* things — not about ignoring performance. Good performance is *planned and measured*, never assumed. The chapter's discipline: **measure before optimizing**, then use a profiler to locate the *actual* hot path before touching code. In .NET Core there is no "go faster" button; developers must set performance targets and verify them empirically. Profiling should run in a **representative config** (Release, real data volumes, quiet machine) because external factors — the garbage collector, disk speed, other processes — distort measurements.

## Frameworks Introduced
- **xUnit.Performance (microbenchmarks)**: A .NET Standard library giving performance tests a TDD-style feedback loop, analogous to xUnit for unit tests. Mark methods `[Benchmark]`, iterate over `Benchmark.Iterations`, wrap the measured region in `iteration.StartMeasurement()`. Runs many iterations and reports AVERAGE/STDEV/MIN/MAX to console + CSV/Markdown/XML.
  - *When to use*: regression-tracking a small unit of code's speed; comparing two implementations. *How*: you write your own harness (`XunitPerformanceHarness`) and run `dotnet run --perf:collect stopwatch`.
- **PerfView (CPU/GC/exception profiling)**: Free Windows tool (Vance Morrison) that records **ETW** (Event Tracing for Windows) events machine-wide. Single exe, no install, run as administrator.
  - *When to use*: to answer *why* code is slow — find CPU hot paths, GC pressure, exceptions being thrown. *How*: Collect > Run to launch the app; open **CPU Stacks**, **GCStats**, or **Events/Exception Stacks** views.
- **perfcollect on Linux**: A shell script that captures **Linux Perf Events** (the ETW analog) into a `.trace.zip` viewable in PerfView on Windows. EventPipe / `COMPlus_PerfMapEnabled` emits managed symbol maps so stacks resolve.
  - *When to use*: profiling a .NET Core app running on Linux. *How*: install script, set env var, `sudo ./perfcollect collect mytrace`, Ctrl-C to stop, copy zip to Windows.

## Key Concepts
- **Stack / frame**: chain of method calls (`Main → WriteLog → ToString`, top = innermost). Each frame identified by assembly + class + method. Line numbers usually absent in CPU profiles.
- **Symbols (.pdb)**: map frames to filename + line number. .NET assemblies show class/method names *without* symbols; natively compiled frames *need* symbols. Missing symbols show as `?`. Note: .NET Core symbols aren't published to the public Microsoft symbol server.
- **Inclusive vs. exclusive cost**: *exclusive* = time in a method's own instructions (summed across calls). *inclusive* = exclusive + all callees. If A calls B(5%) and C(6%), A's inclusive = 12%, exclusive = 1%. Costs shown as % of total CPU.
- **Sampling**: CPU Stacks % = samples in a stack ÷ samples included by filters (not % of whole profile). Default sample interval = 1 ms, adjustable.
- **GC generations (0/1/2)**: new objects start gen 0; survivors get promoted. Gen 0 collections are frequent/cheap; gen 2 rare/expensive. **Induced** = manually triggered gen 2. xUnit.Performance induces a gen 2 GC before each test so one test's allocations don't skew the next.
- **Inlining**: compiler pastes a callee's body into the caller (optimization) — inlined methods (e.g. `string.Join`, `TextWriter.WriteLine`) disappear from the stack.
- **Circular profiling**: cap profile size (e.g. 500 MB, keep latest) so long repros don't produce giant files.
- **StopWatch** (`System.Diagnostics`): cross-platform timing. On non-Windows, `--perf:collect stopwatch` gives *only* timings; Windows adds ETW kernel events + CPU counters (branch mispredicts, L2 hits).

## Mental Models
- **Profile is a window, not a verdict**: it reveals what the app *actually* does (child processes, hidden exceptions, GC pauses) that you didn't know about.
- **Cancel out the noise to compare**: two file-writing tests spent equal *total* CPU but differed in `SimpleWriter` time; by folding/grouping away file-manipulation frames you compare the two `WriteLine` implementations directly — the difference shows up in **exclusive %**.
- **Optimize the biggest slice**: file I/O had less impact than expected; the CSV-formatting code used the bigger % of time, so that's where optimization pays off.

## Anti-patterns
- Putting `StopWatch` timers inside a unit test — little info, inconsistent results.
- Ignoring benchmark memory allocation — test code's GC pauses threads and corrupts product-code measurements.
- Starting `InnerIterationCount` high — a slow disk makes the run take forever; start low, raise until results stabilize.
- Reading a single MAX spike as a regression — the 13.312 ms MAX was just the GC firing on the last-run test. Randomize order or add iterations to absorb GC.
- Profiling machine-wide and grabbing the wrong PID — `dotnet run` spawns several child processes; use the CommandLine column (find `dotnet exec ...CsvWriterPerfTests.dll`).
- Exceptions in performance-critical paths — throwing/catching is expensive; keep exceptions for exceptional cases.

## Code Examples
```csharp
using Microsoft.Xunit.Performance;

public class PerfTests {
    [Benchmark(InnerIterationCount=10000)]
    public void BenchmarkSimpleWriter() {
        var buffer = new byte[500000];
        var memoryStream = new MemoryStream(buffer);      // static buffer up front
        var values = new Dictionary<string, string> {      // prep dict up front
            ["Year"]="2008", ["Title"]="Iron Man",
            ["Production Studio"]="Marvel Studios"
        };
        foreach (var iteration in Benchmark.Iterations) {
            using (var streamWriter = new StreamWriter(
                       memoryStream, Encoding.Default, 512, true)) {  // created OUTSIDE measurement
                using (iteration.StartMeasurement()) {               // <-- only this is timed
                    var simpleWriter = new SimpleWriter(streamWriter);
                    simpleWriter.WriteHeader("Year","Title","Production Studio");
                    for (int i = 0; i < Benchmark.InnerIterationCount; i++)
                        simpleWriter.WriteLine(values);
                    streamWriter.Flush();
                }
            }
            memoryStream.Seek(0, SeekOrigin.Begin);   // rewind before next iteration
        }
    }
}
```
- **What it demonstrates**: The `[Benchmark]` + `Benchmark.Iterations` + `iteration.StartMeasurement()` shape. Allocations and stream creation happen *outside* the `using(StartMeasurement())` so only the target code is measured; `InnerIterationCount` amplifies a fast operation into a measurable duration.

Minimal harness (Program.cs) — required because xUnit.Performance ships no runner entry point:
```csharp
using (var harness = new XunitPerformanceHarness(args)) {
    var entryAssemblyPath = Assembly.GetEntryAssembly().Location;
    harness.RunBenchmarks(entryAssemblyPath);   // searches current assembly for [Benchmark]
}
```

## Reference Tables

**What each tool answers**
| Tool | Answers | Invoke |
|------|---------|--------|
| xUnit.Performance | Regression-track a microbenchmark's speed; compare implementations (AVERAGE/STDEV/MIN/MAX) | `dotnet run --perf:collect stopwatch` |
| PerfView | CPU hot paths, GC pressure/allocations, exception counts+stacks | Collect > Run (Windows, as admin) |
| perfcollect | Capture profile on Linux, analyze later in PerfView | `sudo ./perfcollect collect mytrace` |

**Which PerfView view for what**
| Goal | View (tree location) |
|------|----------------------|
| CPU hot path | **CPU Stacks** (then CallTree tab) |
| GC pressure / allocations | **GCStats** (Memory Group); optional allocation sampling |
| Exceptions thrown | **Events** (filter to exception events) |
| Exception call stacks | **Exception Stacks** (Advanced Group) |

**CPU Stacks filters** (condense noisy stacks)
| Filter | Purpose | Example |
|--------|---------|---------|
| group | collapse assemblies you don't care about | `xunit%->xunit;clr%=>coreclr` (`->` hides internals, `=>` keeps entry point only) |
| fold | remove frames entirely | `^Thread`, `system.private.corelib%;system.runtime.extensions%` |
| inclusive | restrict to a process/method | `csvwriterperftests!...BenchmarkSimpleWriterToFile` |
| — | resolve names | right-click > **Lookup Warm Symbols** |

**GCStats summary fields to watch**: Total GC CPU Time, Total Allocs (MB), % Time paused for GC, Max GC Heap Size, Induced count (per-generation rollup: Count / Max Pause / Total Alloc MB / Mean Pause).

## Worked Example
1. **Build the code**: `CsvWriter` library with `SimpleWriter` (dictionary-based `WriteLine`), an xUnit project asserting output matches `Marvel.csv`.
2. **Benchmark it**: create `CsvWriterPerfTests` console app, add `xunit.performance.api` (beta — needs a `nuget.config` pointing at the dotnet-core myget feed), write the harness + `BenchmarkSimpleWriter`. Run `dotnet run --perf:collect stopwatch` → ~2.229 ms for 10k lines (memory).
3. **Vary the config**: add `BenchmarkSimpleWriterToFile` → ~3.78 ms. File I/O costs *some* time but not dominant; re-running with files pre-created shrinks the gap further. Conclusion: the CSV-formatting code, not file I/O, is the biggest slice.
4. **Try an optimization**: add `WriteLine(params string[])` using `string.Join(",", values)` (no dictionary, no manual loop). New benchmarks (`...Join`) drop memory from ~2.5 ms to ~1.26 ms. Big win — but *which* change (dropping the dict vs. `string.Join`) caused it?
5. **Profile to find out**: launch tests under PerfView (set symbol path to the `.pdb`s + Microsoft Symbol Server, Collect > Run). Open **CPU Stacks**, pick the `dotnet exec ...CsvWriterPerfTests.dll` process (via CommandLine column). Clear the default group pattern, apply `xunit%->xunit;clr%=>coreclr`, fold `^Thread` and corelib, set inclusive to the file benchmarks, Lookup Warm Symbols. The two file tests show equal inclusive CPU but different `SimpleWriter` time — the difference is in **exclusive %**. `string.Join`/`WriteLine` may be inlined/symbol-less so they vanish from the stack.
6. **Check GC**: open **GCStats**, find the matching PID. Table shows 134 collections, mostly gen 0, four *induced* gen 2 (one before each test). Summary: Total CPU 1,905 ms, GC CPU only 47 ms (~2.5%), max heap 6 MB → GC is not the bottleneck here.
7. **On Linux**: `curl -OL http://aka.ms/perfcollect && chmod +x perfcollect && sudo ./perfcollect install`; in the app terminal `export COMPlus_PerfMapEnabled=1`; in a second terminal `sudo ./perfcollect collect mytrace`, Ctrl-C to stop (add `Console.ReadKey()` before the benchmark so you can time the manual start). Copy `mytrace.trace.zip` to Windows, open in PerfView.

## Key Takeaways
- **Measure first**: benchmarks reveal where time actually goes; optimizing the biggest % of total time is what pays off.
- Keep allocations/setup **outside** `StartMeasurement()`; the GC pauses all threads regardless of where they are.
- External factors (GC, disk, other processes) cause fluctuation — run repeatedly, add iterations, quiet the machine, don't over-read a single MAX.
- PerfView answers *why*: CPU Stacks (hot paths, inclusive vs. exclusive), GCStats (allocation/pause pressure), Events/Exception Stacks (hidden exceptions).
- **Profiling on Linux differs from Windows**: no Run option and only Perf Events (no full ETW/CPU counters); collect with perfcollect + EventPipe/`COMPlus_PerfMapEnabled`, then view in PerfView on Windows.
- `--perf:collect stopwatch` is the cross-platform lowest common denominator; richer ETW data is Windows-only.

## Connects To
- **Ch 4**: reuses the xUnit test infrastructure (`[Fact]`, `dotnet new xunit`, embedded-resource assertions) — xUnit.Performance is the perf-testing sibling that layers `[Benchmark]` on the same mental model; a functionally-correct unit test is the precondition for a meaningful benchmark.
- **Ch 1**: performance and cross-platform reach are core .NET Core selling points — this chapter shows the measurement discipline (and Linux profiling story) that makes those claims verifiable rather than aspirational.
- **Ch 3**: the CSV *parser* built earlier; here you build and profile the complementary CSV *writer*.
- **Ch 7 / Ch 8**: `curl` (ch 7) to fetch perfcollect; self-contained apps (ch 8) give the process a real name in PerfView instead of `dotnet`.
- **Ch 10**: emitting your own ETW events builds on the ETW foundation PerfView consumes here.
