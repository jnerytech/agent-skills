# Chapter 24: Distributed Periodic Scheduling with Cron
*Authors: Štěpán Davidovič (edited by Kavita Guliani)*

## Core Idea
Single-machine cron has one failure domain and fire-and-forget launches. At datacenter scale, cron becomes a stateful, Paxos-replicated service that launches jobs through the datacenter scheduler (Borg). It has to track every launch, resolve partial failures, and prefer skipping a launch to launching twice.

## Frameworks Introduced
- **"Fail closed": prefer skipped launches over double launches**: infrastructure should favor skipping a launch over risking a duplicate, as far as it can.
  - When to use: deciding failure semantics for any scheduler or "run exactly once" system serving mixed workloads.
  - How: (1) recognize that jobs differ, some idempotent (garbage collection) and some not (newsletter email, payroll); (2) default the system to skipping; (3) make job owners responsible for monitoring their jobs, so a skip is detected and handled in a way that suits the job.
  - Why it works / failure mode: a skipped launch can be recovered from (rerun it), but a double launch (a second newsletter) may be impossible to undo. Fail-open behavior systematically creates bad state.
- **Two synchronization points per launch**: use Paxos to announce *"about to launch"* and *"finished launch"* synchronously to a quorum. Launches are uniquely identified by **cron job + scheduled launch time**.
  - How: the leader waits for quorum confirmation of "about to launch" before it actually launches. Followers update their next scheduled time when they hear about a commenced launch and track the *open launches* (begun but not completed). "Finished" means the launch was *attempted*, whether or not it succeeded externally.
  - Why it works / failure mode: if the leader launches before informing followers and then dies, the new leader repeats the launch.
