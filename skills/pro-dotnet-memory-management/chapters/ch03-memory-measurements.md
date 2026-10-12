# Chapter 3: Memory Measurements

## Core Idea
Memory management is a runtime phenomenon: to understand and fix it you must **measure**, and the right tool depends on the platform (Windows vs Linux) and the tradeoff between overhead and detail. This chapter is the reference catalog of .NET memory/GC tooling plus the vocabulary (overhead, sampling vs tracing, call trees, object graphs, latency vs throughput) needed to read their output.

## Frameworks Introduced
- **Measure Early / Measure GC Early (Rule 5)**: Do not optimize prematurely; first measure whether a performance/memory need exists at all, then monitor GC continuously.
  - When to use: from the first deployment in small environments through production monitoring.
  - How: instrument performance counters (Windows) or CLI-collected counters/events (Linux); wire checks into CI/CD; at minimum, manually compare metrics after each production deploy vs the previous release. Track (1) process memory and whether it grows uncontrolled, (2) GC frequency/duration and its overhead.
  - Why it works: catches memory regressions and degradation *trends* early, before they become production incidents.
- **Sampling vs. Tracing (instrumenting)**: Two ways tools collect data.
  - Tracing (event-based): record on specific events (GC start, file open). Precise but high overhead if events are frequent — never used for method enter/return in production.
  - Sampling (time-based): snapshot state periodically (e.g., call stacks every 1 ms). Lower overhead, statistical accuracy; may miss anything faster than the sample interval.
- **Overhead vs. Invasiveness**: Overhead = how much slower/heavier the app runs (a %); low-overhead tools are production-safe. Invasiveness = how much the tool disturbs the app (restart, recompile, permissions); ideal tools toggle on/off on a live process.
- **Object graph size metrics (shallow / total / retained)**: Three distinct "sizes" — always ask which a tool reports.

