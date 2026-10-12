# Chapter 11: Measuring and Monitoring Velocity

## Core Idea
Velocity is the story points of *completed* stories per iteration; track planned vs. actual velocity and burndown charts to detect plan deviations early — but never count partial stories, never use actual hours, and never retroactively change a completed story's points.

## Frameworks Introduced
- **Measuring velocity**:
  - When to use: end of every iteration.
  - How: sum the (pre-iteration) story points of stories that *finished* (passed acceptance tests). Exclude partially completed stories entirely.
  - Why: percent-done is hard to judge; avoids false precision (43.8); incomplete stories deliver no value and hide complexity in the last 10%; needing partials means stories are too big or teamwork is lacking.
- **Planned vs. actual velocity chart** (Fig 11.1): graph both per iteration; don't react to one or two early iterations (velocity is volatile early — wait 2–3 iterations).
- **Cumulative story-point chart** (Fig 11.2): plot total points completed through each iteration; reveals whether an early lead has eroded (needed alongside velocity to judge release outlook).
- **Iteration burndown chart** (Fig 11.3/11.4): plot story points *remaining* at the end of each iteration; reflects both completed work AND added/changed scope — but does NOT show team speed (use velocity/cumulative charts for that).
- **Daily burndown chart** (Fig 11.5/11.6): during an iteration, plot *hours remaining* per day; each member updates hours-remaining on a shared whiteboard.

## Key Concepts
- **Velocity**: completed story points per iteration.
- **Net progress**: completed − changed-estimate increases − new-story points.
- **Burndown chart**: work remaining over time (story points by iteration, or hours by day).
- **Hours remaining (not expended)**: daily charts track work *left*, not effort spent.
- **No retroactive re-scoring**: a story estimated at 4 but really 7 still contributes 4; use the lesson on *future* estimates only.
- **Defects per story point**: track to ensure velocity gains aren't bought with bugs.
- **Big visible charts**: post large in common areas (e.g., taped axes on whiteboards).

## Mental Models
- Count only finished stories: it's far easier to forgo half a 1-point story than to fairly value a 12-point partial; chronic partials signal oversized stories or weak teamwork ("all-for-one" beats everything-90%-done).
- A burndown shows distance left, not speed — don't yell at a team whose line went *up* (115→120); they may have completed 90 points while the customer added 95. Read speed from velocity/cumulative charts.
- Track hours *remaining*, not *expended*: what matters is effort left; expended hours invite micromanagement feelings and imprecision. Programmers must feel as free to *raise* a remaining estimate as to lower it.
- Add new tasks mid-iteration only for forgotten work needed by an already-included story — never to smuggle in new scope (that goes to the next planning session).

## Reference Tables
Project progress & scope change over four iterations (Table 11.2). Net progress = completed − changed estimates − new stories:

| | Iter 1 | Iter 2 | Iter 3 | Iter 4 |
|---|---|---|---|---|
| Points at start of iteration | 130 | 113 | 78 | 31 |
| Completed during iteration | 45 | 47 | 48 | 31 |
| Changed estimates | 10 | 4 | -3 | — |
| Points from new stories | 18 | 8 | 4 | — |
| Points at end of iteration | 113 | 78 | 31 | 0 |

Daily-tracking whiteboard snippet (Fig 11.6) — last columns are successive hours-remaining:

| Task | Who | Est | Updated |
|---|---|---|---|
| Create HTML page | Thad | 2 | 0 |
| Read search fields from HTML form | Thad | 2 | |
| Create better sample data | Mary | 2 | 4 |
| Write servlet to perform search | Mary | 4 | |
| Generate results page | Thad | 2 | |

## Worked Example
The Table 11.2 team planned ~45 points/iteration over 3 iterations from 130 points. Iteration 1: completed 45, but raised unstarted estimates by 10 and the customer added 18 in new stories → net progress 45 − 10 − 18 = 17, leaving 113. The slope already showed three iterations wouldn't suffice, so they agreed to run four. Iteration 2: 47 − 4 − 8 = 35 net (→78 left). Iteration 3: estimates *dropped* 3, so 48 + 3 − 4 = 47 net (→31 left). Iteration 4: completed the final 31 → 0. The burndown's post-iteration-1 slope made the overrun obvious early. In Fig 11.6, "Create HTML page" went 2→0 (done) while Mary *raised* "create better sample data" 2→4 — only current remaining effort matters.

## Key Takeaways
1. Velocity = points of *finished* stories (acceptance-tests-passing); never count partials.
2. Don't predict trends from one or two iterations — early velocity is volatile.
3. Never retroactively change a completed story's points; apply the lesson to future estimates instead.
4. Use planned-vs-actual + cumulative charts to read speed; burndown charts show remaining work and absorb scope changes but hide speed.
5. Daily burndown tracks hours *remaining*, not expended; everyone keeps the whiteboard current.
6. Add mid-iteration tasks only for forgotten in-scope work; watch defects/point so speed isn't bought with bugs.
7. Make all charts big and visible.

## Connects To
- **Ch 8 (Estimating)**: velocity is the predictor justified by the Central Limit Theorem.
- **Ch 9 (Planning a Release)**: measured velocity recalibrates the release forecast.
- **Ch 10 (Planning an Iteration)**: the whiteboard task hours feed the daily burndown.
