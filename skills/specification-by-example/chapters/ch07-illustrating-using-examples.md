# Chapter 7: Illustrating using examples

## Core Idea
Concrete, realistic examples beat abstract requirement statements because they are unambiguous and force functional gaps into the open before implementation; capture one consistent set of examples from analysis through testing so every role shares the same understanding. Good examples must be **precise, complete, realistic, and easy to understand** — and even cross-cutting "nonfunctional" requirements can be illustrated this way.

## Frameworks Introduced

### The Four Qualities of Good Examples
Every illustrative example should be precise, complete, realistic, and easy to understand. Each quality has supporting patterns.

- **Precise**: no room for misunderstanding; clearly define context, expected behavior, and ideally something easily checkable.
  - **Don't have yes/no answers** — When: the underlying concept isn't separately defined. Yes/no tables create false shared understanding (e.g., "email sent? Y/N" hides email *contents*). Rewrite to capture key attributes of what actually happens. Yes/no is acceptable only if the concept (e.g., contents) is illustrated by a *separate* set of examples.
  - **Avoid abstract classes of equivalence** — When: you can specify a concrete example. "Less than 10" or variables hide disagreements (are negatives included?). Equivalence classes as *inputs* force outputs to be formulas that just re-describe the function, losing the example's value and pushing translation work onto whoever automates. Use a representative concrete value. Equivalence classes are OK as *outputs*, especially for nondeterministic processes (e.g., "result between 0.1 and 0.2").

- **Complete**: enough examples to cover the whole scope; primary cases are a start, not the sum.
  - **Experiment with data**: once a set feels complete, look at the example structure and invent valid input combinations that could violate the rule. For numbers, use large/small values around boundaries, zero, negatives. For entities, try more than one, zero, or the same entity twice. Testers drive this. Many cases will be invalid — fine, skip detail unless demonstrating error messages.
  - **Ask for an alternative way to check the functionality** — When: complex/legacy infrastructures. Ask the business user "How else would you be able to test this?" (Bas Vodde: "Is there anything else that would happen?"). Surfaces forgotten downstream systems (legacy data warehouses, migration targets) and helps decide where to automate.

- **Realistic**: real cases flush out ambiguities; invented/simplified/abstracted examples lack the detail and variation needed. Avoid abstract entities like "customer A" — find a real customer with the characteristic, or focus on the characteristic itself.
  - **Avoid making up your own data** — When: data-driven projects. Invented examples miss real variations and inconsistencies; legacy data routinely defies logic. Use realistic data drawn from the existing system (obfuscate sensitive fields) instead of brand-new cases.
  - **Get basic examples directly from customers** — When: working with enterprise customers. Product managers proxying many customers can write precise examples that still miss what customers want. Insist on real customer examples (e.g., customer emails describing a desired dialog) to kick-start workshops; include them in the executable specs.

- **Easy to understand**: huge tables with dozens of columns/rows make consistency and completeness impossible to evaluate. Keep examples precise and realistic but simple.
  - **Avoid the temptation to explore every combinatorial possibility**: testers often want every argument combination; redundant examples don't improve understanding. Keep examples that *move the discussion forward*. But never discard a suggested edge case without discussion — either the suggester misunderstands existing examples, or they found a real gap; both are worth talking through.
  - **Look for implied concepts**: too many or too complex examples signal a missing higher-level abstraction. Identify hidden/implied concepts, make them explicit, and specify each separately with its own focused example set. This is core to domain-driven design and yields better software structure.

### Illustrating Nonfunctional Requirements
"Nonfunctional" usually means cross-cutting (e.g., security) or measurable on a sliding scale (e.g., performance) — and implies an unidentified stakeholder. Every such requirement can be illustrated by example.

