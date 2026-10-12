# Chapter 9: Planning a Release

## Core Idea
A release plan answers "when?" and "what priority?", then uses **velocity** to convert total story points into a number of iterations, allocating the highest-priority stories into successive iteration "piles" — an approximate forecast (5–7 iterations), never a fixed date.

## Frameworks Introduced
- **Release planning sequence**:
  - When to use: start of a release, ideally from a product roadmap (Beck's "themes").
  - How: (1) ask when the release is wanted (prefer a date *range*); (2) have the customer prioritize all stories; (3) estimate each story (points already on cards); (4) determine velocity; (5) total points ÷ velocity = number of iterations; (6) fill iterations with highest-priority stories until points are exhausted.
- **MoSCoW prioritization (DSDM)**:
  - How: classify stories as **Must have** (fundamental), **Should have** (important but has a short-term workaround; mandatory if no time pressure), **Could have** (droppable if time runs out), **Won't have this time** (deferred to a later release).
- **Customer prioritizes by value + risk, with developer input**:
  - How: customer sorts into a *precise order* (1st, 2nd, 3rd…), not high/med/low buckets. Inputs: technical factors (risk a story can't be done as desired; impact on other stories if deferred) and customer factors (broad-base desirability, importance to a few key customers, cohesiveness with other stories). On disagreement, the customer wins — every time — but cannot prioritize without dev estimates.
  - Why it works: "juicy bits first" (Gilb) lets the team release early and defer infrastructure, while still elevating genuinely high-risk stories enough to learn feasibility.
- **Estimating initial velocity** (three ways): (1) use historical values (best, but rarely available); (2) run one initial iteration and measure; (3) take a guess — for a 1-ideal-day point, expect velocity ≈ ⅓ to ½ of developer-days per iteration.

## Key Concepts
- **Theme / product roadmap (Beck)**: main focus areas for upcoming releases.
- **Velocity**: points completed per iteration; the unit→calendar converter.
- **Cost changes priority**: learning a story is expensive can lower the customer's priority for it.
- **Mixed-priority story**: a story whose parts deserve different priorities — split it.
- **Infrastructural/nonfunctional story**: risky non-feature need (performance, tiering) that may need a story to be prioritized at all.
- **Iteration length**: typically 1–4 weeks; err short.

## Mental Models
- Fix the date, flex the scope: iterative process makes dates easy and content hard to pin, so start with a date range for flexibility.
- "Cost changes priority": always give the customer the estimate before she prioritizes (the Enter-vs-Tab key story dropped once it cost a person-week instead of hours).
- Split to un-stick prioritization: if a story can't be prioritized, its parts have mixed value — split it (search by author/title vs. publication/date vs. combined).
- Developers must *resist* steering infrastructure/architecture higher than warranted, but should flag deferred work that gets much costlier later (e.g., adding a middle tier; the "install locally vs. separately" story was invented to give 3-tier capability a priority).
- Don't over-trust the plan: say "ready in ~5–7 iterations," not "done June 3"; reset expectations each iteration.

## Reference Tables
MoSCoW rules (DSDM):

| Category | Meaning |
|---|---|
| Must have | Fundamental to the system |
| Should have | Important; short-term workaround exists (mandatory if no time limit) |
| Could have | Droppable if time runs out |
| Won't have this time | Desired but deferred to a later release |

Initial-velocity guess example: 6-person team × 2-week (10-day) iteration = 60 developer-days → plan velocity ≈ 20–30 points.

## Worked Example
Project totals 100 story points; estimated velocity 20 points/iteration → 100 ÷ 20 = 5 iterations. The customer and developers collaboratively pull the top-priority 20 points into iteration 1, the next 20 into iteration 2, and so on until all stories are allocated (release plan = stories piled by iteration, communicated via wall columns, sorted spreadsheets, photocopied cards, or trivial Gantt charts). Story Card 9.1 shows estimates already written on cards ("Estimate: 3 days") so the customer prioritizes by value relative to cost.

## Key Takeaways
1. Release planning needs two inputs first: a (preferably ranged) target date and the customer's relative priorities.
2. Customer prioritizes into a precise order, using value + risk and developer estimates; on conflict the customer decides.
3. Use MoSCoW to avoid endless high/medium/low debates.
4. Convert points to calendar time via velocity; estimate initial velocity from history, a trial iteration, or a guess (⅓–½ of developer-days).
5. Split mixed-priority stories; let cost reshape priority.
6. Developers flag costly-to-defer infrastructure but must not inflate technical priorities.
7. Treat the plan as an approximation and continuously re-estimate.

## Connects To
- **Ch 8 (Estimating)**: supplies the story points and velocity this plan consumes.
- **Ch 10 (Planning an Iteration)**: refines each iteration pile into tasks at iteration start.
- **Ch 11 (Velocity)**: measured velocity recalibrates the release plan over time.
