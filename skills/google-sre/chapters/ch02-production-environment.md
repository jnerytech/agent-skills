# Chapter 2: The Production Environment at Google, from the Viewpoint of an SRE
*Authors: JC van Winkel (edited by Betsy Beyer)*

## Core Idea
Google production is homogeneous hardware abstracted by software (Borg, Colossus, GSLB, Chubby, Borgmon, Stubby) so that services never bind to specific machines; the chapter supplies the vocabulary used throughout the book and walks a sample service (Shakespeare) through it.

## Frameworks Introduced
- **Machine vs. Server terminology**: *Machine* = a piece of hardware (or VM); *Server* = a piece of software that implements a service. Machines can run any server; no machine is dedicated to a program.
  - When to use: Whenever discussing capacity or failures — separates hardware failure domains from software instances.
  - Why it works: Decoupling lets the cluster OS (Borg) bin-pack and reschedule freely; hardware failure becomes a scheduling event, not an outage.
- **Datacenter topology hierarchy**: tens of machines → *rack*; racks → *row*; one or more rows → *cluster*; a datacenter building houses multiple clusters; nearby buildings → *campus*.
- **Borg job model**: A *job* (long-running server or batch, e.g., MapReduce) consists of one to thousands of identical *tasks*. Borg finds machines, starts tasks, monitors them, kills and restarts malfunctioning tasks (possibly elsewhere).
  - How: Each job declares resources (e.g., 3 CPU cores, 2 GiB RAM); Borg bin-packs tasks accounting for failure domains (not all tasks on one rack — top-of-rack switch would be a SPOF). Tasks exceeding their request are killed and restarted ("a slowly crashlooping task is usually preferable to a task that hasn't been restarted at all").
- **Borg Naming Service (BNS) indirection**: Address tasks by name, not IP:port: `/bns/<cluster>/<user>/<job name>/<task number>` → `<IP address>:<port>`.
- **Storage stack layers**: D (disk/flash fileserver on nearly every machine) → Colossus (cluster-wide filesystem, replication + encryption; successor to GFS) → database-like services: Bigtable (NoSQL, petabyte scale, eventually consistent cross-DC replication), Spanner (SQL-like, global real consistency), Blobstore and others.
- **GSLB three-level load balancing**: (1) geographic DNS load balancing (Ch 19); (2) user-service level (e.g., YouTube, Maps); (3) RPC level (Ch 20). Owners give a symbolic name, list of BNS addresses, and capacity per location (QPS).
- **N + 2 provisioning**: Provision peak tasks + 2 so that one task can be down for update and one machine can fail simultaneously while still serving peak.
  - Why it works / failure mode: Assumes two simultaneous task failures are negligibly likely; shared SPOFs (top-of-rack switches, power distribution) can invalidate that assumption.

## Key Concepts
- **Borg**: Distributed cluster OS (similar to Apache Mesos; ancestor of Kubernetes) managing jobs at cluster level.
- **Jupiter**: Clos network fabric of hundreds of Google-built switches; up to 1.3 Pbps bisection bandwidth.
- **B4**: Globe-spanning SDN backbone (OpenFlow) with elastic bandwidth allocation between datacenters.
- **Bandwidth Enforcer (BwE)**: Allocates network bandwidth to maximize average available bandwidth, like Borg for compute.
- **Chubby**: Lock service with a filesystem-like API, uses Paxos for consensus; used for master election and consistent data (e.g., BNS path → IP:port mappings).
- **Borgmon**: Monitoring program that "scrapes" metrics for alerting, behavior comparison, and capacity trends.
- **Stubby / gRPC**: Google's RPC infrastructure; used even for local calls to ease later refactoring into separate servers.
- **Protocol buffers (protobufs)**: Serialization format; 3–10x smaller and 20–100x faster than XML, less ambiguous.
- **Frontend / backend**: A server receives RPCs from its frontend (client) and sends RPCs to its backend (server).
- **Monorepo + CL + push-on-green**: Single shared repository, all changes reviewed as changelists, continuous testing of all dependents, some projects auto-push after passing tests.
- **GFE (Google Frontend)**: Reverse proxy that terminates the user's TCP connection.

