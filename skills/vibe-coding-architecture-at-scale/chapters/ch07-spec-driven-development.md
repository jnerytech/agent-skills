# Chapter 7: Spec-Driven Development: The Spec Is the Guardrail

## Core Idea
Spec-Driven Development (SDD) is Vibe Architecture viewed from the input side: every Part II guardrail — context file, annotations, tests, diagram, logging policy, docs — is one specification expressed in several enforceable forms. Feed the AI a version-controlled spec instead of ad-hoc prose; the human is the architect, the spec is the contract, the prompt is merely a trigger saying "satisfy this."

## Frameworks Introduced
- **Spec-Driven Development (SDD) as unification**: one artifact, many enforceable forms.
  - When to use: framing why the separate guardrails belong together; replacing chat-window intent with durable intent.
  - How: map each guardrail to a spec layer — context file = project spec; annotation = element spec; architectural test = boundary spec; behavioral test = feature spec; living diagram = structure spec; logging policy = behavior spec; documentation surface = prose half (reasoning + routing). Store all of it in the repo, not the model's volatile context window.
- **The Repository as Constitution**: a `.specs/` directory the AI must read before changing anything.
  - When to use: any project where features are AI-implemented.
  - How: (1) **Specify** — write `feature-spec-timeout.md`: expected behavior, edge cases, security rules, explicit out-of-scope. (2) **Plan, then execute** — prompt: "Read `.specs/tech-stack.md` and `feature-spec-timeout.md`. Produce an implementation plan in `plan.md` and stop. Do not write code yet." Review the plan (≈30 s). (3) **Validate** — implement against the spec; `tech-stack.md` lists forbidden deps and version pins so the AI cannot shortcut with an unapproved library (shift left as a directory layout).
- **Specification by Example (AI-driven BDD)**: the tightest spec is simultaneously human-readable and executable — Gherkin.
  - When to use: feature/business-logic behavior.
  - How: the human writes the `.feature` file (the intent — the one artifact a model should not author); the AI writes app code and step definitions; loop until green. The AI may never weaken the scenario to declare success.
- **Contract-Driven Development**: for anything with an interface, the API contract (OpenAPI / AsyncAPI / JSON Schema) drives the code.
  - When to use: microservices, REST endpoints, MCP tools.
  - How: "Using `api-spec.yaml`, generate the controller layer; every validation annotation must match the schema exactly." Same artifact then runs as a contract test (Ch 18) — authors the code, then refuses drift.
- **The Three-Phase Workflow**: requirements.md → design.md → tasks.md = what → how → do; each file boundary is a human review gate.
  - When to use: any spec driving real work, greenfield or brownfield.
  - How: **Phase 1 Requirements / bug analysis** — what, never how; user stories + explicit acceptance criteria. For defects, `bugfix.md`: current (wrong) behavior, expected behavior, and **behavior that must remain unchanged** (a written regression contract / allowed blast radius). **Phase 2 Design** — only now how: architecture, components, sequence/data flow, error handling, testing approach; not started until requirements are approved. **Phase 3 Tasks** — discrete units with one checkable outcome each, trackable, runnable alone or all at once.
- **The command-driven loop (tool shape)**: `/constitution → /specify → /plan → /tasks → /implement`, human gate on every arrow; optional `/clarify` (surface ambiguities before planning) and `/analyze` (check spec/plan/tasks for mutual contradiction).
  - How: `/specify` forbids naming libraries or classes; `/plan` physically stops before code; `/tasks` yields units small enough that a red task names its own fix; `/implement` is Ch 5's write-test-fix loop run against the whole spec.

## Key Concepts
- **Vibe coding (literal sense)**: short ad-hoc prompts ("fix this bug", "add a button") with the context window as source of truth — doesn't scale.
- **Hallucination suppressant**: a precise spec removes the degrees of freedom in which hallucination happens; LLMs are weak at inventing structure, strong at translating rigid structure to syntax.
- **`.specs/` constitution**: `mission.md` (why/what, domain, guardrails, non-goals), `tech-stack.md` (approved + forbidden deps, version pins), `roadmap.md` (phases, in/out of this slice), plus CLAUDE.md/.cursorrules.
- **Spec clause as ADR descendant**: a decision plus its why, versioned next to code — but now read by the AI before every task; "the record that used to be archaeology is now enforcement."
- **Architecture characteristics as spec lines**: Richards/Ford "-ilities" become lines in `mission.md`/`tech-stack.md` the generator must satisfy.
- **bugfix.md**: the brownfield SDD artifact; its "must remain unchanged" clause is "do not weaken the test" stated before code is touched.
- **EARS**: Easy Approach to Requirements Syntax — "WHEN [trigger], THE SYSTEM SHALL [response]" — a constrained grammar for requirements (Kiro).
- **Spec as wish**: a formatted spec with no test behind it — the AI satisfies its letter and erodes the structure beneath.

## Mental Models
- Think of SDD as **the umbrella, not the ribs**: tools industrialize authoring and sequencing of the spec; enforcement is still tests, annotations, diagrams, pipeline.
- Use **"what before how"** as a file boundary: the design file isn't started until the requirements file is approved.
- Think of each gate as **a 30-second human read that saves a regenerated afternoon**.
- Place any new spec tool by asking **which layer it occupies** (substrate / harness / requirements-grammar / multi-agent orchestrator).

