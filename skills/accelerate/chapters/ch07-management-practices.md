# Chapter 7: Management Practices for Software
*Authors: Nicole Forsgren, Jez Humble, Gene Kim*

## Core Idea
Lean management practices (WIP limits, visual displays, and feedback from production monitoring) used *together* predict higher software delivery performance, decrease burnout, and foster a generative culture; and external change approval (CAB) slows delivery without improving stability, so it is worse than no approval process at all.

## Frameworks Introduced
- **Lean management (three components, plus lightweight change management)**:
  1. **Limiting work in progress (WIP)**, and using these limits to drive process improvement and increase throughput.
  2. **Visual displays** showing key quality and productivity metrics and the current status of work (including defects), available to both engineers and leaders, with metrics aligned to operational goals.
  3. **Using data from application performance and infrastructure monitoring tools to make business decisions on a daily basis.**
  - When to use: to manage flow in software teams and expose obstacles.
  - How: WIP limits must make obstacles to flow visible *and* teams must remove them through process improvement; displays should share quality, productivity, failure and defect information broadly and accessibly (kanban, storyboards, dashboards).
  - Why it works: WIP limits on their own do **not** strongly predict delivery performance; only in combination with visual displays and a feedback loop from production monitoring to delivery teams or the business is there a strong effect. Failure mode: WIP limits that do not lead to improvements that increase flow are "no good".
  - Outcomes: improved software delivery performance, decreased burnout, more generative culture (Westrum).

- **Lightweight change management**: use a lightweight change approval process based on **peer review** (pair programming or intrateam code review) **combined with a deployment pipeline** to detect and reject bad changes. Applies to code, infrastructure, and database changes.
  - When to use: replacing CAB/manager approval of production changes.
  - Why it works: external reviewers unfamiliar with system internals cannot accurately assess tens of thousands of lines changed by hundreds of engineers against a complex production system. Failure mode of the alternative: **risk management theater**, checking boxes so that "at least we followed the process", adding only delays and handoffs.

- **Segregation of duties without a CAB**: two mechanisms that satisfy both the letter and spirit of the control (e.g., PCI DSS):
  1. Every committed change is reviewed by someone not involved in authoring it (can be same team), before or immediately after commit, with approval recorded in a system of record (e.g., approving a GitHub pull request, or a manual pipeline stage right after commit).
  2. Changes reach production only through a fully automated deployment pipeline: committed to version control, validated by the standard build and test process, deployed via pipeline trigger. Auditors get a complete record of which changes went to which environments, their source, tests run, and who approved them and when.

- **Governance role for external risk teams**: outside-team risk managers should monitor delivery performance and help teams improve it via practices known to increase stability, quality, and speed, rather than inspecting individual changes.

## Key Concepts
- **WIP limits**: caps on concurrent work that prevent overburdening (longer lead times) and expose obstacles to flow.
- **Visual displays**: dashboards, kanban boards, storyboards that publicly share quality, productivity, and defect information.
- **Production monitoring feedback loop**: application and infrastructure monitoring data fed back to teams and the business for daily decisions.
- **Change advisory board (CAB)**: external body that approves production changes; associated with lower performance.
- **Peer review**: intrateam code review or pair programming as the change-approval mechanism.
- **Deployment pipeline**: automated path to production that detects and rejects bad changes and creates an audit trail.
- **Risk management theater**: process followed for blame cover, not for actual risk reduction.
- **Segregation of duties**: regulatory control requiring that authors do not approve their own changes.
- **Lean Software Development**: Mary and Tom Poppendieck's adaptation of Toyota's Lean philosophy to software.

## Mental Models
- Think of **Lean management as a system**: the three practices are complementary; any one in isolation yields little.
- Use **peer review plus pipeline** when tempted to add an approval layer: put review close to the code and automation close to production.
- Think of an **external approver as a delay, not a safety net**: it hurts tempo metrics and does not move stability metrics.
- Use **governance over inspection** for central risk teams: steer capabilities and outcomes, not individual changes.

## Anti-patterns
- **WIP limits without improvement**: limiting WIP without using it to expose and remove obstacles to flow.
- **External change approval (manager or CAB)**: negatively correlated with lead time, deployment frequency, and restore time; no correlation with change fail rate; worse than no approval process.
- **Days-or-weeks change processes** layered on top of team-level code review.
- **Assuming segregation of duties requires a CAB or separate ops team**.
- **Manual changes to production** outside the pipeline.
- **Risk management theater**.

## Reference Tables

**Change approval scenarios and findings**

| Scenario | Correlation with software delivery performance |
|---|---|
| 1. All production changes approved by an external body (manager or CAB) | Lower performance |
| 2. Only high-risk changes (e.g., database changes) require approval | Not correlated |
| 3. Rely on peer review to manage changes | Higher performance |
| 4. No change approval process | Higher performance |

**External approval vs. the four key metrics**

| Metric | Correlation with external approval |
|---|---|
| Lead time | Negative (slower) |
| Deployment frequency | Negative |
| Time to restore service | Negative (slower) |
| Change fail rate | No correlation |

**Lean management model (Figure 7.1 / 7.2)**

| Inputs | Outcomes |
|---|---|
| Limit WIP; visual displays; feedback from production monitoring; (lightweight change approvals) | Higher software delivery performance; less burnout; more generative culture |

## Worked Example
**What the WIP and visual-display constructs actually measure.** For WIP, the survey did not just ask whether teams limit WIP and have a process for it; it asked whether WIP limits **make obstacles to higher flow visible**, and whether teams **remove these obstacles through process improvement**, leading to improved throughput. For visual displays, it asked whether dashboards share information, whether kanban or storyboards organize work, whether quality and productivity information is readily available, and whether failures or defect rates are shown publicly. The central dimensions: what information is displayed, how broadly it is shared, and how easy it is to access. A team with a kanban board and WIP caps that never changes its process would score low; a team whose WIP limit exposed a review bottleneck, which it then fixed, and whose defect rate is on a public dashboard, would score high.

## Key Takeaways
1. Implement WIP limits, visual displays, and production-monitoring feedback as a bundle, not piecemeal.
2. Treat every WIP-limit breach as a signal to find and remove an obstacle to flow.
3. Make quality, productivity, and defect data public and easy to access for engineers and leaders.
4. Replace CAB/manager approvals with peer review plus a deployment pipeline for code, infrastructure, and database changes.
5. Satisfy segregation of duties with non-author review recorded in a system of record and pipeline-only production changes.
6. Redeploy central risk/change teams into a governance role that monitors and improves delivery performance.

## Connects To
- **Ch 2**: the four key metrics (lead time, deployment frequency, time to restore, change fail rate) used to evaluate CAB impact.
- **Ch 3**: Lean management leads to a more generative (Westrum) culture.
- **Ch 4**: deployment pipeline and continuous delivery practices.
- **Ch 6**: compliance in regulated contexts handled by automation rather than gates.
- **Ch 8**: Lean product management complements Lean management.
- **Ch 9**: Lean management decreases burnout; leaders limit WIP.
- **Ch 11**: leaders' role in removing roadblocks.
- **Toyota Production System / Lean Software Development (Poppendieck)**: origin of the practices.
- **ITIL change management / CAB**: the traditional approach the findings challenge.
