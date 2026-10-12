# Chapter 10: Planning an Iteration

## Core Idea
At the start of each iteration the whole team takes release planning one step finer: discuss each prioritized story, disaggregate it into tasks, have an individual accept each task, then individually estimate accepted tasks in ideal hours to confirm no one is over-committed.

## Frameworks Introduced
- **Iteration planning meeting**:
  - When to use: start of every iteration, with the customer and all developers (programmers, testers, others).
  - How (sequence): (1) discuss a story — customer reads highest-priority story, developers ask just enough questions to break it down; (2) disaggregate the story into constituent tasks; (3) one developer accepts responsibility for each task; (4) after all top-velocity-worth of stories are processed, each developer estimates her accepted tasks (ideal time) to check for over-commitment.
  - Why it works: disaggregation is a "short burst of just-in-time design" replacing waterfall's up-front design phase, and the group setting surfaces forgotten tasks.
- **Disaggregation guidelines** (no mandatory task size):
  - Separate a task that's particularly hard to estimate (e.g., needs a slow remote VP's approval).
  - Split tasks that different developers could do in parallel (basic vs. advanced search screen).
  - Break out a part if knowing it's done has value (a finished basic-search screen lets DB code connect even if advanced search lags).
- **Accept responsibility + over-commitment check**:
  - How: one name per task (even when pairing). After estimating, each developer sums her hours; if too much (e.g., 53 hrs in a two-week iteration) she may keep-and-hope, ask a teammate to take tasks, or ask the customer to drop/split a story.

## Key Concepts
- **Task**: a constituent unit of work derived from a story; estimated in ideal hours.
- **Disaggregation**: converting a user-valued story into a developer to-do list of tasks.
- **Just-in-time design**: the minimal design implied by breaking stories into tasks.
- **Accepting responsibility**: an individual signs up for a task and ensures it gets done.
- **Fluid commitments**: task ownership shifts during the iteration as work proves easier/harder.
- **"We're all in this together"**: whole-team accountability — no "I finished mine, Tom didn't."
- **Stable priorities mid-iteration**: customer should resist changing priorities once the iteration starts.

## Mental Models
- A story is user-valued functionality, not a to-do list — disaggregate to expose forgotten work (e.g., updating the help system/user's guide) and to let multiple developers share a story, especially late in the iteration.
- Compare uncoded-vs-coded fairly: the customer who wanted to swap a two-thirds-coded search feature for a "better" one was really comparing two *uncoded* ideas; wait to the iteration's end, then she's comparing a working feature vs. a 10-day rewrite — usually not worth it.
- Estimate to confirm, not to plan precisely: tasks should be small enough to estimate reliably; if not, take a best guess and move on.
- One name per task, but ownership is fluid and collective: if you'll finish early, take a teammate's work.

## Reference Tables
Whiteboard task plan for story "A user can search for a hotel on various fields" (Table 10.1):

| Task | Who | Estimate (hrs) |
|---|---|---|
| Code basic search screen | Susan | 6 |
| Code advanced search screen | Susan | 8 |
| Code results screen | Jay | 6 |
| Write & tune SQL for basic searches | Susan | 4 |
| Write & tune SQL for advanced searches | Susan | 8 |
| Document new functionality in help system & user's guide | Shannon | 2 |

## Worked Example
Story "A user can search for a hotel on various fields" is disaggregated into: code basic search screen; code advanced search screen; code results screen; write/tune SQL for basic searches; write/tune SQL for advanced searches; document new functionality in help/user's guide. The documentation task was added even though the story never mentioned docs — the team knew from prior iterations the help system must stay accurate. Developers write their names beside tasks (Table 10.1) and add hour estimates; if velocity is 40 points, stories are processed until ~40 points are covered, then each developer sums her hours to confirm she isn't over-committed.

## Key Takeaways
1. Iteration planning refines only the starting iteration: discuss → disaggregate → accept → estimate.
2. The whole team (incl. customer) attends; disaggregation is collaborative just-in-time design that catches forgotten tasks.
3. Tasks have no mandatory size; split them to ease estimation or enable parallel work.
4. One developer accepts each task (even when pairing), but commitments stay fluid and team-owned.
5. Developers estimate accepted tasks in ideal hours to detect over-commitment, then rebalance or drop scope.
6. The customer should hold priorities steady during the iteration.

## Connects To
- **Ch 9 (Planning a Release)**: consumes the iteration's pile of prioritized stories and velocity target.
- **Ch 8 (Estimating)**: stories use team-owned points; tasks here use individually-owned ideal hours.
- **Ch 11 (Velocity)**: the whiteboard task estimates feed the daily burndown chart.
