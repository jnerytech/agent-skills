# Chapter 14: Vibe Coding Playbook: Prompting as Engineering

## Core Idea
The Vibe Coding Playbook (github.com/RiyaParikh0112/vibe-coding-playbook) treats *how you phrase the ask* as an engineering problem: replace conversational prompts — sticky notes that hand the agent an improvisation budget the size of the feature — with XML-structured prompts that physically separate objective, context, constraints, deliverables and an approval gate. It pairs this with a three-layer quality system that routes each class of defect to the cheapest capable checker.

## Frameworks Introduced
- **XML Prompting**: structure every non-trivial request as tagged sections so each is independently verifiable.
  - When to use: prompts produce inconsistent output and you need to tighten the specification of the ask itself (complex features, API design, schema, legacy migration, performance debugging).
  - How: wrap in `<planning_request>`; put the goal in `<objective>` (prefixed "PLAN FIRST"); put stack and patterns in `<context>`; enumerate `<constraints>` (never imply them); list concrete `<deliverables>`; end with `<approval_gate>`. When output is wrong, change the tag that caused it.
- **Three-Layer Quality System**: match capability to cost so each gate filters what the next must process.
  - When to use: as the verification pipeline for any agent output.
  - How: **Layer 1 Technical Verification (automated)** — `tsc --noEmit`, ESLint with zero warnings, circular-dependency detection, tests; runs on every change, blocks before human eyes. **Layer 2 Functional Verification (AI-assisted)** — structured prompts asking the AI to audit its own output against the spec: business logic, edge cases, performance, security. **Layer 3 Architectural Review (human)** — pattern compliance, scalability, maintainability, tech-debt impact, "does this still make sense in eighteen months."
- **APPROVAL_GATE**: a structural element every planning prompt carries, making the gate unavoidable rather than something to remember.
  - When to use: every planning request.
  - How: end the prompt with `<approval_gate>WAIT FOR MY EXPLICIT APPROVAL BEFORE IMPLEMENTING ANY CODE.</approval_gate>`; require the plan as a committed deliverable (DB changes, API routes, components, testing strategy) that implementation is measured against.
- **The Junior Engineer Mental Model**: the AI is "a competent junior engineer who follows strict protocols rather than making autonomous decisions, proposes detailed plans before writing any code, respects established patterns and architectural constraints, and undergoes systematic review for every output."
  - When to use: diagnosing bad output.
  - How: resolve every failure to a missing context or constraint in the prompt — ignoring the PRD means insufficient context; overcomplicating means scope too loose. Fix with better context, not less trust or a different tool.

## Key Concepts
- **Sticky-note prompt**: a conversational prompt with one idea, no structure, meaning at the receiver's mercy.
- **Improvisation budget**: the interpretation space a vague prompt leaves for the model to fill.
- **Separation of concerns in prompts**: instructions, context, constraints and success criteria in distinct tags instead of one prose block.
- **Composability**: XML templates combine without collision.
- **Debuggability**: a wrong output points to the tag to change rather than a guess about which sentence the model latched onto.
- **Enforcement vs verification**: Layer 1 prevents at the point of deviation; Layers 2–3 catch after the fact.
- **Plan as deliverable**: a written technical plan, not a verbal summary.

## Mental Models
- Think of a prose prompt as a sticky note and an XML prompt as a spec — the latter collapses the interpretation space the way EARS does for requirements.
- Use machines for syntax, AI for logic, humans for architecture — syntax violations have no business reaching human review.
- Think of the approval gate as the natural protocol for an engineer whose judgment you are still calibrating, not friction.
- When the agent misbehaves, ask "what context or constraint did my prompt omit?" before blaming the model.

## Anti-patterns
- **Paragraph-of-prose feature requests**: blend instructions, context and constraints so nothing is verifiable.
- **Implied constraints**: unenumerated constraints are invisible to the agent.
- **Remembering to ask for approval**: a gate that depends on developer memory gets skipped; embed it in the template.
- **Spending human review on syntax or edge cases**: wastes the scarcest reviewer on what Layer 1/2 catch cheaply.
- **Assuming one session's discipline persists**: the next prompt starts fresh; without codebase guardrails nothing forces it to honor earlier decisions.

## Code Examples
```xml
<planning_request>
  <objective>PLAN FIRST: Create user authentication system with JWT tokens.</objective>
  <context>
    <tech_stack>Next.js 14, TypeScript, PostgreSQL with Prisma</tech_stack>
    <existing_patterns>Follow auth patterns in /lib/auth.ts</existing_patterns>
  </context>
  <constraints>
    Cannot modify package.json without permission.
    Must handle rate limiting and security headers.
  </constraints>
  <deliverables>
    Database schema changes, API routes, frontend components,
    testing strategy with 80%+ coverage.
  </deliverables>
  <approval_gate>WAIT FOR MY EXPLICIT APPROVAL BEFORE IMPLEMENTING ANY CODE.</approval_gate>
</planning_request>
```
- **What it demonstrates**: each section is independently checkable — plan vs code produced, constraints enumerated, gate explicit so the model cannot claim ambiguity about waiting.

## Reference Tables
| Layer | Owner | Checks | Character |
|---|---|---|---|
| 1 Technical Verification | Automated | Types (`tsc --noEmit`), ESLint zero warnings, circular deps, tests | Enforcement: deterministic, every change |
| 2 Functional Verification | AI-assisted | Business logic, edge cases, performance, security vs spec | Verification, cheap |
| 3 Architectural Review | Human | Pattern compliance, scalability, maintainability, tech debt | Verification, judgment |

| Aspect | Vibe Coding Playbook |
|---|---|
| What | XML-structured prompting methodology + three-layer quality system |
| Core move | Machine-readable XML specs separating instructions/context/constraints |
| Human gate | Explicit `<approval_gate>` in every planning prompt: structural, not optional |
| Mental model | AI as junior engineer: clear protocols, explicit plans, systematic review |
| Templates | API design, database schema, legacy migration, performance debugging |
| Limit | Prompting discipline, not codebase enforcement; still needs Ch 4–6 guardrails |

## Why It Works / Failure Mode
- **XML prompting works** because it removes ambiguity at the source: enumerated constraints and an in-prompt gate leave no room to improvise or "forget" to wait. It breaks across sessions — the APPROVAL_GATE closes the loop for one session; only codebase enforcement (annotations, architectural tests, living diagrams) closes it permanently.
- **The three layers work** by stacking filters cheapest-first. The failure mode: only Layer 1 is enforcement; architectural integrity sits in human Layer 3, i.e. it is not automated. Annotations, ArchUnit rules and contract tests shrink Layer 3 by turning structural constraints from judgment-verifiable into machine-verifiable.

## Key Takeaways
1. Structure complex asks as XML: objective, context, constraints, deliverables, approval gate.
2. Enumerate constraints; never imply them.
3. Embed the approval gate in every planning template so it cannot be skipped.
4. Route checks by cost: automation for syntax, AI for logic, humans for architecture.
5. Treat agent failures as missing context or constraints, not as reasons to distrust the tool.
6. Prompt discipline is per-session; move structural rules into the codebase so they persist.

## Connects To
- **Ch 4–6**: annotations, architectural tests and living diagrams that persist discipline beyond the session.
- **Ch 7**: EARS grammar and write-it-down discipline — same interpretation-collapsing move.
- **Ch 12**: Superpowers' two-stage review, here formalized as Layer 2.
- **Ch 13**: the "treat the agent like a junior developer" human gate.
- **Part IV**: contract tests and ArchUnit rules that make Layer 3 cheaper and rarer.
