# Chapter 25: Data Processing Pipelines
*Authors: Dan Dennison (edited by Tim Harvey)*

## Core Idea
Periodic (cron-driven) Big Data pipelines start out stable but become fragile as they grow organically: hanging chunks, scheduling delays, poor monitoring, thundering herds, Moiré load. If the work is continuous, or will become continuous, use a continuous leader-follower system with strong guarantees, like Google's **Workflow**, instead.

## Frameworks Introduced
- **Periodic vs. continuous pipeline decision rule**: periodic pipelines are valuable, but if a data processing problem is continuous or will organically grow into one, don't use a periodic pipeline.
  - When to use: at pipeline design time, and again whenever the business starts asking for fresher results.
  - How: at the outset, scope the expected growth trajectory, demand for design modifications, expected additional resources, and the business's expected latency requirements. Pressure to refactor usually arrives at the worst moment (big new customers, new features, immovable deadlines), so decide early.
  - Why it works / failure mode: periodic pipelines tuned at install time (worker sizing, periodicity, chunking) drift into missed deadlines, resource exhaustion and hanging chunks as data grows, which turns into operational load.
- **Workflow as Model-View-Controller**: a distributed-systems version of MVC, built from the leader-follower (workers) pattern and the system prevalence pattern.
  - **Model = Task Master**: holds all job state in memory and synchronously journals mutations to disk (system prevalence). It is best used to store *pointers* to work, with the data kept in a shared filesystem.
  - **View = workers**: completely stateless, discardable at any time. They transactionally update state with the master from their stage's point of view, and they are self-scheduling (a worker can choose which work type to take).
  - **Controller (optional)**: auxiliary activities such as runtime scaling, snapshotting, workcycle state control, rolling back pipeline state, and global interdiction for business continuity.
  - Stages are *task groups* in the Task Master, so pipeline depth can be anything (map, shuffle, sort, split, merge per stage), with **exactly-once** execution reflected in permanent state.
- **The four Workflow correctness guarantees**:
  1. **Configuration tasks as barriers**: work is predicated on configuration. A worker must cite the config task ID it used, so after a config change, in-flight work done under the old config can't commit.
  2. **Valid lease required to commit**: each work unit has a uniquely held lease, and only the current lease holder can commit.
  3. **Uniquely named output files per worker**: orphaned workers can keep writing but can never overwrite a valid worker's output, and they fail at commit.
  4. **Server token validation**: client and server check a unique Task Master token on every operation, which defends against an address change, memory corruption of IP/port, or a load balancer wrongly put in front of several Task Masters.
  - Plus **task versioning**: any update or lease change creates a new immutable task with a new ID. Tasks being unique and immutable is why Workflow beats simply using Spanner or a database (with a database, every read would have to sit in a long-running transaction).
  - Why it works: correctness is enforced by structure (leases, unique names, versions, tokens), not by timing assumptions.
- **Business continuity via global Workflow with reference tasks**: run two or more local Workflows in distinct clusters plus a global Workflow. The Task Master journals to Spanner (globally consistent, low throughput), Chubby elects the writer Task Master and the result is persisted in Spanner, and clients find the current Task Master through naming services.
  - How: a "stage 1" helper binary (the controller) inserts a *reference task* into the global Workflow for each unit of work and updates a *heartbeat task*. "Stage n" transactionally removes reference tasks when work finishes. If the global Workflow is unavailable, the local one blocks, which preserves correctness. If the heartbeat goes stale past its timeout, the remote Workflow's helper seizes the in-progress work recorded in the reference tasks.

## Key Concepts
- **Data pipeline**: a program that reads data, transforms it and writes output, traditionally run periodically by cron. Lineage: coroutines, DTSS communication files, UNIX pipe, ETL.
- **Simple, one-phase pipeline**: a single program doing periodic or continuous transformation on Big Data.
- **Multiphase pipeline**: a chain of programs where each one's output is the next one's input, organized for ease of reasoning rather than operational efficiency.
- **Pipeline depth**: the number of chained programs, from 1 (shallow) to tens or hundreds (deep).
- **Embarrassingly parallel**: splitting the workload into machine-sized chunks. This is the key enabler of Big Data.
- **Hanging chunk**: one chunk that is much slower (because of data skew such as one huge customer, machine differences, or overallocation) blocks the stage, since downstream steps like sorting need all of the data.
- **Batch scheduling priority**: periodic pipelines run as lower-priority batch work in the gaps Borg leaves. That brings open-ended startup delays and risk of preemption. Cost is inversely proportional to the startup delay you request and directly proportional to resources consumed.
- **Moiré load pattern**: two or more pipelines whose execution cycles occasionally overlap and hit a shared resource at the same time, producing interference peaks that are visible only in stacked usage plots.
- **System prevalence**: in-memory state plus a synchronous journal of mutations to persistent disk.
- **Reference task / heartbeat task**: entries in the global Workflow that record work in progress and local liveness, so another cluster can fail over.