## Key Concepts
- **Call tree**: Tree where each node is a function; children are the functions it called; each carries **Exclusive** (this function only) and **Inclusive** (function + all descendants) time, plus their `%` variants. Data is aggregated across all calls.
- **Object graph (reference graph)**: Graph of objects referencing each other, rooted at GC roots.
- **Shortest root path**: Shortest reference chain from an object to some root — usually the strongest/main reason an object stays reachable (but can be misleading if it's just a cache).
- **Dependency subgraph**: An object plus everything it directly/indirectly references.
- **Retained subgraph / retained size**: The objects that would be freed if the object were removed; retained size = memory reclaimable on deletion. Hardest to compute; ≤ total size.
- **Shallow size**: The object itself (its fields + reference slots). **Total size**: shallow + all objects in its dependency subgraph.
- **Latency**: time to perform one action. **Throughput**: actions per unit time. **Little's Law**: `occupancy = latency * throughput` (stable systems only).
- **ETW (Event Tracing for Windows)**: Low-overhead event pipeline: event / session / provider (GUID) / controller / consumer; buffers live in the kernel so an app crash keeps the data.
- **EventPipe**: Cross-platform diagnostic channel (Named Pipes on Windows, Unix Domain Sockets on Linux/macOS) — how .NET Core emits events and counters everywhere.
- **Percentile / Median / Histogram**: Prefer these over the **average**, which hides distribution and points to no real sample; watch for **bimodal/multimodal** distributions the average misreports.

## Mental Models
- Use **tracing** when you need exact event data and can afford the cost (dev box); use **sampling** in production or for CPU-bound "where does time go" questions.
- Think of the **average as a liar** — Anscombe's quartet: wildly different datasets share the same average/variance. Demand a histogram or percentiles.
- Think of **ETW as machine-wide, not process-wide**: a session collects from all processes implementing a provider; the *consumer* filters by process.
- Choose tools along an axis from **easy GUIs (limited)** → **CLI counters** → **PerfView** → **WinDbg (deepest, steepest)**; commercial GUIs cover "almost" everything — that "almost" is why you learn the low-level ones.

## Anti-patterns
- **Reading current performance-counter values instead of watching changes**: Counters update only at GC start/end and then stay frozen; a stale `% Time in GC` of 50% persists even while the app is idle. Focus on deltas.
- **Sampling counters too rarely**: If a full GC lands right before each sample you get a false `% Time in GC` picture.
- **`.NET Alloc` / stack-per-allocation in production**: Loads a Profiler-API dll and forces the slow allocation path — several orders of magnitude slowdown.
- **Trusting a single average / ignoring multimodal data**: Two response-time clusters (e.g., ~40 ms and ~150 ms) averaged together yield a meaningless number.
- **Forgetting PerfView's Merge before cross-machine analysis**: Without Merge (symbol prep) the collected data is useless on another box.

## Code Examples
```
[BenchmarkDotNet.Attributes.Jobs.ShortRunJob]
[MemoryDiagnoser]
public class TailCallTest
{
    [Params(5, 10, 20)]
    public int N { get; set; }

    [Benchmark]
    public long FibonacciRecursive() { return FibonacciRecursiveHelper(N); }

    private long FibonacciRecursiveHelper(long n)
    {
        if (n < 3) return 1;
        return FibonacciRecursiveHelper(n - 2) + FibonacciRecursiveHelper(n - 1);
    }
}
```
- **What it demonstrates**: BenchmarkDotNet configured via attributes; `[MemoryDiagnoser]` reports allocations + GC counts, `[Params]` sweeps inputs. Run with `BenchmarkRunner.Run<TailCallTest>()`. The library handles warmup, iteration counts, percentiles, and multimodal detection.

## Reference Tables

### Key CLI commands
| Task | Command |
|------|---------|
| Install a CLI diagnostic tool | `dotnet tool install -g dotnet-counters` (also `-trace`, `-dump`, `-gcdump`, `dotnet-gcmon`, `gummycat`) |
| List available counters | `dotnet counters list` |
| Subset of a provider's counters | `--counters System.Runtime[gc-heap-size,loh-size,gen-2-size]` |
| List .NET processes | `dotnet counters ps` |
| Collect counters to CSV/JSON | `dotnet counters collect -p <pid> -o <file> --format json` |
| Collect events (keywords:verbosity) | `dotnet trace collect --providers Microsoft-Windows-DotNETRuntime:40000001:5` |
| Trace by keyword name | `--clrevents gc+stack --clreventlevel 5` |
| Capture a full dump | `procdump -ma <pid>` or `dotnet-dump collect -p <pid> --type Full` |
| Capture a heap graph (small) | `dotnet-gcdump collect -p <pid>` |
| Analyze a dump (SOS, no `!`) | `dotnet-dump analyze <file>` |
| List .NET ETW providers | `logman query providers \| findstr DotNET` |
| Load SOS in WinDbg (modern) | auto-loaded; or `.load <...>\.dotnet\sos\sos.dll` (via `dotnet-sos install`) |

### Selected `System.Runtime` counters (.NET Core)
| Counter | Meaning |
|---------|---------|
| `gc-heap-size` | Total heap size (MB) |
| `gen-0/1/2-size`, `loh-size`, `poh-size` | Per-region heap sizes (POH = Pinned Object Heap) |
| `alloc-rate` | Bytes allocated between intervals |
| `time-in-gc` | % time in GC since last GC |
| `gc-fragmentation` | GC heap fragmentation |
| `gc-committed` | Committed memory by GC (MB) |
| `gen-0/1/2-gc-count` | GCs per generation between intervals |

### Tool summary
| Tool | Purpose | Notes |
|------|---------|-------|
| Performance Monitor (`perfmon`) | Perf-counter viewer | easy, low overhead; can mislead; Windows only |
| dotnet-counters | Counter recorder/visualizer | cross-platform, low overhead, no analysis |
| PerfView | Record + analyze ETW (GCStats view) | very powerful for .NET, low overhead possible; steep; Windows only |
| dotnet-trace | Event recorder (→ .nettrace, opened in PerfView) | cross-platform |
| dotnet-gcmon / GCRealTimeMon | Live GC detail viewer (Maoni Stephens) | cross-platform; realmon shows induced-GC stacks |
| ProcDump / dotnet-dump | Full memory dumps | cross-platform; ProcDump has triggers, dotnet-dump has SOS analysis |
| dotnet-gcdump | Heap object-graph snapshot (.gcdump) | tiny files; usable by VS/PerfView for leak analysis |
| WinDbg + SOS | Deepest managed+native debugging | very steep; Windows only |
| BenchmarkDotNet | Micro-benchmark exec time + allocations | statistical, multimodal detection |
| dnSpy / ILSpy / dotPeek / sharplab.io | Decompile IL / view JITted asm | dnSpy can edit + debug |

## Worked Example
**Diagnosing a memory leak with PerfView heap-snapshot diff.** PerfView's `Memory ➤ Take Heap Snapshot` produces a `.gcdump` — *not* a full dump; it captures the graph of allocated objects (types, counts, references, roots) with no field contents or unmanaged memory, hence tiny files. Take two snapshots over time, open both, and `Diff ➤` compare: the resulting **Diff Stacks** shows the *delta* per type between the files — the types that grew are your leak suspects. Note the **Freeze** option (off by default): freezing pauses the whole process for exact results (intrusive); leaving it off in production keeps the app running but can yield inconsistent data since the app allocates mid-snapshot. Under the hood, generating a `.gcdump` enables `Microsoft-Windows-DotNETRuntime` at verbose level with keyword mask `0x1980001`, triggering a full GC that walks live objects and emits `GCBulkNode` (instances + edge counts) paired with `GCBulkEdge` (referenced instances), plus `GCBulkRootEdge`/`GCBulkRootStaticVar` for roots — reconstructing the live object graph that tools use for leak hunting.

## Key Takeaways
1. **Measure early, then measure GC continuously** — track process memory growth and GC frequency/duration, ideally in CI/CD.
2. Always ask two questions of any tool: what's its **overhead/invasiveness**, and does it **sample or trace**?
3. When reading a "size," know whether it's **shallow, total, or retained**; retained size is what you actually reclaim.
4. **Distrust the average** — demand percentiles/histograms and watch for multimodal distributions.
5. Performance counters are **frozen between GC events** — watch changes, not the current value.
6. Match the tool to the platform: **Performance Monitor/PerfView/WinDbg** (Windows) vs **dotnet-counters/-trace/-dump/-gcdump** (cross-platform via EventPipe).
7. **PerfView** is the workhorse for .NET (low overhead, GCStats, heap diffs); **WinDbg + SOS** is the last resort for object-field-level detail.

## Connects To
- **Ch 2**: VMMap visualizes the committed/reserved page layout described there; low-level HW profilers (VTune, CodeAnalyst) reveal false sharing from Ch 2.
- **Ch 5**: Perf-counter vs ETW measurement differences; the `ReadOnlyHeapMapMessage`/`GCSegmentTypeMap` question; hidden allocations.
- **Ch 12**: "Scenario 12-2 — Memory Leak Because of Events" uses the `.gcdump` live-object graph for leak diagnosis.
- **Ch 15**: The TraceEvent library underlying PerfView's ETW analysis.
- **CLR / ETW / EventPipe**: `Microsoft-Windows-DotNETRuntime` provider (GUID `E13C0D23-...`), GC keywords, `GCStart_V2`/`GCHeapStats_V2`/`GCAllocationTick_V4` events; SOS = "Son of Strike".