- **Resolving partial failures (pick at least one)**: so that a new leader can finish open launches, either (a) **every operation on external systems is idempotent**, or (b) **the state of every external operation can be looked up** to tell unambiguously whether it completed. Without one of these you get missed or double launches.
  - How (Google's approach): precompute datacenter job names ahead of time (no mutation on the scheduler), embed the scheduled launch time in each name, and distribute the names to all replicas. On re-election the new leader looks up every precomputed name and launches only the missing ones.
- **Leader/follower roles over Paxos**: a single leader, which is also the Fast Paxos leader, is the only replica that changes state or launches jobs. Followers mirror its state so they can take over at once. Leader election must converge in **under one minute** (the smallest cron interval); Paxos health checks detect a dead leader within seconds.
  - Rule: the moment a leader loses leadership it must **stop talking to the datacenter scheduler immediately**, because holding leadership is what guarantees mutual exclusion.
- **Hybrid state storage (logs local, snapshots backed up)**: keep Paxos logs and snapshots on the local disk of each of 3 replicas, and back up only the *snapshots* to a distributed filesystem. New replicas fetch the snapshot and logs from a running peer over the network, so they don't depend on local machine state.
- **Crontab "?" extension against thundering herds**: "?" means the system may choose any value, picked by hashing the job configuration over the range (e.g. 0..23 for hour), which spreads launches out.

## Key Concepts
- **crond**: the single-daemon cron implementation. It loads the crontab and launches jobs; its only persistent state is the crontab.
- **anacron**: the exception. It records last-launch timestamps and relaunches jobs (daily or less often) that were missed while the machine was down.
- **Idempotent cron job**: safe to run more than once (e.g. garbage collection). Non-idempotent jobs (newsletter, payroll) are not.
- **Decoupling processes from machines**: you specify requirements and a datacenter, and the datacenter scheduler picks machines and handles machine death. Launching a job becomes one or more RPCs.
- **Hot spares**: standby replicas that take over fast. They are needed because rescheduling a replica (health-check timeout, software install, startup) can take 1–2 minutes, which is too slow for a five-minute job.
- **Partial launch failure**: a logical launch spans several RPCs and the sender dies midway, so some succeed and some don't.
- **Open launch**: a launch whose start was recorded but whose completion wasn't.
- **Paxos log compaction / snapshot**: replace the log of state changes with the current state (e.g. a thousand "increment counter by 1" entries become "set counter to 1,000").
- **Thundering herd**: many jobs (e.g. "daily at midnight" MapReduces from 30 teams) start at the same moment and spike datacenter load.
- **Sharing fate with the scheduler**: running cron per datacenter keeps latency low and ties cron to its core dependency, the datacenter scheduler.

## Mental Models
- Think of **snapshots as your most critical state and logs as a bounded loss**. Losing logs sends cron back in time to the last snapshot; losing snapshots means starting from zero.
- Use **"base services should have very few dependencies"** when choosing storage. Cron must keep running for a while even when parts of the datacenter are gone, so it stores its small state itself rather than in GFS/HDFS, which handle small writes slowly and expensively.
- Think of **a launch's identity as (job, scheduled time)**, everywhere: in internal state and in datacenter job names. Without the time, a long failover after a short, frequent job finishes looks like "not launched" and gets relaunched.
- Use **per-job owner monitoring** as the counterpart to fail-closed: the platform skips, and owners detect the skip and recover.

## Anti-patterns
- **Hosting cron on one machine in a 1,000-machine datacenter**: losing 1/1000th of capacity takes out every scheduled job.
- **Fire-and-forget launches at scale**: you can't account for resources, report state to owners, or recover from failover.
- **Asynchronous Paxos notification of launches**: the launch can happen without followers knowing, and after failover the job gets launched twice.
- **A deposed leader that keeps calling the scheduler**: two leaders issue conflicting actions.
- **Job names without the scheduled launch time**: the new leader can't tell which launch a finished job belongs to, and double-launches.
- **Storing Paxos logs on a distributed filesystem**: frequent small writes carry a heavy performance penalty. Google consciously accepted the risk of losing the most recent log entries instead.
- **Everyone scheduling "0 0 * * *"**: midnight thundering herd of huge MapReduces.

## Code Examples
```
0 0 * * *      # standard crontab: minute 0, hour 0, every day, every month -> daily at midnight
? ? * * *      # Google extension: "?" = system picks the value by hashing the job config over the range
```
What it demonstrates: "?" keeps a job's semantics ("once a day") while letting the scheduler spread launch times to avoid spikes. Even so, the global launch graph stays spiky because many jobs must run at specific times, for example because they depend on external events.

## Reference Tables
| Dimension | Single-machine cron | Google distributed cron |
|---|---|---|
| Failure domain | One machine | Replicas spread within a datacenter (diverse power domains) |
| Persistent state | crontab only | crontab + launch state via Paxos (logs + snapshots) |
| Launch tracking | Fire-and-forget | Full lifecycle, scheduled launch to termination |
| Isolation | Usually none | Containers with up-front resource requests |
| Launch mechanism | fork/exec | RPC(s) to datacenter scheduler (Borg) |
| Failover | None | Paxos leader re-election in seconds, well under 1 min |
| Replicas | 1 | 3 by default |

| State artifact | Stored where | Loss impact |
|---|---|---|
| Paxos logs | Local disk on each of 3 replicas | Bounded: back to last snapshot |
| Snapshots | Local disk + backup on distributed FS | Critical: lose all internal state |

## Worked Example
**Double launch after a long failover.** A short, frequently run job is launched by the leader. Before the launch completion reaches a quorum, the leader crashes. Failover takes unusually long, long enough for the job to finish successfully on the datacenter scheduler. The new leader sees an open launch, looks up the job, sees it completed, and (without launch-time disambiguation) launches it *again*. **Fix:** put the scheduled launch time into the precomputed datacenter job name. The new leader then recognizes the finished job as *this* launch, closes the open launch, and doesn't relaunch.

## Key Takeaways
1. Default distributed schedulers to fail closed (skip rather than double-launch), and require owners to monitor their jobs.
2. Record "about to launch" and "launch done" synchronously through consensus *before* acting, keyed by job and scheduled time.
3. Make external operations idempotent or queryable. Precomputed, time-stamped job names give you both.
4. A replica that loses leadership must stop touching external systems immediately.
5. Compact logs into snapshots, and back up snapshots off-box: they are the irreplaceable state.
6. Keep base services low-dependency and co-located with their core dependency (the datacenter scheduler).
7. Spread launch times (hash-based "?") to tame thundering herds.

## Connects To
- **Ch 23**: Paxos/Fast Paxos, leader election, RSM, and log/snapshot handling come straight from the consensus chapter.
- **Ch 25**: periodic pipelines run on cron and suffer the same thundering-herd and batch-scheduling problems.
- **Ch 2**: Borg is the datacenter scheduler that cron launches into.
- **Ch 22**: synchronized launches cause load spikes that can cascade.
- **Ch 6**: owners monitoring their cron jobs, and exposing launch state.
- **Mesos / Kubernetes CronJob**: named-job lookup enables idempotent recovery (Kubernetes CronJob's "concurrencyPolicy" reflects the same skip-vs-double concern).
