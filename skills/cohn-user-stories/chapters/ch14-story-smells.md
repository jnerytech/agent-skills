# Chapter 14: A Catalog of Story Smells

## Core Idea
A catalog of "bad smells" — observable symptoms that something is amiss in how a project applies user stories — each paired with one or more remedies. Smells are diagnostic indicators, not failures in themselves.

## Frameworks Introduced
- **Smell → symptom → cause → remedy diagnosis**: treat each recurring problem (re-estimating, can't plan, can't prioritize) as a named smell with a known fix.
  - When to use: continuously, as a team self-check; especially during iteration/release planning.
  - How: match the observed symptom to the catalog below, apply the remedy.
  - Why it works: makes drift from story principles visible early; failure mode is ignoring symptoms until planning becomes chronically painful.
- **"If you run out of room, use a smaller card"** (Tom Poppendieck): a forcing function that physically limits detail and pushes detail into conversation.

## Key Concepts
- **Smell**: an indicator that something is amiss; not necessarily a defect, but worth investigating.
- **Goldplating**: developers adding unrequested features or over-implementing a story.
- **Slice of cake**: a story split that spans all application layers (from Ch 7) — the cure for interdependence.
- **Business-value framing**: rewriting technical stories so the customer can see and prioritize their value.
- **Splitting for fit**: legitimately dividing a story so it fits a sprint/velocity — only a smell when it happens *frequently*.

## Mental Models
- Combine first, split later: keep overlapping/dependent small stories merged until the iteration in which they're scheduled forces a split.
- The note card is a design constraint, not a limitation — its small size protects you from over-documentation.
- "Let the customer off the hook": when a customer won't decide, make participation safe and non-threatening rather than demanding accountability.

## Anti-patterns
- **Stories too small**: *Symptom* — frequent re-estimating (estimate swings with implementation order, e.g., save-to-XML vs. save-to-HTML overlap). *Fix* — combine for planning; split only when slotting into an iteration.
- **Interdependent stories**: *Symptom* — can't plan an iteration without dragging in chains of other stories. *Cause* — too small or badly split. *Fix* — combine, or re-split as full "slice of cake" through all layers.
- **Goldplating**: *Symptom* — unplanned features, liberal story interpretation. *Cause* — wanting to "wow," escaping always-producing pressure, leaving a personal mark. *Fix* — daily visibility meetings, detailed end-of-iteration reviews, QA who heard the conversations; self-policing.
- **Too many details**: *Symptom* — gathering detail far ahead; more time writing about stories than talking. *Fix* — smaller cards; value conversation over documentation.
- **UI detail too soon**: *Symptom* — early stories assume specific UI (e.g., "…from the Job Description page"). *Fix* — rewrite without UI presumption ("When viewing details about a job, a Job Seeker may view information about the hiring company").
- **Thinking too far ahead**: *Symptom* — stories won't fit cards, unwarranted push to software, proposals for story templates, finer estimate precision (hours not days). *Cause* — habits from big upfront requirements engineering. *Fix* — refresher on story strengths; recall why the team adopted stories.
- **Splitting too many stories**: *Symptom* — splitting frequently during iteration planning. *Fix* — proactively pass through remaining stories and pre-split candidates.
- **Customer has trouble prioritizing**: *Symptom* — prioritizing is consistently very hard. *Cause* — stories too large (only 3 epics to choose among) or not framed as business value (e.g., "connects via a connection pool"). *Fix* — replace with smaller stories; rewrite for value; have the customer write them.
- **Customer won't write/prioritize stories**: *Symptom* — customer refuses responsibility (blame-avoidant culture). *Fix* — let them off the hook; collect input privately; you take responsibility for final (possibly wrong) decisions.

## Reference Tables
| Smell | Symptom | Cause | Remedy |
|---|---|---|---|
| Too small | Frequent re-estimating | Overlapping work | Combine for planning; split at iteration |
| Interdependent | Can't plan iterations | Too small / bad split | Combine or re-split as slice of cake |
| Goldplating | Unplanned features | Wow / pressure / ego | Visibility, reviews, QA, self-police |
| Too many details | Writing > talking | Over-valuing docs | Smaller cards; converse |
| UI too soon | Early UI assumptions | Premature implementation focus | Rewrite without UI specifics |
| Thinking too far ahead | Won't fit cards; wants templates/finer estimates | Big-upfront habits | Refresh on story strengths |
| Splitting too many | Frequent splits in planning | Stories not pre-sized | Pre-split remaining stories |
| Trouble prioritizing | Prioritizing is hard | Too large / no value framing | Smaller, value-framed stories |
| Won't write/prioritize | Customer ducks responsibility | Blame culture | Let them off the hook; you decide |

## Worked Example
The "connection pool" fix. The customer is handed technical stories — "A user connects to the database via a connection pool" and "A user can view detailed error information in a log file" — and can't prioritize because the business value is invisible. Remedy: rewrite each so the value is explicit — "A user can start the application without a noticeable lag while connecting to the database" and "Whenever an error occurs, users are given enough information to know how to correct the error." Now the customer can weigh and rank them.

## Key Takeaways
1. Smells are symptoms to diagnose, each with a known remedy — watch for them during planning.
2. Most sizing smells (too small, interdependent, splitting too often) resolve by combining and slicing through all layers.
3. Small cards and conversation defend against too-much-detail and thinking-too-far-ahead.
4. Prioritization smells usually trace to size or missing business-value framing; the deepest fix is to have the customer write the stories.
5. When the customer won't engage, reduce the threat — make participation safe.

## Connects To
- **Ch 7 (Good Stories)**: "slice of cake," constraints, avoiding UI detail.
- **Ch 10 (Planning an Iteration)**: splitting stories to fit velocity.
- **Ch 13**: these smells are the flip side of stories' advantages (deferring detail, right size).
- **Refactoring "code smells" (Fowler/Beck)**: external origin of the "smell" diagnostic metaphor.
