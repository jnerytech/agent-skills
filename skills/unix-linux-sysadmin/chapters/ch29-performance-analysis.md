# Chapter 29: Performance Analysis

## Core Idea
Performance is governed by how four resources are shared: **CPU, memory, storage I/O, network I/O**. A process that can't get the resource it needs *waits* — and wait time is the basic measure of degradation. Counterintuitively, **CPU is usually the least important bottleneck**; disk/memory dominate. Diagnose with the scientific method (not anecdote), measure over time (especially peak load), and remember: some situations are fundamentally under-resourced — you can't tune your way out.

## Frameworks Introduced
- **The four resources** (only these much affect performance): CPU utilization (incl. stolen cycles), memory, storage I/O, network I/O. If resources remain after active processes take what they want, performance is as good as it can be.
- **Ways to improve performance** (rough order of effectiveness): add memory → switch to SSDs → load-balance across servers → tune app/system config → fix usage problems (too many services, bad scheduling) → balance I/O across disks → fix network saturation → recognize fundamental inadequacy (un-tunable).
- **Scientific method for performance problems** (5 steps): formulate a specific question → gather & classify evidence (docs + your own telemetry) → critically appraise data → summarize narratively *and graphically* (charts make equivocal numbers decisive) → state a graded conclusion.
- **Transient-slowdown triage**: `ps auxww`/`top` for a runaway (>50% CPU = suspect) → load average (`uptime`) → paging (`vmstat`) → disk monopolizer → network/server (NFS/DNS) delays.

## Key Concepts
- **Disk is the common bottleneck**: mechanical seeks take milliseconds (millions of CPU instructions stalled); ~100–300 seeks/sec vs hundreds of MB/s sequential. **Seek cost dominates** — rotation/bus speed matter little. SSDs sidestep this (no platter/head movement).
- **Memory ↔ disk coupling**: when RAM is scarce, pages get written to disk (**paging**), making memory access as expensive as disk. Adequate physical RAM is the fix — constant page-outs ⇒ buy more RAM.
- **Stolen CPU cycles** (`st` in top/vmstat/mpstat): on a VM, the hypervisor diverts CPU away — either you hit your quota, or the host is oversubscribed (sometimes fixed by restarting the instance onto new hardware). High `st` = throughput silently starved.
- **CPU split rule of thumb**: a general-purpose server should spend ~50% non-idle time in user, ~50% in system, with nonzero idle. Dedicated CPU-intensive app → mostly user time.
- **Load average** (`uptime`, 1/5/15 min): average number of runnable processes — a great baseline metric. Normal load on a bad day ⇒ look elsewhere (network); above-norm ⇒ look at local processes.
- **Linux I/O scheduler**: CFQ (default, mechanical disks), Deadline (minimize latency), **NOOP** (FIFO — best for SSDs and smart SAN controllers, since SSDs have no seek latency). Set via `/sys/block/<disk>/queue/scheduler` (not persistent) or `elevator=` kernel arg.

## Mental Models
- **Don't trust anecdotal problem reports.** Note them, but investigate yourself — rigorous, transparent method gives credible, reproducible conclusions and makes your fixes stick.
- **Measure a cross-section over time, at peak load.** A single snapshot lies; resource limits and misconfigurations surface only under heavy load, often visible only after a month of collection.
- **CPU is rarely the limit; a faster CPU rarely helps overall throughput.** If the system spends *any* time idle on average, there are cycles to spare — upgrading CPU speeds individual ops but not total throughput.
- **Found the greedy process? Usually do nothing.** Heavy operations legitimately need resources. `renice` helps CPU-bound hogs; `ionice -c 3 -p pid` (idle class) helps disk hogs; for memory hogs, ask the owner to run later (kill only in emergencies).
- **A slow remote server poisons its clients.** A DNS glitch making `gethostent` take 2s, a dead NFS/Kerberos server — ripples back as mysterious local slowness. DNS forward/reverse misconfiguration causes "a surprising number" of performance issues.

