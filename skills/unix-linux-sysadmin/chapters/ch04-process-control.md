# Chapter 4: Process Control

## Core Idea
A process is a running program — the abstraction through which memory, CPU, and I/O are managed. UNIX does as much as possible *in* processes (system and user processes obey the same rules, so one toolset controls both). Mastering process control = knowing PIDs, signals, `ps`/`top`, scheduling priority, and how to schedule recurring work.

## Frameworks Introduced
- **Process attributes the admin cares about**: PID, PPID (parent), real/effective/saved UID & GID, niceness, control terminal, and state.
- **fork/exec lifecycle**: no syscall starts a new program directly — a process `fork`s a copy of itself (returns 0 to child, child's PID to parent), then the child `exec`s a new program. On exit, the process calls `_exit`; the parent must `wait` to reap it. Orphans are re-parented to `init`/systemd (PID 1), which reaps them.
- **Signals = process-level interrupts (~30 kinds)**: used for IPC, terminal key events (Ctrl-C/Ctrl-Z), admin `kill`, kernel fault notification.
  - When to use: reload config (HUP), graceful vs forceful termination, suspend/resume.
  - How: a process catches (handler), ignores, or blocks a signal; KILL and STOP can do *none* of these.

## Key Concepts
- **PID / PPID**: unique process ID; parent's PID (trace a mystery process back to its origin).
- **effective vs real UID**: effective drives permission checks; saved UID lets a setuid program drop and re-acquire privilege.
- **Niceness**: scheduling hint, Linux −20..+19 (FreeBSD −20..+20). High nice = low priority ("nice to others"). Children inherit it; only root can *lower* niceness. Affects CPU only — not memory or I/O (use `ionice` for I/O).
- **Zombie / defunct**: finished but unreaped; check its PPID to find the negligent parent.
- **Uninterruptible sleep (`D` state)**: can't be killed or signaled; classic cause = NFS server down on a `hard`-mounted filesystem → fix the cause or reboot.
- **Load average** (`uptime`): avg runnable processes over 1/5/15 min; on Linux includes I/O wait. CPU-bound rule: load should be < number of cores.
- **`/proc`**: pseudo-filesystem exposing kernel/process state; `ps`/`top` read from it. Files appear 0-byte; `cat` them. `/proc/<pid>/` has `cmdline`, `environ`, `exe`, `fd`, `maps`, `status`.

## Mental Models
- **Signal-name decoding** (the vague names matter): `KILL`(9) = unblockable kernel-level destroy, last resort; `TERM`(15, default of `kill`) = clean-up-and-exit request; `INT`(2) = Ctrl-C, cancel current op; `HUP`(1) = "reread your config" for daemons (or terminal hangup); `QUIT`(3) = like TERM but dumps core; `STOP`/`TSTP`(Ctrl-Z) = suspend, `CONT` = resume; `USR1`/`USR2` = app-defined (e.g. Apache USR1 = graceful restart).
- **`kill -9` is the last resort, not the first.** TERM lets the process clean up; reach for KILL only after a polite request fails — and even KILL can't free a process wedged in `D` state.
- **Investigate before you kill a runaway.** Killing destroys the evidence. Capture a `strace`/`truss` first; suspect malware if a process is in a degenerate loop.

## Anti-patterns
- **Stars in every crontab field**: runs every minute (test-only). One minute is cron's finest granularity.
- **Editing crontab files directly**: cron may not notice; use `crontab -e` (or HUP cron). 
- **Assuming a working shell command works in cron**: cron's `sh` is *not* a login shell — it skips `~/.profile`/`~/.bash_profile`, so the environment differs. Wrap the command in a script that sets env vars.
- **`weekday` + `dom` both set**: matches if *either* holds (OR, not AND) — `* * 13 * 5` = every Friday AND every 13th, not "Friday the 13th."
- **Relying on `$PATH` for `nice`**: csh has a built-in `nice` with different syntax; use `/usr/bin/nice`.

## Code Examples
```sh
ps aux                 # overview: all processes, incl. no-tty, user format
ps lax                 # long format: PPID, NI, WCHAN; faster (no UID->name)
ps aux | grep -v grep | grep sshd   # find a PID without matching the grep itself
pidof /usr/sbin/sshd ; pgrep sshd   # PID by program name
kill -HUP <pid>        # reload a daemon's config
kill -9 <pid>          # force-kill (uncatchable); last resort
killall httpd          # kill by program name
pkill -u ben           # signal all of a user's processes
nice -n 5 ~/bin/longtask           # start lower priority
sudo renice -5 8829 ; sudo renice 5 -u boggs   # adjust running / per-user
top                    # live view; press 1 = per-core, f = pick columns (DATA)
sudo strace -p 5810    # trace a running process's syscalls + signals (truss on FreeBSD)
strace -f -e trace=file cmd        # follow forks; only file ops (find config files)
```
```
# crontab line: minute hour dom month weekday command
45 10 * * 1-5 /path/cmd      # 10:45am Mon-Fri
0-18/3 * * * * cmd           # every 3 hours, 0..18  (step syntax)
```

## Reference Tables
**Signals every admin knows**: HUP(1) reset/hangup · INT(2) Ctrl-C · QUIT(3, core) · KILL(9, uncatchable) · SEGV(11)/BUS(10) memory faults · TERM(15) default kill · STOP(17, uncatchable)/TSTP(18, Ctrl-C) suspend · CONT(19) resume · USR1(30)/USR2(31) app-defined. (`kill -l` lists all.)

**`ps aux` columns**: USER, PID, %CPU, %MEM, VSZ (virtual size), RSS (resident pages), TTY, STAT, TIME, COMMAND. STAT codes: `R` runnable, `S` sleeping, `D` uninterruptible sleep, `T` stopped/traced, `Z` zombie; flags `<` high-pri, `N` low-pri, `s` session leader, `+` foreground. Bracketed `[names]` = kernel threads.

## Worked Example
**Find what filled a filesystem.** A runaway process is producing output and the disk is full (logs flooding the console). (1) `df -h` → find the filesystem at 100%+ (root can exceed 100% by using the ~5% reserve). (2) `du -h <mountpoint>` → find the biggest directory; recurse down with `du` until you reach the offending files. Gotcha: `df` counts blocks from filesystem metadata while `du` sums file sizes — if a file was *unlinked but still held open* by a process, `df` shows the space used but `du` won't. To find the holder, use `fuser`/`lsof`; the space frees when the descriptor closes or the file is truncated.

## Key Takeaways
1. Processes are created by fork+exec; PID 1 (init/systemd) reaps orphans — zombies point back to a negligent parent via PPID.
2. Learn the signal vocabulary: HUP=reload, TERM=graceful (default), KILL=forceful last resort, STOP/CONT=suspend/resume.
3. `ps aux`/`ps lax`, `top`, `pgrep`/`pidof` are your daily monitoring kit; `D`-state processes can't be killed without fixing the cause.
4. Niceness tunes CPU scheduling only; only root lowers it; rarely needed on modern hardware.
5. `strace`/`truss` reveal what a stuck or suspicious process is actually doing — use after logs/verbose output fail, and before you kill the evidence.
6. cron schedules recurring work; mind the minute-granularity, the non-login shell environment, and the OR semantics of weekday+dom.

## Connects To
- **Ch 2**: PID 1 / systemd (and systemd timers as a cron alternative).
- **Ch 3**: real/effective UID, setuid, namespaces.
- **Ch 25**: container PID namespaces ("relativity for PIDs").
- **Ch 29**: performance analysis (load averages, top's CPU/memory fields, VIRT/RES/DATA).
