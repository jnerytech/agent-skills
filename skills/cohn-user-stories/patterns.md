# Patterns & Techniques — User Stories Applied (Mike Cohn)

## The Role-Template ("Connextra format")
**When to use**: writing any story so it keeps a concrete user and a reason in view.
**How**: "As a *(role)*, I want *(function)* so that *(business value)*." The "so that" clause is the test of real value — if you can't write it, question the story.
**Trade-offs**: terse and value-focused; the card is a placeholder, never a contract.

## INVEST checklist
**When to use**: writing or reviewing any story.
**How**: test against Independent, Negotiable, Valuable, Estimable, Small, Testable. Each failing letter implies a fix — dependent → combine/re-split; over-specified → strip to a reminder; dev-only value → reframe for users; not estimable → spike; too big → split; vague → add acceptance tests.

## User role modeling (brainstorm → organize → consolidate → refine)
**When to use**: project start, before writing stories — even with on-site users.
**How**: (1) brainstorm role-name cards on a wall, names only, ~15 min; (2) organize spatially so card overlap mirrors role overlap; (3) consolidate — merge equivalents, rip up duplicates and success-irrelevant roles; (4) refine with role attributes. Promote 1–2 vital roles to **personas** (name + backstory + photo, backed by research). Use **extreme characters** sparingly as a creativity probe.
**Trade-offs**: ~1 hour beats 99% of teams' user thinking; over-investing turns a tool into a goal.

## Trawling for requirements
**When to use**: as the mindset for all requirements work.
**How**: make repeated passes with different "mesh" — coarse net for big requirements first, finer nets later — and revisit continuously. Techniques: **user interviews** (default), **questionnaires** (only to prioritize/learn about *existing* stories at scale), **observation** (richest, reveals the need behind the stated need), **story-writing workshops** (fastest high-volume generation).
**Trade-offs**: never catches every requirement; that's expected, not failure.

## Open-ended, context-free questions
**When to use**: interviews and workshops, before drilling into specifics.
**How**: replace "Would you like it in a browser?" with "What would you give up to have it in a browser?"; replace "How fast must searches be?" with "What kind of performance is required?" Where the user goes (and doesn't) is itself signal.

## Low-fidelity prototyping (depth-first)
**When to use**: in a story-writing workshop, to generate stories per role.
**How**: start with an empty box = the main screen, pick a role/persona, ask "what can this role do from here?"; draw a line to a new labeled box per action and write a story. Boxes = components, arrows = links — *not* screens/fields. Throw away within days; keep a parking lot for tangents.

## Working through user proxies
**When to use**: real users are missing or access is limited.
**How**: identify which proxy type(s) you have, anticipate the built-in bias, and combine *different* types so weaknesses offset. Constitute the customer team: add real users → name a project champion (one voice) → determine critical success factors → add proxies whose skills match. When blocked: start a **user task force**, do competitive analysis, release early.
**Trade-offs**: "a real user beats a proxy any time"; developers are usually worse proxies than the proxies.

## Splitting stories
**When to use**: a story is too big to estimate or won't fit an iteration.
**How**: **compound** epic → split along create/edit/delete or data boundaries; **complex** epic → split into a timeboxed **spike** + development story (schedule the spike earlier). Always **slice the cake**: thin vertical slices through every layer, each independently usable — never horizontal "build the form" / "write to DB" splits.
**Trade-offs**: sum of split estimates need not equal the original; frequent splitting *during* iteration planning is a smell — pre-split instead.

## Combining stories
**When to use**: many too-small stories (bugs, minor UI tweaks) clutter planning.
**How**: bundle into one named story of ~half-day to several days; with paper cards, staple under a cover card and plan the bundle as one.

## Two-step acceptance testing
**When to use**: from the first conversation about a story through iteration's end.
**How**: (1) jot test *reminders* on the card back whenever anyone thinks of one; (2) at iteration start turn them into executable tests, before/while coding. Customer-generation questions: What else do programmers need to know? What am I assuming about implementation? When might this behave differently? What can go wrong? Automate with FIT/FitNesse so prior iterations' tests keep passing cheaply.
**Trade-offs**: aim for finding bugs, not coverage; stop when another test stops clarifying.

## Estimating in story points (planning poker + triangulation)
**When to use**: estimating any story with the team that will build it.
**How**: customer reads story → developers question → each privately writes an estimate → simultaneous reveal → high/low explain (surface assumptions, not attack) → discuss → re-vote; rarely >3 rounds, converge "reasonably." Triangulate: pin cards in point-labeled columns and check each new card against column-mates. Use a constrained scale: **½, 1, 2, 3, 5, 8, 13, 20, 40, 80**.
**Trade-offs**: customer answers questions but never estimates; don't pad; precision tracks knowledge.

## Release planning (velocity + iteration piles)
**When to use**: start of a release.
**How**: (1) ask for a target date *range*; (2) customer prioritizes all stories into precise order using value + risk + estimates; (3) estimate stories; (4) determine velocity (history > trial iteration > guess of ⅓–½ developer-days); (5) total points ÷ velocity = iteration count; (6) fill iteration "piles" with highest-priority stories up to velocity. Use **MoSCoW** to avoid high/med/low debate.
**Trade-offs**: say "ready in ~5–7 iterations," never a fixed date; "cost changes priority"; on conflict the customer decides — but only with estimates in hand.

## Iteration planning (disaggregate → accept → estimate)
**When to use**: start of every iteration.
**How**: discuss each prioritized story → disaggregate into tasks → one developer accepts each task → each developer estimates accepted tasks in ideal hours and sums them to detect over-commitment (rebalance, hand off, or drop scope). Add a task only when it's genuinely needed by an in-scope story.
**Trade-offs**: one name per task but ownership stays fluid and team-owned; customer holds priorities steady mid-iteration.

## Measuring & monitoring velocity
**When to use**: end of every iteration; daily within one.
**How**: velocity = sum of *finished* stories' pre-iteration points (exclude partials; never re-score). Track planned-vs-actual + cumulative charts to read speed; iteration burndown for remaining work; daily burndown for hours *remaining*. Make charts big and visible; watch defects/point.
**Trade-offs**: don't trust velocity before 2–3 iterations; a rising burndown means scope grew, not that the team is slow.

## Nonfunctional requirements as constraint cards
**When to use**: a requirement can't be a normal story.
**How**: write it on a card annotated "Constraint"; where possible add an automated test run ≥ daily; estimate at 0 points (it shapes other stories rather than producing its own deliverable).
**Trade-offs**: a few constraints (e.g., "written in Java") aren't worth testing; supplement with other formats (data dictionary) when a card isn't enough.

## Bugs as stories
**When to use**: handling defects in a story-driven plan.
**How**: treat a bug expected to take about as long as a typical story as its own story; staple quick bugs under a cover card and plan the bundle as one.

## Stories with Scrum
**When to use**: a Scrum project adopting stories.
**How**: constrain the product backlog so every item is a value-bearing user story (stock it by role, then story); disaggregate into the sprint backlog; protect the sprint (only the team adds mid-sprint; significant change → abort and re-plan); keep the daily scrum to its three questions.
