# Chapter 32: The Evolving SRE Engagement Model
*Authors: Acacio Cruz and Ashish Bhambhani (edited by Betsy Beyer and Tim Harvey)*

## Core Idea
SRE engagement evolved from the late, expensive **Simple PRR Model** (review a launched service, then take it over), to the **Early Engagement Model** (SRE in design and build), to **Frameworks and SRE Platform**: SRE-built, reusable infrastructure that makes services "production ready by design" and breaks the SRE staffing barrier. All three models are still in use.

## Frameworks Introduced
- **Production Readiness Review (PRR)**: a process that identifies a service's reliability needs from its specifics. It is a prerequisite for an SRE team to accept production responsibility.
  - Objectives: (1) verify that the service meets accepted standards of production setup and operational readiness, and that its owners are ready to work with SRE; (2) improve reliability and minimize the number and severity of expected incidents.
- **Simple PRR Model (phases)**: used for services already launched.
  1. **Engagement**: SRE leadership picks the team, and 1–3 SREs run the PRR. Agree on the SLO/SLA, potentially disruptive design changes, and planning/training schedules.
  2. **Analysis**: gauge maturity along SRE's axes using a service-specific **PRR checklist** (domain expertise, similar systems, Production Guide). Review recent incidents, postmortems and follow-ups.
  3. **Improvements and Refactoring**: prioritize by reliability importance, negotiate a plan with dev, and implement jointly. This phase varies the most in duration.
  4. **Training**: PRR leads train the whole SRE team (design overviews, request-flow deep dives, production setup, hands-on ops exercises) and write the docs.
  5. **Onboarding**: progressive transfer of operations, change management and access rights. Dev stays available as backup for a period.
  6. **Continuous Improvement**: lessons go back to dev as proposals and into the Production Guide.
  - Why it works: a structured gate ensures SRE takes over only services meeting a bar, with an agreed SLO.
  - Failure mode: it starts very late, after launch and at scale. Design flaws are costly to unwind, lead times are quarters long, and takeovers are serialized.
- **SRE engagement axes ("production")**: system architecture and interservice dependencies; instrumentation, metrics and monitoring; emergency response; capacity planning; change management; performance (availability, latency, efficiency).
- **Early Engagement Model**: SRE participates from the Design phase and takes over any time during or after Build.
  - Candidates: significant new functionality within an existing SRE-managed system; a significant rewrite of or alternative to an existing system; dev sought SRE advice or takeover at launch.
  - Benefits by phase: *Design*, prevent incidents ("The best production incidents are those that never happen!") and co-own trade-offs; *Build*, recommend libraries and add operational/emergency controls; *Launch*, patterns like **dark launch**; *Post-launch*, fewer reliability-vs-feature conflicts and faster takeover.
  - Disengaging is a positive outcome if the service is reliable and low-maintenance enough to stay with dev. Effort on services that miss projected usage is accepted business risk.
- **Frameworks and SRE Platform**: SRE-supported platform and service frameworks per language (Java, C++, Go), maintained by SRE and dev together. The four principles:
  1. **Codified best practices**: what works in production is committed to code.
  2. **Reusable solutions**: shareable mitigations for scalability and reliability.
  3. **A common production platform with a common control surface**: uniform interfaces, operational controls, monitoring, logging and config.
  4. **Easier automation and smarter systems**: e.g., a single outage view instead of hand-collected raw data.
  - How: framework modules encapsulate infrastructure concerns (instrumentation/metrics, request logging, traffic and load management control systems). Dev writes business logic. Implementations differ by language but share the same API, behavior, config and controls.
  - Why it works: SRE's concerns are mostly in infrastructure code. Standardizing that code makes reviews trivial and lets improvements propagate to every service.

## Key Concepts
- **Onboarding**: evaluating a service, closing gaps, and instituting SRE support.
- **PRR checklist**: a service-specific list of production-readiness questions for the Analysis phase.
- **Production Guide**: Google's documented production best practices, a source for PRRs and consultations.
- **Alternative support**: documentation and consultation for services that don't get full SRE.
- **Launch consultation**: 1–2 SREs spend a few hours studying the design, then advise on risky areas (LCE does much of this).
- **Dark launch**: copy part of live traffic to the new service and discard its responses, to gain operational insight without user impact.
- **Gold standard config**: an SRE team's preferred configuration form that works with its scalable tooling.
- **Framework**: a prescriptive implementation for using a set of components, plus a canonical way of combining them.
- **Shared responsibility model**: SRE supports the platform (load shedding, overload, automation, traffic management, logging, monitoring), and dev is on-call for application bugs.
- **Universal support by design**: services without SRE still get SRE-built production features.