## Mental Models
- Think of a datacenter as one big computer: Borg is its OS, BNS its naming layer, Colossus its disk.
- Use name-based indirection (BNS) whenever task placement is fluid; never hard-code IP:port.
- Think of a request as a chain of GSLB lookups and RPCs; every hop is a potential failure point (a failing GSLB "would wreak havoc").
- Use N + 2 per region for important serving, and consciously downgrade to N + 1 where cost savings outweigh a small latency risk.

## Anti-patterns
- **Dedicating machines to specific servers**: Prevents bin-packing and turns hardware failure into service failure.
- **Placing all of a job's tasks in one failure domain**: Top-of-rack switch becomes a SPOF.
- **Cross-continent data access from serving path**: Asia backend reading a US Bigtable adds major latency — replicate data per region.
- **Expecting hardware not to fail**: Thousands of machines and disks fail per cluster per year; abstract failures away in software.

## Code Examples
```
/bns/<cluster>/<user>/<job name>/<task number>  ->  <IP address>:<port>
```
What it demonstrates: BNS naming that decouples clients from the physical location of Borg tasks.

## Reference Tables
| Shakespeare region | Peak QPS | Tasks (backend ~100 QPS each) | Redundancy |
|---|---|---|---|
| North America (USA) | 1,430 | 17 | N + 2 |
| South America | 290 | 4 | N + 1 (deliberate) |
| Europe & Africa | 1,400 | 16 | N + 2 |
| Asia & Australia | 350 | 6 | N + 2 |
| Global total | ~3,470 | 35 min; 37 single-site (N + 2) | |

| Network/serialization fact | Value |
|---|---|
| Jupiter bisection bandwidth | 1.3 Pbps |
| Protobuf vs XML | 3–10x smaller, 20–100x faster |
| End-to-end Shakespeare request | a few hundred ms |

## Worked Example
**Shakespeare service** (find where a word appears in Shakespeare's works):
- *Batch*: a MapReduce — map (split texts into words, parallel), shuffle (sort tuples by word), reduce (build `(word, list of locations)`) — each tuple written to a Bigtable row keyed by word. Runs rarely.
- *Life of a request*: (1) browser resolves shakespeare.google.com via DNS → Google DNS consults GSLB for a frontend IP; (2) GFE terminates TCP, identifies the service; (3) GFE uses GSLB to pick a Shakespeare frontend and sends an RPC with the HTTP request; (4) frontend builds a protobuf and asks GSLB for the BNS address of an unloaded backend; (5) backend queries Bigtable; results flow back as protobufs, frontend renders HTML.
- *Sizing*: Load tests show ~100 QPS/backend task; peak ~3,470 QPS → 35 tasks; N + 2 → 37 (one in update, one machine failure). Regionally: 17 USA, 16 Europe, 6 Asia, and South America cut from 5 to 4 (N + 1), accepting latency risk if GSLB spills traffic to another continent, saving 20% of that region's hardware. Larger regions spread across 2–3 clusters. Bigtable replicated per region for resilience and lower latency; eventual consistency is acceptable because data rarely changes.

## Key Takeaways
1. Separate "machine" (hardware) from "server" (software) in all capacity and failure discussions.
2. Refer to tasks through a naming service, never fixed IP:port.
3. Declare resource requirements per task and spread tasks across failure domains.
4. Size serving jobs from load-tested per-task QPS at peak, then add N + 2 (or a deliberate N + 1).
5. Replicate data close to each serving region; choose the datastore (Bigtable vs Spanner) by required consistency.
6. Expose diagnostics via an HTTP server in every binary; use RPC + protobufs for all inter-service calls.

## Connects To
- **Ch 10**: Borgmon in depth.
- **Ch 19 / Ch 20**: GSLB DNS and RPC-level load balancing.
- **Ch 23**: Chubby, Paxos and distributed consensus.
- **Ch 26**: Storage trade-offs (Bigtable, Spanner, Blobstore) and data integrity.
- **Ch 8**: Monorepo, CLs, continuous build/test, push-on-green.
- **Ch 4 / Ch 12**: Shakespeare reused for SLOs and troubleshooting.
- **Kubernetes**: Open-source descendant of Borg.
