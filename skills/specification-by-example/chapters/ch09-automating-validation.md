# Chapter 9: Automating validation without changing specifications

## Core Idea
The right automation for executable specifications keeps a human-readable specification (business) decoupled from automation code (glue/fixtures) that drives the system under test — so you validate without distorting the spec. If automating forces you to rewrite the spec, the telephone game restarts and the value of refinement is lost.

## Frameworks Introduced

- **The three-layer model**: specification (business-readable text/HTML) → automation layer (fixtures/step definitions, in a programming language) → system under test (APIs, DB, or UI).
  - When to use: every executable specification.
  - How: tools extract inputs/expected outputs from the spec and pass them to automation code; automation code calls APIs, hits the DB, or drives the UI. The automation layer depends on the spec, never the reverse — that one-way dependency is what lets you change specs without recompiling, and automate without changing specs.

- **Is automation required at all?**: weigh long-term living-documentation benefit vs. short-term cost before opting out.
  - When to use: deciding whether to use a "natural language" executable-spec tool vs. a purely technical regression tool.
  - How: technical tools give cheaper maintenance and good regression tests but specs stay developer-only; executable-spec tools preserve specs for business communication and living documentation. Dropping automation is a local optimization that forfeits the biggest long-term benefit — control the maintenance cost instead of abandoning it.

- **To learn about tools, try a simple project first**: spike on a small, isolated piece of work.
  - When: working on a legacy system / adopting both SbE and agile at once.
  - How: convert a few existing tests to the new tool to spread tool experience across the whole team at low risk; then get an external consultant to review once you have something concrete.

- **Plan for automation upfront**: expect a productivity drop and undercommit scope.
  - When: systems not designed for testability.
  - How: automation is front-loaded (basic components, spec format, integration, stable environments). Undercommit scope so automation finishes within the iteration; optionally treat the automation toolkit as a separate product with its own backlog and a fixed % of team time (same team builds both).

- **Gain trust with UI tests**: drive specs through the UI temporarily to convince skeptics.
  - When: team members / business users are skeptical of below-the-UI automation.
  - How: hide UI interactions in the automation layer (never put them in the spec); keep the layer flexible so you can drop below the skin later, and reduce UI test count once trust is earned.

- **Automate along system boundaries**: specify and automate only within your responsibility.
  - When: complex, heterogeneous integrations.
  - How: decouple external inputs (e.g., a test page that prepares the data an IVR/voice-to-data system would send), validate all business rules on your side; cover the cross-component handshake with a few separate technical integration tests.

- **Automate below the skin of the application**: bind below the UI to the HTTP/controller layer.
  - When: checking session and workflow constraints that "only" the UI can reach.
  - How: send a hash-map resembling the HTTP request with defaults overridden per test (WebRat, Twill, Selenium HtmlUnit driver), or bind straight to the MVC controller. No browser → parallel, faster, more reliable (fewer moving parts; browsers lock user profiles).

- **Avoid using prepopulated data** / **Try prepopulated reference data** / **Pull prototypes from the database**: a graded data-setup strategy.
  - When (avoid prepopulated): logic that's not data driven → write data-agnostic tests.
  - When (reference data): data-driven systems → "nuke and pave" the DB, populate config + immutable domain reference data; each test creates and cleans up its own transaction data.
  - When (pull prototypes): legacy data-driven systems where building an object from scratch is error-prone → clone a real object from the DB (background generator) and change only the relevant properties.

