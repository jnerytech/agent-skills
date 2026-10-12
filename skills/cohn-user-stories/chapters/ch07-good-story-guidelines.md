# Chapter 7: Guidelines for Good Stories

## Core Idea
A collection of practical heuristics for writing stories that are well-sized, end-to-end, user-centered, and free of premature solution detail — so cards stay reminders to converse, not specifications.

> Note: this chapter is the "guidelines" set. Cohn's well-known **INVEST** checklist (Independent, Negotiable, Valuable, Estimable, Small, Testable, by Bill Wake) is introduced in the "Writing Stories" material; the guidelines below are the chapter's concrete operationalization of those qualities.

## Frameworks Introduced
- **Start with Goal Stories**: for each user role, list the goals that role has for using the system; these high-level goals seed lower-level stories.
  - When to use: large projects with many roles where you don't know where to begin.
  - How: take a role (e.g., Job Seeker → "find a job"), break the top goal into sub-goals (search jobs, automate the search, make resume findable, easily apply), then generate stories from those.
- **Slice the Cake (Bill Wake)**: when splitting a large story, make each piece a thin vertical slice through all architectural layers rather than a horizontal technical layer.
  - When to use: a story is too big for one iteration.
  - How: avoid "fill out form" + "write form to DB" (neither is useful alone); instead "submit a resume with basic info" + "submit a resume with full info" — each is end-to-end usable.
  - Why it works: each slice exercises every layer (de-risks late integration surprises) and is independently releasable.
- **Write Closed Stories (Lauesen)**: a story should finish with a meaningful, achievable goal that gives the user a sense of accomplishment.
  - How: replace ongoing "A recruiter can manage her ads" with discrete closed stories (review applicant resumes; change an ad's expiration date; delete a poor-match application).
- **Constraint cards (Newkirk & Martin)**: annotate non-implementable requirements as "Constraint"; don't estimate/schedule them, but tape to wall and write automated tests to enforce.

## Key Concepts
- **Goal story**: high-level story derived from a user role's goal.
- **Slicing the cake**: vertical, full-stack story split.
- **Closed story**: ends at a meaningful, completable goal.
- **Constraint**: a rule to obey (e.g., "support 50 concurrent users"), not a feature to build.
- **Implementation horizon**: how soon a story will be built — drives how finely it's written.
- **Epic**: a large, coarse story to be split closer to implementation.
- **Solution vs. requirement leakage**: embedding UI/implementation detail into a story.
- **Role-template**: "As a (role) I want (function) so that (business value)" — Connextra format.

## Mental Models
- Use "size to the horizon": write near-term stories small enough to schedule; leave distant stories large and imprecise — attention follows urgency.
- Think of UI detail as a contaminant: keep it out as long as possible (story 7.2's print-dialog detail is premature early; a "date widget" story is fine late when UI exists).
- Write for *one* user and in active voice: "A Job Seeker can remove her own resumes" exposes the ownership ambiguity that "Job Seekers can remove resumes" hides.
- The card is a reminder, not a contract: don't number cards (avoid "story 13.1" abstraction), add a short title instead; don't replace the conversation with more text.

## Worked Example
"A Job Seeker can post a resume" is too big for one iteration. The *wrong* split is technical/horizontal:
- A Job Seeker can fill out a resume form. (data isn't saved — useless)
- Information on a resume form is written to the database. (no form — useless)

The *right* split slices the cake vertically:
- A Job Seeker can submit a resume with only basic info (name, address, education).
- A Job Seeker can submit a resume with all info an employer may want.

Separately, "Size to the horizon": only the resume-posting theme gets expanded now (add/edit/remove resume, mark inactive/hidden, view count), while "search jobs," "post job opening," "search resumes" stay as single high-level stories until their turn.

## Key Takeaways
1. Begin with each role's goals; let goals generate stories.
2. Split stories vertically (slice the cake) so every piece is end-to-end useful and de-risks all layers.
3. Prefer closed stories that deliver a sense of completion; balance against "small enough to estimate/schedule."
4. Capture constraints on their own cards and enforce them with automated tests run every iteration.
5. Size stories to their implementation horizon — detailed when near, broad when far.
6. Keep UI out as long as possible; include the user role; write for one user, in active voice.
7. Don't number cards; remember the card's purpose is to prompt a conversation.

## Connects To
- **Ch 8 (Estimating)**: stories must be small enough to estimate; epics get split before estimating.
- **Ch 9 (Planning a Release)**: splitting also enables differential prioritization (mixed-priority stories).
- **Ch 6 (Acceptance Testing)**: constraint cards are enforced via automated acceptance tests.
- **INVEST (external/Bill Wake)**: these guidelines operationalize Independent, Valuable, Estimable, Small, Testable.
