# Chapter 4: Initiating the changes

## Core Idea
Start the change by implementing one practice that delivers short-term value (quality or saved time), then let momentum build the rest; pick the starting point that matches your team's situation, and fold collaboration into whatever delivery cadence you already run rather than seeking a universal process.

## Frameworks Introduced

### Starting points for the process change (pick by situation)

- **Implement Specification by Example as part of a wider process change**: bundle the core ideas into a larger agile migration.
  - When: On greenfield projects (or any team already moving to Scrum/XP/Kanban).
  - How: Adopting an agile process is "shock therapy" anyway, so add Specification by Example at the same time. Teams that did this reported fewer problems and faster adoption than teams starting from a dysfunctional Scrum environment — largely because they had support (on-site consultants or a member with prior exposure).

- **Focus on improving quality**: make quality, not a named process, the banner.
  - When: Individuals are likely to resist a labeled process change (Scrum/agile/Kanban).
  - How: Ask all members for improvement suggestions; use them as inspiration (uSwitch did this and adopted most patterns with little resistance). Identify the biggest obstacle to delivering high-quality software, then solve it (David Anderson's Kanban first step). Visualize release activities when devs and testers disagree on "acceptable quality" — e.g. LMAX's release candidate board.

- **Start with functional test automation**: the path of least resistance for code-heavy projects.
  - When: Applying to an existing project that lacks automated functional tests and relies on manual testing.
  - How: Automate functional tests first, then gradually shift from testing-after-development to executable specifications that guide development. Removes the testing bottleneck, engages testers with developers, forces a more testable architecture, frees testers for specification workshops and exploratory testing, flushes out bugs that prove value to stakeholders. **Automate using a tool for executable specifications, not record-and-replay tools** — otherwise you don't get the benefits.
  - Sub-pattern — **Start by automating high-risk parts of the system**: covering an entire legacy system is futile; automate enough to show value and learn the tools, focus on risky/expensive-to-fail areas, then build coverage gradually as changes come.

- **Introduce a tool for executable specifications**: break the wall between testers and developers.
  - When: Testers already own full functional test automation.
  - How: No need to prove test-automation value or fix environments; the problem is cultural (and sometimes financial — per-seat licensed tools like QTP intentionally keep devs/BAs away). Use a moment when the existing toolkit can't test something as the excuse to bring in an executable-specifications tool. Rob Park used a proof-of-insurance PDF QTP couldn't handle to introduce JBehave so developers could run tests on their own machines; Pierre Veragen at Weyerhaeuser justified moving to FitNesse because rewriting broken tests cost less than re-recording them.

- **Use test-driven development as a stepping stone**: extend TDD to business rules.
  - When: Developers already have a good understanding of (unit) TDD, especially greenfield.
  - How: No need to demonstrate test value or make code testable. Frame executable specifications as "tests for business functionality" — TDD applied to business rules (a.k.a. acceptance-test-driven development). Lisa Crispin at ePlan Services paired with one developer on one story's test, repeated with different people/stories each sprint; devs saw value immediately when a test surfaced a misunderstood requirement.

### Culture-change patterns

- **Avoid 'agile' terminology**: implement the practice without the jargon.
  - When: Working in an environment resistant to change.
  - How: Don't say user stories, acceptance tests, or executable specifications. Describe it only as "gathering examples to clarify requirements, deriving tests, and automating them." Make problems visible and gently push people to solve them so they feel ownership. Adam Knight grew it at RainStor with nobody aware of the name; Pierre Veragen took ~6 months at Weyerhaeuser to get a legacy team to stop seeing testing as a post-development phase, mostly because the suite had to grow large enough that failing tests on a dev's machine clearly pointed to their own bugs.

- **Ensure you have management support**: big role changes need backing.
  - How: Roles shift (testers do analysis, devs test, analysts change how they gather requirements, business users actively specify). Productivity drops for the first several months before it rises, so management must understand and approve. If management responds with pressure instead of support, people retreat to old ways and protect their position. Share Ch.1 success stories; if that fails, take smaller, less-ambitious steps.

- **Sell Specification by Example as a better way to do acceptance testing**: eliminate UAT as a separate delivery phase.
  - How: Frequent validation of comprehensive executable specifications makes manual post-delivery acceptance testing unnecessary (exploratory testing still happens). Easiest benefit to quantify: ~12+ releases/year × 3 days UAT each = months of waste; framing it as "get to market two months earlier every year" justifies the investment.

- **Keep one person on legacy scripts during migration ("the Batman" / "Sacrifice One Person")**: protect the team's forward momentum.
  - When: Introducing functional automation to legacy systems.
  - How: Dedicate one person to maintain old tests / urgent bugs (Shore & Warden's "Batman"; Cockburn's "Sacrifice One Person") while the rest build the new suite. Markus Gärtner ran two on the new FitNesse tests, three on legacy, shifting people over until old scripts were thrown away. Rotate the role to break knowledge silos and get everyone's buy-in.

- **Track who is running — and not running — automated checks**: visibility nudges participation.
  - When: Developers are reluctant to participate.
  - How: Veragen put a hook in the fixture code reporting *when and where* tests ran (not results), so he could approach people who weren't running them and find out what was wrong. Like publishing speed-camera locations — people run checks when they know someone's looking. Useful for larger teams a coach can't shadow.

### Sign-off & traceability patterns

- **Keep executable specifications in a version control system**: traceability for free.
  - How: Plain-text spec files tag/branch with source code, give you who-changed-what-when-and-why instantly, link specs to code through the automation layer, and are less likely to disappear than specs in a separate requirements/test tool. Cited as one of the most important practices for a successful implementation.

- **Get sign-off on exported living documentation**: when signing off iteration by iteration.
  - How: Export the next iteration's executable specifications to Word/PDF (Cucumber exports PDF directly) and sign off on that.

- **Get sign-off on scope, not specifications**: when signing off longer milestones.
  - How: For batches larger than one iteration, sign off user stories or use cases, not detailed specs. Rob Park kept a Waterfall story-card approval but cut the BA template from 8 pages to 2; executable specifications became the only source of requirements once scope was approved.

- **Get sign-off on 'slimmed down use cases'**: when regulatory sign-off requires details.
  - How: Mike Vogel (pharma, Scrum+XP) used "structured stories" — use cases that name data chunks but factor data/decisions into separate sections, with *examples living in the acceptance tests, not the use case*. Built a <100-page regulatory requirements document; examples evolved collaboratively with the customer.

- **Introduce use case realizations**: when all details are required for sign-off.
  - How: Matthew Steer (RUP, full sign-off required) added use case realizations — examples and scenarios illustrating each use case, with parameter tables and flows — getting Specification by Example into a formal process "under the radar of the methodology police."

## Key Concepts
- **Living documentation**: spec artifacts that stay current and provide traceability, making agile viable in regulated industries (e.g., first US nuclear-industry agile project).
- **Boomerang**: a story/backlog item that returns for rework within a month of release (extending requirements for innovation does not count).
- **Story champion / story sponsor**: one developer who stays with a story start-to-finish for continuity as pairs rotate (SNS); the sponsor variant (Ultimate Software) also handles cross-team comms and roadblocks.
- **SKIT (Story Knowledge and Information Transfer)**: an in-depth session where the dev/tester pair reviews scenarios with the product analyst before they become requirements.
- **Defect Detection Efficiency (DDE)**: quality metric — Ultimate Software's team hit 99% (Q1–Q3 2010).
- **Differences from Waterfall analysis**: fast feedback via small chunks, efficient communication over long documents, shared ownership (no throwing over walls), integrated cross-functional teams. Dan North: "BDD is V-Model compressed into two weeks."

## Mental Models
- Use **wider-process-change bundling** when you're already going greenfield/agile; use **functional test automation first** when you're on an existing code-heavy project with manual testing.
- Use a **quality banner** when people will fight any named process; use **avoid-agile-terminology** when the whole environment is change-averse.
- Use **TDD as a stepping stone** when developers already trust unit tests — just reframe specs as business-rule tests.
- Use **the Batman** when legacy tests would otherwise drag the whole team backward during migration.
- Use **sign-off on scope** for long milestones, **exported living docs** for per-iteration sign-off, and **use case realizations** when regulators demand every detail.

## Anti-patterns
- **Don't make test automation the end goal**: business users treat "testing" as not their concern, and devs automate to minimize effort, producing technical *scripts rather than specifications* — which become an impediment to change, not a facilitator. Everyone must know automation is only a step.
- **Don't focus on a tool**: programmers picking FitNesse/Cucumber in isolation rarely succeed; they misuse a nontechnical spec tool to manage developer-oriented tests and waste effort. Only Ian Cooper's team at Beazley succeeded — by pushing hard to involve testers/BAs.
- **Tests that change frequently (warning sign)**: Google's heuristic — when a test breaks, if the *code* changed to fix it, it's a good test; if the *test* changed and code didn't, it's bad. Business rules should be more stable than the tech implementing them; frequently-changing specs were written poorly. Also track time spent refactoring specs/automation.
- **Boomerangs (warning sign)**: should drop to rare after adoption; if the rate doesn't fall, the process is wrong. Tracking takes minutes per iteration and builds the business case (compare boomerang time to "wasteful overhead" complaints about automation).
- **Organizational misalignment (warning sign)**: you should finish a story including exploratory testing inside the same iteration; testers lagging behind development is wrong. So is misaligned analysis — too much up front, analyzing things not implemented soon, or being late when details are needed.
- **Just-in-case code (warning sign)**: code written without being needed (Poppendiecks' biggest waste). Watch for people building more than was agreed/specified; also discuss explicitly what's *out of scope*.
- **Shotgun surgery (warning sign)**: a classic code smell applied to living docs — if one small production-code change forces changes to many executable specifications, you're doing it wrong. Organize so one small code change → one small test change.

## Worked Example
**Global Talent Management team at Ultimate Software (Kanban flow).** One of 16 teams on an HR system: a product analyst (combined analyst/product owner), a UX expert, four testers, ten developers, eight months in. The product analyst writes each story at a high level as "story points" — bullet-list items explaining the story, not complexity estimates — avoiding technology-specific language, then adds it to the Kanban backlog. In a daily 30-minute meeting, lead engineers and the product analyst run the backlog, checking each story is sliced correctly, makes sense, and is implementable in four days or less (a self-imposed limit), clarifying questions and dependencies. The story then queues for specification: a developer who'll implement it pairs with someone focused on testing to outline the specifications — the developer's intimate code knowledge cuts down necessary tests and roots out inconsistencies and design flaws missed in the initial review. The tester completes scenarios in Given-When-Then, then the pair and product analyst hold an in-depth **SKIT** session; once the analyst approves, those scenarios *are* the requirements, with no further changes (beyond minor text) until delivery. The developer automates the scenarios — usually before writing production code — querying objects rather than driving the GUI, which makes execution quicker and more stable and frees the tester for exploratory testing. All executable specifications must pass to finish development; tests run again integrated with other teams; a quick product demo gets the analyst's sign-off. Result: **99% Defect Detection Efficiency**. (BNP Paribas's Sierra team fit the same collaboration into XP iterations — BAs prepare acceptance criteria with off-site stakeholders before each two-week iteration; Sky Network Services fit it into Scrum with a two-phase upfront-then-review spec flow and colored stickers signalling each role's review.)

## Key Takeaways
1. Begin with one short-term-value practice matched to your situation; momentum, not a master plan, drives the rest.
2. Functional test automation is the low-hanging fruit for legacy/manual projects — but it's a *step*, never the end goal, and must use an executable-specifications tool, not record-and-replay.
3. In resistant environments, drop the jargon: describe only "gather examples, derive tests, automate," make problems visible, and let the team own the solution.
4. Big role changes fail without management support; expect a productivity dip for the first few months and get buy-in upfront.
5. There's no universal process — fit collaboration into your existing flow/iterations (Kanban, XP, Scrum all worked with different shapes).
6. Store executable specifications in version control for free traceability; satisfy sign-off needs by signing off scope, exported living docs, or slimmed-down use cases / use case realizations rather than detailed specs.
7. Track warning signs as adjustment signals (not targets): frequently-changing tests, boomerangs, organizational misalignment, just-in-case code, shotgun surgery.

## Connects To
- **Ch 1**: success stories and benefits used to win management support and build the business case.
- **Ch 6**: "Choosing a collaboration model" — designing the process to fit your team.
- **Ch 8**: "Scripts aren't specifications" — the failure mode behind making test automation the end goal.
- **Ch 9 & 11**: designing well-structured executable specifications and "Listen to your living documentation" — how to avoid shotgun surgery and high maintenance cost.
- **Ch 12**: the uSwitch case study (focus-on-quality starting point).
