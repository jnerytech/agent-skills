# Chapter 4: Prioritizing and Estimating User Stories

## Core Idea
Prioritization focuses the team on the most valuable stories first; estimation approximates the effort to deliver them. Pick a prioritization technique that matches your product's goals, and estimate with *relative* sizing rather than fixed hours.

## Frameworks Introduced
- **MoSCoW prioritization**: classify each story as Must Have / Should Have / Could Have / Won't Have.
  - When to use: clear "must-haves" vs "nice-to-haves" are distinguishable; constraints on time, budget, or resources.
  - How: Must Have = critical, no compromise, in-timeframe; Should Have = important but a workaround exists, can slip to a later release; Could Have = nice-to-have, droppable; Won't Have = not feasible/aligned, removed from backlog.

- **Value-based prioritization**: rank stories by assigned business value.
  - When to use: maximizing value/ROI when many features compete.
  - How: (1) identify business objectives, (2) define metrics (financial like revenue/cost savings/churn, or non-financial like satisfaction/engagement), (3) assign each story a value vs those metrics, (4) sort backlog high-to-low.

- **WSJF (Weighted Shortest Job First)**: economic prioritization by cost of delay over size.
  - When to use: maximize economic value, prioritize highest ROI, minimize waste.
  - How: `WSJF = (Business Value + Opportunity Enablement + Time Criticality + Risk Reduction) / Job Size`. Score the four numerator factors, estimate Job Size, compute, sort high-to-low.

- **RICE**: numeric framework from Intercom — Reach, Impact, Confidence, Effort.
  - When to use: impact and reach are decisive (driving adoption or revenue).
  - How: score each factor 1–10, then combine (book: "scores are multiplied together" — note Reach×Impact×Confidence with Effort in denominator is the canonical Intercom form). Higher total = higher priority.

- **Kano model**: categorize needs by the satisfaction they produce (Noriaki Kano, 1980s).
  - When to use: focusing on customer satisfaction/delight and market differentiation.
  - How: sort stories into Basic needs (expected, no extra value), Performance needs (more is better), Delight needs (unexpected "wow"). Delight = highest priority, then Performance; Basic is necessary but not prioritized.

- **Story points**: relative effort unit capturing complexity, risk, uncertainty.
  - When to use: Agile contexts valuing flexibility over fixed plans.
  - How: assign each story a relative size, commonly on the Fibonacci sequence (1, 2, 3, 5, 8, 13…) vs other backlog stories; not time-based.

- **Ideal days**: estimate the working days a story needs assuming zero interruptions.
  - When to use: fixed-timeline products needing a time-based estimate.
  - How: estimate uninterrupted days, factoring velocity, resources, dependencies. More accurate on time, slower to produce.

## Key Concepts
- **Cost of delay**: economic loss from not delivering a work item sooner; the driver behind WSJF.
- **Job size**: relative effort/duration of a work item — the WSJF denominator.
- **Velocity**: amount of work (story points) a team completes per sprint, used to forecast.
- **Cycle time**: time to complete a story from work-start to finish.
- **Lead time**: time from a story entering the backlog to being marked complete.
- **Throughput**: number of stories completed in a given period; aids sprint capacity planning.
- **Dependencies**: when one story can't finish until another does (e.g. a required DB migration).
- **#NoEstimates**: movement favoring delivering small value increments over investing in estimates.
- **T-shirt sizing**: relative estimation in sizes XS/S/M/L/XL.
- **Bucket system**: categorizing features into effort "buckets."

## Mental Models
- Use **MoSCoW** when stakeholders argue about scope and you need a shared, blunt must/should/could line under a deadline.
- Use **WSJF or RICE** when you must defend ordering with numbers (economics, reach, impact) to stakeholders.
- Use the **Kano model** when the product is commoditized and you need delighters to differentiate, not just more basics.
- Use **story points** when the timeline is flexible and uncertainty is high; use **ideal days** when the deadline is fixed and time-accuracy matters more than adaptability.

## Anti-patterns
- **Estimating in hours / committing to fixed timelines**: invites treating estimates as promises; relative sizing (points, ideal days) avoids the false precision trap.
- **Over-investing in up-front estimation**: time-consuming and often inaccurate given inherent uncertainty — the #NoEstimates critique; can be counterproductive to iterative delivery.
- **Dropping all estimates blindly (#NoEstimates downside)**: makes large-scale resourcing, budgeting, and stakeholder progress-communication hard, risking delays and dissatisfaction.
- **Treating priorities/estimates as set-in-stone**: they must be revisited and refined as the product evolves and actuals come in.
- **Ignoring dependencies and complexity when estimating**: hidden blockers and required skill levels silently inflate effort.

## Reference Tables

### Prioritization technique selector
| Technique | Best suited for |
|---|---|
| MoSCoW | Clear must-haves vs nice-to-haves; time/budget/resource constraints |
| Value-based | Maximizing value/ROI among many competing features |
| RICE | When reach and impact are essential (adoption, revenue) |
| Kano | Customer satisfaction/delight and market differentiation |
| WSJF | Maximizing economic value; highest ROI, minimal waste |

### MoSCoW categories
| Category | Meaning |
|---|---|
| Must Have | Critical; no compromise; must ship in timeframe |
| Should Have | Important, not critical; workaround exists; can defer |
| Could Have | Nice-to-have; droppable without hurting vision |
| Won't Have | Not feasible/aligned; removed from backlog |

### Kano need types
| Need | Effect on satisfaction |
|---|---|
| Basic | Expected; absence dissatisfies, presence adds little |
| Performance | Incremental value; more is better |
| Delight | Unexpected "wow"; strong emotional differentiation |

## Worked Example
**WSJF on an e-commerce backlog (simplified to user value ÷ size).** The team assumes every story takes one sprint (two weeks) and costs the same, so Job Size is constant. They score user value 1–10:

| Story | User value | WSJF (value ÷ size) |
|---|---|---|
| Add to cart/checkout | 9 | 4.5 |
| Search functionality | 8 | 4.0 |
| View product details | 7 | 3.5 |
| Customer order management | 6 | 3.0 |
| Account creation/management | 5 | 2.5 |
| Product inventory/pricing mgmt | 3 | 1.5 |

Dividing each value by the (equal) estimated size yields the WSJF score, producing the delivery order top-to-bottom: checkout → search → product details → order management → account management → inventory. Lesson: with size held constant, highest-value-per-effort ships first.

## Key Takeaways
1. Choose the prioritization technique by goal — MoSCoW for scope cuts, Value/WSJF/RICE for economics, Kano for differentiation — and combine them when useful; they aren't mutually exclusive.
2. Estimate with relative sizing (story points on Fibonacci, or ideal days), never raw hours, to avoid false commitments.
3. Always weigh complexity, dependencies, and uncertainty (build in contingency) when sizing a story.
4. Track cycle time, lead time, and throughput to ground future estimates in real historical data.
5. Run prioritization/estimation as a cross-functional exercise: Product Owner, dev team, Scrum Master, stakeholders, UX/UI, domain experts.
6. Revisit and refine priorities and estimates regularly; treat them as planning tools, not promises.
7. Know the #NoEstimates trade-off: less estimation overhead and deadline pressure, but harder large-scale planning and stakeholder communication.

## Connects To
- **Ch 3**: well-formed, INVEST-style stories are the units you prioritize and estimate here; vague stories resist both.
- **Ch 5 (Working with Stakeholders)**: prioritization and estimation are collaborative acts — the next chapter covers engaging the stakeholders who set value and consume timelines.
