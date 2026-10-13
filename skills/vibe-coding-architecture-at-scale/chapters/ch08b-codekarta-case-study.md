# Chapter 8b: CodeKarta: A Spec-Driven Case Study

## Core Idea
A complete, machine-readable SPEC.md (dictated libraries, executable guardrail blocks, a verification fixture) turns a single prompt into a working multi-module library in ~13 minutes; a compiler-style tier separation then makes every later feature additive instead of risky. When syntax is free, structure is your only asset.

## Frameworks Introduced
- **Compiler-Style Three-Tier Pipeline (Input → IR → Layout → Render)**: treat diagram generation (or any generator) as a compiler: source → language-agnostic intermediate representation → positioned graph → output. No tier knows about the others' concerns.
  - When to use: whenever a tool mixes *describing* a thing, *placing* it, and *drawing* it, so changing one breaks the other two (the Mermaid/PlantUML/D2 failure mode).
  - How: (1) Tier 1 Input parses source via AST and emits pure data: nodes, edges, groups, no coordinates or colors. (2) Tier 2 Layout writes (x, y, width, height) onto nodes and knows nothing about meaning. (3) Tier 3 Render writes SVG at the given coordinates: no layout math, no parsing. (4) Put a shared `core` IR module at the bottom with zero external deps. (5) Put each tier in its own Maven sub-module so a wrong-direction dependency is a build error, not a convention.

- **Machine-Readable SPEC.md (XML-sectioned spec)**: write the spec as a contract with explicit XML-tagged sections (`<system_context>`, `<dependency_stack>`, `<ai_guardrails>`), not conversational prose, so the agent extracts boundaries without spending attention on sentence parsing.
  - When to use: before writing any code for an agent-built project.
  - How: (1) `<system_context>`: language, build system, core philosophy. (2) Directory architecture tree with one line per module. (3) `<dependency_stack>`: exact library coordinates and versions per tier. (4) `<ai_guardrails>`: numbered, enforceable rules (fault tolerance, token-efficient flat IR, semantic separation, sizing formulas). (5) A verification fixture section. (6) An operational journal section appended over time.

- **Dictate the Libraries**: name every dependency and version in the spec; never let the agent choose.
  - When to use: always, for anything with a supply chain.
  - How: list exact GAV coordinates (e.g. `javaparser-core:3.26.3`, `graphviz-java:0.18.1`) per tier; state "zero external UI frameworks" where you mean none. AI is an exceptional carpenter but a poor supply-chain manager: left alone it picks the library with the most 2018 blog posts, abandoned wrappers, or hand-rolled coordinate math.

- **Spec → PLAN.md → Iteration Loop**: the spec holds durable intent; PLAN.md holds the agent's persisted reasoning; each phase is a spec edit plus a tight prompt.
  - When to use: every phase after the first.
  - How: (1) Update SPEC.md with a new section. (2) Write a focused prompt that names the phase, cites the section, names the module that may change, states the exit condition. (3) Agent revises PLAN.md reasoning and touches only affected tiers. (4) Agent iterates until `mvn verify` is green. Never re-prompt from scratch.

- **Living Spec / Operational Journal**: append timestamped fixes and improvements (FIX-001, IMP-002) as clauses in SPEC.md, not in commit messages.
  - When to use: every time real usage surfaces an edge case.
  - How: add a `system_journal` section; each entry gives an ID, the decision, the reason, and a date. Future sessions read it as part of the contract, so "magic constants" carry their reason (prompt lineage at the spec layer).