## Mental Models
- Think of SRE engagement like **bug-fix cost**: the earlier SRE is involved, the cheaper and better the outcome.
- Use **Simple PRR** for a fait-accompli backlog of launched services, **Early Engagement** for high-value new or rewritten systems, and **Frameworks** to scale beyond SRE headcount.
- Think of a **platform** as the best engagement: it short-circuits bespoke systems "arriving at SRE's door".
- Use **consultation → long-term engagement** escalation when a service has grown by orders of magnitude or has become a dependency of many clients.

## Anti-patterns
- **Engaging only after launch at scale**: the main PRR limitation. Suboptimal design must be unwound.
- **Reimplementing production features per service**: e.g., functionally similar logging frameworks rebuilt repeatedly in the same language.
- **Service-local SRE engineering**: improvements don't propagate to already-onboarded services.
- **SREs acting as an external unit during PRR**: they should work as part of the dev team, visibly, with knowledge sharing.
- **Binary engagement (full SRE or nothing)**: replaced by shared responsibility on a platform.
- **Retrofitting apps to SRE specs, or retrofitting more SREs to unusual services**: frameworks remove both.

## Reference Tables
| Dimension | Simple PRR (pre-frameworks) | Frameworks/Platform |
|---|---|---|
| SREs per onboarding | 2–3 | 1 |
| Onboarding duration | 2–3 quarters | ~1 quarter |
| PRR lead time | Quarters away | Much faster |
| Idea → SRE-level production | Months | "A matter of days" |
| Staffing basis | Per service | Per platform (shared across products) |

| Model | When SRE engages | Typical target |
|---|---|---|
| Simple PRR | After Launch | Already launched service |
| Early Engagement | Design phase onward | Important new/rewritten service |
| Frameworks & SRE Platform | Before design (build on the platform) | All services, including non-SRE ones |

## Worked Example
**Engaging with Shakespeare (Simple PRR).** Developers initially carried the pager. As usage and revenue grew, SRE support became desirable. Since the service had already launched, SRE ran a PRR and found that dashboards didn't fully cover some SLO metrics. After all filed issues were fixed, SRE took the pager, with two developers remaining in the on-call rotation. Developers attend the weekly on-call meeting (last week's problems, upcoming maintenance and cluster turndowns), and future launches are now planned with SRE.

**Sample PRR checklist items:** Do updates impact an unreasonably large percentage of the system at once? Does the service connect to the right serving instance of dependencies (not a batch system for user requests)? Does it request high enough network QoS for critical remote calls? Does it report errors and degraded responses to central logging? Are all user-visible request failures instrumented, monitored and alerted on?

## Key Takeaways
1. Gate SRE takeover with a PRR: agree on the SLO, analyze with a checklist, fix jointly, train, transfer progressively, and keep improving.
2. Engage at design time for important new or rewritten systems. It is cheaper than unwinding a launched design.
3. Use dark launches and SRE-recommended libraries and controls to make launches smooth.
4. Treat disengagement as success when a service is reliable enough to stay with dev.
5. Encode production best practices in shared, per-language frameworks with identical APIs and controls.
6. Move to shared responsibility: SRE owns the platform and control systems, dev owns business-logic on-call.
7. Staff platform teams by platform need, not by service count.

## Connects To
- **Ch 1 (Introduction)**: dev demand for SRE deliberately exceeds SRE bandwidth.
- **Ch 4 (SLOs)**: SLO/SLA set during the Engagement phase.
- **Ch 21–22 (Handling Overload / Cascading Failures)**: load shedding and overload control as framework modules.
- **Ch 27 (Reliable Product Launches)**: LCE consultation, launch patterns, dark launches.
- **Ch 28 (Accelerating SREs to On-Call)**: the PRR Training phase.
- **Ch 31 (Communication and Collaboration)**: early design collaboration, DFP→F1.
- **External, microservices**: they increase service cardinality and the demand for low deployment lead time.
