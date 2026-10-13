# Patterns & Techniques — Enterprise Vibe Coding for Agentic Engineering

## Bounded Delegation (Three Shifts)
**When to use**: Handing any task to an agent that touches a shared codebase.
**How**: Give a bounded task (inputs, permitted tools, allowed actions, definition of done), not an open outcome. Name a human who approves. Require evidence in the PR (spec, tests, scans, rationale). Write the rules in the repo and enforce them in the pipeline. (Ch 1)
**Trade-offs**: Slower than "prompt → ship" for throwaway work, so keep vibe coding for prototypes.

## Primitive Stack Adoption
**When to use**: Making agent output repeatable across people and sessions.
**How**: Adopt in this order: concise global + glob-scoped instructions → intent-named prompts with fixed outlines → 3–5 least-privilege agents → 3–5 skills with failure modes → a few fast deterministic hooks → MCP read-only, pinned and logged. One job per file: rules / what / who / how / enforce / connect. (Ch 3)
**Trade-offs**: Files are surface-specific (Copilot vs Claude Code), so the pattern ports but the files must be re-mapped. Primitives need monthly upkeep.

## RPI Cadence
**When to use**: Every agent task in every SDLC phase.
**How**: Research (read spec/ADR/code, emit an assumptions note) → Plan (diff scope, tests, rollback) → human approves → Implement in small PRs carrying test/lint/scan evidence → independent validation still runs afterwards. (Ch 4)
**Trade-offs**: Approval ≠ correctness. High-risk changes need a second reviewer or independent checks.

## Release Pipeline as Active Safety System
**When to use**: Any agent-assisted path to production.
**How**: build → test pyramid + agent eval harness → staging → smoke-test agent → named human approval → canary → SLO watch → promote/rollback. Release agents halt on anomalies (coverage drop, unusual files, new MCP server). Agents never decide to release. (Ch 4)
**Trade-offs**: The human gate adds latency on purpose. That gate is where speed and trust are traded.

## Spec-to-Test-Plan
**When to use**: Turning user stories into tests before writing code.
**How**: Per story: happy path + 3 edge cases + 2 failure modes + 1 security case. The tech lead reviews the plan before test code. For agentic apps, add scenario tests (replayable traces) and E2E tests through MCP against a sandbox. (Ch 4)

## Band Placement by Blast Radius
**When to use**: Deciding how much control any agent action needs.
**How**: Place each action on the five-band spectrum: creative drafting in bands 1–2; generated code in band 3 (must pass deterministic gates); consequential operations in band 4 (agent picks a reproducible script); release and authorization in band 5 (policy, no model). Also assign exactly one decision level (0–3). (Ch 5)
**Trade-offs**: Over-pinning kills the creative value. Under-pinning (a band-2 instruction guarding a band-5 action) causes the incident.

## Instruction → Hook → Policy Escalation
**When to use**: A rule matters enough that a violation is unacceptable.
**How**: Write it imperatively in a scoped instruction. If it must hold, enforce it with a `PreToolUse` hook (blocks the call). If it must hold org-wide, survive model swaps and be revocable in one place, move it to deny-by-default policy-as-code (OPA/Rego, Cedar) with tests, decision logs, versioning and an owner. (Ch 5)
**Trade-offs**: Hooks are per-repo and must be copied. Policies need central infrastructure.

## Deterministic Parallelism
**When to use**: Running several subagents at once.
**How**: Declare file, tool and dependency scopes and run in parallel only when they are disjoint; otherwise run sequentially. Make every shared write idempotent (deterministic dedupe keys, content-addressed uploads). Hand off through repo files, never model-to-model messages. (Ch 5)
**Trade-offs**: Less parallelism in exchange for outputs that don't depend on timing.

## Orchestration Pattern Selection (MAF)
**When to use**: Starting any multi-agent product.
**How**: Pick from the shape of the problem. Sequential: real dependencies. Concurrent: independent fan-out plus aggregation. Group chat: iterative rounds. Magentic: open-ended, steps unknown. Handoff: single-threaded conversation where expertise shifts (one voice). (Ch 6)
**Trade-offs**: Handoffs add latency and cost, so measure against a simpler single-agent design.

## Grounded Specialist + Failure Path
**When to use**: Agents that quote facts (price, stock, availability) or perform multi-step bookings.
**How**: The agent stating a fact is the one connected to its system of record via MCP, never memory. On partial failure, use idempotency, bounded retries, preserve/compensate completed steps, then escalate to a human with the full handoff/tool-call trace. (Ch 6)

## Layered Content Gate
**When to use**: Compliance/brand checks on generated content at volume.
**How**: Deterministic rules reject clear violations first, then AI reviewers flag ambiguity, then a legal/compliance human approves high-risk or regulated claims. Put a human gate on the plan before generation starts. Encode rules once in a skill, never in a dozen prompts. (Ch 6)

## Delivery Loop (Five Stages, Two Gates)
**When to use**: Recurring feature delivery that should advance without a human driving every step.
**How**: The issue is an executable contract with checkbox criteria. Each tick runs instructions (law) → engine prompt → skill (playbook) → state rebuilt from the issue/PR thread → advance one capability. Stages: Discover → Plan (Gate 1: explicit approval; silence = wait) → Execute in small slices → Verify and Recover (failure becomes the next input) → Complete (Gate 2: human merge). A done-condition job blocks while any box is unchecked. (Ch 7)
**Trade-offs**: Needs bounding: continuation caps, `MAX_STARTS`, idempotent "loop-started" marking, conflict detection, least-privilege MCP, hard gates for sensitive areas.

## Bounded Recovery
**When to use**: An agent loop retrying on failing checks.
**How**: Halt after 3 failed attempts on the same criterion or on a repeating failure pattern. In auth/payments/PII/production, stop on the first failure. The human then chooses: roll back, revise the plan, or escalate. (Ch 7)

## Resumable Handoff View (AX)
**When to use**: Agents that work for hours or days while the human is away.
**How**: Pick one long-running workflow. Gather the plan, diff, assumptions, evidence, retries and pending decision into one view that answers the five return questions without the transcript. (Ch 8)
