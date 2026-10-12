# Chapter 2: Key process patterns

## Core Idea
Specification by Example is a chain of seven recurring process patterns that carry a feature from a business goal all the way to living documentation. Successful teams apply them just-in-time — not as an up-front Waterfall sequence — so each artifact feeds the next without losing meaning.

## Frameworks Introduced
- **The 7 key process patterns (the flow)**: The patterns shared by the most successful teams, applied in sequence but just-in-time.
  - When to use: Across the whole delivery lifecycle; derive scope at the start of a phase/milestone, specify only when ready to implement an item.
  - How: 1) Deriving scope from goals → 2) Specifying collaboratively → 3) Illustrating using examples → 4) Refining the specification → 5) Automating validation without changing specifications → 6) Validating frequently → 7) Evolving a documentation system.

- **Deriving scope from goals** (detailed in Ch 5): Start from a measurable business goal, then collaborate to define scope that achieves it.
  - When to use: Beginning of a project/phase, before deciding what to build.
  - How: Business users communicate intent and expected value; the delivery team proposes a cheaper/faster/easier solution rather than accepting a pre-designed feature list.

- **Specifying collaboratively** (Ch 6): Business users, developers, and testers design specifications together.
  - When to use: When defining the solution for an item the team is about to build.
  - How: Workshops/conversations that capture technical, testing, and domain knowledge; creates collective ownership.

- **Illustrating using examples** (Ch 7): Replace ambiguous prose with concrete key examples of expected behavior.
  - When to use: Whenever requirements risk multiple interpretations or rely on jargon/domain expertise.
  - How: Team identifies key examples; devs/testers add edge cases; if the system passes all key examples it meets the agreed spec.

- **Refining the specification** (Ch 8): Strip examples down to a concise, precise context.
  - When to use: After collaboration produces verbose, UI-flavored examples.
  - How: Remove extraneous detail (the "how"); keep "what"; produce *specifications with examples* — a spec, an acceptance test, and a future regression test.

- **Automating validation without changing specifications** (Ch 9): Automate the spec while keeping its text identical.
  - When to use: When specs must be validated repeatedly and stay readable by business users.
  - How: Use a framework that pulls inputs/expected outputs from the document itself; the result is an *executable specification* with a single version of the truth.

- **Validating frequently** (Ch 10): Run all executable specifications often.
  - When to use: Continuously during development.
  - How: Frequent checks surface drift between system and spec early; discuss differences with business users and resync.

- **Evolving a documentation system** (Ch 11): Keep specs organized, findable, and current as the domain changes.
  - When to use: Ongoing, over the life of the project.
  - How: Update specs to reflect domain/market changes, producing *living documentation*.

