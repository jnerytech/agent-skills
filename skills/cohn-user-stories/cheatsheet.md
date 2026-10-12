# Cheatsheet — User Stories Applied (Cohn)

Decision aid. The judgment calls Cohn would make, stated so you can act without re-reading the book.

## Story template & the 3 Cs
- Write: **"As a *(role)*, I want *(function)* so that *(value)*."** Can't write "so that"? → the story has no clear value; rework it.
- A story = **Card** (reminder) + **Conversation** (detail, deferred) + **Confirmation** (acceptance tests on the back). The card is a *promise to talk*, never a contract.

## INVEST — fix-by-symptom
| Letter | If it fails… | Fix |
|---|---|---|
| **I**ndependent | can't plan without dragging in others | combine, or re-split as a vertical slice |
| **N**egotiable | card is over-specified | strip to a reminder; move decided detail to tests |
| **V**aluable | only developers care | reframe in user/customer value |
| **E**stimable | team can't size it | spike (domain/tech gap) or split (too big) |
| **S**mall | won't fit an iteration | split (compound→CRUD/data; complex→spike+dev) |
| **T**estable | "fast", "easy", "never" | add measurable acceptance tests |

## When a story won't behave — diagnose the smell
| Symptom | Likely smell | Remedy |
|---|---|---|
| Re-estimating constantly | stories too small | combine for planning; split at iteration time |
| Can't plan without chains | interdependent | combine or re-split as slice-of-cake |
| Unrequested features appear | goldplating | daily visibility, end-of-iteration review, self-police |
| Writing about stories > talking | too many details | smaller cards; converse |
| Early cards name screens/buttons | UI too soon | rewrite without UI assumptions |
| Wants templates, hour-level estimates | thinking too far ahead | refresh on why you chose stories |
| Customer can't prioritize | stories too big / no value framing | smaller, value-framed stories |
| Customer won't engage | blame culture | let them off the hook; you decide, collect input privately |

## Splitting rule
- **Slice the cake**: every split piece runs end-to-end through all layers and is independently usable. Never "build form" + "save to DB" (neither works alone).
- Compound epic → split by create/edit/delete or data boundary. Complex epic → **spike** (timeboxed) + development story, spike scheduled earlier.

## Estimating
- Estimate in **story points** (relative size), not time. Scale: **½ 1 2 3 5 8 13 20 40 80** (bigger = less known; pick "40 or 80," not "79 or 80").
- **Planning poker**: private estimate → reveal together → high & low explain → re-vote; ≤3 rounds; converge *reasonably*, not exactly.
- Estimate as a **team that will do the work**; customer answers questions, **never estimates**, never reacts to numbers.
- Constraints → **0 points** (they shape other stories).
- Pairing changes **velocity, not estimates**.

## Planning — what to commit to
- Decide by **velocity**: iterations = total points ÷ velocity. No history? guess velocity ≈ **⅓–½ of developer-days** per iteration, and stay conservative for iteration 1.
- Communicate **"ready in ~5–7 iterations,"** never a fixed date. Flex **scope**, not date or quality.
- **Cost changes priority** — always give the customer the estimate before she prioritizes.
- On a priority conflict, **the customer wins every time** — but cannot prioritize without estimates.
- **MoSCoW**: Must (fundamental) / Should (workaround exists) / Could (drop if late) / Won't (next release).

## Iteration mechanics
- Story → tasks (**disaggregate**), one developer **accepts** each, estimate accepted tasks in **ideal hours**, sum to catch over-commitment.
- Mid-iteration: customer **holds priorities steady**; add a task only for forgotten in-scope work.

## Velocity & charts — read them right
- Velocity = **finished stories only** (passed acceptance tests). Never count partials; never re-score a completed story.
- **Don't trust velocity before 2–3 iterations** — it's volatile early.
- Burndown **rising** ≠ slow team → scope grew faster than completion. Read *speed* from velocity / cumulative charts, *not* burndown.
- Daily burndown tracks **hours remaining**, not hours expended.
- Net progress = completed − added re-estimates − new-story points.

## Acceptance tests
- **Customer** writes them, on the **card back**, **before/while coding** — they define "done."
- Cover happy path + edge + explicit **failure** cases (expired/over-limit/invalid cards, non-admins, wrong brand).
- Stop when another test adds no clarification; let unit tests handle minutiae. Automate (FIT/FitNesse) so prior tests re-run cheaply.
- Writing the tests is itself a requirements conversation — it clarifies scope and can simplify design.

## Real users vs. proxies
- **A real user beats a proxy any time.** Developers are usually *worse* proxies than the proxies.
- Forced to use proxies? combine **different** types so biases cancel; use salespeople/managers as *conduits* to users, not the sole voice; spin up a **user task force**.
- Proxy bias tells: manager amplifies (1 min → "5 min"); marketing favors feature *count*; trainer/support optimize for train/support, not user priorities; domain expert risks expert-only software.

## Requirements doc vs. story (when someone wants "real specs")
- Story ≈ **one use-case scenario**; story + acceptance tests ≈ a use case.
- Stories are **smaller, less complete, transient** (ripped up after iteration), and exist for **planning + conversation**, not documented agreement.
- Focus on the user's **goal**, not a "shall" list of attributes — an attribute list lets you build the wrong thing.

## Card hygiene tells
- Out of room on the card? → **use a smaller card** (forces detail into conversation).
- Don't number cards (avoids "4.6.1" abstraction); add a short title.
- Start with **paper cards**; switch to software only for distributed teams or ISO traceability.
- Err toward **retaining** completed cards — they've saved deals, rewrites, acquisitions.