## Anti-patterns
- **Collapsing requirements, design and tasks into one prompt**: Ch 1's volatile-chat-window failure "with extra Markdown" — no review boundaries.
- **Letting the model author the `.feature` file**: the scenario *is* the intent.
- **"Make me a billing endpoint"**: maximizes the space the model must hallucinate into.
- **Naming libraries/classes in `/specify`**: reintroduces the guessing; what must be pinned before how.
- **Spec tool without Ch 3–6 guardrails**: a Spec Kit document with no architectural test is a wish, not a guardrail.
- **Bugfix spec without "must remain unchanged"**: no stated blast radius, so the fix may silently regress neighbors.

## Code Examples
```gherkin
Feature: Premium Subscription Upgrades
  Scenario: User upgrades with valid payment
    Given the user has a "Free" account tier
    When the user submits a valid credit card for the "Premium" tier
    Then their account tier should change to "Premium"
    And a webhook should be dispatched to the billing microservice
```
- **What it demonstrates**: a human-owned executable spec; the AI writes code + step definitions and cannot weaken the predicate.

```text
.specs/
├── mission.md      # the "why" and "what": core domain, guardrails, non-goals
├── tech-stack.md   # approved + forbidden dependencies, framework/version pins
└── roadmap.md      # sequential phases; what is in and out of this slice
CLAUDE.md / .cursorrules   # behavioral constraints (Ch 3 context file)
```
- **What it demonstrates**: the repository constitution — Tier 1 invariants in CLAUDE.md, durable what/why in `.specs/`, per-feature intent in a reviewed feature spec.

## Reference Tables
| Dimension | Vibe Coding | Spec-Driven Development |
|---|---|---|
| Primary input | Ad-hoc chat prompts | Version-controlled specs, schemas, scenarios |
| Source of truth | LLM context window (volatile) | Repository spec directory (durable) |
| Human role | Reviewer of massive diffs; prompt-tweaker | Architect, constraint-setter, orchestrator |
| Scale suitability | Weekend hacks, prototypes | Enterprise systems, long-term maintenance |

**Tool landscape layers**
| Layer | Example | What it does |
|---|---|---|
| Substrate (agent-native spec files) | CLAUDE.md + `.claude/commands/`; Cursor `.cursor/rules/` | Loop can run by hand; doesn't standardize across a team |
| Spec-workflow harness | GitHub Spec Kit | Imposes ordered command loop on any agent (Claude Code, Copilot, Cursor, Gemini CLI) |
| Requirements-grammar tool | Kiro | requirements/design/tasks files; EARS grammar; cloud-native targets |
| Multi-agent spec orchestrator | Intent / Zenflow | Coordinator reads living bidirectional spec, dispatches micro-tasks to specialists |

## Worked Example
**Adding "session timeout" the SDD way.** Instead of prompting "add session timeout": write `feature-spec-timeout.md` (expected behavior, edge cases, security rules, out of scope). Prompt: "Read `.specs/tech-stack.md` and `feature-spec-timeout.md`. Produce an implementation plan in `plan.md` and stop. Do not write code yet." Read the plan against the spec (~30 s). Approve; AI implements. Because `tech-stack.md` enumerates forbidden dependencies and version pins, the AI cannot pull in an unapproved session library to shortcut. Intent lived in the repo, reviewed and versioned, before any prompt implemented it.

## Why It Works / Failure Mode
- **Spec as hallucination suppressant**: models excel at pattern completion and translation of rigid structure, fail at inventing structure; specs, schemas, EARS grammar, `/clarify` and `/analyze` all remove degrees of freedom before the model improvises into them. Fails when the spec isn't backed by something that can fail a build — the AI satisfies the letter and erodes the structure.
- **Three-phase gates**: each file boundary forces a cheap human review at the point where errors are cheapest to fix (what before how before do). Fails when phases are collapsed into one prompt or gates are rubber-stamped.

## Key Takeaways
1. Every guardrail in Part II is a clause of one specification; SDD is the industry's name for that.
2. Move intent out of the chat window into `.specs/` and feature specs that are written, reviewed and versioned before implementation.
3. Humans own the intent artifacts (`.feature` files, API schemas, requirements); AI owns everything downstream.
4. Run requirements → design → tasks as separate files with a human gate between each; for bugs, always state what must remain unchanged.
5. Precise specs are the strongest hallucination suppressant — they collapse the space the model would guess into.
6. Spec tools standardize authoring and sequencing; they do not enforce — tests, annotations and diagrams do.

## Connects To
- **Ch 1**: volatile source of truth doesn't scale; Vibe Architecture thesis.
- **Ch 2 / 2b**: shift left; architect role; architecture characteristics.
- **Ch 3 / 4 / 5 / 6 / 6b / 6c**: the guardrails unified here as spec forms.
- **Ch 8**: Spec Kit hands-on; **Ch 9** Kiro; **Ch 10** Zenflow; **Ch 11** Get-Shit-Done.
- **Ch 18**: contract tests — the downstream twin of contract-driven generation.
- **Ch 21**: multi-agent enforcement, counterpart to spec orchestrators.
- **BDD / Specification by Example (Adzic)**, **ADRs (Nygard)**, **EARS (Mavin)**, **Richards & Ford architecture characteristics**.
