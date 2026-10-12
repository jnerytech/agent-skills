# Chapter 8: Refining the specification

## Core Idea
Raw examples from a workshop are like uncut diamonds — valuable but unfinished. Successful teams refine them into a clear, unambiguous specification that captures the conditions of satisfaction without extraneous detail, so anyone can pick it up months or years later and understand it.

## Frameworks Introduced

- **The six properties of a good specification**: A specification with examples must satisfy two goals — be a development target now, and be living documentation later. To do both it should be: *Precise and testable*, *A true specification not a script*, *About business functionality not software design*, *Self-explanatory*, *Focused*, *In domain language*.
  - When to use: Whenever turning raw key examples into a recorded specification.
  - How: Apply the refining advice below against each property.

- **Scripts are not specifications**: A script describes *how* something is tested (lower-level UI/workflow interactions); a specification describes *what* the system does.
  - When to use: Whenever business users describe steps ("first do this, then that").
  - How: Strip the workflow/session steps; state the business rule directly. Watch for flow-like descriptions — unless a genuine process flow, a sequence signals a rule hidden in a script.

- **Use a descriptive title and explain the goal**: Title summarizes intent (think: what you'd type into Google to find it); a short header paragraph explains the goal and the structure of the examples.
  - When to use: Every specification.
  - How: Write the examples first, then explain them aloud to someone; capture what you said and put it in the header.

- **Show and keep quiet**: To check self-explanatoriness, hand the spec to someone else and say nothing.
  - When: Someone is working on specifications alone. In order to: check whether a specification is self-explanatory.
  - How: Ask them to explain what they understood; if it doesn't match your intention, write down the explanation you'd have given and fold it into the header/names.

- **Start with basic examples; then expand through exploring**: Specify only the happy path before building; automate it; then explore additional cases by risk.
  - When: Describing rules with many parameter combinations.
  - How: Tester + developer specify a happy path; developer automates and codes; testers reuse the framework to add risk-based cases; failing cases go back to programmers to extend the spec.

- **Apply defaults in the automation layer**: Push responsibility for building valid objects to the automation layer so the spec mentions only important attributes.
  - When: Objects need lots of setup/dependencies.
  - How: Prepopulate sensible defaults and dependencies in code (or a global config file if business users should change them). E.g., specify "user has $100 on the card" — not full address and card details.

- **Don't explicitly set up all the dependencies in the specification**: Move dependencies unrelated to the goal into the automation layer.
  - When: Complex dependencies / referential integrity (data-driven projects).
  - How: Keep only the attributes/objects the rule cares about in the spec; let the automation layer wire the rest. Prefer realistic data over context guessed by the team.

- **Resist working around technical difficulties in specifications**: Solve technical quirks in the automation layer, not the spec.
  - When: Working on a legacy system.
  - How: Use the tool's separation of human-readable spec from automation-code layer; contain workarounds in code so spec stays stable when design improves.

## Key Concepts
- **Conditions of satisfaction**: The expected output/acceptance criterion a refined specification captures — a good spec with examples *is* an acceptance test.
- **Self-explanatory**: Readable and understandable years later by people who never attended the discussion.
- **Focused**: Describes a single thing (one rule, function, or process step) and only the attributes relevant to it.
- **Ubiquitous Language**: Eric Evans' single shared domain language (DDD) used by users, analysts, testers, developers — removes translation loss and bottleneck analysts.
- **Brittle test**: A test that breaks on design changes even when business functionality is unchanged — caused by specs tightly coupled to code.
- **Incidental complexity**: Names/IDs/concepts in a spec that aren't first-order domain concepts (database identifiers, technical service names, invented test concepts).

## Mental Models
- Use a **specification** (what) when describing a business rule; use a script (how) only for a genuine process flow.
- Use **Given-When-Then** when you need to declare context, trigger a single action, then assert post-conditions.
- Use **three key examples specified properly** rather than a hundred specified poorly — a primary spec for feedback, a linked supplementary test for exhaustive combinations (run overnight).
- Use the **automation layer** when you hit a technical difficulty, default value, or dependency — not the specification.

## Anti-patterns
- **Using raw examples directly**: Skips refining; produces huge document sets nobody can understand later.
- **Scripts / flow-like descriptions**: Bake in workflow & session constraints; break on irrelevant changes (e.g., disabled user account); force readers to reverse-engineer the rule.
- **Coupling specs to code/design**: Brittle tests; Hellesøy reported up to 8 hours to fix test scripts after a big refactor.
- **Mixing technical tests with executable specs**: Use technical-test tools for technical tests; don't expect executable specs to cover unit/integration concerns — keep them separate.
- **Overspecifying / covering every case**: Key examples drown in a sea of values; slows feedback. Specs aren't a replacement for combinatorial regression testing. Fear of blame is no excuse — responsibility is shared.
- **Getting trapped in UI details**: Teams burned hours on navigation menus (near-zero risk) instead of edge cases and user journeys.
- **Always relying on defaults**: Removing duplication is good in code, not always in specs — state a key attribute explicitly even if it equals the default, so the default can change and intent stays visible (Ian Cooper).
- **Blank/unrelated cells (e.g., FitNesse)**: Signal instability, missing rules, or a human-checked "test" that defeats automation.

## Worked Example

**Good specification — Free delivery (self-explanatory, focused):**
> Free delivery is offered to VIP customers once they purchase a certain number of books. Not offered to regular customers or to VIP customers buying anything else than books. Given the minimum is five books:

| Customer type | Cart contents          | Delivery       |
|---------------|------------------------|----------------|
| VIP           | 5 books                | Free, Standard |
| VIP           | 4 books                | Standard       |
| Regular       | 10 books               | Standard       |
| VIP           | 5 washing machines     | Standard       |
| VIP           | 5 books, 1 washing machine | Standard   |

Why it works: descriptive title + intro paragraph explain the rule (no reverse-engineering); realistic examples cover edge cases; says nothing about workflow, sessions, or implementation — that's left to developers; includes only attributes relevant to the rule.

**Bad specification (figure 8.1, a real ex-FitNesse payroll page):** Employees table (with id, name, address, salary), a "Pay day" table, and two unrelated "Paycheck inspector" tables with blank assertion cells. Problems: unclear what's specified (must work backwards from data); incidental complexity (names/addresses/DB ids irrelevant to the rule); "Paycheck Inspector" is an invented testing concept (violates Ubiquitous Language); blank cells = FitNesse troubleshooting output that checks nothing → false positives; check ordering unspecified → the author worked around a technical difficulty *in the spec* instead of the automation layer, so the test passes even if the wrong people got paid.

**Refined version — "Payroll Check Printing" (figure 8.2):** Give it a Google-able title and a header paragraph stating the goal and rules: one check per employee (name, address, salary); print the payroll date; check numbers unique, ascending from the next available number; checks printed in alphabetic order by employee name (a new ordering rule agreed with the business to make it testable). Context (payroll date, next available check number, employee data) is pulled into a visually distinct **PAYROLL CONTEXT** header that prepares data without verifying it. The payroll-run action is left implicit — the results table triggers it. "Paycheck Inspector" becomes **"All checks printed in the payroll run"** so automation can't use subset matching (which would miss duplicate checks). DB identifiers dropped — name+address matches employees to checks. Result: shorter, no incidental clutter, self-explanatory. Then ask "Are we missing anything?" via boundary heuristics (e.g., salary of 0 for a suspended/ex-employee → do we still print?), and consider splitting into generic check-printing vs. payroll-specific specs.

## Reference Tables

Given-When-Then Cucumber scenario (single action, multiple pre/post-conditions allowed):
```
Scenario: New user, suspicious transaction
  Given a user with no previous transaction history,
  And the user's account registration country is the UK,
  When the user places an order with delivery country U.S.,
  Then the transaction is marked as suspicious,
  But the user sees order status as 'Pending.'
```

## Key Takeaways
1. Don't use the first set of examples directly — refine the specification from them; that step gives specs long-term value.
2. Aim for all six properties: precise/testable, true-spec-not-script, business-functionality-not-design, self-explanatory, focused, domain-language.
3. Use **Given-When-Then** (Arrange-Act-Assert): declare context, trigger one single action, assert post-conditions; name a meaningful set of actions as a higher-level domain method rather than listing many actions.
4. Give every spec a descriptive (searchable) title and a short goal paragraph; verify self-explanatoriness with "show and keep quiet."
5. Solve technical difficulties, dependencies, and defaults in the **automation layer**, not in the specification.
6. List only key representative examples (one per business aspect, technical edge case, and known trouble spot); link a separate test for exhaustive combinations.
7. Define and use the Ubiquitous Language across specs, design, and tests; the problem (and solution) is in the team's effort, not the tool.

## Connects To
- **Ch 7 (Illustrating using examples)**: Supplies the precise, realistic, complete key examples that this chapter refines; "examples should be precise" and "realistic" techniques are reused here.
- **Ch 9 (Automating without changing specifications)**: Where the automation layer, test-data management, and the spec/automation separation referenced throughout this chapter are detailed.
