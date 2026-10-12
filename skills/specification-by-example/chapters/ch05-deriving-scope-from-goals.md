# Chapter 5: Deriving scope from goals

## Core Idea
Scope is a solution, not a given — successful teams refuse to passively accept requirements-as-tasks and instead push back to the underlying business goal, then collaboratively derive scope (and a better, cheaper solution) from that goal. Building the wrong scope means "the rest is just painting the corpse."

## Frameworks Introduced

- **Have developers provide the 'I want' part of user stories**: Split the standard `As a __ / I want __ / in order to __` so business users own the stakeholder (`As a`) and benefit (`in order to`) parts, while developers own the solution (`I want`) part.
  - When to use: Business users trust the development team (and the team has high-level control of scope).
  - How: Business defines who + why; delivery team firmly takes responsibility for the solution; involve developers and testers in scope discussions; keep solutions anchored to clearly defined goals.

- **Ask how something would be useful**: Instead of taking a technical feature spec, ask for a high-level concrete example of how the feature would help.
  - When to use: You lack high-level control; "why" feels confrontational, especially in large organizations.
  - How: Request a real example of the feature in use → it points at the real problem without challenging anyone's authority. (Gentler replacement for "keep asking why until they mention money.")

- **Ask for an alternative solution**: Ask what the user would do differently / work around if the system did NOT provide this feature.
  - When to use: People still can't articulate value even after you ask for a usefulness example.
  - How: Elicit the manual workaround → exposes real value and makes the requester reconsider whether their proposed solution is best; starts an options discussion with the delivery team.

- **Don't look only at the lowest level**: Maintain higher-level stories/specs, not just iteration-sized fragments.
  - When to use: Teams over-slicing backlog items to fit sprints lose the big picture and can't tell when a feature is truly done.
  - How: Use a hierarchical (not flat/linear) backlog; capture high-level examples as high-level specifications; low-level tests prove the parts, a high-level acceptance test proves the parts work together.

- **Make sure teams deliver complete features**: Reorganize component teams into feature teams that deliver end-to-end.
  - When to use: Large multisite projects where work is split by component (e.g., domain layer vs UI).
  - How: Restructure so each team owns a full feature; removes duplication, repetition, and rework; lets teams discuss complete expected outputs with users. (See Feature Team Primer.)

## Key Concepts
- **Business goal**: The real outcome/value sought (e.g., "stop losing time merging databases").
- **Scope**: A high-level chosen solution (use cases, user stories, backlog items) — already implies a solution and should be derived, not inherited.
- **Solution**: The concrete implementation; the lowest of the three levels.
- **Challenging requirements**: Reactively questioning given stories — better than passive, but inferior to proactively co-creating the right stories.
- **Understand 'why' and 'who'**: Evaluating a suggested solution by who needs it and why, applied even at the high scope level.
- **Report-first / outputs-first**: Start from expected system outputs to discover goals and engage business users early.
- **Minimum Marketable Features**: Denne & Cleland-Huang's value-driven prioritization unit (Software by Numbers).

## Mental Models
- Use **goal-level prioritization** (dollar value per feature) when business users can attach numbers — prioritizing features/goals beats prioritizing low-level stories or tasks.
- Use **outputs as the starting point** when goals are hard to pin down — analyzing why outputs are required leads you back to the goals, and users only truly engage when they see results.
- Use **"how would this be useful"** instead of **"why"** when in a large org or a confrontational setting, to avoid putting people on the defensive.
- Use a **hierarchical backlog** when slicing stories small — so a higher-level acceptance test still defines "done."

## Anti-patterns
- **Customer-is-always-right / requirements set in stone**: Blindly implementing suggested solutions; you build the wrong thing efficiently.
- **Treating scope as someone else's job**: Passing responsibility for scope to business users who have never designed software (Brooks: deciding what to build is the hardest part).
- **Building data-in/process-flow first, reports last**: Users engage only at the visible output stage → causes rework.
- **Estimating individual stories**: Once everything is sized 1–3 the numbers are meaningless; measure cycle time instead.
- **Splitting only to the lowest level**: You can't tell from the backlog whether the whole feature actually works.

## Worked Example
Peter Janssens (iLean) owned a tool storing local traffic-sign data — a simple Access database that grew to cover most countries, with one data collector per country using local copies that were occasionally merged. To fix painful merges, they decided to build an online web application: four months of contacting suppliers and comparing bids, a selected bid of ~100,000 euros.

The day before go/no-go, an engineer refused to accept the stated solution ("we need a web solution for the central database") and instead probed the problem: "your problem is actually that you need a single source to work on because you're losing time merging" — yes. Then the **'who'** question: how many users? Ten people, one per country group, editing data that changes only once or twice a year (on average one user a month). The real problem was merging, not volume or concurrency.

The engineer put the single Access database on a Citrix (remote desktop) server by the next day. Cost: nothing. A five-month, six-figure project evaporated because someone understood the **why** (eliminate merge loss) and the **who** (ten infrequent users) before accepting the implied web-app scope. Rob Park's insurance team shows the prioritization side: a feature like "Deliver proof of insurance as PDF for 14 states" was costed by realizing 25% of calls dealt with proof-of-insurance cards — putting a dollar value behind the feature so business could prioritize at the goal level.

## Key Takeaways
1. Requirements are usually solutions in disguise; push back to the real problem before building (the F-16 reached its goal — escape combat — via agility, not the requested Mach 2.5).
2. Apply 'why' and 'who' at the scope level, not just the story level — it can redirect a whole project.
3. Start from expected outputs/reports to surface goals and keep business users engaged, avoiding late rework.
4. Prioritize and (lightly) estimate at the goal/feature level with dollar values; skip estimating individual stories and measure cycle time.
5. When you have control and trust, let developers own the 'I want' solution part while business owns who + why.
6. Without high-level control you can still influence scope: ask how it'd be useful, ask for an alternative/workaround, keep higher-level stories, and form feature teams.
7. Investigate emerging techniques to derive scope from goals: feature injection, effect mapping, user story mapping.

## Connects To
- **Ch 4**: Initiating the change — deriving scope from goals is one of the most controversial, least-adopted key patterns and demands collaborative culture.
- **Ch 6**: The high-level "examples of how a feature is useful" become the raw material for specifying with examples / collaborative specification workshops.
