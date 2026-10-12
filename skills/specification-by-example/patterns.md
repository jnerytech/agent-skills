# Patterns — Specification by Example

Named process patterns from the book. Most carry the author's explicit **When:** trigger.

## Deriving scope from goals (Ch 5)

## Have developers provide the 'I want' part of user stories
**When**: business users trust the development team.
**How**: business states goal + who benefits; developers propose the scope/solution.
**Trade-offs**: faster, taps technical creativity; needs trust to avoid gold-plating.

## Ask how something would be useful / Ask for an alternative solution
**When**: a requirement arrives as a pre-baked solution.
**How**: peel back to the goal — "how would that help?" / "what else could achieve it?"
**Trade-offs**: surfaces cheaper options; can feel like pushback to stakeholders.

## Make sure teams deliver complete features
**When**: large, multisite projects.
**How**: slice scope so each team owns an end-to-end feature, not a horizontal layer.

## Specifying collaboratively (Ch 6)

## Try big, all-team workshops
**When**: starting out with SBE. **How**: whole team explores examples together. **Trade-offs**: best shared understanding; expensive in people-time.

## Try smaller workshops ('Three Amigos')
**When**: domain requires frequent clarification. **How**: one each of business/dev/test refine examples. **Trade-offs**: cheaper, frequent; narrower perspective.

## Pair-writing
**When**: mature products. **How**: analyst + developer co-write specs. **Trade-offs**: efficient; relies on individuals' shared context.

## Try informal conversations
**When**: business stakeholders are readily available. **How**: clarify examples ad hoc. **Trade-offs**: lightweight; risks lost decisions if undocumented.

## Illustrating using examples (Ch 7)

## The four qualities of good examples
**How**: every example must be **precise** (no yes/no, no abstract equivalence classes), **complete** (experiment with data, cover the rule), **realistic** (use real customer data; avoid invented data), **easy to understand** (avoid exhaustive combinatorial cases; look for implied concepts).
**Trade-offs**: realistic+precise examples cost more to gather but eliminate ambiguity.

## Illustrating nonfunctional requirements
**How**: "Get precise performance requirements" (When: performance is a key feature), "Use low-fi prototypes for UI", "Try the QUPER model" (When: sliding-scale reqs), "Use a checklist for discussions" (When: cross-cutting concerns), "Build a reference example" (When: impossible to quantify).

## Refining the specification (Ch 8)

## Make specifications self-explanatory
**How**: descriptive title + short goal paragraph; "Show and keep quiet" to test clarity; don't overspecify examples; **Given-When-Then**; keep in domain language.
**Trade-offs**: readable by stakeholders; takes discipline to resist scripting.

## Keep specs about business, not software
**How**: "Scripts are not specifications"; don't create flow-like descriptions; don't couple to code/UI; "Apply defaults in the automation layer" instead of restating setup.

## Automating validation without changing specifications (Ch 9)

## Three-layer model
**How**: specification (business language) → automation layer (glue/fixtures) → system under test; dependency flows one way; the spec never changes to suit the tool.
**Trade-offs**: clean separation; requires investing in the automation layer as first-class code.

## Automate below the skin / along system boundaries
**When**: checking session/workflow constraints, complex integrations.
**How**: drive the app just under the UI; "Don't check business logic through the UI"; "Don't replicate business logic in the automation layer"; "Avoid recorded UI tests".

## Validating frequently (Ch 10)

## Reduce unreliability
**How**: "Find the most annoying thing, fix it, and repeat"; "Identify unstable tests using CI history"; dedicated continuous validation environment; fully automated deployment; "Wait for events, not for elapsed time"; isolate/simplify external systems with test doubles.

## Get feedback faster
**How**: separate quick vs slow tests; current-iteration pack; parallelize runs; break long packs into modules; keep overnight packs stable.

## Manage failing tests
**How**: "Create a known regression failures pack"; "Automatically check which tests are turned off" so disabled tests don't hide.

## Evolving a documentation system (Ch 11)

## Keep living documentation healthy
**How**: **easy to understand** (don't create long specs; look for higher-level concepts), **consistent** (evolve a language; base on personas for web projects; document building blocks), **organized for access** (by stories → functional areas; tags not URLs; "Listen to your living documentation").

## Initiating the changes (Ch 4)

## Choose an adoption entry point
**How**: "Implement SBE as part of a wider process change" (When: greenfield); "Start with functional test automation" (When: existing project); "Use TDD as a stepping stone" (When: devs understand TDD); "Avoid 'agile' terminology" (When: change-resistant env); "Don't make test automation the end goal".

## Sign-off & traceability
**How**: keep executable specs in version control; "Get sign-off on scope, not specifications"; "Get sign-off on exported living documentation" (iteration by iteration); "Introduce use case realizations" (When: all details required for sign-off).