## Key Concepts
- **CodeKarta**: a Java-native architecture-mapping engine that extracts module, class, sequence, and exception-flow diagrams from source and renders SVG.
- **Intermediate Representation (IR)**: a flat, language-agnostic graph of nodes/edges/groups; kept flat to avoid exhausting context windows.
- **`<ai_guardrails>` block**: executable policy clauses the agent must follow; part of the repo-as-constitution.
- **Verification fixture**: a canonical example project (`example-shipping-system`) that integration tests parse on `mvn verify`; if extraction fails, the build fails.
- **PLAN.md**: an agent-written reasoning document (decisions plus rationale), not a to-do list; persists reasoning across sessions.
- **Blast radius**: the set of modules a change can touch; with decoupled tiers it is knowable before writing code.
- **Shattered Path / Exception Flow Map**: a diagram of exception propagation (`EXCEPTION_PROPAGATION` edges, try-boundary groups) that exposes the area where vibe-generated code is weakest.
- **Mirror vs constitution**: a visualizer shows what *is*; enforced annotations and tests define what *should be*.

## Mental Models
- Think of the spec as the instruction set and the code as the output, never the input.
- Policy the build does not read is a comment: a guardrail only shapes behavior if something fails when it is violated.
- Use CodeKarta-style visualization for *archaeology* (understanding inherited code); use guardrails (VibeTags, ArchUnit, living diagrams) for *engineering* (keeping architecture true).
- Spend an hour on the spec to save three days of prompt-loop back-and-forth.

## Anti-patterns
- **Entangled describe/place/draw concerns**: one relationship tweak scrambles the layout; an AI-hallucinated bracket crashes the whole DSL.
- **Letting the agent choose libraries**: it picks deprecated wrappers or rebuilds coordinate math from scratch that breaks at the fifth node.
- **Prose specs**: the agent burns attention parsing sentences instead of extracting boundaries.
- **Over-specifying the prompt**: telling the agent which classes or visitor pattern to use; the prompt should name phase, section, module, exit condition only.
- **Knowledge only in git log**: every new session starts with no memory of lessons learned the hard way.
- **Hand-maintained diagrams**: they go stale (people are confidently wrong) or become a second job.

## Code Examples
```markdown
# Specification: code-karta (Java Architecture Mapping Engine)
<system_context>
- Language Stack: Java (JDK 21+)
- Build System: Maven Multi-Module Project (Root Reactor)
- Core Philosophy: Strictly decoupled, compiler-style 3-tier pipeline.
  Zero visual logic in the parser; zero language logic in the renderer.
</system_context>
<dependency_stack>
- Tier 1 (Input/AST):   com.github.javaparser:javaparser-core:3.26.3
- Tier 2 (Layout Math): guru.nidi:graphviz-java:0.18.1
- Tier 3 (Rendering):   Zero external UI frameworks. Pure Java String/XML → SVG.
</dependency_stack>
<ai_guardrails>
1. High Fault Tolerance: parsers never crash on malformed files. Log a warning,
   bypass the broken block, infer context gracefully.
2. Token Efficiency: keep the IR flat and compressed.
3. Strict Semantic Separation: Parser = WHAT connects to WHAT.
   Layout = WHERE it sits. Renderer = HOW it looks.
4. Compute node widths before Tier 2:
   Math.max(minWidth, label.length() * charMultiplier)
</ai_guardrails>
```
- **What it demonstrates**: a spec with dictated dependencies and enumerated, enforceable guardrails that an agent can execute autonomously.

```text
I've added Phase 3 ('Exception Flow Mapping') to SPEC.md. Read the new target
requirements in Section 6-D, adjust the core graph models in code-karta-core if
you need new edge types, and implement the exception AST traversal logic. Run
verification checks until compilation returns green.
```
- **What it demonstrates**: the iteration-phase prompt shape (phase + section + module + exit condition, no implementation detail).

## Reference Tables
| Tier | Module | Knows | Must not know |
|---|---|---|---|
| Core | `code-karta-core` | IR data model | anything external (zero deps) |
| 1 Input | `code-karta-input` | AST (JavaParser): WHAT connects | coordinates, colors |
| 2 Layout | `code-karta-layout` | WHERE: x, y, w, h | meaning of nodes |
| 3 Render | `code-karta-render` | HOW: SVG shapes/text | parsing, layout math |

| Phase 1 result | Value |
|---|---|
| Tests | 62, 0 failures, 4 modules |
| Java added | 1,962 lines |
| API time / wall clock | 29 s / 12 min 52 s |
| Cost | $1.51 |

