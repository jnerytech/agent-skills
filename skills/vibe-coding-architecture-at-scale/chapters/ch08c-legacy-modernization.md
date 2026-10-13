# Chapter 8c: AI-Assisted Legacy Modernization

## Core Idea
Legacy has no trustworthy spec, so the SDD order inverts: extract intent from code you cannot yet touch, ratify it, freeze it, and only then refactor under it. This adds no new instrument; it runs every instrument in the book in the one order that is safe when you do not know what the code does.

## Frameworks Introduced
- **The Brownfield Procedure (7 steps, strict order)**:
  - When to use: a 5–10-year-old monolith whose authors left, whose wiki nobody trusts, and whose behavior is defined only by the running code.
  - How:
    1. **Characterize before you touch.** Have the AI write a parameterized characterization-test suite for one module that pins current behavior, bugs and quirks included. Use golden-master/approval tests for complex output. Nothing else is safe until this is green.
    2. **Reverse-engineer the spec, then ratify it.** The AI drafts BDD `.feature` scenarios from code plus characterization tests; a human reads and ratifies *every* scenario, deciding what was meant vs. what was a thirteen-year-old accident. This is the one artifact a model must not solely author.
    3. **Freeze the wire contract.** Generate OpenAPI/Pact from live endpoints and lock it. The inside is negotiable; the wire is not, because you neither control nor can redeploy consumers.
    4. **Draw the real architecture, then ratchet.** Generate the actual dependency graph; encode it as ArchUnit rules that *permit today's tangled edges*. Every refactor may remove a permitted edge, never add one.
    5. **Annotate the landmines.** `@AILocked` load-bearing integrations nobody understands; `@AIContract`/`@AIThreadSafe` characterized behavior to preserve; `@AIDeprecated` code slated for migration so new work routes away. Without VibeTags/Java: CLAUDE.md lists off-limits files, behavior to preserve, deprecated paths, plus `.aiignore`/`.claudeignore`, enforced by the grep-in-CI gate.
    6. **Now, and only now, refactor under the net.** Every change keeps characterization tests and the frozen contract green; CI law and the Inquisitor apply; when a refactor goes sideways, reload rather than untangle.
    7. **Strangle, do not rewrite.** Strangler fig: new functionality is greenfield-disciplined behind the frozen contract; migrate one module at a time. A module graduates from *characterized* to *specified* only when its replacement passes the ratified `.feature` scenarios.

- **Ratchet Pattern (applied to legacy architecture)**: rules start by documenting the mess and only ever tighten.
  - When to use: step 4, any time the current architecture violates the target.
  - How: snapshot existing dependency edges as allowed exceptions; fail the build on any new edge; delete exceptions as refactors remove edges. Architecture can only improve.

- **Behavior Expand-Contract**: changing pinned behavior is a separate, deliberate, spec'd, reviewed act.
  - When to use: after characterization, when a pinned "bug" should actually change.
  - How: pin the old, add the new beside it, retire the old only when nothing depends on it (Chapter 18's expand-contract, applied to behavior instead of schema).

## Key Concepts
- **Characterization test**: a test that records what the code *does*, not what it *should* do, so any change becomes visible.
- **Golden master / approval test**: snapshot-based characterization for output too complex to assert by hand.
- **Recovered intent**: the ratified `.feature` scenarios: a spec written, for once, after the fact.
- **Frozen wire contract**: the OpenAPI/Pact document of what the legacy system emits today; no refactor may break it.
- **Landmine**: a load-bearing integration an agent must not "tidy"; marked `@AILocked`.
- **Characterized vs specified**: "we recorded what it does" vs "we decided what it should do".
- **Strangler fig**: incremental replacement behind a stable contract instead of a rewrite.

## Mental Models
- Think of legacy modernization as the SDD loop run backwards: code → tests → spec → contract → refactor.
- Treat the AI's reverse-engineered spec as a draft; the characterization tests and frozen contract are what make it true.
- Use the ratchet when you cannot fix architecture now but must stop it getting worse.
- Pinning bugs is the point, not a flaw: it separates "refactor" from "behavior change".

## Anti-patterns
- **Refactoring before characterizing**: the Blind Refactor (Chapter 24b) at monolith scale; changes are invisible.
- **Letting the AI solely author the recovered spec**: accidents get canonized as intent.
- **Encoding the wished-for architecture as rules on day one**: the build is red forever; encode the real one and ratchet.
- **The big-bang rewrite**: the move the AI eagerly volunteers for, and the one that forfeits every safety net.
- **Untangling a refactor gone sideways**: reload instead (Chapter 24).

## Why It Works / Failure Mode
Each step builds a net the next relies on: pinned behavior (1) makes ratification grounded (2); the frozen wire (3) protects consumers you cannot redeploy; the ratchet (4) bounds architectural drift; annotations (5) keep agents out of landmines; so the refactor (6) and strangling (7) happen under full coverage. Fails when the order is skipped (refactoring before tests are green) or when behavior changes ride along with refactors instead of being separate spec'd acts.

## Key Takeaways
1. Invert the order: extract → ratify → freeze → refactor.
2. Nothing is safe until characterization tests pin current behavior, bugs included.
3. A human must ratify every reverse-engineered scenario.
4. The wire contract is non-negotiable; the internals are.
5. ArchUnit rules start by permitting the mess and only ever tighten.
6. Strangle module by module; never accept the rewrite.

## Connects To
- **Ch 24b**: Blind Refactor anti-pattern this procedure prevents.
- **Ch 7**: BDD `.feature` scenarios as spec.
- **Ch 18**: OpenAPI/Pact contracts and expand-contract.
- **Ch 6 / Ch 5**: generated dependency graph and ArchUnit ratchet rules.
- **Ch 4 (Section 4.8)**: VibeTags and their hand-written CLAUDE.md equivalent.
- **Ch 21 / Ch 22 / Ch 24**: CI law and grep-in-CI gate, the Inquisitor, reload over untangle.
- **Conclusion**: the greenfield adoption roadmap this chapter complements.
- **Michael Feathers, characterization tests (Working Effectively with Legacy Code)**; **Strangler Fig (Fowler)**; **Approval testing**.
