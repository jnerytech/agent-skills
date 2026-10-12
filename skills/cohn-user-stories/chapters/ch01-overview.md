# Chapter 1: An Overview

## Core Idea
A user story is a short description of functionality valuable to a user or purchaser, deliberately kept thin on the card because its real substance lives in conversation and in acceptance tests. Software requirements is fundamentally a communication problem, and stories spread decision-making across the whole project instead of front-loading it.

## Frameworks Introduced
- **The 3 Cs of a Story (Ron Jeffries)**: a story is made of three aspects — **Card**, **Conversation**, **Confirmation**.
  - When to use: every story, always; it defines what a story *is*.
  - How: write a one-sentence reminder on the **Card**; flesh out details in **Conversation** between customer and developers at the time it matters; record agreement as **Confirmation** = acceptance tests (often on the card's back).
  - Why it works: cards "represent requirements rather than document them" (Rachel Davies). Failure mode: treating the card as a contract ("I said so right there") — stories are not contractual obligations.
- **Story-driven workflow**: write stories → developers estimate (story points) → customer prioritizes → plan release/iterations → develop → acceptance test.
  - When to use: any agile process (XP, Scrum, agile UP, home-grown).
  - How: story-writing workshop produces initial set; pick a fixed iteration length (1–4 weeks); sort prioritized stories into iteration "piles" capped at estimated **velocity**; adjust each iteration as real velocity emerges.

## Key Concepts
- **User story**: a description of functionality valuable to a user or purchaser of the system.
- **Card / Conversation / Confirmation**: the written reminder / the detail-fleshing dialogue / the tests that prove completion.
- **Epic**: a story too large to be useful; split into smaller stories before working on it.
- **Customer team**: those who ensure the software meets users' needs — may include testers, a product manager, real users, interaction designers.
- **Developer team**: those who build and estimate the software.
- **Velocity**: amount of work (story points) developers complete per iteration; first estimate is always wrong and gets corrected by actuals.
- **Story points**: relative measure of size/complexity; a 4-point story is expected to take ~twice a 2-point story.
- **Release vs. iteration**: a release = one or more iterations; release planning balances timeline against desired functionality; iteration planning selects stories for one iteration.
- **Acceptance test**: verification that a story works exactly as the customer team expected.

## Mental Models
- Think of the card as a **promise to have a conversation**, not a frozen spec — details are deferred until "the point when they become important."
- Use **resource allocation as a shared problem**: when either business or developers dominate communication, the project loses (mandated dates vs. jargon-driven scope).
- Treat planning as **decisions made often on the information at hand**, not one all-encompassing up-front plan — you cannot draw a perfect PERT chart for software.
- Think of acceptance-test reminders as the teacher answering "How long does it have to be?" — they tell developers when they are *done*.

## Reference Tables
Release planning by piling stories into iterations capped at velocity (velocity = 13):

| Iteration | Stories | Story Points |
|-----------|---------|--------------|
| 1 | A, B, C | 13 |
| 2 | D, E, F | 12 |
| 3 | G, H, J | 12 |
| 4 | I | 5 |

Note: lower-priority Story J (2 pts) was chosen over higher-priority Story I (5 pts) for iteration 3 because I would not fit. Alternative: split I into Y (3) + Z (2) so Y rides in iteration 3.

## Worked Example
BigMoneyJobs job site. Initial card (front):
> "Users can view information about each job that is matched by a search."
> *Marco says show description, salary, and location.*

Back of the same card (acceptance-test reminders, short and incomplete):
- Try it with an empty job description.
- Try it with a really long job description.
- Try it with a missing salary.
- Try it with a six-digit salary.

The epic "A user can search for a job" is split into: search by attributes (location, salary, title, company, date posted); view info for each matched job; view detailed company info. It is *not* split further into "view a job description / view salary range / view location" — those are conversation details, not stories.

## Key Takeaways
1. Keep the card thin; push detail into conversation and tests, not numbered "4.6.1"-style sub-requirements.
2. Write stories in the language of the business so the customer can value and prioritize them — "the software will be written in C++" is not a story (users don't care).
3. Have the **customer team write the stories**: they speak business language and are the product visionaries who must prioritize and later flesh out detail.
4. Prioritize by value to the organization, but only ever relative to cost (the developers' estimate).
5. Write acceptance tests early in the iteration — they surface assumptions and remind developers of forgotten cases (e.g., expired credit cards).
6. If a story won't fit an iteration, split it; if a story is too large to work with, it's an epic — defer detail until just before development.

## Connects To
- **Ch 2 (Writing Stories)**: how to size, split, combine, and add the right level of detail; introduces INVEST.
- **Ch 6 (Acceptance Testing)**: expands the Confirmation/test side of the 3 Cs.
- **Ch 9–10 (Planning Releases/Iterations)**: the velocity-and-piles mechanics.
- **Extreme Programming / Scrum**: the iterative processes stories were designed to feed.