- **Get precise performance requirements** — When: performance is a key feature. Specify as "import X records within Y minutes on Z CPUs." "Faster than the current system" is not a requirement — say how much faster and in what way.
- **Use low-fi prototypes for UI** — When: UI/usability can't fit truth tables. Paper prototypes (cutouts + notes) or Balsamiq Mockups; walk through one or two examples to confirm all needed info is on a screen. Interactive prototypes (even shell-script CLIs) elicit real usage details and prevent boomerangs.
- **Try the QUPER model** — When: sliding-scale requirements. Visualize cost, value, quality on an S-curve; expose breakpoints and cost barriers for discussion (see below).
- **Use a checklist for discussions** — When: cross-cutting concerns. Global blanket requirements ("all pages load < 1s") usually waste money. Treat cross-cutting requirements as a checklist (Christian Hassa): for each story decide which concerns apply, then illustrate only those.
- **Build a reference example** — When: requirements are impossible to quantify (usability, fun, playability). Build one feature to final shippable quality early as the definition of "done" (Supermassive's "vertical slice"), supplemented by a low-fidelity "horizontal slice" plus concept art.

## Key Concepts
- **Telephone game**: distortion as requirements pass between analyst, developer, tester — each inventing inconsistent examples; one shared example set prevents it.
- **Feedback exercise**: after discussing a special case, have everyone independently write how the system should behave, then compare; matching answers prove shared understanding, mismatches cluster into discussion points.
- **Black-box test as completeness check** (Weinberg & Gause): if you can't design good black-box test cases, you lack info to build the system. Illustrative examples *are* those tests.
- **QUPER breakpoints**: *Utility* (unusable→usable), *Differentiation* (competitive advantage begins), *Saturation* (more quality is overkill). **Cost barriers**: points where quality gains stop being cheap (rewrite/architecture impact). Set targets as intervals, not discrete points.
- **Implied concept**: a hidden abstraction (e.g., "trade location," "migration status") whose extraction collapses combinatorial example explosion.
- **Vertical / horizontal slice**: a fully-finished thin section vs. a broad low-fidelity blockout of the whole product.

## Mental Models
- Use **concrete representative values** when the process is deterministic; use **equivalence-class ranges as outputs** when it's nondeterministic.
- Use **real/legacy data** when the project is data-driven or migrates legacy systems; invented data only hides the surprises that bite mid-iteration.
- Use **"look for implied concepts"** when one feature needs many or complex examples — split into focused sets rather than enumerating combinations.
- Use a **reference example / vertical slice** when quality is subjective and unquantifiable (usability, fun) instead of forcing it into a metric.

## Anti-patterns
- **Yes/no tables**: give a false sense of agreement; hide the attributes (contents, message structure) that actually matter.
- **Abstract entities ("customer A", "less than 10")**: mask disagreements and dump translation/ambiguity onto whoever automates.
- **Inventing your own data**: assumes consistency real (and legacy) data won't honor — produces "too many surprises" when real data arrives.
- **Combinatorial explosion**: covering every argument combination adds noise without understanding; signals a missing concept.
- **Global blanket nonfunctional requirements**: "all pages < 1s" defined before the product exists wastes money on pages that don't need it.
- **"Faster than the current system"**: unmeasurable, untestable, no shared target.

## Worked Example
ACME OnlineShop (the book's only fictional company) runs a specification workshop. Barbara (BA) pre-gathered examples from owner Owen and introduces the **free delivery** story.

- **Basic example (Barbara)**: buy a Manning book (e.g., *Specification by Example*) → shopping cart offers free delivery.
- **Functional gap (David, dev)**: "Free delivery to anywhere? An island off South America would cost more than the book earns." → Barbara: not worldwide, **domestic only**. (A new constraint surfaced.)
- **Counter-example (Tessa, tester)**: add a case proving free delivery is *not* offered for all books. → Barbara: *Agile Testing* (Addison-Wesley) → no free delivery. (Illustrates the rule's boundary, avoiding a yes-everywhere misread.)
- **Experiment with data (David)**: no numerical boundaries, but play with the cart list — buy *both* Agile Testing and Specification by Example? → Barbara: free delivery for both; as long as a Manning book is in the cart, delivery is free.
- **Edge case → open question (David)**: buy Specification by Example **and a fridge**? Delivery would dwarf the book's earnings. → Barbara: "I didn't discuss that with Owen. I'll get back to you." (Genuine gap, parked.)
- **Close**: David and Tessa confirm they have enough to start, apart from the fridge problem; Barbara commits to resolve it early next week.

Outcome: in minutes the team converted an abstract story into precise, complete-enough examples, surfaced two gaps (geography, mixed-cart), and knew exactly what was still unknown — far cheaper than discovering it mid-implementation.

## Key Takeaways
1. Capture one consistent set of examples used from specification through development to testing — it is the single source of truth that defeats the telephone game.
2. Illustrating with examples takes far less time than implementing; realizing "we can't illustrate this" is a cheap early signal that information is missing.
3. Make examples precise (no yes/no, no abstract equivalence classes) and complete (experiment with data, ask for alternative ways to test).
4. Make examples realistic — use real and legacy data, get examples straight from customers; invented data hides the variations that cause late surprises.
5. Make examples easy to understand — don't chase every combination; when examples multiply, extract the implied concept and split into focused sets.
6. There is no requirement too "nonfunctional" to illustrate: quantify performance precisely, prototype UI low-fi, model sliding scales with QUPER, checklist cross-cutting concerns, and build reference examples for the unquantifiable.

## Connects To
- **Ch 4**: boomerangs — invented examples and UI-only thinking let bugs return mid-iteration; realistic examples and prototypes prevent them.
- **Ch 5**: "don't look only at the lowest level" — interactive prototypes also help identify scope, not just illustrate it.
- **Ch 8**: refining the specification — experimenting with data over-produces near-duplicate examples and scripts aren't specifications; refinement cleans both up.
- **Ch 9**: test data management — using realistic/legacy data requires obfuscation and a data strategy for automation.
