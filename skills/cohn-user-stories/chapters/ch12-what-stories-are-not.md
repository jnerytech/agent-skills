# Chapter 12: What Stories Are Not

## Core Idea
User stories are best understood by contrasting them with three other requirements approaches — IEEE 830 software requirements specifications, use cases, and interaction-design scenarios — which differ from stories in scope, level of detail, longevity, purpose, and who writes them. Stories deliberately favor conversation over documentation and describe user goals, not lists of system attributes.

## Frameworks Introduced
- **Goals vs. requirements-list test**: Read a requirement and ask "what is the user's goal?" rather than "what attribute must the system have?"
  - When to use: whenever requirements read as "The system shall…" lists.
  - How: restate each item as the user goal it serves; design to the goal.
  - Why it works: a list of attributes (gasoline engine, four wheels, steering wheel) lets you build the wrong thing (a car); the goal ("mow my lawn easily") reveals the right thing (a riding mower).
- **Story ≈ one use-case scenario (+ acceptance tests)** (James Grenning): a story card plus its acceptance tests is roughly equivalent to a use case.
  - How: story text ↔ main success scenario; story's acceptance tests ↔ use-case extensions.
- **Essential use case** (Constantine & Lockwood): a use case stripped of UI/technology assumptions, written as User Intention / System Responsibility columns; its user intentions can be read almost directly as stories.

## Key Concepts
- **IEEE 830**: 1998 standard for software requirements specs; signature form is "The system shall…".
- **Use case**: generalized description of interactions between system and actors (Jacobson; Cockburn templates).
- **Main Success Scenario**: the primary successful path through a use case.
- **Extensions**: alternate/error paths; each full path is a *scenario*.
- **Use case brief**: unstructured-text use case; larger scope than a story, and persistent.
- **Interaction-design scenario**: detailed narrative of a user (e.g., Maria) interacting with the system; has setting, actors, goals, actions/events (Carroll).
- **Primary vs. secondary actor**: in scenarios, the main user vs. a supporting person (Maria vs. Jessica); scenario actors are always people.
- **Change of scope (critique)**: misnomer implying scope was ever fully defined; ignores the feedback loop from users seeing software.

## Mental Models
- Think of a story as a *single scenario* of a use case, not the whole use case.
- Use cases are *artifacts of analysis*; stories are a *support tool for* analysis (notes that start conversations).
- Cards are transient (often ripped up after the iteration); use cases and scenarios are permanent artifacts that outlive iterations.
- Documents feel like contracts ("so final"); conversations don't — "if we learn something next month, we talk again."

## Anti-patterns
- **Ping-ponging spec between Dev and Marketing/Product**: each rewrites it under a new name (e.g., "Functional Specification") to claim ownership of intent — a warning sign of end-of-project blame positioning.
- **Embedding UI assumptions in use cases**: e.g., "New Message" menu item, dialog, Send button — precludes alternative UIs (click-name, voice). Story "A user can compose and send email messages" avoids it.
- **Designing while reading requirement lists**: readers solve for the first few items they hit (Carroll), locking in a premature solution.
- **Cost hidden until the spec is done**: analysts spend months, then learn the 6-month wish is a 24-month build; three-fourths of the writing is wasted.

## Reference Tables
| Dimension | IEEE 830 | Use Case | Interaction Scenario | User Story |
|---|---|---|---|---|
| Form | "The system shall…" list | template or brief | detailed narrative | short sentence on a card |
| Scope | tiny per item | large (1 UC = many stories) | largest (1 scenario ⊃ many UCs) | small (≤~10 dev days) |
| Detail | high, exhaustive | high | very high | minimal placeholder |
| Longevity | permanent | permanent | permanent | transient (per iteration) |
| Purpose | specify behavior | document agreement Dev↔Customer | explore user interaction | drive planning + conversation |
| Cost visible? | only after all written | — | — | estimate per story, up front |

## Worked Example
The same requirement, three ways. **IEEE 830:** "4.6) The system shall allow a company to pay for a job posting with a credit card. 4.6.1) … accept Visa, MasterCard, American Express. 4.6.2) … charge before posting. 4.6.3) … give a unique confirmation number." **Use case:** "Pay for a job posting," Primary Actor Recruiter, with a 5-step Main Success Scenario plus extensions (expired card → prompt for another). **Story:** "A Recruiter can pay for a job posting with a credit card," with acceptance tests on the back (Visa/MC/Amex pass; Diner's Club fail; bad/missing card IDs; expired cards; over-limit amounts) — the tests map onto the use-case extensions.

## Key Takeaways
1. No amount of upfront thinking can fully specify a nontrivial system; the feedback loop of users seeing software is essential.
2. Focus on users' *goals*, not a checklist of solution attributes.
3. A story ≈ one use-case scenario; story + acceptance tests ≈ a use case.
4. Stories differ from use cases in scope (smaller), completeness (less), longevity (transient), and purpose (planning + conversation vs. documented agreement).
5. Keep UI assumptions out of stories — let the UI emerge in conversation.

## Connects To
- **Ch 13**: turns these contrasts into the positive case for choosing stories.
- **Ch 6 (Acceptance Testing)**: the card-tests = use-case-extensions mapping.
- **Ch 7 (Good Stories)**: constraints, avoiding UI detail.
- **Cockburn, *Writing Effective Use Cases***: external source for use-case templates and essential use cases.