## Anti-patterns
- **Tuning your way out of a fundamentally inadequate system**: recognize when demand simply exceeds capacity — no config change saves you.
- **Killing a legitimate resource hog reflexively**: heavy work isn't illegitimate; prefer renice/ionice/ulimit or asking the owner to reschedule.
- **Ignoring `st` (stolen) on VMs**: your workload is starved even though it looks under quota.
- **Refreshing `top` too rapidly**: `top` itself becomes a CPU hog.
- **Constant paging tolerated long-term**: occasional paging is fine and inevitable; a steady page-out stream means buy RAM (don't just bump `swappiness`).
- **All filesystems used together on one disk**: split them (and swap) across disks to parallelize I/O (e.g. web data vs web logs vs DB logs).

## Code Examples
```sh
# Hardware inventory (set realistic expectations)
cat /proc/cpuinfo            # CPU type/cores; /proc/meminfo, /proc/diskstats
sudo dmidecode -t 4          # processor info (also -t 17 memory)

# CPU + memory: vmstat (interval, count) — first line is since-boot
vmstat 5 5                   # us/sy/id/wa CPU; si/so paging; cs context switches
mpstat -P ALL                # per-CPU breakdown (multiprocessor)
uptime                       # load averages (1/5/15 min)
ps aux                       # per-process CPU; top for live view
top                          # watch the %st (stolen) field on VMs

# Memory
swapon -s                    # swap usage; VM = real RAM + swap used
# /proc/sys/vm/swappiness (default 60) — but if tempted, just add RAM

# Disk I/O
iostat 5                     # tps, kB_read/s, kB_wrtn/s per disk
lsof / fuser                 # which processes touch which files/filesystems
fio read-write.fio           # benchmark IOPS + latency (SAN, shared storage)

# Historical + profiling
sar                          # CPU since midnight (needs sa1 from cron); sar -d disk, -n DEV net
sudo perf top                # live system-wide function-level CPU profile

# Throttle hogs (instead of killing)
renice 5 <pid>               # CPU-bound
ionice -c 3 -p <pid>         # disk-bound: idle class (I/O only when nothing else wants it)
ulimit -m 32000000           # cap subsequent processes' physical memory
```

## Reference Tables
**`vmstat` columns**: `r`/`b` (runnable/blocked procs), `si`/`so` (Linux swap in/out), `bi`/`bo` (block in/out), `in`/`cs` (interrupts/context-switches — high = misbehaving device), `us`/`sy`/`id`/`wa`/`st` (CPU: user/system/idle/iowait/stolen).

**Performance tools**: `vmstat` (CPU+memory+paging), `mpstat` (per-CPU), `iostat` (disk), `sar` (historical, portable), `fio` (storage benchmark), `perf` (deep Linux profiler), `top`/`ps` (per-process). Hardware: `/proc/cpuinfo`, `dmidecode`.

**Linux I/O schedulers**: CFQ (default, mechanical, fair), Deadline (low latency), NOOP (FIFO — SSDs/smart-SAN).

## Worked Example
**"My server just got really slow" — triage.** (1) `ps auxww`/`top`: look for a runaway — any process >50% CPU is a prime suspect; if none, count processes ≥10% — more than 2-3 means the load average is high (itself a cause of slowness). (2) `uptime` for load average + `vmstat` to confirm the CPU is ever idle. (3) If no CPU contention, `vmstat` again for paging: lots of page-outs ⇒ memory contention (add RAM); heavy disk traffic *without* paging ⇒ a process monopolizing the disk. There's no direct disk-op→process map, but any disk-heavy process uses some CPU — make an educated guess and `kill -STOP <pid>` to test the theory. (4) Found the culprit? Usually do *nothing* — heavy work is often legitimate; `renice` a CPU hog or `ionice -c 3` a disk hog rather than killing it. (5) If no runaway, suspect the **network** (a cron job firing network calls fleet-wide at the same minute causes brief glitches) or a **slow remote server** (dead NFS, a DNS lookup taking 2s in `gethostent`) — these ripple back as local slowness and are easy to miss.

## Key Takeaways
1. Four resources matter — CPU, memory, storage I/O, network I/O; wait-time is the degradation metric, and CPU is usually the *least* important.
2. Disk seeks dominate mechanical-disk performance (SSDs fix it); inadequate RAM turns memory access into disk access via paging — add RAM before tuning swappiness.
3. Diagnose scientifically over time at peak load; chart the data; don't trust anecdotes.
4. On VMs, watch the stolen-cycle (`st`) metric — hypervisor contention silently starves you.
5. Use vmstat/mpstat/iostat/sar/perf to localize the bottleneck; load average is a key baseline.
6. When you find a hog, usually leave it — renice (CPU) / ionice (disk) / ulimit (memory) or reschedule, rather than kill; and check network/DNS/NFS for ripple-effect slowness.

## Connects To
- **Ch 4**: process control (nice/renice, ps/top, runaway processes, load average).
- **Ch 20**: storage (SSDs, RAID, I/O balancing, the disk bottleneck).
- **Ch 28**: monitoring (collecting performance metrics over time, baselines, Grafana).
- **Ch 9/24**: cloud/virtualization (stolen cycles, resizing instances).
- **Ch 16**: DNS (misconfiguration as a hidden performance killer).