## Worked Example
**Phase 1.** Prompt: "Make a plan from SPEC.md and keep it updated in PLAN.md including your reasoning, then implement the plan and write tests for everything except the examples, then run mvn clean compile until it compiles and all tests pass." The agent first writes PLAN.md with auditable decisions: Java 21 LTS over the spec's 24 target; a pure-Java `SimpleLayoutEngine` (BFS/topological layering) behind a `LayoutEngine` interface instead of native Graphviz/ELK, which break on a clean CI compile; `java.util.logging` over SLF4J to avoid cross-module binding deps; mutable POJOs for coordinates, with immutability enforced *architecturally* (parsers never call layout, renderer never calls parsers); Gradle Kotlin DSL dual build. Output: module, class (`ExpressCargo extends Cargo implements ShippingUnit`), and sequence (`OrderProcessor.submit()` → `InventoryService.checkStock()`) diagrams from one run.

**Phase 3, Exception Flow.** The SPEC edit adds Section 6-D: distinguish `CALL` from `EXCEPTION_PROPAGATION` edges; wrap every `TryStmt`'s inner calls in a `GraphGroup`; emit an exception edge from a method throwing a declared checked exception up to its caller. A fixture `OrderProcessor` has a `processOrder` catching `InventoryException` and a `submit()` throwing `OrderValidationException`. Resulting change: one new enum value, one AST visitor/group rule, three CSS classes (red dashed = uncaught, orange = caught-and-wrapped, gray = caught-and-suppressed). Layout engine, SVG format, and module structure: untouched.

**Journal.** `FIX-001`: enforced a default 150px minimum box width in Tier 2 so short names like `A.java` don't clip (2026-05-18). `IMP-002`: javaparser upgraded for Java 24 record patterns in pattern-matching switches.

## Why It Works / Failure Mode
- **Three tiers**: tiers share no mutable state, so a new diagram type is additive; it cannot break existing renderers because no shared path exists. Breaks when tier separation is only a convention (one package, no module boundary): the agent will take the shortcut and the blast radius becomes unknowable.
- **Complete spec → autonomous first prompt**: the agent needs no hand-holding because libraries, boundaries, and the definition of "correct" (the fixture) are fixed up front. Breaks when guardrails are not checked by the build. Then they become decoration, and the visualizer becomes a mirror that drifts into a lie within months unless VibeTags/ArchUnit/living diagrams make the architecture law.

## Key Takeaways
1. Write the spec before any code, in XML-sectioned machine-readable form.
2. Dictate exact libraries and versions; the agent builds, you supply the materials.
3. Put a verification fixture in the spec and run it on `mvn verify` so "correct" is defined on day one.
4. Enforce tier boundaries as module boundaries; the payoff is cheap, predictable features later.
5. Iterate by editing the spec and issuing a short phase prompt; let PLAN.md carry reasoning across sessions.
6. Log fixes as timestamped clauses in the spec so future sessions inherit the lessons.
7. A diagram tool is archaeology; enforced annotations and tests are engineering. The first run is free; the second year is free only if architecture is law.

## Connects To
- **Ch 7**: spec as guardrail and repo-as-constitution; the `<ai_guardrails>` block is a constitution clause.
- **Ch 8**: the tool loop this case study runs; reproduce via Spec Kit (`specify init`, `specify plan`, `specify tasks`).
- **Ch 4**: VibeTags (`@AIArchLayer`, `@AILocked`, `@AIIgnore`, `@AIPerformance`, sidecar aggregation) keep context rules from rotting.
- **Ch 5**: ArchUnit turns what the exception map shows (e.g. `IOException` leaking from `core` to `api`) into a build failure.
- **Ch 6**: living diagrams regenerated every build make stale diagrams impossible.
- **Ch 12**: `forge.sh` skills learned from `@AIArchLayer` tags and package structure.
- **Compiler design (source → IR → codegen)**; **Spring Modulith** (package structure as enforceable law).
