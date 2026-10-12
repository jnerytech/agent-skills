# Chapter 15: Using Stories with Scrum

## Core Idea
Although stories originated in Extreme Programming, they integrate cleanly into Scrum: constraining the *product backlog* to user stories makes prioritization, sprint planning, sprint review, and the daily scrum all easier, because every backlog item then expresses customer value.

## Frameworks Introduced
- **Story-constrained product backlog**: require every product backlog item to be a user story describing value to a user or product owner (no raw technical tasks, issues, or defects).
  - When to use: any Scrum project adopting stories.
  - How: stock the backlog by first identifying user roles, then writing stories per role.
  - Why it works: with all items in business terms, the product owner can trade one feature for another; failure mode avoided is a "random collection" of tasks the team can't demo or prioritize.
- **Scrum sprint cycle**: 30-day sprints; pull from prioritized product backlog → sprint backlog of tasks → daily scrum → potentially shippable increment → sprint review.
  - How: sprint planning (up to a day) sets a *sprint goal*; team commits to the work it can complete; only the team adds to the sprint once started.

## Key Concepts
- **Sprint**: a thirty-day iteration.
- **Product backlog**: master prioritized list of all desired functionality; reprioritizable any time by the product owner.
- **Sprint backlog**: tasks the team has committed to for the current sprint; only the team may add to it mid-sprint.
- **Product owner**: the Scrum equivalent of XP's customer; owns and prioritizes the product backlog.
- **ScrumMaster**: project-manager role recast as servant-leader/facilitator who removes obstacles and enforces Scrum's few rules.
- **Sprint goal**: short statement of the sprint's aim; success is assessed against it, not item-by-item.
- **Daily scrum**: ≤15-minute standup; each member answers: what did you do yesterday? what today? what obstacles?
- **Potentially shippable product increment**: coded, tested, usable software produced each sprint.
- **Sprint review**: informal end-of-sprint demo of working software (no PowerPoint; ≤2 hours prep).
- **Iterative vs. incremental**: refining the whole through successive passes (sculptor roughs then details) vs. finishing one complete piece at a time (sculptor finishes the nose, then eyes); Scrum is both.

## Mental Models
- Product owner = XP customer; ScrumMaster ≈ project manager but leads/serves rather than directs.
- Self-organizing team: no "Mary codes, Bill tests" edict, so role labels (programmer/architect/tester) are dropped; all work is owned collectively.
- Commitments at the daily scrum are made to peers, not to the manager.
- Keep the daily scrum on the three questions — defer design/issue resolution to a follow-up meeting with just the people needed.

## Anti-patterns
- **Technology-driven backlog items** (e.g., "Refactor the Login class to throw an exception"): hard to prioritize and demo; reframe as customer value.
- **Daily scrum drifting into design/estimates**: don't solve issues or ask "how much time left?" in the standup — it turns the meeting into a numbers grilling; track estimates separately on a whiteboard.
- **Outsiders redirecting the standup**: non-team attendees (even the "Big Boss") may listen but not ask questions.
- **Adding work mid-sprint**: no one (CEO, sales, even the product owner) adds to a started sprint; if change is unavoidable, abort and re-plan.

## Reference Tables
| Scrum element | Role with stories |
|---|---|
| Product backlog | All items are user stories (value to user/PO) |
| Sprint backlog | Stories disaggregated into tasks |
| Product owner | = XP customer; prioritizes backlog |
| ScrumMaster | Servant-leader; removes obstacles |
| Sprint planning | PO describes top stories; team commits, sets sprint goal |
| Sprint review | Stories make "done" easy to demo |
| Daily scrum | Stories keep focus on user intent |

## Worked Example
**Cosmodemonic Biotech case study** (Scrum + stories vs. waterfall on the *same* product). A 100-developer waterfall team had taken 9 months (540 person-months), producing 3,000 use-case pages, 58,000 lines of Java (120 LOC/person-month). The rewrite used Scrum augmented with stories, team ≤7 including PO and ScrumMaster: 12 calendar months but only 54 person-months, 1,400 stories (0 use-case pages), 51,000 lines of Java — 840 LOC/person-month. Same functionality, one-tenth the effort.

## Key Takeaways
1. Stories are XP-born but drop neatly into Scrum as the backlog's content.
2. Constraining the product backlog to value-bearing stories eases prioritization, planning, review, and standup focus.
3. Scrum is both iterative (refine the whole) and incremental (deliver complete pieces); sprints yield potentially shippable increments.
4. Product owner = customer; ScrumMaster leads/serves; teams self-organize and own work collectively.
5. The sprint is protected — only the team adds work once it starts; significant change means aborting and re-planning.

## Connects To
- **Ch 10 (Planning an Iteration)**: disaggregating stories into sprint-backlog tasks.
- **Ch 3 (User Role Modeling)**: stocking the product backlog by role then story.
- **Ch 13**: stories' "right size for planning" is why they fit Scrum planning.
- **Schwaber & Beedle, *Agile Development with Scrum***: external full treatment of Scrum.