## Mental Models
- Think of **pipeline completion time as the slowest chunk**. End-to-end runtime is capped by the largest indivisible unit (e.g. the biggest customer).
- Use **"the minimum average scheduling delay is a latency floor"**: once the execution interval approaches the scheduling delay, running more often brings no progress, only overlapping or killed runs.
- Think of **Workflow's correctness as layered fences** (config barrier, lease, unique filename, server token). Each layer catches a failure the previous one misses, so orphaned workers and rogue masters can't corrupt state.
- Use **"periodic pipelines report at the end"** as a warning sign: metrics collected during the job and reported only on completion disappear when the job fails. Continuous pipelines emit real-time telemetry by design.

## Anti-patterns
- **Killing and restarting a hanging job**: the "sensible" default, but pipelines usually have no checkpointing, so every chunk restarts from zero and all the time, CPU and human effort is wasted.
- **Shrinking the execution interval below the scheduling-delay floor**: runs stack up on the scheduler, or the next run kills the nearly finished current one, which halts all progress.
- **Adding more workers when a pipeline runs late**: inexperienced engineers make the thundering herd worse.
- **No retry logic, or naive retry logic**: without retries, work is silently dropped (a correctness problem); naive retries compound overload.
- **Over-relying on batch scheduler resources**: you risk preemption when the cluster is loaded. Separate batch resources from production-priority resources to rationalize acquisition cost.
- **Metrics reported only at job completion**: no visibility during an emergency.
- **A load balancer in front of independent Task Masters**: operations run smoothly until a task ID collision. Server tokens prevent it.
- **Using a general database as the Task Master**: workable, but every read must sit inside a long-running transaction, which is "terribly inefficient."

## Reference Tables
| Periodic pipeline failure mode | Cause | Mitigation |
|---|---|---|
| Jobs exceed run deadline | Organic data growth vs. fixed tuning | Re-scope growth; go continuous |
| Hanging chunk | Uneven chunk sizes, machine variance | Better chunking; checkpointing; don't blind-restart |
| Open-ended startup delay / preemption | Low-priority batch scheduling | Secure dedicated capacity; distinguish batch vs. prod resources |
| Overlapping or killed runs | Interval below scheduling-delay floor | Keep interval well above delay (e.g. >40 min for ~20-min job) |
| No in-flight metrics | Report-on-completion monitoring | Real-time telemetry (continuous design) |
| Thundering herd | Thousands of workers starting at once; bad retries | Bounded workers, sane retries/backoff |
| Moiré load | Overlapping cycles of multiple pipelines on shared resources | Plot stacked shared-resource usage; desynchronize |

## Worked Example
**Execution interval vs. scheduling delay (Fig. 25-1).** Take a periodic pipeline whose job takes about 20 minutes. As you lower the execution interval, the idle time between runs shrinks along a downward-sloping line until it meets the scheduling delay. Below about **40 minutes** the runs may overlap: depending on batch policy, new runs queue behind unfinished ones, or the nearly finished run is killed when the next one starts, so progress stops entirely. **Moiré example (Figs. 25-2/25-3):** three periodic pipelines each look fine on separate plots. Stacked on shared infrastructure, their cycles occasionally line up and aggregate load peaks near **1.2M**, and those peaks are when on-call pain happens.

## Key Takeaways
1. Before building a pipeline, scope the growth trajectory, how often the design will change, the resources it will need, and its latency requirements. If it is or will be continuous, don't make it periodic.
2. Design chunking for skew, and add checkpointing so a restart doesn't throw away all the work.
3. Keep the periodic interval well above the batch scheduling delay, and secure appropriate capacity rather than relying on preemptible batch resources.
4. Emit real-time pipeline metrics, not just end-of-run summaries.
5. Control thundering herds with bounded worker counts and proper retry/backoff, and check stacked shared-resource graphs for Moiré peaks.
6. For continuous processing, use a leader-follower model with stateless workers, leases, unique output names, versioned immutable tasks, config barriers and server tokens, which gives exactly-once semantics.
7. For business continuity, mirror work into a globally consistent store (reference tasks plus heartbeat) so another cluster can take over automatically.

## Connects To
- **Ch 24**: cron launches periodic pipelines, and both suffer thundering herds and batch scheduling limits.
- **Ch 23**: Chubby (consensus) elects the Task Master writer, and Spanner provides globally consistent journals.
- **Ch 2**: Borg batch scheduling and preemption.
- **Ch 22**: retry storms and overload during thundering herds.
- **Ch 26**: data integrity and exactly-once correctness of pipeline outputs.
- **Ch 6**: real-time monitoring vs. end-of-run metrics.
- **MapReduce / Flume / Apache Beam / Dataflow**: the frameworks behind periodic pipelines and their continuous successors.
