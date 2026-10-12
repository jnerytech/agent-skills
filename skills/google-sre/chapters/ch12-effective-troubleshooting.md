# Chapter 12: Effective Troubleshooting
*Authors: Chris Jones (sidebar "Negative Results Are Magic" by Randall Bosetti)*

> "Be warned that being an expert is more than understanding how a system is supposed to work. Expertise is gained by investigating why a system doesn't work." — Brian Redman
> "Ways in which things go right are special cases of the ways in which things go wrong." — John Allspaw

## Core Idea
Troubleshooting is learnable: apply the **hypothetico-deductive method** (observe → hypothesize → test → repeat) combined with solid system knowledge, while first stopping the bleeding and avoiding predictable reasoning fallacies.

## Frameworks Introduced
- **Troubleshooting process (Figure 12-1)**: Problem Report → **Triage** → **Examine** → **Diagnose** → **Test/Treat** → **Cure** (loop back from Test to Diagnose until a root cause is identified).
  - When to use: every problem, from "the system is slow" to a global outage.
  - How:
    1. **Problem report**: expected behavior, actual behavior, how to reproduce; consistent form, searchable store (open a bug for every issue).
    2. **Triage**: assess severity; *make the system work as well as it can under the circumstances* — divert traffic, drop traffic to prevent cascades, disable subsystems; preserve evidence (logs).
    3. **Examine**: metrics/time-series, logs, request tracing (Dapper), state-exposing endpoints, instrumented clients.
    4. **Diagnose**: simplify and reduce, divide and conquer/bisection, ask what/where/why, check what touched it last, build service-specific diagnostics.
    5. **Test and Treat**: rule hypotheses in/out via comparison with observed state or controlled changes.
    6. **Cure**: narrow to probable causal factors, fix, and write a postmortem.
  - Why it works: makes explicit what you know, what you don't, and what you need to know; bounds time-to-recovery instead of relying on luck or experience.
  - Failure mode: jumping straight to root-causing during a major outage — "Ignore that instinct!"; users aren't helped if the system dies while you root-cause.
