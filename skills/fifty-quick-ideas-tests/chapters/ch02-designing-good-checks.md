# Chapter 2: Designing Good Checks

## Core Idea
Turn agreed needs into clear, deterministic checks that are easy to automate. The heart of the part: a handful of well-chosen **key examples** at the right level of abstraction beats a huge list of complex scenarios — and the Given-When-Then structure is a *design* tool, not just an automation format.

## Frameworks Introduced

- **Focus on key examples**: a small number of simple, understandable scenarios, instead of exhaustive lists.
  - When to use: refining acceptance criteria for any non-trivial story.
  - How (4 strategies for complexity): 1. Look for missing concepts; 2. Group by commonality, show only variations; 3. Split validation and processing; 4. Summarise and explore important boundaries.
  - Why it works: 6 rules × 5 examples = ~40 examples vs 5⁷ ≈ 80,000 combined; smaller groups → modular software, parallel work, faster feedback.

- **Contrast examples with counter-examples**: pair each key example with cases where the feature does *not* apply; vary one input at a time.
  - How: write the simplest passing example as a table row; for each output identify a different value reachable by the *smallest* input variation; repeat until every output value has ≥1 row. Best counter-examples are as close as possible to positives but yield different outputs.

- **Given-When-Then in strict sequence**: structural pattern (= Precondition-Trigger-Postcondition = Arrange-Act-Assert).
  - How: all parameters in `Given`, the *single* action under test in `When`, all expected outcomes in `Then`. Don't mix clauses. Trick: past tense for Given, present for When, future for Then; Given/Then passive (values), When active (action).

- **Flip equivalence classes between inputs and outputs**: reduce equivalence classes for outputs too, not just inputs.
  - When to use: actions with several output types (e.g. validation messages, audit trails, alerts) — one field's error can mask another's.
  - Heuristic (Bach/Kaner/Pettichord, "Test Every Error Message"): explore input equivalence for valid cases, output equivalence for invalid cases.

- **Three competing forces / "three C's"**: BDD artifacts serve 3 roles (Specification, Acceptance tests, Documentation) balancing Conciseness, Completeness, Coherence.
  - How: critique each artifact from all three perspectives; don't over-optimise one. Test footprint is usually bigger than change footprint — completeness is a force, not an absolute goal.

- **Write assertions first**: write outputs/`Then` clauses (or right-hand table columns) before inputs.
  - Why it works: keeps tests focused on one thing, strips incidental detail, makes splitting easy. Iterate between outputs and inputs — not a single top-down pass.

- **Treat too many boundaries as a modelling problem**: an explosion of edge cases signals wrong abstractions/coupling, not just hard testing.
  - How: probe models by designing test cases *before* programming; try 3–4 models, pick the one with fewest scenarios. Look for hidden domain concepts (Evans, *DDD*).

## Key Concepts
- **Key example**: a simple, concrete scenario at the right abstraction that illustrates a business rule.
- **Counter-example** ("negative test", a term the authors avoid): a near-identical input that produces a different output, providing contrast.
- **Describe what, not how**: keep acceptance criteria on *purpose* (business decisions), not mechanics (clicks, page reloads); split into two layers/meetings.
- **Separate inputs and outputs**: inputs left / top (`Given`), outputs right / bottom (`Then`); ideally one `When`.
- **One test, one topic**: each test = one action; watch for multiple `When`s or conjunctions.
- **Split technical and business checks**: ask "who resolves a failure?" — programmer → technical group; business decision → business group; both → split the test.

## Anti-patterns
- **Pages of complex scenarios**: false sense of completeness, hard to split/parallelise, no business confidence.
- **Mathematical formulas in examples** (`Report date - 30 < Transaction`): just restate the rule, hide data-type/timezone/boundary assumptions. Use concrete values; intervals OK only for *output* equivalence classes.
- **Mechanics in acceptance criteria** (login → click → reload): hides purpose, forces full-stack execution, expensive record-and-replay maintenance.
- **Interleaved inputs/outputs**: unclear what's actually being checked; if hard to separate, the team doesn't understand the story — re-discuss, don't clean up.
- **Multiple interdependent `When`s**: fragile, combinatorial boundaries, hard to diagnose.
- **Oversized tables**: too many columns → combinatorial row explosion; errors hide (e.g. a wrong payout in row 9).
- **Automating manual tests as-is**: loses the human's tangential observation *and* creates brittle automation — worst of both worlds. Rewrite from scratch, keep only the purpose.

## Reference Tables
Replacing one big blackjack table with focused per-concept tables (result vs payout vs insurance):

| player | dealer | result?   |
|--------|--------|-----------|
| 19     | 18     | win       |
| 18     | 19     | lose      |
| 19     | 19     | push      |
| BJ     | 19     | blackjack |
| bust   | bust   | lose      |

| bet | result    | payout? |
|-----|-----------|---------|
| 10  | win       | 20      |
| 10  | blackjack | 25      |
| 10  | push      | 10      |
| 10  | lose      | 0       |

## Worked Example
**Free-delivery counter-examples.** Rule: *"Free delivery for VIP customers who order five or more books in a single order."* Key example: *5 books, VIP → qualifies.* Vary one input at a time to get counter-examples:
- 4 books, VIP → does **not** qualify (quantity)
- 5 books, standard customer → does **not** qualify (status)
- 5 refrigerators, VIP → does **not** qualify (item type)
- 5 books + 1 refrigerator, VIP → does **not** qualify (mixed order)

Discussing the refrigerator cases forces restating the rule: *"Orders that include items other than books do not qualify."* The examples sharpened the rule.

## Key Takeaways
1. Prefer a few key examples at the right abstraction over exhaustive scenario lists — it reduces both bugs and combinatorial volume.
2. Always add counter-examples that differ by the smallest input change; contrast is what makes examples informative.
3. Use Given-When-Then as a *design* discipline: one action, parameters separated from outcomes, strict clause order.
4. Reduce equivalence classes on outputs (validation, audit, alerts), not just inputs — error handling is where catastrophic bugs hide.
5. Describe *what*, not *how*; keep mechanics in the automation layer so business checks survive UI change.
6. Write the assertions first to stay focused and keep tests short.
7. An explosion of boundaries is a modelling smell — fix the model, not the test management.

## Connects To
- **Ch 1**: capabilities/key risks feed the key examples here.
- **Ch 3**: "describe what, not how" & "minimise UI interactions" share the same decoupling logic ([[ch03-improving-testability]]).
- **Ch 4**: "decouple coverage from purpose" extends "split technical and business checks" ([[ch04-managing-large-test-suites]]).
- **Specification by Example / BDD / JBehave**: origin of Given-When-Then.
- **CWE/SANS Top 25**: top risks are bad invalid-input handling — supports output equivalence.
