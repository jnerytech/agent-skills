# Chapter 8: Estimating User Stories

## Core Idea
Estimate stories in relative **story points** rather than calendar time, derive estimates collectively as a team via an iterative (Wideband Delphi / planning-poker-style) process, and let **velocity** convert points into duration — precision of any single estimate doesn't matter.

## Frameworks Introduced
- **Story points**: a relative measure of size/complexity/effort, defined by each team as it sees fit.
  - When to use: estimating any story or epic.
  - How: each team picks a unit (Cohn prefers ~one ideal day of work; could be ideal week, or pure complexity). Estimate everything the story needs (testing, talking to customer, automating acceptance tests).
  - Why it works: ideal time is easier than elapsed time (you ignore meetings, email, etc.) and converts to calendar time later via velocity; "your points ≠ my points."
- **Iterative team estimation (Wideband Delphi, a.k.a. planning poker)**:
  - When to use: every estimation session, with customer + the developers who'll do the work.
  - How: (1) customer reads a story; developers ask questions, customer answers; (2) each developer privately writes an estimate on a card; (3) reveal simultaneously; (4) high and low estimators explain their thinking (not an attack — surface hidden assumptions); (5) discuss a few minutes; (6) re-estimate and reveal again; repeat (rarely >3 rounds) until estimates converge "reasonably," not exactly.
  - Failure mode: lone-expert estimates lose the team's collective knowledge and aren't owned by the team.
- **Triangulation**: estimate a story by comparing it to already-estimated stories.
  - How: a 4-point story should be ~twice a 2-point story; a 3-pointer sits between them. Pin cards on a wall in columns labeled by points (Fig 8.1) and check each new card against its column-mates ("about the same?").

## Key Concepts
- **Ideal time vs. elapsed time**: ideal = uninterrupted work; elapsed = wall-clock including interruptions.
- **NUTs (Kerievsky)**: "Nebulous Units of Time" — wry label for story points.
- **Velocity**: number of story points a team completes per iteration.
- **Central Limit Theorem rationale**: summing many independent estimates yields an approximately normal distribution, so one iteration's velocity predicts future ones.
- **Pair-programming neutrality**: pairing doesn't change point estimates, only the velocity number.
- **Decreasing precision with size**: large estimates carry less real precision.

## Mental Models
- Estimate as a *team*, own estimates as a *team*: nobody knows yet who'll do the work, and group estimates beat individual ones. Customer may answer questions but may NOT estimate or editorialize.
- "Everything takes four hours": include all incidental work (testing, customer talk, acceptance-test automation) or you've planned the couch trip as one hour.
- Use a constrained scale to avoid false precision — arguing 2 vs 3 points (50% more) is meaningful; arguing 7 vs 8 is not.
- Don't pad, don't give in to pressure for low estimates; aim for consistency (all 2-pointers feel alike) so velocity smooths out bias.

## Reference Tables
Recommended constrained story-point scale (larger = less known):

| Allowed values |
|---|
| ½, 1, 2, 3, 5, 8, 13, 20, 40, 80 |

For an epic you decide "40 or 80," not "79 or 80."

## Worked Example
Planning-poker round on a story: developers reveal cards; estimates differ widely (good news). The high estimator: "to test this we'll need a mock database object — maybe a day — and our compression algorithm may not be memory-efficient enough." The low estimator: "I figured we'd store it in an XML file, easier than a DB; I hadn't considered the extra data." Brief discussion, customer clarifies, a note is jotted, cards may be added. Re-vote: cards now read 4, 4, 4, 3. Cohn simply asks the low estimator if she's OK with 4 — converged. Reasonableness over absolute precision.

Velocity illustration: project estimated at 300 points; team projects 30 pts/iteration → 10 iterations. After iteration 1 they actually complete 50 → six iterations total, and they *should* keep planning on 50 if (a) nothing unusual (overtime/extra staff) skewed it, (b) estimates were generated consistently, (c) stories were independent.

## Key Takeaways
1. Story points are relative (size/complexity/effort), not time; each team defines its own unit.
2. Estimate as a team via iterative reveal-explain-revise rounds (planning poker); the team owns the estimates.
3. Triangulate against existing estimates and pin cards by size to keep the point-meaning stable.
4. Prefer ideal time over elapsed time; convert to calendar time later through velocity.
5. Pairing affects velocity, not estimates; sums of split stories/tasks need not equal the original.
6. Don't pad; use a constrained scale (½,1,2,3,5,8,13,20,40,80) so precision tracks knowledge.

## Connects To
- **Ch 9 (Planning a Release)**: velocity turns total points into number of iterations.
- **Ch 10 (Planning an Iteration)**: tasks (vs. stories) are estimated in ideal hours and owned by individuals.
- **Ch 11 (Velocity)**: measured velocity recalibrates these estimates over time.
