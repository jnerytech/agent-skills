# Chapter 2: Writing Stories

## Core Idea
Good stories share six attributes captured by the acronym INVEST; the craft of writing stories is getting size and detail right — splitting epics, combining tiny stories, keeping value visible to customers, and resisting the urge to bake in UI and technology assumptions too early.

## Frameworks Introduced
- **INVEST (Bill Wake)**: a good story is **I**ndependent, **N**egotiable, **V**aluable to users or customers, **E**stimatable, **S**mall, **T**estable.
  - When to use: as a checklist whenever writing or reviewing a story.
  - How: test each story against the six; fix the ones that fail (split, combine, rephrase for value, send a spike to make it estimatable, add tests for testability).
  - Why it works: each letter targets a concrete failure (dependencies wreck planning; over-specified cards kill conversation; developer-only value can't be prioritized). Note: INVEST is previewed here but the full guidelines live in Ch 7.
- **Splitting epics (compound vs. complex)**:
  - When to use: a story is too big to estimate or won't fit an iteration.
  - How: a **compound** story (many small stories bundled) → split along create/edit/delete OR along data boundaries. A **complex** story (inherently large, uncertain) → split into an investigative **spike** (timeboxed) + a development story; ideally put the spike in an earlier iteration so the customer can prioritize research separately.
- **Combining stories**: bundle several too-small stories (bugs, minor UI tweaks) into one named story of ~half-day to several days; with paper cards, staple them under a cover card.

## Key Concepts
- **Negotiable**: the card is a reminder to converse, not a written contract; include known details only as brief annotations.
- **Valuable to purchasers or users**: distinguish *user* (uses the software) from *purchaser* (buys it); stories may serve either, but avoid stories valued only by developers.
- **Spike**: a brief, timeboxed experiment to learn enough to estimate or de-risk a story.
- **Timebox**: the defined maximum time allotted to a spike, which makes the unestimatable estimatable.
- **Compound story**: an epic that bundles multiple independent shorter stories.
- **Complex story**: an epic that is inherently large and resists clean disaggregation.
- **Nonfunctional requirement**: a requirement about the software but not its functionality — must still be made testable (replace "never"/"easy to use" with measurable targets).
- **Three reasons a story isn't estimatable**: lack of domain knowledge, lack of technical knowledge, or the story is too big.

## Mental Models
- Use the card as a **reminder + open questions on the front, tests on the back** — already-decided details become tests, not card clutter.
- Beware **detail masquerading as precision**: too many notes make a discussion feel concrete and definitive, suppressing the needed conversation.
- Think Goldilocks for size: epics can't be planned, tiny stories aren't worth tracking — aim for "just right" relative to your team and tech.
- Rewrite tech/UI assumptions as **outcomes the customer can value**: "all connections through a connection pool" → "up to fifty users on a five-user database license."

## Worked Example
Dependent BigMoneyJobs payment stories (pay by Visa / MasterCard / Amex) — estimating is ambiguous because the first card costs 3 days and each next 1 day. Two fixes:
- **Combine** → "A company can pay for a job posting with a credit card" (5 days, independent).
- **Re-split** → "pay with one type of credit card" + "pay with two additional types."

Card detail, done right (front):
> A company can pay for a job posting with a credit card.
> Note: Will we accept Discover cards?
> Note for UI: don't have a field for card type (derive from first two digits).

Back of card (the over-detailed annotations turned into tests):
- Visa, MasterCard, Amex (pass); Diner's Club (fail)
- good / bad / missing card ID numbers; expired cards; over and under $100

Untestable → testable: "A user must never wait long for any screen" → "New screens appear within two seconds in 95% of all cases."

## Key Takeaways
1. Run every story through INVEST; treat a failing letter as a prompt to rewrite, split, or combine.
2. Eliminate dependencies by combining or re-splitting; if you can't, put two estimates on the card (one if done first, a lower one if done after).
3. Strip UI and technology assumptions from stories; express the underlying need as user/customer value so it can be prioritized.
4. Convert a not-estimatable story by sending a timeboxed spike, then writing the real-work story separately.
5. Split compound epics along create/edit/delete or data boundaries; split complex epics into spike + development and schedule the spike earlier.
6. Combine bug-fix and tiny-UI stories into one named, schedulable story.
7. Make nonfunctional stories testable with concrete, measurable thresholds; aim for ~99% test automation.

## Connects To
- **Ch 1**: builds on Card/Conversation/Confirmation — annotations are conversation reminders, tests are confirmation.
- **Ch 7 (Guidelines for Good Stories)**: full treatment of INVEST and splitting advice.
- **Ch 6 (Acceptance Testing)**: turning card-back tests into automated confirmation.
- **Extreme Programming**: source of *spike* and *timebox*.