## Key Concepts
- **Specification with examples**: A refined, self-explanatory document that is simultaneously a spec of work, an acceptance test, and a future regression test.
- **Executable specification**: A specification with examples, automated without changing its text, usable as a development target and a clarification source.
- **Living documentation**: A reliable, authoritative, code-equivalent but readable source of what the system does and why — also free regression testing.
- **Key examples**: The concrete cases that define what the software must do and serve as the objective "done" criterion.
- **Just-in-time**: Deriving scope and specs only when the team is ready for that work, never all up front.
- **Checks vs tests**: Checks are deterministic, automatable validations (this book's focus); tests need human insight (exploratory, usability).

## Mental Models
- Use **derive scope from goals** when business users hand you a solution — they aren't software designers; start from the goal instead.
- Use **examples over prose** when "obvious" requirements actually need domain expertise — small misunderstandings compound into rework.
- Use **"tests are specifications; specifications are tests"** — once a concrete spec is automated there is no difference between the two.
- Use **the flow just-in-time** when tempted to specify everything before development — that is just big Waterfall in disguise.

## Anti-patterns
- **Accepting a customer's requirement list as the scope**: Asks non-designers to design the solution; loses the delivery team's knowledge, builds what was asked but not what was wanted.
- **Specifying in isolation**: Forces separate hand-off communication; details get lost in translation, causing post-delivery rework.
- **Verbose, UI-driven examples**: Detailing "how" instead of "what" over-constrains the system and is harder to understand.
- **Automating with traditional unit/functional tools that alter the spec**: Detail gets lost; the automated version becomes inaccessible to business users and can't be reused when requirements change.
- **Keeping two versions of the truth** (test + Word/web copy): Guarantees synchronization problems; paper documentation goes stale.
- **Running the whole sequence up front for all specs**: That's Waterfall, not Specification by Example.

## Worked Example
**Business goal** (measurable): "Increase repeat sales to existing customers by 50% over the next 12 months." A good goal lets you earn/save/protect money and track success.

**Scope** (Ch 5): A customer-loyalty theme is broken into chunks. The team chooses a *basic loyalty system* first (customers register for a VIP program; VIP customers get free delivery on certain items), postponing advanced bonus schemes.

**User stories**:
- As a marketing manager, I want customers to register personal details by joining a VIP program (to enable direct marketing).
- As a marketing manager, I want the system to offer free delivery on certain items to VIP customers (to entice registration).
- As an existing customer, I want to receive information on special offers (to save money).

**Key examples** (Ch 6–7): Working the *free delivery* story, collaboration narrows it: free delivery on **books only** (avoids shipping electronics/large items), and to drive repeat sales, "free delivery" becomes "free delivery for **five or more** books." The mixed-cart question (books + electronics) is postponed — simplest thing first: no free delivery if the order contains anything but books. Key examples:
- VIP, 5 books → free delivery
- VIP, 4 books → no free delivery
- Regular, 5 books → no free delivery
- VIP, 5 washing machines → no free delivery
- VIP, 5 books + 1 washing machine → no free delivery

**Specification with examples** (Ch 8): Refined into a self-explanatory document, formatted for later automation:

> Free delivery is offered to VIP customers once they purchase a certain number of books. Not offered to regular customers, or to VIP customers buying anything other than books. Given the minimum is five books:

| Customer type | Cart contents | Delivery |
|---------------|---------------|----------|
| VIP | 5 books | Free, Standard |
| VIP | 4 books | Standard |
| Regular | 10 books | Standard |
| VIP | 5 washing machines | Standard |
| VIP | 5 books, 1 washing machine | Standard |

Stored in a spec repository (e.g., a FitNesse wiki or a directory of Cucumber feature files) to become part of living documentation.

**Executable specification** (Ch 9): Initially the test fails (not yet automated, feature not built). Developers implement the feature and connect an automation framework that pulls inputs and validates outputs **without changing the specification document**. Once automated, the spec is executable.

**Validate frequently / living documentation** (Ch 10–11): The executable spec is checked often to stay synced with the system and is kept current as the domain evolves — becoming reliable living documentation.

## Key Takeaways
1. The method is seven patterns forming a flow from business goal to living documentation — learn them as a chain, not isolated tips.
2. Apply the flow just-in-time; running it all up front is Waterfall.
3. Start from measurable goals and derive scope collaboratively — don't accept a pre-baked feature list.
4. Concrete key examples are both the development target and the objective "done" criterion.
5. Refine examples to capture *what*, not *how*; the result is spec + acceptance test + regression test in one.
6. Automate without altering the specification so it stays a single, readable version of the truth.
7. Frequent validation + ongoing curation turns executable specs into trustworthy living documentation.

## Connects To
- **Ch 5**: Deriving scope from goals — the first pattern, in depth.
- **Ch 6**: Specifying collaboratively — running the collaboration.
- **Ch 7**: Illustrating using examples — choosing key examples.
- **Ch 8**: Refining the specification — making examples concise and precise.
- **Ch 9**: Automating validation without changing specifications — executable specs.
- **Ch 10**: Validating frequently — keeping system and specs in sync.
- **Ch 11**: Evolving a documentation system — living documentation.