## Key Concepts
- **Automation layer / fixtures / step definitions**: programming-language glue that connects a spec to the system; needs recompile/redeploy when changed.
- **Living documentation**: the long-lived payoff that automation-without-changing-specs guarantees the correctness of.
- **Three levels of UI automation**: business-rule level (what's exercised), user-workflow level (how, as activities), technical-activity level (concrete clicks/steps).
- **Front-loaded effort**: disproportionate work at the start that drops sharply as basic components stabilize and get reused.
- **Validation process**: *how* something is tested (vs. *what* is tested) — belongs in the automation layer, not the spec.

## Mental Models
- Use the three-level decomposition when automating through a UI: spec stays at business-rule level; the automation layer assembles workflow-level steps from technical-activity blocks.
- Use below-the-skin binding when you can; reserve UI execution for gaining trust, JavaScript/form-field UI logic, or legacy systems lacking a clean API.
- Use prepopulated reference data when the domain is data-driven; use data-agnostic tests when it is not.
- Use "what is the user trying to achieve" (goal) rather than "type/click" scripts to make tests resilient to UI change.

## Anti-patterns
- **Don't postpone or delegate automation**: marking stories done without an objective automated criterion causes rework; delegating to separate testers/consultants means developers never make the system testable.
- **Avoid automating existing manual test scripts**: manual scripts reuse one long interdependent context; as automation a single failure cascades and hides the real cause. Replace one big script with many small, focused, independent tests.
- **Don't treat automation code as second-grade code**: specs and fixtures are first-class — put your best architects on the test framework; junior-built test systems pick wrong approximations and become unmaintainable.
- **Don't replicate business logic in the automation layer**: faked/"fantasy" state passes while the real flow fails, giving false assurance — use the real system to create state.
- **Don't check business logic through the UI**: UI automation is slow and costly; go to the service/API level for business logic.
- **Specify UI at object level (avoid)**: writing "click/point" Selenium/FitNesse steps in specs couples them to the GUI — one ribbon control broke everything. Specify UI functionality at a higher level of abstraction.
- **Avoid recorded UI tests**: record-and-replay is unreadable, costly to maintain (70,000 lines re-recorded over six months), and requires the UI to already exist — but SbE starts before the software does.

## Worked Example
Iowa Student Loan and the "automate below the skin" pattern. Tim Andersen's team needed to validate workflow/session rules on a web app. Instead of launching a browser, their fixtures ("personas") sent a hash-map shaped like the HTTP request — default values overwritten with only the fields that mattered for each test — straight to where the real HTTP requests land. This used real objects and real state, ran in parallel, and ran far faster than a browser (which locks user profiles to one check at a time). Christian Hassa pushed one level deeper, binding specs directly to the MVC controller and skipping HTTP entirely; given the choice he'd bind *all* specs to the controller and only a limited set to the UI, because UI binding costs significantly more and isn't the primary value.

Crucially the team also refused to fake state: rather than minting a loan from test-helper code, they leveraged the real application (via personas) to set a loan into a valid state — deleting roughly a third of their automation code and exposing real bugs their old fake-state tests had masked. The specification itself never mentioned HTTP, controllers, or browsers — those lived entirely in the automation layer, preserving the one-way dependency that lets the spec stay business-readable.

## Key Takeaways
1. Refined specs should be automated with as little change as possible; the one-way dependency (automation → spec) is the mechanism.
2. The automation layer defines *how* something is tested; the specification defines *what* is tested.
3. Automate below the UI whenever possible (HTTP or controller layer) — UI automation is a last resort, justified mainly to gain trust or to check UI-only logic.
4. Plan for a front-loaded productivity drop; undercommit scope so automation lands within the iteration, and never postpone or delegate it.
5. Treat specs and fixtures as first-class code; put strong people on the framework and never replicate business logic in it.
6. Replace long interdependent manual scripts with many small, focused, independent tests; avoid record-and-replay.
7. Manage test data deliberately: prepopulate only immutable reference data, keep tests data-agnostic when logic isn't data-driven, and clone DB prototypes for legacy domains.

## Connects To
- **Ch 8**: refining specs ("scripts are not specifications"; business functionality, not software design) — Ch 9 keeps that refinement intact by pushing all software-design detail into the automation layer.
- **Ch 10**: validating frequently and further controlling long-term maintenance cost (quick checks for reference data, large/complex infrastructures).
- **Ch 7**: reference examples — Ch 9 notes usability/layout reference examples are not worth automating.
- **Ch 11**: "Listen to your living documentation" — a from-scratch object that's hard to build may signal a wrong domain model.
