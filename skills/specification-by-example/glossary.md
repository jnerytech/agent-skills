# Glossary — Specification by Example

**Acceptance Test-Driven Development (ATDD)** — driving development from acceptance tests written as examples before coding; one of the named practices SBE unifies (Ch 2).

**Agile acceptance testing** — collaborative acceptance testing using business-readable examples; a sibling name for SBE (Ch 2).

**Automation layer** — the glue/fixture code connecting an executable specification to the system under test; holds setup defaults and translation, *not* business logic (Ch 9).

**Below the skin of the application** — automating just under the UI (at service/domain boundaries) so tests are fast and stable without going through the interface (Ch 9).

**Boomerang** — a story that keeps coming back because it was signed off without genuine shared understanding; an adoption warning sign (Ch 4).

**Business goal** — the measurable business outcome a change should achieve; the starting point for deriving scope (Ch 2, Ch 5).

**Continuous validation environment** — a dedicated, production-like environment that runs executable specifications frequently to keep documentation alive (Ch 10).

**Documentation-centric model** — treating the executable specifications as the authoritative project documentation rather than a by-product of testing (Ch 3).

**Domain language (ubiquitous language)** — the shared business vocabulary in which specifications are written so they read as requirements, not scripts (Ch 8, Ch 11).

**Example-Driven Development** — developing from concrete examples; another sibling name for SBE (Ch 2).

**Executable specification** — a specification written in business language that a machine can run as a test; the core SBE artifact (Ch 2, Ch 3, Ch 9).

**Given-When-Then** — structured language for specs: Given a context, When an event, Then an outcome; makes examples self-explanatory and testable (Ch 8).

**Just-in-case code** — code written for unrequested future needs, often surfacing when specs aren't goal-driven; a warning sign (Ch 4).

**Key example** — the minimal set of illustrative examples that pins down a business rule, deliberately *not* exhaustive (Ch 2, Ch 7).

**Key process patterns** — the seven recurring practices successful teams share: deriving scope, specifying collaboratively, illustrating, refining, automating, validating, evolving docs (Ch 2).

**Living documentation** — documentation derived from continuously-validated executable specs; authoritative because it fails the build when wrong, and cheap to maintain (Ch 3, Ch 11).

**Low-fi prototype** — a rough UI sketch used to illustrate interface requirements without over-specifying (Ch 7).

**Pair-writing** — two people (e.g. analyst + developer) writing specifications together; a collaboration model suited to mature products (Ch 6).

**QUPER model** — a model for specifying sliding-scale nonfunctional requirements using utility breakpoints and cost barriers (Ch 7).

**Reference example** — a canonical worked example used when a requirement is impossible to quantify precisely (Ch 7).

**Refining** — turning raw collected examples into a focused, precise, self-explanatory specification (Ch 8).

**Scope** — what the team will build to meet a goal; derived from goals, never accepted as a disguised solution (Ch 2, Ch 5).

**Script (vs specification)** — a step-by-step UI/flow recording; *not* a specification because it describes mechanics, not business intent. "Scripts are not specifications" (Ch 8).

**Shotgun surgery** — one change forcing edits across many tests/specs, signalling poor structure; a warning sign (Ch 4).

**Sign-off** — formal approval; SBE prefers signing off on *scope* (or exported living documentation) rather than on individual specifications (Ch 4).

**Specification by Example (SBE)** — the umbrella method: derive scope from goals, specify collaboratively with realistic examples, automate as executable specs, validate frequently, evolve into living documentation (whole book).

**Specification workshop** — a collaborative session (often all-team) where business, dev, and test refine examples into specs (Ch 6).

**System under test (SUT)** — the application the executable specification validates, sitting below the automation layer (Ch 9).

**Test double** — a simplified stand-in for an external system, used to make validation fast and reliable (Ch 10).

**Three Amigos** — a small workshop with business, development, and testing perspectives to clarify examples; suited to domains needing frequent clarification (Ch 6).

**Warning signs** — adoption anti-patterns: tests that change frequently, boomerangs, organizational misalignment, just-in-case code, shotgun surgery (Ch 4).
