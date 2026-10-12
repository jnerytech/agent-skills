# Patterns & Techniques — Site Reliability Engineering

## Error-Budget Release Gating
**When to use**: Dev and SRE disagree on release velocity vs stability.
**How**: Product sets SLO → monitoring measures actual SLI → budget = 1 − SLO per quarter → release while budget remains; freeze launches and invest in reliability when spent. (Ch 3, 4)
**Trade-offs**: Needs SRE authority to halt launches; an SLO that's too tight blocks everything — loosen it rather than ignore it.

## SLO Control Loop with Safety Margin
**When to use**: Defining and running service targets.
**How**: Pick few SLIs users care about (percentiles, not averages) → set internal SLO tighter than the published one → measure, compare, act. Don't overachieve: if consistently far above SLO, plan controlled outages (global Chubby). (Ch 4)
**Trade-offs**: Too many SLIs dilute attention; averages hide tail latency.

## Toil Elimination under a 50% Cap
**When to use**: Ops work creeps up as the service grows.
**How**: Measure toil (manual, repetitive, automatable, tactical, no enduring value, O(n)); cap at 50%; redirect overflow to dev; spend the rest on engineering that scales sublinearly. (Ch 5)
**Trade-offs**: Some toil is unavoidable (on-call floor); grungy-but-valuable work isn't toil.

## Symptom-Based Paging on the Four Golden Signals
**When to use**: Designing monitoring for user-facing systems.
**How**: Measure latency, traffic, errors, saturation; page on symptoms, not causes; every page must be urgent, actionable, need judgment, and be novel; otherwise ticket or log. (Ch 6, 10)
**Trade-offs**: Cause-based alerts give earlier warning but produce noise.

## Automation Ladder → Autonomous Systems
**When to use**: Deciding how far to automate an operation.
**How**: Climb classes: none → externally maintained script → generic shared tool → internal to the service → autonomous (needs no automation). Judge by competence, latency, relevance. Make automation idempotent and validate inputs ("zero means all" bug). (Ch 7, 13)
**Trade-offs**: Automation at scale fails at scale; add rate limits and sanity checks.

## Hermetic, Self-Service Release Pipeline
**When to use**: Any service shipping frequently.
**How**: Hermetic builds → branch from mainline, cherry-pick fixes → full test suite → canary → staged rollout; config shipped as versioned packages. (Ch 8)
**Trade-offs**: Push-on-green needs strong tests and monitoring.

## Canary / Progressive Rollout
**When to use**: Every change, binary or config.
**How**: Deploy to a small slice (e.g. 0.1% → 1% → 10% → 100%), bake, compare against baseline, roll back first and diagnose later. Estimate fault order U = R·K/C from early reports. (Ch 17, 27, 35)
**Trade-offs**: Slower rollouts; low-traffic faults may slip through.

## Structured Troubleshooting
**When to use**: Any production problem.
**How**: Triage ("stop the bleeding", fly the airplane) → examine (metrics, logs, tracing) → diagnose (simplify/reduce, bisection, what touched it last) → test/treat → cure + postmortem. Prefer horses over zebras. (Ch 12)
**Trade-offs**: Hypothesis fixation; avoid confusing correlation with causation.

## Incident Command (ICS)
**When to use**: Incident needs a second team, is customer-visible, or is unresolved after an hour.
**How**: Separate roles (IC, Ops lead, Communication lead, Planning lead); one command post; live incident state document; explicit handoff ("you're now IC, okay?"). (Ch 14, 35)
**Trade-offs**: Overhead for small issues — declare early, close early.

## Blameless Postmortem
**When to use**: Any incident meeting predefined triggers (user-visible downtime, data loss, on-call intervention, long resolution, monitoring failure).
**How**: Timeline, impact, root causes, trigger, action items with owners; peer review; share widely; track action items to completion. (Ch 15, 35)
**Trade-offs**: Requires management support; blame destroys reporting.

## Load Balancing with Subsetting and Weighted Round Robin
**When to use**: Large client/backend fleets inside a datacenter.
**How**: DNS + anycast/VIP at the edge (Ch 19); inside, deterministic subsetting (20–100 backends per client), weighted round robin using backend-reported utilization; lame-duck state for draining. (Ch 20)
**Trade-offs**: Fast-failing unhealthy tasks can sinkhole traffic under least-loaded RR.

## Overload Defense Stack
**When to use**: Preventing and stopping cascading failures.
**How**: Per-customer quotas → client-side adaptive throttling → criticality-based shedding → graceful degradation → retry budgets with jittered exponential backoff → deadline + cancellation propagation → "overloaded; don't retry". Load-test to find the cliff. Emergency: add capacity, stop health-check kills, restart, drop traffic, enter degraded mode, eliminate batch load. (Ch 21, 22)
**Trade-offs**: Each layer adds complexity; untested degradation paths fail when needed.

## Consensus-Backed Critical State
**When to use**: Leader election, locks, configuration, queues needing strong consistency.
**How**: Use a proven implementation (Paxos/Raft/Zab) as a Replicated State Machine; 2f+1 replicas (5 typical); place replicas across failure domains; batching, pipelining, quorum leases for performance. Never hand-roll heartbeats/STONITH. (Ch 23)
**Trade-offs**: Latency bound by round trips; geography vs throughput.

## Distributed Cron
**When to use**: Periodic jobs that must survive machine loss.
**How**: Paxos-replicated leader; record launch start/finish as two sync points; fail closed; precomputed job names make partial launches idempotent; spread start times with hashing ("?"). (Ch 24)
**Trade-offs**: Missed runs preferred over double runs — check if that's right for your job.

## Continuous Pipeline (Workflow)
**When to use**: Pipelines with deep chains, hanging chunks or moiré load spikes.
**How**: MVC split — Task Master (model, journaled state), stateless workers (view), controller; server tokens and versioned leases for correctness; global workflow with reference tasks for continuity. (Ch 25)
**Trade-offs**: More complex than periodic batch; needed only at scale.

## Recovery-Oriented Data Integrity
**When to use**: Any user-data store.
**How**: Design for restore, not backup. Soft deletion → tiered backups (snapshots → distributed FS → tape) → replication → out-of-band daily validation; test restores continuously; cover 24 failure combinations (root cause × scope × rate). (Ch 26)
**Trade-offs**: Storage cost; replication alone spreads corruption.

## Launch Checklist + Feature Flags
**When to use**: Externally visible launches.
**How**: LCE review; checklist questions each backed by a past disaster (capacity, failure modes, client behavior, processes, dependencies, rollout); gradual rollout via feature flags; kill switch; jittered client retries. (Ch 27, 35)
**Trade-offs**: Checklists grow; keep a fast path for low-risk launch classes.

## Interrupt Polarization
**When to use**: Team drowning in pages/tickets/requests.
**How**: One primary on-call absorbs all interrupts; others are fully in project mode; rotate; scrub tickets for root causes; no half-on-interrupts. (Ch 29, 30)
**Trade-offs**: Interrupt person gets no project work that week.

## Production Readiness Review → Platform
**When to use**: Onboarding services to SRE support.
**How**: Engagement → analysis → improvements → training → onboarding → continuous improvement; evolve to early engagement and shared frameworks with a common control surface. (Ch 32)
**Trade-offs**: PRR doesn't scale alone; frameworks raise the baseline for all services.

## On-Call Training Ladder
**When to use**: Bringing new SREs on-call.
**How**: Learning checklist per component → teachable postmortems + Wheel of Misfortune → shadow on-call → reverse shadow → primary. Avoid "trial by fire". (Ch 28)
**Trade-offs**: Takes weeks of senior time.