- **"Fly the airplane" triage principle**: like novice pilots, your first responsibility is to keep the system up; troubleshooting is secondary. Freezing a system to stop unrecoverable data corruption can beat letting it run.
- **Test design criteria**:
  - Ideal test has **mutually exclusive alternatives** (rules one group in and another out).
  - **Consider the obvious first**: test in decreasing order of likelihood, weighted by risk to the system.
  - Watch for **confounding factors** (a firewall allowing only the app server's IP makes your ping fail).
  - Active tests have **side effects** (more CPUs → faster but more data races; verbose logging worsens latency).
  - Some tests are only **suggestive**, not definitive (races, deadlocks).
  - **Take clear notes** of ideas, tests and results (shared doc/chat gives timestamps); make changes systematically and documented so you can revert to the pre-test setup.
- **Diagnosis heuristics**:
  - **Simplify and reduce**: components with well-defined interfaces → inspect data flowing between them; inject known test data (black-box testing per step); build a reproducible test case, move it to non-production for riskier techniques.
  - **Divide and conquer**: walk the stack from one end to the other (good for pipelines); **bisection** for very large systems.
  - **Ask "what," "where," and "why"**: a malfunctioning system is still doing *something*; find what, where resources/output go, and why (akin to Five Whys).
  - **What touched it last**: systems have inertia; recent config/version/load changes are the best starting point — log deployments at all layers and annotate graphs with them.
- **Negative Results Are Magic** (Bosetti): negative results are conclusive, reusable, and should be published; tools built for disconfirming experiments outlive them; be skeptical of documents that never mention failure.

## Key Concepts
- **Hypothetico-deductive method**: iteratively hypothesize causes from observations plus theory, then test.
- **Treating the system**: changing it in a controlled way to observe results.
- **Proximate cause vs root cause**: you can fix the proximate cause before root-causing or writing the postmortem.
- **Logging verbosity levels**: multiple levels adjustable on the fly without restart; statistical sampling (e.g. 1 in 1,000) for high volume; a selection language ("show operations matching X").
- **State-exposing endpoints**: recent-RPC samples, per-RPC error/latency histograms, current config, Borgmon rule step-by-step tracing.
- **Bisection**: split the system in half, check communication paths, recurse.
- **Spurious correlation**: coincident or common-cause correlation (packet loss and disk failures both from a power outage).
- **Horses not zebras**: not all failures are equally probable; prefer simpler explanations (Occam's Razor), but remember Hickam's dictum — several common low-grade problems may jointly explain symptoms.
- **Path dependence**: systems often must be in a specific state before failure occurs; multiple jointly-causal factors are common.
- **Unique request identifier**: propagated across RPCs to match upstream and downstream log entries.

## Mental Models
- Think of troubleshooting as two factors: generic method × system knowledge; novices are usually limited by the latter.
- Use "what touched it last" first, because a working system stays working until acted upon by an external force.
- When you hear hoofbeats, think horses not zebras — but in some systems whole failure classes are eliminable by design.
- Think of a negative result as a deliverable: it settles design debates and saves the next team the experiment.

## Anti-patterns
- **Irrelevant symptoms / misread metrics**: wild goose chases.
- **Unsafe hypothesis testing**: misunderstanding how to change the system or inputs.
- **Wildly improbable theories or latching onto past causes** ("it happened once, so again").
- **Chasing spurious correlations**: coincidences multiply as more metrics are monitored (e.g. US CS PhDs vs cheese consumption, r² = 0.9416).
- **Root-causing before stopping the bleeding.**
- **Reporting problems directly to a person**: extra transcription, lower quality, invisible to the team, concentrates load on a few people instead of the on-call.
- **Undocumented active changes**: leaves the system in an unknown "hodge-podge" configuration.
- **Not publishing negative results**: biases metrics and forces others to repeat failed experiments.
- **Caching config in-memory with linear scans** (case study): latency scales with config data volume.

## Code Examples
```
GET /api/search
{ 'search_text': 'the forms of things unknown' }

Expected (HTTP 200):
[{
  "work": "A Midsummer Night's Dream",
  "act": 5,
  "scene": 1,
  "line": 2526,
  "speaker": "Theseus"
}]
```
What it demonstrates: a black-box probe with an exact expected payload — the basis of the `Shakespeare-BlackboxProbe_SearchFailure` alert.

## Reference Tables
| Test-design consideration | Example |
|---|---|
| Mutually exclusive alternatives | DB-credentials test vs ping test split network vs DB-refusal hypotheses |
| Obvious first, by likelihood × risk | Check connectivity before a config change revoking access |
| Confounding factors | Firewall IP allowlist makes workstation ping fail |
| Side effects | Verbose logging worsens latency; more CPUs expose races |
| Suggestive only | Race conditions, deadlocks |

| Spanner "what/where/why" chain | |
|---|---|
| Symptom | Spanner cluster high latency, RPCs timing out |
| Why? | Server tasks using all CPU |
| Where (CPU)? | Sorting entries in logs checkpointed to disk |
| Where (code)? | Evaluating a regex against log file paths |
| Solution | Rewrite regex to avoid backtracking; search codebase for similar patterns; use RE2 (linear time, no backtracking; PCRE can be exponential) |

## Worked Example
**Shakespeare search.** Alert: black-box prober can't find "the forms of things unknown" for 5 minutes; the alerting system filed a bug with prober links and the playbook entry. Probes run once a minute; ~half failed over 10 minutes with no pattern (note to fix: prober doesn't log failed responses). Manual `curl` returns **HTTP 502 Bad Gateway** with an `X-Request-Trace` header listing backend addresses — so the request reached the backends, ruling out the API frontend and load balancers. Focus shifts to backends: logs, test queries, exported metrics.

**App Engine case study.** A customer's CMS app saw latency rise ~10× and CPU and instances ~4× with no traffic increase or code change; it started on a Saturday with no pushes in flight, and no other apps were affected. (1) Developers noticed correlation with `merge_join` calls → suboptimal-index theory. (2) Dapper tracing showed static content (not served from datastore) was also slow → the correlation was **spurious**. (3) Memcache RPCs were fast, but ~**250 ms** passed before the first RPC — untraceable app code. (4) Launch was the next week, so they **mitigated first**: moved to the most CPU-rich instance type. (5) Suspected a change in the type of work (a small write burst earlier, dismissed as coincidence). (6) Developers added instrumentation → a per-request whitelist check using an in-memory cache ("blinded by smoke coming from this whitelist cache"). Root cause: a long-standing access-control bug created a whitelist object per access to one path; a pre-launch **automated security scanner** generated thousands in half an hour, each checked linearly on every request. Fixing the bug and deleting the objects restored performance.

## Key Takeaways
1. On a major outage, stop the bleeding first (divert/drop traffic, disable subsystems), preserve evidence, then root-cause.
2. Require problem reports with expected vs actual behavior and repro steps, filed as bugs, not sent to people.
3. Start with "what touched it last," and log/annotate every deploy and config change.
4. Design tests with mutually exclusive outcomes, ordered by likelihood and risk; account for confounders and side effects.
5. Keep timestamped shared notes and make active changes systematically so you can revert.
6. Build observability in from the start: white-box metrics, structured logs, adjustable verbosity, state endpoints, unique request IDs across RPCs.
7. Publish negative results and surprising findings.

## Connects To
- **Ch 10**: exported variables and Borgmon rule tracing as telemetry.
- **Ch 6**: black-box vs white-box monitoring.
- **Ch 13/14**: emergency response and incident declaration for severe triage outcomes.
- **Ch 15**: postmortem as the output of the Cure step.
- **Ch 22**: dropping traffic to prevent cascading failure.
- **Ch 28**: learning a system via first-principles troubleshooting.
- **Ch 29**: routing reports to the on-call, not individuals.
- **Five Whys (Ohno)**, **Occam's Razor / Hickam's dictum**, **Dapper** distributed tracing.
